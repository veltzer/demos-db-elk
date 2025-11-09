from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Index blog posts (parent documents)
blog_posts = [
    {
        "title": "Getting Started with Elasticsearch",
        "content": "Elasticsearch is a powerful search engine that provides full-text search capabilities...",
        "author": "alice_tech",
        "created_at": "2024-01-15T10:00:00",
        "tags": ["elasticsearch", "search", "tutorial"],
        "views": 1500,
        "likes": 45,
        "status": "published",
        "join_field": "blog_post"  # Marking as parent type
    },
    {
        "title": "Advanced Query DSL Techniques",
        "content": "In this post, we will explore advanced Query DSL features including bool queries...",
        "author": "bob_dev",
        "created_at": "2024-01-20T14:30:00",
        "tags": ["elasticsearch", "query-dsl", "advanced"],
        "views": 2300,
        "likes": 78,
        "status": "published",
        "join_field": "blog_post"
    },
    {
        "title": "Scaling Elasticsearch Clusters",
        "content": "Learn how to properly scale your Elasticsearch cluster for production workloads...",
        "author": "charlie_ops",
        "created_at": "2024-02-01T09:15:00",
        "tags": ["elasticsearch", "scaling", "production"],
        "views": 3200,
        "likes": 92,
        "status": "published",
        "join_field": "blog_post"
    }
]

# Index parent documents
for i, post in enumerate(blog_posts, 1):
    es.index(index="blog_system", id=f"post_{i}", body=post)
    print(f"Indexed blog post: {post['title']}")

# Refresh to make documents searchable
es.indices.refresh(index="blog_system")
