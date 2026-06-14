#!/bin/bash -eu
# Remote reindex: pull data from ANOTHER Elasticsearch cluster.
#
# This is the workhorse of a cross-cluster migration or a major-version
# upgrade where you stand up a brand-new cluster and copy data into it
# rather than upgrading in place. The destination cluster runs the reindex
# and reaches out over HTTP to the remote SOURCE cluster.
#
# IMPORTANT PREREQUISITE: the source host must be whitelisted on EVERY node
# of the DESTINATION cluster, in elasticsearch.yml:
#
#     reindex.remote.whitelist: "oldcluster.example.com:9200, 10.0.0.5:9200"
#
# This setting is NOT dynamic - it requires an elasticsearch.yml edit and a
# node restart. Without it, a remote reindex is rejected for security.
#
# Other notes a DBA must know:
#   - "username"/"password" authenticate to the remote cluster (omit if the
#     remote has security disabled, as our localhost demo does).
#   - The remote major version must be no more than one behind the local
#     one (e.g. reindex from 7.x into 8.x is supported).
#   - "socket_timeout" / "connect_timeout" guard against slow remotes.
#   - Slicing is supported but manual remote slices can be needed for big
#     copies; "size" controls the scroll batch pulled from the remote.
#
# Because this single-node demo has no second cluster, the command below is
# written against a placeholder remote host and is EXPECTED to fail with a
# connection / whitelist error. Read it as the template you would run during
# a real migration. Swap REMOTE_HOST for your old cluster's address.
REMOTE_HOST="http://oldcluster.example.com:9200"

echo "=== remote reindex template (will fail without a real remote) ==="
echo "remote host: $REMOTE_HOST"
echo "ensure reindex.remote.whitelist includes it on every dest node!"
echo

curl -X POST "localhost:9200/_reindex?pretty&wait_for_completion=false" \
	-H 'Content-Type: application/json' -d"
{
	\"source\": {
		\"remote\": {
			\"host\": \"${REMOTE_HOST}\",
			\"socket_timeout\": \"1m\",
			\"connect_timeout\": \"30s\"
		},
		\"index\": \"products_v1\",
		\"size\": 1000,
		\"query\": {
			\"match_all\": {}
		}
	},
	\"dest\": {
		\"index\": \"products_from_remote\"
	}
}" || true

echo
echo "(during a real migration run this from the NEW cluster, pointing"
echo " source.remote.host at the OLD cluster, then track the task id.)"
