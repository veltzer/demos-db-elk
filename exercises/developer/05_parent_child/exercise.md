# Parent-Child Relationship Model for Hierarchical Data

## Objective

Learn how to model hierarchical relationships in Elasticsearch using
parent-child joins, understand their use cases, performance implications, and
query patterns.

## Background

Parent-child relationships allow you to model hierarchical data where documents
have relationships with other documents. Common use cases include:

- Blog posts and comments
- Products and reviews
- Companies and employees
- Questions and answers

Elasticsearch is built on Lucene, which stores flat documents and has no
concept of a SQL-style join across rows. The parent-child (or "join") feature
simulates a relationship by storing related documents in the same index and
the same shard, then linking them through a special `join` field. This lets
you update a child without re-indexing the parent, and query one side of the
relationship using the other.

Why does this matter? In a denormalized world you would copy parent data into
every child (or embed children inside the parent as nested objects). That is
fast to read but expensive to update: changing one comment means re-indexing
the whole post. Parent-child trades some query speed for the ability to update
parents and children independently.

## Part 1: Setting Up Parent-Child Mapping

The relationship is declared once, at the index level, inside the mapping. All
parents, children, and grandchildren live in the *same* index and share *one*
`join` field. The mapping lists which document type can be the parent of which
other type. This shared-index design is what allows Elasticsearch to keep
related documents on the same shard.

### Exercise 1.1: Create Index with Join Field

See [`01_create_join_index.py`](./01_create_join_index.py)

**Task:** Create the index and understand the join field structure.

**What's happening:** The mapping defines a field of `type: join` with a
`relations` block. Here `blog_post` is declared as a parent of `comment` and
`author_note`, and `comment` is in turn a parent of `reply`. This creates a
three-level hierarchy: post, comment, reply. The `relations` map is the
contract for the whole index; you cannot link two types unless they appear
here.

**Why this matters:** A join field can only define *one* relationship set per
index, and you cannot point a child at more than one parent type. The non-join
fields (`title`, `content`, `likes`, and so on) are shared by every document
type, so parents and children draw from the same field namespace. Plan your
field names so they make sense across all the document types in the index.

### Exercise 1.2: Index Parent Documents (Blog Posts)

See [`02_index_parent_blog_posts.py`](./02_index_parent_blog_posts.py)

**Task:** Index the parent documents and note how the `join_field` is set.

**What's happening:** For a parent document the `join_field` is set to just the
relation name, for example `"join_field": "blog_post"`. There is no parent to
point at, so a plain string is enough. The document id you assign (such as
`post_1`) becomes the anchor that children will reference later.

**Why this matters:** The parent's id is also its routing value by default,
which is why every child must be sent to that same routing key. Choose stable,
meaningful parent ids; if a parent id changes you would have to re-index all of
its descendants.

### Exercise 1.3: Index Child Documents (Comments)

See [`03_index_child_comments.py`](./03_index_child_comments.py)

**Task:** Index child documents and understand why routing is required.

**What's happening:** A child's `join_field` is an object with two keys: `name`
(the relation, here `comment`) and `parent` (the id of the parent document,
here `post_1`). The index call also passes `routing=parent_id`. Routing tells
Elasticsearch which shard to write the document to.

**Why this matters:** Parent and child *must* live on the same shard, because
join queries run shard-locally; they never reach across shards. By default a
document's shard is chosen from a hash of its own id, which would scatter
children away from their parent. Forcing the routing value to the parent id
guarantees the child lands on the parent's shard. Forget the routing and the
child may be unreachable from the parent, or indexing may fail outright.

### Exercise 1.4: Index Grandchild Documents (Replies to Comments)

See [`04_index_grandchild_replies.py`](./04_index_grandchild_replies.py)

**Task:** Understand the routing requirements for multi-level hierarchies.

**What's happening:** A reply points its `parent` at a *comment* id (such as
`comment_1`), but its routing value is the *root* parent (`post_1`), not the
immediate parent. The whole family tree, post plus comments plus replies, must
share a single shard, so routing always uses the top-level ancestor's id.

**Why this matters:** This is the most common multi-level pitfall. It feels
natural to route a reply to its comment, but the comment itself was routed to
the post. Routing to the comment id would compute a different shard and break
the chain. For any depth of hierarchy, the routing value stays fixed at the
root ancestor while only the `parent` reference changes per level. This is also
why the exercises warn you to keep hierarchies shallow: every level forces more
documents onto the same shard, which can unbalance the cluster.

## Part 2: Querying Parent-Child Relationships

Now that the data is linked, you can query across the relationship. The three
core join queries answer different questions. `has_child` returns *parents*
filtered by their children. `has_parent` returns *children* filtered by their
parent. `parent_id` returns the direct children of one known parent. Knowing
which query returns which side of the relationship is the key to using them
correctly.

