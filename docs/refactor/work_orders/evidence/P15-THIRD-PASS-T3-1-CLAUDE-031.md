# P15 Third Pass T3.1 — Owner structural cleanup (Claude)

BASE `9e312c9fec0d4eb09f0b729456509b0469c7470f`; FEATURE (code) `ab8563b251c7a2fc8b0409fde36a05bc10918f04`. Codex verdicts accepted at start: analyzer P1, SYSTEMDRIVE P1 and **Write Containment P1 CLOSED**; strict SHA-256 manifest PASS; T3.1 GO; T3.5 CONDITIONAL_GO; NTFS settle causality P2 UNRESOLVED; failed-session evidence confidentiality P2 OPEN; REAL_REPORT_PARITY_BLOCKED OPEN; Wave D NOT STARTED.

Scope: eight Owner functions, their five orchestrator call sites, the T3.1 ledger/gates/matrix and documentation. **No** change to Supervisor/Executor/Broker, Step5C CAS/UNKNOWN quarantine, canonical Scanner ranking, `main`, live `C:\Agentra`, Q12 worktrees, Docker or scheduler; no real Broker/LLM; no T3.5/T4/T5/Wave D.

## 1. Inventory and decisions

Starting candidates (matrix at `a5cffb9`, regenerated at BASE-compatible rules): 30 CONTRACT_CANDIDATE, 54 RENAME_CANDIDATE modules; 43 Owner functions with positional output arity >= 8. The numbers are *review candidates*, not defects. Every candidate function was classified by actual input/output, the single production caller, use-time `facade` binding and authority proximity.

| Decision | Functions | Rule |
|---|---|---|
| NAMED_RESULT + SEMANTIC_RENAME (done) | 8 | arity 22-30, one orchestrator caller each, effect-free, facade symbols unchanged |
| SAFETY_LOCK_DEFER | scanner score policy / remaining score-feature projection, Commander decision overlay / context / open-position assessment, Monitor signal score / exit decision | canonical ranking, decision order or risk path; needs its own authority review and ranking/decision differential |
| NAMED_RESULT_DEFERRED | remaining reporter/UI/runtime Owners (20 modules) | same mechanical recipe, deferred to keep T3.1 inside 6-8 evidence-backed functions |
| SEMANTIC_RENAME_DEFERRED | generated names without a paired contract change (25 modules) | name-only change has no ABI/readability payoff alone |

Full per-module table: `docs/refactor/p1_5_third_pass_t3_1_candidate_decisions.json`.

## 2. Changed Owner functions (before/after)

Records are `typing.NamedTuple` subclasses whose field order equals the legacy tuple order; call-site unpacking is unchanged (positional ABI, shallow immutability only, same aliasing as a tuple).

| # | Before (generated name) | After | Record | Arity | Owner module |
|---|---|---|---|---|---|
| 1 | `memory_feedback_best_playbooks_commander_memory_policy_r` | `rebuilt_memory_feedback_facts` | `RebuiltMemoryFeedbackFacts` | 30 | `libs/reporting/trade_memory_projection_parts/memory_feedback_rebuild.py` |
| 2 | `brief_market_active_exit_axis_avg_price_monitor` | `brief_position_exit_axis_evidence` | `BriefPositionExitAxisEvidence` | 24 | `apps/operator_ui/data_access_brief_market_sections.py` |
| 3 | `brief_monitor_decision_reason_execution_quality` | `brief_decision_report_linkage` | `BriefDecisionReportLinkage` | 24 | `apps/operator_ui/data_access_brief_monitor_sections.py` |
| 4 | `brief_monitor_canonical_active_exit_axis_canonical_ave` | `canonical_monitor_snapshot_view` | `CanonicalMonitorSnapshotView` | 24 | `apps/operator_ui/data_access_brief_monitor_sections.py` |
| 5 | `signal_feature_average_volume_breakout_chase_extension` | `volume_pullback_breakout_gate_features` | `VolumePullbackBreakoutGateFeatures` | 24 | **moved** to existing `libs/runtime/monitor/signal_features_breakout_volume_gate.py` |
| 6 | `scan_feature_adx14_adx_component` | `candidate_score_components` | `CandidateScoreComponents` | 24 | `libs/runtime/scanner/score_feature_projection.py` |
| 7 | `decision_ctx_allowed_playbooks_applied_policy_meta` | `decision_policy_context` | `DecisionPolicyContext` | 22 | `libs/runtime/commander/decision_context_projection.py` |
| 8 | `decision_ctx_applied_policy_command_intent` | `applied_policy_command_context` | `AppliedPolicyCommandContext` | 22 | `libs/runtime/commander/decision_context_projection_applied_policy_command.py` |

