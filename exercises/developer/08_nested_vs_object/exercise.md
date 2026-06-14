# Nested Fields vs Objects

This exercise explores one of the most surprising behaviors in
Elasticsearch: how it treats arrays of objects. The default handling
is fast and simple, but it silently breaks the link between the fields
of each array element. Understanding this is essential whenever you
model data like line items in an order, tags with attributes, or, as
here, a student's test scores. Choosing the wrong field type produces
queries that quietly return wrong answers rather than errors, so the
goal is to recognize when you need a `nested` field instead of a plain
object.

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

Why does the default flatten things at all? Under the hood
Elasticsearch is built on Lucene, which only understands flat
documents of fields and values, not nested structures. To fit an
array of objects into that flat model, the default object mapping
spreads each sub-field into its own multi-valued list. Nested fields
work around this by indexing each array element as a separate, hidden
Lucene document that is joined back to its parent at query time. That
extra bookkeeping is exactly why nested fields cost more but stay
correct.

---

## Simple Exercise: Student Grades

Let's use a simple example of students and their test scores to see the
difference.

### Step 1: Create Index with Object Field (Default Behavior)

This mapping defines `tests` with `subject` and `score` sub-fields but
gives it no explicit type. When a field has sub-properties and no type,
Elasticsearch treats it as an object. Notice there is nothing special
in the request: this is what you get by accident if you index an array
of objects without thinking about it.

See [`01_create_object_index.sh`](./01_create_object_index.sh)

### Step 2: Create Index with Nested Field

The only difference here is the single line `"type": "nested"` on the
`tests` field. That one keyword changes how every array element is
indexed and forces you to use a special query later. Comparing this
mapping side by side with Step 1 is the whole point of the exercise.

See [`02_create_nested_index.sh`](./02_create_nested_index.sh)

### Step 3: Add Sample Data to Both Indices

We index the identical document into both indices: Alice with a 95 in
math and a 70 in english. The data is the same; only the mapping
differs. That isolation is what lets us prove the behavior comes from
the field type and not from the data.

See [`03_index_object_doc.sh`](./03_index_object_doc.sh)

See [`04_index_nested_doc.sh`](./04_index_nested_doc.sh)

### Step 4: The Problem Query

Now let's search for students who scored 95 in English. We deliberately
pick a combination that does not exist in the data: Alice scored 95 in
math and 70 in english, so a correct search should match nobody.

**Object Field Query (Wrong Results!):**

This is a plain `bool` query with two `must` clauses, one matching the
subject and one matching the score. On the object index both clauses
are checked against the whole document independently. Because the
document does contain "english" somewhere and does contain 95
somewhere, both clauses pass and Alice matches.

See [`05_search_object_index.sh`](./05_search_object_index.sh)

**Nested Field Query (Correct Results!):**

The nested query looks almost the same but wraps the two clauses in a
`nested` block with `"path": "tests"`. This tells Elasticsearch to run
the inner query against each hidden sub-document one at a time, so both
conditions must be true for the same test. No single test is both
english and 95, so nothing matches. Forgetting the `nested` wrapper on
a nested field is a common pitfall: the query may even error or return
nothing useful, because the sub-documents are not directly searchable
from the top level.

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

The lesson is that on a flattened object the two arrays are parallel
lists with no link between positions. The query never knows that index
1 of `subject` pairs with index 1 of `score`. This is the same trap you
hit with any cross-field condition on an object array, so treat it as a
warning sign whenever you write two clauses about the same nested item.

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

This query reuses the `nested` wrapper but with a single `range` clause
matching any test whose score is greater than 90. Because the condition
only involves one field, the object index would actually give the right
answer here too. The cross-field correctness problem only appears when
you combine two or more conditions on the same item, as in Step 4. This
is a useful reminder that nested fields are not always required: reach
for them specifically when intra-object relationships must be preserved.

See [`07_nested_range_query.sh`](./07_nested_range_query.sh)

### Quick Start Commands

To run this exercise, copy and paste these commands one by one into your
terminal (assumes Elasticsearch is running on localhost:9200):

See [`08_delete_indices.sh`](./08_delete_indices.sh)
