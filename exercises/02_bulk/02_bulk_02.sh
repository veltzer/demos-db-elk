#!/bin/bash -eu
# Generate default dataset (10K products, 5K customers, 20K orders)
python generate_data.py

# Generate smaller dataset for quick testing
python generate_data.py --products 1000 --customers 500 --orders 2000

# Generate larger dataset for stress testing
python generate_data.py --products 50000 --customers 10000 --orders 100000
