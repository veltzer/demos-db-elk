#!/usr/bin/env python
"""Show pending cluster-state tasks and long-running tasks.

Two different things, both important to a DBA:

  GET /_cluster/pending_tasks
    Changes queued against the cluster STATE (mapping updates, shard
    allocation decisions, settings changes) that the master has not yet
    applied. A growing queue means the master node is a bottleneck.

  GET /_tasks
    The live task management API: every running task (search, bulk,
    reindex, snapshot, ...). Long-running tasks here can be cancelled.
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# Flag any running task that has been going longer than this.
LONG_TASK_THRESHOLD_MS = 30_000


def show_pending_tasks() -> None:
    """Print queued cluster-state changes."""
    print("=== pending cluster-state tasks ===")
    result = es.cluster.pending_tasks()
    tasks = result.get("tasks", [])
    if not tasks:
        print("  none - the master is keeping up with cluster-state changes.")
        return
    print(f"{'order':>6} {'prio':>10} {'wait_ms':>9}  source")
    for t in tasks:
        print(
            f"{t.get('insert_order', 0):>6} {t.get('priority', ''):>10} "
            f"{t.get('time_in_queue_millis', 0):>9}  {t.get('source', '')}"
        )


def show_running_tasks() -> None:
    """Print currently running tasks, flagging long-running ones."""
    print("\n=== running tasks (detailed) ===")
    result = es.tasks.list(detailed=True)
    found = False
    long_running = []
    for node_id, node in result.get("nodes", {}).items():
        node_name = node.get("name", node_id)
        for task_id, task in node.get("tasks", {}).items():
            found = True
            running_ms = task.get("running_time_in_nanos", 0) / 1_000_000
            action = task.get("action", "")
            desc = task.get("description", "") or ""
            line = (
                f"  [{node_name}] {action} "
                f"running={running_ms:.0f}ms id={task_id}"
            )
            if desc:
                line += f"\n      {desc[:80]}"
            print(line)
            if running_ms > LONG_TASK_THRESHOLD_MS:
                long_running.append((task_id, action, running_ms))

    if not found:
        print("  none.")

    if long_running:
        print("\n  LONG-RUNNING tasks (over "
              f"{LONG_TASK_THRESHOLD_MS / 1000:.0f}s):")
        for task_id, action, ms in long_running:
            print(f"    {task_id}  {action}  {ms / 1000:.1f}s")
        print(
            "  A task can be cancelled with: "
            "POST /_tasks/<task_id>/_cancel"
        )


if __name__ == "__main__":
    show_pending_tasks()
    show_running_tasks()
