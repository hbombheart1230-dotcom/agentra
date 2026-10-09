# P1.5.11 Full Regression / Docker / UEF Replay / Freeze Implementation Packet v1.0

Status: DESIGN COMPLETE / IMPLEMENTATION GATED
Date: 2026-10-07
Design branch: design/p1.5-p1.6-modernization
Scope: P1.5.11 final integration acceptance and P1.5 structural freeze

## 1. Purpose

P1.5.11 is the final acceptance gate for the complete P1.5 structural refactor.

It does not add new architecture.

It proves that P1.5.1-P1.5.10 changed structure without changing trading behavior, authority boundaries, runtime topology, frozen UEF semantics, execution safety, or operational deployment behavior.

P1.6 may not start until P1.5.11 is formally frozen.

## 2. P1.5 Freeze Meaning

A P1.5 freeze means all of the following are proven:

- structural refactor implementation is complete
- full regression is green against the accepted baseline
- runtime behavior is preserved
- Agent boundaries are explicit and callable
- runtime agent order is unchanged
- LLM decision roles remain exactly Strategist + Reporter
- Scanner/Monitor authority is unchanged
- Commander remains deterministic orchestration
- Supervisor authority is unchanged
- Executor mutation ownership/order is unchanged
- UEF frozen semantics remain unchanged
- UEF-7/8/9 replay remains deterministic and authoritative
- Docker runtime ownership/restart/shutdown behavior remains safe
- no production-write leakage appears in offline/test/replay flows
- no trading-authority leakage appears
- compatibility cleanup is bounded and documented
- test artifacts obey hygiene policy
- independent audit passes
- freeze evidence is immutable and traceable to one candidate SHA

A green unit-test subset is not a freeze.

## 3. Existing Accepted Safety Baselines

P1.5.11 must preserve prior accepted operational/safety evidence.

### P1.3 Docker technical acceptance

P1.3 closed after the read/write-gate fix at:
- NEW_P1_3_ACCEPTANCE_SHA = 11c7e3c097cc97169643a6249c5e7221cd61b139

Later runtime restart/ownership hardening added:
- strict lock process identity
- bounded SQLite ownership wait
- background ownership heartbeat
- host/docker runtime-mode launch gate
- ownership-based Docker healthcheck
- clean shutdown during ownership wait
- recovery matrix behavior

These later safety changes are part of the effective modern runtime baseline and must not regress.

### P1.2 Daily UEF

Daily UEF automation and same-day idempotency/determinism were integrated.

Canonical daily publication requires:
- freshness contracts pass
- one canonical capture
- UEF-7 -> UEF-8 -> UEF-9
- UEF-9 authority_status = VALID
- verified COMPLETE manifest
- current/latest pointers only after verification
- deterministic same-day rerun behavior
- no canonical writes in diagnostic mode

### UEF frozen core

The authoritative freeze manifest remains:
- docs/research/uef_freeze_manifest.md

P1.5.11 must run:
- python scripts/verify_uef_freeze_manifest.py

Expected:
- every manifest row MATCH
- MISMATCH = 0

P1.5 refactor is not authority to regenerate that manifest.

## 4. October 6 Daily UEF Freshness Incident

The 2026-10-06 scheduled Daily UEF run failed closed due to stale/unknown registered upstream source freshness.

This was documented as:
- an operational freshness incident
- not a UEF framework/freeze failure
- no canonical generation
- no backfill or authority mutation

P1.5.11 must not "repair" freeze evidence by:
- backfilling missing source evidence
- weakening freshness contracts
- using diagnostic output as canonical
- republishing a stale day
- changing UEF semantics

Freeze acceptance instead requires one of:

A. a fresh post-refactor canonical trading day that naturally passes the source freshness contracts and reaches UEF-9 VALID, or

B. if no such market day is available during the implementation window, a deterministic replay against an already-authoritative frozen input plus an explicit status:
   LIVE_CROSS_DAY_FRESHNESS = PENDING_OPERATIONAL_OBSERVATION

Option B may prove structural parity but does not fabricate a live daily publication.

If P1.5 freeze policy requires live cross-day proof, the freeze remains blocked until A occurs.

## 5. Source Baseline and Candidate Identity

Before implementation starts, record:

- P1_5_IMPLEMENTATION_BASELINE_SHA
- P1_5_IMPLEMENTATION_BRANCH
- P1_5_FREEZE_CANDIDATE_SHA

