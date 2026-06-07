#!/bin/bash
# Create the index and import data
curl -X PUT "localhost:9200/sample-data" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "ip_address": { "type": "ip" },
      "status_code": { "type": "integer" },
      "response_time_ms": { "type": "integer" },
      "cpu_usage_percent": { "type": "float" },
      "memory_usage_percent": { "type": "float" },
      "total_amount": { "type": "float" },
      "data_type": { "type": "keyword" }
    }
  }
}'

# Import the data
curl -X POST "localhost:9200/sample-data/_bulk" -H 'Content-Type: application/json' --data-binary @sample_data.json
