#!/usr/bin/env python
"""Show the documents currently streamed into the index.

Run this repeatedly (or watch it) while `stream_data.py` is running to see the
document count climb.
"""

import json

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "wpt"


def show() -> None:
    """Print the total count and the most recent documents."""
    es.indices.refresh(index=INDEX_NAME)
    result = es.search(
        index=INDEX_NAME,
        size=10,
        sort=[{"day": {"order": "desc"}}],
        query={"match_all": {}},
    )
    total = result["hits"]["total"]["value"]
    print(f"total documents: {total}")
    print("most recent 10:")
    for hit in result["hits"]["hits"]:
        print(json.dumps(hit["_source"], indent=2, sort_keys=True))


if __name__ == "__main__":
    show()