The design-branch SHA is never the implementation baseline.

The candidate SHA must be immutable for the complete P1.5.11 acceptance run.

Any source-code fix after acceptance begins invalidates candidate acceptance and requires:
- new candidate SHA
- rerun of affected targeted gates
- rerun of all final mandatory gates

Documentation-only evidence additions after the candidate may be separately permitted only if they do not alter code/config/test semantics and are clearly recorded.

## 6. Baseline Metadata Snapshot

Create a final acceptance metadata record containing:

- baseline SHA
- candidate SHA
- Python version
- pytest version
- OS
- Docker version / compose version
- Docker image ID/digest
- active runtime mode
- dependency lock/hash where available
- total test-file count
- collection count
- relevant environment safety flags with secret values redacted
- UEF freeze-manifest digest
- compatibility inventory digest
- patch-note entry count
- timestamp / timezone
- operator/auditor identity fields

No secret value may be written into acceptance evidence.

## 7. Repository Diff Audit

Before tests, inspect the complete baseline -> candidate diff.

Required classifications for every changed file:
- PURE
- ORCHESTRATION
- IO
- AUTHORITY
- EVIDENCE
- TEST
- DOC
- COMPATIBILITY

Explicitly flag changes touching:
- UEF frozen manifest files
- runtime ownership
- live loop
- execute_from_packet
- intent execution owner
- readiness evidence
- Supervisor
- RealExecutor
- broker mutation classifier
- Docker compose
- runtime state schema
- canonical artifact schema

Any unexpected AUTHORITY or frozen-core change blocks freeze.

## 8. Test Inventory Baseline

The source baseline currently contains approximately:
- 508 Python test files
- 27 UEF-named test files
- 2 Docker/compose-named test files
- 13 Step5-named test files
- 28 execution/Supervisor/broker-focused test files
- 12 Commander/runtime-focused files
- 21 Scanner-focused files
- 20 Monitor-focused files
- 9 Strategist-focused files
- 16 Reporter/trade-report-focused files
- 9 Operator UI/summary/visibility-focused files

These are inventory counts, not expected pytest case counts.

Final acceptance records exact pytest collection/pass/fail/skip counts from the freeze candidate.

Do not hard-code a stale expected test-case count in the design.

## 9. Test Artifact Hygiene Gate

P1.5.11 must explicitly validate artifact hygiene.

Existing permanent regression:
- tests/test_pytest_artifact_hygiene.py

Required:
- pytest basetemp outside repository
- successful sessions remove their own scratch
- repeated pytest sessions create no repo-local .pytest-work* / pytest-work* / .pytest-today-prep* accumulation
- success artifacts auto-clean where intended
- failed evidence retained only under bounded policy
- no broad deletion of production evidence

Before and after full regression:
- snapshot repo-local temporary artifact paths
- compare
- fail if new unbounded pytest scratch remains

Production/runtime files generated by an intentionally running live runtime must not be misclassified as pytest scratch.

## 10. Final Validation Layers

P1.5.11 is executed in layers.

Do not jump directly to Docker before unit/integration parity is green.

### Layer A — Static and contract audit
### Layer B — subsystem targeted regression
### Layer C — full pytest
### Layer D — deterministic replay / UEF
### Layer E — Docker operational acceptance
### Layer F — authority/leakage/security audit
### Layer G — independent audit and freeze

Each later layer assumes earlier layers passed.

## 11. Layer A — Static / Architecture Acceptance

Verify:

- no new LLM decision owner
- Strategist + Reporter remain the only LLM roles
- Scanner does not call LLM
- Monitor does not call LLM
- Commander does not call LLM
- Supervisor does not call LLM
- Executor does not call LLM

- Monitor has no direct broker execution path
- Commander has no direct broker mutation path
- Scanner chart/compatibility remains soft-rank-only
- Supervisor remains approval authority
- execute_owned_order remains the canonical claim-dispatch-finish mutation choke point

- Agent order unchanged
- runtime modes unchanged
- preopen/session/closeout phase semantics unchanged
- no LangGraph/pydantic-graph adoption in P1.5

- compatibility inventory is complete
- no duplicate canonical implementation remains where P1.5.10 targeted cleanup

## 12. Layer B — Subsystem Targeted Regression

