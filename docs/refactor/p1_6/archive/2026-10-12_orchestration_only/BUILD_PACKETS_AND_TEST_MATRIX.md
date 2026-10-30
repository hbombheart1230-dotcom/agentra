# P1.6 — Implementation Work Packets / Test & Freeze Matrix

**PLANNING ONLY.** The packets below are **not active** while P1.5 Fast Track/P1.5.11 freeze is ongoing. They specify precisely what Claude should implement and Codex independently check in the future. They do not authorize production modifications or new active `CURRENT.md`.

## Prerequisite: P1.5.11 actual release acceptance (P16-0)

1. Read frozen P1.5.11 manifest/tag and verify SHA: full tests, actual immutable report/LLM parity, Docker mock/restart/ownership/SIGTERM, UEF7→8→9 cross-day, replay determinism, Broker/Step5C/D/R6.2 guards, 0 production-write & trading-authority leakage, independent Codex audit + GPT/user freeze.
2. Compare P1.6 design inspection snapshot (`62cdebf` original ancestry, `fb8de62` latest supplemental static review) against that SHA; list **PATH_DRIFT / ABI_DRIFT / SEMANTIC_DRIFT**. No automatic merge of unfrozen P1.5 code into P1.6 design.
3. Freeze accepted `run_strategist`/`run_scanner`/`run_monitor`/`evaluate_supervisor`/`run_reporter` inputs and adapters. They are P1.5 design target names; use **actual** finalized signatures and file paths.
4. Map **all** Commander runtime modes, fast paths, state keys written/deleted, public symbols/monkeypatch consumers; document `graph_spine` input equality and real M13 mode independence.
5. Create future `docs/refactor/p1_6/P16_BASELINE_MANIFEST.md` with evidence SHA, versions, fixture IDs, expected state/trace hashes. Mark missing genuine frozen data BLOCKED, not PASS.

## WO-16.1 — Build framework-neutral contracts and state bridge

**Files:** ADD `graphs/orchestration/{__init__,contracts,state_bridge,node_bindings,route_contract}.py` and `tests/p16/{conftest,test_state_bridge}.py`. No existing runtime code edits.

**Implement:** `OrchestrationRequest` with `mode=="graph_spine"`, `allow_side_effects=False`; `NodeVisit`; `OrchestrationResult`; injection registry; `split_runtime_state`, `legacy_state_delta`, `apply_legacy_state_patch`, `compare_legacy_state`, `should_hydrate`, `route_after_decide`.

**Tests:** distinguish missing from None, deletion of `decision_detail`, state `intents` filtering/selected clearing, `retry_count_scan`, immutable output/input parity, no unserializable handles leaking; import-time no side effects.

**Gate:** exact observed custom state semantics, no broker/LLM/log/prod path access. This is the hardest contract risk; don't start engine wrappers before proving it.

## WO-16.2 — Establish unchanged reference engine

**Files:** ADD `graphs/orchestration/engines/{__init__,custom}.py`, `tests/p16/test_graphspine_parity.py`, fixture manifest. Use existing `run_trading_graph` with **all seven injected test stubs** (including portfolio_guard and execution_pending marker), no new policy.

**Fixture cases:** no hydrate; explicit hydrate; `skill_runner`-trigger hydrate; no candidate; SELL exit pending guard; BUY Monitor entry passed; risk rejection; portfolio deny clears selected; one bounded scanner retry; multiple retry; rank/selected separation; malformed state; trace/count consistency.

**Gate:** explicit frozen expected outputs and visit order. Never “fix” baseline by changing new engine behavior unilaterally.

## WO-16.3 — Implement LangGraph candidate (offline only)

**Files:** ADD `graphs/orchestration/engines/langgraph_engine.py`, tests in `tests/p16/test_graphspine_parity.py`.

**Implement:** `StateGraph` nodes + conditional `should_hydrate`, `route_after_decide`, shared state bridge, offline invoke with fully injected pure handlers. No direct import of broker, live model or production report writers; no implicit LangGraph retries or durable live checkpoints.

**Gate:** 100% exact parity on allowed fixtures including mutation/DELETE and exit special decisions, 0 prohibited side effects. Pin LangGraph/Python package versions in isolated benchmark manifest, not the general production requirements file.

## WO-16.4 — Implement pydantic-graph candidate (offline only)

**Files:** ADD `graphs/orchestration/engines/pydantic_engine.py`; extend the same parity fixtures. Check official `pydantic_graph.beta` APIs **at installed version**, including `GraphBuilder`/StepContext/decision matching. A single outer async event loop wraps benchmark; no `asyncio.run` nested inside Commander/M13.

**Gate:** same exact parity/negative tests as LangGraph; no alternative policy/retry semantics hidden by typed graph.

## WO-16.5 — Failure, checkpoint, measurement, safety certification

**Files:** ADD `graphs/orchestration/{runner,checkpoint_policy,event_projection}.py`, `scripts/benchmark_p16_orchestration.py`, `tests/p16/{test_engine_failure_recovery,test_authority_firewall,test_mode_boundaries,test_dependency_imports}.py`.

**Implement:** three-engine sequential harness (independent state per run), fault injection before/after pure nodes, checkpoint/resume comparison, mode-blocking, isolated observation-only lineage, empty or blocked unsafe bindings. Metrics: pinned SHA/versions, per-fixture functional diff, cold/warm cost, p50/p95, peak RSS, code/adapter LOC, maintenance complexity, failure recovery.

