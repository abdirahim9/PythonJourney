import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from sklearn.model_selection import train_test_split
from embedded_model import MLSimulator, Signal  # Updated import from Day 50 file

class TestMLSimulator(unittest.TestCase):
    def test_embedded_model(self):
        sim = MLSimulator()
        df = sim.generate_raw_data()
        X = df[['mean', 'var']]
        y = df['label']
        integration_f1 = sim.train_and_embed_model(X, y)
        self.assertGreater(integration_f1, 0.5)
        prediction, adapted_std = sim.real_time_decision(0.5, 100.0)
        self.assertIn(prediction, ['low', 'medium', 'high'])
        self.assertIsInstance(adapted_std, int)
    # Prior tests here

if __name__ == "__main__":
    unittest.main()