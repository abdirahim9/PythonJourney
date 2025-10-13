import unittest
import numpy as np
from io import StringIO
import sys
import threading
import os
from unittest.mock import patch
from numpy_guess import Player, Game  # Make sure this matches your module name

class TestPlayer(unittest.TestCase):
    """Unit tests for Player class."""
    
    def setUp(self):
        """Setup a fresh Player instance for each test."""
        self.player = Player()
    
    def test_load_stats_success(self):
        """Test successful stats loading."""
        with open("stats.txt", "w") as f:
            f.write("5,15")
        self.player.load_stats()
        self.assertEqual(self.player.stats["games"], 5)
        self.assertEqual(self.player.stats["attempts"], 15)
    
    def test_load_stats_error(self):
        """Test stats loading on error (fresh start)."""
        if os.path.exists("stats.txt"):
            os.remove("stats.txt")
        original_stdout = sys.stdout
        sys.stdout = StringIO()
        self.player.load_stats()
        output = sys.stdout.getvalue()
        sys.stdout = original_stdout
        self.assertIn("Loading stats failed", output)
        self.assertEqual(self.player.stats["games"], 0)
        self.assertEqual(self.player.stats["attempts"], 0)
    
    def test_analyze_guesses_empty(self):
        """Test analysis on empty history."""
        result = self.player.analyze_guesses()
        self.assertEqual(result, "No guesses yet.")
    
    def test_analyze_guesses_valid(self):
        """Test NumPy analysis on valid guesses."""
        self.player.guess_history = [50, 80, 72]
        result = self.player.analyze_guesses()
        self.assertIn("Mean: 67.33", result)
        self.assertIn("Std Dev: 12.68", result)  # np.std with ddof=0
        self.assertIn("Sorted: [50 72 80]", result)
    
    def test_add_guess_thread_safe(self):
        """Test thread-safe guess addition."""
        def add_guesses():
            for _ in range(100):
                self.player.add_guess(42)
        
        threads = [threading.Thread(target=add_guesses) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(len(self.player.guess_history), 1000)

class TestGame(unittest.TestCase):
    """Unit tests for Game class."""
    
    def setUp(self):
        self.player = Player()
        self.game = Game(self.player)
    
    @patch('builtins.input', side_effect=["50", "60", "52"])
    @patch('random.randint', return_value=52)
    def test_play_win(self, mock_randint, mock_input):
        """Test game play with a winning scenario."""
        original_stdout = sys.stdout
        sys.stdout = StringIO()

        self.game.play()

        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__

        self.assertIn("Outcome: Won in 3 tries", output)
        self.assertEqual(self.player.stats["games"], 1)
        self.assertEqual(self.player.stats["attempts"], 3)
    
    @patch('builtins.input', side_effect=["abc"])
    def test_play_invalid_input(self, mock_input):
        """Test game play with invalid input."""
        original_stdout = sys.stdout
        sys.stdout = StringIO()

        self.game.play()

        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__

        self.assertIn("Invalid input! Numbers only. Game skipped.", output)
        self.assertEqual(self.player.stats["games"], 0)

if __name__ == "__main__":
    unittest.main()
