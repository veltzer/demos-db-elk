#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Parameterized script for flexible scoring
def search_with_params(query_text, user_preferences):
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
                        "script_score": {
                            "script": {
                                "source": """
                                    double score = _score;

                                    // Apply user preference weights
                                    score *= Math.pow(doc["rating"].value / 5.0, params.rating_weight);
                                    score *= Math.pow(Math.log(2 + doc["review_count"].value) / 10, params.popularity_weight);

                                    // Price sensitivity
                                    if (params.max_price > 0 && doc["price"].value > params.max_price) {
                                        score *= 0.5;  // Penalize over-budget items
                                    }

                                    // Brand preference
                                    if (params.preferred_brands.contains(doc["brand"].value)) {
                                        score *= params.brand_boost;
                                    }

                                    return score;
                                """,
                                "params": user_preferences
                            }
                        }
                    }
                ],
                "boost_mode": "replace"
            }
        },
        "size": 5
    }

    result = es.search(index="products", body=query)

    print(f"\nPersonalized search with user preferences")
    print(f"Preferences: {user_preferences}")
    print("-" * 60)
    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        print(f"Score: {hit['_score']:.2f} | ${p['price']} | {p['brand']} | {p['name'][:30]}")

# Different user profiles
budget_shopper = {
    "rating_weight": 1,
    "popularity_weight": 2,
    "max_price": 100,
    "preferred_brands": ["BookWorld", "HomePlus"],
    "brand_boost": 1.5
}

premium_shopper = {
    "rating_weight": 3,
    "popularity_weight": 1,
    "max_price": 0,  # No budget limit
    "preferred_brands": ["TechPro", "StyleMax"],
    "brand_boost": 2.0
}

search_with_params("quality product", budget_shopper)
search_with_params("quality product", premium_shopper)
