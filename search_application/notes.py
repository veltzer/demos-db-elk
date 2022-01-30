#!/usr/bin/python3

from flask import Flask
from constants import app_name, listening_address, listening_port, index, host, port, pagination_size
from elasticsearch7 import Elasticsearch
from flask import request
import json
import pyvardump

app = Flask(app_name)

form="""
<html>
    <body>
        <h1>Welcome to our notes application</h1>
        <h2>Currently we have {count} notes in the system</h2>
        <a href="/search">Search</a>
        <a href="/add">Add</a>
        <a href="/delete">Delete</a>
        <a href="/edit">Edit</a>
    </body>
</html>
"""

search_form="""
<html>
    <body>
        <h1>Welcome to search</h1>
        <form action="/results" method="get">
            <label for="text">text</label>
            <input type="text" id="text" name="text"></input><br><br>
            <input type="submit" value="Search">
        </form>
        <a href="/">back</a>
    </body>
</html>
"""

@app.route("/")
def all():
    es=Elasticsearch([{'host':host, 'port': port}])
    es.indices.refresh(index)
    res = es.cat.count(index, params={"format": "json"})
    count = res[0]["count"]
    return form.format(count=count)

@app.route("/search")
def search():
    return search_form

@app.route("/results")
def results():
    text = request.args.get("text")
    es=Elasticsearch([{'host':host, 'port': port}])
    # now we need to search the es for {text} both in the {text} and the {title}
    # fields
    doc = {
        'size' : pagination_size,
        'query': {
            "multi_match" : {
                "query": text, 
                "fields": [ "text", "title" ] 
            }
        }
    }
    html = "<html><body>"
    html+="<br></br>"
    res=es.search(index=index, body=doc)
    number_of_results = res['hits']['total']['value']
    hits = res['hits']['hits']
    html += "there are {number_of_results} results...".format(number_of_results=number_of_results)
    html+="<br></br>"
    html+"<ul>"
    for hit in hits:
        # pyvardump.dump_print(hit)
        f_text=hit['_source']['text']
        f_title=hit['_source']['title']
        html+="<li>{f_title}: {f_text}</li>".format(f_text=f_text, f_title=f_title)
        # html+=json.dumps(hit['_source'], indent=4, sort_keys=True)
        html+="<br></br>"
    html+"</ul>"
    html += "</body></html>"
    return html

app.run(port=listening_port, host=listening_address, debug=True)