**Gate:** zero production writes into repo `data/`, `reports/`, live SQLite, log archives, or Operator UI cache; zero real external LLM/network/broker; replay deterministic; bounded retry/cancel and repeated output. Capture incomplete tests as NOT RUN. Existing Step5C/D/R6.2 and UEF suites must retain their preexisting safety authority; a graph checkpoint is not an order journal.

### Benchmark acceptance data schema (proposed)
```json
{
  "freeze_sha": "<P1.5.11 accepted SHA>",
  "fixture_id": "<verified fixture ID>",
  "engine": "custom|langgraph|pydantic_graph",
  "engine_version": "<pinned>",
  "python_version": "<pinned>",
  "result": "PASS|FAIL|BLOCKED|NOT_RUN",
  "final_state_hash": "<hash>",
  "node_visits": [],
  "divergence_count": 0,
  "broker_calls": 0,
  "remote_llm_calls": 0,
  "production_writes": 0,
  "duration_ms_p50": null,
  "duration_ms_p95": null,
  "peak_rss_mb": null
}
```
All values are to be **measured** later. Do not populate fictitious zeros as completed evidence.

## WO-16.6 — Decision & optional future shadow handoff

**File:** ADD `docs/decisions/ADR-0004_P16_Orchestration_Engine_Decision.md` with `KEEP_CUSTOM`, `ADOPT_LANGGRAPH`, `ADOPT_PYDANTIC_GRAPH`, or `DEFER`. Include comparison, independent Codex report, accepted SHA, failure list, patch-notes updates.

**If KEEP/DEFER:** do not modify runtime; close P1.6 comparative evaluation transparently and continue strategy program P2 on custom runtime if approved.

**If ADOPT:** **new user approval** needed for a shadow-only disabled-by-default integration proposal. Modify only selected graph runner seam at `graphs/commander_runtime.py` (if proven necessary). Existing `integrated_chain`, `decision_packet`, M13, Docker, broker safety untouched. Do not merge/promote the candidate automatically; real rollout is a separate change window with rollback test.

## Test ownership and negative-gate matrix

| Existing protected suite / proposed new test | Acceptance obligation |
|---|---|
| `tests/test_m21_graph_spine_parity.py` | The custom baseline's injected approve and scanner retry behavior preserved; test file expectations unchanged. |
| `tests/test_m21_commander_runtime_entry.py` | `graph_runner` dependency injection, Commander mode/phase/fast paths preserved. |
| `tests/test_m13_tick.py`, `test_m13_live_loop.py`, `test_run_m13_live_loop_lock.py` | Market-hours, state load/save, EOD, loop lock and shutdown unaffected. |
| `tests/test_step5c_execution_owner.py`, `test_p0b_step5d_crash_reconciliation.py`, `test_supervisor.py` | Existing safety, journal, unknown outcome, approval authority unchanged. |
| `tests/test_uef8_fair_comparison_validation.py`, `test_uef9_formal_authority.py` | Replay/binding/authority remain frozen, no data mutation. |
| proposed `tests/p16/test_state_bridge.py` | State ownership and deletions; typed projection does not drop legacy keys. |
| proposed `tests/p16/test_graphspine_parity.py` | All 3 engines, exact node count/order/outputs/intent status, no extra Strategist on retry. |
| proposed `tests/p16/test_engine_failure_recovery.py` | Per-node failure/cancel/recovery, checkpoint pure reads only. |
| proposed `tests/p16/test_authority_firewall.py` | Refuse side-effectful callables and unknown modes, no broker/real LLM/Reporter write. |
| proposed `tests/p16/test_mode_boundaries.py` | `integrated_chain`, `decision_packet`, preopen/closeout never routed through candidate. |
| proposed `tests/p16/test_dependency_imports.py` | Custom runtime does not need either optional framework installed. |

## Test artifacts / change reporting / collaboration
- All tests run *after* freeze, in independent isolated workspace/temporary paths with no production writes.
- Success fixtures/temp logs automatically cleaned; failed evidence retained under bounded count/age policy, no repo test artifact growth.
- Claude implementation → Codex independent pinned-SHA audit → GPT/user final acceptance. One focused audit at each risk boundary, not tiny LOC increments. Existing P1.5 work-order entry remains active until its own completion; no historical reread.
- Every actual workflow/code change updates UI-linked `docs/trading_agent_patch_notes_detailed_update/{patch_notes.json,patch_notes.md}` and short daily entry. No ZIP required for P1.6 pre-design per user instruction.

## Decision quality gates
Hard blockers: any trading authority leakage, LLM count changes, report truth/UEF semantics change, event IDs altered, rank/intent policy mismatch, unexpected state deletion/default, non-idempotent resume, hidden production write, altered Host/Docker ownership. No weighted score can compensate.

Relative comparison **only after all hard gates**: end-to-end complexity/LOC, runtime latency, memory and dependency footprint, type safety, error/restart semantics, visibility, reviewer/debug time. Retain custom if new frameworks are ambiguous or costlier.

**P1.6 DESIGN READY** means implementer has exact paths/interfaces/wiring/tests/rollout plan. **P1.6 IMPLEMENTED/ACCEPTED** means gates were actually run, audited and approved; not achieved here.
