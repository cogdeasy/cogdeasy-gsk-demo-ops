# GSK backlog fan-out

Used by the `gsk-backlog-fanout` automation (Jira label `devin-backlog` on an Epic).

## Procedure

1. Read the Epic and its child stories. Expect three lanes: security (SEC), maintenance bug
   (BUG), coverage (COV).
2. Import the latest `scan` results from CI on `main` (job summary and code scanning alerts).
   Post a triage table on the Epic: totals by severity, CVEs fixable now by a patch upgrade of
   a direct dependency, CVEs that need the Spring Boot major upgrade.
3. Start one child Devin session per child story, in parallel, each with the story key, the
   repo and the `gsk-ticket-to-pr` playbook. Tell the COV child the story is tests-only (see
   step 5). Record start time.
4. SEC lane: one dependency family per commit; rescan after each; if an upgrade introduces a
   new finding, say so on the PR and move to the next patch version that does not.
5. COV lane: tests only, so skip the red-test and fix steps of `gsk-ticket-to-pr`. New tests
   pass on the current code; report JaCoCo line and branch coverage before and after for the
   package.
6. When all three PRs are open and CI is green, post on the Epic: PR links, wall-clock time,
   findings before/after, coverage delta, and the remaining items as candidate next tasks.

## Specifications

- Each lane is its own session and its own PR.
- Numbers quoted on the Epic come from CI artefacts.

## Forbidden actions

- No Spring Boot major upgrade inside this Epic; list it as the next candidate task.
