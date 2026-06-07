#!/bin/bash
# Stop processes
if [ -f /tmp/elasticsearch.pid ]; then
    kill $(cat /tmp/elasticsearch.pid)
fi
if [ -f /tmp/kibana.pid ]; then
    kill $(cat /tmp/kibana.pid)
fi

# Or if using systemd services
sudo systemctl stop elasticsearch-archive
sudo systemctl stop kibana-archive
sudo systemctl disable elasticsearch-archive
sudo systemctl disable kibana-archive
sudo rm /etc/systemd/system/elasticsearch-archive.service
sudo rm /etc/systemd/system/kibana-archive.service

# Remove installation directory (WARNING: This deletes all data!)
sudo rm -rf /opt/elastic

# Remove PID files
rm -f /tmp/elasticsearch.pid /tmp/kibana.pid
