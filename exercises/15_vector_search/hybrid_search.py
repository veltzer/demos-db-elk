#!/usr/bin/env python
"""Hybrid search: combine lexical (BM25) and vector (kNN) relevance.

Pure keyword search misses semantically-related documents that use different
words; pure vector search can miss exact term matches. A hybrid query runs
both and lets Elasticsearch add their scores, so a result that is strong on
either signal surfaces.

    ./hybrid_search.py "market rates"
"""

import argparse

from elasticsearch import Elasticsearch

from embedding import embed

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "articles"


def hybrid_search(query_text: str, k: int = 3) -> None:
    """Run a BM25 query and a kNN query together and show the blended ranking.

    When both `query` (BM25) and `knn` are supplied to _search, Elasticsearch
    sums their scores. `boost` on each side tunes their relative weight.
    """
    bm25 = {
        "multi_match": {
            "query": query_text,
            "fields": ["title^2", "content"],
            "boost": 1.0,
        }
    }
    knn = {
        "field": "embedding",
        "query_vector": embed(query_text),
        "k": k,
        "num_candidates": 50,
        "boost": 1.0,
    }

    result = es.search(
        index=INDEX_NAME,
        query=bm25,
        knn=knn,
        size=k,
        source=["title", "category"],
    )

    print(f"query: {query_text!r}")
    print(f"top {k} by blended BM25 + kNN score:")
    for hit in result["hits"]["hits"]:
        src = hit["_source"]
        print(f"  {hit['_score']:.4f}  [{src['category']:7}] {src['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hybrid BM25 + kNN search")
    parser.add_argument("query", nargs="?", default="market rates",
                        help="free-text query")
    parser.add_argument("-k", type=int, default=3, help="number of results")
    args = parser.parse_args()
    hybrid_search(args.query, args.k)
