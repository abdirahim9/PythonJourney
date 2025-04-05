import random

class GuessGame:
    """Manages a number guessing game with recursive hints."""
    def __init__(self):
        self.ranges = (1, 100)
        self.max_attempts = 10
        self.guesses = []
    
    def binary_hint(self, target, low, high, depth=0):
        """Recursively suggest a guess range using binary search logic."""
        if low > high or depth > 10:  # Prevent infinite recursion
            return f"Range too narrow or too deep! Guess between {self.ranges[0]} and {self.ranges[1]}"
        mid = (low + high) // 2
        if mid == target:
            return "You're so close! Guess again."
        elif mid < target:
            hint = f"Try between {mid} and {high}"
            return self.binary_hint(target, mid + 1, high, depth + 1)
        else:
            hint = f"Try between {low} and {mid}"
            return self.binary_hint(target, low, mid - 1, depth + 1)
    
    def play(self):
        """Run a game round with recursive hints."""
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
                hint = self.binary_hint(target, self.ranges[0], self.ranges[1])
                print(f"Too {'low' if guess < target else 'high'}! {hint}")
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
            print(f"Outcome: {outcome} in {attempts} tries. Target was {target}")
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
    print(f"\nFinal guess history: {game.guesses}")

if __name__ == "__main__":
    main()