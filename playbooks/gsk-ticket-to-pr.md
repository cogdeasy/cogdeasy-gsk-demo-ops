# GSK ticket to PR

Used by the `gsk-ticket-to-pr` automation (Jira label `devin`). Repo: cogdeasy/cogdeasy-gsk-ohdsi-webapi.

## Procedure

1. Read the Jira ticket, its acceptance criteria (AC1..ACn) and the repo's AGENTS.md.
2. Comment on the ticket: "Devin picked this up: <session link>".
3. Clone the repo, `export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64`, run
   `mvn -B -q -Pwebapi-postgresql -DskipUnitTests -DskipITtests test-compile`.
4. Reproduce before touching code (`./reproduce.sh` for error-mapper tickets). Paste the output.
5. Search the codebase for the code path and write a short step-by-step plan in the session.
6. Write regression tests from the acceptance criteria, one or more per AC. Run them and show
   which fail on the current code (red). For a tests-only story (no production change), skip
   the red run and step 7; the new tests pass on the current code.
7. Fix the most specific root cause. Do not catch-and-ignore; do not return raw database text.
8. Run the new tests (green), then the full suite `mvn -B -Pwebapi-postgresql test`. Report
   run / passed / failures / errors / skipped from `python3 dev/ci/summary.py`, which totals
   `target/surefire-reports` (unit) and `target/failsafe-reports` (integration).
9. Branch `devin/<ticket-key-lowercase>-<slug>`, PR title `fix(<ticket>): ...`, fill every
   template section: Ticket, URS delta, Test mapping (AC -> test -> before -> after), Change
   record (tier silver).
10. Wait for build, tests and scan. Fix failures caused by the change.
11. Comment on the Jira ticket with the PR link, the test totals and "awaiting GSK approver".

## Specifications

- One ticket, one PR. Never merge; the CODEOWNERS approver merges.
- The PR has a regression test for every acceptance criterion.
- Full-suite totals are quoted from the reports, not estimated.

## Forbidden actions

- Do not push to `main`, do not change branch protection, CODEOWNERS or CI to get green.
- Do not skip or delete existing tests.
