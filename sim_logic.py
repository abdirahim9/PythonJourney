import random
import numpy as np
import pandas as pd

class Signal:
    """Represents a cosmic signal with generation logic."""
    def __init__(self, length=10, frequency=5):
        self.length = length
        self.frequency = frequency
        self.data = self.generate()
   
    def generate(self):
        """Generate signal data using lists and loops."""
        data = []
        for i in range(self.length):
            val = random.randint(0, 100) + (i % self.frequency) * 10  # Loop-based pattern
            data.append(val)
        return data
   
    def analyze(self):
        """Basic analysis with NumPy for efficiency."""
        arr = np.array(self.data)
        return f"Mean: {arr.mean():.2f}, Std: {arr.std():.2f}"

class Simulator:
    """Manages cosmic signal simulations with OOP modular design."""
    def __init__(self):
        self.signals = []
   
    def add_signal(self, signal):
        """Add a signal to the simulator."""
        self.signals.append(signal)
   
    def run_simulation(self):
        """Run simulation and return combined data."""
        combined = []
        for signal in self.signals:
            combined.extend(signal.data)
        df = pd.DataFrame({'signal_data': combined})
        return df.describe().to_dict()

def main():
    sim = Simulator()
    signal1 = Signal(length=20)
    sim.add_signal(signal1)
    print("Signal 1 Analysis:", signal1.analyze())
    results = sim.run_simulation()
    print("Simulation Results:", results)

if __name__ == "__main__":
    main()