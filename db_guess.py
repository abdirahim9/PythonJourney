import random
import sqlite3

class GuessGame:
    """Manages a number guessing game with SQLite stats."""
    def __init__(self, db_name="guess_stats.db"):
        self.ranges = (1, 100)
        self.max_attempts = 10
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        """Create stats table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                games INTEGER DEFAULT 0,
                attempts INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()
        self.cursor.execute("SELECT COUNT(*) FROM stats")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO stats (games, attempts) VALUES (0, 0)")
            self.conn.commit()
    
    def update_stats(self, attempts):
        """Update games and attempts in the database."""
        self.cursor.execute("UPDATE stats SET games = games + 1, attempts = attempts + ? WHERE id = 1", (attempts,))
        self.conn.commit()
    
    def get_stats(self):
        """Fetch current stats from the database."""
        self.cursor.execute("SELECT games, attempts FROM stats WHERE id = 1")
        games, attempts = self.cursor.fetchone()
        return {"games": games, "attempts": attempts}
    
    def play(self):
        """Run a game round and update stats."""
        target = random.randint(self.ranges[0], self.ranges[1])
        print(f"\nGuess a number between {self.ranges[0]} and {self.ranges[1]}!")
        try:
            guess = int(input("Your guess: "))
            if guess < self.ranges[0] or guess > self.ranges[1]:
                print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                return
            attempts = 1
            while guess != target and attempts < self.max_attempts:
                print("Too low!" if guess < target else "Too high!")
                try:
                    guess = int(input("Try again: "))
                    if guess < self.ranges[0] or guess > self.ranges[1]:
                        print(f"Guess must be between {self.ranges[0]} and {self.ranges[1]}!")
                        return
                    attempts += 1
                except ValueError:
                    print("Invalid input! Numbers only.")
                    return
            outcome = "Won" if guess == target else "Lost"
            self.update_stats(attempts)
            stats = self.get_stats()
            print(f"Outcome: {outcome} in {attempts} tries. Target was {target}")
            print(f"Current stats: {stats['games']} games, {stats['attempts']} attempts")
        except ValueError:
            print("Invalid input! Numbers only. Game skipped.")
    
    def __del__(self):
        """Close database connection."""
        self.conn.close()

def main():
    """Main game loop."""
    game = GuessGame()
    play_again = "y"
    while play_again.lower() == "y":
        game.play()
        play_again = input("Play again? (y/n): ").strip()
        if play_again.lower() not in ["y", "n"]:
            print("Invalid input! Assuming 'n'.")
            play_again = "n"
    stats = game.get_stats()
    print(f"\nFinal stats: {stats['games']} games, {stats['attempts']} attempts")

if __name__ == "__main__":
    main()