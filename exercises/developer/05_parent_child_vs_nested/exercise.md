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

One single `POST` to `_doc/1` writes the post and all its comments at
once. Even though Lucene will index each comment as a separate hidden
document internally, from your point of view there is exactly one
document with id `1`. Indexing and retrieving the whole thing is atomic.

**Parent-Child - Separate Documents:**
See [`04_add_parent_child_documents.sh`](./04_add_parent_child_documents.sh)

Here the same data takes three separate `POST` requests: one for the post
(id `1`) and one for each comment (ids `101` and `102`). Two details are
essential:

- Each comment carries `"relation": { "name": "comment", "parent": "1" }`
  so Elasticsearch knows which post it belongs to.
- Each comment request includes `?routing=1`. Routing decides which shard
  a document lands on. By forcing the children to use the parent's id as
  the routing value, they are guaranteed to sit on the same shard as the
  parent. Forget this and the join silently fails, because a child on a
  different shard is invisible to its parent.

### Step 3: Compare Query Approaches

Now you will run equivalent searches against both indices. Pay attention
to how different the query shapes are even though the question is the
same. The query language reveals where the work happens internally.

#### Test 1: Find posts with comments containing "helpful"

*Nested Query:*
See [`05_nested_query_comments_helpful.sh`](./05_nested_query_comments_helpful.sh)

The `nested` query needs a `path` (`comments`) so Elasticsearch knows
which hidden sub-documents to search, and it matches inside that scope.
The result is the parent blog post. Because everything is in one document
already, no cross-document join happens; this is why nested reads are
fast.

*Parent-Child Query:*
See [`06_has_child_query_comments_helpful.sh`](./06_has_child_query_comments_helpful.sh)

The `has_child` query says "return parents that have at least one child
of type `comment` matching this inner query". Under the hood
Elasticsearch must first find matching children, then map them back to
their parents using global ordinals (an in-memory table linking children
to parents). That mapping is the join cost, and it grows with the number
of children.

#### Test 2: Find all comments by Alice

This test exposes a fundamental asymmetry: with nested fields you cannot
return a comment on its own, only the parent that contains it.

*Nested Query:*
See [`07_nested_query_comments_by_alice.sh`](./07_nested_query_comments_by_alice.sh)

This query adds `"inner_hits": {}`. Without it, the hit would be the
whole blog post and you would not know which comment matched. `inner_hits`
asks Elasticsearch to also return the specific nested objects that
satisfied the query, so you can see Alice's comment by itself. This is the
only way to surface individual nested objects.

*Parent-Child Query:*
See [`08_parent_child_query_comments_by_alice.sh`](./08_parent_child_query_comments_by_alice.sh)

With parent-child, comments are real, independent documents, so you can
query them directly. This is a plain `bool` query: match documents where
`relation` is `comment` and `commenter` is `Alice`. No join is needed
here at all, because you are searching the child documents themselves
rather than asking about their parents. This direct addressability of
children is parent-child's biggest advantage.

### Step 4: Compare Update Scenarios

This is where the trade-off bites hardest. Lucene documents are
immutable: an "update" in Elasticsearch always means deleting the old
document and writing a brand new one. The question is how much data you
have to rewrite each time.

#### Adding a New Comment

*Nested - Requires Full Document Reindex:*
See [`09_nested_add_comment_reindex.sh`](./09_nested_add_comment_reindex.sh)

To add one comment you must send the entire post again, including the two
comments that already existed, plus the new third one. Elasticsearch
deletes document `1` and rewrites all of it. With two existing comments
this is cheap, but imagine a post with a thousand comments: adding one
means resending all thousand and one every time.

*Parent-Child - Add Independent Document:*
See [`10_parent_child_add_comment_document.sh`](./10_parent_child_add_comment_document.sh)

Adding a comment is just one small new document (id `103`) with the right
`parent` and `routing`. The post and the other comments are untouched.
The cost of adding a comment stays constant no matter how many comments
already exist.

