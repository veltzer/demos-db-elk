#!/bin/bash
# Create both indexed and non-indexed indices with 10,000 documents each
python create_data.py --create-both --docs 10000

# Or create more documents for better performance testing
python create_data.py --create-both --docs 50000
