import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from pandas_viz_sim import Signal, Simulator # Updated import from Day 39 file
class TestSignal(unittest.TestCase):
    def test_generate(self):
        signal = Signal(length=5)
        self.assertEqual(signal.data.shape[0], 5)
        self.assertTrue(np.issubdtype(signal.data.dtype, np.integer))
        self.assertTrue(all(0 <= x <= 140 for x in signal.data))
    def test_analyze(self):
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        result = signal.analyze()
        self.assertIn("Mean: 30.00", result)
        self.assertIn("Std: 14.14", result)
class TestSimulator(unittest.TestCase):
    def test_add_signal(self):
        sim = Simulator()
        signal = Signal()
        sim.add_signal(signal)
        self.assertEqual(len(sim.signals), 1)
    def test_run_simulation(self):
        sim = Simulator()
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        sim.add_signal(signal)
        results = sim.run_simulation()
        self.assertEqual(results['signal_data']['mean'], 30.0)
        self.assertAlmostEqual(results['signal_data']['std'], 14.142135623730951, places=5)
    def test_analyze_with_pandas(self):
        sim = Simulator()
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        sim.add_signal(signal)
        df = sim.analyze_with_pandas()
        self.assertEqual(df.loc['mean', 'signal_data'], 30.0)
        self.assertAlmostEqual(df.loc['std', 'signal_data'], 15.811388300841896, places=5) # sample std for describe()
    def test_visualize(self):
        sim = Simulator()
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        sim.add_signal(signal)
        filename = "test_hist.png"
        with patch('matplotlib.pyplot.savefig') as mock_save:
            sim.visualize(filename)
            mock_save.assert_called_once_with(filename)
if __name__ == "__main__":
    unittest.main()