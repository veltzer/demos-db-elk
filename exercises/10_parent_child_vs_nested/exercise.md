# Nested vs Parent-Child Comparison Exercise

## Understanding the Trade-offs

When dealing with one-to-many relationships in Elasticsearch, you have two main options: **Nested fields** and **Parent-Child relationships**. This exercise will help you understand when to use each approach by implementing the same scenario both ways.

**Nested Fields**: Store related data as nested objects within the same document
**Parent-Child**: Store related data as separate documents with join relationships

---

## Exercise: Blog Posts and Comments (Both Approaches)

Let's implement the same blog and comments scenario using both approaches to see the differences in practice.

### Step 1: Create Both Index Types

**Nested Index:**
```bash
curl -X PUT "localhost:9200/blog_nested?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "author": { "type": "keyword" },
      "comments": {
        "type": "nested",
        "properties": {
          "text": { "type": "text" },
          "commenter": { "type": "keyword" },
          "date": { "type": "date" }
        }
      }
    }
  }
}'
```

**Parent-Child Index:**
```bash
curl -X PUT "localhost:9200/blog_parent_child?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "author": { "type": "keyword" },
      "comment_text": { "type": "text" },
      "commenter": { "type": "keyword" },
      "date": { "type": "date" },
      "relation": {
        "type": "join",
        "relations": { "post": "comment" }
      }
    }
  }
}'
```

### Step 2: Add Sample Data

**Nested - Everything in One Document:**
```bash
curl -X POST "localhost:9200/blog_nested/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "title": "Getting Started with Elasticsearch",
  "author": "John",
  "comments": [
    {
      "text": "Great tutorial!",
      "commenter": "Alice",
      "date": "2024-01-15"
    },
    {
      "text": "Very helpful, thanks!",
      "commenter": "Bob",
      "date": "2024-01-16"
    }
  ]
}'
```

**Parent-Child - Separate Documents:**
```bash
# Parent document
curl -X POST "localhost:9200/blog_parent_child/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "title": "Getting Started with Elasticsearch",
  "author": "John",
  "relation": { "name": "post" }
}'

# Child documents
curl -X POST "localhost:9200/blog_parent_child/_doc/101?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Great tutorial!",
  "commenter": "Alice",
  "date": "2024-01-15",
  "relation": { "name": "comment", "parent": "1" }
}'

curl -X POST "localhost:9200/blog_parent_child/_doc/102?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Very helpful, thanks!",
  "commenter": "Bob",
  "date": "2024-01-16",
  "relation": { "name": "comment", "parent": "1" }
}'
```

### Step 3: Compare Query Approaches

**Test 1: Find posts with comments containing "helpful"**

*Nested Query:*
```bash
curl -X GET "localhost:9200/blog_nested/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "nested": {
      "path": "comments",
      "query": {
        "match": { "comments.text": "helpful" }
      }
    }
  }
}'
```

*Parent-Child Query:*
```bash
curl -X GET "localhost:9200/blog_parent_child/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "has_child": {
      "type": "comment",
      "query": {
        "match": { "comment_text": "helpful" }
      }
    }
  }
}'
```

**Test 2: Find all comments by Alice**

*Nested Query:*
```bash
curl -X GET "localhost:9200/blog_nested/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "nested": {
      "path": "comments",
      "query": {
        "term": { "comments.commenter": "Alice" }
      },
      "inner_hits": {}
    }
  }
}'
```

*Parent-Child Query:*
```bash
curl -X GET "localhost:9200/blog_parent_child/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "relation": "comment" } },
        { "term": { "commenter": "Alice" } }
      ]
    }
  }
}'
```

### Step 4: Compare Update Scenarios

**Adding a New Comment**

*Nested - Requires Full Document Reindex:*
```bash
curl -X POST "localhost:9200/blog_nested/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "title": "Getting Started with Elasticsearch",
  "author": "John",
  "comments": [
    {
      "text": "Great tutorial!",
      "commenter": "Alice",
      "date": "2024-01-15"
    },
    {
      "text": "Very helpful, thanks!",
      "commenter": "Bob",
      "date": "2024-01-16"
    },
    {
      "text": "I bookmarked this post!",
      "commenter": "Charlie",
      "date": "2024-01-17"
    }
  ]
}'
```

