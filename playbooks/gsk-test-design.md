# GSK test design and execution evidence

## Overview
The test engineer's lane: from a ticket's acceptance criteria and URS lines, design test cases
(positive, negative, boundary), automate them, run the suite and capture execution evidence in
the form the risk route asks for (CSA record or scripted OQ protocol). Started by the
`gsk-test-design` automation (Jira label `devin-test`).

## What's Needed From User
- A GSK Jira issue with AC and URS lines, or a link to the change it tests.
- Repo: cogdeasy/cogdeasy-gsk-ohdsi-webapi.

## Procedure
1. Read the issue, linked issues and any open PR for the change. Read the repo skill
   `test-engineer` and `validation/README.md`. Comment "Devin is designing tests: <session link>".
2. Read the risk assessment for the change if one exists; otherwise use the issue's risk call.
   Low = CSA unscripted record; medium = CSA with scripted tests for changed functions;
   high = full CSV OQ protocol.
3. Design test cases: for each URS line at least one positive and one negative case, plus
   boundary cases where inputs have limits. Write them as a table: id, URS, type, input,
   expected.
4. Automate the cases as JUnit tests on a branch `devin/<key>-tests`. Tests only, no production
   code. Where the fix is not merged yet, mark tests that are expected to fail with the ticket key
   in the name and say so.
5. Run `mvn -B -Pwebapi-postgresql test` with JDK 8 and `python3 dev/ci/summary.py`. Capture the
   per-test results.
6. Fill `validation/csa-test-record.md` or `validation/oq-protocol.md` for the change under
   `validation/changes/<key>/` with steps, expected, actual, pass/fail and evidence refs (CI run
   link, surefire report path).
7. Open one PR, comment on the issue with the PR link, case count per URS, and pass/fail totals.

## Specifications
- Every URS line has at least one positive and one negative test.
- Execution evidence names the commit SHA and CI run it came from.
- Validation: PR open with tests and the filled record; full suite totals in the comment.

## Advice and Pointers
- Flaky tests: re-run once; if a result changes, record it as a deviation in the record rather
  than retrying until green.
- Test data: build it in the test; never depend on a live database.

## Forbidden Actions
- Do not change production code.
- Do not fill tester signature, reviewer or date fields.
- Do not approve or merge.
