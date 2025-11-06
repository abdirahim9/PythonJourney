import random
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests


class Player:
    """Manages player stats, guess history, analysis, visualization, and weather API."""

    def __init__(self):
        self.stats = {"games": 0, "attempts": 0}
        self.guess_history = []
        self.lock = threading.Lock()
        self.weather_data = None

    def load_stats(self, filename="stats.txt"):
        """Load stats from file."""
        with self.lock:
            try:
                with open(filename, "r") as file:
                    data = file.read().strip().split(",")
                    if len(data) != 2:
                        raise ValueError("Invalid stats format")
                    self.stats["games"] = int(data[0])
                    self.stats["attempts"] = int(data[1])
            except (FileNotFoundError, ValueError, IndexError) as e:
                print(f"Loading stats failed: {e}. Starting fresh.")

    def save_stats(self, filename="stats.txt"):
        """Save stats to file."""
        with self.lock:
            try:
                with open(filename, "w") as file:
                    file.write(f"{self.stats['games']},{self.stats['attempts']}")
            except IOError as e:
                print(f"Saving stats failed: {e}")

    def add_guess(self, guess):
        """Add guess to history."""
        with self.lock:
            self.guess_history.append(guess)

    def get_guesses_df(self):
        """Return a DataFrame of guesses."""
        return pd.DataFrame({'guesses': self.guess_history}) if self.guess_history else None

    def fetch_weather_data(self, lat=52.52, lon=13.41):
        """Fetch current weather from Open-Meteo API."""
        if self.weather_data is not None:
            return self.weather_data
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()['current_weather']
            self.weather_data = pd.DataFrame([data])
            return self.weather_data
        except requests.RequestException as e:
            print(f"API fetch failed: {e}. Using default data.")
            return pd.DataFrame([{'temperature': 20.0, 'weathercode': 0}])

    def analyze_guesses(self):
        """Analyze guesses using Pandas and weather fusion."""
        df = self.get_guesses_df()
        if df is None:
            return "No guesses yet."
        weather_df = self.fetch_weather_data()
        temp = weather_df['temperature'].iloc[0]
        adjusted_mean = df['guesses'].mean() + (temp / 10)
        std_dev = df['guesses'].std(ddof=0)
        median = df['guesses'].median()
        mode = df['guesses'].mode()[0] if not df['guesses'].mode().empty else "N/A"
        sorted_guesses = np.sort(df['guesses'].values)
        trend = df['guesses'].rolling(window=5).mean().iloc[-1] if len(df) >= 5 else "Insufficient data"

        # Format trend safely
        trend_str = f"{trend:.2f}" if isinstance(trend, (float, np.floating)) else trend

        return (f"Mean: {df['guesses'].mean():.2f}, Adjusted Mean (Temp {temp}°C): {adjusted_mean:.2f}, "
                f"Std Dev: {std_dev:.2f}, Sorted: {sorted_guesses}, Median: {median:.2f}, Mode: {mode}, "
                f"Recent Trend Mean: {trend_str}")

    def export_guesses_to_csv(self, filename="guesses.csv"):
        df = self.get_guesses_df()
        if df is None:
            print("No guesses to export.")
            return
        df.to_csv(filename, index=False)
        print(f"Guesses exported to {filename}")

    def plot_guess_histogram(self, filename="guess_hist.png"):
        df = self.get_guesses_df()
        if df is None:
            print("No guesses to plot.")
            return
        plt.figure(figsize=(8, 6))
        df['guesses'].hist(bins=10)
        plt.title("Guess Distribution")
        plt.xlabel("Guess Value")
        plt.ylabel("Frequency")
        plt.savefig(filename)
        plt.close()
        print(f"Histogram saved to {filename}")


class Game:
    """Handles a single guessing game."""

    def __init__(self, player):
        self.player = player
        self.ranges = (1, 100)
        self.max_attempts = 10

    def play(self):
        """Run a single game round."""
        self.player.fetch_weather_data()
        target = random.randint(self.ranges[0], self.ranges[1])
        print(f"\nGame {self.player.stats['games'] + 1}: Guess {self.ranges[0]}-{self.ranges[1]}!")
        attempts = 0
        while attempts < self.max_attempts:
            try:
                guess_input = input("Your guess: ")
                guess = int(guess_input)
                if guess < self.ranges[0] or guess > self.ranges[1]:
                    print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                    continue
            except ValueError:
                print("Invalid input! Numbers only. Game skipped.")
                return
            self.player.add_guess(guess)
            attempts += 1
            if guess == target:
                outcome = "Won"
                break
            print("Too low!" if guess < target else "Too high!")
        else:
            outcome = "Lost"

        with self.player.lock:
            self.player.stats["games"] += 1
            self.player.stats["attempts"] += attempts
        self.player.save_stats()
        print(f"Outcome: {outcome} in {attempts} tries")
        print(f"Guess Analysis: {self.player.analyze_guesses()}")


def concurrent_game(player):
    Game(player).play()


def main():
    player = Player()
    player.load_stats()
    threads = []
    play_again = "y"
    while play_again.lower() == "y":
        thread = threading.Thread(target=concurrent_game, args=(player,))
        threads.append(thread)
        thread.start()
        play_again = input("Start another concurrent game? (y/n): ")
    for thread in threads:
        thread.join()
    print(f"\nFinal stats: {player.stats['games']} games, {player.stats['attempts']} attempts")
    print(f"Overall Guess Analysis: {player.analyze_guesses()}")
    player.export_guesses_to_csv()
    player.plot_guess_histogram()


if __name__ == "__main__":
    main()
