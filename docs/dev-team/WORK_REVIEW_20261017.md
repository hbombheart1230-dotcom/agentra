# Work independent review / next checkpoint queue — 2026-10-17

ACTOR: WORK_REVIEW. Runtime behavior remains frozen. This is a coordination
checkpoint and a tested contract proposal, not role acceptance or integration.

## Reviewed anchors

| Surface | Exact SHA | Outcome |
|---|---|---|
| Reporter | 8ce327ecc71c4c92074c1fa5fb6f00428ba9279b | PARTIAL_WITH_BLOCKERS |
| Monitor | a33c28780592917481eb610a3d69c3948e4a4ead | PARTIAL; shared gate repair/inventory pending |
| Runtime BASE | d773709ba2f70471fad9badba4f92400f7818319 | Comparison oracle only |
| Design parent | 3464351f442d68310aebabf257ae056617b1e36d | Corrected charter 00 / order 01 |
| Integration | d269c906ebadad75a0b833778ebc6a632a388e7c | No worker merge performed |
| main | 2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb | Unchanged |

Both role HEADs have zero hosted workflow runs in the GitHub API query for
their exact SHAs. Older successful CI is not evidence for these trees.
Remote branches observed: main, integration, design, Reporter, Monitor (five).
No branch creation/deletion is part of this checkpoint.

### Delta review after initial validation

New commits appeared during this live review and were inspected without
repeating the old inventory:

- Reporter **523dd9ac227a33eb9e5aa9bed82957e4111c5d9b**, R8-001:
  25 changed files, 22 additional bodies / nine new owners. Total now 286
  moves, 20 facade paths, 38 R4/R8 body-owner files. Closed path sets and
  pinned inventory count extended explicitly. Work independently executed
  seed + R4 proof: **1542 PASS, exit 0, 46.37 s**. The proposed guard also
  restores all 286 facade wrappers to BASE; **13 PASS normal + 13 PASS -O**.
  The proposal has separate fixed inventory SHAs for R7 and R8; arbitrary
  new SHA/working-ledger authorization remains forbidden. New R8 `-O` role
  suite and hosted CI are NOT_RUN; earlier R7 `-O` proof stays R7 evidence.
- Monitor **6b2a91340262e1e7e221582646da2beb0b1965f8**, CP-000:
  four documentation/evidence files only. Inventory now 92 files / 408
  function/method/type entries and four named READY batches. Runtime/tests
  identical to a33c287, so initial Work test evidence can be reused with this
  explicit docs-only lineage, not called a fresh run. Issue checkpoint
  6232121991 acknowledges the corrected Monitor-only assignment.

R8 candidates `_to_markdown` and `build_trade_report_detail_view` listed in
R8-A below are now moved: do NOT reassign or redo them. Continue R8-B/R8-C.
CP-000 likewise completes the initial inventory packet of M5-A; deepen
caller/effect/parity coverage rather than recount 408 entries.

**P15-WORK-003 / P2, OPEN:** AST direct-call triage is not transitive effect
proof. In R8, reporter_analysis._latest_day and trade_explain._latest_day
call `_iter_jsonl`; load_reporter_snippet_for_run calls injected `read_json`.
The triage's SAFE_MOVE_CANDIDATE/no-direct-IO label must distinguish
READ_VIA_CALLBACK. Preserve late lookup and require temp-dir BASE/current
content, missing/malformed input, exception and callback-order fixtures.
No observed runtime regression in the executed R8 tests. Other safe work
continues; do not waive the need for these fixtures at role acceptance.

F-R7-03 source-link fix in Reporter JSON is observed; the existing paired
note still describes R7/264. Update JSON and Markdown together for R8/286,
accurate transitive-read caveats, the controlled-lane retained decision and
supersession of T3 v4. Official UI publication stays Work integration-owned.

### Monitor M-001/M-002/M-004 boundary review

