#!/usr/bin/env python

from elasticsearch7 import Elasticsearch
import random
import time
es=Elasticsearch([{'host':'localhost','port':9200}])
index_name="my-index"

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
    time.sleep(1)
print(f"inserted {len(data_elements)} records")
