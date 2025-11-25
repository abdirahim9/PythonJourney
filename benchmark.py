import timeit
import numpy as np
from forecast_ci import MLSimulator

def setup_benchmark():
    # Initialize and train a model for the benchmark
    sim = MLSimulator()
    df = sim.generate_raw_data()
    sim.train_model(df)
    return sim

sim_instance = setup_benchmark()

def test_func():
    # Benchmark the specific forecasting method
    sim_instance.forecast_signal(0.5, 100.0)

if __name__ == "__main__":
    # Run 1000 loops, repeat 10 times to get stable p99
    times = timeit.repeat(test_func, number=1000, repeat=10)
    # Calculate time per call (timeit returns total time for 'number' executions)
    per_call_times = [t / 1000 for t in times]
    p99 = np.percentile(per_call_times, 99)

    print(f"p99 Latency: {p99:.6f} seconds")

    # Strict Gate: 500ms (0.5 seconds)
    if p99 > 0.5:
        raise ValueError(f'Performance Failure: p99 latency {p99:.6f}s exceeds 0.5s limit.')
    print("Performance Check Passed.")