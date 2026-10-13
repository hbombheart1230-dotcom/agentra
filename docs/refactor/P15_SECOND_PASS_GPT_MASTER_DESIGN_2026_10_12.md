# Agentra P1.5 Second Pass — GPT Master Design

> **Third Pass source-verified design (2026-10-13):** [P15_THIRD_PASS_GPT_REPORTER_INCLUSIVE_DESIGN_2026_10_13.md](P15_THIRD_PASS_GPT_REPORTER_INCLUSIVE_DESIGN_2026_10_13.md). Following the user-supplied Codex PASS_WITH_FINDINGS for the parity P1 fix, Reporter pure read-model and guarded bundle-runtime work, second-pass Owner facade/tuple debt, and remaining agent giants precede Wave D. Older Reporter exclusion was only for the completed S1-S6 second pass.

> **Sequencing correction (2026-10-13; authoritative):** [Pre-Wave-D structural closure order](P15_PRE_WAVE_D_STRUCTURAL_CLOSURE_ORDER_2026_10_13.md). S1–S6 bulk → Codex checkpoint → GPT all-seven-agent residual review **including Reporter** → Claude third-and-later bulk module splits **including Reporter** → Codex structural closure audit → **Wave D last**. Any older direct second-pass-to-Wave-D language below is superseded. Reporter is excluded from *S1–S6 only*.
Baseline: refactor/p1.5 @ 1f7add2b0f9b5a33399da27edcdd2f390bdf911b
Status: DESIGN SPECIFICATION / NOT IMPLEMENTED / NOT FINAL_ACCEPTED
Author: GPT architecture; implementation owner Claude; independent verifier Codex.
Reporter implementation is OUT OF SCOPE.
**Canonical current-vs-target tree (Reporter included, Reporter code frozen):** [P15_CANONICAL_TARGET_TREE_AND_REPORTER_ASIS_2026_10_13.md](P15_CANONICAL_TARGET_TREE_AND_REPORTER_ASIS_2026_10_13.md). This reference distinguishes physical existing modules [E] from implementation proposals [P]; do not interpret the 466 files under libs/reporting/ as Reporter-only.

## 1. Goal, evidence boundary and scope
Modularize Agentra around **single responsibility, least authority, narrow interfaces and one canonical owner per behavior**. Do not optimize for file length alone. Retain the seven-agent orchestration semantics, existing prompts, ranking, ordering and release authority. Wave A/B/C have Codex PASS_WITH_FINDINGS, not final integration acceptance.

At pinned HEAD the non-Reporter Python implementation scope contains **340 files (~4.2 MB)** under graphs/, libs/runtime/, libs/execution/, libs/supervisor/, libs/risk/supervisor.py, libs/agent/ and apps/operator_ui/ (Reporter-named paths excluded). Companion machine file lists these files. This is a SOURCE SCOPE census, not a claim of proven deadness or completed semantic analysis of every nested function. Detailed function-level decisions concentrate on actual multi-responsibility hotspots and authority boundaries; small existing Owners default to KEEP_PENDING_REVIEW unless a named consumer conflict emerges.

| Area | Decision | Expected implementation |
|---|---|---|
| Monitor node + entry signal + exit policy | SPLIT P0 | entry/exit context, pure evaluations, result projection; no broker |
| Scanner | SPLIT P0 | candidate source, features, score, canonical ranking, selection, evidence |
| Commander | SPLIT P0 | deterministic policy/decision/projection; preserve run order |
| Operator UI / Brief | SPLIT P0 | read DTO, section assembly, Korean rendering, existing brief LLM and persistence adapters |
| Strategist | SPLIT P1 | context + deterministic planning + projection; LLM call frozen |
| Supervisor | KEEP / SAFETY_LOCK | sole approval verdict; store transition semantics preserved |
| Executor | SAFETY_LOCK / conditional pure extraction | one ordered broker mutation owner; no speculative coordinator split |
| Shared runtime, adapters, aliases | KEEP / REVIEW | reuse existing owners, classify actual consumers, avoid redundant wrappers |
| Reporter, libs/reporting and report prompts | EXCLUDE | no implementation changes |

