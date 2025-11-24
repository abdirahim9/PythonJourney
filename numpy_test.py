import unittest
import numpy as np
import pandas as pd
from forecast_ci import MLSimulator

class TestMLSimulator(unittest.TestCase):
    def test_forecast_integration(self):
        sim = MLSimulator()
        df = sim.generate_raw_data()
        train_f1 = sim.train_model(df)
        self.assertGreater(train_f1, 0.5)
        prediction = sim.forecast_signal(0.5, 100.0)
        self.assertIn(prediction, [0, 1, 2])
        patterns = sim.hybrid_recursive_pattern(initial_std=10, steps=2)
        self.assertEqual(len(patterns), 2)
        self.assertIsInstance(patterns[0][3], int)

if __name__ == "__main__":
    unittest.main()