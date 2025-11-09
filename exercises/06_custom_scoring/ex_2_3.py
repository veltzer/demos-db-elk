#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Boost products near a target price point
def search_with_price_preference(query_text, target_price, price_flexibility):
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
                            "price": {
                                "origin": target_price,
                                "scale": price_flexibility,  # e.g., "50" for ±$50
                                "decay": 0.5
                            }
                        },
                        "weight": 2
                    }
                ],
                "boost_mode": "multiply"
            }
        },
        "size": 10
    }

    result = es.search(index="products", body=query)

    print(f"\nPrice-optimized search (target: ${target_price} ± ${price_flexibility})")
    print("-" * 60)
    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        price_diff = abs(p["price"] - target_price)
        print(f"Score: {hit['_score']:.2f} | Price: ${p['price']} (Δ${price_diff:.2f}) | {p['name'][:30]}")

search_with_price_preference("product", target_price=100, price_flexibility=30)