Mechanics (AST-verified by the converter and by gate `test_t3_1_converted_functions_equal_their_pre_t3_1_bodies_modulo_record_wrapper`): signature (`ast.dump(args)`), every body statement and the returned expressions are identical to BASE; only the `def` name, `return (...)` -> `return Record(...)` and, for #6, the mechanical `if True:` scaffold dedent differ. Names resolve exactly as before (`facade.NAME` at use time; monkeypatch seams untouched).

Structural judgement: the 24-field record added 28 lines to `signal_features.py` (341 -> 369 LOC > 350 limit). Rather than weaken the limit, the function moved to the existing, cohesive sibling Owner `signal_features_breakout_volume_gate.py` (it is the volume/pullback/breakout *gate* computation; 130 -> 208 LOC); `signal_features.py` is now 294 LOC. No file was created, deleted or renamed.

## 3. Arity, named contracts, facade breadth (matrix regenerated at `ab8563b`)

| Measure | Before | After |
|---|---|---|
| CONTRACT_CANDIDATE modules | 30 | 27 |
| RENAME_CANDIDATE modules | 54 | 52 |
| `memory_feedback_rebuild.py` max unconverted arity | 30 | 0 |
| `data_access_brief_monitor_sections.py` | 24 | 6 |
| `data_access_brief_market_sections.py` | 24 | 19 |
| `decision_context_projection_applied_policy_command.py` | 22 | 0 |
| `decision_context_projection.py` | 22 | 15 |
| `signal_features.py` | 24 | 22 |
| `score_feature_projection.py` | 24 | 21 |
| Named-record functions (these modules) | 2 | 10 |

Facade symbol breadth was **not reduced** and is reported as measured: every converted function uses exactly the same `facade.*` symbol set (`facade_symbol_breadth.json`: 11/7/5/1/7/5/2/0 before = after, identical sets); the distinct set across `signal_features.py` + gate module is 33 before and after (module-level counts shift 33 -> 29 and 2 -> 9 only because the function moved).

## 4. Caller / ABI evidence

* Production callers: `libs/reporting/trade_memory_surface.py`, `apps/operator_ui/data_access_core.py`, `libs/runtime/intraday_monitor_signals.py`, `graphs/nodes/scanner_node.py`, `graphs/commander_runtime.py` — import/call rename only (bytes of unpacking statements unchanged); no `.field` access was introduced (a staged named-access migration needs a separate verified step).
* Gates (current-head, `tests/test_p159_current_owner_contract_gates.py`, 14 tests): T3 + T3.1 ledgers consistent with historical ledgers (field order == legacy outputs), record positional compatibility/equality/hash, object-payload alias identity and shared mutation, copy/deepcopy parity with tuples, shallow immutability, 350-LOC limit and import/authority restrictions on every Owner, original public signatures since each stage end, per-function facade symbols not increased, protected-path guard, and the two new T3.1 tests (AST body identity; old names gone from production, new names imported).
* Historical immutable gates (p156/p157/p158) and ABI/authority/symbol-ledger gates: **184 passed** at the final code state (historical p156/p157/p158 gates, current Owner gates incl. the two T3.1 tests, purity closure, matrix provenance, harness guards, ABI/authority, symbol ledger, parity-harness tests).

## 5. Behavioral differential (BASE x2 / FEATURE x2, strict containment)

Harness at `9e312c9` (T3-0.3) with `--containment strict` (default), `--pin-pid`, `--mode det`; sessions: BASE `9e312c9` x2, FEATURE `ab8563b` x2, parallel; interpreter: a clean venv from `requirements.txt` (fastapi/httpx installed, so `test_operator_ui.py` runs); 35 test files that exercise the five orchestrators; recorded functions: `build_trade_report_memory_surface`, `_build_operator_brief_sections`, `evaluate_intraday_entry_signal`, `scanner_node`, `_build_commander_decision` (the call sites of all eight Owners; names resolve identically in both trees).

