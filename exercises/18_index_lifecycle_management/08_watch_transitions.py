#!/usr/bin/env python
"""Watch an index advance through ILM phases in a short, observable session.

Real retention policies use day/week/month time units, so you would never see
a transition during a training session. This script instead:

  1. Lowers the cluster-wide ILM poll interval so checks happen every 10s
     (default is 10 MINUTES) via PUT /_cluster/settings.
  2. Creates a "fast" ILM policy whose phases advance after only a minute or
     two (min_age in minutes, rollover after a single document).
  3. Bootstraps a managed index + write alias.
  4. Indexes a document to trigger the rollover, then polls _ilm/explain and
     prints the phase/action/step of each backing index as it changes.

Within a few minutes you should SEE the rolled-over index walk hot -> warm ->
cold -> delete. Stop early with Ctrl-C.
"""

import time

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

POLICY_NAME = "fast-ilm-demo"
ALIAS = "fastlogs"
FIRST_INDEX = "fastlogs-000001"
TEMPLATE = "fast-ilm-template"

# A policy with tiny min_age values so we can watch transitions live.
FAST_POLICY = {
    "phases": {
        "hot": {
            "min_age": "0ms",
            "actions": {
                # Roll over as soon as a single document lands.
                "rollover": {"max_docs": 1},
                "set_priority": {"priority": 100},
            },
        },
        "warm": {
            "min_age": "1m",
            "actions": {
                "forcemerge": {"max_num_segments": 1},
                "set_priority": {"priority": 50},
            },
        },
        "cold": {
            "min_age": "2m",
            "actions": {
                "readonly": {},
                "set_priority": {"priority": 0},
            },
        },
        "delete": {
            "min_age": "3m",
            "actions": {"delete": {}},
        },
    }
}


def speed_up_ilm() -> None:
    """Lower the cluster ILM poll interval so steps run every 10 seconds."""
    es.cluster.put_settings(
        persistent={"indices.lifecycle.poll_interval": "10s"}
    )
    print("set indices.lifecycle.poll_interval = 10s (default is 10m)")


def setup() -> None:
    """Create the fast policy, template and bootstrap index, then seed a doc."""
    es.ilm.put_lifecycle(name=POLICY_NAME, policy=FAST_POLICY)
    print(f"created fast ILM policy '{POLICY_NAME}'")

    es.indices.put_index_template(
        name=TEMPLATE,
        index_patterns=["fastlogs-*"],
        template={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "index.lifecycle.name": POLICY_NAME,
                "index.lifecycle.rollover_alias": ALIAS,
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "message": {"type": "text"},
                }
            },
        },
        priority=500,
    )
    print(f"created index template '{TEMPLATE}'")

    es.indices.create(
        index=FIRST_INDEX,
        aliases={ALIAS: {"is_write_index": True}},
    )
    print(f"bootstrapped '{FIRST_INDEX}' as write index for alias '{ALIAS}'")

    es.index(
        index=ALIAS,
        document={"@timestamp": "2026-06-14T10:00:00Z", "message": "go"},
    )
    es.indices.refresh(index=ALIAS)
    print("indexed one document to trigger the hot-phase rollover\n")


def watch(minutes: float = 5.0) -> None:
    """Poll _ilm/explain and print phase/action/step changes per index."""
    deadline = time.time() + minutes * 60
    last_state: dict[str, str] = {}
    while time.time() < deadline:
        try:
            explain = es.ilm.explain_lifecycle(index="fastlogs-*")
        except Exception as exc:  # index may be deleted mid-poll
            print(f"explain failed (index likely deleted): {exc}")
            break
        indices = explain.get("indices", {})
        if not indices:
            print("no managed fastlogs indices remain (all deleted)")
            break
        for name, info in sorted(indices.items()):
            phase = info.get("phase", "?")
            action = info.get("action", "?")
            step = info.get("step", "?")
            state = f"{phase}/{action}/{step}"
            if last_state.get(name) != state:
                ts = time.strftime("%H:%M:%S")
                managed = info.get("managed", False)
                print(f"[{ts}] {name}: managed={managed} -> {state}")
                last_state[name] = state
        time.sleep(10)
    print("\ndone watching (timed out or all indices deleted)")


if __name__ == "__main__":
    speed_up_ilm()
    setup()
    try:
        watch()
    except KeyboardInterrupt:
        print("\ninterrupted")
