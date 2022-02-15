#!/usr/bin/python3

from elasticsearch7 import Elasticsearch
client = Elasticsearch("http://localhost:9200")
resp = client.info()
print(resp)
