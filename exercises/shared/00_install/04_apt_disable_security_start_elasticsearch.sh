#!/bin/bash -eu
# Disable security for these exercises by editing the configuration.
# Append the following to /etc/elasticsearch/elasticsearch.yml:
#   xpack.security.enabled: false
#   xpack.security.enrollment.enabled: false
#   xpack.security.http.ssl.enabled: false
#   xpack.security.transport.ssl.enabled: false
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

# Check status
sudo systemctl status elasticsearch
