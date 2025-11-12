import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from preprocessing_pipeline import MLSimulator, Signal  # Updated import from Day 48 file

class TestMLSimulator(unittest.TestCase):
    def test_preprocessing_pipeline(self):
        sim = MLSimulator()
        # Add signals
        for std in [3, 10, 20] * 2:
            sim.add_signal(Signal(length=100, std=std))
        df = sim.generate_raw_data(introduce_missing=True, introduce_outliers=True)
        preprocessor = sim.build_preprocessing_pipeline()
        processed = sim.apply_pipeline(df, preprocessor)
        self.assertIsNotNone(processed)
        self.assertIsInstance(processed, np.ndarray)
        self.assertGreater(processed.shape[0], 0)
    # Prior tests here

if __name__ == "__main__":
    unittest.main()