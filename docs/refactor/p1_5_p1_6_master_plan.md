# Agentra P1.5 / P1.6 Master Plan

Status: P1.5 PREP CLOSED / DESIGN FROZEN / IMPLEMENTATION GATED  
Date: 2026-10-07

## 1. Purpose

P1.5 and P1.6 prepare Agentra for continued strategy development without changing trading semantics during the refactor.

P1.5 makes each agent a clear, independently callable component with explicit contracts.
P1.6 evaluates and, only if justified, modernizes the orchestration layer.

The current production topology and safety authority remain unchanged throughout P1.5.

## 2. Program Order

```text
NOW
 |
 +-- P1.2  UEF cross-day observation
 |
 +-- P1.3  Docker / operational acceptance
 |          -> regression GREEN
 |          -> leakage NONE
 |          -> baseline SHA/tag
 |
 +-- 2.E5-A / P1.5
 |      Structural Modular Refactor
 |
 +-- 2.E5-B / P1.6
 |      Orchestration Modernization
 |
 +-- 2.E6 / P2
 |      Strategy Program Integration
 |
 +-- P3
 |      Safety 5D -> 5E -> 6
 |
 +-- P4
 |      Q100 + Reporter v2
 |
 +-- P5
 |      Evidence Memory / Obsidian
 |
 +-- P6
 |      Self-improvement
 |
 +-- P7
 |      Agentra V2 Freeze
 |
 +-- P8
        Paper / stable-data experiments
```

## 3. P1.2 / P1.3 Gate

P1.5 implementation is blocked until the baseline is frozen.

Required baseline record:

```text
P1.2 PASS / FROZEN
P1.3 PASS / FROZEN
FULL REGRESSION GREEN
EXECUTION AUTHORITY LEAKAGE NONE
PRODUCTION-WRITE LEAKAGE NONE
BASELINE SHA <sha>
BASELINE TAG <tag>
```

P1.2 daily checks remain operational until freeze:
- UEF-7 candidate conservation / evidence completeness
- UEF-8 pair conservation / unique pair IDs / status counts / unexpected COMPARABLE
- UEF-9 binding / authority
- replay determinism
- production-write leakage
- trading-authority leakage

## 4. 2.E5-A / P1.5

Name: **Mechanical Modular Refactor + Agent Boundary Restoration**

P1.5 has four coordinated tracks:

- Architecture
- Naming
- Test architecture
- Documentation architecture

They are applied per subsystem, not as three unrelated mega-projects.

### P1.5 Goals

- preserve behavior
- restore explicit agent boundaries
- create explicit agent input/output contracts
- make agent cores callable without the top-level runtime
- isolate IO, policy, orchestration, authority and evidence responsibilities
- remove development-milestone naming from production runtime code
- restructure tests alongside each subsystem
- refactor canonical/current documentation alongside each subsystem while preserving historical audit evidence
- eliminate unbounded test-artifact accumulation
- retain compatibility seams until consumers are migrated

### P1.5 Non-goals

- no new strategy
- no new trading semantics
- no new LLM decision point
- no production topology change
- no dynamic agent reordering
- no new autonomous planner
- no weakening of Supervisor / Executor safety boundaries
- no orchestration-framework migration

## 5. P1.5 Agent Model

Target concept:

```text
Runtime / Graph Adapter
        |
        v
Agent Input Contract
        |
        v
Agent Component
        |
        +-- pure policy / calculation
        +-- explicit adapters / IO
        +-- evidence surface
        |
        v
Agent Output Contract
        |
        v
Runtime State Patch
```

Expected standalone surfaces:

```text
run_strategist(input) -> StrategistOutput
run_scanner(input) -> ScannerOutput
run_monitor(input) -> MonitorOutput
evaluate_supervisor(input) -> SupervisorOutput
run_reporter(input) -> ReporterOutput
execute(approved_request) -> ExecutorOutput
```

Executor remains authority-dependent even when component-callable.

## 6. LLM Boundary

P1.5 must not increase the number of LLM decision roles.

```text
Commander   deterministic orchestration / policy
Strategist  LLM ALLOWED
Scanner     deterministic
Monitor     deterministic
Supervisor  deterministic safety authority
Executor    deterministic side effects
Reporter    LLM ALLOWED
```

Acceptance:
`NEW LLM DECISION POINTS = 0`

## 7. P1.5 Batch Order

