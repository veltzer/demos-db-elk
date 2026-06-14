#!/usr/bin/env python
"""Create the same hot/warm/cold/delete ILM policy via the Python client.

This is the programmatic equivalent of `01_create_ilm_policy.sh`. Using the
client is handy when the policy is generated from configuration (for example a
retention value that differs per environment) rather than hand-written JSON.
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
POLICY_NAME = "logs-policy"

POLICY = {
    "phases": {
        "hot": {
            "min_age": "0ms",
            "actions": {
                "rollover": {
                    "max_primary_shard_size": "50gb",
                    "max_age": "30d",
                    "max_docs": 100_000_000,
                },
                "set_priority": {"priority": 100},
            },
        },
        "warm": {
            "min_age": "7d",
            "actions": {
                "allocate": {"number_of_replicas": 1},
                "shrink": {"number_of_shards": 1},
                "forcemerge": {"max_num_segments": 1},
                "set_priority": {"priority": 50},
            },
        },
        "cold": {
            "min_age": "30d",
            "actions": {
                "allocate": {"number_of_replicas": 0},
                "readonly": {},
                "set_priority": {"priority": 0},
            },
        },
        "delete": {
            "min_age": "90d",
            "actions": {"delete": {}},
        },
    }
}


def create_policy() -> None:
    """Create (or overwrite) the ILM policy."""
    es.ilm.put_lifecycle(name=POLICY_NAME, policy=POLICY)
    print(f"created ILM policy '{POLICY_NAME}'")
    current = es.ilm.get_lifecycle(name=POLICY_NAME)
    phases = current[POLICY_NAME]["policy"]["phases"]
    print(f"phases defined: {', '.join(sorted(phases))}")


if __name__ == "__main__":
    create_policy()
