#!/bin/bash
sudo tee /etc/systemd/system/kibana-archive.service > /dev/null << 'EOF'
[Unit]
Description=Kibana (Archive Installation)
Documentation=https://www.elastic.co
Wants=network-online.target
After=network-online.target elasticsearch-archive.service

[Service]
Type=simple
User=$USER
Group=$USER
ExecStart=/opt/elastic/kibana/bin/kibana
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
