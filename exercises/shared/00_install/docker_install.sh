#!/bin/bash -eu
# Elasticsearch & Kibana installation via Docker Compose.
#
# This script bundles every step of the Docker method as a function. These
# exercises run with security DISABLED, so there is no kibana_system password
# to generate and no enrollment token to configure.
#
# Usage:
#   ./docker_install.sh install     # install Docker, write compose file, start
#   ./docker_install.sh verify      # check the running install
#   ./docker_install.sh uninstall   # stop, remove containers, volumes, images

PROJECT_DIR=~/elastic-docker

uninstall_previous_docker() {
	# Remove Docker CE / Docker Desktop if present. These exercises use the
	# distro's docker.io package, not Docker CE or Docker Desktop.
	if command -v docker-desktop >/dev/null 2>&1; then
		sudo apt-get remove -y docker-desktop || true
	fi
	sudo apt-get remove -y \
		docker-ce docker-ce-cli docker-ce-rootless-extras \
		containerd.io docker-buildx-plugin docker-compose-plugin || true
	# Drop the Docker CE apt repository and key so docker.io is used instead.
	sudo rm -f /etc/apt/sources.list.d/docker.list /etc/apt/keyrings/docker.asc \
		/etc/apt/keyrings/docker.gpg /usr/share/keyrings/docker-archive-keyring.gpg
	rm -rf "$HOME/.docker/desktop"
}

install_docker() {
	# Install the root-installed docker.io package from the distro repos.
	sudo apt-get update
	sudo apt-get install -y docker.io docker-compose-v2

	# Ensure the system (root) Docker daemon is running and enabled.
	sudo systemctl enable --now docker

	# Add user to docker group
	sudo usermod -aG docker "$USER"
	newgrp docker

	# Verify Docker Compose is installed
	docker compose version
}

create_compose_file() {
	# Create and enter project directory
	mkdir -p "$PROJECT_DIR" && cd "$PROJECT_DIR"

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
	docker compose up -d
	# Show container status
	docker compose ps
}

verify() {
	cd "$PROJECT_DIR"
	# Test Elasticsearch (security disabled: plain HTTP, no credentials)
	curl -X GET "http://localhost:9200"

	# Check container status
	docker compose ps

	# Access Kibana (security disabled: no login required)
	echo "Open browser: http://localhost:5601"
}

uninstall() {
	cd "$PROJECT_DIR"

	# Stop and remove containers and volumes (WARNING: This deletes all data!)
	docker compose down -v

	# Remove images (optional)
	docker rmi docker.elastic.co/elasticsearch/elasticsearch:9.1.3 || true
	docker rmi docker.elastic.co/kibana/kibana:9.1.3 || true

	# Remove project directory
	cd ~ && rm -rf "$PROJECT_DIR"
}

install() {
	uninstall_previous_docker
	install_docker
	create_compose_file
	compose_up
	verify
}

usage() {
	cat << 'EOF'
Usage: ./docker_install.sh [command]

Commands:
  install     install Docker, write compose file, start services (default)
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
