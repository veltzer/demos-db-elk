#!/bin/bash -eu
# Generate all types of sample data (4000 records total)
python generate_sample_data.py --count 1000 --output sample_data.json

# Or generate specific data types
python generate_sample_data.py --type web_logs --count 500 --output web_logs.json
python generate_sample_data.py --type ecommerce --count 500 --output ecommerce.json
