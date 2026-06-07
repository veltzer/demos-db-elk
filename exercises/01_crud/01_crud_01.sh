#!/bin/bash
# Verify Elasticsearch is running
curl -X GET "localhost:9200" -u elastic:your-password

# Install Python dependencies (for methods 3 & 4)
pip install requests elasticsearch
