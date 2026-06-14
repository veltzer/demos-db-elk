#!/bin/bash -eu
# Inspect Elastic Stack's built-in monitoring features (READ-ONLY).
#
# Elasticsearch ships its own monitoring subsystem. This script queries the
# endpoints that tell you what is available and whether self-monitoring /
# Watcher are enabled on your license. It only reads; it changes nothing.

echo "=== Which X-Pack features are available on this license? ==="
# _xpack/usage shows feature usage; _xpack tells you what is enabled.
curl -s "localhost:9200/_xpack?pretty" || true

echo
echo "=== Feature usage (monitoring, watcher, ...) ==="
# On a Basic license some sections will show enabled:false / available:false.
curl -s "localhost:9200/_xpack/usage?pretty" || true

echo
echo "=== Current license ==="
curl -s "localhost:9200/_license?pretty" || true

cat <<'NOTES'

------------------------------------------------------------------------
Built-in monitoring: the production options
------------------------------------------------------------------------
1. Metricbeat (RECOMMENDED). Run Metricbeat with the elasticsearch and
   kibana modules pointed at your cluster; it ships metrics to a separate
   monitoring cluster and powers Kibana's Stack Monitoring UI
   (Kibana -> Stack Monitoring). This is the supported path on all
   licenses and keeps monitoring load off the production cluster.

2. Legacy "self" / internal collection via the cluster setting
   xpack.monitoring.collection.enabled: true. Deprecated in favor of
   Metricbeat but still seen in the wild. It writes .monitoring-* indices.

3. Kibana Alerting + Stack Monitoring rules. Modern, license-gated
   alerting built into Kibana (Stack Management -> Rules). Out-of-the-box
   rules cover CPU, memory/heap, disk usage, cluster health, license
   expiry, and more. This is the recommended successor to raw Watcher for
   most teams because the rules are configured in the UI.

4. Watcher (see 07_watcher_example.sh). The low-level, JSON-defined,
   push-based alerting engine. Powerful but requires a non-Basic license.

For this course (free Basic license, single node) the practical approach is
the PULL-based check in this exercise: 02_threshold_check.py run from cron
(03_cron_alert_wrapper.sh), plus the self-monitoring index (05_index_metrics.py)
charted in Kibana. The built-in options above are what you graduate to in
a licensed production deployment.
------------------------------------------------------------------------
NOTES
