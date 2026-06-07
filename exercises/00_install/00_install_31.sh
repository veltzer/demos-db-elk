#!/bin/bash -eu
# Check ports are listening
sudo netstat -tlnp | grep -E '9200|5601'

# Check logs (APT method)
sudo journalctl -u elasticsearch -f
sudo journalctl -u kibana -f

# Check logs (Docker method)
docker compose logs elasticsearch
docker compose logs kibana

# Check logs (Archive method)
tail -f /opt/elastic/elasticsearch/logs/*.log
tail -f /tmp/kibana.log
