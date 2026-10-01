# AppSec beat (WebAPI)

How the security part of the demo runs on `cogdeasy/cogdeasy-gsk-ohdsi-webapi`.

| file | what |
|---|---|
| `threat-model.md` | entry points, assets, attacker models and top risks, with file references |
| `scan-profile.md` | text to paste into a Security Swarm scan profile |

## Two layers

| | Trivy in CI | Security Swarm |
|---|---|---|
| what | known CVEs in dependencies inside `WebAPI.war` | code-level findings in WebAPI's own code |
| where | `scan` check in `.github/workflows/ci.yml`, SARIF to GitHub code scanning; reports, does not block | Devin app, Security > Start scan, with the profile from `scan-profile.md` |
| output | CVE list per library | findings with severity, file and line, data flow, evidence, optional sandbox validation |
| fix | dependency upgrade PR, one library family per PR (Q2-SEC) | Devin fix PR per finding |

Docs: [Security Swarm](https://docs.devin.ai/work-with-devin/security-swarm), [Code Scans](https://docs.devin.ai/work-with-devin/code-scans).

## Flow

1. The AppSec reviewer creates the profile from `scan-profile.md` and starts a scan on the WebAPI repo with Interactive mode on.
2. Devin proposes a threat model. The reviewer compares it with `threat-model.md`, corrects it, then lets the scan run.
3. Findings go to the AppSec reviewer. For each: dismiss (false positive or duplicate, for example a GenericExceptionMapper finding that duplicates GSK-1), mark reviewed, or assign to Devin.
4. An assigned finding becomes a Devin fix PR with a regression test. The PR goes through the normal path: `build`, `tests`, `scan` checks, the evidence pack, and the named CODEOWNERS approver. Devin does not merge.

## Rules

- No scan is started from this repo. The reviewer starts it.
- Findings and the threat model are drafts until the AppSec reviewer accepts them. Reviewer, decision and date fields are left for that person.
- Profiles hold no credentials. Sandbox validation uses the repo's embedded test database only.
