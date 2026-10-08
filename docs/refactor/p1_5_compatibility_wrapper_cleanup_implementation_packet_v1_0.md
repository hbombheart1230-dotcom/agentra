# P1.5.10 Compatibility-Wrapper Cleanup Implementation Packet v1.0

Status: DESIGN COMPLETE / IMPLEMENTATION GATED
Date: 2026-10-07
Design branch: design/p1.5-p1.6-modernization
Scope: P1.5.10 compatibility-wrapper cleanup

## 1. Purpose

P1.5.10 removes only compatibility seams proven to have no active runtime, deployment, operator, test, or public-import consumer.

This phase is NOT a bulk wrapper deletion.

The repository intentionally accumulated compatibility facades during P1.5.1-P1.5.9 so structural extraction could be behavior-preserving. P1.5.10 is the proof-and-cleanup phase.

Primary goals:
- identify every intentionally retained compatibility seam
- classify active vs historical vs safety-critical usage
- migrate remaining active production consumers to canonical owners
- remove only redundant wrappers with positive consumer proof
- leave historical and safety seams intact when provenance/risk outweighs cleanup value

## 2. Cleanup Principle

A wrapper is removable only when all active consumers are proven migrated.

Required proof sources:
1. repository import/reference search
2. runtime entrypoint inspection
3. deploy/scheduler/service template inspection
4. operator UI/API import inspection
5. active tests
6. current docs/runbooks
7. state/env/schema compatibility usage
8. Docker/runtime smoke
9. full regression
10. UEF / Step5 safety replay where applicable

Historical docs/tests do not count as active runtime consumers, but they may still require import compatibility if they execute in the full test suite.

## 3. Classifications

### REMOVE_NOW

Only when:
- no production import
- no active CLI/deploy usage
- no current test import except tests specifically intended for removal
- no schema/state/env consumer
- full targeted regression passes after deletion

### MIGRATE_THEN_REMOVE

Active consumers still exist, but canonical owner is already known.

Process:
1. migrate consumers
2. retain wrapper for one tranche
3. prove no non-compat consumer remains
4. remove wrapper
5. run regression

### KEEP_STABLE_FACADE

The facade itself is a deliberate public boundary.

Examples:
- graph node entrypoints
- Operator UI data access stable import
- current canonical runtime API

Do not remove merely because implementation is elsewhere.

### HISTORICAL_COMPATIBILITY

Historical milestone/test path still executed for regression/provenance.

Keep unless test migration is explicitly approved.

### SAFETY_LOCK

Execution/ownership/Step5/UEF compatibility seam.

Do not remove in P1.5.10 unless dedicated safety proof exists.

### CONTRACT_ALIAS

Serialized state/env/schema/path compatibility.

Removal requires migration evidence, not just Python import proof.

## 4. Cross-P1.5 Wrapper Inventory

P1.5 design packets intentionally retained wrappers in:

- Reporting
- Operator UI / Brief
- Strategist
- Scanner
- Monitor
- Commander/runtime
- runtime naming aliases
- Executor

P1.5.10 is the only phase allowed to evaluate deletion of those wrappers.

## 5. Commander Compatibility Surface

### libs/runtime/commander/integrated_chain_support.py

Current source explicitly states:
- compatibility export surface
- new code should import nodes.py, shadow_runtime.py, execution.py, fast_paths.py directly

Current active evidence:
- graphs/commander_runtime.py still imports multiple symbols from integrated_chain_support.py

Classification:
MIGRATE_THEN_REMOVE

Migration:
- replace commander_runtime imports with direct canonical owner imports
- scan tests/scripts for direct integrated_chain_support imports
- retain wrapper through the migration commit
- delete only after all active consumers are canonical

Do not remove before Commander C9 facade migration is complete.

### graphs/nodes/commander_node.py

Thin graph wrapper over canonical runtime.

Classification:
KEEP_STABLE_FACADE

This is an intentional graph-node boundary, not accidental compatibility noise.

### libs/agent/commander.py

Source explicitly identifies itself as legacy compatibility scaffolding.