At CP-000 the plan is not yet implementation acceptance. Work inspected
the exact three M-001 source bodies and monitor_node consumers: entry_evidence
47 LOC; monitor_exit.observability 290 LOC; order_lifecycle 78 LOC. Observability
builds output, order lifecycle projects already obtained order_status into
state[monitor] after intent generation, and entry evidence still calls the
same injected scoring/extraction collaborators. Within this structural
mandate the three exact whole-blob/strict-identity moves may proceed; do not
generalize to monitor_exit policy/price/guard modules. This refines old
KEEP_WITH_REASON inventory dispositions, not trading authority. Update that
ledger rationale explicitly; prove callback invocation order/arguments,
mutable aliases, exceptions and same import/monkeypatch identity.

For M-002, feature_alias_map / feature_context_from_state are observation
views; original selected_snapshot remaining price/quote/feature authority
and module statements must remain AST-identical. monitor_posture_for_cycle
and transition snapshots describe existing intents/readiness but can affect
persisted observation/events: retain exact branching, thresholds, mutation
and callback ordering. M-004 display functions use to_float/_is_trueish;
maintain use-time patching in the ORIGINAL reasons facade. All actual
reason-priority/hard/soft/emergency definitions stay byte/AST identical.

## Independently executed evidence

Linux, Python 3.12.14, isolated venv, pytest 9.1.1. Consumer tests additionally
use PyYAML 6.0.3. No real broker, LLM or persisted production report input.
Commands and results are in WORK_REVIEW_20261017.json. Counts in different
rows overlap and MUST NOT be added as unique coverage or project progress.

| Selection | Result | Exit |
|---|---|---|
| Reporter seed + R4 body proof | 1423 PASS | 0 |
| Reporter original current T3 authority path test | 1 FAIL (numbered R4 owner) | 1 |
| Same Reporter selection, Python -O | 1423 PASS | 0 |
| Reporter ABI / symbol ledger / AI / node / service / story consumers | 179 PASS | 0 |
| Monitor role + existing T3/T4-B structural gates | 167 PASS / 5 FAIL | 1 |
| Monitor role + Wave B, Python -O, isolated TEMP | 916 PASS | 0 |
| Monitor intent / cascade / exit / freshness / price / handoff consumers | 151 PASS | 0 |
| UEF2A/UEF5_1, both BASE and Reporter, same environment | EACH 119 PASS / 9 FAIL / 1 SKIP | 1 |
| Proposed facade guard mutation suite | 13 PASS normal; 13 PASS -O | 0 / 0 |
| Deliberately corrupted same-path facade: old T3 v4 + moved-body AST proof | 265 PASS (demonstrates gap) | 0 |
| Same corrupted facade: proposed new guard | REJECTED, as required | 1 |

Monitor's eleven destination files independently match the raw BASE Git blobs.
No normalized-only equivalence claim is needed. The five failures reproduce
the exact two T3 + three T4-B legacy-owner/shim resolution failures reported
by the worker, not a newly observed policy regression.

## Second live delta review — R9 and Monitor CP-001/002

**Reporter dd0b378b46dff0c2ecf6699a4b08776fd4412b76** after 523dd9a:
12 changed files; 27 additional bodies from intraday_trade_reports,
trade_report_common and symbol_read_model; three owner files. Total now
**313 functions /23 facade paths /41 R4-R9 body-owner files**. Work ran the
updated seed + body proof: **1680 PASS, exit0, 48.44s**, Linux Python3.12.14.
The proposed full facade guard supports this third literal inventory SHA:
all23 facade modules reconstruct to unchanged d773709, **13 PASS normal
(2.248s), 13 PASS -O (2.219s)**. R9 role-suite -O is NOT_RUN; no extrapolation
from R7. Source diff excludes graph/authority/controlled-lane execution paths.
New file inventory is developer classification evidence, not a new complete
independent architecture inventory. Work did not regenerate the 500-file scan.

