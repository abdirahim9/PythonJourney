import random
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests

API_KEY = "YOUR_API_KEfdbae91e525f6e0434b93525b75caf57Y"  # Replace with your OpenWeatherMap API key
CITY = "London"  # Customizable city


class Player:
    """Manages player stats, file I/O, guess history with Pandas analysis, visualization, and API trends."""

    def __init__(self):
        self.stats = {"games": 0, "attempts": 0}
        self.guess_history = []  # List for guesses
        self.weather_data = []  # List for API weather entries
        self.lock = threading.Lock()

    def load_stats(self, filename="stats.txt"):
        """Load stats from file, default to 0 on error."""
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
        """Add guess to history for analysis."""
        with self.lock:
            self.guess_history.append(guess)

    def fetch_weather(self):
        """Fetch current weather from OpenWeatherMap API and add to data."""
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            weather_entry = {
                'temp': data['main']['temp'],
                'condition': data['weather'][0]['main']
            }
            with self.lock:
                self.weather_data.append(weather_entry)
            return weather_entry
        except requests.exceptions.RequestException as e:
            print(f"API error: {e}. Using default values.")
            return {'temp': 20.0, 'condition': 'Clear'}  # Fallback

    def get_weather_trends_df(self):
        """Get Pandas DataFrame from weather data for trends."""
        if not self.weather_data:
            return None
        df = pd.DataFrame(self.weather_data)
        avg_temp_by_condition = df.groupby('condition')['temp'].mean().to_dict()
        return avg_temp_by_condition

    def get_guesses_df(self):
        """Get Pandas DataFrame from guess history."""
        return pd.DataFrame({'guesses': self.guess_history}) if self.guess_history else None

    def analyze_guesses(self):
        """Use Pandas for analysis, fused with weather trends."""
        df = self.get_guesses_df()
        if df is None:
            return "No guesses yet."

        mean = df['guesses'].mean()
        std_dev = df['guesses'].std(ddof=0)
        median = df['guesses'].median()
        mode = df['guesses'].mode()[0] if not df['guesses'].mode().empty else "N/A"
        sorted_guesses = np.sort(df['guesses'].values)
        trend = df['guesses'].rolling(window=5).mean().iloc[-1] if len(df) >= 5 else "Insufficient data"
        weather_trends = self.get_weather_trends_df() or "No weather data"

        # ✅ Fix: conditional formatting outside the f-string
        trend_str = f"{trend:.2f}" if isinstance(trend, (float, int)) else str(trend)

        return (
            f"Mean: {mean:.2f}, "
            f"Std Dev: {std_dev:.2f}, "
            f"Sorted: {sorted_guesses}, "
            f"Median: {median:.2f}, "
            f"Mode: {mode}, "
            f"Recent Trend Mean: {trend_str}, "
            f"Weather Trends: {weather_trends}"
        )

    def export_guesses_to_csv(self, filename="guesses.csv"):
        """Export guess history to CSV using Pandas."""
        df = self.get_guesses_df()
        if df is None:
            print("No guesses to export.")
            return
        df.to_csv(filename, index=False)
        print(f"Guesses exported to {filename}")

    def plot_guess_histogram(self, filename="guess_hist.png"):
        """Plot histogram of guesses using Matplotlib."""
        df = self.get_guesses_df()
        if df is None:
            print("No guesses to plot.")
            return
        plt.figure(figsize=(8, 6))
        df['guesses'].hist(bins=10, color='skyblue', edgecolor='black')
        plt.title("Guess Distribution")
        plt.xlabel("Guess Value")
        plt.ylabel("Frequency")
        plt.grid(False)
        plt.savefig(filename)
        plt.close()
        print(f"Histogram saved to {filename}")


class Game:
    """Handles guessing game logic with API-fused difficulty."""

    def __init__(self, player):
        self.player = player
        weather = self.player.fetch_weather()
        temp = weather['temp']
        # Ensure range stays reasonable even for cold temps
        if temp > 20:
            self.ranges = (1, int(100 + temp))
        else:
            self.ranges = (1, max(10, int(100 - (20 - temp))))
        self.max_attempts = 10

    def play(self):
        """Run a single game round, adding guesses to history."""
        target = random.randint(self.ranges[0], self.ranges[1])
        print(f"\nGame {self.player.stats['games'] + 1}: Guess {self.ranges[0]}-{self.ranges[1]}! (Weather-adjusted)")
        try:
            guess = int(input("Your guess: "))
            if guess < self.ranges[0] or guess > self.ranges[1]:
                print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                return
            self.player.add_guess(guess)
            attempts = 1
            while guess != target and attempts < self.max_attempts:
                print("Too low!" if guess < target else "Too high!")
                try:
                    guess = int(input("Try again: "))
                    if guess < self.ranges[0] or guess > self.ranges[1]:
                        print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                        return
                    self.player.add_guess(guess)
                    attempts += 1
                except ValueError:
                    print("Invalid input! Numbers only.")
                    return

            outcome = "Won" if guess == target else "Lost"
            with self.player.lock:
                self.player.stats["games"] += 1
                self.player.stats["attempts"] += attempts
            self.player.save_stats()
            print(f"Outcome: {outcome} in {attempts} tries")
            print(f"Guess Analysis: {self.player.analyze_guesses()}")
        except ValueError:
            print("Invalid input! Numbers only. Game skipped.")


def concurrent_game(player):
    """Wrapper to run games in separate threads."""
    game = Game(player)
    game.play()


def main():
    """Main game loop with API trends, analysis, export, and plot."""
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