### Exercise 2.1: Has Child Query

See [`05_has_child_query.py`](./05_has_child_query.py)

**Task:** Find all blog posts that have at least one comment.

**What's happening:** `has_child` takes the child `type` and an inner query.
It matches every parent that has at least one child of that type satisfying the
inner query. The hits returned are the *parent* documents, not the children.

**Why this matters:** Because the inner query runs against children but the
result is the parent, `has_child` is heavier than a normal query: the engine
must evaluate children and then join back to parents on each shard. Use it when
you genuinely need to filter parents by a property of their children.

### Exercise 2.2: Has Parent Query

See [`06_has_parent_query.py`](./06_has_parent_query.py)

**Task:** Find all comments on posts authored by a specific user.

**What's happening:** `has_parent` is the mirror image of `has_child`. You give
it the `parent_type` and an inner query against the parent; it returns the
*child* documents whose parent matches. Here it returns comments, filtered by a
property (the author) that lives on the post, not on the comment.

**Why this matters:** This lets a child be filtered by data it does not store
itself. Without parent-child you would have to copy the post author onto every
comment. The trade-off is the same join cost: the inner query runs on parents,
then the engine walks down to their children.

### Exercise 2.3: Parent ID Query

See [`07_parent_id_query.py`](./07_parent_id_query.py)

**Task:** Retrieve all comments for a specific blog post.

**What's happening:** `parent_id` takes a child `type` and a single parent
`id`, and returns the direct children of exactly that parent. It is the most
direct of the three join queries.

**Why this matters:** When you already know the parent id, prefer `parent_id`
over `has_child` or `has_parent`. It does not have to evaluate an inner query
across many documents, so it is the cheapest way to fetch a known parent's
children. The performance tips at the end of this exercise call this out
explicitly.

### Exercise 2.4: Children Aggregation

See [`08_children_aggregation.py`](./08_children_aggregation.py)

**Task:** Calculate the average number of likes on comments per blog post.

**What's happening:** The `children` aggregation is a bucket aggregation that
shifts the context from parents to their children. After selecting blog posts
with a `term` query, the `children` aggregation drops into the matching comment
documents, then nested sub-aggregations (like `terms` on the comment author)
run over those children.

**Why this matters:** Regular aggregations only see the documents matched by
the query. The `children` aggregation is what lets you summarize the *other*
side of the relationship without a separate query. It is the join-aware cousin
of the `nested` aggregation, which does the same thing for embedded nested
objects.

## Part 3: Advanced Parent-Child Patterns

### Exercise 3.1: Inner Hits - Getting Related Documents

See [`09_inner_hits_comments.py`](./09_inner_hits_comments.py)

**Task:** Retrieve blog posts with their most recent 5 comments.

**What's happening:** A plain `has_child` query tells you *which* parents
match, but it does not show you the matching children. Adding an `inner_hits`
block makes Elasticsearch attach the children that caused each parent to match,
right inside that parent's hit. You can size and sort the inner hits
independently, for example the top three comments by likes.

**Why this matters:** Without `inner_hits` you would need a second round trip:
one query to find the posts, then a `parent_id` query per post to fetch its
comments. `inner_hits` collapses that into a single request and keeps each
child grouped under its parent. The cost is a larger response payload, so cap
the inner hit `size` to what you actually display.

### Exercise 3.2: Scoring with Child Documents

See [`10_has_child_function_score.py`](./10_has_child_function_score.py)

**Task:** Score blog posts based on the number of comments they have.

**What's happening:** `has_child` accepts a `score_mode` that folds the
children's scores into the parent's relevance score. Combined with a
`function_score` inner query, you can turn a child property, such as the number
of comments, into a ranking signal for the parent.

**Why this matters:** This is how you make engagement influence search ranking,
for example pushing heavily commented posts higher. By default `has_child`
ignores child scores (`score_mode: none`); you must opt in with `min`, `max`,
`sum`, or `avg`. Computing child scores is more work than a simple existence
check, so only enable it when ranking truly depends on the children.

### Exercise 3.3: Complex Multi-Level Queries

See [`11_multi_level_has_child.py`](./11_multi_level_has_child.py)

**Task:** Find comments that have replies from the original post author.

**What's happening:** This query spans two levels of the hierarchy at once. It
looks at comments (`has_child` of type `reply`) whose replies match a condition
on the reply author. The three-level mapping from Exercise 1.1 is what makes
this possible.

**Why this matters:** Each additional join level multiplies the work, because
the engine resolves the relationship one level at a time. Multi-level join
queries are powerful but the slowest pattern here. If you find yourself
reaching across several levels frequently, that is a strong signal to
reconsider the data model, which is exactly what Part 4 explores.

