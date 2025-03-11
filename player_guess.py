import random

class Player:
    """Manages player stats and file I/O."""
    def __init__(self):
        self.stats= {"games": 0, "attempts": 0}

    def load_stats(self, filename="stats.txt"):
        """Load stats from file, default to 0 on error."""
        try:
            with open(filename, "r") as file:
                data= file.read().strip().split(",")
                if len(data) != 2:
                    raise ValueError("Invalid stats format")
                self.stats["games"] = int(data[0])
                self.stats["attempts"] = int(data[1])
        except (FileNotFoundError, ValueError, IndexError) as e:
            print(f"Loading stats failed: {e}. Starting fresh.")

    def save_stats(self, filename="stats.txt"):
        """Save stats to file."""
        try:
            with open(filename, "w") as file:
                file.write(f"{self.stats['games']},{self.stats['attempts']} ")
        except IOError as e:
            print(f"Saving stats failed: {e}")

class Game:
    """Handles guessing game logic."""
    def __init__(self, player):
        self.player= player
        self.ranges= (1,100)
        self.max_attempts= 10

    def play(self):
        """Run a single game round. """
        target= random.randint(self.ranges[0], self.ranges[1])
        print(f"\nGame {self.player.stats['games'] + 1}: Guess {self.ranges[0]}-{self.ranges[1]}! ")
        try:
            guess= int(input("Your guess: "))
            if guess < self.ranges[0] or guess > self.ranges[1]:
                print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}! ")
                return
            attempts= 1
            while guess != target and attempts < self.max_attempts:
                print("Too low!" if guess < target else "Too high! ")
                try:
                    guess= int(input("Try again:"))
                    if guess < self.ranges[0] or guess > self.ranges[1]:
                        print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                        return
                    attempts += 1
                except ValueError:
                    print("Invalid input! Numbers only.")
                    return
            outcome= "Won" if guess == target else "Lost"
            self.player.stats["games"] += 1
            self.player.stats["attempts"] += attempts
            self.player.save_stats()
            print(f"Outcome: {outcome} in {attempts} tries")
        except ValueError:
            print("Invalid input! Numbers only. Game skipped. ")

def main():
    """Main game loop."""
    player= Player()
    player.load_stats()
    play_again= "y"
    while play_again.lower() == "y":
        game= Game(player)
        game.play()
        play_again= input("Play again? (y/n): ")
    print(f"\nFinal stats: {player.stats['games']} games, {player.stats['attempts']} attempts")

if __name__ == "__main__":
    main()