Run the targeted suites required by each P1.5 packet.

Minimum groups:

### Reporting / Operator UI
- trade report AI/reporting focused tests
- reporter service/hooks
- operator UI
- operator Brief
- operator summary/visibility

### Strategist
- output schema
- LLM integration
- reasoning quality
- refresh/cache
- strategy frame
- quant context
- explanation contract

### Scanner
- strategy frame
- Monitor compatibility
- rank plumbing
- policy overlay
- practical selection
- feature hydration
- memory bias
- quote hydration
- fallback
- live-symbol filter

### Monitor
- intraday monitor signals
- exit guards
- exit policy
- candidate cascade
- memory bias
- position sizing
- price freshness
- intent-only authority

### Commander / Runtime
- Commander runtime entry
- graph-spine parity
- runtime mode gate
- runtime ownership
- resilience/cooldown
- runtime lifecycle
- reporter hooks
- portfolio preflight

### Naming / Compatibility
- canonical and legacy imports
- canonical and legacy CLI wrappers
- env alias precedence
- state-key alias precedence
- compatibility inventory tests

### Executor / Safety
- execute_from_packet
- execution trace completeness
- open-order reconciliation
- execution readiness
- paper execution finalization
- guard precedence
- Step5B
- Step5C
- Supervisor
- unknown quarantine
- broker outcome

No targeted suite may be dropped because it is inconvenient after refactor.

## 13. Layer C — Full Pytest

Mandatory command:

python -m pytest -q

Acceptance:
- 0 implementation-caused failures
- no newly skipped safety/authority tests
- exact PASS/FAIL/SKIP/XFAIL counts recorded

If the baseline itself has known failures:
- reproduce them on the exact implementation baseline
- create an explicit baseline-failure ledger
- candidate may only freeze if there are zero NEW failures and none of the baseline failures mask P1.5-touched behavior

Preferred P1.5 freeze standard:
- full suite GREEN

A permanently failing baseline should be repaired before formal freeze whenever feasible.

## 14. Baseline Failure Ledger

If any full-suite failures pre-exist, record for each:

- test node id
- baseline result
- candidate result
- owner/subsystem
- relation to P1.5 touched files
- reason it is safe or unsafe to carry
- remediation plan

Any pre-existing failure in:
- execution safety
- UEF
- runtime ownership
- Agent authority
- Docker health/readiness
- state compatibility

is a freeze blocker.

## 15. Layer D1 — UEF Frozen-Core Integrity

Run:

python scripts/verify_uef_freeze_manifest.py

Required:
- all listed hashes match
- no manifest regeneration
- no silent re-freeze
- MISMATCH = 0

Also run focused frozen-core tests:
- UEF-1
- UEF-2A
- UEF-2B
- UEF-3A
- UEF-3B
- UEF-3C

P1.5 freeze is blocked by any semantic drift.

## 16. Layer D2 — UEF-7 Candidate Conservation

Required replay assertions:

- candidate count conserved from canonical Alpha Board into UEF-7
- candidate IDs unique
- no candidate silently dropped
- no candidate silently invented
- evidence completeness status preserved
- source references remain attributable
- canonical run identity deterministic

Known current representative authority fixture:
- candidate_count = 14

Do not require 14 for every future live day unless that day's canonical board actually contains 14.

The invariant is conservation, not a magic count.

## 17. Layer D3 — UEF-8 Pair Conservation

For N UEF-7 candidates:

expected_pair_count = N * (N - 1) / 2

Required:
- pair_count exactly expected
- all comparison_pair_id values unique
- no duplicate/reversed pair identity
- status counts sum to pair_count
- no unknown status
- unexpected COMPARABLE requires explicit investigation

Known representative frozen replay:
- N = 14
- pairs = 91
- COMPARABLE = 0
- CONDITIONAL = 7
- NOT_COMPARABLE = 84

These numbers are useful regression evidence for the known frozen fixture, not universal live-day constants.

## 18. Layer D4 — UEF-9 Binding / Authority

Required:
- UEF-9 source UEF-7 run ID matches
- UEF-9 source UEF-8 run ID matches
- semantic digests bind correctly
- candidate counts match
- pair counts match
- summary counts match
- authority_status = VALID

Any structural contradiction must fail closed.

## 19. Layer D5 — Replay Determinism

Run the same frozen/replay input at least twice in isolated output roots.

