#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

def advanced_ecommerce_scoring(query_text, user_context):
    """
    Complex scoring for e-commerce with:
    - Business goals (profit, inventory)
    - User context (history, preferences)
    - Item quality (ratings, returns)
    - Temporal factors (trends, seasons)
    """

    query = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"name": {"query": query_text, "boost": 2}}},
                            {"match": {"description": query_text}},
                            {"match": {"tags": {"query": query_text, "boost": 1.5}}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                "functions": [
                    # Business metrics
                    {
                        "field_value_factor": {
                            "field": "profit_margin",
                            "factor": 3,
                            "modifier": "square"
                        },
                        "weight": user_context.get("business_weight", 1)
                    },
                    # Inventory management - boost high stock items
                    {
                        "filter": {"range": {"stock_quantity": {"gt": 50}}},
                        "weight": 2
                    },
                    # Clear low stock items
                    {
                        "filter": {
                            "bool": {
                                "must": [
                                    {"range": {"stock_quantity": {"gt": 0, "lte": 10}}},
                                    {"term": {"is_on_sale": True}}
                                ]
                            }
                        },
                        "weight": 3
                    },
                    # Quality signals
                    {
                        "script_score": {
                            "script": {
                                "source": """
                                    // Bayesian average for ratings
                                    double C = 10;  // Minimum reviews for credibility
                                    double m = 4.0; // Prior mean rating
                                    double reviews = doc["review_count"].value;
                                    double rating = doc["rating"].value;

                                    double bayesian_rating = (C * m + reviews * rating) / (C + reviews);
                                    return Math.pow(bayesian_rating / 5.0, 2);
                                """
                            }
                        },
                        "weight": 4
                    },
                    # Trending items (high recent sales)
                    {
                        "gauss": {
                            "last_restocked": {
                                "origin": "now",
                                "scale": "7d",
                                "decay": 0.5
                            }
                        },
                        "weight": 2
                    },
                    # Personalization based on category preference
                    {
                        "filter": {"terms": {"category": user_context.get("preferred_categories", [])}},
                        "weight": 3
                    }
                ],
                "score_mode": "sum",
                "boost_mode": "multiply",
                "max_boost": 20
            }
        },
        "size": 10,
        "_source": ["name", "price", "rating", "review_count", "profit_margin", "stock_quantity"],
        "explain": False
    }

    result = es.search(index="products", body=query)

    print(f"\nAdvanced E-commerce Scoring")
    print(f"Query: \"{query_text}\"")
    print(f"User Context: {user_context}")
    print("-" * 80)
    print(f"{'Score':<10} {'Price':<10} {'Rating':<10} {'Reviews':<10} {'Margin':<10} {'Stock':<10} {'Name'}")
    print("-" * 80)

    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        print(f"{hit['_score']:<10.2f} ${p['price']:<9.2f} {p['rating']:<10.1f} "
              f"{p['review_count']:<10} {p['profit_margin']:<10.2f} {p['stock_quantity']:<10} "
              f"{p['name'][:20]}")

# Different user contexts
regular_user = {
    "business_weight": 1,
    "preferred_categories": ["Electronics", "Books"]
}

vip_user = {
    "business_weight": 0.5,  # Less focus on profit for VIP
    "preferred_categories": ["Electronics", "Sports"]
}

advanced_ecommerce_scoring("premium", regular_user)
advanced_ecommerce_scoring("premium", vip_user)
