#!/usr/bin/env python
"""Capture the state of an Elasticsearch cluster to a baseline file.

Run this ONCE on a freshly installed cluster (see the 00_install exercise).
It records the names of everything that exists right after install plus the
cluster settings, and writes them to a JSON baseline file. The companion
reset script (elk_reset) later reads this file and deletes anything that is
NOT in it, returning the cluster to its post-install state between exercises.

What is captured:
  * indices            -- every index name, including system (dot-prefixed)
  * data_streams       -- data stream names
  * index_templates    -- composable index template names
  * component_templates-- component template names
  * legacy_templates   -- legacy (_template) names
  * ilm_policies       -- ILM policy names
  * slm_policies       -- SLM (snapshot lifecycle) policy names
  * ingest_pipelines   -- ingest pipeline names
  * snapshot_repos     -- registered snapshot repository names
  * transforms         -- transform ids
  * cluster_settings   -- persistent + transient settings (values, not just
                          names: these should be empty on a fresh install, so
                          recording the values lets the reset detect drift)

This records NAMES, not contents. The reset deletes by name; it does not try
to restore the internal contents of a default object that an exercise edited
in place. Node-level config (elasticsearch.yml, JVM heap, node.attr.*) lives
on disk, not in the REST API, and is therefore NOT captured here.

The baseline is machine-specific state, not source, so it is written outside
the repo and is not committed.

Set ES_URL to target a non-default host (default http://localhost:9200).
Set ELK_BASELINE to change the output path (default ~/elk_baseline.json).

Usage:
    ./elk_capture_baseline.py
    ES_URL=http://host:9200 ./elk_capture_baseline.py
    ELK_BASELINE=/tmp/mine.json ./elk_capture_baseline.py
"""

import json
import os

from elasticsearch import Elasticsearch

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
BASELINE = os.environ.get(
    "ELK_BASELINE", os.path.expanduser("~/elk_baseline.json")
)


def _names(items, key):
    """Sorted list of the `key` field from a list of dicts (deterministic)."""
    return sorted(item[key] for item in items)


def capture(es) -> dict:
    """Query every relevant API and return the baseline as a plain dict."""
    # Indices: include system (dot-prefixed) and closed ones, since those are
    # part of the post-install state and must be preserved by the reset.
    indices = es.cat.indices(
        h="index", format="json", expand_wildcards="all"
    )

    data_streams = es.indices.get_data_stream(name="*").get("data_streams", [])

    index_templates = es.indices.get_index_template().get(
        "index_templates", []
    )
    component_templates = es.cluster.get_component_template().get(
        "component_templates", []
    )
    # Legacy templates and the *_policy / pipeline / repo / transform APIs
    # return name-keyed objects, so their keys are the names.
    legacy_templates = es.indices.get_template()
    ilm_policies = es.ilm.get_lifecycle()
    slm_policies = es.slm.get_lifecycle()
    ingest_pipelines = es.ingest.get_pipeline()
    snapshot_repos = es.snapshot.get_repository()

    transforms = es.transform.get_transform(transform_id="*").get(
        "transforms", []
    )

    # Cluster settings as actually overridden (not include_defaults): on a
    # fresh install both of these are empty {}.
    settings = es.cluster.get_settings(flat_settings=True)

    return {
        "es_url": ES_URL,
        "indices": _names(indices, "index"),
        "data_streams": _names(data_streams, "name"),
        "index_templates": _names(index_templates, "name"),
        "component_templates": _names(component_templates, "name"),
        "legacy_templates": sorted(legacy_templates.keys()),
        "ilm_policies": sorted(ilm_policies.keys()),
        "slm_policies": sorted(slm_policies.keys()),
        "ingest_pipelines": sorted(ingest_pipelines.keys()),
        "snapshot_repos": sorted(snapshot_repos.keys()),
        "transforms": sorted(t["id"] for t in transforms),
        "cluster_settings": {
            "persistent": settings.get("persistent", {}),
            "transient": settings.get("transient", {}),
        },
    }


def main() -> None:
    """Capture the cluster baseline and write it to the baseline file."""
    es = Elasticsearch(ES_URL)
    print(f"target: {ES_URL}")

    baseline = capture(es)

    with open(BASELINE, "w", encoding="utf-8") as handle:
        json.dump(baseline, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # Short summary so you can sanity-check what was recorded.
    print(f"wrote baseline to {BASELINE}")
    for key, value in baseline.items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)}")
    persistent = baseline["cluster_settings"]["persistent"]
    transient = baseline["cluster_settings"]["transient"]
    print(
        f"  cluster_settings: {len(persistent)} persistent, "
        f"{len(transient)} transient"
    )
    if persistent or transient:
        print(
            "  note: cluster settings are non-empty; on a truly fresh install "
            "these are usually both empty."
        )


if __name__ == "__main__":
    main()
