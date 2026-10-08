# P1.5 PREP Closure Report

Status: PREP CLOSED / DESIGN FROZEN / IMPLEMENTATION GATED
Date: 2026-10-07
Design branch: design/p1.5-p1.6-modernization
Design HEAD at closure preparation: d84d332936dfba723179a51aadf2a9dedf8ef38e

## 1. Executive Summary

P1.5 preparation is complete.

This closure freezes the detailed implementation design for P1.5.1-P1.5.11 while explicitly NOT starting runtime implementation.

Current gating:
- P1.3 remains operationally open per current program state.
- P1.5 implementation baseline is therefore not yet frozen.
- No P1.5 runtime implementation branch should be cut until the upstream baseline gate closes.

What P1.5 PREP accomplished:
- inventoried the principal monoliths and their hidden compatibility/safety seams
- froze Agent responsibility boundaries
- designed explicit contracts/state adapters for Strategist, Scanner, Monitor and Commander runtime
- designed Reporting and Operator UI decomposition
- isolated Executor low-risk extraction from safety-critical mutation semantics
- designed canonical runtime naming with backward-compatible aliases
- designed compatibility-wrapper cleanup by consumer proof
- designed full regression, Docker, UEF replay and formal-freeze acceptance
- kept the entire design branch documentation-only

## 2. Important Truth: How Much Has Actually Been Reduced?

At PREP close:
- runtime Python reduction actually implemented: 0 LOC
- production runtime topology change: 0
- trading behavior change: 0
- Agent ordering change: 0
- LLM role change: 0
- broker/execution authority change: 0

P1.5 PREP is a design freeze, not an implementation freeze.

The reduction numbers below are IMPLEMENTATION TARGETS frozen by the design packets.

## 3. Current Giant-Surface Inventory

Primary giant surfaces mapped:

| Area | Current giant surface |
|---|---:|
| Reporting: 3 giant public modules | 18,743 LOC |
| Operator UI / Brief: 3 giant modules | 11,925 LOC |
| Strategist node | 8,879 LOC |
| Scanner node | 4,179 LOC |
| Monitor node | 3,633 LOC |
| Commander runtime | 6,298 LOC |
| Executor execute_from_packet | 4,190 LOC |
| **Primary total** | **57,847 LOC** |

Secondary giant hotspot:
- libs/runtime/intraday_monitor_signals.py: ~3,608 LOC

Including that adjacent Monitor signal engine:
- mapped giant/hotspot surface = approximately 61,455 LOC

This is not the whole repository. It is the concentrated refactor surface identified by P1.5.

## 4. Facade Shrink Target

The six structural façade groups that P1.5 actively decomposes before Executor are:

| Area | Current | Target façade | Approx façade shrink |
|---|---:|---:|---:|
| Reporting 3 giant facades | 18,743 | 850-1,550 | 91.7-95.5% |
| Operator UI / Brief hotspots | 11,925 | 1,200-2,000 | 83.2-89.9% |
| Strategist node | 8,879 | ~150-350 | ~96.1-98.3% |
| Scanner node | 4,179 | 150-350 | 91.6-96.4% |
| Monitor node | 3,633 | 150-350 | 90.4-95.9% |
| Commander runtime | 6,298 | 200-500 | 92.1-96.8% |
| **Total** | **53,657** | **~2,700-5,100** | **~90.5-95.0%** |

Interpretation:
- approximately 48,500-51,000 LOC are intended to disappear from giant façade/orchestrator files
- most of that logic moves into focused owners
- it is NOT a promise that repository total LOC falls by 50k
- repository total LOC may remain similar or even temporarily increase because of contracts, adapters, compatibility wrappers and tests

The meaningful reduction is:
- giant-file cognitive load
- hidden responsibility mixing
- arbitrary graph-state mutation
- implicit IO
- compatibility ambiguity
- test monkeypatch coupling

## 5. Definite Code Deletion Identified

Reporting contains an approximately 1,100 LOC unreachable legacy tail after an early return.

This is the strongest definite deletion candidate.

