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

An **embedding** is just a list of numbers (a vector) that stands in for a
piece of text. The whole game of vector search is to convert both your
documents and your query into vectors using the *same* model, then ask "which
document vectors point in nearly the same direction as the query vector?".
Because the model is trained so that related meanings produce nearby vectors,
geometric distance becomes a proxy for semantic similarity. Elasticsearch
stores these vectors in a `dense_vector` field and does the distance maths for
you.

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

**What's happening.** The mapping mixes two worlds on purpose. `title` and
`content` are ordinary `text` fields, so Elasticsearch analyses them into
tokens and builds the usual inverted index for BM25 keyword search.
`category` is a `keyword` (stored verbatim, not analysed) so it can be used
as an exact-match filter. The `embedding` field is the new piece: it holds the
16-number vector for each article.

**Why `dims` must match.** A `dense_vector` field commits to a fixed length the
moment you index the first document. Every vector in the field must have
exactly that many components, because kNN compares vectors component by
component — mismatched lengths are meaningless. If you later switch to a real
model that outputs 384 numbers, you must change `dims` to 384 and reindex.

**Why `index: true` and `similarity: cosine`.** Setting `index: true` tells
Elasticsearch to build a special graph structure (HNSW, explained in the
Discussion) so that approximate nearest-neighbour queries are fast. Without it
the vectors are merely stored and can only be searched with a slow exact scan.
`similarity: cosine` chooses *how* "closeness" is measured. Cosine compares the
*angle* between two vectors and ignores their length, which suits text
embeddings where direction encodes meaning. This is also why `embedding.py`
normalises every vector to length one.

### Step 2: Load the Data

```bash
./load_data.py
```

This embeds each article's title and content and indexes six short articles
across the `finance`, `tech` and `sports` categories.

**Why embed at index time.** The vector is computed *before* the document is
stored, then saved alongside it. Search never re-reads or re-embeds the
stored documents — it only compares their precomputed vectors against the
query vector. This is what makes vector search scale: the expensive embedding
work happens once per document, not once per query.

**One vital rule: use the same embedding on both sides.** `load_data.py` and
the search scripts both import `embed` from `embedding.py`. If the indexing
embedding and the query embedding ever differed, their vectors would live in
different coordinate systems and the distances would be nonsense. After
indexing, the script calls `refresh` so the new documents become immediately
visible to search rather than waiting for the periodic refresh.

### Step 3: Run a kNN Search

```bash
./knn_search.py "stock market rally"
```

The two finance articles rank highest because their vectors are nearest the
query vector. (With this word-overlap embedding the query must share vocabulary
with the documents; see the note above and Exercise 3 for true semantic
matching.)

**What's happening under the hood.** `knn_search.py` embeds your query string
into a 16-number vector, then sends a `knn` block naming the `embedding` field,
the `query_vector`, `k` (how many neighbours to return) and `num_candidates`.
Elasticsearch walks the HNSW graph from the query point, gathers up to
`num_candidates` close vectors per shard, keeps the best `k`, and returns them
ranked by similarity. The `_score` you see is derived from the cosine
similarity, so a higher score means a smaller angle between the document and
query vectors. Notice there is no keyword matching at all here: a document can
rank highly without containing any of the query's words, which is exactly the
behaviour pure keyword search cannot give you.

### Step 4: Filter the kNN Search

Restrict the neighbours to a single category:

```bash
./knn_search.py --category sports "a close contest"
```

**Why filtered kNN is special.** When you pass `--category`, the script adds a
`filter` term inside the `knn` block. The key point is *where* the filter is
applied: Elasticsearch enforces it *during* the graph traversal, so it only
ever counts vectors that already match the category toward your `k` results.
The naive alternative — find the `k` nearest neighbours first, then throw away
the ones in the wrong category — can leave you with far fewer than `k` results
(or none) when matches are rare. Filtering inside the search avoids that trap
and still returns a full set of relevant neighbours.

### Step 5: Hybrid Search

Blend keyword and vector relevance in one query:

```bash
./hybrid_search.py "market rates"
```

**What's happening.** `hybrid_search.py` sends *both* a `query` (a BM25
`multi_match` over `title` and `content`) and a `knn` block in the same
`_search` request. Elasticsearch runs the two independently and then adds the
scores together per document, so a document that scores well on *either* the
keyword side or the vector side rises to the top. The `boost` value on each
side lets you weight one signal more than the other; here both are `1.0`, an
even split. Note that `title^2` inside the keyword query separately boosts
title matches over content matches — a reminder that you can tune relevance at
several levels at once.

**Why combine them at all.** Keyword and vector search fail in opposite ways.
BM25 is precise on exact and rare terms (product codes, names) but blind to
paraphrase. Vectors capture meaning but can drift on short queries or miss an
exact term the user typed deliberately. Blending the two gives a ranking that
is robust when either signal alone would be weak.

### Step 6: Clean Up

```bash
./remove_data.py        # empty the index
```

**Empty versus drop.** `remove_data.py` runs a `delete_by_query` with
`match_all`, so it removes every document but leaves the index and its mapping
in place. That is handy when you want to reload fresh data without recreating
the `dense_vector` field. To get rid of the index entirely — mapping, settings
and all — drop it instead.

To remove the index entirely, see
[`02_drop_articles_index.sh`](./02_drop_articles_index.sh).

## Discussion

The points below explain the trade-offs you are implicitly making with the
defaults in these scripts. None of them change what the exercise does, but
understanding them is what separates running vector search from tuning it.

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
