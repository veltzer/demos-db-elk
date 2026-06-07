#!/bin/bash
# Enable and start Elasticsearch
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# Check status
sudo systemctl status elasticsearch
