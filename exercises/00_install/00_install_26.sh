#!/bin/bash -eu
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch-archive
sudo systemctl enable kibana-archive
