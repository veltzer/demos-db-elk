#!/usr/bin/env python

# Report shard count vs data size for every index and flag suspicious shard
# sizing. This is the heart of the "oversharding" problem that bites real
# clusters: thousands of tiny shards each carry fixed memory/overhead on the
# heap, so a cluster with too many small shards wastes resources and slows
# down even though the actual data is small.
#
# Rule of thumb used here (mirrors official Elastic guidance):
#   - Aim for an average shard size of roughly 10GB to 50GB.
#   - Keep shards per GB of heap below ~20.
#   - A shard well under ~1GB is usually a candidate for fewer shards
#     (use _shrink, or fewer primaries next time / reindex).
#   - A shard well over ~50GB is a candidate for more shards (use _split).
#
# We read the per-shard store sizes from _cat/shards (PRIMARIES only, so we
# do not double-count replicas) and summarise per index.

from collections import defaultdict

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

GB = 1024 ** 3
MB = 1024 ** 2

# Target shard-size band (in bytes).
TARGET_MIN = 10 * GB
TARGET_MAX = 50 * GB
TINY_SHARD = 1 * GB  # below this a primary shard is "too small"


def human(n):
    """Render a byte count as a short human string."""
    if n >= GB:
        return f"{n / GB:.2f}GB"
    if n >= MB:
        return f"{n / MB:.2f}MB"
    return f"{n / 1024:.2f}KB"


def main():
    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        return

    # Pull per-shard primary stats. format=json gives us clean dicts.
    shards = es.cat.shards(
        h="index,shard,prirep,docs,store", format="json", bytes="b"
    )

    # Aggregate primaries per index.
    by_index = defaultdict(lambda: {"shards": 0, "store": 0, "docs": 0})
    for s in shards:
        if s.get("prirep") != "p":
            continue
        # Skip system/hidden indices for a cleaner report.
        idx = s["index"]
        if idx.startswith("."):
            continue
        store = int(s["store"]) if s.get("store") not in (None, "") else 0
        docs = int(s["docs"]) if s.get("docs") not in (None, "") else 0
        entry = by_index[idx]
        entry["shards"] += 1
        entry["store"] += store
        entry["docs"] += docs

    if not by_index:
        print("No user indices found. Did you run 02_load_sample_data.py?")
        return

    print(f"{'index':<24}{'shards':>7}{'total':>12}{'avg/shard':>12}  flag")
    print("-" * 72)

    for idx in sorted(by_index):
        e = by_index[idx]
        n = e["shards"]
        avg = e["store"] / n if n else 0

        if avg < TINY_SHARD and n > 1:
            flag = "OVERSHARDED (shards too small -> consider _shrink)"
        elif avg > TARGET_MAX:
            flag = "UNDERSHARDED (shards too big -> consider _split)"
        elif TARGET_MIN <= avg <= TARGET_MAX:
            flag = "OK (within 10-50GB target band)"
        else:
            flag = "small (fine for dev; review at production scale)"

        print(
            f"{idx:<24}{n:>7}{human(e['store']):>12}"
            f"{human(avg):>12}  {flag}"
        )

    print()
    print("Guidance: target ~10-50GB per shard. Many tiny shards waste heap")
    print("and cluster overhead; very large shards slow recovery and search.")


if __name__ == "__main__":
    main()
