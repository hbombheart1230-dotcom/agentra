# P1.5.8 Milestone / Runtime Naming Cleanup Implementation Packet v1.0

Status: DESIGN COMPLETE / IMPLEMENTATION GATED
Date: 2026-10-07
Design branch: design/p1.5-p1.6-modernization
Scope: P1.5.8 milestone/runtime naming cleanup

## 1. Purpose

P1.5.8 removes development-milestone vocabulary from active production runtime surfaces while preserving historical provenance, serialized contracts, safety identifiers, import compatibility, CLI compatibility and runtime behavior.

This phase is a compatibility migration, not a cosmetic repository-wide rename.

The P1.5 constitution is authoritative:

- production code uses domain/responsibility names, not development milestones
- m10_/m11_/m13_/stepX_/phaseX_/fixX_ style runtime names are normally removed
- genuine protocol/program identifiers such as UEF and Q10/Q12/Q100 are preserved
- state-key renames require canonical-read + legacy fallback + migration + proof before alias removal

## 2. Repository Inventory

A repository-tree inventory against the P1.5 source baseline found approximately 468 milestone/phase/step-named file paths.

By top-level area:

- docs: 217
- tests: 140
- scripts: 63
- data: 15
- deploy: 14
- libs: 13
- graphs: 6

This distribution is critical.

Most milestone-named files are historical documents, historical regression tests, recorded evaluation data or milestone tooling.

Therefore P1.5.8 must NOT mechanically rename 468 files.

The naming cleanup target is active runtime vocabulary and active operator/developer entry surfaces.

## 3. Classification

Every naming candidate must be classified before change.

### RENAME_CANONICAL

Active production/runtime surface whose current name is a development milestone.

Action:
- introduce domain/responsibility canonical name
- move implementation to canonical owner where appropriate
- leave legacy compatibility wrapper/alias

### COMPAT_ALIAS

Public import, CLI, state key, env var or path still used by existing consumers.

Action:
- canonical name becomes preferred
- legacy alias remains accepted
- remove only in P1.5.10 after consumer proof

### HISTORICAL_KEEP

Historical plan, audit, incident record, milestone test, fixture or evaluation dataset.

Action:
- retain original name
- do not rewrite history
- index/classify if needed

### CONTRACT_KEEP

Serialized schema version, event kind, artifact field/value, path or other externally visible contract where changing text is a semantic migration.

Action:
- do not rename in P1.5.8
- version/additive migration required if ever changed

### SAFETY_LOCK

Safety-critical Step/Phase identifiers or paths whose renaming could disturb execution/ownership/audit behavior.

Action:
- no implementation rename in P1.5.8 unless a pure compatibility facade is independently proven
- no semantic change

### DOMAIN_KEEP

A name that looks version-like but is a genuine current program/protocol identifier.

Examples:
- UEF-7/8/9
- Q10
- Q12
- Q100

Action:
- preserve

## 4. Historical Documentation Policy

Historical M/Step/Phase documents are evidence, not stale variable names.

Preserve:
- docs/plan/m*.md
- docs/daily_patch historical entries
- incident/freeze reports
- historical milestone summaries
- old project-tree snapshots
- old development closeout notes

Do not rewrite old files to pretend they used current naming.

Current architecture/index documents may point from the new canonical name to the historical milestone artifact.

## 5. Historical Test Policy

Historical regression tests are assets.

Examples:
- tests/test_m13_*.py
- tests/test_m28_*.py
- tests/test_m31_*.py
- tests/test_step5*.py

P1.5.8 does NOT bulk-rename historical test files.

Instead:
- canonical runtime tests are added/migrated gradually
- old tests continue exercising compatibility imports
- milestone test names remain provenance when they describe the original regression/freeze
- duplicate canonical tests are introduced only when they validate the new public surface

## 6. Active M13 Runtime — Highest-Priority Rename

The most important active milestone naming is the M13 live-loop runtime.

