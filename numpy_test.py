import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, mock_open
import json
import threading
from concurrent_sim import Signal, Simulator # Updated import from Day 42 file
class TestSignal(unittest.TestCase):
    def test_generate(self):
        signal = Signal(length=5)
        self.assertEqual(signal.data.shape[0], 5)
        self.assertTrue(np.issubdtype(signal.data.dtype, np.floating))  # Adjusted for float dtype due to scale
        self.assertTrue(all(0 <= x <= 140 for x in signal.data))  # Adjusted for pattern

    def test_analyze(self):
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        result = signal.analyze()
        self.assertIn("Mean: 30.00", result)
        self.assertIn("Std: 14.14", result)  # population std

    def test_to_dict(self):
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        d = signal.to_dict()
        self.assertEqual(d['length'], 5)
        self.assertEqual(d['data'], [10.0, 20.0, 30.0, 40.0, 50.0])  # tolist() makes float

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
        self.assertAlmostEqual(results['signal_data']['std'], 14.142135623730951, places=5)  # population std

    def test_analyze_with_pandas(self):
        sim = Simulator()
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        sim.add_signal(signal)
        df = sim.analyze_with_pandas()
        self.assertEqual(df.loc['mean', 'signal_data'], 30.0)
        self.assertAlmostEqual(df.loc['std', 'signal_data'], 15.811388300841896, places=5)  # sample std for describe()

    def test_visualize(self):
        sim = Simulator()
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        sim.add_signal(signal)
        filename = "test_hist.png"
        with patch('matplotlib.pyplot.savefig') as mock_save:
            sim.visualize(filename)
            mock_save.assert_called_once_with(filename)

    def test_save_state(self):
        sim = Simulator()
        signal = Signal(length=5)
        sim.add_signal(signal)
        filename = "test_state.json"
        mock_data = json.dumps([signal.to_dict()])
        with patch("builtins.open", mock_open()) as mock_file:
            sim.save_state(filename)
            mock_file.assert_called_with(filename, 'w')
        # Note: json.dump not mocked, but call verified indirectly

    def test_load_state(self):
        sim = Simulator()
        filename = "test_state.json"
        mock_state = [{'length': 5, 'frequency': 5, 'scale': 1.0, 'data': [10, 20, 30, 40, 50]}]
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_state))):
            with patch('os.path.exists', return_value=True):
                sim.load_state(filename)
                self.assertEqual(len(sim.signals), 1)
                np.testing.assert_array_equal(sim.signals[0].data, np.array([10, 20, 30, 40, 50]))

    def test_concurrent_add_signal(self):
        sim = Simulator()
        def add_signals():
            for _ in range(100):
                signal = Signal(length=5)
                sim.add_signal(signal)
        threads = [threading.Thread(target=add_signals) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(sim.signals), 1000)

if __name__ == "__main__":
    unittest.main()