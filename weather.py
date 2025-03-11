import random
import requests
import os

class Player:
    """Tracks player stats with file persistence."""
    def __init__(self, name, filename="stats.txt"):
        self.name = name
        self.filename = filename
        self.stats = self.load_stats()

    def load_stats(self):
        """Load stats from file, default to 0 on error."""
        try:
            with open(self.filename, "r") as file:
                data = file.read().strip().split(",")
                if len(data) != 2:
                    raise ValueError("Invalid stats format")
                return {"games": int(data[0]), "attempts": int(data[1])}
        except (FileNotFoundError, ValueError, IndexError) as e:
            print(f"Loading stats failed: {e}. Starting fresh.")
            return {"games": 0, "attempts": 0}

    def save_stats(self):
        """Save stats to file."""
        try:
            with open(self.filename, "w") as file:
                file.write(f"{self.stats['games']},{self.stats['attempts']}")
        except IOError as e:
            print(f"Saving stats failed: {e}")

    def update_stats(self, attempts):
        """Update games and attempts, save to file."""
        self.stats["games"] += 1
        self.stats["attempts"] += attempts
        self.save_stats()

class WeatherGame:
    """Guessing game with real weather data."""
    def __init__(self, player, api_key):
        self.player = player
        self.api_key = api_key
        self.ranges = (-50, 50)  # Realistic temp range
        self.max_attempts = 10

    def get_weather(self, city="London"):
        """Fetch current temperature from OpenWeatherMap."""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            temp = int(data["main"]["temp"] - 273.15)
            if temp < self.ranges[0] or temp > self.ranges[1]:
                raise ValueError(f"Temperature {temp}°C out of expected range")
            return temp
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Weather fetch failed: {e}. Using random target.")
            return random.randint(self.ranges[0], self.ranges[1])

    def play(self):
        """Run a game round guessing the temperature."""
        target = self.get_weather()
        print(f"\nGame {self.player.stats['games'] + 1}: Guess {self.player.name}'s city temp (Celsius)!")
        try:
            guess = int(input("Your guess: "))
            if guess < self.ranges[0] or guess > self.ranges[1]:
                print(f"Temperature must be between {self.ranges[0]}°C and {self.ranges[1]}°C!")
                return
            attempts = 1
            while guess != target and attempts < self.max_attempts:
                print(f"Too {'low' if guess < target else 'high'}! (Hint: {max(self.ranges[0], target - 5)} to {min(self.ranges[1], target + 5)})")
                try:
                    guess = int(input("Try again: "))
                    if guess < self.ranges[0] or guess > self.ranges[1]:
                        print(f"Temperature must be between {self.ranges[0]}°C and {self.ranges[1]}°C!")
                        return
                    attempts += 1
                except ValueError:
                    print("Invalid input! Numbers only.")
                    return
            outcome = "Won" if guess == target else "Lost"
            self.player.update_stats(attempts)
            print(f"Outcome: {outcome} in {attempts} tries. Actual temp: {target}°C")
        except ValueError:
            print("Invalid input! Numbers only. Game skipped.")

def main():
    """Main game loop."""
    api_key = "fdbae91e525f6e0434b93525b75caf57"  # Replace with your OpenWeatherMap API key
    player = Player("User")
    game = WeatherGame(player, api_key)
    play_again = "y"
    while play_again.lower() == "y":
        game.play()
        play_again = input("Play again? (y/n): ").strip()
        if play_again.lower() not in ["y", "n"]:
            print("Invalid input! Assuming 'n'.")
            play_again = "n"
    print(f"\nFinal stats for {player.name}: {player.stats['games']} games, {player.stats['attempts']} attempts")

if __name__ == "__main__":
    main()