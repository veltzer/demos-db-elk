#!/bin/bash -eu
# Built-in alerting with Watcher (DEMONSTRATION ONLY).
#
# ---------------------------------------------------------------------------
# IMPORTANT: Watcher requires a commercial (Gold/Platinum/Enterprise) license
# OR a trial license. It is NOT available on the free Basic license that this
# course runs on, so the PUT below will likely return a 403 / "current license
# is non-compliant for [watcher]" on a default install. We present it as a
# reference for what built-in, push-based alerting looks like in production.
#
# To try it for real: start a 30-day trial with
#   curl -X POST "localhost:9200/_license/start_trial?acknowledge=true"
# then run this script. Tear it down later with
#   curl -X POST "localhost:9200/_license/start_basic?acknowledge=true"
# ---------------------------------------------------------------------------
#
# This watch runs every minute. It calls GET /_cluster/health, and if the
# cluster status is RED (or there are unassigned shards), the condition is
# met and the (logging) action fires. In production you would swap the
# "logging" action for "email", "slack", "webhook", or "pagerduty".

curl -X PUT "localhost:9200/_watcher/watch/cluster_health_red?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"trigger": {
		"schedule": { "interval": "1m" }
	},
	"input": {
		"http": {
			"request": {
				"host": "localhost",
				"port": 9200,
				"path": "/_cluster/health"
			}
		}
	},
	"condition": {
		"compare": {
			"ctx.payload.status": { "eq": "red" }
		}
	},
	"actions": {
		"log_alert": {
			"logging": {
				"text": "ALERT: cluster {{ctx.payload.cluster_name}} is RED. Unassigned shards: {{ctx.payload.unassigned_shards}}."
			}
		}
	}
}'

echo
echo "If you have a trial/commercial license, inspect or trigger the watch:"
echo "  curl 'localhost:9200/_watcher/watch/cluster_health_red?pretty'"
echo "  curl -X POST 'localhost:9200/_watcher/watch/cluster_health_red/_execute?pretty'"
echo "Delete it with:"
echo "  curl -X DELETE 'localhost:9200/_watcher/watch/cluster_health_red?pretty'"
echo
echo "On the free Basic license, prefer the pull-based check in"
echo "02_threshold_check.py driven by cron (03_cron_alert_wrapper.sh)."
