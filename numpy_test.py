import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from regression_model import MLSimulator, Signal  # Updated import from Day 46 file
class TestMLSimulator(unittest.TestCase):
    def test_train_regression(self):
        sim = MLSimulator()
        signal = Signal(length=20)
        sim.add_signal(signal)
        mse, r2, importance = sim.train_regression()
        self.assertIsInstance(mse, float)
        self.assertIsInstance(r2, float)
        self.assertIsInstance(importance, np.ndarray)
        self.assertLess(mse, 10000)  # Loose bound for variance
    # Add more as needed
if __name__ == "__main__":
    unittest.main()