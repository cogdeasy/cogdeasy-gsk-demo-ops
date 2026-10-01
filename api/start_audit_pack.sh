#!/usr/bin/env bash
# Start the GSK audit pack for one change through the Devin API (v3).
# Needs: DEVIN_API_KEY (service user with session permissions), DEVIN_ORG_ID (org-...).
# Usage: api/start_audit_pack.sh GSK-1 [--dry-run]
set -euo pipefail
key="${1:?usage: $0 <GSK key> [--dry-run]}"
playbook="playbook-${GSK_AUDIT_PLAYBOOK_ID:?set GSK_AUDIT_PLAYBOOK_ID (uuid part)}"
body=$(python3 - "$key" "$playbook" <<'PY'
import json, sys
key, playbook = sys.argv[1], sys.argv[2]
print(json.dumps({
    "title": f"GSK audit pack {key}",
    "prompt": f"Build the inspection-readiness pack for {key} on cogdeasy/cogdeasy-gsk-ohdsi-webapi. Read-only.",
    "playbook_id": playbook,
    "repos": ["cogdeasy/cogdeasy-gsk-ohdsi-webapi", "cogdeasy/cogdeasy-gsk-demo-ops"],
    "tags": ["gsk-demo", "audit"],
}))
PY
)
if [[ "${2:-}" == "--dry-run" ]]; then echo "$body"; exit 0; fi
curl -sS -X POST "https://api.devin.ai/v3/organizations/${DEVIN_ORG_ID:?}/sessions" \
  -H "Authorization: Bearer ${DEVIN_API_KEY:?}" -H "Content-Type: application/json" -d "$body"
