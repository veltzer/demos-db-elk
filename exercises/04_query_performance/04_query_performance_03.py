#!/usr/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def profile_query(index_name, query_body):
    """Use Elasticsearch's Profile API to get detailed timing"""
    
    profile_query = {
        **query_body,
        "profile": True
    }
    
    result = es.search(index=index_name, body=profile_query)
    
    print(f"\nProfile for index: {index_name}")
    print("-" * 50)
    print(f"Total took: {result['took']}ms")
    print(f"Total hits: {result['hits']['total']['value']}")
    
    if 'profile' in result:
        shards = result['profile']['shards']
        for i, shard in enumerate(shards):
            print(f"\nShard {i}:")
            for search in shard['searches']:
                print(f"  Query type: {search['query'][0]['type']}")
                print(f"  Time: {search['query'][0]['time_in_nanos'] / 1_000_000:.2f}ms")
                print("  Breakdown:")
                breakdown = search['query'][0]['breakdown']
                for key, value in sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:5]:
                    if value > 0:
                        print(f"    {key}: {value / 1_000_000:.2f}ms")

# Profile a complex query
complex_query = {
    "query": {
        "bool": {
            "must": [
                {"range": {"age": {"gte": 25, "lte": 50}}},
                {"term": {"is_active": True}}
            ],
            "should": [
                {"match": {"full_name": "John"}},
                {"terms": {"tags": ["python", "java"]}}
            ],
            "minimum_should_match": 1
        }
    }
}

profile_query('users_indexed', complex_query)
