# Day 1: Hello Script

- 'input()': Asks for 'name' and 'age'-stores what I type.
- 'for \_ in range(3)': Loops 3 times-repeats the questions.
- 'tries += 1': Counts each loop-tracks attempts.
- 'print()': Shows greeting with variables -e.g., "Hello, Abdirahim! At 27, attempt My first Python script-mastery starts here!

# Day 2: Calculator Script

- 'float(input())': Takes number-converts strings to decimals.
- 'Math ops: '+', '-', '\*', '/', '//', '%' -compute on 'num1','num2'.
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
  -'if**name** == "main\_\_": Runs 'main()' standard entry
  Functions make my game modular-code's clean now.

# Day 7: Lists and Dictionaries in Guessing Game (list_dict.py)

- 'guesses =[]': Empty list-stores each game's guesses.
- 'guesses.append(guess)': Adds guesses-builds histroy (e.g [50, 80,60,55])
- 'stats ={"games": 0, ...}: Updates dict-tracks totals.
- 'guesses[-attempts:]': Slices list shows last game's tries
- 'guesses =[]': Resets list fresh for next game
  Lists track guesses, dicts manage stats-data's great!

# Day 8: Tuples and Sets in Guessing Game

- 'ranges= (1,100)': Tuple immutable min/max for randint()'.
- 'guess_histroy = set()': Set-stores unique guesses (e.g 50, 82)
- 'random.randint(range[0], ranges[1])': Uses tuple dynamic range
- 'sorted (guess_history)': Sorts set for display-e.g [50, 72]
- 'guess_history = set()': Resets fresh uniques per game
  Tuples look ranges, sets track uniques-data preciseness!

# Day 9: File I/O in Guessing Game

- 'def load_stats()': Reads 'stats.txt'-loads games, attempts (e.g 3,19).
- 'with open(..., "r)': Opens file-reads via 'file.read().split(",").
- 'except FileNotFoundError': Defaults to 0-handles no file case.
  -'def save_stats(stats)': Writes stats-e.g "3,16" to 'stats.txt'.
- 'with open(..., "w")': Overwrites file saves after each game.
- 'stats[ "attempts"] = stats.get(...)': Updates dict-safe key access.
  Stats persist acroos runs file I/O understood!

# Day 10: Error Handling in Guessing Game

- 'try: ... except ValueError': Outer-catches first guess errors (e.g "abc"), skips game
- 'try:... except ValueError': Inner-catches loop guesses, retries without counting.
- 'if guess < range [0]': Validates range skips out of bounds (e.g, 0,101)
- 'except (FileNotFoundError, ValueError, IndexError)':'load stats' handles file issues, defaults to 0.
- 'raise ValueError ("Invalid stats format")': Flags bad file data e.g "2" instead of "2,6"
- 'except IOError': save_stats'-logs write fails, game continues.
  Error-proof game-handles all crashes with grace!

# Day 11: Intro to OOP with Guessing Game

- 'class player': Holds self.stats'-encapsulates stats and file I/O.
- 'def **init** (self)': Sets initial stats-OOP constructor
- 'load_stats(slef)':Loads from 'stats.txt'-instance method
- 'class Game': Runs gameplay-links to 'Player' via 'self.player'.
- 'play(self)': Handles guessing-updates 'self.player.stats.'
- 'self' everywhere: Ties data to instances-OOP core!
  First OPP step structured, reusable code!

# Day 12: OOP with API in Weather Game

- 'class Player': Persists 'self.stats' in 'stats.txt'- file I/O restored
- 'class WeatherGame': Fetches temp via API-timeout, range checks.
- 'get weather()': 'timeout=5', catches 'KeyError'-bulletproof API
- API key: Integrated in main()'-simplified execution.
- Hint bounds: 'ma/min'-valid hints always
- 'main()': Validates replay-error-free loop
  Robust weather guessing-OOP + API with integrated key!

# Day 13: Algorithms with Sorted Guessing Game

- `class GuessGame`: Tracks `self.guesses`—OOP with history.
- `bubble_sort(self, arr)`: Sorts guesses—O(n²) algorithm.
- `self.guesses.copy()`: Preserves original list—sorted per game.
- `play()`: Adds guesses, sorts, displays—algorithm meets game.
- Final sorted history: Full session sorted—clean output.
  First algorithm—bubble sort nailed!

# Day 14: Recursion with Guessing Game

- `class GuessGame`: Tracks `self.guesses`—OOP foundation.
- `binary_hint(self, target, low, high, depth)`: Recursive hints—binary search style.
- `depth > 10`: Base case—prevents stack overflow.
- `play()`: Integrates hints—smarter guidance.
- Final history: Unsorted guesses—raw player input.
  Recursion rocks—intelligent hints nails it!

# Day 15: Data Persistence with Guessing Game

- `class GuessGame`: Manages game with SQLite—OOP + DB.
- `create_table()`: Sets up `stats` table—single-row design.
- `update_stats(self, attempts)`: Persists games, attempts—parameterized query.
- `get_stats()`: Fetches live stats—real-time feedback.
- `__del__()`: Closes connection—clean resource management.
  SQLite persistence—Week 3 capped well!

# Day 16: Unit Testing with Guessing Game
- `TestGuessGame`: Tests `db_guess.py`—`unittest` suite.
- `setUp()`: Uses `:memory:` DB—clean test environment.
- Tests: Table creation, stats updates, win, invalid input, out-of-range.
- Mocking: `patch` for `randint`, `stdin`, `stdout`—isolates gameplay.
- `tearDown()`: Closes DB—resource cleanup.
Testing rigor—`db_guess.py` solid!

# Day 17: Logging with Guessing Game
- `GuessGame`: Extends `db_guess.py`—OOP with SQLite, logging.
- `logging.basicConfig`: Sets `game.log`—INFO level, timestamped.
- Logs: Initialization, guesses, outcomes, errors, stats updates.
- Levels: `INFO` for events, `WARNING` for range issues, `ERROR` for invalid inputs.
- `__del__`: Logs DB closure—clean exit.
Logging adds debug power—game events clear!

# Day 18: Configuration with Guessing Game
- `GuessGame`: Extends `log_guess.py`—OOP with SQLite, logging, config.
- `configparser`: Loads `game.ini`—range, attempts, DB, log settings.
- Error Handling: Catches `KeyError`, `ValueError`, `sqlite3.Error`—logs issues.
- Dynamic Logging: Sets level from `game.ini`—flexible debugging.
- Validation: Checks `min_range < max_range`—robust config.
Config-driven game—settings made scalable!

# Day 19: CLI with Guessing Game
- `GuessGame`: Extends `config_guess.py`—OOP with SQLite, logging, config, CLI.
- `argparse`: Adds `--min`, `--max`, `--attempts`, `--stats`—customizes game.
- CLI Priority: Overrides `game.ini` settings—flexible control.
- `show_stats()`: Displays stats for `--stats`—user-friendly.
- Error Handling: Logs `FileNotFoundError`, `sqlite3.Error`, CLI errors.
CLI-driven game—ultimate user control!