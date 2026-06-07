#!/usr/bin/env python
# Force refresh after insert
es.index(index=INDEX_NAME, id="1", document=doc, refresh=True)

# Or refresh the entire index
es.indices.refresh(index=INDEX_NAME)