1. P1.5.0 baseline metadata + pytest baseline + artifact hygiene
2. P1.5.1 Reporting definite dead-code cleanup
3. P1.5.2 Reporting decomposition + corresponding test decomposition
4. P1.5.3 Operator UI / Operator Brief decomposition
5. P1.5.4 Strategist contracts + decomposition
6. P1.5.5 Scanner orchestration decomposition
7. P1.5.6 Monitor orchestration decomposition
8. P1.5.7 Commander/runtime decomposition
9. P1.5.8 milestone/runtime naming cleanup
10. P1.5.9 Executor low-risk extraction
11. P1.5.10 compatibility-wrapper cleanup
12. P1.5.11 full regression + Docker + UEF replay + P1.5 freeze

Supervisor CAS/idempotency and broker-mutation semantics are safety-locked until late review.

## 8. 2.E5-B / P1.6

Name: **Orchestration Modernization**

P1.6 starts only after P1.5 freeze.

Compare the same framework-neutral agent components under:

- current Agentra custom runtime
- LangGraph 1.x
- pydantic-graph

Initial shadow graph:

```text
Strategist -> Scanner -> Monitor -> Supervisor
```

Executor is excluded from the initial orchestration benchmark.

Compare:
- LOC / boilerplate
- type safety
- state handling
- conditional routing
- cycle support
- checkpoint / resume
- replay
- failure recovery
- observability
- testability
- runtime overhead
- maintenance cost

Adopt a new framework only if it materially improves the system while preserving behavior and safety.

P1.6 does not add new trading flows.

## 9. 2.E6 / P2 Strategy Program Integration

Only after P1.5/P1.6 structural freeze.

Integrate and normalize strategy programs and contexts such as:
- Q10
- Q12
- regime
- overnight/global context
- BTC
- US/SOX
- JPY
- Samsung / SK Hynix / KOSPI / KOSDAQ relationships

The purpose is to add strategy work onto the cleaned architecture instead of refactoring newly added complexity later.

## 10. P3 Safety

Sequence remains:

```text
5D -> 5E -> 6
```

Safety finalization is performed on the structurally stable runtime.

## 11. P4 Q100 + Reporter v2

Q100 and Reporter v2 remain after strategy and safety stabilization.

Rationale:
- evaluation attribution must target a stable strategy/execution system
- reporting quality should not be calibrated against moving semantics

## 12. P5-P8

- P5: Evidence Memory / Obsidian integration
- P6: Self-improvement / controlled feedback loop
- P7: Agentra V2 formal freeze
- P8: paper experiments and stable-data collection

Research-question, methodology, metric and ablation design may proceed earlier; final empirical claims should use the stable system.

## 13. Cloud Delivery Model

```text
GPT
  architecture / detailed design
        |
        v
Codex Cloud
  implementation + pytest + failure repair
        |
        v
Claude Cloud
  independent audit + independent pytest
        |
        v
PASS / PASS_WITH_FINDINGS / FAIL
```

Codex is the implementer.
Claude is the independent verifier.
Architecture ambiguity should be resolved before Codex receives a batch.


## P1.5 PREP Closure

P1.5 preparation/design is formally closed on 2026-10-07.

Authority:
- docs/refactor/p1_5_prep_closure_report.md
- detailed implementation packets indexed by docs/refactor/README.md

Important:
- this is a DESIGN/PREP freeze, not a runtime implementation freeze
- P1.5 implementation remains gated until the upstream implementation baseline is formally frozen
- no P1.5 runtime Python change is authorized by this closure
- P1.6 implementation remains blocked until P1.5 formal freeze


## 2026-10-08 P1.5.1–P1.5.11 Responsibility Alignment Addendum

Authority: [p1_5_1_to_11_responsibility_alignment_v1_1.md](p1_5_1_to_11_responsibility_alignment_v1_1.md).

All eleven stages were reviewed against the original responsibility-minimal constitution. The v1.0 stage-specific implementation packets and stage order remain intact. A stage cannot close solely on giant-file LOC reduction or focused pytest: canonical single Owner per responsibility, independently callable Agent contracts, explicit state adapters and IO/authority boundaries, consumer-proven compatibility exceptions and test preservation are mandatory evidence. P1.5.10 receives wrapper-debt carryovers; P1.5.11 must include an architecture ownership ledger and test-conservation proof alongside existing full pytest, Docker, UEF and independent safety gates. Executor remains the intentional safety-constrained façade-size exception. This is a design supplement only, not retroactive approval of implementation or P1.2/P1.3 baseline freeze.
