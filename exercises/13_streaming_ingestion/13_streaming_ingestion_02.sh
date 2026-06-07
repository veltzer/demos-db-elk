#!/bin/bash -eu
# Drop the "wpt" index entirely (mapping and all documents).
curl -X DELETE "localhost:9200/wpt?pretty"