*Parent-Child - Add Independent Document:*
```bash
curl -X POST "localhost:9200/blog_parent_child/_doc/103?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "I bookmarked this post!",
  "commenter": "Charlie",
  "date": "2024-01-17",
  "relation": { "name": "comment", "parent": "1" }
}'
```

**Updating an Existing Comment**

*Nested - Must Update Entire Document:*
```bash
curl -X POST "localhost:9200/blog_nested/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "title": "Getting Started with Elasticsearch",
  "author": "John",
  "comments": [
    {
      "text": "Great tutorial! Updated my comment.",
      "commenter": "Alice",
      "date": "2024-01-15"
    },
    {
      "text": "Very helpful, thanks!",
      "commenter": "Bob",
      "date": "2024-01-16"
    },
    {
      "text": "I bookmarked this post!",
      "commenter": "Charlie",
      "date": "2024-01-17"
    }
  ]
}'
```

*Parent-Child - Update Individual Comment:*
```bash
curl -X POST "localhost:9200/blog_parent_child/_doc/101?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Great tutorial! Updated my comment.",
  "commenter": "Alice",
  "date": "2024-01-15",
  "relation": { "name": "comment", "parent": "1" }
}'
```

### Step 5: Compare Storage and Performance

**Check Document Counts:**
```bash
# Nested: 1 document total (all comments stored within)
curl -X GET "localhost:9200/blog_nested/_count?pretty"

# Parent-Child: Multiple documents (1 parent + N children)
curl -X GET "localhost:9200/blog_parent_child/_count?pretty"
```

**View Actual Storage:**
```bash
# Nested: All data in one document
curl -X GET "localhost:9200/blog_nested/_doc/1?pretty"

# Parent-Child: Separate documents
curl -X GET "localhost:9200/blog_parent_child/_doc/1?pretty"
curl -X GET "localhost:9200/blog_parent_child/_doc/101?routing=1&pretty"
```

**Performance Test - Add Many Comments:**
```bash
# For nested: Each addition requires reindexing the entire document
# For parent-child: Each addition is a simple new document

# Try adding 10 more comments to each approach and notice the difference!
```

### Key Differences Summary

| Aspect | Nested | Parent-Child |
|--------|---------|-------------|
| **Storage** | All data in one document | Separate documents |
| **Document Count** | 1 document per blog post | 1 document per blog post + 1 per comment |
| **Updates** | Must reindex entire document | Update individual children only |
| **Query Performance** | Faster (single document) | Slower (join operations + global ordinals) |
| **Memory Usage** | Lower | Higher (global ordinals mapping) |
| **Routing Required** | No | Yes (children must be on same shard) |
| **Best Use Case** | Read-heavy, stable data | Write-heavy children, frequent updates |
| **Query Complexity** | Moderate (`nested` queries) | Higher (`has_child`/`has_parent` queries) |

### When to Choose Which?

**Choose Nested When:**
- Comments/children are rarely updated
- You prioritize query performance
- You have limited memory resources
- Data relationships are stable

**Choose Parent-Child When:**
- Comments/children are frequently added/updated/deleted
- You need to update children without affecting parents
- You have sufficient memory for global ordinals
- You need maximum flexibility in data management

### Real-World Performance Simulation

**Add 5 More Comments - Compare the Effort:**

*Nested (must include ALL existing comments each time):*
```bash
# You'd need to fetch the existing document, add the new comment to the array,
# and reindex the entire document - more complex and resource intensive
```

*Parent-Child (simple new documents):*
```bash
curl -X POST "localhost:9200/blog_parent_child/_doc/104?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Fourth comment!",
  "commenter": "David",
  "date": "2024-01-18",
  "relation": { "name": "comment", "parent": "1" }
}'

# Much simpler - just add new documents independently!
```

### Exercise Questions

1. **Scenario**: A news website with articles that receive hundreds of comments daily. Which approach would you choose?

2. **Scenario**: A product catalog where each product has 3-5 reviews that are rarely updated. Which approach would you choose?

3. **Scenario**: A social media platform where posts can have thousands of comments, and comments are frequently edited or deleted. Which approach would you choose?

### Clean Up

```bash
curl -X DELETE "localhost:9200/blog_nested?pretty"
curl -X DELETE "localhost:9200/blog_parent_child?pretty"
```

### Exercise Answers

1. **Parent-Child** - High volume of comment updates favors independent document management
2. **Nested** - Stable, low-volume data benefits from faster query performance  
3. **Parent-Child** - Frequent edits and deletes make independent documents essential
