import unittest
import numpy as np
from numpy_sim import Signal, Simulator

class TestSignal(unittest.TestCase):

    def test_generate(self):
        signal = Signal(length=5)
        self.assertEqual(signal.data.shape[0], 5)
        self.assertTrue(np.issubdtype(signal.data.dtype, np.integer))
        # Maximum possible value = 100 + (frequency-1)*10
        self.assertTrue(all(0 <= x <= 140 for x in signal.data))

    def test_analyze(self):
        signal = Signal(length=5)
        signal.data = np.array([10, 20, 30, 40, 50])
        result = signal.analyze()
        self.assertIn("Mean: 30.00", result)
        self.assertIn("Std: 14.14", result)  # population std


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


if __name__ == "__main__":
    unittest.main()
