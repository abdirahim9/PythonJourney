import random

# Welcome message and initialize stats
print("Welcome to the Number Guessing Game! ")
print("You have 10 attempts per game to guess a number between 1 and 100. ")
games_played= 0
total_attempts= 0
total_score= 0
play_again= "y"

# Main game loop
while play_again.lower() == "y":
    target= random.randint(1,100)
    print(f"\nGame {games_played + 1}: I've picked a number between 1 and 100. ")
    guess= int(input("Your guess: "))
    attempts= 1
    max_attempts= 10

    # Guessing loop with attempt limit
    while guess != target and attempts < max_attempts:
        if guess < target:
            print(f"Too low! (Guess #{attempts}/{max_attempts}) ")
        else:
            print(f"Too high! (Guess #{attempts}/{max_attempts}) ")
        guesses_left = max_attempts - attempts
        print(f"{guesses_left} guesses remaining. ")
        guess= int(input("Try again: "))
        attempts += 1

    # Outcome check
    if guess == target:
        score= max_attempts - attempts + 1 # Score: remaining attempts + 1
        print(f"You got it in {attempts} attempts! Score: {score} ")
        total_score += score
    else:
        print(f"Game over! Out of attempts. The number was {target}. Score: 0")

    # Update stats and replay prompt
    games_played += 1
    total_attempts += attempts
    print(f"Current stats: {games_played} games, {total_attempts} total attempts, {total_score} total score. ")
    play_again= input("Play again? (y/n): ")

#Final summary
print(f"\nThanks for playing! ")
print(f"Final stats: {games_played} games won, {total_attempts} total attempts, {total_score} total score. ")
if games_played > 0:
    avg_attempts= total_attempts / games_played
    print(f"Average attempts per games: {avg_attempts:.2f}")