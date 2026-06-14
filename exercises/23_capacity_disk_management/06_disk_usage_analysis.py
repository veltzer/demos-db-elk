#!/usr/bin/env python
"""Find which FIELDS consume the most disk in an index.

Wraps POST /<index>/_disk_usage?run_expensive_tasks=true. This API actually
reads the on-disk Lucene structures, so it is genuinely expensive (it scans
segments) and must be opted into with run_expensive_tasks=true. The payoff is a
precise per-field breakdown: how many bytes each field spends on its inverted
index, doc values, stored fields, points, etc.

For a DBA this answers "what should I stop indexing / change the mapping for to
shrink this index?". Big offenders are usually high-cardinality text fields
(inverted index) and analyzed message fields. Often you can switch such a field
to keyword, set index:false, or drop doc_values to reclaim a lot of space.

Usage:
    ./06_disk_usage_analysis.py [index_name] [top_n]
"""

import sys

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def human(num_bytes):
    """Format a byte count as a human-readable string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0:
            return f"{value:6.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


def main():
    index = sys.argv[1] if len(sys.argv) > 1 else "capacity_demo"
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        sys.exit(1)

    print(f"Running disk usage analysis on '{index}' (this is expensive)...")
    # run_expensive_tasks is mandatory; without it the API refuses to run.
    result = es.indices.disk_usage(
        index=index, run_expensive_tasks=True
    )

    stats = result[index]
    total = stats["store_size_in_bytes"]
    print(f"\nTotal store size: {human(total)}\n")

    fields = stats.get("fields", {})
    rows = []
    for name, info in fields.items():
        rows.append((name, info["total_in_bytes"], info))
    rows.sort(key=lambda r: r[1], reverse=True)

    header = f"{'field':<22}{'total':>10}{'inverted':>10}{'docvals':>10}"
    header += f"{'stored':>10}{'points':>10}"
    print(header)
    print("-" * len(header))
    for name, total_bytes, info in rows[:top_n]:
        print(
            f"{name:<22}"
            f"{human(total_bytes):>10}"
            f"{human(info.get('inverted_index', {}).get('total_in_bytes', 0)):>10}"
            f"{human(info.get('doc_values_in_bytes', 0)):>10}"
            f"{human(info.get('stored_fields_in_bytes', 0)):>10}"
            f"{human(info.get('points_in_bytes', 0)):>10}"
        )

    print(
        "\nTip: the 'inverted' column is the analyzed/searchable index. If a "
        "big text field is never searched, set index:false. If you never "
        "aggregate/sort on a field, doc_values:false saves the 'docvals' cost."
    )


if __name__ == "__main__":
    main()
