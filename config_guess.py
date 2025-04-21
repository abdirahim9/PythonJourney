import random
import sqlite3
import logging
import configparser

class GuessGame:
    """Manages a number guessing game with SQLite stats, logging, and config."""
    def __init__ (self, config_file="game.ini"):
        # Load config
        config = configparser.ConfigParser()
        config.read(config_file)
        try:
            self.ranges = (
                int(config["Game"]["min_range"]),
                int(config["Game"]["max_range"])
            )
            self.max_attempts = int(config["Game"]["max_attempts"])
            self.db_name = config["Game"]["db_name"]
            self.log_file = config["Game"]["log_file"]
            log_level = config["Game"]["log_level"].upper()
        except (KeyError, ValueError) as e:
            logging.error("Config error %s", e)
            raise
        # Validate ranges
        if self.ranges[0] >= self.ranges[1]:
            logging.error("Invalid range: min_range must be less than max_range")
            raise ValueError("Invalid range: min_range must be less than max_range")
        # Setup logging
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        logging.basicConfig(
            filename=self.log_file,
            level=log_levels.get(log_level, logging.INFO),
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Game initialized with config from %s", config_file)
        # Setup database
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Create stats table if it doesn't exist."""
        try:
            self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS stats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            games INTEGER DEFAULT 0,
                            attempts INTEGER DEFAULT 0
                            )
                            """)
            self.conn.commit()
            self.cursor.execute("SELECT COUNT(*) FROM stats")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO stats (games, attempts) VALUES (0,0)")
                self.conn.commit()
            logging.info("Stats table checked/created")
        except sqlite3.Error as e:
            logging.error("Database error %s", e)
            raise

    def update_stats(self,attempts):
        """Update games and attempts in the database."""
        try:
            self.cursor.execute("UPDATE stats SET games = games + 1, attempts = attempts + ? WHERE id = 1", (attempts,))
            self.conn.commit()
            logging.info("Stats updated: +1 game, +%s attempts", attempts)
        except sqlite3.Error as e:
            logging.error("Database error %s", e)
            raise

    def get_stats(self):
        """Fetch current stats from the database."""
        try:
            self.cursor.execute("SELECT games, attempts FROM stats WHERE id = 1")
            games, attempts = self.cursor.fetchone()
            logging.info("Stats retrieved: %s games, %s attempts", games, attempts)
            return {"games": games, "attempts": attempts}
        except sqlite3.Error as e:
            logging.error("Database error %s", e)
            raise
    def play(self):
        """Run a game round and update stats."""
        target = random.randint(self.ranges[0], self.ranges[1])
        logging.info("New game started, target number: %s", target)
        print(f"\nGuess a number between {self.ranges[0]} and {self.ranges[1]} !")
        try:
            guess = int(input("Your guess: "))
            logging.info("Player guessed: %s", guess)
            if guess < self.ranges[0] or guess > self.ranges[1]:
                print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                logging.warning("Out-of-range guess: %s", guess)
                return
            attempts = 1
            while guess != target and attempts < self.max_attempts:
                print("Too low!" if guess < target else "Too high!")
                try:
                    guess = int(input("Try again: "))
                    logging.info("Player guessed: %s", guess)
                    if guess < self.ranges[0] or guess > self.ranges[1]:
                        print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]} !")
                        logging.warning("Out-of-range guess: %s", guess)
                        return
                    attempts += 1
                except ValueError as e:
                    print("Invalid input! Numbers only.")
                    logging.error("Invalid input: %s", e)
                    return
                outcome = "Won" if guess == target else "lost"
                self.update_stats(attempts)
                stats = self.get_stats()
                print(f"Outcome: {outcome} in {attempts} tries. Target was {target}")
                print(f"Current stats: {stats['games']} games, {stats['attempts']} attempts")
                logging.info("Game outcome: %s in %s tries", outcome, attempts)
        except ValueError as e:
            print("Invalid input! Numbers only. Game skipped.")
            logging.error("Invalid initial guess: %s", e)

    def __del__(self):
        """Close database connection."""
        try:
            self.conn.close()
            logging.info("Database connection closed")
        except AttributeError as e:
            pass # conn might not be exist if init failed

def main():
    """Main game loop."""
    try:
        game = GuessGame()
        play_again = "y"
        while play_again.lower() == "y":
            game.play()
            play_again = input("Play again? (y/n): ").strip()
            if play_again.lower() not in ["y", "n"]:
                print("Invalid input! Assuming 'n'.")
                logging.warning("Invalid play again input: %s", play_again)
                play_again = "n"
        stats = game.get_stats()
        print(f"\nFinal stats: {stats['games']} games, {stats['attempts']} attempts")
        logging.info("Session ended")
    except Exception as e:
        logging.error("Main loop error: %s", e)
        raise

if __name__ == "__main__":
    main()