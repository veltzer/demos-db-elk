#!/bin/bash -eu
sudo tee /etc/systemd/system/elasticsearch-archive.service > /dev/null << 'EOF'
[Unit]
Description=Elasticsearch (Archive Installation)
Documentation=https://www.elastic.co
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
ExecStart=/opt/elastic/elasticsearch/bin/elasticsearch
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