It depends on:
- libs.agent.strategist
- libs.agent.scanner
- libs.agent.monitor
- libs.agent.reporter
- libs.agent.executor

Classification:
HISTORICAL_COMPATIBILITY / MIGRATE_THEN_REMOVE candidate

Removal gate:
- no current runtime import
- no active tests instantiate Commander
- no demos/operator tools rely on CommandResult
- run_canonical bridge has no consumer
- legacy Agent stack can be retired as one coherent unit

Do not delete one child adapter while legacy Commander still imports it.

## 6. Strategist Legacy Adapter

### libs/agent/strategist.py

Source explicitly states:
- Legacy strategist compatibility adapter
- canonical behavior is graphs/nodes/strategist_node.py
- retained for M15/M20 compatibility
- Plan is a compatibility DTO

Classification:
HISTORICAL_COMPATIBILITY

Potential removal is coupled to libs/agent/commander.py and libs/agent/scanner.py because Scanner imports Plan.

Do not remove Plan independently.

Preferred P1.5.10 action:
- prove current production runtime does not import libs.agent.strategist
- retain if historical tests still execute
- otherwise archive/remove the entire legacy Agent stack coherently

Private wrappers in strategist_node created during P1.5.4 are separate:
- remove only if direct test imports are migrated
- keep graph state adapter and canonical public node facade

## 7. Scanner Compatibility Surfaces

### libs/agent/scanner.py

Explicit legacy adapter.

Classification:
HISTORICAL_COMPATIBILITY

Coupled to legacy Plan/Commander stack.

Do not delete independently if libs/agent/commander.py remains.

### graphs/nodes/scan_candidates.py

Explicit compatibility candidate-stage helper.

Known active regression consumer:
- tests/test_m11_2_scanner.py imports scan_candidates directly

Classification:
HISTORICAL_COMPATIBILITY

It should not be used by current integrated-chain runtime.

Removal options:
- keep permanently as historical regression fixture surface, or
- migrate M11 test to archived fixture/non-runtime package and then remove

Default P1.5.10 recommendation:
KEEP, because cleanup value is low and provenance value is high.

### graphs/nodes/select_candidate.py

Historical M11-2 selector with placeholder cheap-first logic.

Known active regression consumer:
- tests/test_m11_2_scanner.py imports it directly

Classification:
HISTORICAL_COMPATIBILITY

Default:
KEEP until historical test policy explicitly changes.

It must never be reintroduced into canonical Scanner runtime.

### graphs/nodes/scanner_node.py private wrappers

P1.5.5 retained private import/monkeypatch seams.

Classification:
MIGRATE_THEN_REMOVE

Remove only after:
- unit tests import canonical owner modules
- monkeypatch targets migrate
- scanner_node facade still exposes only true public graph entrypoint

## 8. Monitor Compatibility Surfaces

### libs/agent/monitor.py

Explicit no-op legacy Monitor interface.

Classification:
HISTORICAL_COMPATIBILITY

Coupled to libs/agent/commander.py.

Recommended:
remove only with legacy Agent stack retirement.

### graphs/nodes/monitor_node.py private wrappers

P1.5.6 retained helper aliases for direct imports and monkeypatch tests.

Classification:
MIGRATE_THEN_REMOVE

Migration:
- move tests to canonical monitor modules
- preserve monitor_node itself as graph facade
- delete only unused helper re-exports

### libs/runtime/intraday_monitor_signals.py

P1.5.6 design defines it as compatibility facade after signal-engine decomposition.

Classification:
KEEP_STABLE_FACADE during P1.5

Reason:
public/runtime imports are broad and signal semantics are safety-sensitive.

Do not delete in P1.5.10 unless MO7 migration proves all active imports canonical and full Monitor regression remains green.

Default recommendation:
KEEP through P1.5 freeze.

## 9. Operator UI Compatibility Surfaces

### apps/operator_ui/data_access.py

Source:
- explicit thin compatibility facade
- preserves import path apps.operator_ui.data_access
- delegates to data_access_core

Known active test consumer:
- tests/test_operator_ui_data_access_phase2.py imports apps.operator_ui.data_access directly

