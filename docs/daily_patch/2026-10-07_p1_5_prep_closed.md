# 2026-10-07 — P1.5 PREP Closed / Design Frozen

## Scope

P1.5 preparation and design closure only.

No runtime Python, Docker runtime, UEF semantics, strategy, execution guard, Step5C/Step5D, broker behavior, state schema or production topology was changed.

## PREP Closure

P1.5 PREP is now formally:

- CLOSED
- DESIGN FROZEN
- IMPLEMENTATION GATED

The detailed implementation packets for P1.5.1-P1.5.11 are complete and indexed.

P1.5 implementation remains blocked until the upstream implementation baseline is formally frozen.

## Quantified Refactor Surface

Primary mapped giant surface:

- Reporting giants: 18,743 LOC
- Operator UI / Brief giants: 11,925 LOC
- Strategist node: 8,879 LOC
- Scanner node: 4,179 LOC
- Monitor node: 3,633 LOC
- Commander runtime: 6,298 LOC
- Executor execute_from_packet: 4,190 LOC

Primary total:
- 57,847 LOC

Adjacent Monitor signal hotspot:
- intraday_monitor_signals.py: ~3,608 LOC

Mapped giant/hotspot surface including the adjacent signal engine:
- ~61,455 LOC

## Target Façade Shrink

For the six non-Executor giant façade groups:

- current giant surface: 53,657 LOC
- target façade/orchestrator surface: ~2,700-5,100 LOC
- target façade shrink: ~90.5-95.0%

This is NOT a claim that repository total LOC falls by 50k.

Most logic moves into focused owners:
- contracts
- services
- state adapters
- deterministic policy/scoring
- evidence/observability
- IO/persistence
- compatibility facades

Definite deletion opportunity already identified:
- approximately 1,100 LOC unreachable Reporting legacy tail

## Executor Exception

execute_from_packet.py remains intentionally large.

P1.5.9 only permits low-risk extraction of:
- observability projection
- canonical artifact coordination
- optional pure order-view helpers

Supervisor/guard/readiness/Step5C/BrokerOutcome/UNKNOWN/cancel-recovery sequencing remains centralized and safety-locked.

## Target Shape

The architecture moves from giant graph-node/runtime modules to:

- thin graph/runtime adapters
- explicit Agent input/result contracts
- focused service modules
- explicit state adapters
- dedicated evidence/observability owners
- stable public compatibility facades
- centralized safety mutation boundary

Core target packages include:

- libs/runtime/strategist/
- libs/runtime/scanner/
- libs/runtime/monitor/
- libs/runtime/commander/
- libs/reporting/trade_report/
- libs/reporting/trade_report_markdown/
- libs/reporting/trade_story/
- apps/operator_ui/brief/
- apps/operator_ui/views/
- libs/execution/ low-risk observational helpers

## Authority Model Preserved

- Strategist: LLM framing
- Scanner: deterministic candidate rank/select
- Monitor: deterministic actionable timing / intent only
- Commander: deterministic orchestration
- Reporter: LLM reporting
- Supervisor: safety approval
- Executor: broker side-effect authority

LLM decision roles remain 2 -> 2:
- Strategist
- Reporter

## Naming / Compatibility

Active runtime milestone names receive domain names with compatibility aliases.

Historical:
- docs
- regression tests
- Step5 identifiers
- UEF/Q program identifiers
- artifact/deploy compatibility paths

are not cosmetically rewritten.

## Testing / Freeze

P1.5.11 defines the final acceptance sequence:
- baseline/candidate identity
- targeted regression
- full pytest
- artifact hygiene
- UEF frozen-manifest + deterministic replay
- Step5 safety / authority leakage
- Docker source parity / ownership / restart / SIGTERM
- compatibility/docs/security review
- Claude independent audit
- human approval
- freeze tag

## Truth at PREP Close

Actual runtime LOC removed:
- 0

Runtime Python files changed by P1.5 design branch:
- 0

Production behavior changed:
- 0

This closure freezes the implementation design, not the implementation itself.

## Authority

See:
- docs/refactor/p1_5_prep_closure_report.md
- docs/refactor/p1_5_p1_6_master_plan.md
- docs/refactor/README.md

## Status

P1_5_PREP_CLOSED = YES
P1_5_DESIGN_FROZEN = YES
P1_5_IMPLEMENTATION_STARTED = NO
P1_5_FORMAL_FREEZE = NO
