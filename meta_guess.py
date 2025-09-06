import random
import sqlite3
import logging
import configparser
import argparse
import csv
import datetime
import os  # Added to fix NameError in init_csv

class GuessGame:
    """Base class for guessing game with SQLite stats, logging, config, CLI, and CSV history."""
    def __init__(self, config_file="game.ini", min_range=None, max_range=None, max_attempts=None):
        # Load config
        config = configparser.ConfigParser()
        config.read(config_file)
        # Prefer CLI args over config
        self.ranges = (
            int(min_range if min_range is not None else config["Game"]["min_range"]),
            int(max_range if max_range is not None else config["Game"]["max_range"])
        )
        self.max_attempts = int(max_attempts if max_attempts is not None else config["Game"]["max_attempts"])
        self.db_name = config["Game"]["db_name"]
        self.log_file = config["Game"]["log_file"]
        self.history_file = config["Game"]["history_file"]
        log_level = config["Game"]["log_level"].upper()
        # Setup logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Game initialized with config %s, CLI args: min=%s, max=%s, attempts=%s",
                     config_file, min_range, max_range, max_attempts)
        # Setup database
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        # Setup CSV
        self.init_csv()
    
    def init_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        with open(self.history_file, mode="a", newline="") as f:
            writer = csv.writer(f)
            if os.stat(self.history_file).st_size == 0:
                writer.writerow(["Timestamp", "Outcome", "Attempts", "Target"])
    
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
    
    def update_stats(self, attempts):
        """Update games and attempts in the database."""
        self.cursor.execute("UPDATE stats SET games = games + 1, attempts = attempts + ? WHERE id = 1", (attempts,))
        self.conn.commit()
    
    def get_stats(self):
        """Fetch current stats from the database."""
        self.cursor.execute("SELECT games, attempts FROM stats WHERE id = 1")
        games, attempts = self.cursor.fetchone()
        return {"games": games, "attempts": attempts}
    
    def show_stats(self):
        """Display current stats."""
        stats = self.get_stats()
        print(f"\nStats: {stats['games']} games played, {stats['attempts']} total attempts")
    
    def play(self):
        """Run a single game round."""
        target = random.randint(self.ranges[0], self.ranges[1])
        print(f"\nGuess a number between {self.ranges[0]} and {self.ranges[1]}!")
        try:
            guess = int(input("Your guess: "))
            if guess < self.ranges[0] or guess > self.ranges[1]:
                print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                return
            attempts = 1
            while guess != target and attempts < self.max_attempts:
                print("Too low!" if guess < target else "Too high!")
                try:
                    guess = int(input("Try again: "))
                    if guess < self.ranges[0] or guess > self.ranges[1]:
                        print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                        return
                    attempts += 1
                except ValueError:
                    print("Invalid input! Numbers only.")
                    return
            outcome = "Won" if guess == target else "Lost"
            self.update_stats(attempts)
            stats = self.get_stats()
            print(f"Outcome: {outcome} in {attempts} tries. Target was {target}")
            print(f"Current stats: {stats['games']} games, {stats['attempts']} attempts")
        except ValueError:
            print("Invalid input! Numbers only. Game skipped.")
    
    def __del__(self):
        """Close database connection."""
        self.conn.close()
    
def main():
    """Main game loop with CLI args."""
    parser = argparse.ArgumentParser(description="Number guessing game with CSV history")
    parser.add_argument("--min", type=int, help="Minimum range value")
    parser.add_argument("--max", type=int, help="Maximum range value")
    parser.add_argument("--attempts", type=int, help="Maximum attempts allowed")
    parser.add_argument("--stats", action="store_true", help="Show stats and exit")
    args = parser.parse_args()
    game = GuessGame(min_range=args.min, max_range=args.max, max_attempts=args.attempts)
    if args.stats:
        game.show_stats()
        return
    play_again = "y"
    while play_again.lower() == "y":
        game.play()
        play_again = input("Play again? (y/n): ").strip()
    print("Game session ended.")
    
if __name__ == "__main__":
    main()