| Item | Result |
|---|---|
| Sessions | 4/4 exit 0, **1253 passed** each; outcomes identical |
| Recorded calls | **474**: 469 BYTE_IDENTICAL, 5 JUSTIFIED_TOLERANCE, **0 REAL_MISMATCH, 0 UNRESOLVED** |
| Strict SHA-256 write containment | 4/4 PASS, 0 differences, `ISOLATION_VERDICT=PASS` |
| Per function | Commander `_build_commander_decision` 161/161 identical; Monitor `evaluate_intraday_entry_signal` 191/191; Operator Brief sections 39/39; Reporter memory surface 4/4; Scanner `scanner_node` 79 (74 identical + 5 justified) |

The 5 justified records are all rule `R-MEMORY-PACKET-ID` in `test_decision_trace_ledger...` (scanner node trace): one `memory_<20hex>` content-hash id embeds the session temp path and takes four different values in the four sessions (`b1 != b2`, `f1 != f2`), i.e. it is session-dependent and not BASE-vs-FEATURE dependent; the other four ids in that record are identical across all sessions. No tolerance was added or changed in this stage.

Owner execution proof (a call-count profile plugin over the same 35 files on the FEATURE tree, 1253 passed): `candidate_score_components` 165, `applied_policy_command_context` 161, `decision_policy_context` 161, `volume_pullback_breakout_gate_features` 86, `brief_position_exit_axis_evidence` 39, `brief_decision_report_linkage` 39, `canonical_monitor_snapshot_view` 39, `rebuilt_memory_feedback_facts` 4 — all eight converted Owners were actually executed. The Reporter memory path has only 4 calls in this suite (byte-identical); the scanner/commander/monitor/brief outputs (rank, signals, decisions, operator brief) are compared as whole orchestrator results (state/ranking/decision payloads), with no ranking, signal or decision difference.

Scope limits (not claimed): historical Second Pass / T1 / T2 parity evidence is **not** presented as T3.1 behavioral parity; real-report parity stays REAL_REPORT_PARITY_BLOCKED OPEN; no Operator Brief *byte* output comparison beyond the 39 recorded `_build_operator_brief_sections` results and `test_operator_ui.py` passing; ordered filesystem effects were not in scope (the eight Owners are effect-free; the profile and AST gates show no I/O tokens).

Full suite in the clean venv (`requirements.txt`, FEATURE tree): 7620 passed, 27 skipped, **34 failed + 2 errors** in `test_step5b_fix4`, `test_uef2a_*`, `test_uef5_1_*`, `test_uef5_2_*`, `test_uef6c_*`, `test_uef9_*`, `tests/apps/api/test_isolation.py`. The identical 34 failures + 2 errors reproduce on a pristine clone of BASE `9e312c9` in the same venv (34 failed, 181 passed on those files) - pre-existing, not caused by T3.1, and **not counted as PASS**.

## 6. Actual tree changes

0 files created, 0 deleted, 0 renamed; 1 function moved between existing sibling Owner modules; 7 Owner modules edited (+ the gate module); 5 caller modules edited (import/call names); ledger `docs/refactor/p1_5_third_pass_t3_1_owner_contract_ledger.json` and decisions file added; ownership matrix/tree overlay regenerated at `ab8563b`; gates extended (`tests/test_p159_current_owner_contract_gates.py`) and `scripts/refactor/p159_ownership_matrix.py` reads the T3.1 ledger when present. Canonical-vs-actual tree delta (matrix `tree_delta`): unchanged `delta: 0` for planned `[P]` files — no file was created merely to match the old design tree.

## 7. P2 follow-ups recorded (not implemented here)

* **Failed-session evidence confidentiality (P2 OPEN):** filename filtering alone cannot stop secret *content* being copied into a failed bundle. T3.1 used synthetic/mock fixtures only, all sessions PASSED (no bundle written), and only metadata-level JSON summaries are committed. The automatic copy scope is not widened; **metadata-only retention (manifests + hashes, no file bodies) by default is a mandatory security follow-up before T3.5**. No unrelated harness rewrite was done.
* NTFS directory-mtime settle workaround: P2 UNRESOLVED (unchanged).
* Contract/rename backlog: 27 CONTRACT and 52 RENAME candidates remain with the decisions above.

## 8. Remaining / readiness

T3.1 implementation delivered; independent Codex T3.1 audit pending. T3.5 CONDITIONAL_GO is not started; T4/T5/Wave D NOT STARTED; REAL_REPORT_PARITY_BLOCKED OPEN.
