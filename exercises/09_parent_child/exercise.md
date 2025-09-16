# Elasticsearch: Parent-Child Relationship Exercise

## Understanding Parent-Child Relationships

**Parent-Child relationships** in Elasticsearch allow you to store related documents separately while maintaining their connection. Unlike nested fields (which store everything in one document), parent-child relationships use separate documents that can be independently updated, deleted, and queried.

**Key Benefits**:
- **Independent updates**: Change child documents without reindexing the parent
- **Dynamic relationships**: Add/remove children without affecting the parent
- **Better performance**: For scenarios with many children per parent

**Use Case**: Blog posts (parents) and their comments (children). Comments can be added, updated, or deleted independently of the blog post.

---

## Simple Exercise: Blog Posts and Comments

### Step 1: Create Index with Parent-Child Mapping

```bash
curl -X PUT "localhost:9200/blog?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "content": { "type": "text" },
      "author": { "type": "keyword" },
      "comment_text": { "type": "text" },
      "commenter": { "type": "keyword" },
      "my_join_field": {
        "type": "join",
        "relations": {
          "post": "comment"
        }
      }
    }
  }
}' 
```

### Step 2: Add Parent Documents (Blog Posts)

```bash
curl -X POST "localhost:9200/blog/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "title": "Learning Elasticsearch",
  "content": "Elasticsearch is a powerful search engine...",
  "author": "John",
  "my_join_field": {
    "name": "post"
  }
}'
```

```bash
curl -X POST "localhost:9200/blog/_doc/2?pretty" -H 'Content-Type: application/json' -d'
{
  "title": "Advanced Search Techniques",
  "content": "In this post we will explore advanced features...",
  "author": "Sarah",
  "my_join_field": {
    "name": "post"
  }
}'
```

### Step 3: Add Child Documents (Comments)

**Important**: Child documents must be indexed with routing to the same shard as their parent!

```bash
curl -X POST "localhost:9200/blog/_doc/101?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Great article! Very helpful.",
  "commenter": "Alice",
  "my_join_field": {
    "name": "comment",
    "parent": "1"
  }
}'
```

```bash
curl -X POST "localhost:9200/blog/_doc/102?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Thanks for sharing this knowledge.",
  "commenter": "Bob",
  "my_join_field": {
    "name": "comment",
    "parent": "1"
  }
}'
```

```bash
curl -X POST "localhost:9200/blog/_doc/103?routing=2&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Could you explain more about aggregations?",
  "commenter": "Charlie",
  "my_join_field": {
    "name": "comment",
    "parent": "2"
  }
}'
```

### Step 4: Query Examples

**Find all blog posts:**
```bash
curl -X GET "localhost:9200/blog/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "my_join_field": "post"
    }
  }
}'
```

**Find all comments:**
```bash
curl -X GET "localhost:9200/blog/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "my_join_field": "comment"
    }
  }
}'
```

**Find posts that have comments containing "helpful":**
```bash
curl -X GET "localhost:9200/blog/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "has_child": {
      "type": "comment",
      "query": {
        "match": {
          "comment_text": "helpful"
        }
      }
    }
  }
}'
```

**Find comments belonging to the "Learning Elasticsearch" post:**
```bash
curl -X GET "localhost:9200/blog/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "has_parent": {
      "parent_type": "post",
      "query": {
        "match": {
          "title": "Learning Elasticsearch"
        }
      }
    }
  }
}'
```

### Step 5: Update Child Document Independently

**Add a new comment without affecting the parent post:**
```bash
curl -X POST "localhost:9200/blog/_doc/104?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "I bookmarked this post for future reference!",
  "commenter": "Diana",
  "my_join_field": {
    "name": "comment",
    "parent": "1"
  }
}'
```

**Update an existing comment:**
```bash
curl -X POST "localhost:9200/blog/_doc/101?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Great article! Very helpful. I learned a lot.",
  "commenter": "Alice",
  "my_join_field": {
    "name": "comment",
    "parent": "1"
  }
}'
```

### Why Routing is Crucial

**The Problem**: Elasticsearch is a distributed system that spreads data across multiple shards. Without proper routing, parent and child documents could end up on different shards across different nodes.

**Why Same Shard Matters**:
- **Join operations happen at shard level**: Elasticsearch can only perform parent-child joins within a single shard
- **Network overhead**: If parent and child are on different shards, Elasticsearch would need to send data across the network between nodes
- **Performance**: Cross-shard operations are much slower and more resource-intensive

**Example Without Routing**:
```
Node 1, Shard 0: Blog Post "Learning Elasticsearch" (ID: 1)
Node 2, Shard 1: Comment "Great article!" (Parent: 1)
```
❌ **Result**: Elasticsearch cannot efficiently join these documents!

**Example With Routing**:
```
Node 1, Shard 0: Blog Post "Learning Elasticsearch" (ID: 1)
Node 1, Shard 0: Comment "Great article!" (Parent: 1, routing=1)
```
✅ **Result**: Both documents are on the same shard, joins work efficiently!

### Why Parent-Child Queries Are More Expensive

**1. Memory Usage**:
- Elasticsearch must load a **global ordinals** structure into memory
- This structure maps every child document to its parent across the entire index
- For large indices, this can consume significant heap memory

**2. Query Execution Process**:
```
Regular Query: Find documents → Return results
Parent-Child Query: 
  1. Load parent-child mapping into memory
  2. Find matching children/parents
  3. Join the results
  4. Return combined results
```

**3. Two-Phase Execution**:
- **Phase 1**: Find all matching children (or parents)
- **Phase 2**: Find their related parents (or children) and join
- Much more work than a simple document lookup

**4. Cannot Use Index Caching Effectively**:
- Results depend on the relationship between documents
- Harder to cache compared to simple term or match queries

**Performance Comparison Example**:
```bash
# Fast: Direct document search
curl -X GET "localhost:9200/blog/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "title": "Elasticsearch" } }
}'

# Slower: Parent-child relationship query
curl -X GET "localhost:9200/blog/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "has_child": {
      "type": "comment",
      "query": { "match": { "comment_text": "helpful" } }
    }
  }
}'
```

**When to Use Parent-Child vs Nested**:
- **Use Parent-Child**: When you frequently update children independently
- **Use Nested**: When you mostly read data and performance is critical

### Exercise Questions

1. Add a new blog post and several comments for it
2. Find all posts written by "Sarah"
3. Find all comments made by "Alice"
4. Update one of the comments without reindexing its parent post

### Clean Up Commands

```bash
# Remove the index when you're done
curl -X DELETE "localhost:9200/blog?pretty"
```