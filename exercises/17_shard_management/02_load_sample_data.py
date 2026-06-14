#!/usr/bin/env python

# Load sample log documents into the "logs_sharded" index using the bulk
# helper. We generate realistic-looking log lines with the faker library so
# the shards have meaningful, varied content and a non-trivial store size.
#
#   pip install elasticsearch faker
#
# The number of documents is configurable on the command line. The default
# (50000) is enough to give each of the 4 primary shards some store size to
# look at in the _cat APIs, while still loading quickly on a laptop.

import sys
import random
from datetime import datetime, timedelta

from faker import Faker
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch("http://localhost:9200")
fake = Faker()

INDEX = "logs_sharded"

LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]
SERVICES = ["auth", "billing", "search", "cart", "shipping", "gateway"]
STATUSES = [200, 201, 301, 400, 401, 404, 500, 503]


def gen_docs(count):
    """Yield bulk-action dicts of fake log documents."""
    base = datetime.utcnow() - timedelta(days=7)
    for _ in range(count):
        ts = base + timedelta(seconds=random.randint(0, 7 * 24 * 3600))
        yield {
            "_index": INDEX,
            "_source": {
                "timestamp": ts.isoformat(),
                "level": random.choice(LEVELS),
                "service": random.choice(SERVICES),
                "host": fake.hostname(),
                "message": fake.sentence(nb_words=12),
                "latency_ms": round(random.uniform(0.5, 1500.0), 2),
                "status": random.choice(STATUSES),
            },
        }


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50000

    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        sys.exit(1)

    print(f"Bulk loading {count} documents into '{INDEX}' ...")
    success, errors = helpers.bulk(
        es.options(request_timeout=120), gen_docs(count), chunk_size=2000
    )
    print(f"Indexed {success} documents, {len(errors)} errors")

    # Refresh so the new documents are immediately visible to _cat/_count.
    es.indices.refresh(index=INDEX)
    total = es.count(index=INDEX)["count"]
    print(f"Index '{INDEX}' now contains {total} documents")


if __name__ == "__main__":
    main()
