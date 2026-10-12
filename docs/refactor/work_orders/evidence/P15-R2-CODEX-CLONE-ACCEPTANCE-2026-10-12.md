# P1.5.2 isolated clone acceptance — 2026-10-12

Checked source: `02d66710f5ea4feb1d3e2f683b63a59403031976` (`refactor/p1.5`).
Original `C:\\Agentra` was not modified. Clone: `C:\\AgentraEvidence\\p152_local_clone_02d6671`.

## Environment

- Python: `C:\\Agentra\\venv\\Scripts\\python.exe`
- Version: 3.14.2
- pytest: 9.1.1
- FastAPI: 0.142.2
- Clone retained Git history; it was not a git-archive-only test tree.
- Live writer processes were observed only against `C:\\Agentra`; no process targeted the clone.

## Tests and audit

- P1.5.2 selection: **295 passed, 1 skipped**, exit 0.
- Clone write-audit: **zero CREATED/MODIFIED/DELETED markers**; clone Git worktree remained clean.
- Full `pytest -q`: **NOT PASS / incomplete**. FastAPI collection errors were resolved with the venv. The first failure was the pre-existing out-of-scope API test `tests/apps/api/test_isolation.py::test_api_routes_are_get_only` (`11 passed, 1 failed` at `6.10s` under `--maxfail=1`). A subsequent unrestricted run reached 50% before its process terminated without a pytest summary; it is not counted as complete.
- Logs: `C:\\AgentraEvidence\\p152_selected_clone_02d6671.log` and `C:\\AgentraEvidence\\p152_full_clone_02d6671.log`.

## Snapshot parity

No independently frozen before/after Markdown/JSON/JSONL copies or LLM trace were present under `C:\\AgentraEvidence`; no live `reports/` or `data/` content was used. Actual parity remains **BLOCKED / NOT RUN**.

## Façades and scope

Keep/defer the three façades as the ABI/patch surface: 2,761 / 2,658 / 636 LOC. No new Owner extraction. No API, Scanner, UEF, Step5B, execution, LLM, Docker, Q12, or live-data changes.

Remaining BLOCKED items are real snapshot/LLM provenance and complete clean full-suite totals. P1.5.3 remains unauthorized.
