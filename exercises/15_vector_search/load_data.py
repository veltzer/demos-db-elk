#!/usr/bin/env python
"""Index a small corpus of articles, each with a dense_vector embedding.

Run `15_vector_search_01.sh` first to create the index. Each document gets an
"embedding" computed by embedding.py so we can later search by vector
similarity (kNN) as well as by keywords (BM25).
"""

from typing import Any

from elasticsearch import Elasticsearch

from embedding import embed

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "articles"

# A handful of short articles across a few topics. Documents that share words
# land near each other in vector space with our toy embedding.
ARTICLES = [
    {"title": "Stock market hits record high",
     "content": "shares rallied as investors bought into the market",
     "category": "finance"},
    {"title": "Central bank raises interest rates",
     "content": "the bank raised rates to cool inflation in the market",
     "category": "finance"},
    {"title": "New smartphone released",
     "content": "the phone ships with a faster chip and better camera",
     "category": "tech"},
    {"title": "Breakthrough in machine learning",
     "content": "researchers trained a neural network on a huge dataset",
     "category": "tech"},
    {"title": "Local team wins the championship",
     "content": "the team beat their rivals in a thrilling final game",
     "category": "sports"},
    {"title": "Marathon record broken",
     "content": "the runner finished the race in record time",
     "category": "sports"},
]


def load() -> None:
    """Embed and index every article, then refresh so they are searchable."""
    for i, article in enumerate(ARTICLES, start=1):
        doc: dict[str, Any] = dict(article)
        # Embed title + content together for a richer document vector.
        doc["embedding"] = embed(f"{article['title']} {article['content']}")
        result = es.index(index=INDEX_NAME, id=str(i), document=doc)
        assert result["_shards"]["successful"] >= 1
        print(f"indexed #{i}: {article['title']}")

    es.indices.refresh(index=INDEX_NAME)
    print(f"\nindexed {len(ARTICLES)} articles into '{INDEX_NAME}'")


if __name__ == "__main__":
    load()