Compare:
- semantic payloads
- deterministic run IDs
- candidate order
- pair IDs
- status counts
- authority result
- canonical hashes excluding explicitly nondeterministic operational metadata

Expected:
- semantic equality
- identical deterministic IDs

No wall-clock-dependent ranking/order drift.

## 20. Layer D6 — Daily UEF Publication Safety

In an isolated repository/output root or approved safe test environment:

Verify:
- diagnostic mode writes no canonical Board/UEF authority
- failed freshness guard advances no pointer
- partial generation without COMPLETE is non-authoritative
- manifest tamper is detected
- same-day unchanged rerun is ALREADY_COMPLETE and non-mutating
- conflicting same-day source fails closed
- latest/current pointers only reference verified COMPLETE
- sole canonical writer invariant holds

Do not run a mutating canonical Daily UEF acceptance against live production state unless operationally approved.

## 21. Layer D7 — Cross-Day Operational Observation

P1.2 remains an operational requirement after code regression.

On a fresh trading day after P1.5 candidate deployment:

Check:
- scheduler/entrypoint actually started
- process START and END lifecycle evidence
- source freshness contracts
- one verified canonical COMPLETE generation
- current/latest consistency
- UEF-7 conservation
- UEF-8 pair conservation
- unique pair IDs
- status counts
- unexpected COMPARABLE
- UEF-9 binding / VALID authority
- same-day rerun idempotency
- production-write leakage
- trading-authority leakage

If upstream sources are stale:
- classify as source freshness incident
- do not weaken UEF
- do not fabricate canonical success
- P1.5 live operational freeze proof remains pending if policy requires a live day

## 22. Production-Write Leakage Audit

Offline/unit/replay/refactor tests must not write to canonical production roots unexpectedly.

Audit:
- data/state
- data/logs
- reports canonical paths
- runtime ownership DB
- intent-state DB
- readiness evidence
- canonical Daily UEF pointers
- broker/order stores

For replay/tests:
- use isolated tmp roots
- snapshot production-root hashes/mtimes before/after where meaningful

Expected:
PRODUCTION_WRITE_LEAKAGE = NONE

Exception:
explicitly authorized operational acceptance runs must declare exactly which canonical files may change.

## 23. Trading-Authority Leakage Audit

Verify no refactor creates a new route to broker mutation.

Required static/runtime assertions:
- Scanner cannot dispatch
- Monitor cannot dispatch
- Reporter cannot dispatch
- UI/API cannot dispatch
- Commander only delegates approved execution path
- Supervisor remains mandatory
- execute_owned_order remains claim owner
- RealExecutor mutation path remains guarded
- test/replay paths cannot reach a real broker mutation

Expected:
TRADING_AUTHORITY_LEAKAGE = NONE

## 24. Step5 Safety Acceptance

Mandatory:
- Step5B broker submission safety
- Step5C execution ownership / physical-order ownership / authoritative intent
- Step5C mutation fail-closed
- Step5D reconciliation/crash-recovery regressions
- readiness evidence R6/R6.1/R6.2
- UNKNOWN outcome quarantine
- execution guard precedence

Freeze requires:
- no duplicate dispatch
- no implicit replay
- no execution without approval
- no CAS weakening
- no broker mutation ordering change
- UNKNOWN remains reconciliation-required/quarantined as designed

## 25. Docker Acceptance Strategy

P1.5.11 Docker acceptance is rerun because P1.5 changes runtime structure/imports/entrypoints even if Docker files are unchanged.

Primary acceptance uses the isolated mock trading compose:
- deploy/trading/compose.trading.yaml

Safety:
- EXECUTION_MODE=mock
- KIWOOM_MODE=mock
- EXECUTION_ENABLED=false
- ALLOW_REAL_EXECUTION=false
- isolated test-state data/reports
- no production broker dispatch

Do not use production shared volumes for destructive crash tests.

## 26. Docker D1 — Image / Source Parity

Build from the exact freeze candidate SHA in a clean checkout/worktree.

Verify image baked source parity for:
- graphs/
- libs/
- scripts/
- config/
- data/specs/
- relevant deploy/runtime files

Required:
- image source matches candidate
- no dirty worktree source accidentally baked
- no secrets baked
- image ID/digest recorded

## 27. Docker D2 — Startup / Health / Readiness

