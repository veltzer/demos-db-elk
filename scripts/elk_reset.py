#!/usr/bin/env python
"""Reset an Elasticsearch cluster back to its post-install baseline.

This is the companion to elk_capture_baseline.py. It reads the baseline file
(captured ONCE on a fresh install) and deletes everything that is present now
but NOT in the baseline -- user indices, data streams, templates, ILM/SLM
policies, ingest pipelines, snapshot repositories and transforms an exercise
created -- then wipes all cluster settings back to their defaults. The result
is the cluster as it looked right after installation.

It is meant to run BEFORE and AFTER every exercise, so it is:
  * idempotent  -- running it twice is the same as running it once; deleting
                   something already gone is treated as success (404 is fine).
  * quiet       -- prints nothing unless something was changed or --verbose.
  * safe        -- refuses to touch a non-local cluster unless you opt in with
                   ELK_RESET_ALLOW_REMOTE=1, since this is destructive.

What it does NOT do: it deletes objects by NAME, so it does not restore the
internal contents of a default object that an exercise edited in place, and it
cannot revert node-level config (elasticsearch.yml, JVM heap, node.attr.*)
which lives on disk, not in the REST API. Cluster settings ARE reset.

Set ES_URL to target a non-default host (default http://localhost:9200).
Set ELK_BASELINE to change the baseline path (default ~/elk_baseline.json).

Usage:
    ./elk_reset.py              # quiet reset to baseline
    ./elk_reset.py -v           # report every object removed
    ELK_RESET_ALLOW_REMOTE=1 ES_URL=http://host:9200 ./elk_reset.py
"""

import json
import os
import sys

from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
BASELINE = os.environ.get(
    "ELK_BASELINE", os.path.expanduser("~/elk_baseline.json")
)
ALLOW_REMOTE = os.environ.get("ELK_RESET_ALLOW_REMOTE", "0") == "1"

VERBOSE = "-v" in sys.argv[1:] or "--verbose" in sys.argv[1:]


def log(message: str) -> None:
    """Print only in verbose mode (the script is quiet by default)."""
    if VERBOSE:
        print(message)


def is_local(url: str) -> bool:
    """True if the URL points at the local machine."""
    return "localhost" in url or "127.0.0.1" in url


