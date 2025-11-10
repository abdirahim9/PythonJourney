import unittest
import numpy as np
import pandas as pd
from sim_logic import Signal, Simulator # Updated import from Day 37 file
class TestSignal(unittest.TestCase):
    """Unit tests for Signal class."""
   
    def test_generate(self):
        """Test signal generation."""
        signal = Signal(length=5)
        self.assertEqual(len(signal.data), 5)
        self.assertTrue(all(0 <= x <= 140 for x in signal.data)) # Adjusted for pattern
   
    def test_analyze(self):
        """Test signal analysis."""
        signal = Signal(length=5)
        signal.data = [10, 20, 30, 40, 50] # Mock for consistency
        result = signal.analyze()
        self.assertIn("Mean: 30.00", result)
        self.assertIn("Std: 14.14", result)
class TestSimulator(unittest.TestCase):
    """Unit tests for Simulator class."""
   
    def test_add_signal(self):
        """Test adding signals."""
        sim = Simulator()
        signal = Signal()
        sim.add_signal(signal)
        self.assertEqual(len(sim.signals), 1)
   
    def test_run_simulation(self):
        """Test running simulation."""
        sim = Simulator()
        signal = Signal(length=5)
        signal.data = [10, 20, 30, 40, 50]
        sim.add_signal(signal)
        results = sim.run_simulation()
        self.assertEqual(results['signal_data']['mean'], 30.0)
        self.assertEqual(results['signal_data']['std'], np.std([10,20,30,40,50], ddof=1)) # Fixed ddof=1 for describe()
if __name__ == "__main__":
    unittest.main()