Current active surfaces include:

- graphs/pipelines/m13_live_loop.py
- graphs/pipelines/m13_tick.py
- graphs/pipelines/m13_eod_report.py
- libs/runtime/entrypoints/m13_live_loop.py
- scripts/run_m13_live_loop.py
- state["m13_tick_pipeline"]
- env M13_LIVE_LOCK_PATH
- env M13_LIVE_LOCK_STALE_SEC
- legacy tick value "legacy_m10"

These are production/runtime names and should be canonicalized.

## 7. Frozen Canonical M13 Mapping

### Module / function mapping

| Legacy | Canonical |
|---|---|
| graphs/pipelines/m13_live_loop.py | graphs/pipelines/live_cycle.py |
| run_m13_once | run_live_cycle_once |
| graphs/pipelines/m13_tick.py | graphs/pipelines/runtime_tick.py |
| run_m13_tick | run_runtime_tick |
| graphs/pipelines/m13_eod_report.py | graphs/pipelines/eod_report.py |
| run_m13_eod_report | run_eod_report |
| libs/runtime/entrypoints/m13_live_loop.py | libs/runtime/entrypoints/live_loop.py |
| scripts/run_m13_live_loop.py | scripts/run_live_loop.py |

Legacy modules remain thin wrappers/re-exports during P1.5.

### State key mapping

Legacy:
- m13_tick_pipeline

Canonical:
- runtime_tick_pipeline

Migration rule:
1. read runtime_tick_pipeline
2. fallback-read m13_tick_pipeline
3. normalize
4. write runtime_tick_pipeline
5. mirror legacy key while old consumers remain
6. migrate all active consumers
7. legacy mirror removal only in P1.5.10 after proof

### Tick path value mapping

Current legacy value:
- legacy_m10

Canonical internal value:
- legacy_decision_pipeline

Compatibility input aliases remain accepted:
- legacy_m10
- legacy
- m10

Integrated-chain value remains:
- integrated_chain

During migration:
- canonical state may expose runtime_tick_pipeline=legacy_decision_pipeline
- legacy compatibility surface may continue exposing legacy_m10 where required by old tests/consumers

Do not silently change a serialized field consumed elsewhere without compatibility coverage.

### Environment mapping

Legacy:
- M13_LIVE_LOCK_PATH
- M13_LIVE_LOCK_STALE_SEC

Canonical:
- LIVE_LOOP_LOCK_PATH
- LIVE_LOOP_LOCK_STALE_SEC

Read precedence:
1. canonical env
2. legacy env
3. existing default

Legacy env remains supported through P1.5.10.

### Default path

Current default:
- data/state/m13_live_loop.lock

P1.5.8 does not move the default lock file path unless dual-path compatibility and single-instance safety are proven.

Changing a lock path can create two independent locks and is therefore a runtime-ownership risk.

The filename may remain legacy during P1.5.8 even after the environment variable becomes canonical.

## 8. Legacy M10 Runtime Dependency

graphs/pipelines/m13_tick.py still lazily imports:

- graphs/pipelines/m10_live_pipeline.py
- run_m10_live_pipeline

This is an active compatibility dependency when the legacy tick path is selected.

Canonical target:

- graphs/pipelines/legacy_decision_pipeline.py
- run_legacy_decision_pipeline

Migration:
1. move/copy behavior to the canonical module with byte-for-byte/behavior-equivalent sequencing
2. m10_live_pipeline.py becomes a wrapper to canonical implementation
3. runtime_tick.py imports the canonical module
4. old run_m10_live_pipeline import remains available

Do not alter pipeline order.

Current legacy M10 order remains exactly:
- load_state
- build_snapshots
- build_risk_context
- build_decision_context
- decide_trade
- execute_from_packet
- update_state_after_execution
- save_state

M11/M11.2 pipeline files are historical/legacy surfaces unless consumer proof demonstrates active use.

