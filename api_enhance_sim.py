import random
import numpy as np
import pandas as pd
import time # For benchmarking
import matplotlib.pyplot as plt
import requests

API_KEY = "fdbae91e525f6e0434b93525b75caf57" # Replace with your OpenWeatherMap API key
CITY = "London" # Customizable city

class Signal:
    """Represents a cosmic signal with NumPy vectorized generation."""
    def __init__(self, length=10, frequency=5, scale=1.0):
        self.length = length
        self.frequency = frequency
        self.scale = scale  # Fuse: Scale by API data (e.g., temp factor)
        self.data = self.generate()
    def generate(self):
        """Generate signal data using NumPy arrays (vectorized)."""
        base = np.random.randint(0, 101, size=self.length) # Random integers 0-100
        pattern = (np.arange(self.length) % self.frequency) * 10 # Repeating pattern
        return (base + pattern) * self.scale  # Fuse: Apply scale
    def analyze(self):
        """Analyze signal using mean and population standard deviation."""
        mean_val = np.mean(self.data)
        std_val = np.std(self.data, ddof=0) # population std
        return f"Mean: {mean_val:.2f}, Std: {std_val:.2f}"
class Simulator:
    """Manages cosmic signal simulations."""
    def __init__(self):
        self.signals = []
    def add_signal(self, signal):
        """Add a Signal object to the simulation."""
        self.signals.append(signal)
    def run_simulation(self):
        """Return mean and population standard deviation of all signals."""
        if not self.signals:
            return {'signal_data': {'mean': 0.0, 'std': 0.0}}
        combined = np.concatenate([s.data for s in self.signals])
        results = {
            'signal_data': {
                'mean': np.mean(combined),
                'std': np.std(combined, ddof=0) # population std
            }
        }
        return results
    def analyze_with_pandas(self):
        """Pandas-based analysis on combined data."""
        if not self.signals:
            return pd.DataFrame()
        combined = np.concatenate([s.data for s in self.signals])
        df = pd.DataFrame({'signal_data': combined})
        return df.describe()
    def visualize(self, filename="signal_hist.png"):
        """Visualize combined signals with Matplotlib histogram."""
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
def fetch_weather_scale():
    """Fetch weather temp as scale factor from API."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        temp = response.json()['main']['temp'] / 100  # Normalize to scale (e.g., 0.2 for 20C)
        return temp
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
def main():
    # Fuse API into simulation
    scale = fetch_weather_scale()
    sim = Simulator()
    signal1 = Signal(length=20, scale=scale)
    sim.add_signal(signal1)
    print("Signal 1 Analysis (Scaled):", signal1.analyze())
    results = sim.run_simulation()
    print("Simulation Results:", results)
    pandas_df = sim.analyze_with_pandas()
    print("Pandas Analysis:\n", pandas_df)
    sim.visualize()
    # Benchmark
    loop_time = benchmark_loop_version()
    numpy_time = benchmark_numpy_version()
    print(f"Loop version (100k): {loop_time:.4f}s")
    print(f"NumPy version (100k): {numpy_time:.4f}s")
    print(f"Speedup: {loop_time / numpy_time:.2f}x")
if __name__ == "__main__":
    main()