#!/bin/bash -eu
# Generate only products with specific settings
python generate_data.py --products 100000 --customers 0 --orders 0 --format ndjson
