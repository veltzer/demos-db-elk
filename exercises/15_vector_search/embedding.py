#!/usr/bin/env python
"""A tiny, dependency-free text embedding.

Real vector search uses a trained model (e.g. sentence-transformers) to turn
text into a dense vector that captures meaning. To keep this exercise fully
self-contained — no model download, no extra pip packages — we use a small
deterministic "bag-of-words hashing" embedding instead.

It is NOT semantically smart: it maps words to fixed buckets and L2-normalises
the result, so documents that share words end up close together in vector
space. That is enough to *demonstrate* kNN mechanics. The `Exercises` section
of the README shows how to swap this for real sentence-transformers vectors.

The dimension is intentionally small (16) so the vectors are easy to print and
reason about.
"""

import math

DIMS = 16


def embed(text: str) -> list[float]:
    """Map text to a fixed-length, L2-normalised vector.

    Each token bumps the bucket chosen by its hash; the vector is then
    normalised so cosine similarity behaves sensibly.
    """
    vec = [0.0] * DIMS
    for token in text.lower().split():
        # Deterministic, stable across runs (unlike Python's salted hash()).
        bucket = sum(ord(c) for c in token) % DIMS
        vec[bucket] += 1.0

    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


if __name__ == "__main__":
    # Quick sanity check: similar sentences should share buckets.
    for sentence in ("the quick brown fox", "a quick brown dog", "stock market crash"):
        print(f"{sentence!r:30} -> {embed(sentence)}")
