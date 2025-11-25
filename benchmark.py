import requests
import numpy as np
import time

times = []
for _ in range(100):
    start = time.time()
    payload = {"mean": 0.5, "var": 100.0}
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.Qw4w9WgXcQ"}  # Generate valid token
    requests.post("http://localhost:8000/predict", json=payload, headers=headers)
    times.append(time.time() - start)
p50, p95, p99 = np.percentile(times, [50, 95, 99])
print(f"p50: {p50:.3f}s, p95: {p95:.3f}s, p99: {p99:.3f}s")
if p99 > 0.5:
    raise ValueError(f"p99 {p99:.3f}s exceeds 500ms")