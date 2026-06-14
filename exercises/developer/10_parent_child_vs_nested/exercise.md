# Nested vs Parent-Child Comparison Exercise

## Understanding the Trade-offs

When dealing with one-to-many relationships in Elasticsearch, you have two main
options: **Nested fields** and **Parent-Child relationships**. This exercise
will help you understand when to use each approach by implementing the same
scenario both ways.

**Nested Fields**: Store related data as nested objects within the same document
**Parent-Child**: Store related data as separate documents with join
relationships

Why does this choice exist at all? Elasticsearch is built on Lucene,
which stores flat documents. There are no real "tables" to join like in a
relational database. If you simply put an array of objects in a normal
field, Lucene flattens it: the values of all objects get mixed together,
so a search for "comment by Alice that says helpful" could match a
document where Alice said something else and Bob said "helpful". Both
nested fields and parent-child relations are mechanisms that restore the
ability to keep the boundaries between related objects intact, but they
do it in very different ways with very different costs.

The core trade-off you will feel in this exercise is **read speed versus
write flexibility**. Nested keeps everything in one document, so reads
are fast but any change means rewriting the whole document. Parent-child
keeps documents separate, so each child can change on its own, but
queries must perform a join at search time, which costs CPU and memory.

---

## Exercise: Blog Posts and Comments (Both Approaches)

Let's implement the same blog and comments scenario using both approaches to see
the differences in practice.

### Step 1: Create Both Index Types

The mapping is where the two strategies diverge before you index a single
document. Read both scripts side by side and notice how the relationship
is declared.

**Nested Index:**
See [`01_create_nested_index.sh`](./01_create_nested_index.sh)

In the nested index, `comments` is given `"type": "nested"`. This tells
Elasticsearch to treat each comment as its own hidden Lucene document
behind the scenes, even though they all live inside one visible blog
document. That hidden separation is what lets a query say "this single
comment matched both conditions" instead of matching across comments.

**Parent-Child Index:**
See [`02_create_parent_child_index.sh`](./02_create_parent_child_index.sh)

In the parent-child index there is no nested block. Instead there is a
`join` field named `relation` that declares `"post": "comment"`, meaning
documents of type `post` can have children of type `comment`. Notice the
comment fields (`comment_text`, `commenter`, `date`) sit at the top level
alongside the post fields. Both document types share one flat mapping;
the `relation` field is what marks which role a given document plays.

**Why this matters**: parent and child documents must live in the same
index and on the same shard. The join only works within a single shard,
which is why routing becomes mandatory later on.

### Step 2: Add Sample Data

**Nested - Everything in One Document:**
See [`03_add_nested_document.sh`](./03_add_nested_document.sh)

**Parent-Child - Separate Documents:**
See [`04_add_parent_child_documents.sh`](./04_add_parent_child_documents.sh)

### Step 3: Compare Query Approaches

#### Test 1: Find posts with comments containing "helpful"

*Nested Query:*
See [`05_nested_query_comments_helpful.sh`](./05_nested_query_comments_helpful.sh)

*Parent-Child Query:*
See [`06_has_child_query_comments_helpful.sh`](./06_has_child_query_comments_helpful.sh)

#### Test 2: Find all comments by Alice

*Nested Query:*
See [`07_nested_query_comments_by_alice.sh`](./07_nested_query_comments_by_alice.sh)

*Parent-Child Query:*
See [`08_parent_child_query_comments_by_alice.sh`](./08_parent_child_query_comments_by_alice.sh)

### Step 4: Compare Update Scenarios

#### Adding a New Comment

*Nested - Requires Full Document Reindex:*
See [`09_nested_add_comment_reindex.sh`](./09_nested_add_comment_reindex.sh)

*Parent-Child - Add Independent Document:*
See [`10_parent_child_add_comment_document.sh`](./10_parent_child_add_comment_document.sh)

#### Updating an Existing Comment

*Nested - Must Update Entire Document:*
See [`11_nested_update_comment_reindex.sh`](./11_nested_update_comment_reindex.sh)

*Parent-Child - Update Individual Comment:*
See [`12_parent_child_update_comment_document.sh`](./12_parent_child_update_comment_document.sh)

### Step 5: Compare Storage and Performance

**Check Document Counts:**
See [`13_compare_document_counts.sh`](./13_compare_document_counts.sh)

**View Actual Storage:**
See [`14_view_stored_documents.sh`](./14_view_stored_documents.sh)

**Performance Test - Add Many Comments:**
See [`15_performance_test_instructions.sh`](./15_performance_test_instructions.sh)

### Key Differences Summary

| Aspect | Nested | Parent-Child |
|--------|---------|-------------|
| **Storage** | All data in one document | Separate documents |
| **Document Count** | 1 per blog post | 1 per post + 1 per comment |
| **Updates** | Must reindex whole document | Update individual children |
| **Query Performance** | Faster (single doc) | Slower (joins + ordinals) |
| **Memory Usage** | Lower | Higher (global ordinals mapping) |
| **Routing Required** | No | Yes (children on same shard) |
| **Best Use Case** | Read-heavy, stable data | Write-heavy children, updates |
| **Query Complexity** | Moderate (`nested`) | Higher (`has_child`) |

### When to Choose Which

#### Choose Nested When

- Comments/children are rarely updated
- You prioritize query performance
- You have limited memory resources
- Data relationships are stable

#### Choose Parent-Child When

- Comments/children are frequently added/updated/deleted
- You need to update children without affecting parents
- You have sufficient memory for global ordinals
- You need maximum flexibility in data management

### Real-World Performance Simulation

**Add 5 More Comments - Compare the Effort:**

*Nested (must include ALL existing comments each time):*
See [`16_nested_add_many_comments_note.sh`](./16_nested_add_many_comments_note.sh)

*Parent-Child (simple new documents):*
See [`17_parent_child_add_comment_simple.sh`](./17_parent_child_add_comment_simple.sh)

### Exercise Questions

1. **Scenario**: A news website with articles that receive hundreds of comments
   daily. Which approach would you choose?
1. **Scenario**: A product catalog where each product has 3-5 reviews that are
   rarely updated. Which approach would you choose?
1. **Scenario**: A social media platform where posts can have thousands of
   comments, and comments are frequently edited or deleted. Which approach would
   you choose?

### Clean Up

See [`18_cleanup_delete_indices.sh`](./18_cleanup_delete_indices.sh)

### Exercise Answers

1. **Parent-Child** - High volume of comment updates favors independent document
   management
1. **Nested** - Stable, low-volume data benefits from faster query performance
1. **Parent-Child** - Frequent edits and deletes make independent documents
   essential
