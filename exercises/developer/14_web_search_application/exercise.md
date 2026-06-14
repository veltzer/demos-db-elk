# Elasticsearch Web Search Application Exercise

This exercise builds a small but complete web application — a notes/search app —
on top of Elasticsearch. It shows how full-text search, multi-field matching and
pagination come together behind a real (if minimal) user interface.

## Overview

A "note" has two fields: a `title` and a `text` body. The app lets a user search
across both fields at once and pages through the matches. The sample data is a
small movie catalogue (`movies.csv`); each movie's title and overview are loaded
as a note so there is something interesting to search.

Why model it this way? This mirrors the classic shape of almost every search
feature you will ever build: a short, important field (a title, a name, a
subject line) and a longer, descriptive field (a body, a description, an
abstract). Once you can search both at once and present the matches in pages,
you have the core of a real search product. Elasticsearch is a good fit here
because it was built for full-text search: it breaks text into terms, ranks
documents by relevance, and returns results in milliseconds, which a plain
relational `LIKE '%term%'` query cannot do well.

The exercise includes:

- Loading a CSV dataset into an Elasticsearch index
- A Flask web app with home, search and results pages
- Full-text `multi_match` search across the `title` and `text` fields
- Pagination of the result set with prev/next navigation

## Files

- `constants.py` - Shared configuration (Elasticsearch URL, index, port, page size)
- `bootstrap.py` - Loads `movies.csv` into the `notes` index (idempotent)
- `notes.py` - The Flask web application
- `show.py` - Utility that dumps every note in the index (for debugging)
- `movies.csv` - Sample dataset
- `requirements.txt` - Python dependencies

## Design Brief

Writing the brief first is a useful habit: it pins down what "done" means before
any code is written, and each bullet below maps directly to a concrete piece of
Elasticsearch behaviour (counting documents, matching across fields, paging the
result set). The original design goal for this app:

- A note is a `title` (short) and a `text` body (longer).
- The web app has a home page (showing the note count), a search page (a single
  text box) and a results page.
- The results page shows the total number of matches and which slice is on
  screen (for example "showing 11-20 of 43 results").
- A search matches against both the title and the text.
- When a search matches more than one page of notes, the results are paginated.

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure Elasticsearch is Running

Elasticsearch should be reachable on `localhost:9200`. See the
[`00_install`](../../shared/00_install/exercise.md) exercise if you have not
set it up yet.

Why this matters: both `bootstrap.py` and `notes.py` talk to the cluster over
HTTP on this address (it is set once in `constants.py` as `ES_URL`). If the
cluster is down, `bootstrap.py` deliberately calls `es.ping()` and fails with a
clear message rather than crashing later in a confusing way. Failing fast with a
readable error is a small but important habit when a service depends on another
service being up.

## Quick Start

### Step 1: Load the Data

```bash
./bootstrap.py
```

This connects to Elasticsearch, creates the `notes` index if needed, clears any
existing data and loads the movies as notes. It is safe to re-run.

What's happening under the hood: an *index* in Elasticsearch is the rough
equivalent of a table in a relational database — a named place where documents
of a similar shape live. Each note becomes a *document*: a small JSON object
with `title` and `text` keys. Notice that `bootstrap.py` never declares a schema
(a *mapping*) for these fields. Elasticsearch supports *dynamic mapping*, so the
first time it sees a string value it infers a sensible type (a `text` type that
is analyzed for full-text search). This is convenient for getting started, but
in production you usually define the mapping explicitly so you control exactly
how each field is analyzed.

The "clears any existing data" step makes the script *idempotent* — running it
ten times leaves you in the same state as running it once. It does this with a
`delete_by_query` over `match_all` rather than deleting and recreating the
index, which keeps any mapping or settings you may have added. After loading,
the script calls `es.indices.refresh(...)`. Refreshing is needed because
Elasticsearch indexes documents into an in-memory buffer first and only makes
them visible to searches when a *refresh* occurs (automatically about once a
second, or on demand). Forcing a refresh here guarantees the documents are
searchable the moment the script finishes.

### Step 2: Run the Web App

```bash
./notes.py
```

Then open [http://localhost:8080](http://localhost:8080) in a browser. From the
home page follow the **Search** link, enter a term (try "love" or "war") and
page through the results.

The home page is worth a glance: it calls `es.count(index=INDEX)` to show how
many notes exist. `count` is cheaper than a full search because Elasticsearch
does not have to fetch, rank or return any document bodies — it only tallies
matching documents. Using the right call for the job (count when you only need a
number, search when you need the documents) keeps the app responsive.

### Step 3: Inspect the Index (optional)

```bash
./show.py
```

This dumps every stored note as JSON. It runs a `match_all` query (which matches
every document) with a large `size` so you can see exactly what `bootstrap.py`
loaded. Being able to look directly at your raw documents is invaluable when a
search returns surprising results: more often than not the data is not shaped
the way you assumed. A word of caution — pulling 10,000 documents at once like
this is fine for a tiny demo index, but it is not how you read large indices in
production. There you would page through results or use a dedicated scrolling
mechanism instead of one huge request.

## How the Search Works

The results route issues a `multi_match` query so a single search box covers
both fields. A plain `match` query searches one field; `multi_match` runs the
same query text against several fields and combines the scores, so one search
box can cover both the `title` and the `text` without the user picking a field.
This is exactly what users expect from a single search bar:

```json
{
  "query": {
    "multi_match": {
      "query": "<user text>",
      "fields": ["text", "title"]
    }
  }
}
```

Behind the scenes the matched text is *analyzed*: Elasticsearch lowercases the
query, splits it into terms, and looks each term up in an *inverted index* (a
map from each term to the list of documents that contain it). That is what makes
full-text search fast and why a search for "Love" finds documents containing
"love". It also ranks the hits by a relevance score, so the best matches come
first rather than in insertion order.

Pagination is implemented with the `from` (offset) and `size` parameters:
`from = (page - 1) * page_size`. The results page reports the slice and total so
the user always knows where they are. `size` is how many hits to return;
`from` is how many leading hits to skip. To show page 3 of 10-item pages you
skip the first 20 and return the next 10.

Common pitfall: `from`/`size` pagination is simple but gets expensive for deep
pages, because the cluster must gather and sort `from + size` hits on every
shard before discarding the ones it skips. Asking for page 10,000 forces it to
sort a huge list just to return ten rows. Elasticsearch enforces a default
`from + size` ceiling of 10,000 for this reason. For small result sets like this
demo it is perfectly fine; the final exercise below explores the alternative.

## Exercises

These extensions each teach a distinct search concept; they are ordered roughly
from easiest to hardest.

1. Add an **Add note** page that indexes a new note from a web form.
1. Boost the `title` field so title matches rank above body matches
   (hint: `"fields": ["title^3", "text"]`). The `^3` multiplies that field's
   contribution to the relevance score, so a hit in the title outweighs the same
   word buried in the body — usually what users want.
1. Add result highlighting so the matched terms are shown in bold.
   Elasticsearch can return a `highlight` section with the matching fragments
   already wrapped in tags, so you do not have to find the terms yourself.
1. Replace `from`/`size` pagination with `search_after` and discuss why it
   scales better for deep pages. Instead of skipping `from` documents,
   `search_after` remembers the sort values of the last hit on the current page
   and asks for documents *after* that point, so the cost does not grow with the
   page number.