Other likely net deletions:
- duplicate/shadowed helper definitions
- duplicate AgentExecutor implementation
- proven orchestration duplication after canonical owner migration
- zero-consumer compatibility wrappers in P1.5.10

These are not counted as removed until implementation + regression proves deletion safe.

## 6. Why Executor Does Not Get the Same Pretty LOC Target

execute_from_packet.py is approximately 4,190 LOC.

P1.5.9 intentionally does NOT force it to ~300 LOC.

Reason:
- readiness
- ordered guards
- Supervisor verdict
- immutable readiness evidence
- intent admission
- Step5C physical/logical ownership
- broker dispatch
- BrokerOutcome classification
- UNKNOWN quarantine
- cancel/recovery

form one auditable safety chain.

P1.5.9 only extracts:
- observability projection
- canonical artifact coordination
- optional pure order-view helpers

Expected reduction:
- only a few hundred LOC

A 3,000+ LOC execution authority coordinator is explicitly acceptable if that makes mutation ordering easier to audit.

This is intentional asymmetry:
- ordinary orchestration gets aggressively decomposed
- broker authority remains intentionally centralized

## 7. Before: Architectural Shape

Conceptually, the current concentrated shape is:

```text
graphs/nodes/strategist_node.py       8,879
graphs/nodes/scanner_node.py          4,179
graphs/nodes/monitor_node.py          3,633
graphs/commander_runtime.py           6,298
graphs/nodes/execute_from_packet.py   4,190

libs/reporting/
  trade_report_ai.py                  giant
  trade_report_markdown_clean.py      giant
  trade_story_pipeline.py             giant
                                      ------
                                      18,743 total

apps/operator_ui/
  data_access_core.py                 6,872
libs/reporting/
  operator_period_summary.py          3,205
  operator_visibility.py              1,848
                                      ------
                                      11,925 total
```

Characteristics:
- graph adapters also contain business logic
- deterministic policy, IO, evidence and compatibility writes are mixed
- tests directly import/monkeypatch private graph-node helpers
- state dictionaries act as implicit contracts
- milestone vocabulary leaks into active runtime names
- public compatibility and canonical implementations are not always visually obvious

## 8. After: Target Architectural Shape

The target shape is responsibility-first.

```text
graphs/
  nodes/
    strategist_node.py       # thin graph adapter
    scanner_node.py          # thin graph adapter
    monitor_node.py          # thin graph adapter
    commander_node.py        # thin graph adapter
    execute_from_packet.py   # intentionally larger safety coordinator

libs/
  contracts/
    agents/
      strategist.py

  runtime/
    strategist/
      service.py
      state_adapter.py
      observability.py
      context/
      llm/
      policy/
      output/

    scanner/
      contracts.py
      service.py
      state_adapter.py
      scoring.py
      evidence.py
      guidance.py
      repeat_guard.py
      symbol_prior.py
      compatibility.py
      ...existing focused owners...

    monitor/
      contracts.py
      service.py
      state_adapter.py
      entry_orchestrator.py
      exit_orchestrator.py
      intent_arbitration.py
      evidence.py

    monitor_entry_signals/
      policy_resolution.py
      chart_context.py
      policy_interpreter.py
      scoring.py
      candle_series.py
      evaluation.py

    monitor_exit/
      ...existing canonical exit owners...

    commander/
      contracts.py
      service.py
      state_adapter.py
      policy_composition.py
      decision_builder.py
      entry_control.py
      open_position_control.py
      phase_router.py
      lifecycle.py
      evidence.py
      reporter_hooks.py
      ...existing focused owners...

  reporting/
    trade_report/
      normalization.py
      operator_text.py
      sections.py
      service.py

    trade_report_markdown/
      summary_input.py
      summary_render.py
      strategist.py
      memory.py
      labels.py

    trade_story/
      market_context.py
      scanner_reason.py
      monitor_reason.py
      filters.py
      lifecycle.py
      service.py

  execution/
    executor_observability.py
    executor_artifacts.py
    order_views.py
    ...existing safety owners...
    intent_execution_owner.py
    readiness_evidence.py
    guards/

apps/
  operator_ui/
    data_access.py            # stable public facade
    data_access_core.py       # small compatibility/orchestration facade
    data_access_status.py
    data_access_runs.py
    data_access_reports.py
    data_access_linkage.py
    data_access_brief.py

    brief/
      canonical_input.py
      sections.py
      compact_input.py
      sanitation.py
      prompting.py
      generation.py
      persistence.py
      rendering.py
      service.py

    views/
      overview.py
      run_detail.py
      health.py
```

