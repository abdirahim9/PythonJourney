import random
import threading
import numpy as np

class Player:
    """Manages player stats, file I/O, and guess history with NumPy analysis."""
    def __init__(self):
        self.stats = {"games": 0, "attempts": 0}
        self.guess_history = []  # List to store all guesses for analysis
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
        """Add guess to history for NumPy analysis."""
        with self.lock:
            self.guess_history.append(guess)
    
    def analyze_guesses(self):
        """Use NumPy to analyze guess history: mean, std dev, sorted."""
        if not self.guess_history:
            return "No guesses yet."
        guesses_array = np.array(self.guess_history)
        mean = np.mean(guesses_array)
        std_dev = np.std(guesses_array)
        sorted_guesses = np.sort(guesses_array)
        return f"Mean: {mean:.2f}, Std Dev: {std_dev:.2f}, Sorted: {sorted_guesses}"

class Game:
    """Handles guessing game logic with NumPy-integrated stats."""
    def __init__(self, player):
        self.player = player
        self.ranges = (1, 100)
        self.max_attempts = 10
    
    def play(self):
        """Run a single game round, adding guesses to history."""
        target = 79
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
    """Main game loop with final NumPy analysis."""
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

if __name__ == "__main__":
    main()