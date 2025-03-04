import random

def game_with_structures():
    guess_history= set()      # Set for unique guesses across all games
    ranges= (1,100)           # Tuple for immutable range
    stats={"games": 0}        # Dictionary for minimal stats
    print(f"Guess between {ranges[0]} and {ranges[1]}! ")
    play_again= "y"
    
    while play_again.lower() == "y":
        target= random.randint(ranges[0], ranges[1])
        print(f"\nGame {stats['games'] + 1}: Start guessing! ")
        guess= int(input("Guess: "))
        guess_history.add(guess)   # Add guess to set (duplicates ignored)
        attempts= 1
        max_attempts= 10

        while guess != target and attempts < max_attempts:
            print("Too low!" if guess < target else "Too high! ")
            guess= int(input("Guess again: "))
            guess_history.add(guess)    # Add each guess to set
            attempts += 1

        outcome= "Won" if guess == target else "Lost"
        print(f"Outcome: {outcome} in {attempts} tries")
        stats["games"] += 1
        print(f"Unique guesses so far: {sorted(guess_history)} ")
        guess_history= set()   # Reset set for next game
        play_again= input("Play again? (y/n): ")

    print(f"Total games: {stats['games']} ")

if __name__ == "__main__":
    game_with_structures()            
