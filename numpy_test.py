import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from sklearn.model_selection import train_test_split
from clustering_model import MLSimulator, Signal  # Updated import from Day 51 file

class TestMLSimulator(unittest.TestCase):
    def test_clustering(self):
        sim = MLSimulator()
        df = sim.generate_raw_data()
        clustered_df, score = sim.apply_clustering(df)
        self.assertEqual(clustered_df.shape[0], df.shape[0])
        self.assertGreater(score, 0.4)  # Reasonable threshold for good clustering
        self.assertIn('cluster', clustered_df.columns)
    # Prior tests here

if __name__ == "__main__":
    unittest.main()