## 9. The Main Visual Improvement

The intended mental model becomes:

```text
Graph / Runtime Adapter
        |
        v
 Explicit Input Contract
        |
        v
 Focused Service / Pure Policy
        |
        v
 Explicit Result Contract
        |
        v
 State Adapter / Evidence / IO
```

Instead of:

```text
state dict
  -> giant graph node
       -> policy
       -> file IO
       -> network
       -> state mutation
       -> evidence
       -> compatibility
       -> more policy
       -> hidden side effect
  -> state dict
```

That is the main P1.5 cleanliness gain.

## 10. Agent Boundaries After P1.5

### Strategist
- LLM role retained
- strategic framing
- explicit StrategistAgentInput / StrategistAgentResult
- graph node becomes adapter

### Scanner
- deterministic
- candidate rank/select authority
- soft chart-fit context
- explicit ScannerAgentInput / ScannerAgentResult

### Monitor
- deterministic
- hard actionable entry/exit timing
- emits intent only
- explicit MonitorAgentInput / MonitorAgentResult
- no broker authority

### Commander
- deterministic orchestration and runtime routing
- no LLM
- CommanderRuntimeInput / CommanderRuntimeResult / CommanderRoutePlan
- no broker mutation authority

### Reporter
- LLM role retained
- focused reporting services behind stable public facade

### Supervisor
- safety authority unchanged

### Executor
- broker side-effect authority unchanged
- execute_owned_order remains mutation choke point
- low-risk extraction only

LLM decision roles:
- before = 2
- target after = 2
- Strategist + Reporter only

## 11. Compatibility Philosophy

The tree becomes cleaner without pretending history never existed.

Keep intentionally:
- graph node facades
- apps/operator_ui/data_access.py
- libs/reporting/trade_report_ai.py through P1.5 freeze
- selected historical M11/M13/M28 surfaces
- state/env aliases still required operationally
- Step5 safety wrappers
- historical docs/tests

Remove only with proof:
- transitional integrated_chain_support after direct consumer migration
- duplicate AgentExecutor implementation
- unused private helper re-exports
- zero-consumer runtime naming wrappers

Therefore "pretty" means:
- one canonical owner per responsibility
- explicit bounded compatibility
- not zero wrappers

## 12. Runtime Naming Cleanup

Active runtime vocabulary moves away from development milestone names.

Examples:

- m13_live_loop -> live_cycle / live_loop
- m13_tick -> runtime_tick
- m13_eod_report -> eod_report
- m13_tick_pipeline -> runtime_tick_pipeline
- legacy_m10 -> legacy_decision_pipeline
- m31_agent_chain_probe -> agent_chain_probe
- M13_LIVE_LOCK_* -> LIVE_LOOP_LOCK_*
- M28_LIFECYCLE_* -> RUNTIME_LIFECYCLE_*
- M25_BATCH_* -> OPS_BATCH_*
- M25_NOTIFY_* -> NOTIFY_*

But historical names remain where they are evidence.

Step5C/Step5D and UEF/Q program identifiers are intentionally not cosmetically renamed.

## 13. Test Tree Improvement

Current tests contain many milestone and giant-module private-seam tests.

Target organization is responsibility-oriented:

```text
tests/
  unit/
    strategist/
    scanner/
    monitor/
    commander/
    execution/
    reporting/
    operator_ui/

  integration/
    agent_chain/
    commander/
    reporting/
    operator_ui/
    execution/

  regression/
    strategist/
    scanner/
    monitor/
    commander/
    execution/

  acceptance/
    uef/
    docker/
```

Historical incident/milestone tests remain assets until explicitly migrated.

