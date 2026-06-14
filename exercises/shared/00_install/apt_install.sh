#!/bin/bash -eu
# Elasticsearch & Kibana installation via the APT package manager.
#
# This script bundles every step of the APT method as a function so you can
# read it top to bottom and run the phase you need. These exercises run with
# security DISABLED, so no generated passwords or enrollment tokens are needed.
#
# Usage:
#   ./apt_install.sh install     # install + configure + start everything
#   ./apt_install.sh verify      # check the running install
#   ./apt_install.sh uninstall   # stop, remove packages and all data

install_dependencies() {
	# Install required packages
	sudo apt install -y wget apt-transport-https ca-certificates gnupg
}

add_elasticsearch_repo() {
	# Import the Elasticsearch GPG key
	wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | \
		sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg

	# Add the repository
	echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] \
https://artifacts.elastic.co/packages/9.x/apt stable main" | \
		sudo tee /etc/apt/sources.list.d/elastic-9.x.list

	# Update package list
	sudo apt update
}

install_elasticsearch() {
	# Install Elasticsearch. Security is DISABLED below, so the generated
	# password and enrollment token shown during installation are not needed.
	sudo apt install -y elasticsearch
}

configure_and_start_elasticsearch() {
	# Disable security for these exercises.
	sudo tee -a /etc/elasticsearch/elasticsearch.yml > /dev/null << 'EOF'
xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false
EOF

	# Enable and start Elasticsearch
	sudo systemctl daemon-reload
	sudo systemctl enable elasticsearch
	sudo systemctl start elasticsearch
	sudo systemctl status elasticsearch
}

install_kibana() {
	# Install Kibana. With Elasticsearch security disabled, no enrollment token
	# is required; Kibana connects over plain HTTP with no credentials.
	sudo apt install -y kibana
}

start_kibana() {
	# Enable and start Kibana
	sudo systemctl daemon-reload
	sudo systemctl enable kibana
	sudo systemctl start kibana
	sudo systemctl status kibana
}

verify() {
	# Test Elasticsearch (security disabled: plain HTTP, no credentials)
	curl -X GET "http://localhost:9200"

	# Access Kibana (security disabled: no login required)
	echo "Open browser: http://localhost:5601"
}

uninstall() {
	# Stop and disable services
	sudo systemctl stop kibana
	sudo systemctl stop elasticsearch
	sudo systemctl disable kibana
	sudo systemctl disable elasticsearch

	# Remove packages
	sudo apt remove --purge -y elasticsearch kibana

	# Remove data directories (WARNING: This deletes all data!)
	sudo rm -rf /var/lib/elasticsearch
	sudo rm -rf /var/lib/kibana

	# Remove configuration
	sudo rm -rf /etc/elasticsearch
	sudo rm -rf /etc/kibana

	# Remove repository
	sudo rm -f /etc/apt/sources.list.d/elastic-9.x.list
	sudo rm -f /usr/share/keyrings/elasticsearch-keyring.gpg
	sudo apt update
}

install() {
	install_dependencies
	add_elasticsearch_repo
	install_elasticsearch
	configure_and_start_elasticsearch
	install_kibana
	start_kibana
	verify
}

usage() {
	cat << 'EOF'
Usage: ./apt_install.sh [command]

Commands:
  install     install + configure + start everything (default)
  verify      check the running install
  uninstall   stop, remove packages and all data
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
