import unittest
import numpy as np
import pandas as pd
from io import StringIO
import sys
import threading
import os
from unittest.mock import patch, MagicMock
from requests_api import Player, Game
import requests


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player()

    def test_load_stats_success(self):
        with open("stats.txt", "w") as f:
            f.write("5,15")
        self.player.load_stats()
        self.assertEqual(self.player.stats["games"], 5)
        self.assertEqual(self.player.stats["attempts"], 15)

    def test_load_stats_error(self):
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
        self.assertEqual(self.player.analyze_guesses(), "No guesses yet.")

    def test_analyze_guesses_valid(self):
        self.player.guess_history = [50, 80, 72]
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {'current_weather': {'temperature': 20.0, 'weathercode': 0}}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            result = self.player.analyze_guesses()
        self.assertIn("Mean: 67.33", result)
        self.assertIn("Adjusted Mean (Temp 20.0°C): 69.33", result)
        self.assertIn("Std Dev: 12.68", result)
        self.assertIn("Sorted: [50 72 80]", result)
        self.assertIn("Median: 72.00", result)
        self.assertIn("Mode: 50", result)
        self.assertIn("Recent Trend Mean: Insufficient data", result)

    def test_analyze_guesses_trend(self):
        self.player.guess_history = [50, 60, 70, 80, 90]
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {'current_weather': {'temperature': 20.0, 'weathercode': 0}}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            result = self.player.analyze_guesses()
        self.assertIn("Recent Trend Mean: 70.00", result)

    def test_export_guesses_to_csv(self):
        self.player.guess_history = [50, 80, 72]
        filename = "test_guesses.csv"
        if os.path.exists(filename):
            os.remove(filename)
        original_stdout = sys.stdout
        sys.stdout = StringIO()
        self.player.export_guesses_to_csv(filename)
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn(f"Guesses exported to {filename}", output)
        df = pd.read_csv(filename)
        self.assertEqual(list(df['guesses']), [50, 80, 72])
        os.remove(filename)

    def test_plot_guess_histogram(self):
        self.player.guess_history = [50, 80, 72]
        filename = "test_hist.png"
        if os.path.exists(filename):
            os.remove(filename)
        with patch('matplotlib.pyplot.savefig') as mock_savefig:
            original_stdout = sys.stdout
            sys.stdout = StringIO()
            self.player.plot_guess_histogram(filename)
            output = sys.stdout.getvalue()
            sys.stdout = sys.__stdout__
            self.assertIn(f"Histogram saved to {filename}", output)
            mock_savefig.assert_called_once_with(filename)

    def test_fetch_weather_data_success(self):
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {'current_weather': {'temperature': 15.0, 'weathercode': 1}}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            df = self.player.fetch_weather_data()
        self.assertEqual(df['temperature'].iloc[0], 15.0)
        self.assertIsNotNone(self.player.weather_data)

    def test_fetch_weather_data_error(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Connection error")
            original_stdout = sys.stdout
            sys.stdout = StringIO()
            df = self.player.fetch_weather_data()
            output = sys.stdout.getvalue()
            sys.stdout = sys.__stdout__
            self.assertIn("API fetch failed", output)
            self.assertEqual(df['temperature'].iloc[0], 20.0)

    def test_add_guess_thread_safe(self):
        def add_guesses():
            for _ in range(100):
                self.player.add_guess(42)
        threads = [threading.Thread(target=add_guesses) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(self.player.guess_history), 1000)


class TestGame(unittest.TestCase):

    def setUp(self):
        self.player = Player()
        self.game = Game(self.player)

    @patch('builtins.input', side_effect=["50", "90", "82"])
    @patch('random.randint', return_value=82)
    @patch('requests.get')
    def test_play_win(self, mock_get, mock_randint, mock_input):
        mock_response = MagicMock()
        mock_response.json.return_value = {'current_weather': {'temperature': 20.0, 'weathercode': 0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        original_stdout = sys.stdout
        sys.stdout = StringIO()
        self.game.play()
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn("Outcome: Won in 3 tries", output)
        self.assertEqual(self.player.stats["games"], 1)
        self.assertEqual(self.player.stats["attempts"], 3)

    @patch('builtins.input', side_effect=["abc", "50"])  # Fixed StopIteration
    @patch('requests.get')
    def test_play_invalid_input(self, mock_get, mock_input):
        mock_response = MagicMock()
        mock_response.json.return_value = {'current_weather': {'temperature': 20.0, 'weathercode': 0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        original_stdout = sys.stdout
        sys.stdout = StringIO()
        self.game.play()
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn("Invalid input! Numbers only. Game skipped.", output)
        self.assertEqual(self.player.stats["games"], 0)


if __name__ == "__main__":
    unittest.main()
