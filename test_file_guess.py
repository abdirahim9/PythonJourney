import unittest
import sqlite3
import csv
import os
import logging
import json
from unittest.mock import patch, call
from csv_guess import GuessGame

class TestGuessGame(unittest.TestCase):
    """Unit tests for GuessGame class in csv_guess.py."""
    def setUp(self):
        """Set up config, DB, and CSV for testing in project directory."""
        self.config_file = "test_game.ini"
        self.json_config_file = "test_game.json"
        self.db_name = "test_guess_stats.db"
        self.history_file = "test_game_history.csv"
        self.log_file = "test_game.log"
        
        # Reset database and files
        for file in [self.db_name, self.history_file, self.log_file, 
                    "test_guess_stats.json.db", "test_game_history.json.csv", "test_game.json.log"]:
            if os.path.exists(file):
                os.remove(file)
        
        # Create test INI config
        with open(self.config_file, "w") as f:
            f.write(
                "[Game]\n"
                "min_range = 1\n"
                "max_range = 10\n"
                "max_attempts = 3\n"
                "db_name = {}\n"
                "log_file = {}\n"
                "log_level = INFO\n"
                "history_file = {}\n"
                "test_db_name = {}\n"
                "test_history_file = {}\n".format(
                    self.db_name, self.log_file, self.history_file,
                    self.db_name, self.history_file
                )
            )
        
        # Create test JSON config
        with open(self.json_config_file, "w") as f:
            json.dump({
                "Game": {
                    "min_range": 5,
                    "max_range": 15,
                    "max_attempts": 4,
                    "db_name": "test_guess_stats.json.db",
                    "log_file": "test_game.json.log",
                    "log_level": "INFO",
                    "history_file": "test_game_history.json.csv",
                    "test_db_name": "test_guess_stats.json.db",
                    "test_history_file": "test_game_history.json.csv"
                }
            }, f)
    
    def tearDown(self):
        """Close DB, keep files for inspection."""
        pass
    
    def test_initialization(self):
        """Test game initialization with INI config and CLI args."""
        game = GuessGame(config_file=self.config_file, min_range=1, max_range=10, max_attempts=3)
        self.assertEqual(game.ranges, (1, 10))
        self.assertEqual(game.max_attempts, 3)
        self.assertEqual(game.db_name, self.db_name)
        self.assertEqual(game.history_file, self.history_file)
    
    def test_csv_initialization(self):
        """Test CSV file initialization with headers."""
        game = GuessGame(config_file=self.config_file)
        with open(self.history_file, "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertEqual(headers, ["Timestamp", "Outcome", "Attempts", "Target"])
    
    def test_db_initialization(self):
        """Test SQLite database initialization."""
        game = GuessGame(config_file=self.config_file)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stats'")
        self.assertIsNotNone(cursor.fetchone())
        cursor.execute("SELECT games, attempts FROM stats WHERE id = 1")
        stats = cursor.fetchone()
        self.assertEqual(stats, (0, 0))
        conn.close()
    
    @patch("builtins.input", side_effect=["5", "5"])
    @patch("random.randint", return_value=5)
    def test_play_win(self, mock_randint, mock_input):
        """Test a winning game scenario."""
        game = GuessGame(config_file=self.config_file)
        with patch("builtins.print") as mock_print:
            game.play()
            self.assertEqual(game.get_stats(), {"games": 1, "attempts": 1})
            mock_print.assert_any_call("Outcome: Won in 1 tries. Target was 5")
            mock_print.assert_any_call("Current stats: 1 games, 1 attempts")
        with open(self.history_file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip headers
            rows = list(reader)
            self.assertGreater(len(rows), 0, "No data rows in CSV")
            row = rows[-1]
            self.assertEqual(row[1], "Won")
            self.assertEqual(int(row[2]), 1)
            self.assertEqual(int(row[3]), 5)
    
    @patch("builtins.input", side_effect=["1", "2", "3"])
    @patch("random.randint", return_value=5)
    def test_play_lose(self, mock_randint, mock_input):
        """Test a losing game scenario."""
        game = GuessGame(config_file=self.config_file)
        with patch("builtins.print") as mock_print:
            game.play()
            self.assertEqual(game.get_stats(), {"games": 1, "attempts": 3})
            mock_print.assert_any_call("Outcome: Lost in 3 tries. Target was 5")
            mock_print.assert_any_call("Current stats: 1 games, 3 attempts")
        with open(self.history_file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip headers
            rows = list(reader)
            self.assertGreater(len(rows), 0, "No data rows in CSV")
            row = rows[-1]
            self.assertEqual(row[1], "Lost")
            self.assertEqual(int(row[2]), 3)
            self.assertEqual(int(row[3]), 5)
    
    @patch("builtins.input", side_effect=["abc", ""])
    def test_invalid_input(self, mock_input):
        """Test invalid input handling."""
        game = GuessGame(config_file=self.config_file)
        with patch("builtins.print") as mock_print:
            game.play()
            mock_print.assert_any_call("Invalid input! Numbers only. Game skipped.")
            self.assertEqual(game.get_stats(), {"games": 0, "attempts": 0})
    
    @patch("builtins.input", side_effect=["11", ""])
    def test_out_of_range_guess(self, mock_input):
        """Test out-of-range guess handling."""
        game = GuessGame(config_file=self.config_file)
        with patch("builtins.print") as mock_print:
            game.play()
            mock_print.assert_any_call("Guess must be between 1 and 10!")
            self.assertEqual(game.get_stats(), {"games": 0, "attempts": 0})
    
    def test_invalid_config(self):
        """Test initialization with invalid INI config."""
        with open(self.config_file, "w") as f:
            f.write(
                "[Game]\n"
                "min_range = 10\n"
                "max_range = 1\n"
                "max_attempts = 3\n"
                "db_name = test_guess_stats.db\n"
                "log_file = test_game.log\n"
                "log_level = INFO\n"
                "history_file = test_game_history.csv\n"
                "test_db_name = test_guess_stats.db\n"
                "test_history_file = test_game_history.csv\n"
            )
        with self.assertRaises(ValueError) as cm:
            GuessGame(config_file=self.config_file)
        self.assertEqual(str(cm.exception), "min_range must be less than max_range")
    
    def test_missing_config_file(self):
        """Test initialization with missing config file."""
        with self.assertRaises(FileNotFoundError) as cm:
            GuessGame(config_file="nonexistent.ini")
        self.assertEqual(str(cm.exception), "Config file nonexistent.ini not found")
    
    def test_missing_config_keys(self):
        """Test initialization with missing INI config keys."""
        with open(self.config_file, "w") as f:
            f.write("[Game]\nmin_range = 1\nmax_range = 10")
        with self.assertRaises(KeyError) as cm:
            GuessGame(config_file=self.config_file)
        self.assertTrue("Missing config keys" in str(cm.exception))
    
    def test_invalid_log_level(self):
        """Test initialization with invalid log level."""
        with open(self.config_file, "w") as f:
            f.write(
                "[Game]\n"
                "min_range = 1\n"
                "max_range = 10\n"
                "max_attempts = 3\n"
                "db_name = test_guess_stats.db\n"
                "log_file = test_game.log\n"
                "log_level = INVALID\n"
                "history_file = test_game_history.csv\n"
                "test_db_name = test_guess_stats.db\n"
                "test_history_file = test_game_history.csv\n"
            )
        game = GuessGame(config_file=self.config_file)
        self.assertEqual(logging.getLogger().getEffectiveLevel(), logging.INFO)
    
    def test_invalid_config_values(self):
        """Test initialization with non-integer INI config values."""
        with open(self.config_file, "w") as f:
            f.write(
                "[Game]\n"
                "min_range = abc\n"
                "max_range = 10\n"
                "max_attempts = 3\n"
                "db_name = test_guess_stats.db\n"
                "log_file = test_game.log\n"
                "log_level = INFO\n"
                "history_file = test_game_history.csv\n"
                "test_db_name = test_guess_stats.db\n"
                "test_history_file = test_game_history.csv\n"
            )
        with self.assertRaises(ValueError) as cm:
            GuessGame(config_file=self.config_file)
        self.assertEqual(str(cm.exception), "Config values for min_range, max_range, max_attempts must be integers")
    
    def test_stats_display(self):
        """Test stats display functionality."""
        game = GuessGame(config_file=self.config_file)
        game.update_stats(5)
        with patch("builtins.print") as mock_print:
            game.show_stats()
            mock_print.assert_called_with("\nStats: 1 games played, 5 total attempts")
    
    @patch("sys.argv", ["csv_guess.py", "--min", "5", "--max", "15", "--attempts", "4"])
    def test_cli_args(self):
        """Test initialization with CLI arguments."""
        game = GuessGame(config_file=self.config_file, min_range=5, max_range=15, max_attempts=4)
        self.assertEqual(game.ranges, (5, 15))
        self.assertEqual(game.max_attempts, 4)
    
    @patch("sys.argv", ["csv_guess.py", "--config", "custom.ini"])
    def test_cli_config_file(self):
        """Test CLI INI config file override."""
        with open("custom.ini", "w") as f:
            f.write(
                "[Game]\n"
                "min_range = 10\n"
                "max_range = 20\n"
                "max_attempts = 5\n"
                "db_name = custom_guess_stats.db\n"
                "log_file = custom_game.log\n"
                "log_level = INFO\n"
                "history_file = custom_game_history.csv\n"
                "test_db_name = custom_guess_stats.db\n"
                "test_history_file = custom_game_history.csv\n"
            )
        game = GuessGame(config_file="custom.ini")
        self.assertEqual(game.ranges, (10, 20))
        self.assertEqual(game.max_attempts, 5)
        self.assertEqual(game.db_name, "custom_guess_stats.db")
        self.assertEqual(game.history_file, "custom_game_history.csv")
    
    @patch("sys.argv", ["csv_guess.py", "--min", "20", "--max", "10"])
    def test_invalid_cli_args(self):
        """Test invalid CLI arguments."""
        with self.assertRaises(ValueError) as cm:
            GuessGame(config_file=self.config_file, min_range=20, max_range=10)
        self.assertEqual(str(cm.exception), "min_range must be less than max_range")
    
    @patch("sys.argv", ["csv_guess.py", "--attempts", "-1"])
    def test_negative_attempts_cli(self):
        """Test negative max_attempts in CLI."""
        with self.assertRaises(ValueError) as cm:
            GuessGame(config_file=self.config_file, max_attempts=-1)
        self.assertEqual(str(cm.exception), "max_attempts must be positive")
    
    def test_json_config_initialization(self):
        """Test initialization with JSON config."""
        game = GuessGame(config_file=self.json_config_file)
        self.assertEqual(game.ranges, (5, 15))
        self.assertEqual(game.max_attempts, 4)
        self.assertEqual(game.db_name, "test_guess_stats.json.db")
        self.assertEqual(game.history_file, "test_game_history.json.csv")
    
    def test_invalid_json_config(self):
        """Test initialization with invalid JSON config."""
        with open(self.json_config_file, "w") as f:
            f.write("{invalid json}")
        with self.assertRaises(ValueError) as cm:
            GuessGame(config_file=self.json_config_file)
        self.assertTrue("Invalid JSON" in str(cm.exception))
    
    def test_missing_json_config_keys(self):
        """Test initialization with missing JSON config keys."""
        with open(self.json_config_file, "w") as f:
            json.dump({"Game": {"min_range": 5, "max_range": 15}}, f)
        with self.assertRaises(KeyError) as cm:
            GuessGame(config_file=self.json_config_file)
        self.assertTrue("Missing config keys" in str(cm.exception))
    
    @patch("sys.argv", ["csv_guess.py", "--config", "test_game.json"])
    def test_cli_json_config_file(self):
        """Test CLI JSON config file override."""
        game = GuessGame(config_file=self.json_config_file)
        self.assertEqual(game.ranges, (5, 15))
        self.assertEqual(game.max_attempts, 4)
        self.assertEqual(game.db_name, "test_guess_stats.json.db")
        self.assertEqual(game.history_file, "test_game_history.json.csv")

if __name__ == "__main__":
    unittest.main()