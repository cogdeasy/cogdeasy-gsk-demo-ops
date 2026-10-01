# Role profiles in the demo path

Every GSK role in the change lifecycle, what Devin does for it, and where the human decides.
Validation route: CSA by default; full GAMP 5 CSV when the risk assessment rates the change high.

| # | role | input | Devin does | human decides | evidence produced | trigger / surface |
|---|---|---|---|---|---|---|
| 1 | Business analyst / product owner | rough request | AC, draft URS lines, impacted code, duplicate check, initial risk call | accepts AC and scope | refined ticket comment | Jira `devin-refine` -> `gsk-refine` |
| 2 | CSV / validation lead | refined ticket, PR | risk assessment, route CSA or CSV, document list | confirms risk and route | `risk-assessment.md`, validation plan delta (high) | PR opened -> `gsk-gxp-evidence-pack` |
| 3 | Architect | upgrade or design question | DeepWiki / Ask Devin on the repo, ADR draft | chooses the option | ADR | session or Ask Devin |
| 4 | Software engineer | ticket with AC | reproduce, red tests, fix, PR, CI | reviews and owns the code | PR, CI runs, Devin Review | Jira `devin` -> `gsk-ticket-to-pr`; Epic `devin-backlog` -> `gsk-backlog-fanout` |
| 5 | Test engineer / QA automation | AC, URS | test design (positive, negative, boundary), automation, execution evidence | accepts coverage, signs execution | CSA test record or OQ protocol, IQ (high) | Jira `devin-test` -> `gsk-test-design`; repo skill `test-engineer` |
| 6 | Code reviewer | PR | Devin Review: bugs, security, flags on every PR | resolves or rejects findings | PR review comments, check status | Devin Review (auto) |
| 7 | AppSec engineer | scan findings | Security Swarm investigation with evidence; fix PR per finding; risk-acceptance draft | accepts risk, approves fix | threat-model delta, scan delta, risk-acceptance draft | Security Swarm scan; Jira `devin-security` -> `gsk-security-remediation` |
| 8 | SAP functional / ABAP developer | Z-object, wave | Z-code brief (analysis only); S/4 readiness inventory; wave remediation, one PR per object | owns transports, SAP decisions | `docs/zcode/*.md`, `docs/s4/*`, remediation PRs | Jira `devin-abap` -> `gsk-zcode-reader`; Epic `devin-migrate` -> `gsk-s4-remediation-wave` |
| 9 | Data migration lead | wave extracts | cleansing and reconciliation checks in `tools/datamig` (cogdeasy/gsk) | signs reconciliation | reconciliation report | part of the migration wave |
| 10 | QA approver | evidence pack | QA checklist pre-filled, gap and deviation list | approves / rejects in GSK's quality system | `qa-review-checklist.md`, `deviation-capa.md` | GitHub label `ready-for-qa` -> `gsk-qa-review-prep` |
| 11 | Named GSK approver (CODEOWNER) | PR + pack | nothing; Devin cannot approve or merge | merges | GitHub approval | branch protection |
| 12 | Release / change manager | release scope | release notes, change-board pack, deploy and rollback plan | go / no-go | `validation/releases/<release>/*` | Jira `devin-release` -> `gsk-release-pack` |
| 13 | R&D scientist (end user) | release notes, PQ script | drafts the PQ / UAT script and training note | executes UAT, accepts | `pq-uat-script.md`, `training-note.md` | evidence-pack child |
| 14 | R&D support | user reports | dedupe, link, reproduce, fix or route | owns priority | linked issues, triage comments | Jira `rd-support` (live); Slack (needs channel) |
| 15 | SRE / on-call | alert | classify new / duplicate / runbook / noise, investigate, propose fix or rollback | performs any prod action | Bug or comment, runbook update | webhook -> `gsk-oncall-triage` |
| 16 | Auditor / inspection readiness | a change key | full chain request -> approval, completeness check | inspection outcome | `inspection-pack.md` | Devin API -> `gsk-audit-pack` |
| 17 | Platform owner (Devin admin) | org setup | n/a | owns playbooks, automations, skills, plugins, security profile | Automations and playbook history | Devin app / API |

## The boundary, every role

Devin drafts, tests, proposes and opens PRs. People accept requirements, decide risk, approve
code, sign validation records, approve releases and touch production. Devin never fills a
reviewer, decision, signature or date field, never approves, never merges.
