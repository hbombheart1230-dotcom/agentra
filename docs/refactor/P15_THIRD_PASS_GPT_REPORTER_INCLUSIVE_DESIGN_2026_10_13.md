# P1.5 Third Pass — GPT Reporter-inclusive function/authority design (2026-10-13)

> **2026-10-13 scope addendum:** [P15_ACTUAL_TREE_LARGE_FUNCTION_DELETE_AUDIT_2026_10_13.md](P15_ACTUAL_TREE_LARGE_FUNCTION_DELETE_AUDIT_2026_10_13.md). This audit discovered previously omitted `libs/contracts/agent_outputs.py` (Monitor 809, Strategist 530, Scanner 466, Commander 358 lines), `graphs/nodes/decide_trade.py` (~457), `libs/runtime/monitor_minute_ohlcv.py` (~395), `libs/runtime/monitor_strategy_frame.py` (~381), and Reporting metrics (~471). Add these to T3.5/T4 structural inventory, preserve all ABI/authority; do not interrupt Reporter T0/T1. A separate read-only deletion audit is required. The target tree's old [P] markers are not current status.

**Status:** THIRD_PASS_DESIGN; implementation NOT started. **Code and evidence baseline:** `bf59c4d2941442fc2dff41c3c2888f053b4b1577` on `refactor/p1.5`. **Previous verified CI:** successful for that SHA. **Human-provided independent Codex result:** PASS_WITH_FINDINGS for second-pass parity P1 fix. This design does not claim GPT re-ran Codex's tests.

**Scope:** all seven agents plus Operator UI, with **Reporter INCLUDED BEFORE WAVE D**. Existing schema/ABI/public facades remain stable. No new live trading, real Broker/LLM call, production-file write, main merge or Wave D without separate authorization. The second-pass AST parity audit and targeted replay are a **checkpoint**, not a permanent waiver of regression checks.

## 0. Outcome required

The goal is **coherent responsibility extraction and bounded capabilities**, not simply moving lines into another wrapper or creating a large number of one-off files. Review the actual existing package first. For every candidate, choose SPLIT / KEEP / REVIEW / SAFETY_LOCK, then preserve the original ordered I/O, event, State, exceptions, monkeypatch seams, prompt payload and report bytes. Target named pure Owners typically <=350 physical LOC; an effect-owning coordinator can exceed that cap if justified with measured ordered-side-effect evidence.

**Approval order:** (a) this pinned GPT design → (b) Claude coherent bulk implementation and focused gates → (c) Codex independent structural audit → (d) GPT residual inventory and additional coherent pass if needed → (e) **Wave D last** (full native pytest, Docker mock, UEF, exact frozen report/LLM/Operator artifact parity, broker mock and production-write isolation). No automatic leap to Wave D.

## 1. Verified actual source census (function LOC excludes only earlier definitions)

