# Agentra P1.5 — TECH LEAD CANONICAL ARCHITECTURE DECISION (2026-10-18)

**Authored by:** GPT Tech Lead, direct source/tree review; **read snapshot:** integration `5cb90b39d00cee483be292272b893d8e8a4c6e78`. **State:** DESIGN_BASELINE_FROZEN_FOR_REVIEW, **NOT** source migration approval or P1.5 acceptance. Codex/Claude ongoing branch tips must be selectively rechecked at integration time. Current pinned historical target: `TREE_V3_FROZEN.md` (HYBRID-7 V3); this **refines but does not replace** that target. Old user-provided Trading_Agent_System M15 project_tree describes historical interfaces, not the 2026-10-18 Agentra tree.

## 1. Facts, not estimates
- Git tree: **3,908 tracked blobs**, **289 directory trees**, top-level `libs` **1,220**, `docs` **1,269**, `tests` **640**, `scripts` **415**, `apps` **235**, `graphs` **45**.
- `libs/`: **26 distinct first-level packages + `__init__.py`**. Largest: reporting500, runtime319, agents115, research110; together1,044/1,220. Full exact files: `P15_TREE_ALL_PATHS_PINNED_20261018.txt`; proposed EVERY-file ownership: `P15_ALL_FILES_OWNERSHIP_CANDIDATES_20261018.csv`. Every CSV 'candidate' is PATH-BASED classification, **not** independently proved caller graph.
- Large first-party runtime files: `graphs/nodes/strategist_node.py` 202774B; `graphs/nodes/execute_from_packet.py` 183181B; `graphs/commander_runtime.py` 152986B; `libs/runtime/intraday_monitor_signals.py` 135937B; `libs/reporting/live_execution_bundle_runner.py` 130855B; `libs/contracts/agent_outputs.py` 105768B; `apps/operator_ui/data_access_core.py` 162853B. Size is a triage indicator, not automatic move authorization.
- Contrary to names, `graphs/trading_graph.py` explicitly avoids hard LangGraph dependency and its `executor_node.py` is a STUB. Actual order path: `graphs.commander_runtime` → `graphs.nodes.execute_from_packet` → Supervisor/Approval/Guard/Step5C/Executor/Broker. Do **not** treat graph stub as broker execution.

## 2. Desired navigable tree (end state, not physical current tree)
```text
agentra/
  apps/          api/{routers,services,domain,models,adapters,infrastructure}/  web/  operator_ui/
  graphs/        commander_runtime.py [operational adapter] trading_graph.py [M17 test spine]
                 nodes/ [compat/state adapters; executor_node STUB]
  libs/
    agents/      commander/ strategist/ scanner/ monitor/ reporter/ supervisor/ executor/
                 # SEVEN peer PUBLIC CONTRACT surfaces, real ownership, no cosmetic stubs
    contracts/   [DTOs, output ABI and versioned serialization, dependency inversion]
    runtime/     [cross-role scheduling, locks, evidence writer, common runtime primitives]
    reporting/   [EOD publisher, persisted read models, report render/bundle effects]
    research/    [Q10/Q12 alpha, forward validation, non-order diagnosis]
    strategies/  [candidate generation/playbooks; scanner still exclusive ranking owner]
    core/ market/ market_data/ news/ data_quality/ read/ catalog/ skills/
    llm/ ai/ performance/ diagnostics/ tools/ storage/
    kiwoom/ risk/ approval/ supervisor/ execution/  # LOCKED operational effect owners
    agent/       [old M15 compatibility facade; KEEP until proven unused]
  config/ data/ deploy/ scripts/ tests/ docs/ .github/
```
**Important:** Reorganizing directories is NOT the goal; one verified callable owner and one truthful public import is. Preserve real runtime, stable imports, State/DTO schema, callable identity, monkeypatch seams, environment read timing, order/LLM/write ordering, logs, and legacy shims. Re-exporting live `execute_from_packet` at import time could activate broker imports: do not treat it as automatically safe.

## 3. Seven-role authority table
| Role | Actual operational anchor at pinned integration | Public peer today | Definitive ownership |
|---|---|---|---|
| Commander | `graphs/commander_runtime.py` + `libs/runtime/commander/` | missing | orchestration/route only, not ranking/orders |
| Strategist | `graphs/nodes/strategist_node.py` + `libs/runtime/strategist/` | `libs/agents/strategist/` partial | thematic frame, evidence, LLM strategic context |
| Scanner | `graphs/nodes/scanner_node.py` + scanner owner modules | `libs/agents/scanner/` partial | **only** ranking, Top-1 candidate selection |
| Monitor | `graphs/nodes/monitor_node.py`, `libs/runtime/monitor[_exit]/` | `libs/agents/monitor/` partial | observe selected/held symbols; emit OrderIntent, never submit |
| Reporter | `libs/agent/reporter.py`, `libs/reporting/`, `graphs/nodes/reporter_node.py` | `libs/agents/reporter/` partial | read models, reports, replay, feedback; not evaluation authority |
| Supervisor | `libs/risk/supervisor.py`, `libs/supervisor/`, `libs/approval/service.py` | missing | **exclusive** approval/intent state/override authority SAFETY_LOCK |
| Executor | `graphs/nodes/execute_from_packet.py`, `libs/execution/`, `libs/kiwoom/` | missing | **exclusive** authorized broker/order mutation SAFETY_LOCK |

