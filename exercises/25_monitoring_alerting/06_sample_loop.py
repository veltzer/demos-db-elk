#!/usr/bin/env python
"""Sample metrics on a fixed interval for a fixed duration.

This generates a short time series of dba-metrics documents so a learner
can immediately see a line chart in Kibana without waiting hours for cron
to accumulate data points.

Usage:

    ./06_sample_loop.py [interval_seconds] [duration_seconds]

Defaults: sample every 10 seconds for 120 seconds (13 data points).

    ./06_sample_loop.py            # every 10s for 2 minutes
    ./06_sample_loop.py 5 60       # every 5s for 1 minute

Run 04_create_metrics_index.sh first to set up the index/alias.
"""

import sys
import time

from importlib import import_module

index_metrics = import_module("05_index_metrics")


def run_sampler(interval_s, duration_s):
    """Index a metrics doc every interval_s for duration_s seconds."""
    start = time.monotonic()
    deadline = start + duration_s
    tick = 0

    while True:
        tick += 1
        doc = index_metrics.build_metrics_doc()
        success, errors = index_metrics.index_metrics_doc(doc)
        if errors:
            print(f"tick {tick}: FAILED to index: {errors}")
        else:
            print(
                f"tick {tick}: indexed "
                f"status={doc['status']} "
                f"heap={doc['heap_used_percent_max']}% "
                f"disk={doc['disk_used_percent_max']}% "
                f"@ {doc['@timestamp']}"
            )

        # Stop once we have crossed the duration; we always take a final
        # sample at or just past the deadline.
        if time.monotonic() >= deadline:
            break
        time.sleep(interval_s)

    print(f"Done. Took {tick} sample(s) over ~{duration_s}s.")
    print(
        "Open Kibana (exercise 07), create a data view for 'dba-metrics-*', "
        "and chart heap_used_percent_max or disk_used_percent_max over "
        "@timestamp."
    )


def main():
    """Parse optional args and run the sampling loop."""
    interval_s = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    duration_s = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    print(
        f"Sampling every {interval_s}s for {duration_s}s into "
        f"'{index_metrics.METRICS_ALIAS}'..."
    )
    run_sampler(interval_s, duration_s)


if __name__ == "__main__":
    main()
