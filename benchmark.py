import os
import sys
import time
import numpy as np


def run_benchmark() -> None:
    """
    Simple latency benchmark.

    - Runs an operation N times.
    - Computes mean latency and p99.
    - Optionally gates on P99_THRESHOLD env var (seconds).
    """
    N = 1000
    times = []

    for _ in range(N):
        start = time.perf_counter()
        # ---- Replace this block with your real operation if desired ----
        _ = np.sort(np.random.randn(1000))
        # ----------------------------------------------------------------
        end = time.perf_counter()
        times.append(end - start)

    times = np.array(times)
    p99 = float(np.percentile(times, 99))
    avg = float(times.mean())
    print(f"Average latency: {avg:.6f}s, p99: {p99:.6f}s")

    # p99 gate for CI
    threshold_str = os.getenv("P99_THRESHOLD", "").strip()
    if threshold_str:
        try:
            threshold = float(threshold_str)
        except ValueError:
            print(f"Invalid P99_THRESHOLD value: {threshold_str}", file=sys.stderr)
            sys.exit(1)

        if p99 > threshold:
            print(
                f"p99 gate FAILED: {p99:.6f}s > threshold {threshold:.6f}s",
                file=sys.stderr,
            )
            sys.exit(1)
        else:
            print(
                f"p99 gate PASSED: {p99:.6f}s <= threshold {threshold:.6f}s",
            )


if __name__ == "__main__":
    run_benchmark()