Verify:
- container starts
- healthcheck becomes healthy
- runtime ownership acquired
- ownership generation recorded
- state/reports writable where expected
- root filesystem remains read-only
- execution remains disabled in mock acceptance

Liveness and execution readiness remain distinct.

A healthy container may report execution not ready when recovery/reconciliation is intentionally incomplete.

## 28. Docker D3 — Double-Runtime Ownership

Start a contender against the same isolated ownership DB.

Required:
- exactly one owner
- contender cannot steal a valid lease
- no second tick dispatch
- no mutation
- ownership reason observable

This revalidates the P0-D/P1.3 single-runtime contract after structural refactor.

## 29. Docker D4 — Controlled Restart / Recovery

Test:
- controlled stop/start
- hard kill in isolated environment
- bounded wait while old lease valid
- stale takeover only after legitimate expiry
- recovery_required semantics
- readiness recovery only through canonical readiness chain
- no restart storm
- ownership generation monotonic

No production shared state.

## 30. Docker D5 — SIGTERM / Drain

Verify:
- SIGTERM handled
- in-flight policy respected
- no new tick after shutdown request
- ownership heartbeat stopped
- ownership released
- lock released where applicable
- exit code expected
- OOMKilled = false

Also validate shutdown during bounded ownership wait.

## 31. Docker D6 — Persistence

Across container recreation verify intended isolated persistent state survives:
- runtime ownership DB schema/state as appropriate
- intent-state DB
- state.json
- reports/evidence needed by contract

Do not assert a transient lease itself should survive as live authority after container death.

## 32. Docker D7 — Resource / EOD Smoke

P1.5.11 does not require reproducing a full 6h47m soak if structural changes do not affect memory-critical EOD loaders, but it requires:

- bounded multi-cycle runtime smoke
- memory sample series
- no monotonic runaway obvious in the bounded window
- no OOM
- one isolated closeout/EOD maintenance rehearsal against a production-sized COPY if touched code includes Reporting/Operator/Commander closeout paths

Canonical production data must never be mutated by the rehearsal.

If prior EOD memory fixes are touched, a stronger production-sized memory acceptance is mandatory.

## 33. Docker D8 — Paper Read-Only Connectivity

Because P1.3 acceptance established the read/write separation, P1.5.11 should revalidate when credentials and a safe window are available:

With:
- EXECUTION_MODE=real
- KIWOOM_MODE=mock
- EXECUTION_ENABLED=false
- ALLOW_REAL_EXECUTION=false

Verify:
- auth read PASS
- account read PASS
- open-order read PASS
- explicit BUY/SELL dispatch BLOCKED

No order should be submitted.

If unavailable:
- record PAPER_READ_ACCEPTANCE = NOT_RUN with reason
- mock Docker acceptance may still prove structural/container safety
- final freeze policy decides whether paper read is mandatory based on touched files

If RealExecutor/request/read-write gating changed during P1.5, paper read acceptance becomes mandatory.

## 34. Docker / Observability Independence

P1.5 freeze also confirms trading runtime and observability remain independently deployable.

Verify:
- deploy/trading compose operation does not restart observability compose
- observability API/web mounts are read-only
- UI/API remains read-only with respect to trading authority
- patch-note mount still resolves after P1.5 naming/refactor changes

## 35. Compatibility Freeze Acceptance

Use the P1.5.10 compatibility inventory.

Every remaining seam must be one of:
- intentional stable facade
- historical compatibility
- safety lock
- contract alias
- explicitly deferred migration

No seam may remain with:
- duplicate active business logic
- unknown owner
- ambiguous canonical implementation
- unexplained production consumer

Compatibility wrapper count does not need to be zero.

## 36. Agent Modularity Acceptance

For each primary component demonstrate a focused callable/core:

Strategist:
- explicit input/result contract
- state adapter separated

Scanner:
- explicit input/result contract
- deterministic ranking core
- state adapter separated

Monitor:
- explicit input/result contract
- deterministic entry/exit core
- intent-only result
- state adapter separated

Commander:
- deterministic runtime input/result / route plan
- no LLM authority

Reporter:
- explicit reporting service/facade with LLM role preserved

Executor:
- auditable execution boundary
- mutation owner unchanged
- low-risk extraction only

Supervisor:
- unchanged safety authority

The final package does not need every graph facade deleted.

