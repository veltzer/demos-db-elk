#!/usr/bin/env python
"""Approximate k-nearest-neighbour (kNN) search over the article embeddings.

Given a free-text query, we embed it with the same embedding.py used at index
time, then ask Elasticsearch for the documents whose vectors are closest
(cosine similarity) to the query vector.

Pass a query on the command line, or use the default:

    ./knn_search.py "stock market rally"
    ./knn_search.py --category finance "stock market rally"
"""

import argparse

from elasticsearch import Elasticsearch

from embedding import embed

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "articles"


def knn_search(query_text: str, category: str | None = None, k: int = 3) -> None:
    """Find the k articles nearest to the query vector.

    `num_candidates` controls the accuracy/speed trade-off of the HNSW search:
    more candidates explored per shard -> better recall, slightly slower.
    An optional category `filter` restricts which documents kNN may return.
    """
    knn = {
        "field": "embedding",
        "query_vector": embed(query_text),
        "k": k,
        "num_candidates": 50,
    }
    if category is not None:
        knn["filter"] = {"term": {"category": category}}

    result = es.search(index=INDEX_NAME, knn=knn, source_includes=["title", "category"])

    print(f"query: {query_text!r}" + (f" (category={category})" if category else ""))
    print(f"top {k} by vector similarity:")
    for hit in result["hits"]["hits"]:
        src = hit["_source"]
        print(f"  {hit['_score']:.4f}  [{src['category']:7}] {src['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="kNN vector search over articles")
    parser.add_argument("query", nargs="?", default="stock market rally",
                        help="free-text query to embed and search with")
    parser.add_argument("--category", default=None,
                        help="restrict results to this category (filtered kNN)")
    parser.add_argument("-k", type=int, default=3, help="number of neighbours")
    args = parser.parse_args()
    knn_search(args.query, args.category, args.k)
