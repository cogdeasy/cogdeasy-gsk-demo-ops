#!/usr/bin/env bash
# Cold start: build the WAR (unless SKIP_BUILD=1), build the runtime image, start the stack and wait for ATLAS.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
cd "$here"
port="${PROXY_PORT:-8090}"
start=$(date +%s)

if [ "${SKIP_BUILD:-0}" != "1" ] || [ ! -f webapi/WebAPI.war ]; then
  scripts/build-webapi.sh
fi
docker compose up -d --build

echo -n "waiting for WebAPI"
until curl -fs "http://localhost:$port/WebAPI/info" >/dev/null 2>&1; do echo -n .; sleep 5; done
echo
until curl -fs "http://localhost:$port/WebAPI/source/sources" | grep -q EUNOMIA; do sleep 3; done
curl -fs "http://localhost:$port/WebAPI/info"; echo
echo "stack ready in $(( $(date +%s) - start ))s: http://localhost:$port/atlas/"
