# Elasticsearch Vector Search Exercise

This exercise demonstrates **vector search** (semantic / k-nearest-neighbour
search) in Elasticsearch — the technique behind "find similar items",
semantic search, recommendations and retrieval-augmented generation (RAG).

## Overview

Traditional search (BM25) matches documents by the *words* they contain.
Vector search instead represents each document as a `dense_vector` — a point in
a high-dimensional space — and finds the documents whose vectors are *closest*
to the query vector. With a real embedding model, closeness in that space
approximates closeness in *meaning*, so a search for "money and the economy"
can surface a finance article that never uses those exact words.

The exercise covers:

- A `dense_vector` field mapping with HNSW indexing (`index: true`)
- Turning text into vectors with a small, dependency-free embedding
- Approximate **kNN** search (`knn` in `_search`)
- **Filtered kNN** — restricting neighbours by a `keyword` field
- **Hybrid search** — blending BM25 and kNN scores in one query

> **About the embeddings.** Real systems use a trained model to produce
> embeddings. To keep this exercise self-contained (no model download, no extra
> dependencies), `embedding.py` uses a tiny deterministic hashing embedding
> based on **word overlap**: documents that share words end up near each other.
> This is enough to demonstrate the *mechanics* of kNN, but it has **no real
> semantic understanding** — a query only ranks a document highly if they share
> vocabulary. True meaning-based matching (e.g. "money" finding "stock market")
> only appears once you swap in a real model, which [Exercise 3](#exercises)
> walks through.

## Files

- `01_create_articles_index.sh` - Create the `articles` index with a
  `dense_vector` field
- `02_drop_articles_index.sh` - Drop the `articles` index
- `embedding.py` - Tiny deterministic text → vector function (no dependencies)
- `load_data.py` - Embed and index a small corpus of articles
- `knn_search.py` - kNN vector search (with optional category filter)
- `hybrid_search.py` - Combined BM25 + kNN (hybrid) search
- `remove_data.py` - Delete all documents from the index (keeps the mapping)

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install elasticsearch
```

### 2. Ensure Elasticsearch is Running

Elasticsearch should be reachable on `localhost:9200` with security disabled.
See the [`00_install`](../../shared/00_install/exercise.md) exercise if you
have not set it up yet. `dense_vector` kNN requires Elasticsearch 8.0+ (this
course uses
9.1.3).

## Quick Start

### Step 1: Create the Index

See [`01_create_articles_index.sh`](./01_create_articles_index.sh)

The `embedding` field is declared as a `dense_vector` with `dims: 16`,
`index: true` and `similarity: cosine`. The dimension **must** match the
embedding produced by `embedding.py`.

### Step 2: Load the Data

```bash
./load_data.py
```

This embeds each article's title and content and indexes six short articles
across the `finance`, `tech` and `sports` categories.

### Step 3: Run a kNN Search

```bash
./knn_search.py "stock market rally"
```

The two finance articles rank highest because their vectors are nearest the
query vector. (With this word-overlap embedding the query must share vocabulary
with the documents; see the note above and Exercise 3 for true semantic
matching.)

### Step 4: Filter the kNN Search

Restrict the neighbours to a single category:

```bash
./knn_search.py --category sports "a close contest"
```

### Step 5: Hybrid Search

Blend keyword and vector relevance in one query:

```bash
./hybrid_search.py "market rates"
```

### Step 6: Clean Up

```bash
./remove_data.py        # empty the index
```

To remove the index entirely, see
[`02_drop_articles_index.sh`](./02_drop_articles_index.sh).

## Discussion

- **Why approximate?** Exact kNN compares the query against every vector — fine
  for six documents, far too slow for millions. Setting `index: true` builds an
  **HNSW** graph so Elasticsearch can find near neighbours in roughly
  logarithmic time. `num_candidates` trades recall for speed: more candidates
  explored per shard means better accuracy and slightly higher latency.
- **Similarity metric.** We use `cosine`, which ignores vector magnitude and
  compares direction — a good default for text embeddings. `dot_product`
  (requires normalised vectors) and `l2_norm` are the other options.
- **Filtered kNN** applies the filter *during* the graph search, so you still
  get `k` results that satisfy the filter — unlike post-filtering, which could
  return fewer than `k`.
- **Hybrid search** matters because lexical and semantic search fail in
  different ways: BM25 misses paraphrases, vectors miss exact/rare terms.
  Summing their scores (optionally weighted with `boost`) gets the best of
  both. For production ranking, look at **RRF** (reciprocal rank fusion), which
  Elasticsearch can apply to combine result sets more robustly than raw score
  addition.

## Exercises

1. Increase the corpus in `load_data.py` and observe how ranking changes.
1. Change the `similarity` in `01_create_articles_index.sh` from `cosine` to
   `l2_norm`, reload, and compare the scores.
1. Swap the toy embedding for a real one: `pip install sentence-transformers`,
   then in `embedding.py` return
   `model.encode(text).tolist()` from `all-MiniLM-L6-v2` (384 dims) and update
   `dims` in `01_create_articles_index.sh` to `384`. Re-run and notice that
   semantically similar sentences now rank well even with no shared words.
1. Replace the hybrid query's score addition with **RRF** using the `retriever`
   syntax and compare the rankings.
1. Add `num_candidates` as a command-line flag to `knn_search.py` and watch how
   very low values hurt recall.
