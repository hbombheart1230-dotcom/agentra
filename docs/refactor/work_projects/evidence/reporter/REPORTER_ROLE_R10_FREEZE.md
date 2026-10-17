# Reporter role — R10 freeze packet (REPORTER_LOCAL_READY_FOR_INTEGRATION / WAITING_ON_WORK; role status PARTIAL_WITH_BLOCKERS until Work acceptance)

> R-11 update: test matrix, 3.14 / FastAPI results, hygiene prevention and Work findings R11-F1/F2 are in `R11_CHECKPOINTS.md` (R10 suites now 54 PASS / 0 SKIP).

Current pushed SHA: see branch head after this file (previous: 359ef16). BASE d773709. No main merge.

## Totals
- Moved: 12 relocated modules (R-1/R-2), 3 decompositions (R-3), 313 bodies / 23 facade paths / 41 owner files (R-4..R-9).
- Retained in facades: 47 RETAIN_FACADE (READ_ONLY 34, WRITER 4, CLOCK_LOG_ENV 3, MODULE_IDENTITY 4, REDEFINITION 2) — 47/47 COVERED by offline BASE-vs-HEAD contracts (r10a_retained_coverage.json); relocation NOT authorised.
- Authority exclusions: 22 (r10d_authority_map.json; 21 + _broker_order_status_payload). No test invokes them.
- controlled_mock_lane_report: retained (Work decision).

## Registered API path consumers
apps/api/adapters/safe_reports.py, trade_bundle.py, llm_artifacts.py, operator_summary.py, services/trade_timeline_projection.py, routers/trades.py (REPORTER_ROLE_FREEZE_PACK_R8.md). safe_reports exercised against BASE- and HEAD-produced artifacts (R10-002).

## Test matrix (local, this session)
| Suite | Windows Py 3.13.14 | `-O` | Linux Py 3.12 | Py 3.14 |
|---|---|---|---|---|
| seed/scope `test_work_reporter_seed_migration.py` | 72 PASS | PASS (R8) | Work: PASS (R9 review) | NOT_RUN (no pytest) |
| moved bodies `test_work_reporter_r4_facade_bodies.py` | PASS (1608 at R-9) | PASS | Work: PASS | NOT_RUN |
| `test_work_reporter_r8_read_contracts.py` | 3 PASS | PASS | Work: PASS | NOT_RUN |
| `test_work_reporter_r8_read_via_callback_parity.py` | 25 PASS | PASS | NOT_RUN (post-fix) | NOT_RUN |
| `test_work_reporter_renderer_bytes.py` | 54 PASS | PASS | NOT_RUN | NOT_RUN |
| `test_work_reporter_r10_retained_io_contracts.py` | 53 PASS / 3 SKIP* | PASS | NOT_RUN | NOT_RUN |
| `test_work_reporter_r10_artifact_parity.py` | 3 PASS | PASS | NOT_RUN | NOT_RUN |
| `tests/test_p152_facade_symbol_ledger.py` (v1@BASE + v2) | PASS | PASS | Work: PASS | NOT_RUN |
| FastAPI tests (tests/apps/api) | NOT_RUN: fastapi absent; needs isolated venv with requirements.txt fastapi>=0.116.0, httpx>=0.28.0, uvicorn>=0.34.0 (download approval) | | | |
\* the 3 callback readers inside the generic parametrisation; each has a dedicated fixture test (asserted).
Combined run of all role suites at 359ef16-era code: 1819 PASS / 3 SKIP / 1 FAIL — the FAIL was the scope test catching the accidental `%SystemDrive%` folder, fixed in R10-003.
Negative mutations (all detected): R-4 lazy/AST negatives; R8 `day > best`, reason literal, `build_daily_trade_index` -> {}; renderer `'\n'.join` -> CRLF; R10 jsonl order reversal, injected KeyError, trade_report* newline mutation; input-timestamp +1 min.
Pre-existing (identical at BASE): 8 UEF2A (missing operational files), UEF5_1 x2 Windows (1 Linux).

## Required CI list (proposal for Work; workflows unchanged on this branch)
Add to the required Linux job (fetch-depth: 0, needs commits d773709 and eeb742a): the 7 role suites above + tests/test_p152_facade_symbol_ledger.py. Windows job: same list; R10 suites spawn subprocesses with the full inherited environment and temp cwd.

## Outstanding (Work-owned / decisions)
P15-WORK-001 shared T3 guard (P1) + agent-package allowlist + CI wiring; UI patch-note publication (source: apps/api/adapters/patch_notes.py -> docs/trading_agent_patch_notes_detailed_update/patch_notes.json; proposal NOT_PUBLISHED); any I/O or authority relocation needs a narrow Work decision.

## Recovery / artefact policy
Resume from the branch head; ledgers are the source of truth (r4_facade_ledger.json, facade_symbol_ledger_v2.json, r8_function_triage.json, r10a_retained_coverage.json, r10d_authority_map.json). Tests write only to pytest tmp dirs (session-isolated basetemp); successful temp output is discarded by pytest; no failure bundles kept. Changed-files ZIP + SHA-256 manifest outside the repo.

## Next action by owner
Work: shared candidate (guard + allowlist + CI list) and independent acceptance; Codex: Monitor (unchanged); Claude: respond to new SHA-bound Reporter findings only.
