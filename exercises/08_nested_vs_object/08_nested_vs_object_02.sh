#!/bin/bash
curl -X PUT "localhost:9200/students_nested?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "tests": {
        "type": "nested",
        "properties": {
          "subject": { "type": "keyword" },
          "score": { "type": "integer" }
        }
      }
    }
  }
}'
