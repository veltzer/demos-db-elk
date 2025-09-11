#!/usr/bin/env python

from elasticsearch import Elasticsearch

es=Elasticsearch([{'host':'localhost','port':9200}])
res = es.delete_by_query(index="wpt", body={"query": {"match_all": {}}})
deleted = res['deleted']
assert res['total'] == deleted
print(f"deleted {deleted} records")
