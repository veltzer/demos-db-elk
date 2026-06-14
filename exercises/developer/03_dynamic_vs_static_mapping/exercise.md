# Dynamic vs Static Mappings in Elasticsearch

## Objective

Learn the differences between dynamic and static mappings in Elasticsearch
and understand when to use each approach.

A mapping is the schema of an Elasticsearch index. It describes every field
in your documents and tells Elasticsearch how to store, index, and search
each one. Unlike a relational database, where the schema is always declared
up front, Elasticsearch can either build the schema for you on the fly
(dynamic mapping) or use one you define yourself (static mapping). The choice
has lasting consequences: once a field's type is set, it cannot be changed
without reindexing, so understanding mappings early saves a great deal of
pain later.

## Prerequisites

- Python 3.x installed
- Elasticsearch running locally (default: <http://localhost:9200>)
- Python elasticsearch module installed (`pip install elasticsearch`)

## Background

### Dynamic Mapping

- Elasticsearch automatically detects and adds new fields when documents are
  indexed
- Field types are inferred from the data
- Convenient but can lead to mapping conflicts

When a field is seen for the first time, Elasticsearch guesses its type from
the value: a JSON number becomes `long` or `float`, a JSON boolean becomes
`boolean`, and a JSON string becomes a `text` field with a `keyword`
sub-field (or a `date` if it parses as one). This guess is locked in for the
whole index. The danger is that the very first document silently decides the
type for every future document, and that decision is hard to undo.

### Static Mapping

- You explicitly define the mapping before indexing data
- Provides control over field types and indexing options
- Prevents mapping conflicts and ensures data consistency

Defining the mapping yourself is the equivalent of writing a `CREATE TABLE`
statement before inserting rows. You decide whether a string is full-text
searchable, exactly matchable, or both; whether a number is an `integer` or
a `float`; and what date format to expect. This control is what makes a
static mapping the right default for any system you intend to run in
production.

## Part 1: Dynamic Mapping

### Exercise 1.1: Observe Dynamic Mapping Behavior

See [`01_observe_dynamic_mapping.py`](./01_observe_dynamic_mapping.py)

This script indexes a single document into a fresh `dynamic_test` index
without any mapping, then asks Elasticsearch to print the mapping it
generated. Notice that you never told Elasticsearch the schema; it inferred
one from the values you sent.

**What's happening:** As the document is indexed, Elasticsearch inspects each
field and records a type for it. Watch how `age` (an integer) becomes `long`,
`score` (a decimal) becomes `float`, `is_active` becomes `boolean`, and
`joined_date`, because the string matches a date pattern, becomes `date`. The
`name` string becomes a `text` field with a `keyword` sub-field underneath
it. That last pattern is the default for every string and is worth
remembering.

**Task:** Run the code and observe the field types Elasticsearch assigned
automatically.

### Exercise 1.2: Dynamic Mapping Conflicts

See [`02_dynamic_mapping_conflicts.py`](./02_dynamic_mapping_conflicts.py)

This script indexes a second document into the same `dynamic_test` index, but
this time `age` carries the string value `"thirty"` instead of a number.
Because the first document already locked `age` to the numeric type `long`,
Elasticsearch cannot store the word `thirty` there and rejects the document.

**Why this matters:** This is the core risk of dynamic mapping. The type was
decided by whichever document arrived first, and every later document must
conform to it. In a real system, a single malformed record early in an
index's life can dictate the schema, and a later record with a different
shape will fail to index. There is no automatic coercion across types, and
you cannot simply change `age` from `long` to `text` afterward; that requires
creating a new index and reindexing.

**Task:** Run this code and observe the mapping conflict error. Why does it
occur?

## Part 2: Static Mapping

### Exercise 2.1: Create Static Mapping

See [`03_create_static_mapping.py`](./03_create_static_mapping.py)

This script creates a `static_test` index and passes a full mapping in the
create call, before any document exists. Each field is given an explicit
type: `name` is `text` with a `keyword` sub-field, `age` is `integer` rather
than the `long` that dynamic mapping would have chosen, `joined_date` is a
`date` with an explicit `yyyy-MM-dd` format, and `tags` is a pure `keyword`
field.

**Why this matters:** Defining the mapping up front removes the guesswork.
You decide that `age` only needs `integer` range, that dates must arrive in a
specific format (so a stray value cannot be misread), and that `tags` should
be exact-match values rather than analyzed prose. Compare the printed mapping
against the one from Part 1 and note where your choices differ from
Elasticsearch's defaults.

**Task:** Create the index with static mapping and compare it to the dynamic
mapping from Part 1.

### Exercise 2.2: Index Documents with Static Mapping

See [`04_index_documents_static_mapping.py`](./04_index_documents_static_mapping.py)

This script indexes three documents into the `static_test` index you just
created. Each document includes `description` text and a `tags` list, the
fields the later search and aggregation exercises rely on.

**What's happening:** Because the mapping already exists, Elasticsearch does
not infer any types here; it validates each value against the schema you
defined. The documents succeed because they match the declared types. This is
the payoff of a static mapping: predictable, validated ingestion instead of
silent type guessing.

**Task:** Index the documents and verify they were indexed successfully.

## Part 3: Comparing Search Capabilities

### Exercise 3.1: Text vs Keyword Fields

See [`05_text_vs_keyword_fields.py`](./05_text_vs_keyword_fields.py)

**Task:** Run both searches and observe the difference between text and keyword
field searches.

### Exercise 3.2: Aggregations

See [`06_aggregations.py`](./06_aggregations.py)

**Task:** Run the aggregation and analyze the results.

## Part 4: Advanced Mapping Features

### Exercise 4.1: Multi-fields

See [`07_multi_fields.py`](./07_multi_fields.py)

**Task:** Compare the results of searching on `name` vs `name.keyword`.

### Exercise 4.2: Disable Dynamic Mapping

See [`08_disable_dynamic_mapping.py`](./08_disable_dynamic_mapping.py)

**Task:** Observe what happens when trying to index a document with unmapped
fields when dynamic mapping is set to "strict".

## Challenges

### Challenge 1: Design a Mapping

Design and implement a static mapping for an e-commerce product catalog with
the following requirements:

- Product name (searchable and sortable)
- Description (full-text searchable)
- Price (numeric, for range queries)
- Categories (multiple values, for filtering)
- In stock (boolean)
- Created date
- Rating (1-5 scale)

### Challenge 2: Migration Strategy

Write a Python script that:

1. Reads the mapping from an existing index
1. Creates a new index with modified mapping
1. Reindexes all documents from the old index to the new one
1. Verifies the migration was successful

### Challenge 3: Dynamic Templates

Research and implement dynamic templates to automatically map fields based on
naming patterns:

- Fields ending with `_date` should be mapped as dates
- Fields starting with `is_` should be mapped as booleans
- Fields ending with `_count` should be mapped as integers

## Best Practices

1. **Always define mappings explicitly for production systems**
1. **Use multi-fields when you need both analyzed and exact matching**
1. **Set `dynamic: false` or `dynamic: strict` to prevent mapping explosions**
1. **Test your mappings with sample data before going to production**
1. **Document your mapping decisions and field purposes**
1. **Consider using index templates for consistent mappings across indices**

## Summary Questions

1. What are the main differences between dynamic and static mappings?
1. When would you choose dynamic mapping over static mapping?
1. What is the purpose of multi-fields in Elasticsearch?
1. How can you prevent mapping conflicts in production?
1. What are the implications of changing a fields mapping after data has been
   indexed?

## Resources

- [Elasticsearch Mapping Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)
- [Dynamic Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-mapping.html)
- [Field Data Types](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html)
- [Python Elasticsearch Client](https://elasticsearch-py.readthedocs.io/)
