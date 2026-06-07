#!/bin/bash -eu
curl -X GET "localhost:9200/students_object/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "tests.subject": "english" } },
        { "term": { "tests.score": 95 } }
      ]
    }
  }
}'
