#!/bin/bash -eu
sudo sysctl -w "vm.max_map_count=262144"
docker run --network host --detach "sebp/elk"
