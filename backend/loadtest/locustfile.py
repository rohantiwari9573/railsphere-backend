"""
Load test against real RailSphere endpoints, weighted to roughly
match how the frontend actually uses the API: mostly reads, search
autocomplete firing on every keystroke (debounced), occasional deep
dives into a station/train/route detail page.

Run: locust -f loadtest/locustfile.py --host https://16-176-230-154.nip.io
Headless baseline: locust -f loadtest/locustfile.py --host <url> \
    --users 50 --spawn-rate 5 --run-time 1m --headless --csv=loadtest/results
"""

import random

from locust import HttpUser, between, task

# A handful of real station/train/route ids from the live dataset,
# so detail-page requests hit actual rows instead of guessing at 404s.
STATION_IDS = [1779, 794, 7851, 1, 2, 1272, 1269]
TRAIN_IDS = [4932, 4921, 4930, 5620, 907]
ROUTE_IDS = [1563, 1564, 684, 1, 212]

SEARCH_TERMS = [
    "kanpur", "delhi", "central", "junction", "howrah",
    "chennai", "mumbai", "bangalore", "jn", "express",
]


class RailSphereUser(HttpUser):
    wait_time = between(1, 4)

    @task(10)
    def search_stations(self):
        term = random.choice(SEARCH_TERMS)
        self.client.get(
            f"/stations?search={term}&limit=8", name="/stations?search=*"
        )

    @task(6)
    def browse_stations(self):
        skip = random.choice([0, 50, 100, 500])
        self.client.get(
            f"/stations?skip={skip}&limit=50", name="/stations?skip=*"
        )

    @task(4)
    def station_detail(self):
        station_id = random.choice(STATION_IDS)
        self.client.get(f"/stations/{station_id}", name="/stations/[id]")

    @task(2)
    def station_trains(self):
        station_id = random.choice(STATION_IDS)
        self.client.get(
            f"/stations/{station_id}/trains", name="/stations/[id]/trains"
        )

    @task(3)
    def train_detail(self):
        train_id = random.choice(TRAIN_IDS)
        self.client.get(f"/trains/{train_id}", name="/trains/[id]")

    @task(3)
    def route_detail(self):
        route_id = random.choice(ROUTE_IDS)
        self.client.get(f"/routes/{route_id}", name="/routes/[id]")

    @task(5)
    def journey_search(self):
        a, b = random.sample(STATION_IDS, 2)
        self.client.get(
            f"/journeys/search?from_station_id={a}&to_station_id={b}",
            name="/journeys/search",
        )

    @task(4)
    def analytics_overview(self):
        self.client.get("/analytics/overview", name="/analytics/overview")

    @task(3)
    def analytics_top_stations(self):
        self.client.get(
            "/analytics/top-stations?limit=10", name="/analytics/top-stations"
        )
