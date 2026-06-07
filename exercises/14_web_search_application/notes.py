#!/usr/bin/env python
"""A minimal Flask web search application backed by Elasticsearch.

Routes:

- ``/``        home page, shows how many notes are in the system
- ``/search``  a search form
- ``/results`` paginated search results (multi_match over title + text)

Start it with ``./notes.py`` and open http://localhost:8080 in a browser.
"""

from elasticsearch import Elasticsearch
from flask import Flask, request

from constants import (
    APP_NAME,
    ES_URL,
    INDEX,
    LISTENING_ADDRESS,
    LISTENING_PORT,
    PAGINATION_SIZE,
)

app = Flask(APP_NAME)
es = Elasticsearch(ES_URL)

HOME_PAGE = """
<html>
  <body>
    <h1>Welcome to our notes application</h1>
    <h2>Currently we have {count} notes in the system</h2>
    <a href="/search">Search</a>
  </body>
</html>
"""

SEARCH_PAGE = """
<html>
  <body>
    <h1>Search</h1>
    <form action="/results" method="get">
      <label for="text">Search text</label>
      <input type="text" id="text" name="text"></input><br><br>
      <input type="submit" value="Search">
    </form>
    <a href="/">back</a>
  </body>
</html>
"""


@app.route("/")
def home() -> str:
    es.indices.refresh(index=INDEX)
    result = es.count(index=INDEX)
    return HOME_PAGE.format(count=result["count"])


@app.route("/search")
def search() -> str:
    return SEARCH_PAGE


@app.route("/results")
def results() -> str:
    text = request.args.get("text", "")
    page = max(int(request.args.get("page", "1")), 1)
    offset = (page - 1) * PAGINATION_SIZE

    response = es.search(
        index=INDEX,
        from_=offset,
        size=PAGINATION_SIZE,
        query={
            "multi_match": {
                "query": text,
                "fields": ["text", "title"],
            }
        },
    )

    total = response["hits"]["total"]["value"]
    hits = response["hits"]["hits"]
    first = offset + 1 if hits else 0
    last = offset + len(hits)

    parts = ["<html><body>", f"<h1>Results for '{text}'</h1>"]
    parts.append(f"<p>showing {first}-{last} of {total} results</p>")
    parts.append("<ul>")
    for hit in hits:
        source = hit["_source"]
        parts.append(f"<li><b>{source['title']}</b>: {source['text']}</li>")
    parts.append("</ul>")

    if page > 1:
        parts.append(f'<a href="/results?text={text}&page={page - 1}">prev</a> ')
    if last < total:
        parts.append(f'<a href="/results?text={text}&page={page + 1}">next</a>')
    parts.append('<br><br><a href="/search">back</a>')
    parts.append("</body></html>")
    return "".join(parts)


if __name__ == "__main__":
    app.run(host=LISTENING_ADDRESS, port=LISTENING_PORT, debug=True)
