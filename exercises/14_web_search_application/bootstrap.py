#!/usr/bin/env python
"""Prepare the search index for the notes application.

What this script does:

1. Connect to Elasticsearch (and fail clearly if it is not reachable).
2. Ensure the `notes` index exists, creating it if necessary.
3. Empty the index so re-running is idempotent.
4. Load the sample dataset (movies.csv) as notes — each movie's title and
   overview become a note's `title` and `text`.
"""

import csv

from elasticsearch import Elasticsearch

from constants import ES_URL, FILENAME, INDEX


def main() -> None:
    es = Elasticsearch(ES_URL)

    if not es.ping():
        raise ValueError(
            f"cannot connect to Elasticsearch. "
            f"Please make sure it is running on {ES_URL}"
        )
    print(f"connected to Elasticsearch on {ES_URL}")

    if es.indices.exists(index=INDEX):
        print("index exists, removing existing data")
        result = es.delete_by_query(index=INDEX, query={"match_all": {}})
        print(f"deleted {result['deleted']} records")
    else:
        print("index does not exist, creating it")
        es.indices.create(index=INDEX)

    inserted = 0
    with open(FILENAME, newline="") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # skip the header row
        for row in reader:
            if len(row) < 10:
                continue
            note = {
                "title": row[8],   # original_title
                "text": row[9],    # overview
            }
            result = es.index(index=INDEX, document=note)
            assert result["_shards"]["successful"] >= 1
            inserted += 1

    es.indices.refresh(index=INDEX)
    print(f"inserted {inserted} notes into '{INDEX}'")


if __name__ == "__main__":
    main()
