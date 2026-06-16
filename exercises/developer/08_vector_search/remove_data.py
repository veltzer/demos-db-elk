#!/usr/bin/env python
"""Delete all documents from the articles index, keeping the mapping.

Use this to reset between runs without re-running 15_vector_search_01.sh.
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "articles"


def remove() -> None:
    """Delete every document but leave the index and its mapping in place."""
    result = es.delete_by_query(
        index=INDEX_NAME,
        query={"match_all": {}},
        refresh=True,
    )
    print(f"deleted {result['deleted']} documents from '{INDEX_NAME}'")


if __name__ == "__main__":
    remove()