Classification:
KEEP_STABLE_FACADE

This facade is a useful application-layer public boundary.

Do not remove in P1.5.10.

### apps/operator_ui/data_access_reports.py

Thin compatibility facade over libs.reporting.trade_read_model.

Known active test consumer:
- tests/test_operator_ui_data_access_phase2.py imports it directly

Classification:
KEEP_STABLE_FACADE or MIGRATE_THEN_REMOVE only if Operator UI current modules no longer require the path.

Default recommendation:
KEEP through freeze.

### apps/operator_ui/data_access_core.py wrappers

After P1.5.3 decomposition, private helper wrappers may become cleanup candidates.

Classification:
MIGRATE_THEN_REMOVE

But:
- data_access_core itself may remain a small compatibility/orchestration facade
- only redundant helper implementations/re-exports should be removed

### data_access_linkage legacy paths

Fields named legacy_* represent artifact compatibility, not Python wrapper noise.

Classification:
CONTRACT_ALIAS

Do not delete based only on code-reference search.

Artifact corpus compatibility must be proven first.

## 10. Reporting Compatibility Surfaces

### libs/reporting/trade_report_ai.py

P1.5.1/P1.5.2 deliberately retain it as compatibility facade.

Classification:
KEEP_STABLE_FACADE for P1.5 freeze

Reason:
large number of reporting/test imports and runtime report generation still use this public module.

Internal private wrapper functions:
MIGRATE_THEN_REMOVE after tests use canonical owner modules.

Do not remove the facade itself in P1.5.10 unless consumer proof is exceptionally strong.

### libs/reporting/trade_report_ai_summary_adapter.py

This is not merely a legacy wrapper.
It owns concrete summary-evaluation normalization, prompting and deterministic payload logic.

Classification:
KEEP CANONICAL OWNER

Do not delete because the filename says adapter.

### Reporter script wrappers

tests/test_reporter_script_wrappers.py explicitly protects script-level compatibility.

Classification:
HISTORICAL/CLI COMPATIBILITY

Keep unless scripts are formally deprecated and current operator entrypoints migrate.

## 11. Executor Compatibility Surfaces

### libs/agent/executor.py
### libs/agent/executor/agent_executor.py

Both define an AgentExecutor wrapper around ExecutorAgent with materially equivalent submit behavior.

This is a strong deduplication candidate.

Classification:
MIGRATE_THEN_REMOVE

Canonical recommendation:
- libs/agent/executor/agent_executor.py owns AgentExecutor
- libs/agent/executor.py becomes a thin re-export temporarily
- update libs/agent/commander.py and current consumers to package import
- after proof, remove duplicate class implementation

Do not alter ExecutorAgent or execution safety semantics.

### libs/agent/executor/executor_agent.py

Contains actual legacy two-phase execution behavior.

Classification:
HISTORICAL_COMPATIBILITY + SAFETY-SENSITIVE

Do not delete merely because execute_from_packet is canonical integrated runtime.

Legacy approval tooling may still depend on it.

### graphs/nodes/execute_from_packet.py private wrappers

Unknown quarantine wrappers and Step5 private imports are safety regression seams.

Classification:
SAFETY_LOCK

Default:
KEEP through P1.5 freeze.

Do not remove in P1.5.10 unless a dedicated safety consumer audit proves safe.

## 12. Core Event Logger Compatibility

### libs/core/event_logger_compat.py

Purpose:
handles multiple historical EventLogger constructor signatures.

Classification:
MIGRATE_THEN_REMOVE candidate

Removal gate:
- canonical EventLogger constructor is stable
- all call sites use canonical constructor
- no tests inject alternate EventLogger signatures
- no older runtime/plugin path requires compatibility

If uncertainty remains:
KEEP, because file is tiny and low maintenance cost.

Cleanup value is low.

## 13. Runtime Naming Wrappers from P1.5.8

P1.5.8 intentionally creates canonical names plus legacy aliases for:

