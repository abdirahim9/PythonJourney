import timeit
import numpy as np

def test_func():
    # Simulate forecast call; replace with actual integration if needed
    pass

times = timeit.repeat(test_func, number=100, repeat=10)
p99 = np.percentile(times, 99)
if p99 > 0.5:  # Gate: <500ms
    raise ValueError(f'p99 exceeds 500ms: {p99}')
print(f'p99: {p99}')