#!/usr/bin/env python
"""Nagios-style threshold check for Elasticsearch.

Runs the metrics collector from 01_metrics_collector.py, evaluates each
metric against a configurable threshold, prints one OK/WARN/CRITICAL line
per check, and exits with a Nagios-compatible code:

    0  OK        all checks passed
    1  WARNING   at least one WARN, no CRITICAL
    2  CRITICAL  at least one CRITICAL

Because the exit code follows the Nagios convention, this script can be
dropped straight into Nagios/Icinga, a cron job, or a CI gate.

Run it:

    ./02_threshold_check.py

Tune the THRESHOLDS dict below for your environment.
"""

import sys

from importlib import import_module

# 01_metrics_collector starts with a digit, so we cannot "import" it with
# normal syntax. import_module handles the numeric module name.
collector = import_module("01_metrics_collector")

# Nagios-style severity levels and their exit codes.
OK = 0
WARN = 1
CRITICAL = 2
LABELS = {OK: "OK", WARN: "WARN", CRITICAL: "CRITICAL"}

# Configurable thresholds. Edit these for your cluster's SLOs.
THRESHOLDS = {
    "heap_used_percent_max": {"warn": 75.0, "crit": 85.0},
    "disk_used_percent_max": {"warn": 80.0, "crit": 85.0},
}


def check_status(metrics):
    """Cluster status: green=OK, yellow=WARN, red=CRITICAL."""
    status = metrics["status"]
    if status == "green":
        return OK, "cluster status is green"
    if status == "yellow":
        return WARN, "cluster status is YELLOW (replicas unassigned)"
    return CRITICAL, "cluster status is RED (primary shards missing)"


def check_unassigned_shards(metrics):
    """Any unassigned shard is at least a warning."""
    n = metrics["unassigned_shards"]
    if n == 0:
        return OK, "no unassigned shards"
    # Red status already flags missing primaries as CRITICAL; here we treat
    # unassigned shards on a non-red cluster as a WARNING (usually replicas).
    level = CRITICAL if metrics["status"] == "red" else WARN
    return level, f"{n} unassigned shard(s)"


def check_thread_pool_rejections(metrics):
    """Thread-pool rejections mean the cluster dropped work."""
    n = metrics["thread_pool_rejections_total"]
    if n == 0:
        return OK, "no thread-pool rejections"
    return WARN, f"{n} thread-pool rejection(s) (queues filling up)"


def check_pending_tasks(metrics):
    """A growing pending-task queue signals a struggling master."""
    n = metrics["pending_tasks"]
    if n == 0:
        return OK, "no pending cluster tasks"
    if n < 10:
        return WARN, f"{n} pending cluster task(s)"
    return CRITICAL, f"{n} pending cluster task(s) (master overloaded?)"


def check_numeric(metrics, key, label):
    """Generic warn/crit check for a percentage-style metric."""
    value = metrics[key]
    limits = THRESHOLDS[key]
    if value >= limits["crit"]:
        return CRITICAL, f"{label} is {value:.1f}% (>= {limits['crit']}%)"
    if value >= limits["warn"]:
        return WARN, f"{label} is {value:.1f}% (>= {limits['warn']}%)"
    return OK, f"{label} is {value:.1f}%"


def main():
    """Evaluate all checks and exit with the worst severity found."""
    metrics = collector.collect_metrics()

    results = [
        check_status(metrics),
        check_unassigned_shards(metrics),
        check_numeric(metrics, "heap_used_percent_max", "max heap used"),
        check_numeric(metrics, "disk_used_percent_max", "max disk used"),
        check_thread_pool_rejections(metrics),
        check_pending_tasks(metrics),
    ]

    worst = OK
    for level, message in results:
        print(f"{LABELS[level]}: {message}")
        worst = max(worst, level)

    print("-" * 50)
    print(f"OVERALL: {LABELS[worst]} (exit {worst})")
    sys.exit(worst)


if __name__ == "__main__":
    main()