## 37. Agent Order Acceptance

Production ordering remains semantically identical to the pre-refactor runtime.

No:
- planner
- dynamic reorder
- recursive autonomous delegation
- new LLM gate
- Monitor->broker shortcut
- Scanner->execution shortcut
- Reporter->authority shortcut

Any ordering drift blocks freeze.

## 38. LLM Role Acceptance

Required final statement:

LLM_DECISION_ROLES_BEFORE = 2
LLM_DECISION_ROLES_AFTER = 2

Allowed:
- Strategist
- Reporter

No new LLM invocation in:
- Commander
- Scanner
- Monitor
- Supervisor
- Executor

A helper LLM call that can influence runtime authority still counts as a new decision role and blocks freeze.

## 39. Contract / Schema Diff Acceptance

Compare baseline vs candidate for:
- Agent DTOs
- state compatibility keys
- monitor_output
- scanner_output
- Commander decision
- execution result
- Operator Brief artifact v14
- Reporter/trade report schema
- canonical artifact paths
- Daily UEF authority files

Allowed:
- additive optional fields where explicitly designed
- internal implementation moves
- compatibility aliases

Blocked:
- required-field removal
- silent semantic reinterpretation
- unversioned incompatible schema change
- artifact path drift without compatibility

## 40. Patch Notes / Documentation Acceptance

Required:
- every meaningful implementation tranche has daily patch note
- canonical UI/API patch_notes.md updated
- canonical patch_notes.json updated
- source paths exist
- no historical patch note rewritten to pretend new naming existed earlier
- compatibility inventory current
- architecture docs match final code

Patch-note count is recorded in freeze evidence but is not itself an acceptance metric.

## 41. Security / Secrets Acceptance

Verify:
- .env remains untracked
- no credentials in git diff
- no credentials in acceptance logs
- Docker images contain no .env.real or secret file
- debug artifacts redact sensitive broker/LLM credentials
- generated zip/evidence bundle excludes secrets

## 42. Freeze Evidence Artifacts

P1.5 implementation should generate a bounded final evidence set, for example:

docs/refactor/p1_5_freeze_report.md
docs/refactor/p1_5_freeze_manifest.json
docs/refactor/p1_5_compatibility_inventory.md
docs/daily_patch/<date>_p1_5_formal_freeze.md

Optional non-repo evidence root:
reports/refactor_acceptance/p1_5/<candidate_sha>/

The manifest should include hashes/references for:
- baseline/candidate SHA
- full pytest result
- targeted suite summaries
- UEF freeze-manifest result
- UEF replay outputs
- Docker image digest
- Docker acceptance summary
- Step5 safety result
- compatibility inventory
- independent audit verdict

Do not commit giant raw logs if concise hashed evidence is sufficient.

## 43. Freeze Manifest Schema

Recommended fields:

- schema_version
- program = "P1.5"
- baseline_sha
- candidate_sha
- freeze_tag
- generated_at
- test_summary
- subsystem_summaries
- uef_core_manifest
- uef_replay_summary
- daily_uef_operational_status
- docker_summary
- ownership_summary
- execution_safety_summary
- authority_leakage_summary
- production_write_leakage_summary
- compatibility_summary
- artifact_hygiene_summary
- independent_audit
- final_verdict
- evidence_paths
- evidence_hashes

final_verdict:
- PASS
- PASS_WITH_OPERATIONAL_PENDING
- FAIL

Formal P1.5 freeze requires PASS unless the master plan/human explicitly accepts a narrowly defined operational-pending item that cannot mask structural behavior drift.

## 44. Independent Claude Audit

After Codex implementation and all gates:

Claude performs an independent audit of:
- complete baseline->candidate diff
- architecture adherence
- behavior preservation
- hidden coupling
- state/DTO compatibility
- test weakening/removal
- authority leakage
- production-write leakage
- UEF invariants
- Step5 safety
- Docker evidence
- compatibility inventory

Allowed audit verdict:
- PASS
- PASS_WITH_FINDINGS
- FAIL

Formal freeze normally requires PASS.

PASS_WITH_FINDINGS requires each finding to be:
- non-behavioral
- documented
- explicitly accepted by human
- not safety/UEF/authority related

## 45. Human Freeze Approval

No automated agent should self-declare the final production freeze.

After:
- Codex implementation
- GPT architecture review
- Claude independent audit
- acceptance manifest complete

