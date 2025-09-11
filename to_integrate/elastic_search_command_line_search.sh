#!/bin/bash -eu
curl -X GET "localhost:9200/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "query_string": {
      "query": "Veltzer",
      "default_field": "Surname"
    }
  }
}
'
