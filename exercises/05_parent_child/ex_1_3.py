from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Index comments (child documents)
comments = [
    {
        "content": "Great tutorial! This helped me understand the basics.",
        "author": "user_john",
        "created_at": "2024-01-15T12:30:00",
        "likes": 5,
        "join_field": {
            "name": "comment",
            "parent": "post_1"  # Reference to parent document ID
        }
    },
    {
        "content": "Could you add more examples about aggregations?",
        "author": "user_jane",
        "created_at": "2024-01-15T15:45:00",
        "likes": 3,
        "join_field": {
            "name": "comment",
            "parent": "post_1"
        }
    },
    {
        "content": "The bool query section is excellent!",
        "author": "user_mike",
        "created_at": "2024-01-21T10:00:00",
        "likes": 8,
        "join_field": {
            "name": "comment",
            "parent": "post_2"
        }
    },
    {
        "content": "How does this compare to using nested queries?",
        "author": "user_sarah",
        "created_at": "2024-01-21T11:30:00",
        "likes": 6,
        "join_field": {
            "name": "comment",
            "parent": "post_2"
        }
    }
]

# Index child documents with routing
for i, comment in enumerate(comments, 1):
    parent_id = comment["join_field"]["parent"]
    es.index(
        index="blog_system",
        id=f"comment_{i}",
        body=comment,
        routing=parent_id  # IMPORTANT: routing required for child documents
    )
    print(f"Indexed comment for {parent_id}")

es.indices.refresh(index="blog_system")
