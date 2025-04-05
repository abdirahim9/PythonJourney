import random

class GuessGame:
    """Manages a number guessing game with sorted history."""
    def __init__(self):
        self.ranges = (1, 100)
        self.max_attempts = 10
        self.guesses = []
    
    def bubble_sort(self, arr):
        """Sort an array using bubble sort algorithm."""
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr
    
    def play(self):
        """Run a single game round and sort guesses."""
        target = random.randint(self.ranges[0], self.ranges[1])
        print(f"\nGuess a number between {self.ranges[0]} and {self.ranges[1]}!")
        try:
            guess = int(input("Your guess: "))
            if guess < self.ranges[0] or guess > self.ranges[1]:
                print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                return
            attempts = 1
            self.guesses.append(guess)
            while guess != target and attempts < self.max_attempts:
                print("Too low!" if guess < target else "Too high!")
                try:
                    guess = int(input("Try again: "))
                    if guess < self.ranges[0] or guess > self.ranges[1]:
                        print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                        return
                    attempts += 1
                    self.guesses.append(guess)
                except ValueError:
                    print("Invalid input! Numbers only.")
                    return
            outcome = "Won" if guess == target else "Lost"
            sorted_guesses = self.bubble_sort(self.guesses.copy())
            print(f"Outcome: {outcome} in {attempts} tries. Target was {target}")
            print(f"Sorted guesses this game: {sorted_guesses}")
        except ValueError:
            print("Invalid input! Numbers only. Game skipped.")

def main():
    """Main game loop."""
    game = GuessGame()
    play_again = "y"
    while play_again.lower() == "y":
        game.play()
        play_again = input("Play again? (y/n): ").strip()
        if play_again.lower() not in ["y", "n"]:
            print("Invalid input! Assuming 'n'.")
            play_again = "n"
    sorted_history = game.bubble_sort(game.guesses.copy())
    print(f"\nFinal sorted guess history: {sorted_history}")

if __name__ == "__main__":
    main()