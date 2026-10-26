#!/bin/bash
# RF-007 independent E2E peer: REAL read-only observability API (apps/api) over a SYNTHETIC repository root + Vite dev server + Playwright smoke.
# Usage (repo root checked out at the SOURCE_SHA): bash rf007_e2e_runner.sh <repo_root> <python>
set -e
REPO=$1; PY=${2:-python}
$PY "$REPO/docs/refactor/work_orders/evidence/run103_boundary_scripts/rf007_fixture_root.py" "$REPO" /tmp/rf007_root   # fixture dates must be inside the UI default 45-day window
export OBSERVABILITY_REPOSITORY_ROOT=/tmp/rf007_root OBSERVABILITY_REPORTS_ROOT=/tmp/rf007_root/reports OBSERVABILITY_LOGS_ROOT=/tmp/rf007_root/logs OBSERVABILITY_STATE_ROOT=/tmp/rf007_root/state
(cd "$REPO" && PYTHONPATH=. $PY -m uvicorn apps.api.main:create_app --factory --host 127.0.0.1 --port 8000 --log-level warning &)
(cd "$REPO/apps/web" && npm ci --no-audit --no-fund && npx vite --host 127.0.0.1 &)
sleep 10
(cd "$REPO/apps/web" && BROWSER_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome node e2e/smoke.mjs && BROWSER_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome node e2e/public-profile.mjs)