**Monitor a0ea6ff31eaebd90f9414d34fd7c6858b1ab3aa1** after 6b2a913:
two commits, CP-001 0735c67 and CP-002 a0ea6ff. Three new whole BASE blobs
(entry_evidence/observability/order_lifecycle, 415 LOC, 5 functions) plus five
named observation bodies in feature_context_views and entry_state_views.
Work independently verified raw equality for all three added whole blobs,
inspected the body-template verifier and negative tests, and ran original
role + continuous + body-view tests: **273 PASS, exit0, 6.75s**. Whole-module
AST templates protect unmoved definitions/statements AND generated owner AST;
normal/-O child negatives and legacy/canonical pickle/import identity pass.
Source diff leaves graphs, authority paths and workflows unchanged.

Work reran impacted Monitor consumers plus original T3/T4-B:
**170 PASS /5 FAIL, exit1, 5.40s**. The same two T3 /three T4-B tests fail at
their first unmapped legacy owners. This is not proof that no later owner
would fail after the first error is repaired. Shared queue must additionally
register **libs/runtime/monitor/entry_evidence.py →
libs/agents/monitor/projections/entry_evidence.py** with strict identity checks.
Keep the five exact M-002 function transfers in work_monitor_current_tree.py
as separately proved whole-module reconstruction, not facade/path exemptions.

These snapshots show substantive commits during this review. They are not a
promise of running workers after this session. Both roles remain intermediate;
P15-WORK-001 integration open and P15-WORK-003 characterization open.
Next Reporter packets: transitive-read/missing/malformed/offline byte fixtures,
consumer/DTO/API map and synchronized current proposed notes. Next Monitor
packets: M-003 defaults, M-004 display, then complete role responsibility and
broader parity/negative proof. Do not start a fresh full Strategist inventory
while Reporter safe scope/acceptance is open; next-role program belongs to
Work after role freeze and reuses existing frozen-tree evidence.

The UEF failure IDs match between BASE and Reporter: eight UEF2A failures
read absent reports/data files; one UEF5_1 failure flags the same
libs/reporting/evaluation/uef6/validation_replay.py import boundary. Existing
skip: no persisted q9_day_validity artifacts. This substantiates THESE nine
historical failures only. It does not account for the worker's second
UEF5_1 failure (ten claimed total); request its exact ID/environment rather
than inventing a waiver. Actual persisted/LLM parity remains unproved.

## Shared findings and tested proposal

### P15-WORK-001 / F-R7-01 — P1, integration OPEN

T3 v4 permits an entire approved facade path. A local detached negative probe
changed only the body of trade_report_ai._build_skipped_separated_report to
return {"silently_changed": True}, preserving its name/signature. Applying
the stored T3 v4 patch and running its after-BASE path guard plus all 264
moved-body AST cases returned 265 PASS. This is a real test-strength gap,
not evidence that the actual worker introduced that behavior.

Proposal: proposals/reporter_facade_guard.py and its mutation tests.
It loads the move inventory from immutable reviewed Git object 8ce327e;
checks exact wrapper header/forwarding, constrained owner imports and sys
binding, then restores ONLY approved wrappers to their BASE definitions.
The complete restored module AST must equal d773709, including unmoved
definitions, class bodies, assignments, executable statements and order.
It does not import/execute a facade. Explicit checks stay active under -O.

Positive: all 264 wrapper changes across **20 distinct facade paths** pass.
The ledger has **29 distinct body-owner files**. Prior handoff's "21 modules"
needs denominator reconciliation; do not silently equate it to either count.
Twelve real-source negative mutations are rejected in both modes, including
same-path unmoved body, module calls/assignment/order, wrong/late imports,
wrapper ABI/argument/body/duplicate changes. The deliberately committed
local probe (not pushed) also fails this guard.

This proposal MUST run together with the existing owner-body / use-time
lookup proofs. It is not a replacement for them. No T3, T4, workflow,
historical pin, skip or allowlist was changed in a worker tree. Future move
inventory extensions require a new exact-SHA review; never read an editable
ledger as an automatic authorization list. P1 remains open until a separately
authorized shared candidate wires and independently verifies the guard.

