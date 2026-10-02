#!/usr/bin/env bash
# Stops the stack. Pass -v to also drop the database volume (next start re-seeds Eunomia).
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose down "$@"
