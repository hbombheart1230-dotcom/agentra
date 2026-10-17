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

## R8-003 — Work review ACK (reviewed 523dd9a) + read contracts (START_SHA dd0b378b46dff0c2ecf6699a4b08776fd4412b76)
- REVIEW_ACK P15-WORK-001 (=F-R7-01, P1): Work-owned shared guard; T3 v4 superseded; Reporter branch carries no T3 change. 
- REVIEW_ACK P15-WORK-003 (P2): new `tests/test_work_reporter_r8_read_contracts.py` — pinned BASE function (exec'd on live facade globals) vs current wrapper on temp-dir inputs (valid, malformed, empty, CRLF, missing, directory) for reporter_analysis._latest_day and trade_explain._latest_day (read path + mid-call `_utc_day` re-patch sequence) and trade_read_model.load_reporter_snippet_for_run (5 callback behaviours incl. raising, 3 run ids; read path + call order). 3 PASS; negative mutations (`day > best` -> `<`; changed reason literal) both detected (1 FAIL each, reverted). Triage rows for all 22 R-8 moves relabelled MOVED_R8 / READ_VIA_CALLBACK; only the three above are fixture-proven, the other 19 are explicitly marked "transitive read characterization NOT yet fixture-proven".
- REVIEW_ACK controlled_mock_lane_report: Work decision recorded — Reporter presentation/read adapter, retained at path; no Q10/Q12 change.
- REVIEW_ACK proposed notes: JSON and MD synchronized to 313 moves / facade paths / owner files (counts computed from ledger), controlled-lane decision, T3-v4 supersession.
- UEF: Windows Python 3.13.14 shows 8 UEF2A + 2 UEF5_1. Second UEF5_1 = `tests/test_uef5_1_clean_evidence_registry.py::test_freeze_manifest_stays_11_of_11`: SHA-256 manifest MISMATCH of libs/reporting/evaluation/canonical/*.py bytes because this Windows checkout converts LF->CRLF (core.autocrlf); Linux checkout (Work, Python 3.12.14) does not reproduce it. First UEF5_1 (`test_uef5_package_is_stdlib_only_and_not_imported_by_production_or_core`) lists libs/reporting/evaluation/uef6/validation_replay.py on both. UEF2A x8: missing operational files under reports/trades/2026-05-15/... Identical at BASE archive and HEAD. Not Reporter-caused; not waived.
- NEXT_READY: (1) fixture-prove the remaining 19 READ_VIA_CALLBACK moves (same harness); (2) producer->DTO->renderer->API consumer map; (3) trade_report subtree symbol dispositions + duplicate/module-identity contracts.

## R8-004 — runtime parity for all 22 READ_VIA_CALLBACK moves (START_SHA ca1c6b3b55cf2dac74f8cff81ea4308384b63fa1)
- New `tests/test_work_reporter_r8_read_via_callback_parity.py`: every R-8 move, BASE body (exec'd on live facade globals) vs current wrapper on a temp report tree (trade dir with lifecycle_bundle/story_input, malformed json, jsonl) with 4 argument sets (root / day dir / missing / file; payload battery; real callables for Callable params). Equal outcome bytes or exception type+message, equal ordered list of `open`/`Path.read_text` reads, temp tree byte-identical afterwards (no writes). Wall-clock timestamps generated during the call (3 functions emit `ts`/`generated_at` via datetime.now) are normalised only when within 10 minutes of now; input timestamps compared verbatim. 23 PASS. Negative: forcing `build_daily_trade_index` owner to return {} -> 1 FAIL (reverted).
- All 22 triage rows now point to a runtime proof. P15-WORK-003 acceptance items covered: content/missing/malformed, exception equality, read path/order, mid-call re-patch (R8-003 for _latest_day), injected callback behaviour.
- NEXT_READY: (1) producer->DTO->renderer->API consumer map; (2) trade_report subtree symbol dispositions + duplicate/module-identity contracts; (3) C6 read-only Strategist/Scanner inventory after Reporter safe scope.

## R8-005 — C3 flow map, C4/C6 inventories, safe-scope status (START_SHA 93943097f5627a423e5150e62b9634d63118a51b)
- C3: scripts/refactor/work_reporter_flow_map.py -> r8_flow_map.json: static import closure per report producer/API consumer with inventory categories and renderer modules; modules shared by >=4 entry points listed (duplicate-pipeline signal). Limits: several scripts/*.py are thin launchers (closure 0 by static import), apps/api reads artifacts by path (no static libs.reporting import found) -> those links stay UNVERIFIED; no report deleted/disabled.
- C4 inventory (R8-002) unchanged; trade_report/** = SHARED_CONTRACT (earlier-pass parts pinned by R3/T1/T2 owner paths; moving them would rewrite historical contracts) -> retained with reason.
- C6: c6_strategist_scanner_readonly_inventory.json (read-only): strategist runtime 44 files/5594 LOC (5 shims), agents/strategist 8/761, scanner runtime 29/3171 (16 shims), agents/scanner 20/2662; strategist_node 4053 LOC, scanner_node 1222 LOC. No branch/code started; Work must publish the next whole-role assignment.
- ROLE STATUS: PARTIAL_WITH_BLOCKERS. Remaining Reporter rows: 47 RETAIN_FACADE (direct read/write/time/log calls, module identity (4), redefinitions (2): each needs a temp-dir parity fixture AND an explicit decision to relocate I/O-bearing code), 21 NEEDS_AUTHORITY (LLM routing/retry/model, broker/truth/execution names, incl. `_broker_order_status_payload`), shared T3 guard (Work, P15-WORK-001), UI note publication (Work). Safe structural moves under the current authority are exhausted.
- NEXT_READY (need a decision or Work): (1) approve I/O-bearing RETAIN_FACADE relocation scope (fixtures ready to extend from R8-004 harness); (2) Work shared candidate: guard + both/three Reporter tests in CI; (3) independent audit of the R8 final SHA.

## R8-006 — renderer byte parity (START_SHA 7336bc1cb1ad954fe1370dd30210b4d6739fb6cc; Work R9 review of dd0b378: no new blocker)
- New `tests/test_work_reporter_renderer_bytes.py`: every moved renderer-like function (53 of 313: markdown/render/_md/lines/text/label/summary) — BASE body on live facade globals vs current wrapper, 3 report-shaped payloads (incl. CRLF inside input text, Korean, malformed types); exact UTF-8 bytes / JSON bytes / exception type+message, no line-ending normalisation. 54 PASS. Negative: changing `'\n'.join(lines)` to `'\r\n'.join(lines)` in reporter_analysis `_to_markdown` owner -> 1 FAIL (reverted).
- ACK Work R9 review: READ_VIA_CALLBACK vs pure formatting distinguished in triage (R8-003/004); notes reconciled (R8-003). The C6 read-only inventory from R8-005 is kept only as raw input; per Work, no further Strategist inventory until Reporter role freeze.
- NEXT_READY: (1) role-freeze evidence pack (counts, retained/blocked list, tests list for CI wiring) for Work; (2) API DTO/path consumer map completion (apps/api reads artifacts by path); (3) decision-dependent: I/O-bearing RETAIN_FACADE relocation.

## R8-007 — role-freeze pack (START_SHA c24d683a7a28990ed05e525f3b1555d8a2bd9d5a)
- REPORTER_ROLE_FREEZE_PACK_R8.md: counts, tests for CI wiring, API artifact consumer map (path-based), intentional wrappers, known failures. Safe structural scope exhausted; remaining work is decision/Work-owned.
- NEXT_READY (decision/Work): shared guard candidate + CI wiring; independent audit of final SHA; optional I/O-bearing RETAIN_FACADE relocation scope.