### P15-WORK-002 — P2, test process isolation

Initial Work parallel -O run reused the OS temp root and ended with 526 PASS
and 390 setup ERROR (103.91 s): missing /tmp/Trading_Agent_System/pytest/basetemp-5.
conftest.py derives the path from os.getpid(); isolated command PID namespaces
can share that PID and filesystem. This namespace explanation is inferred
from the observed path and source, not a native Windows reproduction.
Work's first run failed to separate TEMP and is not a runtime regression.

Distinct existing TMPDIR/TEMP/TMP roots per command eliminated the error:
same 916 cases passed in 48.33 s. Use <session>/<role>/<batch>/<command>;
also isolate PYTHONPYCACHEPREFIX/cache if cold-start comparisons matter.
Set variables BEFORE interpreter startup (tempfile/conftest cache roots).
--basetemp alone is insufficient: pytest_configure overrides it. Do not
remove another process's directories or broaden cleanup rights. No cleanup
policy or shared conftest modification is authorized by this note.

### Shared integration queue (Work only)

1. Keep the existing six exact Monitor T3 and five T4-B mapping pairs in
   shared_contract_patch_R4.diff; strict source-AST identity validation first,
   original assertions against canonical owner second. Wrong target, extra
   import and appended executable statement must fail normal and -O.
2. Add exact Reporter {narrative,read_models} and Monitor {events,projections}
   package sets only in a candidate containing both role trees. Unknown
   packages must still fail. No suffix following or arbitrary shim chasing.
3. Replace the unguarded whole-path exception in T3 v4 with proof-gated
   exceptions using this proposal and owner proofs. Keep historical authority
   restrictions/pins and add negative changes outside approved paths.
4. Required CI must include BOTH Reporter seed and R4 body tests, the Monitor
   strict role test, the facade guard/mutations and existing mandatory suites.
   Python 3.12 Linux/native Windows, -O, targeted 3.13/3.14 as supported.
5. Do not apply the Reporter stored CI patch to Reporter alone: it references
   a Monitor test absent there. Do not merge either implementation branch now.
6. Work owns both official UI note formats. The actual API data source is
   apps/api/adapters/patch_notes.py RELATIVE_PATH pointing to
   docs/trading_agent_patch_notes_detailed_update/patch_notes.json.
   Reporter proposed note provenance must cite REPORTER_ROLE_HANDOFF_R7.md,
   not claim official publication. This design note is review/proposal only.
   The design branch's official note store is older (114 entries) than the
   worker/runtime lineage. Do not merge it over the newer store. The paired
   proposals/work_review_patch_note.json/.md are synchronized proposed-only;
   Work applies them to both latest official formats at final integration.

## Ownership decision: controlled_mock_lane_report

Disposition: REPORTER presentation/read adapter, operational dependency
retained at libs/reporting/controlled_mock_lane_report.py for this cycle.
Actual consumers include trade_report_markdown_clean, single_trade_report,
and scripts/run_ai_trade_report_batch.py. It reconstructs/render lane evidence;
it does not submit orders. _ledger_row reads the operational submissions
ledger; _fixed_lane_strategy embeds fallback display facts. Preserve their
bytes, matching precedence, exception handling and all Q10/Q12 values.
Do not transfer operational ledger ownership, split/move these readers, change
selection/truth semantics, or enable Research execution. The unresolved
ownership label is cleared; relocation remains intentionally retained.

## NEXT_READY — no per-batch operator sign-off

Each packet ends with exact pushed SHA, focused proof, finding ACKs and at
least two subsequent safe packets where possible. Check the role Issue for
new comments at checkpoints. A commit is not a reason to stop a live session.

### Claude / Reporter — Issue #11, own branch only

