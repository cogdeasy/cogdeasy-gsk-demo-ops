# Track B demo runbook

One change, every role. The story follows a change from a scientist's rough request to an
audited release, with each GSK role getting its moment, and the five video asks (Q1-Q5) as the
spine. Validation route: CSA by default, full GAMP 5 CSV for high-risk changes. Role detail is in
`docs/ROLES.md`; the Devin surfaces and how skills / plugins fit are in `docs/PLATFORM.md`.

## The path

| act | role(s) | what happens | trigger | ask | live / pre-run |
|---|---|---|---|---|---|
| 0 | R&D scientist, R&D support | Reports arrive; duplicates are linked, R1 joins the GSK-1 fix | `support-sim/post_reports.py --target jira` (label `rd-support`) | Q4 | live intake |
| 1 | Business analyst | Rough request becomes AC, draft URS, impact, risk call | Jira label `devin-refine` | — | live (3-5 min) |
| 2 | Architect | DeepWiki / Ask Devin on WebAPI and ABAP; Spring Boot 2.7 ADR | Ask Devin | — | live |
| 3a | Software engineer, code reviewer | GSK-1: reproduce, red tests, fix, PR, CI, Devin Review | Jira label `devin` | Q1 | **live** (start first, 15-20 min) |
| 3b | Engineers, AppSec | Epic fans out SEC / BUG / COV lanes in parallel | Epic label `devin-backlog` | Q2 | pre-run |
| 3c | AppSec | Security Swarm findings with evidence; one finding to a fix PR | scan from app; label `devin-security` | Q2 | pre-run |
| 3d | SAP / ABAP | Z-code brief, analysis only; S/4 readiness inventory | label `devin-abap` | Q3 | pre-run |
| 3e | SAP, data migration lead | S/4 wave remediation on cogdeasy/gsk, one child and PR per object | Epic label `devin-migrate` | Q3 | pre-run |
| 4 | Test engineer | Test design from URS, CSA record or OQ protocol with execution evidence | label `devin-test` | Q5 | pre-run |
| 5 | CSV lead | PR opened -> risk gate -> document fan-out to child sessions | PR opened | Q5 | automatic on the Q1 PR |
| 6 | QA approver | QA checklist pre-filled, gaps and deviations | PR label `ready-for-qa` | Q5 | live (2-3 min) |
| 7 | Named approver, release manager | Approver merges; release notes, change-board pack, rollback plan | GitHub approval; label `devin-release` | Q5 | pre-run |
| 7b | R&D scientist | Executes the PQ / UAT script Devin drafted | — | Q5 | show the script |
| 8 | SRE / on-call | Alerts: duplicate of GSK-1, runbook case, noise, new | `oncall-sim/post_alert.py` -> webhook | Q4 | live |
| 9 | Auditor | Inspection pack for GSK-1, request to approval | `api/start_audit_pack.sh GSK-1` (Devin API) | Q5 | pre-run, show live start |

## Risk gate (act 5)

| risk | route | documents (owner) |
|---|---|---|
| low | CSA, unscripted | risk assessment, CR, URS delta, trace, CSA test record (test), release notes |
| medium | CSA, scripted for changed functions | + FS/DS delta, OQ protocol (test), PQ/UAT script (scientist), test summary report, QA checklist (QA) |
| high | full CSV | + validation plan delta, IQ checklist, validation summary report (CSV lead), training note |

GSK-1 rates medium (silver tier, error handling on data-integrity violations). The full matrix is
in `validation/README.md` in the WebAPI repo.

## Day before

1. Board seeded (GSK-1..41 plus the role tickets, one per role lane, from the role-ticket seed). Trigger labels are only added
   on stage or in pre-runs.
2. Pre-run: `devin-backlog` on GSK-2, `devin-abap` on GSK-3, `devin-migrate` on the S/4 wave
   Epic, `devin-test` on the OQ test-design story, `devin-release` on the release Task, one
   `devin-security` finding, the audit pack. Review the PRs; leave them open.
3. Dry-run act 3a on a throwaway copy of GSK-1. Time it. Close the PR without merging.
4. `main` CI green on WebAPI, abap2xlsx and gsk; WebAPI blueprint has JDK 8 and a warm Maven cache.
5. Set `DEVIN_ONCALL_WEBHOOK_URL` for act 8 and `DEVIN_API_KEY` / `DEVIN_ORG_ID` for act 9.

## On the day

1. Open: Jira board, GitHub PR lists, Devin sessions list, Automations page.
2. Act 0, then act 3a straight away (it is the long one). Narrate acts 1, 2 and 3b-3e while it
   runs.
3. When the Q1 PR opens, act 5 fires by itself: show the risk result and the child sessions
   writing the documents.
4. Act 4 and 6 on the Q1 PR, act 7 from the pre-run, act 8 live, act 9 to close.
5. The boundary line in every act: Devin drafts and proposes; GSK people accept, sign, approve,
   merge and touch production.

## Numbers

The video's figures (247 tests, 194 findings, 47.4% -> 64.4%, 384 lines, 5 defects, 7 URS,
9 trace rows) are targets. Quote what CI and the sessions report on the day; measured baselines
are in `docs/BASELINE.md`.

## Prerequisites

- Second GitHub user as the GSK approver in CODEOWNERS, with branch protection on WebAPI `main`.
- Devin Jira integration on cog-gtm; Atlassian MCP moved to the v2 endpoint.
- Slack support channel with the Devin app invited (optional for act 0).
- Devin Oncall is not set up in this org; act 8 uses a webhook automation.
- Security Swarm scan started once from the app before the day (not scheduled; scans cost ACUs).
