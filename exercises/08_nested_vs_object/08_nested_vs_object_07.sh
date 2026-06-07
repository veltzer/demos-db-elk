#!/bin/bash -eu
curl -X GET "localhost:9200/students_nested/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "nested": {
      "path": "tests",
      "query": {
        "range": {
          "tests.score": { "gt": 90 }
        }
      }
    }
  }
}'
