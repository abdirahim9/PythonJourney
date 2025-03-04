import random

def load_stats(filename="stats.txt"):
    try:
        with open(filename, "r") as file:
            data= file.read().split(",")
            return {"games": int(data[0]), "attempts": int(data[1])}
    except FileNotFoundError:
        return {"games": 0, "attempts": 0}
    
def save_stats(stats, filename="stats.txt"):
    with open(filename, "w") as file:
        file.write(f"{stats['games']},{stats['attempts']} ")

def guess_with_file():
    stats= load_stats()    # Load stats from file or initialize
    ranges= (1,100)        # Tuple for range
    print(f"Guess between {ranges[0]} and {ranges[1]}-Stats Saved! ")
    play_again= "y"

    while play_again.lower() == "y":
        target= random.randint(ranges[0], ranges[1])
        print(f"\nGame {stats['games'] + 1}: Guess (1-100), 10 tries max! ")
        guess= int(input("Your guess: "))
        attempts= 1
        max_attempts= 10

        while guess != target and attempts < max_attempts:
            print("Too low! " if guess < target else "Too high! ")
            guess= int(input("Try again: "))
            attempts += 1

        outcome= "Won" if guess == target else "Lost"
        stats["games"] +=1
        stats["attempts"] = stats.get("attempts", 0) + attempts  # Ensure attempts key exists
        save_stats(stats) # Save after each game
        print(f"Outcome: {outcome} in {attempts} tries")
        play_again= input("Play again? (y/n): ")

    print(f"\nFinal stats: {stats['games']} games, {stats['attempts']} total attempts ")

if __name__ == "__main__":
    guess_with_file()        