- M13 live loop/tick/EOD
- legacy M10 decision pipeline
- M28 deployment/runtime tooling
- M31 agent-chain probe
- M13/M28/M31 env names
- M25 batch/notification env names
- runtime_tick_pipeline state key

P1.5.10 may remove only aliases proven unused.

Default policy:

### Python module/CLI aliases
MIGRATE_THEN_REMOVE

Possible after:
- active runtime imports canonical
- deploy files canonical
- operator docs canonical
- historical tests are either migrated or explicitly exempted

### State/env aliases
CONTRACT_ALIAS

More conservative.
Removal requires:
- runtime telemetry shows canonical key use
- no deployment env file uses legacy key
- Docker/host task definitions audited
- current operator docs updated
- conflict/fallback tests retired intentionally

### Lock/artifact/deploy paths
KEEP

P1.5.10 does not rename/remove compatibility paths unless separate operational migration has been completed.

## 14. M10/M11/M13 Historical Pipeline Surfaces

### graphs/pipelines/m10_live_pipeline.py

After P1.5.8 canonical legacy_decision_pipeline exists:
- m10 module becomes legacy wrapper

Classification:
HISTORICAL_COMPATIBILITY / MIGRATE_THEN_REMOVE

If runtime still accepts legacy_m10 mode, keep wrapper or equivalent alias through freeze.

### graphs/pipelines/m11_live_pipeline.py
### graphs/pipelines/m11_2_live_pipeline.py

Historical pipeline implementations.

Classification:
HISTORICAL_COMPATIBILITY

Do not delete solely for naming cleanliness.

Required first:
- prove no runtime path dispatches them
- preserve historical tests
- decide whether archive package is preferable

Default P1.5.10:
KEEP.

## 15. Runtime Modes Are Not Wrappers

Do not treat:
- graph_spine
- decision_packet
- integrated_chain

as compatibility wrappers merely because some are older.

They are current RuntimeMode values.

P1.5.10 may only retire a runtime mode if:
- master plan explicitly approves it
- no production configuration uses it
- topology change is separately reviewed

Current P1.5 rule:
DO NOT REMOVE runtime modes.

## 16. State Compatibility Keys

Strategist/Scanner/Monitor/Commander adapters preserve many graph-state fields.

P1.5.10 does not mass-delete state keys.

State key removal requires:
1. canonical producer migrated
2. every current consumer migrated
3. replay/fixture corpus checked
4. reporting/operator UI checked
5. compatibility tests added then retired intentionally
6. full replay/regression
7. patch note / schema documentation

Default:
state compatibility aliases survive P1.5 freeze unless obviously private and unconsumed.

## 17. Private Test Seams

Many P1.5 packets identified direct private imports and monkeypatch targets.

P1.5.10 target pattern:

Before:
tests import graphs.nodes.X._private_helper

After:
tests import canonical owner helper

Then:
graph node wrapper can remove _private_helper alias.

Do not:
- delete test
- weaken assertion
- monkeypatch a different behavior just to make cleanup pass

Migration must preserve test intent.

## 18. Historical Regression Policy

Historical tests such as:
- M11 scanner
- M13 runtime
- M28 deployment
- Step5 execution
- incident regressions

remain assets.

A historical test may continue importing a legacy path if that path itself is the historical behavior under test.

Do not distort provenance for cosmetic cleanup.

If removing the runtime wrapper is desirable:
- move historical implementation to an explicitly historical test fixture/module
- keep test meaning
- do not silently rewrite expected behavior

## 19. Wrapper Cost vs Risk Rule

Delete only when maintenance value is real.

Tiny, stable, side-effect-free compatibility wrappers may remain permanently if:
- deletion creates provenance risk
- deletion forces historical test rewrite
- wrapper has negligible complexity
- wrapper clearly points to canonical owner

P1.5 success is not measured by wrapper count reaching zero.

It is measured by:
- one canonical implementation per responsibility
- no hidden duplicate business logic
- no active production dependency on obsolete implementation
- compatibility surfaces being explicit and bounded

## 20. Strong Cleanup Candidates

### Candidate A — integrated_chain_support.py

Status:
active consumer still exists in commander_runtime.

