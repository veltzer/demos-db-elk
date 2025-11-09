#!/bin/env python

from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Model a company organization structure
if es.indices.exists(index="organization"):
    es.indices.delete(index="organization")

org_mapping = {
    "mappings": {
        "properties": {
            "join_field": {
                "type": "join",
                "relations": {
                    "company": "department",
                    "department": "employee"
                }
            },
            "name": {"type": "text"},
            "type": {"type": "keyword"},
            "budget": {"type": "float"},
            "employee_count": {"type": "integer"},
            "position": {"type": "keyword"},
            "salary": {"type": "float"},
            "hire_date": {"type": "date"}
        }
    }
}

es.indices.create(index="organization", body=org_mapping)
print("Organization structure mapping created")
# Task: Create the index and model a company hierarchy
# Implement indexing for companies, departments, and employees
