#!/usr/bin/env python

from elasticsearch import Elasticsearch
import json
import sys

es=Elasticsearch([{'host':'localhost','port':9200}])

doc = {
    'size' : 10000,
    'query': {
        'match_all' : {}
    }
}
res=es.search(index='wpt', body=doc, scroll='1m')
number_of_results = res['hits']['total']['value']
print(f"number_of_results {number_of_results}")
hits = res['hits']['hits']
for hit in hits:
    print(json.dumps(hit['_source'], indent=4, sort_keys=True))
