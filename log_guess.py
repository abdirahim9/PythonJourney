import random
import sqlite3
import logging

class GuessGame:
    "Manages a number guessing game with SQLite stats and logging."
    def __init__(self, db_name="guess_stats.db"):
        self.ranges = (1, 100)
        self.max_attempts = 10
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        # Setup logging
        log_file = "game.log"  # Define the log file path
        logging.basicConfig(
            filename=log_file, 
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Game initialized with range %s-%s", self.ranges[0], self.ranges[1])

    def create_table(self):
        """Create stats table if it doesn't exist."""
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

    def update_stats(self, attempts):
        """Update games and attempts in the database."""
        self.cursor.execute("Update stats SET games = games + 1, attempts = attempts + ? WHERE id = 1", (attempts,))
        self.conn.commit()
        logging.info("Stats updated: +1 game, +%s attempts", attempts)

    def get_stats(self):
        """"Fetch current stats from the database."""
        self.cursor.execute("SELECT games, attempts FROM stats WHERE id = 1")
        games, attempts = self.cursor.fetchone()
        logging.info("Stats retrieved: %s games, %s attempts", games, attempts)
        return {"games": games, "attempts": attempts}
    
    def play(self):
        """Run a game round and update stats."""
        target = random.randint(self.ranges[0], self.ranges[1])
        logging.info("New game started, target number: %s", target)
        print(f"\nGuess a number between {self.ranges[0]} and {self.ranges[1]}!")
        try:
            guess = int(input("Your guess: "))
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
                except ValueError:
                    print("Invalid input! Numbers only.")
                    logging.error("Invalid input: %s", guess)
                    return
            outcome = "Won" if guess == target else "Lost"
            self.update_stats(attempts)
            stats = self.get_stats()
            print(f"Outcome: {outcome} in {attempts} tries. Target was {target}")
            print(f"Current stats: {stats['games']} games, {stats['attempts']} attempts")
            logging.info("Game outcome: %s in %s tries", outcome, attempts)
        except ValueError as e:
            print("Invalid input! Numbers only. Game skipped.")
            logging.error("Invalid initial input: %s", e)

    def __del__(self):
        """Close database connection."""
        self.conn.close()
        logging.info("Database connection closed.")

def main():
    """Main game loop."""
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

if __name__ == "__main__":
    main()