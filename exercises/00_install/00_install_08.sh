#!/bin/bash
# Stop services
sudo systemctl stop kibana
sudo systemctl stop elasticsearch

# Disable services
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
sudo rm /etc/apt/sources.list.d/elastic-9.x.list
sudo rm /usr/share/keyrings/elasticsearch-keyring.gpg
sudo apt update
