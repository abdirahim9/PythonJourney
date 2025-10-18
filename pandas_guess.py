import random
import threading
import numpy as np
import pandas as pd

class Player:
    """Manages player stats, file I/O, guess history with Pandas DataFrame analysis."""
    def __init__(self):
        self.stats = {"games": 0, "attempts": 0}
        self.guess_history = []  # List for guesses; converted to DF for analysis
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
    
    def analyze_guesses(self):
        """Use Pandas for DataFrame analysis: mean, std, median, mode, trends."""
        if not self.guess_history:
            return "No guesses yet."
        df = pd.DataFrame({'guesses': self.guess_history})
        mean = df['guesses'].mean()
        std_dev = df['guesses'].std(ddof=0)  # Match NumPy ddof=0
        median = df['guesses'].median()
        mode = df['guesses'].mode()[0] if not df['guesses'].mode().empty else "N/A"
        
        sorted_guesses = np.sort(df['guesses'].values)
        # Format sorted guesses as space-separated without numpy types
        sorted_str = "[" + " ".join(str(x) for x in sorted_guesses) + "]"
        
        trend = df['guesses'].rolling(window=5).mean().iloc[-1] if len(df) >= 5 else "Insufficient data"
        trend_str = f"{trend:.2f}" if isinstance(trend, float) else str(trend)
        
        return (f"Mean: {mean:.2f}, Std Dev: {std_dev:.2f}, Sorted: {sorted_str}, "
                f"Median: {median:.2f}, Mode: {mode}, Recent Trend Mean: {trend_str}")
    
    def export_guesses_to_csv(self, filename="guesses.csv"):
        """Export guess history to CSV using Pandas."""
        if not self.guess_history:
            print("No guesses to export.")
            return
        df = pd.DataFrame({'guesses': self.guess_history})
        df.to_csv(filename, index=False)
        print(f"Guesses exported to {filename}")

class Game:
    """Handles guessing game logic with Pandas-integrated stats."""
    def __init__(self, player):
        self.player = player
        self.ranges = (1, 100)
        self.max_attempts = 10
    
    def play(self):
        """Run a single game round, adding guesses to history."""
        target = random.randint(self.ranges[0], self.ranges[1])
        print(f"\nGame {self.player.stats['games'] + 1}: Guess {self.ranges[0]}-{self.ranges[1]}!")
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
    game = Game(player)
    game.play()

def main():
    """Main game loop with final Pandas analysis and CSV export."""
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

if __name__ == "__main__":
    main()
