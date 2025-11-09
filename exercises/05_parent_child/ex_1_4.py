#!/bin/env python

from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Index replies to comments (grandchild documents)
replies = [
    {
        "content": "I agree! The examples are very clear.",
        "author": "user_alice",
        "created_at": "2024-01-15T13:00:00",
        "likes": 2,
        "join_field": {
            "name": "reply",
            "parent": "comment_1"  # Reply to comment_1
        }
    },
    {
        "content": "Check out the official documentation for more aggregation examples.",
        "author": "alice_tech",  # Author replying
        "created_at": "2024-01-15T16:00:00",
        "likes": 4,
        "join_field": {
            "name": "reply",
            "parent": "comment_2"
        }
    }
]

# Index replies with proper routing (must route to the root parent)
for i, reply in enumerate(replies, 1):
    # For replies, we need to route to the blog post (root parent)
    # In this case, comment_1 and comment_2 both belong to post_1
    es.index(
        index="blog_system",
        id=f"reply_{i}",
        body=reply,
        routing="post_1"  # Route to root parent (blog post)
    )
    print(f"Indexed reply to {reply['join_field']['parent']}")

es.indices.refresh(index="blog_system")
