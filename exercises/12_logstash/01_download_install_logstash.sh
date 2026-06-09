#!/bin/bash -eu
# Download Logstash (adjust version as needed)
wget https://artifacts.elastic.co/downloads/logstash/logstash-8.11.0-linux-x86_64.tar.gz

# Extract
tar -xzf logstash-8.11.0-linux-x86_64.tar.gz

# Move to a convenient location
sudo mv logstash-8.11.0 /opt/logstash

# Create symlink for easier access
sudo ln -s /opt/logstash/bin/logstash /usr/local/bin/logstash