| Area / verified actual source function | Approx current LOC | Decision | Reason |
|---|---:|---|---|
| Reporter `libs/reporting/live_execution_bundle_runner.py::main` | 1,529 | SPLIT WITH EFFECT LOCK | This is the actual large bundle CLI orchestrator. It holds job locks/queue and runs a per-lifecycle loop spanning roughly source L1722–L2867, including LLM generation, artifact writes and event ordering. |
| Reporter `libs/reporting/trade_memory_surface.py::build_trade_report_memory_surface` | 675 | SPLIT P0 | Feedback/memory/visibility/strategy projections share one large read-model assembler. |
| Reporter `libs/reporting/trade_read_model.py::build_trade_read_model` | 601 | SPLIT P0 | Artifact load, precedence, execution/entry/exit/monitor truth and display projection are mixed. |
| Reporter `libs/reporting/trade_report_ai_deterministic.py::fallback_report` | 538 | SPLIT P0 | Fallback summary construction, section selection and output schema; many injected dependencies. |
| Reporter `libs/reporting/trade_lifecycle_builder.py::_build_trade_lifecycles` | 535 | SPLIT P1 | Ordered trade lifecycle assembly from run snapshots; conservation/order must hold. |
| Reporter `libs/reporting/closeout_maintenance.py::run_closeout_maintenance` | 476 | REVIEW / EFFECT LOCK | Real closeout maintenance/IO. Do not move effects for cosmetics. |
| Reporter `libs/reporting/agent_pipeline_trace.py::generate_agent_pipeline_trace_report` | 445 | SPLIT REVIEW | Trace/evidence computation vs artifact I/O; preserve provenance. |
| Reporter `libs/reporting/trade_bundle_assembly.py::apply_entry_exit_holding_enrichment` | 428 | SPLIT P1 | Entry/exit/hold projections that can be separated by input/output stage. |
| Reporter `libs/reporting/trade_report_ai_compact_input.py::compact_story_input_for_llm` | 412 | SPLIT P1, PROMPT LOCK | Stable LLM compact input, precedence and char/token shape. Related `sparse_story_input_for_llm` ~326. |
| Reporter `libs/reporting/trade_bundle_state.py::build_live_trade_bundle_payloads` | 399 | SPLIT REVIEW | Provenance, health, artifact-link projections. |
| Reporter `libs/reporting/single_trade_report.py::_build_trade_report_inputs` | 391 | SPLIT REVIEW | Input acquisition vs read projections. |
| Reporter `libs/reporting/operator_visibility.py::build_operator_daily_summary_payload` | 348 | KEEP/REVIEW | Under target bound, but examine true complexity/capabilities. |
| Reporter `libs/reporting/intraday_trade_reports.py::generate_intraday_trade_artifacts` | 202 (file ~1,850) | KEEP COORDINATOR / FILE-LEVEL REVIEW | Very large file is **not** one 1,850-line function. Bundle sync, queue/process, cache invalidation and artifact I/O are spread over many functions; order/write locks protected. |
| Reporter `libs/reporting/trade_report_ai.py` | ~1,657 file | KEEP COMPAT FACADE | Large file made of many short functions and binding surfaces; R0 found real dynamic/static consumers. Do not physically rename/move. |
| Reporter `libs/reporting/trade_report_markdown_clean.py` | ~1,326 file | KEEP COMPAT FACADE | Many small functions, real consumers and monkeypatch seams; no cosmetic physical move. |
| Reporter `libs/reporting/trade_story_pipeline.py` | ~499 file | KEEP COMPAT FACADE | Dynamic and static call-sites; keep public ABI. |
| Scanner `graphs/nodes/scanner_node.py::scanner_node` | 1,262 | SPLIT P1 | Existing score/rank/selected-order boundaries, single canonical ranking source. |
| Strategist `graphs/nodes/strategist_node.py::strategist_node` | 1,217 | SPLIT P1 / LLM LOCK | Preserve real LLM invocation, fallback and prompt call order. |
| Monitor `graphs/nodes/monitor_node.py::monitor_node` | 1,108 | SPLIT P1 / STATE LOCK | Intent-only, cooldown/probe and ordered mutations. |
| Monitor `libs/runtime/exit_policy.py::evaluate_exit_policy` | 674 | SPLIT P1 | Exit trigger priority and hold precedence frozen. |
| Commander `graphs/commander_runtime.py::_resolve_commander_behavior_policy` | 530 | SPLIT P2 | Behavior policy purity; runtime route/order effects remain in current facade. |
| Operator UI `apps/operator_ui/data_access_core.py::_load_operator_brief` | 444 | SAFETY_LOCK | Existing LLM chat/retry/prompt/IO; split ONLY if frozen request and artifact replay exists. |
| Strategist `graphs/nodes/strategist_node.py::_run_strategist_frame_llm` | ~350 | SAFETY_LOCK | Existing LLM behavior, not a low-risk projection. |
| Executor `graphs/nodes/execute_from_packet.py` | >4k file | SAFETY_LOCK | Single submission order, readiness, CAS, UNKNOWN and broker mutation; immutable real-case fixtures are missing. |

**Scope caveat:** 1,941 total Python files; 466 under `libs/reporting/`, including Q10/Q12/UEF/research. These are not all Reporter agent files. The Reporter inventory above samples physically verified high-value core files and should be expanded by a fresh AST census during implementation; missing entries are **NOT** authorized for delete/move. In `libs/reporting/live_execution_bundle_runner.py`, the 1,529-line function is more important than the 1,850-line `intraday_trade_reports.py` file as a giant *function*.

