#!/usr/bin/env python

from elasticsearch7 import Elasticsearch
from constants import index, host, port, filename
import csv

"""
What will this script do?
1) check that es is running and try to connect to it.
    If not - show error to user.
2) check that es has an index called "index" if not, create it.
3) if we have an index called "index" - removed all data from it.
4) enter our set of data (notes) into the search engine.
"""

es=Elasticsearch([{'host':host, 'port':port}])
""" checking elasticsearch connection status as per:
    https://stackoverflow.com/questions/31208136/check-elasticsearch-connection-status-in-python/31644507
"""
if not es.ping():
    raise ValueError(f"cannot connect to es. Please make sure you have elastic search running on {host}:{port}")
print(f"We connected to es")

if es.indices.exists(index=index):
    print("yes index exists, removing data from the index")
    res = es.delete_by_query(index=index, body={"query": {"match_all": {}}})
    deleted = res['deleted']
    assert res['total'] == deleted
    print(f"deleted {deleted} records")
else:
    print("no index, creating one")
    body = {}
    es.indices.create(index = index, body = body)

with open(filename) as cvs_file:
    r = csv.reader(cvs_file)
    for row in r:
        data = {
            "title": row[8],
            "text": row[9]
        }
        res = es.index(index=index, body=data)
        assert res['_shards']['successful']==1
