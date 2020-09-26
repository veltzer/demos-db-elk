#!/usr/bin/env python

from elasticsearch import Elasticsearch
es=Elasticsearch([{'host':'localhost','port':9200}])
index_name="wpt"

data_elements = [
        {
            "day": 1,
            "speed_of_load": 2.76,
        },
        {
            "day": 2,
            "speed_of_load": 2.56,
        },
        {
            "day": 3,
            "speed_of_load": 3.66,
        },
]

for data_element in data_elements: 
    res = es.index(index=index_name, body=data_element)
    print(res)
