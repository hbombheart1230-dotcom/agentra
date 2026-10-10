# P1.5.2 Prelocal 004 — Windows GitHub-hosted Contract Verification

Date 2026-10-10
Code SHA `b12795b6e651d780d7132ffd4ecf9f62552d9bf7`, branch `refactor/p1.5`
CI https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38036845579 — workflow has one failed diagnostics job, NOT an overall all-green verdict.

## Windows clean runner results
- Windows hosted strict owner lock / archive path / Operator UI path / runtime root path / subprocess tests:
  **123 passed, 0 failed**, 1 warning, in 5.95s.
- Separate Windows hosted API route get-only plus Scanner canonical rank test group:
  **11 passed / 2 failed**, 1 warning, in 3.89s.
- Failed cases exactly:
  `tests/apps/api/test_isolation.py::test_api_routes_are_get_only` (no FastAPI route matches `APIRoute`);
  `tests/test_scanner_rank_plumbing_fix.py::test_canonical_scanner_rank_for_runner_up_symbol` (observed `041190` vs expected `000660`).
- JUnit for first Windows group: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38036845579/artifacts/11663828748.
- **Unresolved API and Scanner failures reproduce on both Linux and GitHub-hosted Windows.** Not presumed harmless. Source files/test source originally present and blob-identical at before-R2 code SHA `2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c`; cross-module interactions remain unproven.

## Classification and safety
- Linux strict lock and Windows-style path/test errors are environment/platform sensitive, based on a complete 123-test passing targeted Windows group. This does NOT prove local production environment parity.
- API FastAPI/route recognition and Scanner rank are separate recorded cross-platform defect candidates outside P1.5.2 Reporting source. Do not fix by touching Scanner rank/scoring, trading topology or API routing as part of P1.5.2 without dedicated authorization and guard baselines.
- Clean Windows runner has no user Kiwoom credentials or user report/SQLite data; `C:\Agentra` local read-only reports, actual LLM messages, full Windows repository pytest and independent Claude/Codex remain NOT RUN.
- Job is retained as deliberate `workflow_dispatch` diagnostic after observation (not an automatic red regression job on future non-runtime commits). Preserve negative evidence.
- P1.5.2 OPEN, P1.5.3 NOT AUTHORIZED.