## 2. Architecture and actual capabilities
- **PURE POLICY** receives typed snapshots/scalars only; no direct graph state, facade module, filesystem, logging, clock, globals, broker, LLM, or environment. It returns a deterministic value/proposal.
- **READ MODEL** gets an injected explicitly read-only provider. No persistence or mutable whole-State access. Any live market-data nondeterminism must be frozen in tests.
- **STATE PROJECTION** computes a proposed output or ordered patch, but the node applies the patch at the original exact source location. Never move state writes across an early return, exception, event or guard.
- **LLM OWNER** remains the existing Strategist LLM boundary; the existing Operator Brief generation path also calls chat and requires exact call-count, prompt, model, retries, timeout, error and fallback parity. Do not introduce a new LLM role in Commander/Scanner/Monitor/Executor.
- **PERSISTENCE OWNER** retains existing canonical artifact/state writers. UI presentation/read-only modules must not write.
- **MUTATION OWNER** remains execute_from_packet -> existing readiness/guards -> intent_execution_owner -> executor.execute. CAS/admission, current owner/generation, broker outcome and UNKNOWN quarantine stay in that sequence.
- **PUBLIC FACADE** preserves import path, ABI and historical monkeypatch seams. It may remain large while its internal responsibilities become narrow. Do not use the facade as an unbounded capability token in new Owners.

Proposed contracts (names are DESIGN-ONLY, not existing imports): CandidateContextView; RankedCandidateProjection; EntryEvidenceView; EntryEvaluationDraft; ExitEvaluationDraft; CommanderDecisionInputs; OperatorBriefFacts; ExecutionTraceView; OrderedStatePatch. Prefer existing TypedDict/contracts where possible. Frozen shallow dataclass is insufficient if dict members are mutable: snapshot nested maps or restrict their use.

## 3. Frozen semantics
1. Scanner: exact score operands, sort stability, canonical rank, confidence/risk tie-break, Commander overlay, selected symbol, rank propagation, runner-up evidence. Existing state scanner_ranked fields must not be recomputed in another module.
2. Monitor: intent-only; same position capacity, pending BUY, post-exit cooldown, closeout window, rank-1 opening probe and evidence, sizing, stop/hold, exit confirm, order lifecycle and entry/exit order. No broker or supervisor.
3. Strategist: exact LLM prompt/model/profile/call-kind/token budget/retry/timeout/parser/fallback/call count. State/candidate regime and policy decisions cannot change.
4. Commander: deterministic routing, ownership, fast paths, graph sequence, phase transition, cache/shadow, preflight and existing state fields. No new LLM or direct broker access.
5. Supervisor: verdict is sole approval source; legacy two-phase and SQLite intent store cannot gain or lose authority through helper relocation.
6. Executor: submission_dispatched invariant; once an order may have been submitted, do not replace ACCEPTED/REJECTED/UNKNOWN with NOT_SENT on downstream error. Step5C logical/physical CAS, R6.2 evidence, duplicate guard, broker mutation choke, quarantine and recovery order untouched.
7. Operator UI: source of truth, Reporter provenance, original JSON field/missing-value semantics, precise Korean Markdown text/whitespace, prompt/retry semantics, artifact paths, version and cache invalidation.
8. Legacy: M10/M11 historical tests, runtime modes, Q10/Q12/UEF, state/env/lock aliases maintained pending independent migration proof.
9. No new runtime production writes, order submissions or real LLM calls in tests.

