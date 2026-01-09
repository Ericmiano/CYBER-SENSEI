import time
import requests
import statistics

URL = 'http://127.0.0.1:8000/health'
REQUESTS = 100
TIMEOUT = 5

latencies = []
failed = 0

for i in range(REQUESTS):
    try:
        start = time.perf_counter()
        r = requests.get(URL, timeout=TIMEOUT)
        elapsed = (time.perf_counter() - start) * 1000.0
        if r.status_code == 200:
            latencies.append(elapsed)
        else:
            failed += 1
    except Exception as e:
        failed += 1
    time.sleep(0.01)

print(f"Requests: {REQUESTS}")
print(f"Successful: {len(latencies)}")
print(f"Failed: {failed}")
if latencies:
    print(f"Min: {min(latencies):.2f} ms")
    print(f"Max: {max(latencies):.2f} ms")
    print(f"Mean: {statistics.mean(latencies):.2f} ms")
    print(f"Median: {statistics.median(latencies):.2f} ms")
else:
    print("No successful requests.")
