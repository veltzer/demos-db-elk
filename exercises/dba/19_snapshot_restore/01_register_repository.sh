#!/bin/bash -eu
# Register a filesystem (type "fs") snapshot repository and verify it.
#
# PREREQUISITE: the directory used as "location" must be listed in the
# node setting path.repo, and Elasticsearch must have been restarted after
# setting it. If path.repo is not configured you will get a
# "[location] location [...] doesn't match any of the locations specified
# by path.repo" error. See exercise.md for how to set path.repo for both a
# native (archive/apt) install and a docker-compose deployment.
#
# We use a location of "backups", which is interpreted RELATIVE to the
# first path.repo entry. So if path.repo is ["/tmp/es_snapshots"], the
# snapshots land in /tmp/es_snapshots/backups.

REPO="my_fs_repo"

# Register the repository. compress=true gzip-compresses metadata files
# (not the data blobs, which are already compressed Lucene segments).
echo "=== register repository ${REPO} ==="
curl -s -X PUT "localhost:9200/_snapshot/${REPO}?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"type": "fs",
	"settings": {
		"location": "backups",
		"compress": true
	}
}'

# Read the repository definition back.
echo "=== GET repository definition ==="
curl -s -X GET "localhost:9200/_snapshot/${REPO}?pretty"

# Verify that every node can read and write the repository location.
# This catches the classic mistake of a shared filesystem that is mounted
# on only some nodes. It returns the list of nodes that passed.
echo "=== verify repository ==="
curl -s -X POST "localhost:9200/_snapshot/${REPO}/_verify?pretty"