## 4. Dependency rules
1. `apps/` -> readonly service/query/adapters -> contracts/read models; API/UI **must not** import operational order clients or mutate run State.
2. `graphs/nodes` -> role owner/domain support, not vice versa; **existing reverse imports** are debt to measure before fixing, not permission to bulk rewrite.
3. Strategist -> frame; Scanner -> rank; Monitor -> intent; Supervisor -> authorization; Executor -> guarded mutation; Reporter/Evaluation -> persisted evidence/read model. No second rank, order, approval or UEF publisher.
4. `libs/contracts/agent_outputs.py` currently imports multiple `libs.runtime.*` enrichers: this is an observed **contract→runtime inversion**, and a design-quality issue. Split pure DTO/schema from enriched builders only after exact JSON bytes and public import identity proven; do not 'fix' by circular imports.
5. UEF canonical publisher is `libs/reporting/evaluation/daily_uef_pipeline.py` (verified file header/imports); `libs/market_data/receipts.py` issues/verifies data provenance contract but never declares UEF authority. Both stay in place.
6. Side effects never relocate solely for aesthetic symmetry. Operative Step5C CAS, UNKNOWN quarantine, Broker, approval, replay/golden and Q10/Q12 real lanes retain frozen paths and explicit guards.

## 5. Actual prioritized work (frozen phases)
- **G0 stabilize**: Codex candidate UEF9 hermetic fixture clean-clone/CI; Claude Auditor delta. No main/integration source promotion until exact PASS and compatibility scope reviewed.
- **G1 interface proof**: real callable public Commander and existing four role facades. Implement at most one package per reviewed slice; test stable identities, no import effects, State adapter and old import, especially `libs/agent/`. Monitor implicit namespace marker is not silently safe.
- **G2 decompose pure large modules**: Strategist node, Monitor signal core, Commander pure helpers, `libs/contracts/agent_outputs.py`; prioritize actual repeated call/ownership hotspots by consumer proof, not bytes alone. REWORK static inventory is FROZEN and **cannot** classify a move as SAFE.
- **G3 reporting/research ownership**: 500 file inventory; UEF daily publisher and live report effect runner stay. Reporter narrative/read models are separate from Research/Evaluation Q10/Q12. No mass move of `libs/reporting/evaluation/` or dynamic report facade bodies.
- **G4 operator/API seams**: split `apps/operator_ui/data_access_core.py` into existing brief/read-model/renderer modules by function, preserve output bytes/read-only semantics and UI import path; `apps/api` already segmented into routers/services/domain/infra.
- **G5 safety interface design**: Supervisor/Executor pure Protocol/contracts with **no new submission/approval route**; physical SAFETY_LOCK owner paths stay. Implement only after explicit operator scope approval and dry-run/unknown/Step5C parity.
- **G6 final acceptance**: consumer/import and monkeypatch parity on moved **exact modules**, normal/-O, Windows+Linux CI, hosted gates, replay/golden, UI build+visual, production-write zero, remaining 24 real-data SKIP labeled NOT_RUN/BLOCKED not PASS. Produce SHA-pinned architecture + migration ledger before P1.5 Freeze and P2.

## 6. Integration and change discipline
- Protected `main` **unchanged**. Integration `5cb90b39d00cee483be292272b893d8e8a4c6e78` is design baseline, not acceptance. Only exact audited paths cherry-picked by one integrator; **never merge the whole Claude fork** (221 integration-side paths absent due branch divergence).
- **Developer:** real code and focused tests, no extra meta-analyzer projects. **Auditor:** exact SHA changed scope, positive/negative parity, contract+effect gate, no code write. **GPT Tech Lead:** design, owner matrix, change classification, merge authority review.
- All meaningful source/test changes must update UI-linked `patch_notes.json` and `patch_notes.md` together. This design-only documentation update must say **NO runtime change**. Test scratch per session; successful scratch cleans, failed evidence bounded.
- Existing 7 static-classifier adversarial FAIL remain an explicit unresolved limitation; do not use that classifier to approve callable/source migration. No endless classifier repair in P1.5.

**NEXT_INTEGRATION_GO** requires explicit user decision after risk/CI review. **P1.5_FINAL_ACCEPTED = false.**
