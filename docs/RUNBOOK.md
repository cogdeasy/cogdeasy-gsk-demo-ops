# Track B demo runbook

Five asks, one story: Devin works inside GSK's Jira, GitHub and CI, on GSK-style code, with
GSK people at the gates. Pre-run the long beats; run Q1 live.

| ask | repo | trigger | live or pre-run | artefact to show |
|---|---|---|---|---|
| Q1 Agents in Jira, GitHub, CI | cogdeasy-gsk-ohdsi-webapi | Jira label `devin` on the WEBAPI-DEMO-102 bug | **live** (about 15-20 min, start it first) | Jira comment -> session -> PR with build/tests/scan + Devin Review |
| Q2 Modernisation and backlog | cogdeasy-gsk-ohdsi-webapi | Jira label `devin-backlog` on the Epic | pre-run the day before | Epic summary, 3 PRs, scan before/after, JaCoCo delta |
| Q3 SaaS/ERP and S/4HANA code | cogdeasy-gsk-abap2xlsx | Jira label `devin-abap` | pre-run | `docs/zcode/zexcel_template_get_types.md` PR |
| Q4 Talent plus technology | cogdeasy-gsk-ohdsi-webapi | `support-sim/post_reports.py` -> Jira `rd-support` or Slack | live intake, pre-run triage as backup | duplicates linked under R1, triage evidence on new reports |
| Q5 Governance for GxP | cogdeasy-gsk-ohdsi-webapi | PR opened (from Q1/Q2) | automatic on the Q1 PR | `validation/changes/CR-*.md`, traceability rows, CODEOWNERS gate |

## Day before

1. `python3 jira/seed.py` (no trigger labels). Note the real issue keys.
2. Add `devin-backlog` to the Epic and `devin-abap` to the Q3 story. Let them finish; review the
   PRs, leave them open for the demo.
3. Dry-run Q1 on a throwaway copy of the bug ticket. Time it. Close the PR without merging.
4. Check `main` CI is green and the Devin blueprint snapshot has JDK 8 + a warm Maven cache.

## On the day

1. Open: Jira board, the Q1 bug, GitHub PR list, Devin sessions list.
2. **Q1:** add label `devin` to the bug. Narrate while it runs: trigger, own machine,
   reproduce (`./reproduce.sh` exits 1), plan, red tests, fix, green, PR + CI, Devin Review.
   Merge waits for the CODEOWNERS approver; do not merge on stage.
3. **Q2:** while Q1 runs, open the Epic: triage table, three PRs, rescan and coverage numbers.
4. **Q3:** open the Z-code brief PR. Point at the boundary line: analysis only.
5. **Q4:** run `python3 support-sim/post_reports.py --target jira` and watch duplicates get
   linked to R1/R2/R4. Show the R1 path joins the Q1 fix.
6. **Q5:** back to the Q1 PR: evidence-pack comment, draft CR with blank reviewer, required
   reviewer block on the merge button.

## Numbers

The video's figures (247 tests, 194 findings, 47.4% -> 64.4%, 384 lines, 5 defects, 7 URS,
9 trace rows) are targets. Quote what CI and the sessions actually report on the day; the
baseline numbers measured on `main` are in `docs/BASELINE.md`.

## Prerequisites

- Second GitHub user as the GSK approver, added to CODEOWNERS and branch protection on `main`
  (required review, required checks build/tests/scan).
- Devin Jira integration connected to cog-gtm with the GSK project.
- Slack support channel (optional for Q4) with the Devin app invited; record its channel id in
  `automations/automations.json`.