#### Updating an Existing Comment

*Nested - Must Update Entire Document:*
See [`11_nested_update_comment_reindex.sh`](./11_nested_update_comment_reindex.sh)

To change a single word in Alice's comment, you again resend the whole
post with every comment. There is no way to edit just one nested object
in place; the unit of writing is always the entire top-level document.

*Parent-Child - Update Individual Comment:*
See [`12_parent_child_update_comment_document.sh`](./12_parent_child_update_comment_document.sh)

Here you simply rewrite document `101` (Alice's comment). The post and the
other comments are not even mentioned. Editing or deleting one comment
touches only that one document, which is exactly why parent-child suits
data where children change often and independently.

### Step 5: Compare Storage and Performance

Now make the difference concrete by inspecting what is actually stored.

**Check Document Counts:**
See [`13_compare_document_counts.sh`](./13_compare_document_counts.sh)

The nested index reports a count of `1`: as far as the public document
count is concerned, one blog post equals one document regardless of how
many comments it holds. The parent-child index reports a higher count
(one parent plus each child), because every comment is a first-class
document. This count difference is the most direct evidence of the two
storage models.

**View Actual Storage:**
See [`14_view_stored_documents.sh`](./14_view_stored_documents.sh)

Fetching `blog_nested/_doc/1` returns the post with its comments array
embedded. For parent-child you must fetch each document separately, and
fetching a child (`_doc/101`) requires `?routing=1` because Elasticsearch
needs the routing value to know which shard the document lives on. This
is a recurring gotcha: any direct get, update, or delete of a child must
repeat the same routing value used when it was created.

**Performance Test - Add Many Comments:**
See [`15_performance_test_instructions.sh`](./15_performance_test_instructions.sh)

The lesson this script points to: nested write cost grows with the number
of existing children, while parent-child write cost stays flat. Try it
and feel the difference in effort rather than just reading about it.

### Key Differences Summary

The table below distills everything you just observed. The two rows worth
re-reading are query performance and memory: nested wins on read speed
because there is no join, while parent-child pays for its write
flexibility with the memory of global ordinals and a slower, join-based
query path.

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

This final comparison makes the write-cost asymmetry impossible to miss.

*Nested (must include ALL existing comments each time):*
See [`16_nested_add_many_comments_note.sh`](./16_nested_add_many_comments_note.sh)

This script is a note rather than a command, and that is the point: there
is no shortcut. To add comments you would have to read the current
document, append to the comments array in your application, and reindex
the whole thing. The work scales with how much is already there.

*Parent-Child (simple new documents):*
See [`17_parent_child_add_comment_simple.sh`](./17_parent_child_add_comment_simple.sh)

By contrast, adding a comment is a single self-contained `POST`. No read,
no merge, no rewrite of existing data. For high-volume, frequently edited
children this is the difference between a system that scales and one that
grinds to a halt.

### Exercise Questions

For each scenario, weigh two things: how often the children change, and
how much you care about raw query speed and memory. Frequent child
changes push you toward parent-child; stable, read-heavy data pushes you
toward nested.

1. **Scenario**: A news website with articles that receive hundreds of comments
   daily. Which approach would you choose?
1. **Scenario**: A product catalog where each product has 3-5 reviews that are
   rarely updated. Which approach would you choose?
1. **Scenario**: A social media platform where posts can have thousands of
   comments, and comments are frequently edited or deleted. Which approach would
   you choose?

### Clean Up

Delete both indices so your cluster is left clean and you can rerun the
exercise from scratch. Removing an index frees its storage and any
in-memory structures such as the global ordinals the join field built up.

See [`18_cleanup_delete_indices.sh`](./18_cleanup_delete_indices.sh)

### Exercise Answers

1. **Parent-Child** - High volume of comment updates favors independent document
   management
1. **Nested** - Stable, low-volume data benefits from faster query performance
1. **Parent-Child** - Frequent edits and deletes make independent documents
   essential