Test artifact policy:
- session-isolated temp path
- successful temp cleanup
- bounded failure evidence retention
- no unbounded repo-local pytest directories

## 14. Quantitative PREP Result

### Mapped
- ~57,847 LOC primary giant surface
- ~61,455 LOC including adjacent intraday Monitor signal engine
- 508 Python test files on source-baseline inventory
- ~468 milestone/phase/step-named file paths classified
- Strategist giant: 8,879 LOC
- Scanner giant: 4,179 LOC
- Monitor giant: 3,633 LOC
- Commander giant: 6,298 LOC
- Executor giant: 4,190 LOC
- Reporting giants: 18,743 LOC
- Operator UI/Brief giants: 11,925 LOC

### Designed façade target
- six non-Executor giant façade groups:
  53,657 LOC -> approximately 2,700-5,100 LOC
- façade/orchestrator surface shrink:
  approximately 90.5-95.0%

### Definite deletion opportunity
- Reporting unreachable legacy tail: ~1,100 LOC

### Actual implementation at PREP close
- runtime LOC deleted: 0
- runtime files changed: 0

## 15. What "Prettier" Means in Practice

Before:
- understand one subsystem by scrolling thousands of lines
- private helper monkeypatching
- state dict is the implicit API
- ownership boundaries inferred from call flow
- IO and evidence scattered
- milestone names obscure current responsibility

After target:
- start at service.py
- inspect contracts.py to know input/output
- inspect state_adapter.py to know graph compatibility
- inspect evidence.py to know observability
- inspect policy/scoring/orchestrator modules by responsibility
- graph node says where the subsystem enters, not how every rule works
- safety mutation path remains visibly centralized

This is a much more reviewable shape for Codex, Claude and humans.

## 16. P1.5 Detailed Packets Frozen

Frozen design packets cover:
- P1.5.1 / P1.5.2 Reporting
- P1.5.3 Operator UI / Operator Brief
- P1.5.4 Strategist
- P1.5.5 Scanner
- P1.5.6 Monitor
- P1.5.7 Commander/runtime
- P1.5.8 runtime naming
- P1.5.9 Executor low-risk extraction
- P1.5.10 compatibility cleanup
- P1.5.11 full regression / Docker / UEF replay / formal freeze

P1.5.0 baseline gate is defined by the master plan and final-freeze packet.

## 17. Implementation Order Remains Frozen

Implementation begins only after the upstream baseline gate is satisfied.

Order:
1. P1.5.0 baseline metadata + pytest baseline + artifact hygiene
2. P1.5.1 Reporting definite dead-code cleanup
3. P1.5.2 Reporting decomposition
4. P1.5.3 Operator UI / Brief
5. P1.5.4 Strategist
6. P1.5.5 Scanner
7. P1.5.6 Monitor
8. P1.5.7 Commander/runtime
9. P1.5.8 runtime naming
10. P1.5.9 Executor low-risk extraction
11. P1.5.10 compatibility cleanup
12. P1.5.11 full regression / Docker / UEF replay / freeze

## 18. Current Gate

P1.5 PREP:
- CLOSED

P1.5 DESIGN:
- FROZEN

P1.5 IMPLEMENTATION:
- GATED / NOT STARTED

P1.5 FORMAL FREEZE:
- NO

P1.6 IMPLEMENTATION:
- BLOCKED until P1.5 formal freeze

P1.6 PREP / framework research may be conducted separately if explicitly authorized, but it must not mutate the P1.5 runtime baseline.

## 19. Final PREP Verdict

Architecture inventory             COMPLETE
Detailed subsystem packets         COMPLETE
Agent boundary design              COMPLETE
Target package tree                FROZEN
Compatibility strategy             FROZEN
Runtime naming strategy            FROZEN
Executor safety scope              FROZEN
Full regression plan               FROZEN
Docker acceptance plan             FROZEN
UEF replay/freeze plan             FROZEN
Patch-note integration             COMPLETE
Runtime implementation             NOT STARTED
Runtime code changed on design     NONE
P1.5 PREP                          CLOSED
