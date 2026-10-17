# Reporter R8 checkpoints (issue-ready; this session has no GitHub write access — no credential scraping)

## R8-000 — integrity (START_SHA 8ce327ecc71c4c92074c1fa5fb6f00428ba9279b, clean tree, origin = hbombheart1230-dotcom/agentra)
- Ledger: 264 moves, 264 unique (facade,function) pairs, expected_moves 264; 29 owners, max 324 LOC; every moved name still defined exactly once in its facade.
- UEF pre-existing check (same interpreter Python 3.13.14): `git archive d773709` tree and HEAD fail the IDENTICAL 10 tests (8 test_uef2a_forward_policy_contract, 2 test_uef5_1_clean_evidence_registry); cause = missing operational data, e.g. reports/trades/2026-05-15/.../post_exit_shadow_recap.json (FileNotFoundError). Not Reporter-caused; not waived, just reproduced.
- REVIEW_ACK: F-R7-01 (P1) acknowledged — T3 shared-contract fix and cross-role coordination belong to Work on a separate integration proposal; Reporter branch will not carry or bypass it. My earlier T3 v4 diff is superseded input only; note R-8 adds owners named *_r8_bodies_01.py which the historical bodies_0N rule also matches. F-R7-02 acknowledged (Work: stage Monitor parts only on a combined candidate; add BOTH Reporter tests to CI). F-R7-03 fixed: proposed_patch_note.json sources now point to REPORTER_ROLE_HANDOFF_R7.md + REPORTER_R4_FACADE_BODIES.md; still a proposal, UI source not verified.

## R8-001 — C1 triage + C2 safe moves
- C1: scripts/refactor/work_reporter_triage.py -> r8_function_triage.json: 91 remaining non-trivial functions, rows with real effect calls (AST), authority names, module identity, callers, disposition. Result: 23 SAFE_MOVE_CANDIDATE (scanner token false positives: no direct I/O/authority call; any reads happen in late-bound facade helpers), 47 RETAIN_FACADE (direct read/write/time/log calls, module identity, redefinitions), 21 NEEDS_AUTHORITY (LLM routing/retry/model, broker/truth/execution names).
- C2: 22 of 23 moved (`_broker_order_status_payload` excluded by name: broker). Extractor gained `--only` (token filter waived only for triaged names; all other eligibility checks + unparse round-trip self-check kept; earlier triage reasons preserved in ledger). Owners: libs/agents/reporter/{narrative,read_models}/<module>_r8_bodies_01.py (9 files). MOVES total 286.
- FACADE_LOC (after R-8):
     544 libs/reporting/trade_read_model.py
     411 libs/reporting/trade_explain.py
    1225 libs/reporting/trade_bundle_assembly.py
     783 libs/reporting/trade_lifecycle_builder.py
     466 libs/reporting/single_trade_report.py
     666 libs/reporting/reporter_analysis.py
     536 libs/reporting/post_exit_shadow_recap.py
     562 libs/reporting/symbol_trade_report.py
     575 libs/reporting/agent_pipeline_trace.py
    5768 total
- TESTS: tests/test_work_reporter_r4_facade_bodies.py 1470 PASS (286 moves); seed/scope + p152 ledger/ABI/R3 + T1/T2 gates + 40 consumer files 1397 PASS / 0 FAIL (fastapi-dependent tests excluded: NOT_RUN). Closed scope set extended by explicit R8_OWNER_FILES; ledger test pins 286 moves and exact pairs.
- BLOCKERS: 47 RETAIN_FACADE + 21 NEEDS_AUTHORITY rows (see triage JSON); controlled_mock_lane_report ownership (Work); shared T3 (Work, F-R7-01).
- NEXT_READY: (1) C1-D read-only I/O characterization for RETAIN_FACADE rows with temp-dir parity fixtures; (2) C3 producer/consumer/DTO map + offline byte fixtures; (3) C4 trade_report/ subtree classification; (4) controlled_mock_lane_report consumer evidence for Work.
- PATCH_NOTES: NOT_PUBLISHED (proposal only). BUDGET: UNKNOWN.

## R8-002 — C4 inventory + R-9 moves (START_SHA 523dd9ac227a33eb9e5aa9bed82957e4111c5d9b)
- C4: scripts/refactor/work_reporter_inventory.py -> r8_file_inventory.json, all 500 libs/reporting files: RESEARCH_EVALUATION 236, SHARED_CONTRACT 108 (earlier-pass parts pinned by R3/T1/T2 ledgers, incl. trade_report/**), OPS_SCHEDULER 42, EXTERNAL_AUTHORITY 39, REPORTER_RETAINED 30, REPORTER_FACADE 23, REPORTER_CANONICAL 21, BLOCKED_WITH_PROOF 1 (controlled_mock_lane_report; decision input CONTROLLED_MOCK_LANE_REPORT_DECISION_INPUT.md).
- R-9: 27 pure bodies (default filter, no --only) from intraday_trade_reports (12), trade_report_common (9), symbol_read_model (6; truth-token bodies stay). MOVES total 313. LOC after:
 1576 libs/reporting/intraday_trade_reports.py
  100 libs/reporting/trade_report_common.py
  285 libs/reporting/symbol_read_model.py
 1961 total

- TESTS: proof suite 1608 PASS (313 moves); seed/scope + p152 + T1/T2 + consumers 1098 PASS / 0 FAIL. Closed set R9_FACADE_FILES/R9_OWNER_FILES; ledger test pins 313.
- NEXT_READY: (1) C1-D temp-dir characterization of RETAIN_FACADE rows; (2) C3 offline byte fixtures for markdown/JSON renderers incl. CRLF; (3) C6 read-only Strategist inventory once Reporter safe scope exhausted.
