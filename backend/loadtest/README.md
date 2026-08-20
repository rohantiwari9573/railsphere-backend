# Load testing

`locustfile.py` drives real endpoints (search, station/train/route detail,
journey search, analytics) with a task mix weighted to roughly match actual
frontend usage — search fires often (debounced keystrokes), detail pages and
analytics less so.

## Run it

Interactive UI (http://localhost:8089):

```bash
pip install -r requirements-dev.txt
locust -f loadtest/locustfile.py --host http://127.0.0.1:8000
```

Headless, with a CSV report:

```bash
locust -f loadtest/locustfile.py --host http://127.0.0.1:8000 \
    --users 30 --spawn-rate 5 --run-time 30s --headless --csv=loadtest/results
```

`--host` can point at the deployed instance instead — e.g.
`https://16-176-230-154.nip.io` — to load-test production traffic patterns
directly. The default rate limit (200 req/min per IP) will kick in above
roughly 3 req/s sustained from one client; a real user's browser never gets
close to that, but a load-test client easily can, so keep `--users` and the
rate limit in mind together if testing against the live deployment.

## Baseline (local, single gunicorn dev process, no Redis configured)

30 concurrent users, 30s run, 2026-08-21:

| Endpoint | Median | p95 | Requests |
|---|---|---|---|
| `/analytics/overview` | 53ms | 150ms | 31 |
| `/journeys/search` | 51ms | 150ms | 35 |
| `/stations/[id]/trains` | 50ms | 79ms | 15 |
| `/stations?search=*` | 11ms | 43ms | 83 |
| `/stations?skip=*` | 11ms | 26ms | 46 |
| `/stations/[id]` | 8ms | 17ms | 37 |
| `/trains/[id]` | 9ms | 16ms | 25 |
| `/routes/[id]` | 7ms | 20ms | 25 |
| `/analytics/top-stations` | 8ms | 21ms | 24 |

0 failures across 321 requests. `/analytics/overview` and `/journeys/search`
are the clear standouts on latency — both do real aggregate/join work per
request. `/analytics/overview` is exactly what the Redis cache-aside layer
(`app/core/cache.py`) targets: once `REDIS_URL` is set, this drops to a
cache hit after the first request instead of five `COUNT(*)` queries every
time. `/journeys/search`'s cost is inherent to the query (no cache — results
depend on the two station ids in the request), so it's the next place to look
if this endpoint needs to get faster under load, not this endpoint's caching.
