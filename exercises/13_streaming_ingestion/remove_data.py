#!/usr/bin/env python
"""Delete every document from the streaming index without dropping the index."""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "wpt"


def remove() -> None:
    """Delete all documents matching match_all and report how many went."""
    es.indices.refresh(index=INDEX_NAME)
    result = es.delete_by_query(
        index=INDEX_NAME,
        query={"match_all": {}},
    )
    deleted = result["deleted"]
    print(f"deleted {deleted} records")


if __name__ == "__main__":
    remove()