the human operator gives final approval.

Only then:
- create formal P1.5 freeze tag
- mark master plan P1.5 frozen
- open P1.6 framework-comparison work

## 46. Freeze Tag

Recommended tag pattern:

p1.5-structural-freeze-YYYYMMDD

The tag must point exactly to the accepted candidate SHA, or to a documentation-only freeze commit whose parent is the accepted candidate and whose diff contains only freeze evidence/docs.

If the tag points to a docs-only freeze commit:
- record accepted_candidate_sha separately
- prove no runtime/config/test code changed between candidate and tag commit

Do not tag a dirty/unaccepted branch tip.

## 47. Rollback Baseline

Record an explicit rollback target:
- the pre-P1.5 frozen implementation baseline SHA/tag

P1.5 structural changes must be reversible as one program-level change if a hidden operational regression appears.

Rollback must not overwrite:
- live broker truth
- current runtime ownership database
- execution intent/reconciliation state
- canonical UEF authority artifacts

Code rollback and state rollback are separate concerns.

Never restore stale mutable production state merely to match old code.

## 48. Freeze Blockers

Automatic FAIL / no freeze:

- any new full-regression failure in touched scope
- any UEF frozen-manifest mismatch
- UEF replay nondeterminism
- UEF-7 candidate loss/invention
- UEF-8 pair loss/duplicate identity
- invalid UEF-9 authority
- unexpected production write from replay/test
- any trading-authority leakage
- Monitor direct broker call
- Supervisor bypass
- duplicate broker dispatch
- Step5C CAS/idempotency regression
- readiness evidence ordering regression
- UNKNOWN replay/quarantine regression
- runtime double ownership
- Docker restart storm
- dirty-image/source mismatch
- secret leakage
- required contract break
- new LLM decision role
- test deletion/weakening used to hide failure

## 49. Non-Blockers When Explicitly Classified

Potentially non-blocking if documented and unrelated to structural correctness:

- historical test filename still containing Mxx
- intentionally retained stable facade
- intentionally retained legacy artifact-path alias
- operational Daily UEF freshness failure caused by genuinely stale upstream source, provided deterministic replay/UEF framework gates pass and live-day proof is explicitly marked pending
- paper broker read validation not run when no safe credential/window exists, provided no execution/request-layer code changed and mock/Docker safety gates pass

Human approval determines whether an operational pending item is acceptable for formal freeze.

## 50. Implementation Sequence

### FZ1 — Candidate lock + baseline metadata
- freeze candidate SHA
- create acceptance evidence root
- snapshot environment and diff
- snapshot production roots for leakage detection

### FZ2 — Targeted subsystem regression
- execute every P1.5 packet's required focused suites
- repair implementation-caused failures
- candidate SHA changes if code changes

### FZ3 — Full pytest + artifact hygiene
- full pytest
- exact counts
- baseline failure comparison if needed
- repo scratch before/after audit

### FZ4 — UEF / replay acceptance
- frozen manifest verifier
- UEF 1-9 focused suites
- UEF-7/8/9 replay twice
- deterministic identity comparison
- Daily UEF publication-safety tests
- fresh live-day observation if available/required

### FZ5 — Step5 / authority acceptance
- Supervisor
- execution readiness/evidence
- Step5B/5C/5D
- UNKNOWN quarantine
- static mutation-path audit
- production-write/trading-authority leakage audit

### FZ6 — Docker acceptance
- clean candidate image
- source parity
- startup/health
- double-runtime block
- restart/recovery
- SIGTERM/drain
- persistence
- resource/EOD smoke
- optional/required paper read depending on touched scope
- observability independence

### FZ7 — Compatibility/docs/security acceptance
- compatibility inventory final
- no duplicate canonical owners
- patch notes complete
- docs current
- secrets audit

### FZ8 — Independent audit
- Claude full diff + evidence audit
- resolve all blockers

### FZ9 — Formal freeze
- write freeze report/manifest
- human approval
- create freeze tag
- mark P1.5 frozen
- P1.6 may begin

## 51. Test/Execution Isolation Rules

All destructive/crash/replay acceptance must use isolated roots.

Never:
- hard-kill the canonical production runtime for a test
- run a contender against a different ownership DB and claim double-runtime proof
- point replay into canonical output roots
- use live-account broker credentials
- set KIWOOM_MODE=real for P1.5 acceptance
- run real order mutation as a structural-refactor proof

