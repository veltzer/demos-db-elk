#!/bin/bash -eu
curl -X POST "localhost:9200/students_object/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "name": "Alice",
  "tests": [
    { "subject": "math", "score": 95 },
    { "subject": "english", "score": 70 }
  ]
}'
