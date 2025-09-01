import random
import sqlite3
import csv
import logging
import datetime
import configparser
import os
import argparse

class GuessGame:
    """A number guessing game with CSV history, SQLite stats, config file, and CLI args."""
    def __init__(self, config_file="game.ini", min_range=None, max_range=None, max_attempts=None):
        """Initialize game with config file or CLI args, prioritizing CLI."""
        self.config_file = config_file
        
        # Validate CLI args first
        if min_range is not None and max_range is not None:
            if min_range >= max_range:
                raise ValueError("min_range must be less than max_range")
        if max_attempts is not None and max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        
        # Load config file
        config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found")
        config.read(config_file)
        
        # Validate config section and keys
        if "Game" not in config:
            raise ValueError("Config file missing [Game] section")
        required_keys = ["min_range", "max_range", "max_attempts", "db_name", "log_file", "log_level", "history_file"]
        missing_keys = [key for key in required_keys if key not in config["Game"]]
        if missing_keys:
            raise KeyError(f"Missing config keys: {', '.join(missing_keys)}")
        
        # Use CLI args if provided, else config file
        try:
            self.min_range = min_range if min_range is not None else int(config["Game"]["min_range"])
            self.max_range = max_range if max_range is not None else int(config["Game"]["max_range"])
            self.max_attempts = max_attempts if max_attempts is not None else int(config["Game"]["max_attempts"])
        except ValueError:
            raise ValueError("Config values for min_range, max_range, max_attempts must be integers")
        
        self.db_name = config["Game"]["db_name"]
        self.log_file = config["Game"]["log_file"]
        self.log_level = config["Game"]["log_level"]
        self.history_file = config["Game"]["history_file"]
        
        # Validate ranges and attempts
        if self.min_range >= self.max_range:
            raise ValueError("min_range must be less than max_range")
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        
        self.ranges = (self.min_range, self.max_range)
        self.target = None
        self.attempts = 0
        
        # Setup logging
        try:
            logging.basicConfig(
                filename=self.log_file,
                level=getattr(logging, self.log_level, logging.INFO),
                format="%(asctime)s %(levelname)s %(message)s"
            )
        except ValueError:
            logging.basicConfig(
                filename=self.log_file,
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(message)s"
            )
            logging.warning(f"Invalid log_level {self.log_level}, defaulting to INFO")
        
        logging.info(f"Game initialized with config {config_file}, CLI args: min={min_range}, max={max_range}, attempts={max_attempts}")
        
        self.init_csv()
        self.create_table()
    
    def init_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Outcome", "Attempts", "Target"])
            logging.info(f"CSV file {self.history_file} initialized")
    
    def create_table(self):
        """Create SQLite stats table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY,
                    games INTEGER,
                    attempts INTEGER
                )
            """)
            cursor.execute("INSERT OR IGNORE INTO stats (id, games, attempts) VALUES (1, 0, 0)")
            conn.commit()
            conn.close()
            logging.info("Stats table checked/created")
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise
    
    def update_stats(self, attempts):
        """Update game stats in SQLite."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE stats SET games = games + 1, attempts = attempts + ? WHERE id = 1", (attempts,))
            conn.commit()
            conn.close()
            logging.info(f"Stats updated: +1 game, +{attempts} attempts")
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise
    
    def get_stats(self):
        """Retrieve game stats from SQLite."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT games, attempts FROM stats WHERE id = 1")
            games, attempts = cursor.fetchone()
            conn.close()
            return {"games": games, "attempts": attempts}
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise
    
    def save_game(self, outcome, attempts, target):
        """Save game result to CSV."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.history_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, outcome, attempts, target])
            logging.info(f"Game saved to CSV: {outcome}, {attempts}, {target}")
        except IOError as e:
            logging.error(f"CSV write error: {e}")
            raise
    
    def show_stats(self):
        """Display game stats."""
        stats = self.get_stats()
        print(f"\nStats: {stats['games']} games played, {stats['attempts']} total attempts")
    
    def play(self):
        """Run the guessing game."""
        try:
            self.target = random.randint(self.min_range, self.max_range)
            self.attempts = 0
            logging.info(f"New game started, target: {self.target}")
            
            print(f"Guess a number between {self.min_range} and {self.max_range}!")
            
            while self.attempts < self.max_attempts:
                try:
                    guess_input = input("Enter your guess: ")
                    if not guess_input:  # Handle empty input
                        print("Game skipped due to empty input.")
                        logging.info("Game skipped: empty input")
                        return
                    guess = int(guess_input)
                    self.attempts += 1
                    logging.info(f"Player guessed: {guess}")
                    
                    if guess < self.min_range or guess > self.max_range:
                        print(f"Guess must be between {self.min_range} and {self.max_range}!")
                        logging.info(f"Invalid guess {guess}, out of range")
                        return  # Exit on invalid range
                    if guess == self.target:
                        print(f"Outcome: Won in {self.attempts} tries. Target was {self.target}")
                        self.update_stats(self.attempts)
                        self.save_game("Won", self.attempts, self.target)
                        break
                    elif guess < self.target:
                        print("Too low!")
                    else:
                        print("Too high!")
                except ValueError:
                    print("Invalid input! Numbers only. Game skipped.")
                    logging.info("Game skipped: invalid input")
                    return  # Exit on invalid input
            
            if self.attempts >= self.max_attempts and guess != self.target:
                print(f"Outcome: Lost in {self.attempts} tries. Target was {self.target}")
                self.update_stats(self.attempts)
                self.save_game("Lost", self.attempts, self.target)
            
            print(f"Current stats: {self.get_stats()['games']} games, {self.get_stats()['attempts']} attempts")
        except Exception as e:
            logging.error(f"Game error: {e}")
            raise
    
    def __del__(self):
        """Clean up database connection."""
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Number Guessing Game")
    parser.add_argument("--config", default="game.ini", help="Path to config file")
    parser.add_argument("--min", type=int, help="Minimum range for guessing")
    parser.add_argument("--max", type=int, help="Maximum range for guessing")
    parser.add_argument("--attempts", type=int, help="Maximum number of attempts")
    args = parser.parse_args()
    
    try:
        game = GuessGame(
            config_file=args.config,
            min_range=args.min,
            max_range=args.max,
            max_attempts=args.attempts
        )
        game.play()
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error: {e}")
        logging.error(f"Startup error: {e}")