def load_baseline() -> dict:
    """Read the captured baseline, or exit with a clear message if missing."""
    try:
        with open(BASELINE, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        sys.exit(
            f"error: baseline file not found at {BASELINE}.\n"
            "Run elk_capture_baseline.py on a fresh install first."
        )


def safe_delete(action, name: str) -> bool:
    """Call a delete function for `name`, treating 'already gone' as success.

    Returns True if the object was actually deleted, False if it was already
    absent -- this is what makes the reset idempotent.
    """
    try:
        action(name)
        return True
    except NotFoundError:
        return False


def reset_category(es, label, current, baseline, deleter) -> int:
    """Delete every current object whose name is not in the baseline.

    `current` is the set of names present now, `baseline` the set to keep,
    `deleter` a one-arg function that deletes by name. Returns how many were
    actually removed.
    """
    extra = sorted(set(current) - set(baseline))
    removed = 0
    for name in extra:
        if safe_delete(deleter, name):
            removed += 1
            log(f"  - {label}: {name}")
    if removed:
        print(f"removed {removed} {label}(s)")
    return removed


def current_state(es) -> dict:
    """Return the names currently present, mirroring the baseline structure."""
    indices = es.cat.indices(h="index", format="json", expand_wildcards="all")
    data_streams = es.indices.get_data_stream(name="*").get(
        "data_streams", []
    )
    index_templates = es.indices.get_index_template().get(
        "index_templates", []
    )
    component_templates = es.cluster.get_component_template().get(
        "component_templates", []
    )
    transforms = es.transform.get_transform(transform_id="*").get(
        "transforms", []
    )
    return {
        "indices": [i["index"] for i in indices],
        "data_streams": [d["name"] for d in data_streams],
        "index_templates": [t["name"] for t in index_templates],
        "component_templates": [t["name"] for t in component_templates],
        "legacy_templates": list(es.indices.get_template().keys()),
        "ilm_policies": list(es.ilm.get_lifecycle().keys()),
        "slm_policies": list(es.slm.get_lifecycle().keys()),
        "ingest_pipelines": list(es.ingest.get_pipeline().keys()),
        "snapshot_repos": list(es.snapshot.get_repository().keys()),
        "transforms": [t["id"] for t in transforms],
    }


def reset_cluster_settings(es) -> bool:
    """Clear every persistent and transient cluster setting to its default.

    Setting a key to null removes the override; doing it across the board
    returns the cluster to the empty-settings state of a fresh install. This
    handles the 'exercise changed a watermark / circuit breaker' case that the
    name-based diff cannot see.
    """
    settings = es.cluster.get_settings(flat_settings=True)
    persistent = settings.get("persistent", {})
    transient = settings.get("transient", {})
    if not persistent and not transient:
        return False
    body = {
        "persistent": {key: None for key in persistent},
        "transient": {key: None for key in transient},
    }
    es.cluster.put_settings(body=body)
    log(
        f"  - cluster settings cleared: "
        f"{len(persistent)} persistent, {len(transient)} transient"
    )
    print("reset cluster settings to defaults")
    return True


def main() -> None:
    """Reset the cluster to the captured post-install baseline."""
    if not is_local(ES_URL) and not ALLOW_REMOTE:
        sys.exit(
            f"refusing to reset non-local cluster {ES_URL}.\n"
            "Set ELK_RESET_ALLOW_REMOTE=1 to override (this is destructive)."
        )

    baseline = load_baseline()
    es = Elasticsearch(ES_URL)
    log(f"target: {ES_URL}")

    current = current_state(es)

    changed = 0

    # Order matters: delete data streams before their backing indices, and
    # indices before templates, so nothing is recreated from a template
    # during teardown.
    changed += reset_category(
        es,
        "data stream",
        current["data_streams"],
        baseline.get("data_streams", []),
        lambda n: es.indices.delete_data_stream(name=n),
    )
    changed += reset_category(
        es,
        "index",
        current["indices"],
        baseline.get("indices", []),
        lambda n: es.indices.delete(index=n, expand_wildcards="all"),
    )
    changed += reset_category(
        es,
        "index template",
        current["index_templates"],
        baseline.get("index_templates", []),
        lambda n: es.indices.delete_index_template(name=n),
    )
    changed += reset_category(
        es,
        "component template",
        current["component_templates"],
        baseline.get("component_templates", []),
        lambda n: es.cluster.delete_component_template(name=n),
    )
    changed += reset_category(
        es,
        "legacy template",
        current["legacy_templates"],
        baseline.get("legacy_templates", []),
        lambda n: es.indices.delete_template(name=n),
    )
    changed += reset_category(
        es,
        "ILM policy",
        current["ilm_policies"],
        baseline.get("ilm_policies", []),
        lambda n: es.ilm.delete_lifecycle(name=n),
    )
    changed += reset_category(
        es,
        "SLM policy",
        current["slm_policies"],
        baseline.get("slm_policies", []),
        lambda n: es.slm.delete_lifecycle(policy_id=n),
    )
    changed += reset_category(
        es,
        "ingest pipeline",
        current["ingest_pipelines"],
        baseline.get("ingest_pipelines", []),
        lambda n: es.ingest.delete_pipeline(id=n),
    )
    changed += reset_category(
        es,
        "transform",
        current["transforms"],
        baseline.get("transforms", []),
        lambda n: es.transform.delete_transform(transform_id=n, force=True),
    )
    changed += reset_category(
        es,
        "snapshot repository",
        current["snapshot_repos"],
        baseline.get("snapshot_repos", []),
        lambda n: es.snapshot.delete_repository(name=n),
    )

    if reset_cluster_settings(es):
        changed += 1

    if changed == 0:
        log("already at baseline; nothing to do.")
    else:
        log("reset complete.")


if __name__ == "__main__":
    main()
