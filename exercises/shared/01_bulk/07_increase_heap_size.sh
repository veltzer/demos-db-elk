#!/bin/bash -eu
# Increase the JVM heap by adding these lines to /etc/elasticsearch/jvm.options
sudo tee -a /etc/elasticsearch/jvm.options <<'OPTS'
-Xms4g
-Xmx4g
OPTS
