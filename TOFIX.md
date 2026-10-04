# TOFIX

Findings from a code scan on 2026-10-04.

## Medium

- `scripts/elk_clean.sh:58` - deletes user indices with the wildcard `DELETE /*,-.*`, but Elasticsearch 8+ defaults `action.destructive_requires_name=true` and the course installs 9.1.3 (`exercises/shared/00_install/docker-compose.yml:3`), so the request is rejected and `del` swallows the error - indices are never removed while the script reports "done". The script is also not mentioned anywhere and is superseded by `scripts/elk_reset.py`; delete it, or enumerate index names and delete them one by one.
- `exercises/developer/07_web_search_application/notes.py:105` - `app.run(host=LISTENING_ADDRESS, port=LISTENING_PORT, debug=True)` with `LISTENING_ADDRESS = "0.0.0.0"` (`constants.py:13`) exposes the Werkzeug interactive debugger on every interface; bind to `127.0.0.1` or drop `debug=True`.
- `scripts/elk_reset.py:55` - the "refuse non-local cluster" safety check is a substring test (`"localhost" in url`), so URLs like `http://localhost.prod.example:9200` or `http://prod:9200/?x=127.0.0.1` pass as local and get wiped; parse the URL with `urllib.parse.urlsplit` and compare the hostname exactly.
- `exercises/shared/01_bulk/requirements.txt:5` - caps the client at `elasticsearch<9.0.0` with a comment about supporting 8.x servers, but the course installs a 9.1.3 server and the repo's `uv.lock` resolves `elasticsearch` 9.5.1; the cap and its rationale are stale - drop it (and the uncommented `>=` floors on lines 6-8) so `pip install -r` matches the repo environment.

## Low

- `exercises/shared/01_bulk/test_exercise.sh:40` - `rc=$?` after a plain command under `#!/bin/bash -eu` is dead code: a failure exits the script before the check, so the "Bulk insert test failed" branch never runs (same at line 56); use `if python ...; then` as step 2 does.
- `rsconstruct.toml:49` - orphaned comment "Runtime deps + type stubs so CI installs what the exercises import" with no config under it (it now sits above the actionlint section); remove it.
- `pyproject.toml:31` - `mypy_path = "src:python:scripts"` names `src` and `python` directories that do not exist in this repo; reduce to `scripts` (or match `[processor.mypy] src_dirs`).
