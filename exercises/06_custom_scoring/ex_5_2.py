#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Scoring based on historical click-through rates
def ctr_optimized_search(query_text):
    # First, update some products with CTR data
    ctr_updates = [
        {"id": 1, "clicks": 150, "impressions": 1000},
        {"id": 2, "clicks": 300, "impressions": 2000},
        {"id": 3, "clicks": 50, "impressions": 1500},
        {"id": 4, "clicks": 500, "impressions": 3000},
        {"id": 5, "clicks": 75, "impressions": 500}
    ]

    for update in ctr_updates:
        es.update(
            index="products",
            id=update["id"],
            body={
                "doc": {
                    "clicks": update["clicks"],
                    "impressions": update["impressions"]
                }
            }
        )

    es.indices.refresh(index="products")

    # Search with CTR optimization
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
                                    if (!doc.containsKey("clicks") || !doc.containsKey("impressions")) {
                                        return 1.0;
                                    }

                                    double clicks = doc["clicks"].value;
                                    double impressions = doc["impressions"].value;

                                    if (impressions == 0) return 1.0;

                                    // Wilson score interval for CTR
                                    double ctr = clicks / impressions;
                                    double z = 1.96; // 95% confidence
                                    double n = impressions;

                                    double center = ctr + z*z/(2*n);
                                    double spread = z * Math.sqrt(ctr*(1-ctr)/n + z*z/(4*n*n));
                                    double denominator = 1 + z*z/n;

                                    double lower_bound = (center - spread) / denominator;

                                    return 1 + (lower_bound * 10); // Scale the CTR boost
                                """
                            }
                        }
                    }
                ],
                "boost_mode": "multiply"
            }
        },
        "size": 5
    }

    result = es.search(index="products", body=query)

    print(f"\nCTR-Optimized Search: \"{query_text}\"")
    print("-" * 60)
    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        ctr = 0
        if "clicks" in p and "impressions" in p and p["impressions"] > 0:
            ctr = p["clicks"] / p["impressions"]
        print(f"Score: {hit['_score']:.2f} | CTR: {ctr:.3f} | {p['name'][:40]}")

ctr_optimized_search("quality product")
