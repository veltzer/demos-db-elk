#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Boost products based on proximity to user location
def search_by_proximity(query_text, user_location):
    query = {
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "description": query_text
                    }
                },
                "functions": [
                    {
                        "gauss": {
                            "location": {
                                "origin": user_location,
                                "scale": "10km",
                                "offset": "2km",
                                "decay": 0.5
                            }
                        },
                        "weight": 3
                    }
                ],
                "boost_mode": "multiply"
            }
        },
        "size": 5
    }

    result = es.search(index="products", body=query)

    print(f"\nProximity search from {user_location}")
    print("-" * 50)
    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        print(f"Score: {hit['_score']:.2f} | Location: {p['location']} | {p['name'][:40]}")

# Search for products near a specific location
search_by_proximity("quality", {"lat": 40.7, "lon": -74.0})
