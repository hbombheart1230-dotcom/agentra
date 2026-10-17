# Reporter role-freeze evidence pack (R8) — for Work integration and the independent audit

STATUS: PARTIAL_WITH_BLOCKERS (safe structural scope exhausted under current authority). Audit target = branch head after this file.

## Structure (counts from ledgers)
- R-1/R-2: 12 pure modules relocated (identity shims), R-3: 3 oversize modules decomposed (11 owners, import-only facades with BASE attributes restored).
- R-4..R-9: 313 function bodies, 23 facade paths, 41 owner files in libs/agents/reporter/{narrative,read_models} (<=350 LOC), R3 facade-injection pattern.
- Ledgers: r4_facade_ledger.json (moves + per-facade skipped reasons), facade_symbol_ledger_v2.json (current head; v1 untouched), r8_function_triage.json (91 rows), function_blockers.json, r8_file_inventory.json (500 files), r8_flow_map.json, report_inventory.json.

## Reporter tests to wire into required CI (Work-owned workflows)
tests/test_work_reporter_seed_migration.py, tests/test_work_reporter_r4_facade_bodies.py, tests/test_work_reporter_r8_read_contracts.py, tests/test_work_reporter_r8_read_via_callback_parity.py, tests/test_work_reporter_renderer_bytes.py, plus modified historical-preserving tests/test_p152_facade_symbol_ledger.py. They need git history containing d773709 and eeb742a (fetch-depth 0).

## API artifact consumers (by path, not import) — apps/api
adapters/safe_reports.py (reports/ai_trade_summary, ai_trade_report, quant_trade_diagnosis, post_exit_shadow_recap, strategist_summary), adapters/trade_bundle.py (ai_trade_summary_input.json, entry/hold/exit.json, _health.json, _provenance.json, quant_trade_diagnosis.json, evaluation_exclusion.json), adapters/llm_artifacts.py (ai_trade_report/summary llm responses), adapters/operator_summary.py (daily_summary.json), services/trade_timeline_projection.py (entry/hold/exit.json), routers/trades.py (reports/{report_id}). None of these file names, paths or writers changed in R-1..R-9 (writers/LLM/report-generation code untouched).

## Intentional remaining wrappers / retained code
- Facade wrappers for all 313 moves (ABI: names, signatures, defaults, docstrings, module identity of facades).
- RETAIN_FACADE 47 (direct reads/writes/time/log, module identity 4, redefinitions 2), NEEDS_AUTHORITY 21 (LLM routing/retry/model, broker/truth/execution), 357 thin delegations, 94 short helpers.
- controlled_mock_lane_report: retained at path (Work decision: Reporter presentation/read adapter).
- trade_report/** and *_parts/**: earlier-pass owners pinned by R3/T1/T2 historical owner paths (SHARED_CONTRACT).

## Known failures / not run
- Shared T3 `test_t3_changed_paths_contain_no_authority_surface`: FAIL on branch by design until Work's guard (P15-WORK-001).
- Shared agent-package equality gates (p166/p167/p171/p173): FAIL until Work registers reporter packages.
- Environment: 8 UEF2A (missing operational files) + 2 UEF5_1 on Windows (1 also on Linux; 1 Windows-only CRLF hash) — identical at BASE.
- NOT RUN: hosted CI, full pytest, native Python 3.12/3.14 here, fastapi tests, real LLM/persisted parity.
