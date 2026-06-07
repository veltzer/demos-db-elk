#!/bin/bash
cd /opt/elastic

# Download Kibana
sudo wget https://artifacts.elastic.co/downloads/kibana/kibana-9.1.3-linux-x86_64.tar.gz

# Extract archive
sudo tar -xzf kibana-9.1.3-linux-x86_64.tar.gz

# Create symbolic link
sudo ln -s kibana-9.1.3 kibana

# Set ownership
sudo chown -R $USER:$USER /opt/elastic/kibana-9.1.3
