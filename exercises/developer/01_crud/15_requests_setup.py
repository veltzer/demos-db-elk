#!/usr/bin/env python
"""
Elasticsearch CRUD operations using requests library
"""

import requests
import json
from datetime import datetime  # noqa: F401  (used by sibling snippets)
from typing import Dict, Optional  # noqa: F401  (used by sibling snippets)

# Configuration
ES_HOST = "localhost"
ES_PORT = 9200
ES_URL = f"http://{ES_HOST}:{ES_PORT}"
INDEX_NAME = "products"

# HTTP session (security disabled: no authentication)
session = requests.Session()
session.headers.update({'Content-Type': 'application/json'})


def pretty_print(response):
    """Pretty print JSON response"""
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print(response.text)