Action:
MIGRATE direct imports first, then consider deletion.

### Candidate B — duplicate AgentExecutor implementation

Status:
two equivalent class implementations exist.

Action:
choose package implementation as canonical, convert top-level module to re-export, then delete duplicate implementation when consumers prove migrated.

### Candidate C — private graph-node helper re-exports

Across Strategist/Scanner/Monitor/Commander.

Action:
migrate tests to canonical owners, then remove private aliases.

### Candidate D — M13/M28/M31 Python wrapper modules after P1.5.8

Action:
remove only aliases with zero active imports/CLI/deploy usage.

## 21. Weak Cleanup Candidates / Default Keep

- apps/operator_ui/data_access.py
- trade_report_ai.py facade
- graph node entrypoints
- intraday_monitor_signals.py facade through freeze
- scan_candidates.py historical stage
- select_candidate.py historical stage
- Step5 safety wrappers
- legacy artifact path aliases
- runtime state compatibility keys
- legacy env fallback until deployment audit

## 22. Consumer-Proof Manifest

P1.5.10 implementation should create:

docs/refactor/p1_5_compatibility_inventory.md

Each row:

| seam | canonical owner | classification | runtime refs | test refs | deploy refs | docs refs | action | removal proof |
|---|---|---|---:|---:|---:|---:|---|---|

Required statuses:
- ACTIVE
- TEST_ONLY
- HISTORICAL_ONLY
- ZERO_CONSUMER
- SAFETY_LOCK
- CONTRACT_ALIAS

A removal PR/commit must reference the row.

## 23. Static Search Rules

For every candidate, search:
- exact module path
- exact imported symbol
- wildcard/re-export imports
- dynamic __import__
- string module names
- CLI script path
- subprocess invocations
- deploy/scheduler templates
- README/runbook commands
- tests
- Docker compose / task scheduler definitions

Do not rely on one grep pattern.

## 24. Runtime / Operational Proof

For wrapper paths related to runtime entrypoints/config:

Check:
- Docker compose
- Windows scheduled tasks/templates
- Linux service templates
- host launch scripts
- .env / env template
- operator runbook
- healthcheck
- startup preflight
- closeout tool
- CI/test commands

Python code zero-consumer is insufficient if an ops command still invokes the old script.

## 25. Implementation Batches

### CW1 — Compatibility inventory

Create the manifest.

No deletions.

Populate:
- owner
- classification
- active consumer evidence
- intended action

### CW2 — Canonical consumer migration

Migrate active current code away from transitional wrappers.

Priority:
1. Commander integrated_chain_support direct imports
2. duplicated AgentExecutor owner
3. private helper imports in current non-historical tests
4. current scripts to canonical P1.5.8 entrypoints

No wrapper deletion yet.

### CW3 — Zero-consumer pure wrapper cleanup

Delete only:
- pure re-export wrappers
- duplicate implementations
- private aliases

where inventory proves ZERO_CONSUMER after CW2.

Run targeted tests after each subsystem.

### CW4 — Historical/test-only review

For TEST_ONLY / HISTORICAL_ONLY seams:
- keep by default
- remove only if test can preserve provenance through explicit historical fixture relocation

No cosmetic test rewrite.

### CW5 — Config alias review

Review P1.5.8 env/state aliases.

Default:
KEEP through P1.5 freeze unless operational usage proof is complete.

Do not remove lock/artifact path compatibility in this batch.

### CW6 — Safety wrapper review

Review Executor/Step5/UEF wrappers.

Default:
KEEP.

Removal requires separate safety proof and Claude independent audit.

### CW7 — Full compatibility regression

Run:
- subsystem targeted tests
- current import tests
- CLI smoke
- deploy/preflight checks
- full pytest
- Docker acceptance
- UEF replay
- Step5 safety regressions

Generate final compatibility inventory with remaining intentional wrappers.

## 26. Required Subsystem Validation

### Strategist
- strategist schema/reasoning/LLM tests
- private seam migration tests

### Reporting
- AI report
- reporter service
- script wrapper tests

