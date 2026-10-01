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
| `support-sim/` | ten simulated R&D support reports (half duplicates) and a poster for Jira or Slack |