**R8-A READY: evidence-based remainder triage and safe deterministic bodies.**
Inspect remaining blockers only; do not redo the 264 moves. Concrete token
false-positive candidates: trade_explain._to_markdown (156 LOC; Path is an
annotation), trade_read_model.build_trade_report_detail_view (187 LOC;
"open" is reporting status text). Their inspected calls contain no direct
filesystem operation. Follow every collaborator before claiming purity;
preserve callbacks, aliases, output order and exact facade lookups. Classify
all remaining rows by actual call/effect evidence. Where proven safe, extract
coherent groups with existing R4 AST/ABI/lazy binding + byte/exception proof,
owners <=350 LOC. Retain read/write/network/authority paths. failure_report's
utc_now_iso is an injected clock callback: characterize it, do not label pure
or alter generation/retry policy just because "retry" was a token hit.

**R8-B READY: offline producer-consumer parity.** Add small synthetic temp-dir
fixtures for JSON/Markdown, null/malformed/missing artifacts, key order,
exceptions and callback sequencing. Map renderer/read-model/API consumers
and obsolete report candidates; do not delete/disable reports. Keep LLM,
broker truth, writes and persisted production inputs outside tests. Reuse
existing immutable BASE fixture evidence for unchanged bodies. Report the
unaccounted second UEF5_1 failure ID/environment, reconcile 20 facade /29 owner
denominators and correct proposed-note R7 provenance.

**R8-C READY: complete responsibility coverage.** Use the existing register;
account for unclassified subtree functions/importers, effective duplicate
definitions, facade/ops/shared/research boundaries. Record intentional retained
controlled-lane adapter. Module identity four-callable group stays retained
until actual identity-safe proof; do not force moves for LOC targets. End
ROLE_READY only after all safe scope and proofs are complete, else continue
another READY group. Shared P1 repair is Work's queue, not Claude's stop gate.

### Codex / Monitor — Issue #12, own branch only

**M5-A READY: symbol-level remainder/consumer coverage.** Expand the existing
71-row file/boundary ledger rather than recreate it: list retained functions,
actual caller, pure/effectful segments, policy authority, monkeypatch seams,
proof SHA and next action. entry_evidence combines quote extraction and
_resolve_monitor_entry_scoring_config; retain that policy boundary. numeric
under monitor_exit remains within the protected boundary even if short.
Whole-role completion means justified retention, not compulsory relocation.
Propose any further safe event/view group only after caller analysis.

**M5-B READY: strengthen consumer and negative proofs.** Characterize event
and projection nested aliases, callback-result mutation, exception messages,
ordered effects, absent/malformed data and import order using synthetic inputs.
Retain signature/body/blob checks. Add fail-closed negative policy/Broker/
Supervisor leakage tests without altering guard policy or mocking away the
boundary being asserted. Match BASE outputs including unchanged mutable
inputs; do not describe all eleven modules as immutable pure functions.

**M5-C READY: role freeze evidence / platform matrix.** Reuse now-independent
Linux evidence at exact a33c287; rerun only impacted tests for new SHAs. Attach
existing native Windows replay command/results (149 inputs/689 sampled
variants, not full 2879 replay). Queue missing platform proofs and shared five
FAIL separately; no blanket green. Preserve protected graph/policy hashes,
intent-only behavior, retained-owner rationale and two next actions. Do not
audit Reporter or build a persistent runner under this assignment.

## Session exit / daily digest contract

Last reviewed heads: Reporter dd0b378 (1680 role tests and guard), Monitor
a0ea6ff (273 own-role tests, impacted consumers and shared failures). Next review is
only the diff since those heads plus changed contracts/consumers and new
Issue ACKs. Commits/checkpoints show work during this review window; they do
not prove a process will continue after session exit. No scheduler was created
or verified by this review, and no automatic restart is claimed. Account
remaining credits are UNKNOWN. No routine operator decision is required.

Overall P1.5 percentage is NOT_ESTABLISHED: complete-role acceptance
denominators and future roles remain open. Reporter/Monitor are intermediate
milestones, not two finished roles. Strategist/Scanner programs are next only
after these roles freeze; existing prior moves/PERF are inherited evidence,
not fresh tasks. Main merge remains prohibited pending whole-P1.5 acceptance
and explicit operator authorization.
