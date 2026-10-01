# GSK on-call triage

## Overview
For SRE / on-call: take a production alert for WebAPI, decide if it is new, a duplicate of known
work, a runbook case or noise, investigate new ones, and propose (not perform) the remediation.
Started by the `gsk-oncall-triage` automation (incoming webhook from the monitoring tool; see
`oncall-sim/`).

## What's Needed From User
- The alert payload (title, severity, service, metric, observed value, sample logs).

## Procedure
1. Parse the alert. Search open GSK Bugs and recent `role-sre` issues for the same signature
   (exception class, endpoint, metric).
2. Duplicate of known work (e.g. the GenericExceptionMapper NPE is GSK-1): comment on that issue
   with the alert details and stop.
3. Runbook case (e.g. Hikari pool exhaustion): follow the linked runbook's diagnosis steps
   read-only and report which step applies.
4. Noise (flapping, below threshold on re-check): recommend suppression with the reason.
5. New: read the code path from the stack trace or endpoint, check the recent merges for a likely
   cause, and create a GSK Bug (label `role-sre`) with repro, evidence and a proposed fix or
   rollback. If the fix is clear and small, open a PR via the ticket-to-PR steps.
6. Summarise: classification, evidence, proposed action, owner.

## Specifications
- Every classification cites the evidence that decided it.
- Validation: the alert ends as a comment on an existing issue, a new Bug, or a suppression
  recommendation.

## Advice and Pointers
- Answer key for the simulator: `oncall-sim/expected.json`.

## Forbidden Actions
- Do not roll back, restart, scale or change production. A human on-call engineer approves and
  performs any production action.
- Do not merge.
