import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from sklearn.model_selection import train_test_split
from bias_monitor import MLSimulator  # Updated import from Day 54 file

class TestMLSimulator(unittest.TestCase):
    def test_bias_monitor(self):
        sim = MLSimulator()
        df = sim.generate_raw_data()
        train_f1 = sim.train_with_weighting(df)
        self.assertGreater(train_f1, 0.5)
        disparate_impact = sim.monitor_bias(df)
        self.assertLess(disparate_impact, 1.25)  # Acceptable fairness range
    # Prior tests here

if __name__ == "__main__":
    unittest.main()