# M9: supported Linux proof and official UI integration contract

Runtime source CODE:800841f229606c419dae67b0d6f794b9238676e9.
Design order read-only ref:658a8b99c4e47d59658ddf89e48508573bf52ab0.

## Linux Python3.12: NOT_RUN, concrete environment limit

2026-10-17 local inspection: `wsl --list --quiet` lists ONLY docker-desktop.
`py -0p` lists Windows3.14 and Store3.13, no Linux3.12 interpreter.
Docker's private runtime is not an authorized Linux development environment;
it was not entered, started or restarted. Do not substitute Windows proof for Linux.
Work must execute this on its independent Linux3.12 mock-only worker, using full
Git history (the unchanged native portable helper needs pinned c338ba3 Git objects).

Requirements blob at source HEAD:11c43eb2daa3ba2d0d54881d41bb66daa1098b3b.
The actual Linux workflow uses Python3.12 and pip install -r requirements.txt;
its Windows smoke separately installs pytest/tzdata. Runtime requirements contain
ranges, so installing the same file does NOT prove identical resolved versions.
Record Python plus importlib.metadata versions for pytest, tzdata, requests,
pydantic, pandas, exchange-calendars; do not dump credential-bearing environments.

Commands after Work pins the actual M9 proof commit from Issue12 in a clean clone:

```bash
python3.12 -m venv /tmp/agentra-monitor-m9-venv
/tmp/agentra-monitor-m9-venv/bin/python -m pip install -r requirements.txt tzdata
M9_TMP=$(mktemp -d /tmp/agentra-monitor-m9.XXXXXXXX)
export TMPDIR="$M9_TMP" TEMP="$M9_TMP" TMP="$M9_TMP"
export PYTHONPYCACHEPREFIX="$M9_TMP/pycache" PYTHONHASHSEED=0
export TRADING_AGENT_PYTEST=1 TRADING_AGENT_PYTEST_ROOT="$M9_TMP/runtime"
export TRADING_MODE=mock PRODUCTION_WRITE_AUDIT_MODE=full
export MONITOR_M9_EVIDENCE="$M9_TMP/full.json"
unset OPENROUTER_API_KEY OPENAI_API_KEY KIWOOM_APP_KEY KIWOOM_APP_SECRET
/tmp/agentra-monitor-m9-venv/bin/python -m pytest tests/test_work_monitor_m9_offline.py -q --assert=plain -p no:cacheprovider --junitxml="$M9_TMP/offline.xml"
```

Optional full-mod1 portable replay (NOT a Windows-native replacement):

```bash
/tmp/agentra-monitor-m9-venv/bin/python -m pytest tests/test_work_monitor_m9_native.py -q --assert=plain -p no:cacheprovider --junitxml="$M9_TMP/full.xml"
```

That non-Windows branch delegates to the original gate's pinned BASE extraction
and full same-host comparison. It was prepared, NOT executed locally. No skip or
expected-value relaxation. Preserve failed-session logs/JUnit externally; successful
pytest basetemp cleans normally. Never clean another command's TEMP namespace.

## UI source reconciliation: proposal only

Actual consumer:apps/api/adapters/patch_notes.py:10 RELATIVE_PATH points to
docs/trading_agent_patch_notes_detailed_update/patch_notes.json.
Adapter blob:28c95f4e40a873489215ebedc1e1598dc91ee42a.
At efdab64f this store has schema_version/generated_for/entry_count/entries,
288 entries. Corresponding Markdown is the sibling patch_notes.md.
Own proposals are NOT automatically UI-visible, and cannot be called synchronized
official notes. Work must append M9's paired proposal in both official formats,
preserve every existing entry/order, recalculate entry_count and run the real API
bounded-reader/patch-note tests on its assembled candidate. This lane modifies
neither official store, API adapter nor shared gate/CI. No ZIP upload in CI.
