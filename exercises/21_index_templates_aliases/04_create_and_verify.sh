#!/bin/bash -eu
# Create an index whose name matches a template pattern, then VERIFY that
# the resolved mapping and settings were inherited from the component and
# index templates - we never specify them on the create call itself.

# Create "logs-app-2024". It matches only "logs-*" (logs-template), so it
# inherits common-settings + logs-mappings + the template overrides.
echo "=== create logs-app-2024 (matches logs-template only) ==="
curl -X PUT "localhost:9200/logs-app-2024?pretty"

# Create "logs-audit-2024". It matches BOTH templates by pattern, but the
# higher-priority audit template wins, so it gets replicas=2 plus the
# audit-specific fields.
echo
echo "=== create logs-audit-2024 (audit template wins on priority) ==="
curl -X PUT "localhost:9200/logs-audit-2024?pretty"

# Verify the resolved configuration of the plain app index. Confirm:
#   - settings.index.number_of_replicas == "1" (from logs-template)
#   - settings.index.refresh_interval == "5s" (from common-settings)
#   - mappings include @timestamp/level/service/message/status_code
#     (logs-mappings) and host (logs-template), but NOT actor/action.
echo
echo "=== GET logs-app-2024 (resolved mapping + settings) ==="
curl -s "localhost:9200/logs-app-2024?pretty"

# Verify the audit index. Confirm:
#   - settings.index.number_of_replicas == "2" (audit template override)
#   - mappings include actor and action in addition to the shared fields.
echo
echo "=== GET logs-audit-2024 (resolved mapping + settings) ==="
curl -s "localhost:9200/logs-audit-2024?pretty"
