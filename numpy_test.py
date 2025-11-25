import unittest
import numpy as np
import pandas as pd
from bias_monitor import MLSimulator

class TestMLSimulator(unittest.TestCase):
    def setUp(self):
        # Initialize the simulator and train the model once for all tests
        self.sim = MLSimulator()
        self.df = self.sim.generate_raw_data()
        self.train_f1 = self.sim.train_with_weighting(self.df)

    def test_bias_monitor(self):
        """Test fairness metric calculation and logging."""
        # Check F1 score after training
        self.assertGreater(self.train_f1, 0.85) # Expect a much higher F1 now
        
        # Monitor bias
        di = self.sim.monitor_bias(self.df)
        
        # Disparate Impact should be within the acceptable range (0.8 to 1.25)
        self.assertGreaterEqual(di, 0.8)
        self.assertLessEqual(di, 1.25)
        self.assertIsInstance(di, float)

    def test_weighting_efficacy(self):
        """Ensure model predicts minority classes (1 or 2) when appropriate."""
        
        # Input that is characteristic of a minority class (high variance, std=10 or 20)
        # Variance of 100 corresponds to std=10 (Class 1)
        minority_signal_var = 100.0 
        
        # The model should predict Class 1 or Class 2, NOT the majority Class 0
        test_data = pd.DataFrame({'mean': [0], 'var': [minority_signal_var]})
        pred = self.sim.model.predict(test_data)[0]
        
        # Assertion now passes because the model has enough data to learn the boundary
        self.assertIn(pred, [1, 2])

if __name__ == "__main__":
    unittest.main()