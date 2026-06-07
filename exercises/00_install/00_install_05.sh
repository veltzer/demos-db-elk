#!/bin/bash
# Install Kibana
sudo apt install -y kibana

# Configure Kibana (if you have the enrollment token)
sudo /usr/share/kibana/bin/kibana-setup --enrollment-token <your-token>

# Or manually configure by editing:
sudo nano /etc/kibana/kibana.yml
# Set: server.host: "0.0.0.0" for external access
