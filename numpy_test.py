import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from classification_model import MLSimulator, Signal  # Updated import from Day 47 file

class TestMLSimulator(unittest.TestCase):
    def test_train_classification(self):
        sim = MLSimulator()
        # Add signals with varying std for diverse classes
        std_values = [3, 10, 20]  # Ensures low, medium, high variances
        for std in std_values * 2:  # Repeat for sufficient data (at least 6 signals)
            sim.add_signal(Signal(length=100, std=std))
        metrics_logistic, lime_logistic = sim.train_classification('logistic')
        metrics_rf, lime_rf = sim.train_classification('random_forest')
        for metrics in [metrics_logistic, metrics_rf]:
            self.assertIsInstance(metrics, dict)
            self.assertIn('accuracy', metrics)
            self.assertGreaterEqual(metrics['accuracy'], 0.0)
            self.assertLessEqual(metrics['accuracy'], 1.0)
        for lime in [lime_logistic, lime_rf]:
            self.assertIsInstance(lime, list)
            self.assertGreater(len(lime), 0)
    # Add more as needed from prior days

if __name__ == "__main__":
    unittest.main()