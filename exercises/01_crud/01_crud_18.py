#!/usr/bin/env python
# Check existing mappings
es.indices.get_mapping(index=INDEX_NAME)

# Reindex to new index with correct mappings if needed
