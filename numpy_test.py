import unittest
import numpy as np
from forecast_ci import MLSimulator

class TestMLSimulator(unittest.TestCase):
    def setUp(self):
        self.sim = MLSimulator()
        self.df = self.sim.generate_raw_data()
        self.sim.train_model(self.df)

    def test_forecast_integration(self):
        """Ensure model predicts valid classes (0, 1, 2)."""
        prediction = self.sim.forecast_signal(0.5, 100.0)
        self.assertIn(prediction, [0, 1, 2])

    def test_hybrid_logic(self):
        """Verify hybrid pattern returns correct structure."""
        patterns = self.sim.hybrid_recursive_pattern(initial_std=10, steps=5)
        self.assertEqual(len(patterns), 5)
        # Check if next_std logic matches prediction (logic: 0->3, 1->10, 2->20)
        for _, _, pred, next_std in patterns:
            expected_std = 3 if pred == 0 else 10 if pred == 1 else 20
            self.assertEqual(next_std, expected_std)

    def test_performance_threshold(self):
        """Basic logic check, not full benchmark."""
        import time
        start = time.time()
        self.sim.forecast_signal(0.5, 100.0)
        duration = time.time() - start
        self.assertLess(duration, 0.5, "Single prediction too slow")

if __name__ == "__main__":
    unittest.main()