import random
import numpy as np
import pandas as pd
import time  # For benchmarking
import matplotlib.pyplot as plt
import json  # For persistence
import os  # For file checks
import requests
import threading  # For concurrency

API_KEY = "fdbae91e525f6e0434b93525b75caf57"  # Replace with your OpenWeatherMap API key
CITY = "London"  # Customizable city

class Signal:
    """Represents a cosmic signal with recursive pattern generation."""
    def __init__(self, length=10, frequency=5, scale=1.0, depth=3, data=None):
        self.length = length
        self.frequency = frequency
        self.scale = scale
        self.depth = depth  # Fuse: Recursive depth (e.g., from temp)
        if data is not None:
            self.data = np.array(data)
        else:
            self.data = self.generate()

    def generate_recursive(self, base, current_depth):
        """Recursive helper for fractal patterns."""
        if current_depth == 0:
            return base
        pattern = (np.arange(len(base)) % self.frequency) * 10 / current_depth
        new_base = base + pattern
        return self.generate_recursive(new_base, current_depth - 1)

    def generate(self):
        """Generate signal data with recursion."""
        try:
            base = np.random.randint(0, 101, size=self.length)
            data = self.generate_recursive(base, self.depth)
            return data * self.scale
        except RecursionError as e:
            print(f"Recursion error: {e}. Using base.")
            return base * self.scale

    def analyze(self):
        """Analyze signal using mean and population standard deviation."""
        mean_val = np.mean(self.data)
        std_val = np.std(self.data, ddof=0)  # population std
        return f"Mean: {mean_val:.2f}, Std: {std_val:.2f}"

    def to_dict(self):
        """Serialize signal to dict for JSON."""
        return {
            'length': self.length,
            'frequency': self.frequency,
            'scale': self.scale,
            'depth': self.depth,
            'data': self.data.tolist()
        }

class Simulator:
    """Manages cosmic signal simulations with thread safety."""
    def __init__(self):
        self.signals = []
        self.lock = threading.Lock()  # For thread safety

    def add_signal(self, signal):
        """Add a Signal object to the simulation (thread-safe)."""
        with self.lock:
            self.signals.append(signal)

    def run_simulation(self):
        """Return mean and population standard deviation of all signals."""
        with self.lock:
            if not self.signals:
                return {'signal_data': {'mean': 0.0, 'std': 0.0}}
            combined = np.concatenate([s.data for s in self.signals])
        results = {
            'signal_data': {
                'mean': np.mean(combined),
                'std': np.std(combined, ddof=0)  # population std
            }
        }
        return results

    def analyze_with_pandas(self):
        """Pandas-based analysis on combined data."""
        with self.lock:
            if not self.signals:
                return pd.DataFrame()
            combined = np.concatenate([s.data for s in self.signals])
        df = pd.DataFrame({'signal_data': combined})
        return df.describe()

    def visualize(self, filename="signal_hist.png"):
        """Visualize combined signals with Matplotlib histogram."""
        with self.lock:
            if not self.signals:
                print("No signals to visualize.")
                return
            combined = np.concatenate([s.data for s in self.signals])
        plt.figure(figsize=(8, 6))
        plt.hist(combined, bins=20)
        plt.title("Signal Data Distribution")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.savefig(filename)
        plt.close()
        print(f"Histogram saved to {filename}")

    def save_state(self, filename="sim_state.json"):
        """Save simulator state to JSON."""
        try:
            with self.lock:
                state = [s.to_dict() for s in self.signals]
            with open(filename, 'w') as f:
                json.dump(state, f)
            print(f"State saved to {filename}")
        except IOError as e:
            print(f"Save failed: {e}")

    def load_state(self, filename="sim_state.json"):
        """Load simulator state from JSON."""
        if not os.path.exists(filename):
            print(f"No file {filename} to load.")
            return
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
            with self.lock:
                self.signals = [Signal(length=s['length'], frequency=s['frequency'], scale=s['scale'], depth=s.get('depth', 3), data=s['data']) for s in state]
            print(f"State loaded from {filename}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Load failed: {e}")

def fetch_weather_depth():
    """Fetch weather temp as recursion depth (e.g., int(temp/10))."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        temp = response.json()['main']['temp']
        return int(temp / 10) + 1  # e.g., 3 for 20-29C, min 1
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}. Using default depth.")
        return 3  # Fallback

def fetch_weather_scale():
    """Fetch weather scale factor (e.g., based on humidity)."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        humidity = response.json()['main']['humidity']
        return humidity / 100.0  # Scale factor between 0.0 and 1.0
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}. Using default scale.")
        return 1.0  # Fallback

# -------------------
# Benchmarking functions
# -------------------
def benchmark_loop_version(length=100_000):
    start = time.time()
    data = []
    for i in range(length):
        val = random.randint(0, 100) + (i % 5) * 10
        data.append(val)
    end = time.time()
    return end - start

def benchmark_numpy_version(length=100_000):
    start = time.time()
    base = np.random.randint(0, 101, size=length)
    pattern = (np.arange(length) % 5) * 10
    data = base + pattern
    end = time.time()
    return end - start

def concurrent_generate(sim, length=20, depth=3, scale=1.0):
    signal = Signal(length=length, depth=depth, scale=scale)
    sim.add_signal(signal)

def main():
    # Fuse API into simulation
    depth = fetch_weather_depth()
    scale = fetch_weather_scale()
    sim = Simulator()
    sim.load_state()  # Load persistent if exists
    # Concurrent simulations with recursion
    threads = []
    for _ in range(4):  # 4 concurrent
        t = threading.Thread(target=concurrent_generate, args=(sim, 20, depth, scale))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("Concurrent Recursive Signals Added.")
    results = sim.run_simulation()
    print("Simulation Results:", results)
    pandas_df = sim.analyze_with_pandas()
    print("Pandas Analysis:\n", pandas_df)
    sim.visualize()
    sim.save_state()  # Save for restart-safety
    # Benchmark
    loop_time = benchmark_loop_version()
    numpy_time = benchmark_numpy_version()
    print(f"Loop version (100k): {loop_time:.4f}s")
    print(f"NumPy version (100k): {numpy_time:.4f}s")
    print(f"Speedup: {loop_time / numpy_time:.2f}x")

if __name__ == "__main__":
    main()