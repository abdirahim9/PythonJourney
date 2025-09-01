import random
import sqlite3
import logging
import configparser
import argparse
import csv
import datetime

class GuessGame:
    """Manages a number guessing game with SQLite stats, logging, config, CLI, and CSV history."""
    def __init__(self, config_file: str = "game.ini", min_range: int | None = None, 
                max_range: int | None = None, max_attempts: int | None = None):
        # Load config
        config = configparser.ConfigParser()
        try:
            if not config.read(config_file):
                raise FileNotFoundError(f"Config file {config_file} not found")
            self.ranges = (
                int(min_range if min_range is not None else config["Game"]["min_range"]),
                int(max_range if max_range is not None else config["Game"]["max_range"])
            )
            self.max_attempts = int(max_attempts if max_attempts is not None else config["Game"]["max_attempts"])
            self.db_name = config["Game"]["db_name"]
            self.log_file = config["Game"]["log_file"]
            self.history_file = config["Game"]["history_file"]
            log_level = config["Game"]["log_level"].upper()
        except (KeyError, ValueError, FileNotFoundError) as e:
            logging.error("Config error: %s", e)
            raise
        # Validate ranges
        if self.ranges[0] >= self.ranges[1]:
            logging.error("Invalid range: min_range >= max_range")
            raise ValueError("min_range must be less than max_range")
        # Setup logging
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        logging.basicConfig(
            filename=self.log_file,
            level=log_levels.get(log_level, logging.INFO),
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Game initialized with config %s, CLI args: min=%s, max=%s, attempts=%s",
                     config_file, min_range, max_range, max_attempts)
        # Setup database
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.create_table()
        except sqlite3.Error as e:
            logging.error("Database connection error: %s", e)
            raise
        # Setup CSV
        self.init_csv()
    
    def init_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        try:
            with open(self.history_file, mode="a", newline="") as f:
                writer = csv.writer(f)
                f.seek(0)
                if f.tell() == 0:
                    writer.writerow(["Timestamp", "Outcome", "Attempts", "Target"])
            logging.info("CSV file %s initialized", self.history_file)
        except IOError as e:
            logging.error("CSV initialization error: %s", e)
            raise
    
    def save_to_csv(self, outcome: str, attempts: int, target: int):
        """Save game result to CSV."""
        try:
            with open(self.history_file, mode="a", newline="") as f:
                writer = csv.writer(f)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([timestamp, outcome, attempts, target])
            logging.info("Game saved to CSV: %s, %s, %s", outcome, attempts, target)
        except IOError as e:
            logging.error("CSV write error: %s", e)
            raise
    
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
                self.cursor.execute("INSERT INTO stats (games, attempts) VALUES (0, 0)")
                self.conn.commit()
            logging.info("Stats table checked/created")
        except sqlite3.Error as e:
            logging.error("Database error: %s", e)
            raise
    
    def update_stats(self, attempts: int):
        """Update games and attempts in the database."""
        try:
            self.cursor.execute("UPDATE stats SET games = games + 1, attempts = attempts + ? WHERE id = 1", (attempts,))
            self.conn.commit()
            logging.info("Stats updated: +1 game, +%s attempts", attempts)
        except sqlite3.Error as e:
            logging.error("Stats update error: %s", e)
            raise
    
    def get_stats(self):
        """Fetch current stats from the database."""
        try:
            self.cursor.execute("SELECT games, attempts FROM stats WHERE id = 1")
            games, attempts = self.cursor.fetchone()
            logging.info("Stats retrieved: %s games, %s attempts", games, attempts)
            return {"games": games, "attempts": attempts}
        except sqlite3.Error as e:
            logging.error("Stats retrieval error: %s", e)
            raise
    
    def show_stats(self):
        """Display current stats."""
        stats = self.get_stats()
        print(f"\nStats: {stats['games']} games played, {stats['attempts']} total attempts")
        logging.info("Stats displayed")
    
    def play(self):
        """Run a game round, update stats, and save to CSV."""
        target = random.randint(self.ranges[0], self.ranges[1])
        logging.info("New game started, target: %s", target)
        print(f"\nGuess a number between {self.ranges[0]} and {self.ranges[1]}!")
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
                        print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                        logging.warning("Out-of-range guess: %s", guess)
                        return
                    attempts += 1
                except ValueError as e:
                    print("Invalid input! Numbers only.")
                    logging.error("Invalid guess input: %s", e)
                    return
            outcome = "Won" if guess == target else "Lost"
            self.update_stats(attempts)
            self.save_to_csv(outcome, attempts, target)
            stats = self.get_stats()
            print(f"Outcome: {outcome} in {attempts} tries. Target was {target}")
            print(f"Current stats: {stats['games']} games, {stats['attempts']} attempts")
            logging.info("Game ended: %s in %s tries", outcome, attempts)
        except ValueError as e:
            print("Invalid input! Numbers only. Game skipped.")
            logging.error("Invalid initial guess: %s", e)
    
    def __del__(self):
        """Close database connection."""
        try:
            self.conn.close()
            logging.info("Database connection closed")
        except AttributeError:
            pass

def main():
    """Main game loop with CLI args."""
    parser = argparse.ArgumentParser(description="Number guessing game with CSV history")
    parser.add_argument("--min", type=int, help="Minimum range value")
    parser.add_argument("--max", type=int, help="Maximum range value")
    parser.add_argument("--attempts", type=int, help="Maximum attempts allowed")
    parser.add_argument("--stats", action="store_true", help="Show stats and exit")
    try:
        args = parser.parse_args()
        game = GuessGame(min_range=args.min, max_range=args.max, max_attempts=args.attempts)
        if args.stats:
            game.show_stats()
            return
        play_again = "y"
        while play_again.lower() == "y":
            game.play()
            play_again = input("Play again? (y/n): ").strip()
            if play_again.lower() not in ["y", "n"]:
                print("Invalid input! Assuming 'n'.")
                logging.warning("Invalid replay input: %s", play_again)
                play_again = "n"
        stats = game.get_stats()
        print(f"\nFinal stats: {stats['games']} games, {stats['attempts']} attempts")
        logging.info("Session ended")
    except Exception as e:
        logging.error("Main loop error: %s", e)
        raise

if __name__ == "__main__":
    main()