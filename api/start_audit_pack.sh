#!/usr/bin/env bash
# Start the GSK audit pack for one change through the Devin API (v3).
# Needs: GSK_AUDIT_PLAYBOOK_ID, DEVIN_API_KEY (service user with session permissions),
#        DEVIN_ORG_ID (org-...). The request is built and sent by demo_ops.audit_pack.
# Usage: api/start_audit_pack.sh GSK-1 [--dry-run]
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v uv >/dev/null 2>&1; then
  exec uv run --quiet --project "$root" demo-ops-audit-pack "$@"
fi
PYTHONPATH="$root/src${PYTHONPATH:+:$PYTHONPATH}" exec python3 -m demo_ops.audit_pack "$@"
