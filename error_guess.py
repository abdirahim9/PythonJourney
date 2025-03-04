import random

def load_stats(filename="stats.txt"):
    """Load game stats from file, return defaults on error."""
    try:
        with open(filename, "r") as file:
            data= file.read() .strip() .split(",")
            if len(data) != 2:
                raise ValueError("Invalid stats format")
            return {"games": int(data[0]), "attempts": int(data[1])}
    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error loading stats: {e}. Starting fresh. ")
        return {"games": 0, "attempts": 0}
    
def save_stats(stats,filename="stats.txt"):
    """Save game stats to file."""
    try:
        with open(filename, "w") as file:
            file.write(f"{stats['games']}, {stats['attempts']}")
    except IOError as e:
        print(f"Error saving stats: {e}")

def guess_with_file():
    """Run guessing game with error handling and file persistence."""
    stats= load_stats()
    ranges= (1,100)
    print(f"Guess between {ranges[0]} and {ranges[1]}-Safe and Saved! ")
    play_again= "y"

    while play_again.lower() == "y":
        target= random.randint(ranges[0], ranges[1])
        print(f"\nGame {stats['games'] + 1}: Guess (1-100), 10 tries max! ")
        try:
            guess= int(input("Your guess: "))
            if guess < ranges[0] or guess > ranges[1]:
                print(f"Guess must be between {ranges[0]} and {ranges[1]}! ")
                continue
            attempts= 1
            max_attempts= 10

            while guess != target and attempts < max_attempts:
                print("Too low!" if guess < target else "Too high! ")
                try:
                    guess= int(input("Try again: "))
                    if guess < ranges[0] or guess > ranges[1]:
                        print(f"Guess must be between {ranges[0]} and {ranges[1]}! ")
                        continue
                    attempts += 1
                except ValueError:
                    print("Invalid input! Numbers only. Try again. ")
                    continue

                outcome= "Won" if guess == target else "Lost"
                stats["games"] += 1
                stats["attempts"] = stats.get("attempts", 0) + attempts
                save_stats(stats)
                print(f"Outcome: {outcome} in {attempts} tries ")
        except ValueError:
            print("Invalid input! Numbers only. Game skipped. ") 

        play_again= input("Play again? (y/n): ")

    print(f"\nFinal stats: {stats['games']} games, {stats['attempts']} total attempts")
if __name__ == "__main__":
    guess_with_file()                                