## 2. Phase T0 — Reporter baseline and consumer map BEFORE Reporter edits

**Owner:** Claude builds compact, fixture-only evidence; Codex inspects representative baselines independently. This is a prerequisite to touching Reporter output contracts.

- Freeze API and use-time monkeypatch consumers for `trade_report_ai.py`, `trade_report_markdown_clean.py`, `trade_story_pipeline.py` and actual pipeline entrypoints. At earlier Wave C audit Reporting has 436 public ABI symbols and 330 static consumer UNKNOWN; do not treat UNKNOWN as dead.
- Freeze deterministic representative scenarios: no execution, open/HOLD, partial exit, closed BUY→SELL, reporter LLM failure/fallback, targeted regeneration, queue/lock active and resumptions; include availability/missing-coverage statuses. Prefer existing fixtures and synthetic safe mock inputs. Record provenance and distinguish MOCK vs REAL.
- Capture **exact** output contracts for Markdown, JSON and JSONL, stable key/order when applicable, Korean text, file names, path identity, artifact links, report status, prompt/model/messages/temperature/max_tokens/retry/call count and report generation side effects. If authentic frozen production reports are not lawfully available, mark REAL_REPORT_PARITY_BLOCKED and do not change that unsafe effectful path; do not fabricate a PASS.
- Record existing CI baseline, single-process test root and no-production-write manifest. No real LLM/broker, scheduler or network.

## 3. Phase T1 — Reporter PURE read models/section builders (first implementation tranche)

**Preferred order:** (A) `trade_memory_surface.py::build_trade_report_memory_surface`; (B) `trade_read_model.py::build_trade_read_model`; (C) `trade_report_ai_deterministic.py::fallback_report`; (D) `trade_report_ai_compact_input.py::compact_story_input_for_llm`; then `trade_bundle_assembly.py::apply_entry_exit_holding_enrichment` and `trade_lifecycle_builder.py::_build_trade_lifecycles` only if frozen lifecycle ordering fixtures.

**Contract:** create/reuse cohesive Owners for `memory input + visibility / feedback / status projection`; `artifact read selection + entry-exit truth / read-view`; `fallback sections / final schema assembly`; `compact prompt facts / stable ordered payload`; `entry, exit, holding evidence`; `lifecycle conservation`. Prefer existing `libs/reporting/trade_report/{section_parts,summary_input_parts,summary_render_parts,ai_facade_parts}` or `libs/reporting/trade_story_assembly_parts` instead of generic or numbered helpers. Add new named modules only when existing package semantics do not fit.

Pure Owners receive narrowly typed read-only facts or copied mappings, return structured values and own no LLM, filesystem, clock, broker, runtime State or report persistence. Keep public wrapper with original function names. When an injected dependency dict is already part of a public monkeypatch surface, reduce to explicit callable subset without changing use-time resolution. Freeze read-model precedence including stale/missing truth and real-vs-fallback status; exact fallback report and compact LLM input byte parity are mandatory.

**Completion signal:** meaningfully reduce giant inner functions, no new public API break, diff on frozen fixtures has zero unexplained changes, 0 production writes, Owner inventory and largest-function-before/after published.

## 4. Phase T2 — Reporter runtime orchestration (high-risk but highest payoff)

**Actual seam:** `libs/reporting/live_execution_bundle_runner.py::main` L1404–2932 ~1,529 LOC. Coherent regions:
1. **L1404–1524** CLI/parser, role, lock/PID, environment/state load, policy and report model; retain authorization/lock ownership in runner.
2. **L1525–1721** execution/run evidence acquisition, output artifact bundles, snapshot/lifecycle identification and target filtering; extract PURE plan/read models only, leave I/O/writes/event emission in original exact order.
3. **L1722–2867** per-lifecycle processing (bulk): create a per-trade runner/coordinator only after event/write-order fixtures; split its PURE story/evidence/source-link, strategy anchor, fallback choice, output payload/evaluation plans. Do not extract a 1,100-line function into a new 1,100-line owner and call it complete.
4. **L2300–2380 within per-lifecycle** report generation mode, LLM starting event, `execute_ai_trade_report_generation` and exception handling: **LLM + artifact + event SAFETY_LOCK** unless exact frozen call/response/retry/prompt/call-count fixtures exist.
5. **L2663–2867** story/payload persistence, follow-up refresh and bundle backfill: keep write ordering, idempotency and source truth; plans may be pure, mutating actions effect owned and replay-proven.
6. **L2869–2930** final summary output, queue drain, lock release, follow-up job: preserve exactly. NEVER use a pure helper that writes or spawns implicitly.

