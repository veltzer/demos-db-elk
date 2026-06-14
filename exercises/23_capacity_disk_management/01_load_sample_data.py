#!/usr/bin/env python

# Load sample documents into the "capacity_demo" index so the later disk and
# capacity scripts have a non-trivial store size to look at. We generate
# realistic-looking event documents with the faker library.
#
#   pip install elasticsearch faker
#
# The number of documents is configurable on the command line. The default
# (100000) gives the index a few tens of megabytes of store, which is enough
# to make _cat/allocation, _disk_usage and the forecaster produce meaningful
# numbers while still loading quickly on a laptop.

import sys
import random
from datetime import datetime, timedelta

from faker import Faker
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch("http://localhost:9200")
fake = Faker()

INDEX = "capacity_demo"

LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]
SERVICES = ["auth", "billing", "search", "cart", "shipping", "gateway"]
STATUSES = [200, 201, 301, 400, 401, 404, 500, 503]


def gen_docs(count):
    """Yield bulk-action dicts of fake event documents."""
    base = datetime.utcnow() - timedelta(days=30)
    for _ in range(count):
        ts = base + timedelta(seconds=random.randint(0, 30 * 24 * 3600))
        yield {
            "_index": INDEX,
            "_source": {
                "timestamp": ts.isoformat(),
                "level": random.choice(LEVELS),
                "service": random.choice(SERVICES),
                "host": fake.hostname(),
                "client_ip": fake.ipv4(),
                "url": fake.uri_path(),
                "user_agent": fake.user_agent(),
                "message": fake.sentence(nb_words=16),
                "latency_ms": round(random.uniform(0.5, 1500.0), 2),
                "bytes": random.randint(120, 120000),
                "status": random.choice(STATUSES),
            },
        }


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100000

    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        sys.exit(1)

    print(f"Bulk loading {count} documents into '{INDEX}' ...")
    success, errors = helpers.bulk(
        es, gen_docs(count), chunk_size=5000, request_timeout=120
    )
    print(f"Indexed {success} documents, {len(errors)} errors")

    # Refresh so the new documents are immediately visible to _cat/_stats.
    es.indices.refresh(index=INDEX)
    total = es.count(index=INDEX)["count"]
    print(f"Index '{INDEX}' now contains {total} documents")


if __name__ == "__main__":
    main()
