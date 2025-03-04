import random

def play_game_with_lists():
    guesses= [] # list to store guesses per game
    stats= {"games": 0, "attempts": 0, "score": 0}  # Dictionary for stats
    print("Guess the Number-Track Your Guesses! ")
    play_again= "y"

    while play_again.lower() == "y":
        target= random.randint(1,100)
        print(f"\nGame {stats['games'] + 1}: Guess (1-100), 10 tries! ")
        guess = int(input("Your guess: "))
        guesses.append(guess)   # Add first guess to list
        attempts= 1
        max_attempts= 10

        while guess != target and attempts < max_attempts:
            if guess < target:
                print(f"Too low! Guess #{attempts} ")
            else:
                print("Too high! Guess #{attempts} ")
            guess= int(input("Try again: "))
            guesses.append(guess)  # Add each guess to list
            attempts += 1

        if guess == target:
            score= max_attempts - attempts + 1
            print(f"Got it in {attempts}! Score: {score} ")
            stats["score"] += score
        else:
            print(f"Failed! Number was {target} ")
        stats["games"] += 1
        stats["attempts"] += attempts
        print(f"Guesses this game: {guesses [-attempts:]} ")  # Show last game's guesses
        guesses = []   # Reset list for next game
        play_again= input("Play again? (y/n): ")
    print(f"Stats: {stats} ")
if __name__ == "__main__":
    play_game_with_lists()              