They are not blindly renamed in P1.5.8.

## 9. M28 Runtime / Deployment Tooling

Active operator/developer tooling under libs/runtime/entrypoints still uses M28 names.

Canonical module mapping:

| Legacy module | Canonical module |
|---|---|
| m28_runtime_profile_scaffold_check.py | runtime_profile_check.py |
| m28_runtime_lifecycle_hooks_check.py | runtime_lifecycle_check.py |
| m28_rollout_rollback_check.py | rollout_rollback_check.py |
| m28_startup_preflight_check.py | startup_preflight_check.py |
| m28_scheduler_worker_launch_wrapper_check.py | scheduler_worker_launch_check.py |
| m28_launch_hook_integration_check.py | launch_hook_integration_check.py |
| m28_deploy_launch_template_check.py | deploy_launch_template_check.py |
| m28_launch_templates.py | launch_templates.py |
| m28_registration_helper_check.py | registration_helper_check.py |
| m28_registration_helpers.py | registration_helpers.py |
| m28_closeout_check.py | deployment_readiness_check.py |

Implementation rule:
- canonical module owns implementation
- old m28 module imports/re-exports canonical main/helpers
- old scripts remain CLI wrappers
- new canonical scripts may be added
- return codes and JSON payloads remain identical

Do not rename JSON output keys such as m28_1_profile inside the existing legacy closeout artifact in P1.5.8. They are serialized compatibility fields.

## 10. M28 Deploy Paths — Compatibility Locked

Current paths include:
- deploy/m28_launch_templates
- deploy/m28_registration_helpers
- data/state/m28_*
- reports/milestones/m28_*

These may be used by:
- Windows scheduled-task XML
- Linux service files
- registration helpers
- rollout scripts
- tests
- operational runbooks

P1.5.8 module naming cleanup does not automatically relocate these paths.

Path migration requires:
- canonical path introduction
- legacy fallback or generated compatibility copies
- scheduler/service consumer audit
- rollback proof

Default artifact/deploy path renames are deferred until such proof exists, normally P1.5.10 or a dedicated ops migration.

## 11. M28 Environment Aliases

Known active legacy env names:

- M28_LIFECYCLE_STATE_PATH
- M28_LIFECYCLE_LOCK_STALE_SEC

Canonical aliases:

- RUNTIME_LIFECYCLE_STATE_PATH
- RUNTIME_LIFECYCLE_LOCK_STALE_SEC

Read precedence:
canonical -> legacy -> existing default.

Do not remove legacy env support in P1.5.8.

## 12. M31 Agent-Chain Probe

Current:
- libs/runtime/entrypoints/m31_agent_chain_probe.py
- scripts/run_m31_agent_chain_probe.py

Canonical:
- libs/runtime/entrypoints/agent_chain_probe.py
- scripts/run_agent_chain_probe.py

Legacy modules/scripts remain wrappers.

The probe's behavior, stub Supervisor/Executor behavior and output contract remain unchanged.

## 13. M31 Mock-Exam Session Gate Environment

libs/runtime/live_loop_config.py currently consumes:
- M31_MOCK_EXAM_SESSION_HARD_GATE

Canonical:
- MOCK_EXAM_SESSION_HARD_GATE

Read precedence:
canonical -> legacy -> current default.

No hard-gate default change.

## 14. M25 Notification / Ops Environment Names

Current runtime-profile and operational tooling still expose M25-prefixed configuration.

Known active examples include:

Ops batch:
- M25_BATCH_EVENT_LOG_PATH
- M25_BATCH_REPORT_DIR
- M25_BATCH_LOCK_PATH
- M25_BATCH_LOCK_STALE_SEC
- M25_BATCH_STATUS_JSON_PATH