## Part 4: Performance Considerations

Parent-child flexibility is not free. Join queries cost more CPU than ordinary
queries, and the join field keeps a global ordinals data structure in memory to
map parents to children quickly. This part measures those costs and contrasts
parent-child with the main alternative, nested documents.

### Exercise 4.1: Compare Parent-Child vs Nested Performance

See [`12_query_performance_benchmark.py`](./12_query_performance_benchmark.py)

**Task:** Compare the performance of different parent-child query types.

**What's happening:** The benchmark runs the different join query types and
times them, so you can see in numbers that `parent_id` is cheaper than
`has_child` and `has_parent`, and that deeper or more selective joins cost
more.

**Why this matters:** Measuring on your own data beats relying on rules of
thumb. Run it more than once: the first run pays a warm-up cost while global
ordinals are built and caches fill, so later runs are more representative of
steady state.

### Exercise 4.2: Create Alternative Denormalized Structure

See [`13_denormalized_nested_structure.py`](./13_denormalized_nested_structure.py)

**Task:** Compare query complexity between parent-child and nested approaches.

**What's happening:** This builds a second index where comments are embedded
inside the post as a `nested` array instead of being separate child documents.
The same data is modeled two ways so you can compare them side by side.

**Why this matters:** Nested objects are stored alongside their parent in one
Lucene document, so queries are faster and no routing is needed. The price is
that updating a single comment means re-indexing the entire post, and you
cannot query a comment fully independently of its post. This is the central
design trade-off: parent-child favors independent updates, nested favors read
speed. Choose based on how your data actually changes and is queried.

## Part 5: Real-World Scenarios

These scenarios put the whole toolkit together on data that looks like a real
application. Notice how each question maps onto a specific join query or
aggregation from the earlier parts.

### Exercise 5.1: E-commerce Product Reviews

See [`14_ecommerce_product_reviews.py`](./14_ecommerce_product_reviews.py)

**Task:** Create queries to find:

1. Products with more than 10 reviews
1. Products where all reviews are verified purchases
1. The top-rated products in each category

**Why this matters:** Counting reviews per product and averaging ratings calls
for the `children` aggregation from Exercise 2.4. "All reviews verified" is
subtle: `has_child` finds products with *at least one* matching review, so
expressing "all" usually means combining it with the absence of any unverified
review rather than a single positive match. Thinking through that gap is the
real lesson here.

### Exercise 5.2: Company Organization Structure

See [`15_company_org_hierarchy.py`](./15_company_org_hierarchy.py)

**Task:** Implement a complete company hierarchy with:

1. Company -> Departments -> Employees
1. Queries to find departments over budget
1. Aggregations for salary statistics by department

**Why this matters:** This is another three-level tree, so the routing rule
from Exercise 1.4 applies: every employee and department must route to the
company id at the root. Salary statistics by department combine the `children`
aggregation with a `stats` metric, showing how aggregations compose across the
relationship.

## Best Practices and Considerations

### When to Use Parent-Child

1. **One-to-many relationships** where children are frequently updated
   independently
1. **Large child sets** that would make nested documents too large
1. **Need to query children independently** from parents
1. **Different update frequencies** between parent and child

### When NOT to Use Parent-Child

1. **Small datasets** - Overhead not worth it
1. **Rarely queried relationships** - Denormalization might be better
1. **Need high query performance** - Parent-child queries are slower
1. **Simple aggregations** - Nested might be sufficient

### Performance Tips

```python
performance_tips = """
1. Always use routing for child documents
2. Keep parent-child hierarchies shallow (max 2-3 levels)
3. Use eager_global_ordinals for frequently queried join fields
4. Consider denormalization for read-heavy workloads
5. Monitor memory usage - join fields use global ordinals
6. Use has_child/has_parent queries sparingly
7. Prefer parent_id queries when possible
"""
print(performance_tips)
```

## Challenges

### Challenge 1: Multi-tenant Blog System

Design and implement a multi-tenant blog system where:

- Each tenant has multiple blogs
- Each blog has multiple posts
- Each post has comments and ratings
- Comments can have nested replies

### Challenge 2: Product Catalog with Variants

Create a product catalog where:

- Products have multiple variants (size, color)
- Each variant has its own inventory
- Products have reviews
- Calculate aggregate ratings considering all reviews

### Challenge 3: Migration Strategy

Write a script to migrate from a parent-child structure to a denormalized
structure and compare:

- Index size
- Query performance
- Update performance
- Memory usage

## Summary Questions

1. When should you use parent-child vs nested documents?
1. Why is routing required for child documents?
1. What are the performance implications of parent-child relationships?
1. How do inner_hits work and when should you use them?
1. What are the limitations of parent-child relationships in Elasticsearch?