Review `intraday_trade_reports.py` by *function* ownership: queue/lock/process/cache/artifact responsibilities; keep `generate_intraday_trade_artifacts` stable public entry, do not move process-launch, SIGTERM or background lock semantics without bespoke crash/process fixtures.

**Phase T2 decision:** if deterministic fixtures do NOT capture ordered side effects (per trade/queue/lock/LLM), mark these effectful seams REVIEW / SAFETY_LOCK, improve only nearby PURE data projections and proceed. No cosmetic façade move as substitute for safety proof.

## 5. Phase T3 — Second-pass Owner contract cleanup

Codex second-pass reports **42/45 broad facade injection** and max tuple return arity **24**. They are P2 structural debt, not an excuse to break use-time monkeypatch compatibility.

- Rank Owners by breadth of accessed facade symbols and return arity. Narrow facade injection to explicit functions/config/accessor capabilities and pure input snapshots. Preserve dynamic lookup on original public façade at *use time* where monkeypatch consumers rely on it. Do not eagerly bind a formerly patchable method.
- Replace **selected** high-arity (>8) output tuples with named immutable result records or dataclasses, including a stable field-order adapter at the facade boundary. Never convert all 45 mechanically in one go; test every call-site's unpacking, identity, deepcopy/hash and event order.
- Rename mechanically generated `*_projection_*` names only after verified consumer mapping; prefer semantic Owner names. Avoid repeated facade/Owner bounces and new circular imports. Don't rename Reporter ABI facades; leave `bodies_01..05` as REVIEW until consumer-safe and role-specific.
- Report capability matrix before/after: pure Owner should not receive wide import/module root, Broker, LLM provider, mutable TradeState, unmanaged I/O or credential/env root.

## 6. Phase T4 — Remaining non-Reporter large functions

- **Scanner P1**: `scanner_node` 1,262 LOC. Candidate evidence/fallback, guard evaluation and selection projection; canonical rank/tie/rank-1 ordering unchanged. Use invariant fixture for selected/runner-up.
- **Monitor P1**: `monitor_node` 1,108 LOC, `evaluate_exit_policy` 674. Further pure entry vs exit decision plans, event/state application stays ordered, cooldowns, controlled opening rank-1 probe and apply-once policy untouched.
- **Strategist P1**: `strategist_node` 1,217 LOC. Market/memory/context + deterministic policy and output, preserve frame LLM prompt/provider/retry/timeout model path. Do not recut SAFETY_LOCK LLM frame unless frozen data.
- **Commander P2**: `_resolve_commander_behavior_policy` 530 LOC; pure policy precedence normalization only, no runtime phase/fast-path order changes.
- **Operator UI**: renderer ~351 LOC and `_load_operator_brief` 444 LLM-bound. Pure render/read views only with canonical facts, no premature LLM refactor.
- **Supervisor/Executor**: preserve authority choke/Step5C CAS/BrokerOutcome UNKNOWN until immutable executor actual-case fixtures and independent safety authorization.

All agent-node mutation/event/exception order remains at the original effect boundary. Make substantive cuts, not hundreds of tiny wrappers.

## 7. Phase T5 — Controlled mock-lane operational root (separate risk remediation)

**Verified actual source:** `libs/runtime/controlled_mock_lanes/ledger.py` L13 `DEFAULT_ROOT = Path("data/logs/controlled_mock_lanes")` and L21 root selection checks `CONTROLLED_MOCK_LANE_LOG_ROOT`. A test's mock run created `data/logs` in a disposable clone; targeted harness now redirects it, but the default runtime path is still cwd-relative.

