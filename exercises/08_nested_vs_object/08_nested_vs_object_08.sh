#!/bin/bash
# Clean up any existing indices
curl -X DELETE "localhost:9200/students_object?pretty"
curl -X DELETE "localhost:9200/students_nested?pretty"

# Run all the commands above in order, then compare the search results!
