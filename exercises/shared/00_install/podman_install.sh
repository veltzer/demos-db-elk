#!/bin/bash -eu
# Elasticsearch & Kibana installation via Podman.
#
# Podman is a daemonless, rootless-capable container engine compatible with the
# same docker-compose.yml used in the Docker method; it reads the file through
# its compose provider. These exercises run with security DISABLED.
#
# Usage:
#   ./podman_install.sh install     # install Podman, write compose file, start
#   ./podman_install.sh verify      # check the running install
#   ./podman_install.sh uninstall   # stop, remove containers, volumes, images

PROJECT_DIR=~/elastic-podman

install_podman() {
	# Install Podman (Debian/Ubuntu)
	sudo apt update
	sudo apt install -y podman

	# Verify Podman and the compose provider are available
	podman --version
	podman compose version
}

create_compose_file() {
	# Create and enter project directory
	mkdir -p "$PROJECT_DIR" && cd "$PROJECT_DIR"

	# Same compose file as the Docker method; Podman reads it via its provider.
	cat > docker-compose.yml << 'EOF'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:9.1.3
    container_name: elasticsearch
    environment:
      - node.name=elasticsearch
      - cluster.name=docker-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      # Disable security features
      - xpack.security.enabled=false
      - xpack.security.enrollment.enabled=false
      - xpack.security.http.ssl.enabled=false
      - xpack.security.transport.ssl.enabled=false
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    network_mode: host

  kibana:
    image: docker.elastic.co/kibana/kibana:9.1.3
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://localhost:9200
      - ELASTICSEARCH_URL=http://localhost:9200
      # Disable security for Kibana as well
      - xpack.security.enabled=false
      - xpack.encryptedSavedObjects.encryptionKey=fhjskloppd678ehkdfdlliverpoolfcr
    network_mode: host

volumes:
  elasticsearch-data:
    driver: local
EOF
}

compose_up() {
	cd "$PROJECT_DIR"
	# Start in detached mode
	podman compose up -d
	# Show container status
	podman compose ps
}

verify() {
	cd "$PROJECT_DIR"
	# Test Elasticsearch (security disabled: plain HTTP, no credentials)
	curl -X GET "http://localhost:9200"

	# Check container status
	podman compose ps

	# Access Kibana (security disabled: no login required)
	echo "Open browser: http://localhost:5601"
}

uninstall() {
	cd "$PROJECT_DIR"

	# Stop and remove containers and volumes (WARNING: This deletes all data!)
	podman compose down -v

	# Remove images (optional)
	podman rmi docker.elastic.co/elasticsearch/elasticsearch:9.1.3 || true
	podman rmi docker.elastic.co/kibana/kibana:9.1.3 || true

	# Remove project directory
	cd ~ && rm -rf "$PROJECT_DIR"
}

install() {
	install_podman
	create_compose_file
	compose_up
	verify
}

usage() {
	cat << 'EOF'
Usage: ./podman_install.sh [command]

Commands:
  install     install Podman, write compose file, start services (default)
  verify      check the running install
  uninstall   stop, remove containers, volumes and images
  help        show this help
EOF
}

case "${1:-install}" in
	install) install ;;
	verify) verify ;;
	uninstall) uninstall ;;
	help | -h | --help) usage ;;
	*) echo "Unknown command: $1" >&2; usage >&2; exit 1 ;;
esac
