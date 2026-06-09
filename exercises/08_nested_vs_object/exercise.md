# Nested Fields vs Objects

## Understanding the Difference

**Object Fields** are the default way Elasticsearch handles complex data
structures. When you store an array of objects, Elasticsearch internally
flattens the structure, losing the relationship between fields within each
object. This can lead to unexpected search results.

**Nested Fields** preserve the relationship between fields within each object in
an array. They store each object as a separate hidden document, maintaining the
integrity of the data relationships.

**Key Difference**: Object fields can return false positives in searches because
field values get mixed up between array elements. Nested fields prevent this by
keeping each object's data together.

---

## Simple Exercise: Student Grades

Let's use a simple example of students and their test scores to see the
difference.

### Step 1: Create Index with Object Field (Default Behavior)

See [`01_create_object_index.sh`](./01_create_object_index.sh)

### Step 2: Create Index with Nested Field

See [`02_create_nested_index.sh`](./02_create_nested_index.sh)

### Step 3: Add Sample Data to Both Indices

See [`03_index_object_doc.sh`](./03_index_object_doc.sh)

See [`04_index_nested_doc.sh`](./04_index_nested_doc.sh)

### Step 4: The Problem Query

Now let's search for students who scored 95 in English:

**Object Field Query (Wrong Results!):**
See [`05_search_object_index.sh`](./05_search_object_index.sh)

**Nested Field Query (Correct Results!):**
See [`06_search_nested_index.sh`](./06_search_nested_index.sh)

### Step 5: Results Analysis

- **Object field result**: Returns Alice (WRONG! Alice scored 70 in English,
  not 95)
- **Nested field result**: Returns no results (CORRECT! No one scored 95 in
  English)

### Why This Happens

With object fields, Elasticsearch internally stores Alice's data like this:

```
tests.subject: ["math", "english"]
tests.score: [95, 70]
```

The relationship between "english" and "70" is lost! So when you search for
"english" AND "95", Elasticsearch finds both values exist for Alice, even though
they're not related.

With nested fields, each test is stored as a separate document, preserving the
relationships:

```
{ "subject": "math", "score": 95 }
{ "subject": "english", "score": 70 }
```

### Exercise Questions

1. Add more students with different test scores
1. Try searching for students who scored 70 in Math - what happens with each
   index?
1. What query would you use to find students who scored above 90 in any subject
   using nested fields?

**Answer to Question 3:**
See [`07_nested_range_query.sh`](./07_nested_range_query.sh)

### Quick Start Commands

To run this exercise, copy and paste these commands one by one into your
terminal (assumes Elasticsearch is running on localhost:9200):

See [`08_delete_indices.sh`](./08_delete_indices.sh)
