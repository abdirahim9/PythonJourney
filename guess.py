import random

print("Welcome to the Number Guessing Game! ")
games_played = 0
total_attempts= 0
play_again= "y"
while play_again.lower() == "y":
    target= random.randint(1,100)
    print("I've picked a number between 1 and 100. ")
    guess= int(input("Your guess: "))
    attempts= 1
    while guess != target:
        if guess < target:
            print(f"Too low! (Guess #{attempts}) ")
        else:
            print(f"Too high! (Guess # {attempts}) ")
        guess= int(input("Try again: "))
        attempts += 1
    print(f"You got it in {attempts} attempts! ")
    games_played += 1
    total_attempts += attempts
    play_again =input("Play again? (y/n): ")
print(f"Thanks for playing! You won {games_played} games in {total_attempts} total attempts. ")    