Notification:
- M25_NOTIFY_EVENT_LOG_PATH
- M25_NOTIFY_PROVIDER
- M25_NOTIFY_ON
- M25_NOTIFY_WEBHOOK_URL
- M25_NOTIFY_PORTFOLIO_GUARD_ESCALATION_MIN
- M25_NOTIFY_PORTFOLIO_GUARD_PROVIDER
- M25_NOTIFY_PORTFOLIO_GUARD_WEBHOOK_URL
- M25_NOTIFY_TIMEOUT_SEC
- M25_NOTIFY_STATE_PATH
- M25_NOTIFY_DEDUP_WINDOW_SEC
- M25_NOTIFY_RATE_LIMIT_WINDOW_SEC
- M25_NOTIFY_MAX_PER_WINDOW
- M25_NOTIFY_RETRY_MAX
- M25_NOTIFY_RETRY_BACKOFF_SEC
- M25_NOTIFY_DRY_RUN
- M25_NOTIFY_FAIL_ON_ERROR

Canonical prefix policy:

- M25_BATCH_* -> OPS_BATCH_*
- M25_NOTIFY_* -> NOTIFY_*

Examples:
- M25_NOTIFY_PROVIDER -> NOTIFY_PROVIDER
- M25_BATCH_LOCK_PATH -> OPS_BATCH_LOCK_PATH

Migration:
- canonical env read first
- legacy env fallback
- current runtime-profile/legacy report fields may continue rendering legacy keys until schema migration
- no notification behavior, provider routing or thresholds change

## 15. Serialized Event Kinds — Do Not Rename

libs/reporting/alert_notifier.py currently emits values such as:
- kind = "m25_ops_batch"

This is serialized event data.

P1.5.8 does not rename this value in place.

Changing it can break:
- queries
- metrics
- dashboards
- report filters
- archived log comparisons

If a canonical event kind is required later:
- add a new field or schema version
- keep old field semantics
- migrate consumers explicitly

Classification:
CONTRACT_KEEP.

## 16. Schema Version Strings — Do Not Rename

Examples such as:
- phase5_validation_bundle.v1

are serialized schema identifiers.

They are not code-symbol naming targets.

Do not change a v1 schema string merely because the identifier contains a historical phase label.

Any replacement requires parallel schema/version migration.

Classification:
CONTRACT_KEEP.

## 17. Step5C / Step5D — Safety Lock

Although stepX naming is normally removed from production vocabulary, current Step5C/Step5D identifiers are tightly bound to execution-ownership, mutation-safety, reconciliation and historical regression evidence.

Known surfaces include:
- scripts/step5d_crash_reconciliation.py
- Step5C execution-owner tests
- Step5B/Step5C safety regression suites
- associated audit documentation

P1.5.8 does NOT rename or relocate these safety-critical implementation/test surfaces.

Reasons:
- execution ownership and mutation ordering are frozen
- audit references use these identifiers
- a rename provides low architectural value relative to safety/provenance risk

A future compatibility facade may expose a responsibility name such as crash_reconciliation without altering the Step5D authority, but that is not required for P1.5.8.

Classification:
SAFETY_LOCK + HISTORICAL_KEEP.

## 18. UEF / Q Programs — Domain Keep

Do not rename:
- UEF-7
- UEF-8
- UEF-9
- Q10
- Q12
- Q100

These are program/protocol identifiers, not accidental milestone names.

Classification:
DOMAIN_KEEP.

## 19. Commander Runtime Names

Current Commander public surfaces already use responsibility/domain names:
- graphs/commander_runtime.py
- run_commander_runtime
- graph_spine
- integrated_chain
- decision_packet
- preopen/session/closeout

These remain.

Do not rename current runtime mode or phase values simply because P1.5.8 is a naming phase.

The word "phase" in RuntimePhase is domain lifecycle vocabulary, not a development Phase-X label.

## 20. Default Run IDs

Example:
- commander_runtime_once.py default run-id "m21-runtime-once"

run_id is observability identity and may affect artifact paths.

