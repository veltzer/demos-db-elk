#!/usr/bin/env python
"""Continuously stream synthetic time-series data into Elasticsearch.

This simulates a real-world ingestion pipeline (metrics, sensor readings,
page-load timings, …) where documents arrive one at a time, indefinitely.
Run it in one terminal and watch the data grow with `show_data.py` in another.

Stop it with Ctrl-C.
"""

import random
import time

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "wpt"  # "web page timings"


def stream() -> None:
    """Insert one document per second until interrupted."""
    day = 1
    inserted = 0
    try:
        while True:
            doc = {
                "day": day,
                "speed_of_load": random.uniform(0, 1) * 3,
            }
            result = es.index(index=INDEX_NAME, document=doc)
            assert result["_shards"]["successful"] >= 1
            inserted += 1
            day += 1
            print(f"added record #{inserted} (day={day - 1})")
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\nstopped after inserting {inserted} records")


if __name__ == "__main__":
    stream()
