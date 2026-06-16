#!/usr/bin/env python
"""Shared configuration for the notes/search web application."""

# Elasticsearch
ES_URL = "http://localhost:9200"
INDEX = "notes"

# Dataset loaded by bootstrap.py
FILENAME = "movies.csv"

# Flask web app
APP_NAME = "notes_app"
LISTENING_ADDRESS = "0.0.0.0"
LISTENING_PORT = 8080

# How many results to show per page
PAGINATION_SIZE = 10
