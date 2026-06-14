#!/bin/bash -eu
# Verification and troubleshooting commands shared across all install methods.
# Security is DISABLED for these exercises: plain HTTP, no credentials needed.
#
# Usage:
#   ./check_status.sh elasticsearch   # Elasticsearch health, info and indices
#   ./check_status.sh kibana          # Kibana API status
#   ./check_status.sh troubleshoot    # ports and per-method log locations
#   ./check_status.sh all             # run elasticsearch + kibana (default)

elasticsearch() {
	# Basic health check
	curl -X GET "http://localhost:9200/_cluster/health?pretty"
	# Cluster information
	curl -X GET "http://localhost:9200"
	# List indices
	curl -X GET "http://localhost:9200/_cat/indices?v"
}

kibana() {
	# Check Kibana API status
	curl -X GET "http://localhost:5601/api/status"
	# Or verify in the browser at http://localhost:5601 (or http://<server-ip>:5601)
}

browse() {
	# Open the Kibana UI in the default browser
	xdg-open "http://localhost:5601"
}

troubleshoot() {
	# Check ports are listening
	sudo netstat -tlnp | grep -E '9200|5601' || true

	echo "--- APT method logs:    sudo journalctl -u elasticsearch -f / -u kibana -f"
	echo "--- Docker method logs: docker compose logs elasticsearch / kibana"
	echo "--- Podman method logs: podman compose logs elasticsearch / kibana"
	echo "--- Archive method logs: tail -f /opt/elastic/elasticsearch/logs/*.log / /tmp/kibana.log"
}

all() {
	elasticsearch
	kibana
}

usage() {
	cat << 'EOF'
Usage: ./check_status.sh [command]

Commands:
  elasticsearch   cluster health, info and index listing
  kibana          Kibana API status
  browse          open the Kibana UI in the default browser
  troubleshoot    listening ports and per-method log locations
  all             elasticsearch + kibana (default)
  help            show this help
EOF
}

case "${1:-all}" in
	elasticsearch) elasticsearch ;;
	kibana) kibana ;;
	browse) browse ;;
	troubleshoot) troubleshoot ;;
	all) all ;;
	help | -h | --help) usage ;;
	*) echo "Unknown command: $1" >&2; usage >&2; exit 1 ;;
esac
