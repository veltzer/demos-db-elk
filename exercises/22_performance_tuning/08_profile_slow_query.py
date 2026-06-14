#!/usr/bin/env python
"""Diagnose where a single query spends its time using profile=true.

The Profile API (`"profile": true` in the search body) returns a detailed
per-shard, per-query-component timing breakdown. It is the tool you reach
for when one specific query is slow and you need to know WHY rather than
just THAT it is slow.

NOTE: field-indexing and query-timing fundamentals are covered in
exercise 04_query_performance. This script is intentionally short: it
just shows the operational technique of reading a profile to attribute
time to query components (and points at the `_search?explain` companion
for score attribution).
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

INDEX = "perf_demo"


def main() -> None:
    """Run one profiled query and summarise the timing breakdown."""
    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        return

    body = {
        "profile": True,
        "size": 5,
        "query": {
            "bool": {
                "must": [{"match": {"bio": "london paris"}}],
                "filter": [
                    {"term": {"department": "sales"}},
                    {"range": {"salary": {"gte": 50000}}},
                ],
            }
        },
    }

    result = es.search(index=INDEX, body=body)
    print(f"server-reported took: {result['took']} ms")
    print(f"total hits: {result['hits']['total']['value']}")

    for s, shard in enumerate(result.get("profile", {}).get("shards", [])):
        print("=" * 60)
        print(f"shard {s}: {shard['id']}")
        print("=" * 60)
        for search in shard["searches"]:
            for q in search["query"]:
                ms = q["time_in_nanos"] / 1_000_000
                print(f"  {q['type']:<28} {ms:8.3f} ms")
                # Top time-consuming sub-operations of this query node.
                top = sorted(
                    q["breakdown"].items(),
                    key=lambda kv: kv[1],
                    reverse=True,
                )
                for name, nanos in top[:3]:
                    if nanos > 0:
                        print(f"      {name:<24} {nanos / 1_000_000:8.3f} ms")

            # Time spent collecting/aggregating results on the shard.
            for coll in search.get("collector", []):
                ms = coll["time_in_nanos"] / 1_000_000
                print(f"  collector: {coll['name']:<18} {ms:8.3f} ms")

    print("=" * 60)
    print(
        "Companion: GET /<index>/_search with \"explain\": true returns a "
        "per-document SCORE breakdown (why a doc matched and how it was "
        "scored), which complements the per-component TIMING above."
    )


if __name__ == "__main__":
    main()