P1.5.8 classification:
COMPAT_ALIAS / OBSERVABILITY CONTRACT.

Recommended canonical default:
- commander-runtime-once

But change only after:
- artifact-path tests
- operator-query consumer audit
- explicit-run-id tests

Explicit user-supplied run IDs are never rewritten.

If risk is non-trivial, retain the legacy default through P1.5.8 and change only in P1.5.10.

## 21. Artifact / Report Paths

Examples:
- reports/milestones/m28_*
- data/logs/milestones/m25/*
- data/state/m25_*
- data/state/m28_*

These paths are observable and often operationally referenced.

P1.5.8 does not mass-move them.

A path can remain historically named while the active Python module/CLI becomes canonical.

Path migration is a separate compatibility operation.

## 22. Deployment Files

deploy/m28_launch_templates and deploy/m28_registration_helpers contain actual scheduler/service artifacts.

Do not rename directories without:
- generated-template parity
- scheduler registration audit
- Windows task path audit
- Linux service path audit
- rollback test
- deployment documentation update

Current file contents may be regenerated from canonical entrypoints while preserving old destination paths.

## 23. Public Import Compatibility Pattern

Canonical implementation example:

graphs/pipelines/runtime_tick.py
- owns run_runtime_tick

Legacy wrapper:

graphs/pipelines/m13_tick.py
- imports run_runtime_tick
- exposes run_m13_tick compatibility wrapper
- translates legacy parameter names such as run_m10 if needed
- contains no independent business logic

The legacy wrapper should be intentionally small and marked for P1.5.10 consumer review.

Do not maintain two copies of logic.

## 24. CLI Compatibility Pattern

Add a canonical CLI:
- scripts/run_live_loop.py

Keep:
- scripts/run_m13_live_loop.py

Legacy script becomes a thin import/dispatch wrapper.

Both must:
- return the same exit code
- accept the same current options
- produce the same runtime behavior

Canonical help text should no longer describe the feature primarily as M13.

Legacy help compatibility can mention that the old command is retained as an alias.

## 25. Environment Compatibility Pattern

Use a single helper where practical:

resolve_env_alias(canonical, legacy, default)

Rules:
1. canonical wins when explicitly set
2. fallback to legacy
3. otherwise existing default
4. optional observability records which source won
5. do not log secret values
6. do not modify control flow except through the same resolved value

Never print secrets while migrating env keys.

## 26. State-Key Compatibility Pattern

For state keys such as runtime_tick_pipeline:

1. read canonical
2. fallback legacy
3. normalize to canonical internal representation
4. write canonical
5. temporarily mirror legacy output where required
6. update all active consumers
7. add conflict test
8. remove legacy write/read only in P1.5.10 after proof

If both keys are provided:
- canonical key is authoritative per the constitution naming policy
- emit observational compatibility evidence if useful
- do not silently merge incompatible values

## 27. Function Keyword Compatibility

Function parameter names can also be public test/injection surfaces.

Example:
- legacy run_m10 injection
- canonical run_legacy_pipeline injection

Do not break old keyword callers.

Canonical function may use domain naming.
Legacy wrapper translates old keyword name to the canonical call.

## 28. Test Strategy

P1.5.8 needs both canonical and compatibility tests.

### Canonical surface tests

Verify:
- new module imports
- new function names
- new CLI names
- canonical state/env keys
- canonical value normalization

### Compatibility tests

Verify:
- legacy imports still work
- legacy CLI wrappers still work
- legacy env keys still work
- legacy state keys still work
- old parameter names still work
- output/return codes unchanged

### Conflict tests

When canonical and legacy config keys coexist:
- canonical is selected
- compatibility source is traceable
- no duplicate execution path is created

### Historical tests

Keep milestone-named regression tests as-is when they encode historical provenance.

## 29. Known Focused Regression Assets

The directly inspected naming-sensitive suites include at least 66 tests across:

- tests/test_m13_e2e_once.py
- tests/test_m13_eod_report.py
- tests/test_m13_live_loop.py
- tests/test_m13_tick.py
- tests/test_m28_1_runtime_profile_scaffold.py
- tests/test_m28_2_runtime_lifecycle_hooks.py
- tests/test_m28_3_rollout_rollback_check.py
- tests/test_m28_4_startup_preflight_check.py
- tests/test_m28_5_scheduler_worker_launch_wrapper_check.py
- tests/test_m28_6_launch_hook_integration_check.py
- tests/test_m28_7_deploy_launch_templates.py
- tests/test_m28_8_registration_helpers.py
- tests/test_m28_9_closeout_check.py
- tests/test_m31_agent_chain_probe.py
- tests/test_run_phase5_validation_bundle.py
- tests/test_p0b_step5d_crash_reconciliation.py
- tests/test_step5c_execution_owner.py

Additional live-loop ownership/restart tests also protect M13-path behavior.

## 30. Implementation Batches

Do not rename everything in one commit.

### N1 — Characterization + naming manifest

Create a machine-readable/Markdown naming manifest with:
- legacy identifier
- canonical identifier
- classification
- consumer count/known consumers
- compatibility strategy
- removal gate

No runtime behavior change.

### N2 — Live runtime canonicalization

Canonicalize M13 live runtime:
- live_cycle
- runtime_tick
- eod_report
- live_loop entrypoint/script
- legacy decision pipeline bridge

Keep old M13/M10 wrappers.

Required parity:
- tick open/closed behavior
- transient-state clearing
- integrated_chain default
- legacy pipeline path
- EOD once-per-day behavior
- report generation
- save-state ordering
- live-loop lock behavior

### N3 — Deployment/runtime tooling canonicalization

Add canonical M28/M31 entrypoint/module names.

Old milestone modules/scripts become wrappers.

Do not move deploy/data/report paths yet.

### N4 — Config/state alias migration

Introduce:
- runtime_tick_pipeline
- LIVE_LOOP_LOCK_*
- RUNTIME_LIFECYCLE_*
- MOCK_EXAM_SESSION_HARD_GATE
- OPS_BATCH_*
- NOTIFY_*

Keep legacy fallbacks.

Add conflict/source tests.

### N5 — Active import/consumer migration

Migrate active production code to canonical imports.

Order:
1. libs/runtime
2. graphs/current runtime
3. scripts/current operator commands
4. deploy template generators
5. current tests

Historical docs/tests remain.

### N6 — Current documentation cleanup

Update canonical/current docs and CLI help text to domain names.

Do not rewrite historical M/Phase/Step documents.

Indexes may state:
- canonical current name
- legacy alias
- historical origin

### N7 — Naming regression / compatibility freeze

Run focused and full regression.

Produce compatibility inventory for P1.5.10:
- wrappers still consumed
- legacy env keys still observed
- legacy state keys still observed
- legacy CLI references
- artifact/deploy paths not yet migrated

P1.5.8 does NOT delete wrappers.

## 31. Removal Gates for P1.5.10

A legacy alias may be removed only if:

- no production import remains
- no deploy/service file references it
- no active script references it
- no canonical current test requires it except explicit compatibility tests
- no state/config source emits it
- no operator runbook uses it
- full regression passes without alias
- Docker acceptance passes
- UEF replay remains unchanged
- execution safety regression remains green

Historical files do not count as active consumers.

## 32. Behavior Locks

All remain SAME:

- runtime topology
- Commander agent order
- graph_spine/integrated_chain/decision_packet semantics
- preopen/session/closeout semantics
- live-loop market-hours behavior
- tick skip behavior
- EOD report timing
- integrated_chain default
- legacy decision pipeline behavior
- lock semantics
- runtime ownership/CAS
- shutdown/drain behavior
- Strategist/Scanner/Monitor behavior
- Supervisor authority
- Executor authority
- execution guard order
- broker mutation ordering
- serialized event semantics
- artifact schemas
- existing default artifact paths
- UEF
- Q10/Q12/Q100 identifiers
- Step5C/Step5D safety semantics

## 33. Explicit Non-Goals

P1.5.8 does NOT:
- delete historical milestone docs
- rename historical regression tests en masse
- change schema versions
- change event kind values
- move historical reports
- move production lock path without safety proof
- rename UEF/Q programs
- refactor Step5C/Step5D execution safety
- change route topology
- adopt LangGraph
- alter strategy
- alter execution behavior
- remove compatibility wrappers

## 34. Forbidden Changes

Stop/report rather than improvise if naming cleanup appears to require:

- broker/execution semantic change
- lock/ownership path split that can permit a second runtime
- state contract break without alias
- env removal without fallback
- serialized schema/event value mutation
- historical audit rewrite
- Supervisor bypass
- mutation guard reorder
- Step5 safety change
- UEF semantic change
- Q-program rename

## 35. Required Validation

Focused:
- tests/test_m13_e2e_once.py
- tests/test_m13_eod_report.py
- tests/test_m13_live_loop.py
- tests/test_m13_tick.py
- all M13 lease/ownership/restart/shutdown regressions
- tests/test_m28_1_runtime_profile_scaffold.py
- tests/test_m28_2_runtime_lifecycle_hooks.py
- tests/test_m28_3_rollout_rollback_check.py
- tests/test_m28_4_startup_preflight_check.py
- tests/test_m28_5_scheduler_worker_launch_wrapper_check.py
- tests/test_m28_6_launch_hook_integration_check.py
- tests/test_m28_7_deploy_launch_templates.py
- tests/test_m28_8_registration_helpers.py
- tests/test_m28_9_closeout_check.py
- tests/test_m31_agent_chain_probe.py
- runtime entrypoint/import-boundary tests
- runtime profile/lifecycle tests

Safety:
- tests/test_p0d_runtime_ownership.py
- Step5B/Step5C execution safety regressions
- Step5D reconciliation tests
- execution guard regressions

Then:
- affected Commander/runtime suites
- full pytest
- Docker acceptance at integration gate
- UEF replay

Acceptance:
- canonical imports PASS
- legacy imports PASS
- canonical CLI PASS
- legacy CLI PASS
- env fallback PASS
- state-key fallback PASS
- no duplicate runtime lock PASS
- artifact/schema drift NONE
- new LLM decision roles 0
- production-write leakage NONE
- trading-authority leakage NONE
- UEF SAME
- Step5C/D SAME

## 36. Documentation / Patch Notes

Each implementation tranche must:
- update current architecture/navigation docs
- preserve historical milestone evidence
- update docs/daily_patch/
- update UI/API canonical patch notes
- record compatibility aliases introduced
- record aliases proven unused
- never claim an old historical artifact used the new name

## 37. Implementation Gate

P1.5.8 runtime implementation starts only from the frozen P1.5 implementation baseline required by the master plan.

This design branch remains documentation/design only.

## 38. Design Verdict

Repo-wide milestone-named path inventory: COMPLETE
468 milestone/phase/step paths classified by area: YES
historical-vs-runtime policy frozen: YES
M13 active runtime mapping frozen: YES
legacy M10 bridge strategy frozen: YES
M28 runtime/deploy tooling mapping frozen: YES
M31 probe mapping frozen: YES
M13/M28/M31 env aliases defined: YES
M25 notify/ops canonical prefix policy defined: YES
serialized event/schema no-rename rule frozen: YES
Step5C/Step5D safety exception frozen: YES
UEF/Q domain-identifier preservation frozen: YES
state-key compatibility pattern frozen: YES
wrapper-removal gate deferred to P1.5.10: YES
N1-N7 implementation sequence frozen: YES
Runtime implementation: NOT STARTED
