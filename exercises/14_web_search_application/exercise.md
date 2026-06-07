# Elasticsearch Web Search Application Exercise

This exercise builds a small but complete web application — a notes/search app —
on top of Elasticsearch. It shows how full-text search, multi-field matching and
pagination come together behind a real (if minimal) user interface.

## Overview

A "note" has two fields: a `title` and a `text` body. The app lets a user search
across both fields at once and pages through the matches. The sample data is a
small movie catalogue (`movies.csv`); each movie's title and overview are loaded
as a note so there is something interesting to search.

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

The original design goal for this app:

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
[`00_install`](../00_install/exercise.md) exercise if you have not set it up yet.

## Quick Start

### Step 1: Load the Data

```bash
./bootstrap.py
```

This connects to Elasticsearch, creates the `notes` index if needed, clears any
existing data and loads the movies as notes. It is safe to re-run.

### Step 2: Run the Web App

```bash
./notes.py
```

Then open [http://localhost:8080](http://localhost:8080) in a browser. From the
home page follow the **Search** link, enter a term (try "love" or "war") and
page through the results.

### Step 3: Inspect the Index (optional)

```bash
./show.py
```

## How the Search Works

The results route issues a `multi_match` query so a single search box covers
both fields:

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

Pagination is implemented with the `from` (offset) and `size` parameters:
`from = (page - 1) * page_size`. The results page reports the slice and total so
the user always knows where they are.

## Exercises

1. Add an **Add note** page that indexes a new note from a web form.
1. Boost the `title` field so title matches rank above body matches
   (hint: `"fields": ["title^3", "text"]`).
1. Add result highlighting so the matched terms are shown in bold.
1. Replace `from`/`size` pagination with `search_after` and discuss why it
   scales better for deep pages.
