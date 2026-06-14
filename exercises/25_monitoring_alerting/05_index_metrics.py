#!/usr/bin/env python
"""Self-monitoring: index collected metrics back into Elasticsearch.

Runs the collector from 01_metrics_collector.py, stamps the result with a
UTC @timestamp, and bulk-indexes it as one document into the dba-metrics
write alias. Storing metrics this way lets you chart cluster health over
time in Kibana (Discover, Lens, or a dashboard) - see exercise 07 for the
Kibana setup.

Run 04_create_metrics_index.sh first to create the index template + alias,
then run this script (repeatedly, or from cron) to accumulate a time series.

    ./04_create_metrics_index.sh
    ./05_index_metrics.py
"""

from datetime import datetime, timezone
from importlib import import_module

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

collector = import_module("01_metrics_collector")

es = Elasticsearch("http://localhost:9200")

# We write to the alias, not a concrete index, so rollover stays transparent.
METRICS_ALIAS = "dba-metrics"


def build_metrics_doc():
    """Collect metrics and add a UTC @timestamp suitable for Kibana."""
    doc = collector.collect_metrics()
    doc["@timestamp"] = datetime.now(timezone.utc).isoformat()
    return doc


def index_metrics_doc(doc):
    """Bulk-index a single metrics document into the dba-metrics alias.

    We use the bulk helper even for one document so the same code path
    scales if you batch multiple samples (see 06_sample_loop.py).
    """
    actions = [{"_index": METRICS_ALIAS, "_source": doc}]
    success, errors = bulk(es, actions, refresh="wait_for")
    return success, errors


def main():
    """Collect once and store the metrics document."""
    doc = build_metrics_doc()
    success, errors = index_metrics_doc(doc)
    if errors:
        print(f"FAILED to index metrics: {errors}")
        raise SystemExit(1)
    print(
        f"Indexed metrics into '{METRICS_ALIAS}' "
        f"(status={doc['status']}, heap={doc['heap_used_percent_max']}%, "
        f"disk={doc['disk_used_percent_max']}%, "
        f"@timestamp={doc['@timestamp']})"
    )


if __name__ == "__main__":
    main()
