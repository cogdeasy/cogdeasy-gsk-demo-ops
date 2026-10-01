# GSK backlog fan-out

## Overview
Work a GSK Epic's child stories in parallel on cogdeasy/cogdeasy-gsk-ohdsi-webapi: one child
Devin session and one PR per lane (security, maintenance bug, coverage), then summarise the
results on the Epic. Started by the `gsk-backlog-fanout` automation (Jira label
`devin-backlog` on an Epic).

## What's Needed From User
- A GSK Epic key whose child stories are the three lanes: security (SEC), maintenance bug
  (BUG), coverage (COV).
- The `GSK ticket to PR` playbook in the org (each child uses it).

## Procedure
1. Read the Epic and its child stories; map each child to a lane (SEC, BUG, COV).
2. Import the latest `scan` results from CI on `main` (job summary and code-scanning alerts).
   Post a triage table on the Epic: totals by severity, CVEs fixable now by a patch upgrade of a
   direct dependency, CVEs that need the Spring Boot major upgrade.
3. Start one child Devin session per child story, in parallel, each with the story key, the
   repo and the `GSK ticket to PR` playbook. Tell the COV child the story is tests-only.
   Record the start time.
4. SEC lane: one dependency family per commit, rescanning after each; if an upgrade adds a new
   finding, say so on the PR and move to the next patch version that does not.
5. COV lane: tests only (skip the red-test and fix steps). Report JaCoCo line and branch
   coverage for the package before and after.
6. Wait for the three children to finish and their PRs to show green CI.
7. Post on the Epic: PR links, wall-clock time, findings before/after, coverage delta, and the
   remaining items as candidate next tasks.

## Specifications
- Each lane is its own session and its own PR.
- Numbers quoted on the Epic come from CI artefacts.
- Validation: three PRs open with green `build`/`tests`/`scan`, and the Epic summary comment
  links all three.

## Advice and Pointers
- Children run on separate machines; give each the full story key, repo and lane rules in its
  prompt.

## Forbidden Actions
- No Spring Boot major upgrade inside this Epic; list it as the next candidate task.
- Do not merge any PR.
