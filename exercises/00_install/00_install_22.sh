#!/bin/bash
# Generate enrollment token for Kibana
/opt/elastic/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana

# Configure Kibana with the token
/opt/elastic/kibana/bin/kibana-setup --enrollment-token <your-token>

# Or manually edit configuration
nano /opt/elastic/kibana/config/kibana.yml
# Set: server.host: "0.0.0.0"
