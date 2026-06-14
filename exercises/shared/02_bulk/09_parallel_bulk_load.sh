#!/bin/bash -eu
# Split large file
split -l 10000 products.ndjson products_part_

# Load parts in parallel
for file in products_part_*; do
    python bulk_insert.py --data-file $file &
done
