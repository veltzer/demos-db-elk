#!/bin/bash -eu
# Compare indexed vs non-indexed performance
python bulk_insert.py --data-file data/products_bulk.json

# Test only indexed configuration
python bulk_insert.py --test-type indexed

# Test only non-indexed configuration
python bulk_insert.py --test-type non-indexed
