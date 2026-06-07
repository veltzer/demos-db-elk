#!/bin/bash
curl -X PUT "localhost:9200/students_object?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "tests": {
        "properties": {
          "subject": { "type": "keyword" },
          "score": { "type": "integer" }
        }
      }
    }
  }
}'
