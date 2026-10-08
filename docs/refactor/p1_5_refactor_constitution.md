# P1.5 Refactor Constitution

Status: DESIGN AUTHORITY  
Date: 2026-10-07

## 1. Primary Rule

P1.5 is behavior-preserving structural refactoring.

The target is not "smaller files" by itself.
The target is explicit responsibility, explicit contracts, independently testable agent components, and a replaceable orchestration boundary.

## 2. Architectural Layers

```text
PURE
calculation / normalize / rank / deterministic policy

ORCHESTRATION
agent sequencing / runtime routing / state adaptation

IO
broker / file / sqlite / API / market data

AUTHORITY
Commander policy / Supervisor approval / Executor ownership

EVIDENCE
UEF / audit / observability / reporting
```

Cross-layer mixing should be reduced.

## 3. Classification Vocabulary

Each existing function or module is classified as:

- KEEP: remains at current responsibility boundary
- MOVE: implementation relocates to an owning module
- WRAPPER: compatibility/public import/monkeypatch seam remains temporarily
- DEAD: proven unreachable/obsolete; remove only after evidence
- SAFETY-LOCK: do not structurally alter until safety review permits it

## 4. Agent Modularity Acceptance

Required:

```text
Strategist standalone callable   YES
Scanner standalone callable      YES
Monitor standalone callable      YES
Supervisor standalone callable   YES
Reporter standalone callable     YES
Executor component callable      YES, authority contract required

Explicit input contract          YES
Explicit output contract         YES
Deterministic fixture test       YES where applicable
Replayable                       YES
Hidden peer mutation             NO
Hidden runtime dependency        minimized / explicit
Arbitrary production ordering    NO
Validated future composition     structurally possible
```

## 5. Production Topology

P1.5 preserves the existing production behavior and topology.

No new composition is enabled during P1.5.

Alternative compositions such as Scanner-only, Strategist-only, Scanner -> Strategist -> Scanner, research graphs or shadow graphs are future features, not P1.5 behavior.

## 6. LLM Policy

Only Strategist and Reporter may retain LLM roles.

P1.5 must not introduce an LLM into:
- Commander decision routing
- Scanner
- Monitor
- Supervisor
- Executor

Supervisor and Executor remain deterministic safety/execution authorities.

## 7. Contract Policy

Prefer typed Pydantic v2 contracts for agent boundaries where practical.

Core stability rules:
- do not remove required fields
- additive optional fields are preferred
- semantic changes require a new field or version
- keep old import/schema facades while consumers migrate
- do not silently reinterpret an existing field

Large legacy contract modules may be split behind compatibility facades.

## 8. Naming Policy

Production code must use domain/responsibility names, not development milestones.

Normally remove from runtime names:
- m10_
- m11_
- m13_
- stepX_
- phaseX_
- fixX_
- final2_
- temp_/new_ when they are merely historical labels

Do not remove genuine domain/protocol identifiers:
- UEF-7/8/9
- Q10/Q12/Q100 when they identify strategy/evaluation programs

State-key renames require compatibility migration:
1. read new canonical key
2. fallback-read legacy key
3. write new canonical key
4. migrate all consumers
5. remove legacy alias only after proof

## 9. Size Guidance

These are review thresholds, not mechanical rules.

```text
ordinary function       ~10-50 LOC
complex function        ~50-80 LOC
orchestration function  ~50-120 LOC

module target            ~100-300 LOC
agent facade             ~150-350 LOC
orchestrator             ~200-400 LOC

500+ LOC                 REVIEW
800+ LOC                 normally prohibited
1000+ LOC                target zero
```

Responsibility is more important than raw LOC.

## 10. Test Architecture

Target organization:

```text
tests/
  unit/
    strategist/
    scanner/
    monitor/
    supervisor/
    executor/
    reporter/
    commander/
    reporting/
    contracts/
  integration/
    runtime/
    execution/
    reporting/
    persistence/
    operator_ui/
  regression/
    trading/
    reporting/
    incidents/
  acceptance/
    uef/
    docker/
    live/
  fixtures/
```

Do not migrate all tests in one bulk move.
Move and clean tests with the subsystem being refactored.

Test classification:
- KEEP
- MOVE
- RENAME
- MERGE
- DEAD
- HISTORICAL_REGRESSION
- ACCEPTANCE

Historical incident regression tests are assets, not cleanup noise.

## 11. Test Artifact Hygiene

All test temporary artifacts must use session-isolated locations where practical.

```text
PASS -> temporary artifacts automatically cleaned
FAIL -> diagnostic evidence retained
      -> bounded by recent-N or retention period
```

Do not allow recurring pytest runs to accumulate unbounded repo files/directories.

## 12. Required Batch Validation

Codex Cloud must:
1. implement only the specified batch
2. run targeted pytest
3. fix implementation-caused failures
4. run affected integration/regression tests
5. run required full pytest
6. report exact pass/fail/skip counts
7. update UI-linked patch notes
8. leave successful temporary artifacts cleaned
9. preserve failed evidence only under bounded retention

Claude Cloud must independently audit:
- diff
- architecture adherence
- behavior preservation
- hidden coupling
- contract compatibility
- test weakening/removal
- authority leakage
- production-write leakage
- UEF invariants

Verdict:
- PASS
- PASS_WITH_FINDINGS
- FAIL

## 13. Forbidden Codex Autonomy

Codex must not independently:
- change an agent boundary
- add a dependency
- add an LLM call
- change state semantics
- change trading topology
- introduce a breaking DTO change
- weaken Supervisor authority
- reorder Executor/broker mutations
- add features outside batch scope
- remove compatibility without consumer proof
- delete tests because they appear redundant

If such a change appears necessary, stop that part and report the finding.

## 14. Safety Invariants

```text
Trading semantics                  SAME
Production graph topology          SAME
Agent ordering                     SAME
LLM decision roles                 2 -> 2
Monitor direct broker execution    NEVER
Execution without approval         NEVER
Guard override weakening           NEVER
CAS/idempotency weakening          NEVER
Broker mutation ordering           SAME unless separately approved
UEF semantics                      SAME
Replay determinism                 NO REGRESSION
Production-write leakage           NONE
Trading-authority leakage          NONE
```

## 15. Branch Policy

The design branch may contain planning/documentation only.

The first P1.5 implementation branch must be created from the P1.2/P1.3 frozen baseline SHA/tag.

Do not treat the design-branch creation SHA as the implementation baseline.

## 16. Documentation Policy

P1.5 refactors documentation together with code, naming and tests.

Rules:
- current canonical documents must describe the current responsibility model
- historical incident/freeze/milestone records are not rewritten to look modern
- documentation movement requires inbound-link and patch-note-source analysis
- `docs/daily_patch/` remains the detailed technical audit history
- the structured Patch Notes UI source remains the existing JSON/Markdown pair until an explicitly tested adapter migration changes it
- stale navigation pages may be rewritten; historical evidence pages are preserved
- subsystem refactor completion requires corresponding canonical documentation and UI-linked patch-note updates