### Operator UI
- tests/test_operator_ui.py
- tests/test_operator_ui_data_access_phase2.py

### Scanner
- tests/test_m11_2_scanner.py
- current scanner focused suites
- scanner/monitor compatibility

### Monitor
- intraday signal
- exit guard
- candidate cascade
- current Monitor integration

### Commander/runtime
- test_m21_commander_runtime_entry
- runtime mode gate
- graph spine parity
- reporter hooks
- runtime ownership

### Naming/entrypoints
- M13 tests
- M28 tests
- M31 probe
- runtime entrypoint import boundaries

### Executor
- execute_from_packet
- readiness
- Step5B
- Step5C
- Supervisor
- unknown outcome / quarantine

## 27. Full Acceptance Gates

P1.5.10 passes only if:

Canonical implementation duplication     REDUCED
Active obsolete wrapper imports          ZERO where targeted
Stable public facades                    PRESERVED
Historical regression meaning            SAME
Runtime topology                         SAME
Agent order                              SAME
LLM decision roles                       2 -> 2
State semantics                          SAME
Runtime modes                            SAME
Supervisor authority                     SAME
Execution guard order                    SAME
CAS/idempotency                          SAME
Broker mutation ordering                 SAME
Production-write leakage                 NONE
Trading-authority leakage                NONE
UEF semantics                            SAME
Step5C/Step5D semantics                  SAME

## 28. Explicit Non-Goals

P1.5.10 does NOT:
- force wrapper count to zero
- rename historical docs/tests
- delete historical pipeline implementations without review
- remove graph node facades
- remove Operator UI public facade
- remove Reporting public facade merely for layering purity
- remove runtime modes
- remove state/env compatibility blindly
- remove Step5 safety wrappers
- alter strategy or execution behavior
- change artifact schemas/paths
- change UEF/Q program identifiers
- adopt LangGraph

## 29. Forbidden Changes

Stop/report if cleanup requires:
- behavior change
- topology change
- test weakening
- historical evidence rewrite
- Supervisor bypass
- guard reorder
- CAS/idempotency change
- broker mutation change
- state/schema break
- operator command break
- deploy/service command break
- lock path split
- UEF/Step5 semantic change

## 30. Recommended End State at P1.5 Freeze

Expected remaining wrappers are intentional:

- graph node facades
- Operator UI data_access facade
- Reporting trade_report_ai facade
- selected historical M11/M13/M28 compatibility paths
- selected config aliases needed by deployment
- Step5 safety wrappers
- artifact/schema legacy aliases needed for old data

Expected removed/reduced:

- transitional Commander integrated_chain_support after direct import migration if zero-consumer
- duplicate AgentExecutor implementation
- unused graph-node private helper re-exports
- obsolete P1.5.8 wrapper modules proven zero-consumer

P1.5 freeze may legitimately retain compatibility surfaces.

## 31. Implementation Gate

P1.5.10 implementation starts only from the frozen P1.5 implementation baseline after P1.5.1-P1.5.9 implementation tranches are complete and green.

This design branch remains documentation/design only.

## 32. Design Verdict

Cross-P1.5 compatibility inventory: MAPPED
Deletion philosophy: PROOF-BASED
Stable facade policy: FROZEN
Historical compatibility policy: FROZEN
Safety wrapper policy: FROZEN
Commander integrated_chain_support: MIGRATE_THEN_REMOVE
Operator UI data_access: KEEP_STABLE_FACADE
Reporting trade_report_ai: KEEP_STABLE_FACADE
legacy Strategist/Scanner/Monitor Agent stack: HISTORICAL_COMPATIBILITY
scan_candidates/select_candidate: HISTORICAL_COMPATIBILITY
duplicate AgentExecutor: STRONG CLEANUP CANDIDATE
runtime naming aliases: REVIEW AFTER P1.5.8 MIGRATION
Step5/Executor private safety wrappers: SAFETY_LOCK
state/env/path aliases: CONTRACT_AUDIT REQUIRED
CW1-CW7 sequence: FROZEN
Runtime implementation: NOT STARTED
