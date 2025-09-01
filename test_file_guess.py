import unittest
import sqlite3
import csv
import os
from unittest.mock import patch, call
from csv_guess import GuessGame

class TestGuessGame(unittest.TestCase):
    """Unit tests for GuessGame class in csv_guess.py."""
    def setUp(self):
        """Set up config, DB, and CSV for testing in project directory."""
        self.config_file = "test_game.ini"
        self.db_name = "test_guess_stats.db"
        self.history_file = "test_game_history.csv"
        self.log_file = "test_game.log"
        
        # Reset database by deleting if exists
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        
        # Create test config
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
        
        # Initialize game
        self.game = GuessGame(
            config_file=self.config_file,
            min_range=1,
            max_range=10,
            max_attempts=3
        )
    
    def tearDown(self):
        """Close DB, keep files for inspection."""
        self.game.__del__()
        # Keep files for debugging
        # os.remove(self.config_file)
        # os.remove(self.db_name)
        # os.remove(self.history_file)
        # os.remove(self.log_file)
    
    def test_initialization(self):
        """Test game initialization with config and CLI args."""
        self.assertEqual(self.game.ranges, (1, 10))
        self.assertEqual(self.game.max_attempts, 3)
        self.assertEqual(self.game.db_name, self.db_name)
        self.assertEqual(self.game.history_file, self.history_file)
    
    def test_csv_initialization(self):
        """Test CSV file initialization with headers."""
        with open(self.history_file, "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertEqual(headers, ["Timestamp", "Outcome", "Attempts", "Target"])
    
    def test_db_initialization(self):
        """Test SQLite database initialization."""
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
        with patch("builtins.print") as mock_print:
            self.game.play()
            self.assertEqual(self.game.get_stats(), {"games": 1, "attempts": 1})
            mock_print.assert_any_call("Outcome: Won in 1 tries. Target was 5")
            mock_print.assert_any_call("Current stats: 1 games, 1 attempts")
        with open(self.history_file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip headers
            rows = list(reader)  # Read all rows
            self.assertGreater(len(rows), 0, "No data rows in CSV")
            row = rows[-1]  # Get the last row
            self.assertEqual(row[1], "Won")
            self.assertEqual(int(row[2]), 1)
            self.assertEqual(int(row[3]), 5)
    
    @patch("builtins.input", side_effect=["1", "2", "3"])
    @patch("random.randint", return_value=5)
    def test_play_lose(self, mock_randint, mock_input):
        """Test a losing game scenario."""
        with patch("builtins.print") as mock_print:
            self.game.play()
            self.assertEqual(self.game.get_stats(), {"games": 1, "attempts": 3})
            mock_print.assert_any_call("Outcome: Lost in 3 tries. Target was 5")
            mock_print.assert_any_call("Current stats: 1 games, 3 attempts")
        with open(self.history_file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip headers
            rows = list(reader)  # Read all rows
            self.assertGreater(len(rows), 0, "No data rows in CSV")
            row = rows[-1]  # Get the last row
            self.assertEqual(row[1], "Lost")
            self.assertEqual(int(row[2]), 3)
            self.assertEqual(int(row[3]), 5)
    
    @patch("builtins.input", side_effect=["abc"])
    def test_invalid_input(self, mock_input):
        """Test invalid input handling."""
        with patch("builtins.print") as mock_print:
            self.game.play()
            mock_print.assert_any_call("Invalid input! Numbers only. Game skipped.")
            self.assertEqual(self.game.get_stats(), {"games": 0, "attempts": 0})
    
    @patch("builtins.input", side_effect=["11"])
    def test_out_of_range_guess(self, mock_input):
        """Test out-of-range guess handling."""
        with patch("builtins.print") as mock_print:
            self.game.play()
            mock_print.assert_any_call("Guess must be between 1 and 10!")
            self.assertEqual(self.game.get_stats(), {"games": 0, "attempts": 0})
    
    def test_invalid_config(self):
        """Test initialization with invalid config."""
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
    
    def test_stats_display(self):
        """Test stats display functionality."""
        self.game.update_stats(5)
        with patch("builtins.print") as mock_print:
            self.game.show_stats()
            mock_print.assert_called_with("\nStats: 1 games played, 5 total attempts")

if __name__ == "__main__":
    unittest.main()