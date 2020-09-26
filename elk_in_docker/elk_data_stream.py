#!/usr/bin/env python

from elasticsearch import Elasticsearch
import random
import time
es=Elasticsearch([{'host':'localhost','port':9200}])
index_name="wpt"

day = 1
while True:
    elem = {
            "day": day,
            "speed_of_load": random.uniform(0, 1)*3
    }
    res = es.index(index=index_name, body=elem)
    assert res['_shards']['successful']==1
    day += 1
    print("added another record...")
    time.sleep(3)
print(f"inserted {len(data_elements)} records")
