# Day 1: Hello Script
- 'input()': Asks for 'name' and 'age'-stores what I type.
- 'for _ in range(3)': Loops 3 times-repeats the questions.
- 'tries += 1': Counts each loop-tracks attempts.
- 'print()': Shows  greeting with variables -e.g., "Hello, Abdirahim! At 27, attempt My first Python script-mastery starts here!

# Day 2: Calculator Script
- 'float(input())': Takes number-converts strings to decimals.
- 'Math ops: '+', '-', '*', '/', '//', '%' -compute on 'num1','num2'.
- 'print(f"...)': Formats results-shows all 6 operations cleanly.
My calc does sums to remainders-math in python is on!

# Day 3: Logic Script
- 'int(input())': Takes age-coverts to integer.
- 'if/else': Decides adult/minor-nested 'if checks 21 or 13.
- 'for i in range(5)': Counts 0-4-just loops!
- 'while count <5': Counts with control-stops at 5.
- 'print(f"...)': Shows decisions and counts-logic rules!
My script thinks now-control flow is mine!

# Day 4: Number Guessing Game
- 'import random': Brings 'random.randint(1,100)'-sets a secret 'target'.
- 'int(input())': Gets 'guess'-user's number
- 'if/else': Hints "Too low/high"-guides guesses.
- 'while play_again.lower() == "y"': Replays-keeps going.
-'attempts','games_played': Tracks stats-shows skill. 
My first game-logic and loops!

# Day 5: Enhanced Guessing Game
- 'random.randint(1,100)' : Sets 'target'-random challenge
- 'while play_again.lower() == "y"': Loops games-replay control.
- 'while guess != target and attempts < max_attempts': Limits guesses to 10 attempts.
- 'if guess < target': Guides with "Too low/high"-feedback loop
- 'score = max_attempts - attempts + 1': Scores by attempts left e.g 9 for 4 guesses.
- 'total_scores', 'games_played': Tracks wins-stats shine
- 'avg_attempts = total_attempts /games_played' : Average attempts e.g 3.5
My game's pro now-limits, scores and stats!

# Day 6: Function-Based Guessing game 
- 'import random ': Gets 'randint()' -random targets
- 'def start_game()': Sets up prints welcome, returns 'stats' dict
- 'def main()': Controls flow-calls, functions, loops with 'play_again'.
- 'stats[ "score"] +=score': Updates dict in function-tracks totals
-'if__name__ == "main__": Runs 'main()' standard entry
Functions make my game modular-code's clean now.