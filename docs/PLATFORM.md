# Devin surfaces used in this demo

What each piece is, where it shows up, and what is set up today. Sources are Devin docs links.

| surface | what it is | in this demo | status |
|---|---|---|---|
| Automations | Event or schedule triggers that start sessions. Sources include Jira, GitHub, Slack, Linear, PagerDuty, schedule and incoming webhook ([docs](https://docs.devin.ai/product-guides/automations#trigger-sources)) | all role triggers in `automations/automations.json` | 5 live; new ones defined, created on approval |
| Playbooks | Reusable procedures attached to a session; the automation prompt names one | `playbooks/*.md`, one per role lane | 5 live; 8 new + 1 update to create |
| Managed Devins (child sessions) | A coordinator session starts child sessions, each on its own VM, and compiles results ([docs](https://docs.devin.ai/work-with-devin/advanced-capabilities#managed-devins)) | Q2 lanes, Q5 document fan-out, S/4 wave one-per-object | used |
| Devin Review | Automated PR review; posts bugs and security findings as PR comments and a check status ([docs](https://docs.devin.ai/work-with-devin/devin-review)) | every PR; QA prep checks open findings | on (it reviewed every demo PR) |
| Security Swarm / code scans | Agentic security scan with threat modelling, evidence and confidence per finding; scan profiles; schedulable from Automations ([docs](https://docs.devin.ai/work-with-devin/security-swarm)) | AppSec beat; `security/scan-profile.md` | profile text ready; scan not started (cost) |
| DeepWiki and Ask Devin | Generated wiki and architecture diagrams for a connected repo; Q&A grounded in it ([docs](https://docs.devin.ai/work-with-devin/deepwiki)) | architect beat; ABAP onboarding (`docs/s4/deepwiki.md` in abap2xlsx) | available on connected repos |
| Devin for migrations | Playbook-driven, parallel migration work: framework upgrades, language and code modernisation ([docs](https://docs.devin.ai/use-cases/migration-modernization)) | S/4HANA wave remediation on cogdeasy/gsk; Spring Boot 1.5 -> 2.7 ADR on WebAPI | playbook ready |
| Devin API | REST API to start and manage sessions with a playbook, tags and structured output ([docs](https://docs.devin.ai/api-reference/overview)) | `api/start_audit_pack.sh` starts the audit pack from GSK tooling | script ready; needs a service-user key |
| Devin Oncall | Responders for Slack channels or PagerDuty incidents, incident investigation | SRE beat | not set up in this org (Oncall setup incomplete); the demo uses a webhook automation instead |
| Integrations / MCP | Jira (native + Atlassian MCP), GitHub, Slack, PagerDuty, Datadog etc. | Jira and GitHub in use | Atlassian MCP on v1 endpoint: move to v2 |
| Knowledge | Org notes injected when relevant | not required | — |

## Skills, plugins, rules: how they fit

- **Skill**: a `SKILL.md` with a name and description. Devin sees the list of available skills at
  session start and reads the full file only when it invokes one. Repo skills live in
  `.agents/skills/<name>/SKILL.md` (recommended; `.devin/skills/` and others also scanned)
  ([docs](https://docs.devin.ai/product-guides/skills)).
  In this demo: `gxp-evidence-pack` and `test-engineer` in the WebAPI repo,
  `abap-s4-readiness` in abap2xlsx. They carry the *how* for one repo.
- **Playbook**: the *what and in which order* for one lane, attached to a session (often by an
  automation). A playbook step can say "use the repo skill `test-engineer`".
- **Rule**: always-on guidance. A repo's `AGENTS.md` is the rule file here (analysis only for
  ABAP; Java 8 and the Maven profile for WebAPI).
- **Plugin**: a package that bundles skills, rules, hooks and MCP servers, installed for the org
  from a marketplace (Devin official or the org's own repo) so every session gets them
  ([docs](https://docs.devin.ai/product-guides/plugins)). For GSK: a `gsk-gxp` plugin could carry
  the evidence-pack and test-engineer skills, the "never sign, never merge" rule and the Jira MCP,
  once, for every repo - instead of copying `.agents/skills` into each repo.

Rule of thumb: repo-specific how -> repo skill; cross-repo policy -> plugin rule; ordered lane
procedure -> playbook; when it starts -> automation.
