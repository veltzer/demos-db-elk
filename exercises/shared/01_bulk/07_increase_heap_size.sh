#!/bin/bash -eu
# Increase the JVM heap by adding these lines to /etc/elasticsearch/jvm.options
cat <<'OPTS' | sudo tee -a /etc/elasticsearch/jvm.options
-Xms4g
-Xmx4g
OPTS
