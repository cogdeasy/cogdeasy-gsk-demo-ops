# GSK Track B demo ops

Demo-control repo for the GSK AI Accelerator Day Track B demo: Devin playbooks, automation definitions, Jira seed data, the R&D support-report simulator and the rehearsal runbook.

Subject repos:

- [cogdeasy-gsk-ohdsi-webapi](https://github.com/cogdeasy/cogdeasy-gsk-ohdsi-webapi) - Q1, Q2, Q4, Q5
- [cogdeasy-gsk-abap2xlsx](https://github.com/cogdeasy/cogdeasy-gsk-abap2xlsx) - Q3

| path | what |
|---|---|
| `docs/RUNBOOK.md` | demo path Q1-Q5: live vs pre-run, day-before and on-the-day steps |
| `playbooks/` | the five Devin playbooks the automations run |
| `automations/automations.json` | desired-state definitions of the six automations |
| `jira/seed.json`, `jira/seed.py` | demo tickets for the GSK project, created without trigger labels |
| `jira/backlog.json` | background backlog (4 Epics, ~30 issues) so the board looks active; `seed.py --file jira/backlog.json` creates the issues only (no status, priority, assignee, comments or links) |
| `support-sim/` | ten simulated R&D support reports (half duplicates) and a poster for Jira or Slack |
| `oncall-sim/` | four synthetic WebAPI alerts, the answer key and a poster for a Devin webhook trigger |
| `api/start_audit_pack.sh` | starts the audit-pack session through the Devin API v3 (wraps `demo-ops-audit-pack`) |
| `src/demo_ops/` | the code behind every script: one HTTP client, env settings, the CLIs, JSON Schemas |
| `docs/MODERNISATION.md` | tooling decisions and open follow-ups |

The repo stays a thin control plane. Playbooks and JSON say what happens; Devin sessions do the
work. The Python here only seeds Jira, posts simulated reports and alerts, and starts sessions.

## Setup

Python 3.11+ and [uv](https://docs.astral.sh/uv/). `uv sync` installs the locked dependencies
and the `demo-ops-*` commands into `.venv/`. Plain pip also works: `pip install -e .`.

```bash
uv sync                   # runtime + dev tools, from uv.lock
uv run pre-commit install # ruff, mypy, shellcheck, data validation on commit
```

| command | old path (still works) | env (live mode) |
|---|---|---|
| `uv run demo-ops-seed [--file jira/backlog.json] [--dry-run]` | `python3 jira/seed.py` | `JIRA_EMAIL`, `JIRA_API_TOKEN`, optional `JIRA_BASE_URL` |
| `uv run demo-ops-support-sim --target jira\|slack [--delay 2] [--dry-run]` | `python3 support-sim/post_reports.py` | Jira vars + optional `JIRA_PROJECT`, or `SLACK_WEBHOOK_URL` |
| `uv run demo-ops-oncall-sim [--alert A3\|--all] [--delay 5] [--dry-run]` | `python3 oncall-sim/post_alert.py` | `DEVIN_ONCALL_WEBHOOK_URL`, `DEVIN_ONCALL_WEBHOOK_SECRET` |
| `uv run demo-ops-audit-pack GSK-1 [--dry-run]` | `api/start_audit_pack.sh GSK-1` | `GSK_AUDIT_PLAYBOOK_ID` (dry run too), `DEVIN_API_KEY`, `DEVIN_ORG_ID` |
| `uv run demo-ops-validate [file ...]` | - | none |

`--dry-run` posts nothing, needs no credentials and runs on a bare `python3` through the old
paths. Live runs check every variable they need before the first request and name all the
missing ones.

### Secrets

Every secret comes from the environment. None are in code, config, tests or logs, and none are
needed for dry runs. `.env.example` lists each variable; copy it to `.env` (git-ignored) and load
it with `set -a; . ./.env; set +a`. Error messages show only the host of a failed URL, because
Slack and Devin webhook URLs carry their secret in the path.

### Checks

```bash
uv run ruff check . && uv run ruff format --check .   # lint + format
uv run mypy                                           # strict typecheck
uv run pytest                                         # unit tests, HTTP mocked
uv run demo-ops-validate                              # JSON Schemas + cross-file checks
```

CI (`.github/workflows/ci.yml`) runs all of the above, shellcheck, and the dry runs on every PR.
Editing a data file? Run `demo-ops-validate`. The schemas are in `src/demo_ops/schemas/`.
