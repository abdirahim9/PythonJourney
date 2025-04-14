import unittest
import random
from unittest.mock import patch
from io import StringIO
from db_guess import GuessGame

class TestGuessGame(unittest.TestCase):
    """Tests for GuessGame class."""
    def setUp(self):
        """Set up a fresh game instance for each test."""
        self.game = GuessGame(db_name=":memory:")
        random.seed(42)  # Consistent random numbers for testing
    
    def test_initialization(self):
        """Test game initializes correctly."""
        self.assertEqual(self.game.ranges, (1, 100))
        self.assertEqual(self.game.max_attempts, 10)
        self.assertIsNotNone(self.game.conn)
        self.assertIsNotNone(self.game.cursor)
    
    def test_create_table(self):
        """Test stats table is created correctly."""
        self.game.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stats'")
        table_exists = self.game.cursor.fetchone()
        self.assertIsNotNone(table_exists)
        self.game.cursor.execute("SELECT games, attempts FROM stats WHERE id = 1")
        stats = self.game.cursor.fetchone()
        self.assertEqual(stats, (0, 0))
    
    def test_update_stats(self):
        """Test stats are updated correctly."""
        self.game.update_stats(3)
        stats = self.game.get_stats()
        self.assertEqual(stats["games"], 1)
        self.assertEqual(stats["attempts"], 3)
        self.game.update_stats(2)
        stats = self.game.get_stats()
        self.assertEqual(stats["games"], 2)
        self.assertEqual(stats["attempts"], 5)
    
    def test_play_win(self):
        """Test winning gameplay updates stats."""
        with patch("random.randint", return_value=50), \
             patch("sys.stdin", StringIO("50\nn\n")):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.game.play()
                output = fake_out.getvalue()
                self.assertIn("Outcome: Won in 1 tries", output)
                self.assertIn("Current stats: 1 games, 1 attempts", output)
                stats = self.game.get_stats()
                self.assertEqual(stats["games"], 1)
                self.assertEqual(stats["attempts"], 1)
    
    def test_play_invalid_input(self):
        """Test invalid input skips game."""
        with patch("random.randint", return_value=50), \
             patch("sys.stdin", StringIO("abc\nn\n")):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.game.play()
                output = fake_out.getvalue()
                self.assertIn("Invalid input! Numbers only. Game skipped.", output)
                stats = self.game.get_stats()
                self.assertEqual(stats["games"], 0)
                self.assertEqual(stats["attempts"], 0)
    
    def test_play_out_of_range(self):
        """Test out-of-range guess skips game."""
        with patch("random.randint", return_value=50), \
             patch("sys.stdin", StringIO("150\nn\n")):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.game.play()
                output = fake_out.getvalue()
                self.assertIn("Guess must be between 1 and 100!", output)
                stats = self.game.get_stats()
                self.assertEqual(stats["games"], 0)
                self.assertEqual(stats["attempts"], 0)
    
    def tearDown(self):
        """Clean up database connection."""
        self.game.conn.close()

if __name__ == "__main__":
    unittest.main()