Do not casually change operational path because existing generated files, scripts and observers may depend on it. First map all users of default root and actual configured production root/relative cwd; propose a fail-closed deterministic path resolution with explicit mode semantics, provide migration/compatibility strategy and focused Step5C/mock-lane acceptance. Treat **OPERATIONAL_PATH_OPEN** until independently approved. No changes to real trading ledger/order history in this design pass.

## 8. Exact gates and cadence

- No shared dirty clones. Claude implementation isolated from Codex independent audit. No concurrent pushes to same branch without fast-forward verification and explicit reconciliation.
- Each coherent tranche is a real bulk group, NOT a multi-hour unbounded prompt or tiny 100-line handoff. Commit/push after focused parity gates with a concise evidence file; proceed to next coherent tranche unless safety BLOCKED. Keep one integrated final Codex audit for third-pass set.
- Test artifact roots isolated per session outside repo, successful runs auto-clean, failed evidence bounded; prevent `controlled_mock_lanes` write bleed. Never use TEST fixture generation to assert real report/LLM parity.
- Every meaningful code change updates **both** `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and `patch_notes.md` plus daily patch, and reconciles current/target architecture's [E]/[P] markers.
- Report (for each large function): original function/LOC, retained effect ownership, new named owner/LOC, actual largest function after, direct consumers, ABI/monkeypatch contract, output and ordered side-effect parity, tests, safety deferred. Cosmetic moves alone do not satisfy completion.
- Any real ranking, decision, prompt, LLM call count, broker, lock/queue event, report bytes, Step5C or State mutation discrepancy = stop & rollback that slice; report P0/P1 immediately.
- Reviewer must verify no hidden ability for pure owner to call Broker/LLM/real filesystem; double-check dynamic imports and facade injection at call time.

## 9. Proposed repo layout, only after source-backed Owner assignment

~~~text
graphs/nodes/                           [E] original 7-agent surfaces kept
libs/runtime/{monitor,monitor_exit,scanner,strategist,commander}/   [E] current packages, cohesive additions only
libs/reporting/
  intraday_trade_reports.py             [E] retain report-generation entry; queue/process lock owner
  live_execution_bundle_runner.py       [E] retain CLI orchestration, lock/queue/persist sequence
  trade_memory_surface.py               [E] retain compatibility API; delegate coherent read projections
  trade_read_model.py                   [E] retain compatibility API; delegate coherent read projections
  trade_report_ai_deterministic.py      [E] retain fallback facade, exact report schema
  trade_report_ai_compact_input.py      [E] retain compact prompt APIs/shape
  trade_lifecycle_builder.py           [E] keep lifecycle ordering coordinator
  trade_report/{summary_input_parts,summary_render_parts,section_parts,ai_facade_parts}/ [E] reuse first
  trade_story_assembly_parts/           [E] reuse lifecycle/story owners first
  reporter_bundle_runtime_parts/        [P] only if a real cohesive per-trade read-only plan group cannot fit existing owners
  trade_memory_projection_parts/        [P] only if existing named inputs/summary owners do not fit
  trade_read_model_parts/               [P] only if existing ownership truly distinct
  evaluation/, baseline_*/, alpha_research_board/ [E] separate research/evaluation, NOT automatically moved
apps/operator_ui/                       [E] canonical read-model + explicit Brief LLM boundary
~~~

**Prior R0 Codex result:** no proven safe mechanical Reporter file moves/renames. This design does NOT overturn that result. It moves function *responsibility* only after parity evidence, keeping public compatibility.

## 10. Third-pass completion boundary

Do not call structural closure merely because these files shrink: check *largest actual function*, facade injection capability, output tuple contract, report source/format parity, and active effect owners. Remaining genuinely unsafe slices recorded as SAFETY_LOCK with fixture owner and reason. Codex integrated audit then GPT/user decide whether further structural round is required. **Wave D after all chosen structurally safe rounds**, never before; Wave D's essential real output/LLM and authority gates cannot be silently waived.
