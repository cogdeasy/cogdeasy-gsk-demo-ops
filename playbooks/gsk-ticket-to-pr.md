# GSK ticket to PR

## Overview
Take one GSK Jira ticket on cogdeasy/cogdeasy-gsk-ohdsi-webapi from label to a reviewed PR:
reproduce, write regression tests from the acceptance criteria, fix the root cause, open one PR
that passes `build`, `tests` and `scan`, and hand it to the named GSK approver. Started by the
`gsk-ticket-to-pr` automation (Jira label `devin`), or by a parent session for a child story.

## What's Needed From User
- A GSK Jira ticket key (e.g. `GSK-1`) with acceptance criteria AC1..ACn in the description.
- Repo: cogdeasy/cogdeasy-gsk-ohdsi-webapi (Java 8, Maven profile `webapi-postgresql`).

## Procedure
1. Read the Jira ticket, its acceptance criteria and the repo's `AGENTS.md`. Comment on the
   ticket: "Devin picked this up: <session link>".
2. Clone the repo, `export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64`, and run
   `mvn -B -q -Pwebapi-postgresql -DskipUnitTests -DskipITtests test-compile`.
3. Reproduce before touching code (`./reproduce.sh` for error-mapper tickets; exit 1 = bug
   present). Paste the output in the session.
4. Search the codebase for the code path and write a short step-by-step plan.
5. Write regression tests from the acceptance criteria, at least one per AC. Run them and show
   which fail on the current code (red). For a tests-only story (no production change), skip
   the red run and step 6; the new tests pass on the current code.
6. Fix the most specific root cause. Do not catch-and-ignore; do not return raw database text.
7. Run the new tests (green), then the full suite `mvn -B -Pwebapi-postgresql test`. Report
   run / passed / failures / errors / skipped from `python3 dev/ci/summary.py`, which totals
   unit (surefire) and integration (failsafe) reports.
8. Verify the change end to end: re-run the step-3 reproduction (`./reproduce.sh` exits 0 for
   error-mapper tickets; otherwise the same command or test now passes) and record the terminal
   run. This repo has no frontend (ATLAS is a separate app), so the
   terminal recording replaces the browser walkthrough; attach it to the PR.
9. Branch `devin/<ticket-key-lowercase>-<slug>`, PR title `fix(<ticket>): ...`, and fill every
   PR template section: Ticket, URS delta, Test mapping (AC -> test -> before -> after), Change
   record (tier silver).
10. Wait for `build`, `tests` and `scan`. Fix failures caused by the change.
11. Comment on the Jira ticket with the PR link, the test totals and "awaiting GSK approver".

## Specifications
- One ticket, one PR, on a fresh branch named after the ticket.
- The PR has a regression test for every acceptance criterion.
- Full-suite totals are quoted from the reports, not estimated.
- Validation: `build`, `tests` and `scan` are green on the PR and the Jira ticket carries the
  PR link.

## Advice and Pointers
- Use JDK 8; newer JDKs fail to compile this codebase.
- Database tests start an embedded PostgreSQL; no external database is needed.

## Forbidden Actions
- Never merge; the CODEOWNERS approver merges.
- Do not push to `main`, and do not change branch protection, CODEOWNERS or CI to get green.
- Do not skip or delete existing tests.
