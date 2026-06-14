#!/bin/bash -eu
# Elasticsearch & Kibana installation from the direct-download archives.
#
# This script bundles every step of the archive method as a function. These
# exercises run with security DISABLED, so no password is generated and no
# credentials are needed to connect.
#
# Usage:
#   ./archive_install.sh install     # Java + download + configure + start
#   ./archive_install.sh services    # create + enable systemd services
#   ./archive_install.sh verify      # check the running install
#   ./archive_install.sh uninstall   # stop, remove services and all data

ES_VERSION=9.1.3
INSTALL_DIR=/opt/elastic

install_java() {
	# Install OpenJDK 17
	sudo apt install -y openjdk-17-jdk
	java -version
}

download_elasticsearch() {
	# Create directory for the Elastic stack
	sudo mkdir -p "$INSTALL_DIR"
	cd "$INSTALL_DIR"

	# Download and extract Elasticsearch
	sudo wget "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-${ES_VERSION}-linux-x86_64.tar.gz"
	sudo tar -xzf "elasticsearch-${ES_VERSION}-linux-x86_64.tar.gz"

	# Symbolic link for easier access, plus ownership
	sudo ln -sfn "elasticsearch-${ES_VERSION}" elasticsearch
	sudo chown -R "$USER:$USER" "$INSTALL_DIR/elasticsearch-${ES_VERSION}"
}

configure_elasticsearch() {
	# Append exercise configuration (security is DISABLED for these exercises).
	tee -a "$INSTALL_DIR/elasticsearch/config/elasticsearch.yml" > /dev/null << 'EOF'
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false
EOF
	# JVM heap size can be tuned in config/jvm.options (-Xms / -Xmx).
}

start_elasticsearch() {
	# Start Elasticsearch in the background. With security disabled, no password
	# is generated and no credentials are needed to connect.
	"$INSTALL_DIR/elasticsearch/bin/elasticsearch" -d -p /tmp/elasticsearch.pid
}

download_kibana() {
	cd "$INSTALL_DIR"

	# Download and extract Kibana
	sudo wget "https://artifacts.elastic.co/downloads/kibana/kibana-${ES_VERSION}-linux-x86_64.tar.gz"
	sudo tar -xzf "kibana-${ES_VERSION}-linux-x86_64.tar.gz"

	# Symbolic link plus ownership
	sudo ln -sfn "kibana-${ES_VERSION}" kibana
	sudo chown -R "$USER:$USER" "$INSTALL_DIR/kibana-${ES_VERSION}"
}

configure_kibana() {
	# With Elasticsearch security disabled, no enrollment token is required.
	tee -a "$INSTALL_DIR/kibana/config/kibana.yml" > /dev/null << 'EOF'
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://localhost:9200"]
EOF
}

start_kibana() {
	# Start Kibana in the background and save its PID
	nohup "$INSTALL_DIR/kibana/bin/kibana" > /tmp/kibana.log 2>&1 &
	echo $! > /tmp/kibana.pid
}

services() {
	# Create systemd services (optional but recommended). Run as the current
	# user so the units own the files extracted above.
	sudo tee /etc/systemd/system/elasticsearch-archive.service > /dev/null << EOF
[Unit]
Description=Elasticsearch (Archive Installation)
Documentation=https://www.elastic.co
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
ExecStart=$INSTALL_DIR/elasticsearch/bin/elasticsearch
ExecStop=/bin/kill -TERM \$MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

	sudo tee /etc/systemd/system/kibana-archive.service > /dev/null << EOF
[Unit]
Description=Kibana (Archive Installation)
Documentation=https://www.elastic.co
Wants=network-online.target
After=network-online.target elasticsearch-archive.service

[Service]
Type=simple
User=$USER
Group=$USER
ExecStart=$INSTALL_DIR/kibana/bin/kibana
ExecStop=/bin/kill -TERM \$MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

	sudo systemctl daemon-reload
	sudo systemctl enable elasticsearch-archive
	sudo systemctl enable kibana-archive
}

verify() {
	# Check if processes are running (|| true so a no-match grep doesn't abort under -e)
	ps aux | grep elasticsearch || true
	ps aux | grep kibana || true

	# Test Elasticsearch (security disabled: plain HTTP, no credentials)
	curl -X GET "http://localhost:9200"

	# Access Kibana (security disabled: no login required)
	echo "Open browser: http://localhost:5601"
}

uninstall() {
	# Stop background processes if present
	if [ -f /tmp/elasticsearch.pid ]; then
		kill "$(cat /tmp/elasticsearch.pid)" || true
	fi
	if [ -f /tmp/kibana.pid ]; then
		kill "$(cat /tmp/kibana.pid)" || true
	fi

	# Stop and remove systemd services if they were created
	sudo systemctl stop elasticsearch-archive || true
	sudo systemctl stop kibana-archive || true
	sudo systemctl disable elasticsearch-archive || true
	sudo systemctl disable kibana-archive || true
	sudo rm -f /etc/systemd/system/elasticsearch-archive.service
	sudo rm -f /etc/systemd/system/kibana-archive.service

	# Remove installation directory (WARNING: This deletes all data!)
	sudo rm -rf "$INSTALL_DIR"

	# Remove PID files
	rm -f /tmp/elasticsearch.pid /tmp/kibana.pid
}

install() {
	install_java
	download_elasticsearch
	configure_elasticsearch
	start_elasticsearch
	download_kibana
	configure_kibana
	start_kibana
	verify
}

usage() {
	cat << 'EOF'
Usage: ./archive_install.sh [command]

Commands:
  install     Java, download, configure and start both (default)
  services    create and enable systemd services (optional)
  verify      check the running install
  uninstall   stop processes/services, remove install dir and all data
  help        show this help
EOF
}

case "${1:-install}" in
	install) install ;;
	services) services ;;
	verify) verify ;;
	uninstall) uninstall ;;
	help | -h | --help) usage ;;
	*) echo "Unknown command: $1" >&2; usage >&2; exit 1 ;;
esac
