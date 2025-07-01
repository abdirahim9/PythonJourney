import unittest
import sqlite3
import argparse
from unittest.mock import patch, Mock
from cli_guess import GuessGame

class TestGuessGame(unittest.TestCase):
    """Unit tests for GuessGame class."""
    def setUp(self):
        """Set up test environment with in-memory database."""
        self.config_file = "game.ini"
        self.game = GuessGame(config_file=self.config_file)
        self.game.conn = sqlite3.connect(":memory:")
        self.game.cursor = self.game.conn.cursor()
        self.game.create_table()
    
    def tearDown(self):
        """Clean up database connection."""
        self.game.conn.close()
    
    def test_initialization(self):
        """Test game initialization with config."""
        self.assertEqual(self.game.ranges, (1, 100))
        self.assertEqual(self.game.max_attempts, 10)
        self.assertEqual(self.game.db_name, "guess_stats.db")
        self.assertEqual(self.game.log_file, "game.log")
    
    def test_initialization_with_cli_args(self):
        """Test initialization with CLI arguments."""
        game = GuessGame(config_file=self.config_file, min_range=10, max_range=50, max_attempts=5)
        self.assertEqual(game.ranges, (10, 50))
        self.assertEqual(game.max_attempts, 5)
    
    def test_create_table(self):
        """Test stats table creation."""
        self.game.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stats'")
        table_exists = self.game.cursor.fetchone()
        self.assertIsNotNone(table_exists)
        self.game.cursor.execute("SELECT games, attempts FROM stats WHERE id=1")
        stats = self.game.cursor.fetchone()
        self.assertEqual(stats, (0, 0))
    
    def test_update_stats(self):
        """Test updating stats in database."""
        self.game.update_stats(3)
        stats = self.game.get_stats()
        self.assertEqual(stats["games"], 1)
        self.assertEqual(stats["attempts"], 3)
    
    def test_get_stats(self):
        """Test retrieving stats from database."""
        self.game.cursor.execute("UPDATE stats SET games=2, attempts=5 WHERE id=1")
        self.game.conn.commit()
        stats = self.game.get_stats()
        self.assertEqual(stats["games"], 2)
        self.assertEqual(stats["attempts"], 5)
    
    def test_show_stats(self):
        """Test displaying stats."""
        self.game.cursor.execute("UPDATE stats SET games=2, attempts=5 WHERE id=1")
        self.game.conn.commit()
        with patch("builtins.print") as mocked_print:
            self.game.show_stats()
            mocked_print.assert_called_with("\nStats: 2 games played, 5 total attempts")
    
    @patch("random.randint")
    @patch("builtins.input")
    def test_play_win(self, mocked_input, mocked_randint):
        """Test winning game scenario."""
        mocked_randint.return_value = 50
        mocked_input.side_effect = ["50"]
        with patch("builtins.print") as mocked_print:
            self.game.play()
            mocked_print.assert_any_call("Outcome: Won in 1 tries. Target was 50")
            stats = self.game.get_stats()
            self.assertEqual(stats["games"], 1)
            self.assertEqual(stats["attempts"], 1)
    
    @patch("random.randint")
    @patch("builtins.input")
    def test_play_lose(self, mocked_input, mocked_randint):
        """Test losing game scenario."""
        self.game.max_attempts = 2
        mocked_randint.return_value = 50
        mocked_input.side_effect = ["40", "60"]
        with patch("builtins.print") as mocked_print:
            self.game.play()
            mocked_print.assert_any_call("Outcome: Lost in 2 tries. Target was 50")
            stats = self.game.get_stats()
            self.assertEqual(stats["games"], 1)
            self.assertEqual(stats["attempts"], 2)
    
    @patch("builtins.input")
    def test_play_invalid_input(self, mocked_input):
        """Test invalid input handling."""
        mocked_input.side_effect = ["abc"]
        with patch("builtins.print") as mocked_print:
            self.game.play()
            mocked_print.assert_any_call("Invalid input! Numbers only. Game skipped.")
            stats = self.game.get_stats()
            self.assertEqual(stats["games"], 0)
            self.assertEqual(stats["attempts"], 0)
    
    def test_invalid_range(self):
        """Test invalid range error."""
        with self.assertRaises(ValueError):
            GuessGame(config_file=self.config_file, min_range=100, max_range=1)

if __name__ == "__main__":
    unittest.main()