Use production data only as:
- read-only source
- copied bounded fixture
- explicitly approved read-only broker query

## 52. User-Facing Final P1.5 Freeze Summary

The final freeze report should answer in one page:

- What changed structurally?
- What did not change behaviorally?
- What exact SHA is frozen?
- How many tests passed/failed/skipped?
- Did UEF hashes/replay pass?
- Did Docker ownership/restart/SIGTERM pass?
- Did Step5 safety pass?
- Any production-write leakage?
- Any trading-authority leakage?
- Which compatibility wrappers intentionally remain?
- Any operational pending item?
- Independent audit verdict?
- Rollback target?
- Is P1.6 authorized?

## 53. Acceptance Matrix

| Gate | Required result |
|---|---|
| Baseline/candidate identity | PASS |
| Diff classification | PASS |
| Targeted regression | PASS |
| Full pytest | GREEN preferred; no new failures mandatory |
| Artifact hygiene | PASS |
| UEF frozen manifest | 0 mismatch |
| UEF replay determinism | PASS |
| UEF-7 conservation | PASS |
| UEF-8 pair/ID conservation | PASS |
| UEF-9 authority | VALID |
| Daily UEF publication safety | PASS |
| Production-write leakage | NONE |
| Trading-authority leakage | NONE |
| Supervisor authority | SAME |
| Step5B/C/D safety | PASS |
| Docker image/source parity | PASS |
| Docker single ownership | PASS |
| Docker restart/recovery | PASS |
| Docker SIGTERM/drain | PASS |
| Docker OOM/restart storm | NONE |
| Compatibility inventory | COMPLETE |
| Schema/contract compatibility | PASS |
| Secrets audit | PASS |
| LLM decision roles | 2 -> 2 |
| Independent audit | PASS |
| Human final approval | YES |

## 54. P1.6 Gate

P1.6 is blocked until the P1.5 freeze report states:

P1_5_FORMAL_FREEZE = YES

Only after that may the project compare:
- current runtime
- LangGraph 1.x
- pydantic-graph

P1.6 evaluation must use the frozen P1.5 runtime as the behavior baseline.

## 55. Design Verdict

P1.5 final acceptance layers defined: YES
baseline/candidate identity policy frozen: YES
full pytest policy frozen: YES
artifact hygiene gate frozen: YES
UEF frozen-core manifest gate frozen: YES
UEF-7/8/9 conservation/binding gates frozen: YES
cross-day Daily UEF policy frozen: YES
production-write leakage gate frozen: YES
trading-authority leakage gate frozen: YES
Step5 safety gate frozen: YES
Docker source-parity/ownership/restart/SIGTERM gates frozen: YES
compatibility freeze gate frozen: YES
LLM-role gate frozen: YES
independent audit gate frozen: YES
human approval gate frozen: YES
freeze manifest/tag policy frozen: YES
FZ1-FZ9 sequence frozen: YES
Runtime implementation: NOT STARTED


## 2026-10-09 P1.5 Small-Owner / Executor Closure Gate (v1.2)

In addition to existing FZ1–FZ9 checks, freeze evidence MUST record each newly extracted/touched implementation-owner Python file, exact physical LOC, canonical responsibility and direct test. Any new owner >350 LOC is **FAIL**, not cosmetic PASS. The earlier oversized Reporting owners must be dispositioned using [Reporting v1.2](p1_5_reporting_implementation_packet_v1_2.md). Preserve test conservation, imports/private monkeypatch seams, exact artifact truth, full pytest, deterministic UEF, Docker mock, Step5C/D, R6.2 and human approval.

Executor [v1.1](p1_5_executor_safe_decomposition_packet_v1_1.md) reports before/current/after physical LOC for `execute_from_packet.py` (starting ~4,189); original v1.0 EX1–EX6 plus optional guarded EX7–EX10. Aspirational 1,200–1,800 LOC, interim 2,600–3,200. Any unproven shrink is `SIZE_DEFERRED` or `SAFETY_BLOCKED`, never an invented acceptance. The single ordered Supervisor/readiness/R6.2/Step5C/broker/UNKNOWN authority path cannot be broken to meet a size goal. This amendment does not reopen frozen P1.2/P1.3 or modify runtime code.
