# GSK security remediation

## Overview
For AppSec: take one security finding (from Security Swarm, Trivy or a pen test) on WebAPI,
confirm it, fix it with a test, and draft the security evidence. Started by the
`gsk-security-remediation` automation (Jira label `devin-security`).

## What's Needed From User
- A GSK Jira issue describing one finding: source, location, severity and evidence.

## Procedure
1. Read the issue and `security/threat-model.md` in cogdeasy/cogdeasy-gsk-demo-ops. Comment
   "Devin picked this up: <session link>".
2. Confirm the finding in the code: entry point, data flow, existing controls. If it is not
   exploitable, say why with file references and stop.
3. For a dependency CVE: pick the lowest patch or minor version that fixes it without a framework
   major upgrade; if none exists, draft a risk-acceptance note instead of a change.
4. For a code finding: write a failing test that shows the issue, fix, and make it pass.
5. Run the full suite and open one PR; CI `scan` must show no new findings.
6. Draft a threat-model delta and, for deferred CVEs, a risk-acceptance record in the PR body for
   the AppSec reviewer.
7. Comment on the issue with the PR link and before / after scan counts.

## Specifications
- One finding, one PR.
- Validation: failing-then-passing test (code findings) or scan delta (CVEs) shown in the PR.

## Advice and Pointers
- Spring Boot 1.5 caps many fixes; record those as deferred to the Spring Boot 2 upgrade ADR.

## Forbidden Actions
- Do not accept risk on GSK's behalf; draft it for the AppSec reviewer.
- Do not suppress or baseline findings to make the scan pass. Do not merge.
