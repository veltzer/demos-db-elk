#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Random scoring for result variation
def search_with_randomization(query_text, user_id):
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
                        "random_score": {
                            "seed": user_id,  # Same seed = same random order for user
                            "field": "_seq_no"
                        },
                        "weight": 0.3  # Control randomness strength
                    },
                    {
                        "field_value_factor": {
                            "field": "rating",
                            "factor": 2
                        },
                        "weight": 0.7
                    }
                ],
                "score_mode": "sum",
                "boost_mode": "multiply"
            }
        },
        "size": 5
    }

    print(f"\nRandomized search for user {user_id}")
    print("-" * 50)

    result = es.search(index="products", body=query)
    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        print(f"Score: {hit['_score']:.2f} | Rating: {p['rating']} | {p['name'][:40]}")

# Same user gets consistent results
search_with_randomization("product", user_id=12345)
search_with_randomization("product", user_id=12345)  # Same results

# Different user gets different results
search_with_randomization("product", user_id=67890)
