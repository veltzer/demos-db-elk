#!/bin/bash
# Enable and start Kibana
sudo systemctl daemon-reload
sudo systemctl enable kibana
sudo systemctl start kibana

# Check status
sudo systemctl status kibana
