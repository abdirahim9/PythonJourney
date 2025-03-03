import random

def start_game():
    print("Welcome to the Functional Guessing Game!" )
    return {"games": 0, "attempts": 0, "score": 0}

def play_round(stats):
    target= random.randint(1,100)
    print(f"\nGame {stats['games'] + 1}: Guess a number between 1 and 100. 10 tries max! ")
    guess= int(input("Your guess: "))
    attempts= 1
    max_attempts= 10

    while guess != target and attempts < max_attempts:
        if guess < target:
            print(f"Too low! (guess #{attempts} / {max_attempts}) ")
        else:
            print(f"Too high! (guess #{attempts} / {max_attempts}) ")
        guess= int(input("Try again: "))
        attempts += 1

    if guess == target:
        score= max_attempts - attempts + 1
        print(f"You won in {attempts} tries! Score: {score} ")
        stats["score"] += score
    else:
        print(f"Out of tries! The number was {target}. Score: 0 ")
    stats["games"] += 1
    stats["attempts"] += attempts
    return stats
def main():
    stats= start_game()
    play_again= "y"
    while play_again.lower() == "y":
        stats= play_round(stats)
        print(f"stats: {stats['games']} games, {stats['attempts']} attempts, {stats['score']} score ")
        play_again= input("Play again? (y/n): ")
    print(f"\nFinal stats: {stats['games']} games, {stats['attempts']} attempts, {stats['score']} score ")
if __name__ == "__main__":
    main()