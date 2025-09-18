# Nested Fields vs Objects

## Understanding the Difference

**Object Fields** are the default way Elasticsearch handles complex data structures. When you store an array of objects, Elasticsearch internally flattens the structure, losing the relationship between fields within each object. This can lead to unexpected search results.

**Nested Fields** preserve the relationship between fields within each object in an array. They store each object as a separate hidden document, maintaining the integrity of the data relationships.

**Key Difference**: Object fields can return false positives in searches because field values get mixed up between array elements. Nested fields prevent this by keeping each object's data together.

---

## Simple Exercise: Student Grades

Let's use a simple example of students and their test scores to see the difference.

### Step 1: Create Index with Object Field (Default Behavior)

```bash
curl -X PUT "localhost:9200/students_object?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "tests": {
        "properties": {
          "subject": { "type": "keyword" },
          "score": { "type": "integer" }
        }
      }
    }
  }
}'
```

### Step 2: Create Index with Nested Field

```bash
curl -X PUT "localhost:9200/students_nested?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "tests": {
        "type": "nested",
        "properties": {
          "subject": { "type": "keyword" },
          "score": { "type": "integer" }
        }
      }
    }
  }
}'
```

### Step 3: Add Sample Data to Both Indices

```bash
curl -X POST "localhost:9200/students_object/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "name": "Alice",
  "tests": [
    { "subject": "math", "score": 95 },
    { "subject": "english", "score": 70 }
  ]
}'
```

```bash
curl -X POST "localhost:9200/students_nested/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "name": "Alice",
  "tests": [
    { "subject": "math", "score": 95 },
    { "subject": "english", "score": 70 }
  ]
}'
```

### Step 4: The Problem Query

Now let's search for students who scored 95 in English:

**Object Field Query (Wrong Results!):**
```bash
curl -X GET "localhost:9200/students_object/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "tests.subject": "english" } },
        { "term": { "tests.score": 95 } }
      ]
    }
  }
}'
```

**Nested Field Query (Correct Results!):**
```bash
curl -X GET "localhost:9200/students_nested/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "nested": {
      "path": "tests",
      "query": {
        "bool": {
          "must": [
            { "term": { "tests.subject": "english" } },
            { "term": { "tests.score": 95 } }
          ]
        }
      }
    }
  }
}'
```

### Step 5: Results Analysis

- **Object field result**: Returns Alice (WRONG! Alice scored 70 in English, not 95)
- **Nested field result**: Returns no results (CORRECT! No one scored 95 in English)

### Why This Happens

With object fields, Elasticsearch internally stores Alice's data like this:
```
tests.subject: ["math", "english"]
tests.score: [95, 70]
```

The relationship between "english" and "70" is lost! So when you search for "english" AND "95", Elasticsearch finds both values exist for Alice, even though they're not related.

With nested fields, each test is stored as a separate document, preserving the relationships:
```
{ "subject": "math", "score": 95 }
{ "subject": "english", "score": 70 }
```

### Exercise Questions

1. Add more students with different test scores
2. Try searching for students who scored 70 in Math - what happens with each index?
3. What query would you use to find students who scored above 90 in any subject using nested fields?

**Answer to Question 3:**
```bash
curl -X GET "localhost:9200/students_nested/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "nested": {
      "path": "tests",
      "query": {
        "range": {
          "tests.score": { "gt": 90 }
        }
      }
    }
  }
}'
```

### Quick Start Commands

To run this exercise, copy and paste these commands one by one into your terminal (assumes Elasticsearch is running on localhost:9200):

```bash
# Clean up any existing indices
curl -X DELETE "localhost:9200/students_object?pretty"
curl -X DELETE "localhost:9200/students_nested?pretty"

# Run all the commands above in order, then compare the search results!
```
