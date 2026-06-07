#!/usr/bin/env python
"""Dump every note currently stored in the index (for debugging)."""

import json

from elasticsearch import Elasticsearch

from constants import ES_URL, INDEX


def main() -> None:
    es = Elasticsearch(ES_URL)
    es.indices.refresh(index=INDEX)
    result = es.search(index=INDEX, size=10000, query={"match_all": {}})
    total = result["hits"]["total"]["value"]
    print(f"number of notes: {total}")
    for hit in result["hits"]["hits"]:
        print(json.dumps(hit["_source"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
