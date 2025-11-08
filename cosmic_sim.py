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
        return [random.randint(0, 100) for _ in range(self.length)]
   
    def analyze(self):
        """Basic analysis with NumPy for efficiency."""
        arr = np.array(self.data)
        return f"Mean: {arr.mean():.2f}, Std: {arr.std():.2f}"  # population std

class Simulator:
    """Manages cosmic signal simulations with OOP modular design."""
    def __init__(self):
        self.signals = []
   
    def add_signal(self, signal):
        """Add a signal to the simulator."""
        self.signals.append(signal)
   
    def run_simulation(self):
        """Run simulation and return combined data."""
        if not self.signals:
            return {"signal_data": {"mean": 0.0, "std": 0.0}}

        signal = self.signals[0]  # match your test assumption
        arr = np.array(signal.data)
        return {
            "signal_data": {
                "mean": arr.mean(),
                "std": arr.std()  # population std
            }
        }

def main():
    sim = Simulator()
    signal1 = Signal(length=20)
    sim.add_signal(signal1)
    print("Signal 1 Analysis:", signal1.analyze())
    results = sim.run_simulation()
    print("Simulation Results:", results)

if __name__ == "__main__":
    main()