## 4. Explicit ownership
- graphs/nodes/monitor_node.py owns scheduling of entry/exit and ordered state application; libs/runtime/monitor/ plus existing monitor_exit/ own only bounded pure/read model helpers. libs/runtime/intraday_monitor_signals.py keeps its public entry function and single precedence decision while delegating feature calculations.
- graphs/nodes/scanner_node.py owns graph state writes; libs/runtime/scanner/ owns canonical scoring/rank/selection calculations. Exactly ONE canonical ranking calculator must produce downstream rank.
- graphs/nodes/strategist_node.py owns orchestration and existing LLM call; libs/runtime/strategist/{context,policy,output}/ reuse existing Owners. No copy of LLM invocation in output Owners.
- graphs/commander_runtime.py owns ordered orchestration; libs/runtime/commander/ owns deterministic policy inputs and projection. Existing fast_paths, ownership and execution helpers stay.
- apps/operator_ui/data_access_core.py preserves existing public compatibility surface; apps/operator_ui/data_access_brief* and new bounded brief section/format Owners own read/presentation details only. Original brief LLM and persistence action must remain explicit controlled call sites until parity fixtures permit further isolation.
- libs/risk/supervisor.py, libs/supervisor/{two_phase,intent_state_store}.py and libs/execution/** remain safety authority; no new approval module or submitter.
- Reporter is not in this second-pass mutation scope. Read-only edges to Reporter contracts remain.

## 5. Implementation order — BIG bulk tranches
S1 Monitor node + signal/exit pure segments; S2 Scanner scorer/ranking/selection; S3 Commander policy and decision; S4 Operator Brief sections/render/input; S5 Strategist context and projection; S6 only proven low-risk Supervisor/Executor/legacy/numbered Owner cleanup. These are implementation batches in the SAME branch, NOT six new waves or approval checkpoints.

Every tranche must deliver a visible before/after **largest function LOC**, actual moved responsibilities, new Owner sizes <=350 LOC, exact original state/event/exception order, and test parity. Reuse existing Owners (Scanner 20, Strategist 27, Commander 25, Monitor-exit 24, Executor 19 Python modules at baseline), don't create generic helpers or numbered fragments without cohesion. No tiny one-function completion handoffs.

## 6. Stop, defer and verification gates
- BEFORE each complex slice, freeze immutable baseline inputs/outputs and event/side-effect order, direct consumers and monkeypatch targets; compare old/new on deterministic offline fixtures.
- Compare return data, ordered State mutations, event ordering, audit artifacts, exception type/phase, imports and use-time patch behavior.
- Unmoved code AST equality is helpful but does not prove moved statement equivalence.
- Run focused consumer suites after each large tranche; Codex independent review at integrated second-pass boundary, except a possible safety regression stops immediately.
- Any unresolved broker/Step5/UNKNOWN/Supervisor or LLM/ranking drift: STOP that slice, rollback only that slice, report BLOCKED rather than cosmetically claim success.
- Executor real-case immutable fixture currently unavailable; execution core remains SAFETY_LOCK. Step5B Fix4 has eight baseline EXECUTION_DISABLED failures: do not weaken test or call them new failures.
- Offline tests currently read yfinance public data and are nondeterministic: isolate/freeze these sources for reproducible differentials.
- controlled_mock_lanes write isolation, real frozen report/LLM parity and real-case executor parity remain OPEN/BLOCKED; do not replace them with synthetic fixtures to assert real parity.
- On meaningful code modification sync UI-linked docs/trading_agent_patch_notes_detailed_update/patch_notes.json and patch_notes.md; append concise daily evidence. Session-scoped pytest output auto-cleans on success, failed evidence bounded.
- C:\Agentra live, dirty Q12, main, real LLM/broker, production artifacts, scheduler, Docker remain protected. ZIP generation prohibited.

## 7. Completion and Wave D
The second pass finishes only after giant-function responsibility boundaries have materially improved in P0/P1 and all changed slices pass relevant focused gates. Document genuinely unsafe deferred functions separately and do not invent final success. Codex reviews the aggregate pinned diff. Wave D/P1.5.11 THEN runs full native pytest, Docker mock, UEF replay/cross-day/determinism, frozen Reporter/LLM provenance parity, Executor real-case replay and mock-lane write isolation plus trading-authority leakage checks. FINAL_ACCEPTED/main merge/production require explicit user approval, not this design commit.

Source documents: P15_FAST_TRACK_FIRST_PASS_2026_10_12.md; work_orders/CURRENT.md; P15_FAST_TRACK_WAVE_C_018.md; evidence/P15-FAST-TRACK-WAVE-C-CLAUDE-019.md; p1_5_wrapper_cleanup_inventory_2026_10_12.json; p1_5_commander_runtime_implementation_packet_v1_0.md; p1_5_executor_safe_decomposition_packet_v1_1.md.
