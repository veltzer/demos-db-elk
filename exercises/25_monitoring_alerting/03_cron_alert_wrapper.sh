#!/bin/bash -eu
# Cron-friendly wrapper around the threshold check.
#
# This script runs 02_threshold_check.py, captures its output and exit
# code, and routes an alert when the check is not OK. It is designed to be
# called from cron, where the convention is: stay silent on success, shout
# on failure.
#
# ---------------------------------------------------------------------------
# Running from cron
# ---------------------------------------------------------------------------
# Edit your crontab with `crontab -e` and add a line like this to run the
# check every 5 minutes (adjust the absolute path to this directory):
#
#   */5 * * * * /home/mark/git/veltzer/demos-db-elk/exercises/25_monitoring_alerting/03_cron_alert_wrapper.sh
#
# cron sends any stdout/stderr from a job to the local mail spool of the
# crontab owner, so even without the explicit alerting below you would get
# mailed the output. We make alerting explicit and configurable instead.
# ---------------------------------------------------------------------------

# Directory this script lives in, so it works regardless of cron's CWD.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK="${DIR}/02_threshold_check.py"

# Where to send alerts. Override via the environment from your crontab.
ALERT_EMAIL="${ALERT_EMAIL:-dba@example.com}"
# Optional Slack/PagerDuty/Teams incoming-webhook URL. Empty = disabled.
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"

# Run the check. `set -e` is on, so disable it for this one command since a
# non-zero exit (WARN/CRITICAL) is expected and meaningful, not an error.
set +e
OUTPUT="$("${CHECK}")"
RC=$?
set -e

# RC: 0 = OK, 1 = WARN, 2 = CRITICAL. Stay quiet when everything is OK.
if [ "${RC}" -eq 0 ]; then
	exit 0
fi

SUBJECT="Elasticsearch monitoring: exit ${RC}"

# --- Alert via email (requires a working `mail`/`mailx` MTA) ---------------
if command -v mail >/dev/null 2>&1; then
	printf '%s\n' "${OUTPUT}" | mail -s "${SUBJECT}" "${ALERT_EMAIL}"
fi

# --- Alert via webhook (Slack-style JSON payload) --------------------------
if [ -n "${ALERT_WEBHOOK}" ]; then
	# Escape newlines for JSON; keep the payload minimal and portable.
	PAYLOAD=$(printf '%s' "${OUTPUT}" | sed ':a;N;$!ba;s/\n/\\n/g')
	curl -s -X POST -H 'Content-Type: application/json' \
		-d "{\"text\": \"${SUBJECT}\n${PAYLOAD}\"}" \
		"${ALERT_WEBHOOK}" >/dev/null
fi

# Also print to stdout so cron mails it to the crontab owner as a backstop.
printf '%s\n' "${OUTPUT}"

# Propagate the check's exit code so cron / a parent process can react.
exit "${RC}"
