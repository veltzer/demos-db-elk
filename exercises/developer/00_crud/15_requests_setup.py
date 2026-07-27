#!/usr/bin/env python
"""
Elasticsearch CRUD operations using requests library
"""

import json

# The next two imports are unused here on purpose: they keep this snippet
# identical to the sibling snippets that do use them.
from datetime import datetime  # noqa: F401  # pylint: disable=unused-import
from typing import Dict, Optional  # noqa: F401  # pylint: disable=unused-import

import requests

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
