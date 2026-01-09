import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

ENDPOINTS = [
    'http://127.0.0.1:8000/api/monitoring/metrics',
    'http://127.0.0.1:8000/api/recommendations/testuser',
    'http://127.0.0.1:8000/health',
]

TOTAL_REQUESTS = 500
MAX_WORKERS = 50
TIMEOUT = 10

results = []
failed = 0

start_time = time.perf_counter()

def fetch(url):
    try:
        s = time.perf_counter()
        r = requests.get(url, timeout=TIMEOUT)
        e = (time.perf_counter() - s) * 1000.0
        return (url, r.status_code, e)
    except Exception as exc:
        return (url, None, None)

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
    futures = []
    for i in range(TOTAL_REQUESTS):
        url = ENDPOINTS[i % len(ENDPOINTS)]
        futures.append(ex.submit(fetch, url))

    for fut in as_completed(futures):
        url, status, latency = fut.result()
        if status == 200 and latency is not None:
            results.append(latency)
        else:
            failed += 1

elapsed = time.perf_counter() - start_time

print(f"Total requests: {TOTAL_REQUESTS}")
print(f"Successful: {len(results)}")
print(f"Failed: {failed}")
print(f"Elapsed: {elapsed:.2f}s")
if results:
    print(f"Min: {min(results):.2f} ms")
    print(f"Max: {max(results):.2f} ms")
    print(f"Mean: {statistics.mean(results):.2f} ms")
    print(f"Median: {statistics.median(results):.2f} ms")
else:
    print("No successful requests.")
