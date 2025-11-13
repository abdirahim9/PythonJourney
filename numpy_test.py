import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from sklearn.model_selection import train_test_split  # Added missing import
from tuning_model import MLSimulator, Signal  # Updated import from Day 49 file

class TestMLSimulator(unittest.TestCase):
    def test_tune_model(self):
        sim = MLSimulator()
        for std in [3, 10, 20] * 5:  # Sufficient data
            sim.add_signal(Signal(length=100, std=std))
        df = sim.generate_raw_data()
        X = df[['mean', 'var']]
        y = df['label']
        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        preprocessor = sim.build_preprocessor()
        tuned = sim.tune_model(X_train, y_train, preprocessor)
        self.assertGreater(tuned.best_score_, 0.0)
        self.assertIn('classifier__n_estimators', tuned.best_params_)
    # Prior tests here

if __name__ == "__main__":
    unittest.main()