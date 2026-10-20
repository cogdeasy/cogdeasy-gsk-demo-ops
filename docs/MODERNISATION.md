# Modernisation notes

Where the repo's tooling is now, why, and what is still open. The repo's job is unchanged: a
thin, declarative control plane (playbooks + JSON) that hands the work to Devin sessions.

## Before / after

| area | before | after |
|---|---|---|
| packaging | three loose stdlib scripts, no manifest | `pyproject.toml` (hatchling), Python >=3.11, `uv.lock`, `demo-ops-*` console scripts |
| HTTP | `urllib.request` copied in three scripts; no timeout, no retry | `demo_ops.http.HttpClient` (httpx, 15 s timeout, tenacity retries) used by every caller |
| config | `os.environ[...]` scattered; `KeyError` on a missing var | `demo_ops.settings` dataclasses; one error naming every missing var; URLs must be https |
| Devin API | bash + inline Python + curl | `demo-ops-audit-pack` on the same client; the `.sh` is a `set -euo pipefail` wrapper |
| quality | none | Ruff (lint + format), mypy `--strict`, shellcheck, pre-commit |
| tests | none | pytest: payloads, CLI parsing, seed vs backlog mode, retries, fail-fast, schemas; HTTP mocked |
| data | unchecked JSON | JSON Schema (2020-12) for all 7 data files, plus cross-file checks; `demo-ops-validate` |
| CI | none | `.github/workflows/ci.yml`: lint, format, types, shellcheck, validate, tests, dry runs |

## Decisions

- **httpx + tenacity, not requests.** httpx's `MockTransport` lets the tests mock HTTP with no
  extra test dependency, and it has real timeouts. Both are imported lazily, so `--dry-run`
  through the old script paths still runs on a bare `python3`. The blueprint's simulator
  commands and the RUNBOOK keep working unchanged.
- **Retries only where they cannot duplicate.** Every call is a non-idempotent POST: a Jira
  issue, a Devin session, a webhook-triggered session. So retries cover only connection
  failures, 429 and 503, where the server did not act. Read timeouts and other 5xx fail
  straight away, and the operator checks the board before rerunning.
- **Dataclasses, not pydantic-settings.** Five small settings groups don't justify a
  pydantic dependency.
- **The audit-pack script is ported to Python** so that all API calls go through one client
  layer. The shell entry point stays because the RUNBOOK and `automations.json` name it.
- **JSON stays JSON.** YAML or TOML would not remove any duplication: each file has one owner
  and one consumer. Schemas give more than a format change would.
- **Old script paths are shims.** `jira/seed.py` and the others add `src/` to `sys.path` and
  call the package `main()`, so docs, playbooks and the environment blueprint don't need to
  change.

## Validation coverage

`demo-ops-validate` checks each file against its schema in `src/demo_ops/schemas/`, then:

- automations: names are unique, `playbook` files exist, the `api` trigger script exists;
- Jira seed files: refs and keys are unique; a `parent` is defined earlier in the file (seed
  creates in file order) or is a real key; a link end resolves; `trigger_label` is never
  pre-applied in `labels`;
- support reports: `dup_of` resolves to a report id or a `jira/seed.json` ref;
- on-call: the alert ids in `alerts.json` match the answer-key ids in `expected.json`.

## Open follow-ups

| id | task | why | owner |
|---|---|---|---|
| M1 | Move the org's Atlassian MCP integration from the v1 endpoint to v2 | `docs/PLATFORM.md` flags v1; the move is an org integration setting, not code here | |
| M2 | Turn the CI `check` job into a required status check on `main` | the workflow reports, but branch protection is a repo setting | |
| M3 | Update the environment blueprint to run `uv sync` and use `uv run demo-ops-*` | the old paths work, so this is optional | |
| M4 | Optional `--apply-status` for backlog/roles seeding (status, links, assignee) | today these are set by hand on a fresh board (RUNBOOK, day before) | |
