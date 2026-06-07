# Nested vs Parent-Child Comparison Exercise

## Understanding the Trade-offs

When dealing with one-to-many relationships in Elasticsearch, you have two main
options: **Nested fields** and **Parent-Child relationships**. This exercise
will help you understand when to use each approach by implementing the same
scenario both ways.

**Nested Fields**: Store related data as nested objects within the same document
**Parent-Child**: Store related data as separate documents with join
relationships

---

## Exercise: Blog Posts and Comments (Both Approaches)

Let's implement the same blog and comments scenario using both approaches to see
the differences in practice.

### Step 1: Create Both Index Types

**Nested Index:**
See [`10_parent_child_vs_nested_01.sh`](./10_parent_child_vs_nested_01.sh)

**Parent-Child Index:**
See [`10_parent_child_vs_nested_02.sh`](./10_parent_child_vs_nested_02.sh)

### Step 2: Add Sample Data

**Nested - Everything in One Document:**
See [`10_parent_child_vs_nested_03.sh`](./10_parent_child_vs_nested_03.sh)

**Parent-Child - Separate Documents:**
See [`10_parent_child_vs_nested_04.sh`](./10_parent_child_vs_nested_04.sh)

### Step 3: Compare Query Approaches

#### Test 1: Find posts with comments containing "helpful"

*Nested Query:*
See [`10_parent_child_vs_nested_05.sh`](./10_parent_child_vs_nested_05.sh)

*Parent-Child Query:*
See [`10_parent_child_vs_nested_06.sh`](./10_parent_child_vs_nested_06.sh)

#### Test 2: Find all comments by Alice

*Nested Query:*
See [`10_parent_child_vs_nested_07.sh`](./10_parent_child_vs_nested_07.sh)

*Parent-Child Query:*
See [`10_parent_child_vs_nested_08.sh`](./10_parent_child_vs_nested_08.sh)

### Step 4: Compare Update Scenarios

#### Adding a New Comment

*Nested - Requires Full Document Reindex:*
See [`10_parent_child_vs_nested_09.sh`](./10_parent_child_vs_nested_09.sh)

*Parent-Child - Add Independent Document:*
See [`10_parent_child_vs_nested_10.sh`](./10_parent_child_vs_nested_10.sh)

#### Updating an Existing Comment

*Nested - Must Update Entire Document:*
See [`10_parent_child_vs_nested_11.sh`](./10_parent_child_vs_nested_11.sh)

*Parent-Child - Update Individual Comment:*
See [`10_parent_child_vs_nested_12.sh`](./10_parent_child_vs_nested_12.sh)

### Step 5: Compare Storage and Performance

**Check Document Counts:**
See [`10_parent_child_vs_nested_13.sh`](./10_parent_child_vs_nested_13.sh)

**View Actual Storage:**
See [`10_parent_child_vs_nested_14.sh`](./10_parent_child_vs_nested_14.sh)

**Performance Test - Add Many Comments:**
See [`10_parent_child_vs_nested_15.sh`](./10_parent_child_vs_nested_15.sh)

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
See [`10_parent_child_vs_nested_16.sh`](./10_parent_child_vs_nested_16.sh)

*Parent-Child (simple new documents):*
See [`10_parent_child_vs_nested_17.sh`](./10_parent_child_vs_nested_17.sh)

### Exercise Questions

1. **Scenario**: A news website with articles that receive hundreds of comments
   daily. Which approach would you choose?
2. **Scenario**: A product catalog where each product has 3-5 reviews that are
   rarely updated. Which approach would you choose?
3. **Scenario**: A social media platform where posts can have thousands of
   comments, and comments are frequently edited or deleted. Which approach would
   you choose?

### Clean Up

See [`10_parent_child_vs_nested_18.sh`](./10_parent_child_vs_nested_18.sh)

### Exercise Answers

1. **Parent-Child** - High volume of comment updates favors independent document
   management
2. **Nested** - Stable, low-volume data benefits from faster query performance
3. **Parent-Child** - Frequent edits and deletes make independent documents
   essential
