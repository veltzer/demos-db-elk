#!/bin/bash
# Verify Elasticsearch is running
curl -X GET "localhost:9200"

# Install Python dependencies (for methods 3 & 4)
pip install requests elasticsearch
