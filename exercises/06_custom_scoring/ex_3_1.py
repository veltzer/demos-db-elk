#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Use Painless script for complex scoring logic
def search_with_script_score(query_text):
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
                                    // Custom scoring algorithm
                                    double base_score = _score;
                                    double rating_boost = doc["rating"].value * 2;
                                    double review_boost = Math.log(1 + doc["review_count"].value);
                                    double sales_boost = Math.log(1 + doc["sales_count"].value);
                                    double stock_penalty = doc["stock_quantity"].value > 0 ? 1.0 : 0.5;
                                    double sale_boost = doc["is_on_sale"].value ? 1.5 : 1.0;

                                    // Calculate conversion rate
                                    double views = doc["view_count"].value;
                                    double sales = doc["sales_count"].value;
                                    double conversion_rate = views > 0 ? sales / views : 0;
                                    double conversion_boost = 1 + (conversion_rate * 10);

                                    return base_score * rating_boost * review_boost *
                                           sales_boost * stock_penalty * sale_boost * conversion_boost;
                                """
                            }
                        }
                    }
                ],
                "boost_mode": "replace"  # Replace original score with script score
            }
        },
        "size": 5,
        "explain": False
    }

    result = es.search(index="products", body=query)

    print(f"\nScript-scored search: \"{query_text}\"")
    print("-" * 80)
    print(f"{'Score':<12} {'Rating':<8} {'Reviews':<10} {'Sales':<10} {'Conv Rate':<12} {'Name'}")
    print("-" * 80)

    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        conv_rate = p["sales_count"] / p["view_count"] if p["view_count"] > 0 else 0
        print(f"{hit['_score']:<12.2f} {p['rating']:<8.1f} {p['review_count']:<10} "
              f"{p['sales_count']:<10} {conv_rate:<12.4f} {p['name'][:25]}")

search_with_script_score("excellent features")
