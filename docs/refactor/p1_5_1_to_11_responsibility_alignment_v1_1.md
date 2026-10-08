# P1.5.1–P1.5.11 Responsibility-Minimal Design Alignment v1.1

Status: CROSS-STAGE DESIGN REVIEW COMPLETE / IMPLEMENTATION AND FINAL ACCEPTANCE NOT PROVEN
Review date: 2026-10-08
Authority: P1.5/P1.6 Master Plan, P1.5 Refactor Constitution, and the existing v1.0 per-subsystem implementation packets.
Review source: design/p1.5-p1.6-modernization @ 891f3438da50706498582a0e4b3714a28ec1c84e
Reporting implementation observation: codex/p1.5-reporting, cumulative code ancestry through fbfab9b3f56152f08a2ce50e69cc8173496fde7d (before branch-consolidation documentation change).
Scope: design/acceptance consistency review ONLY. No runtime Python modification, no baseline gate waiver, no new strategy, no framework migration.

## 1. Decision and authority

All P1.5.1–P1.5.11 design packets were checked against the original constitutional objective: **minimum responsibilities in each boundary; one authoritative implementation owner per concern; independently callable Agent cores; explicit contracts and state adapters; stable, small public compatibility façades; behavior and safety unchanged**.

**Verdict: original decomposition design remains valid. DO NOT restart design or repeat R2-A/B/C completed extraction.** The main missing cross-stage guarantee is traceable *responsibility ownership evidence*, rather than a newly designed package hierarchy. This supplement makes that proof mandatory during each implementation batch and at P1.5.11 freeze.

Source precedence:
1. P1.5 constitution and master safety/sequence gates remain authoritative.
2. Original per-stage v1.0 implementation packets remain as frozen historical, detailed technical instructions (not rewritten).
3. P1.5.2 Reporting v1.1 controls residual Reporting ownership/acceptance.
4. This cross-stage v1.1 supplement controls **shared responsibility-minimization/evidence criteria** across all stages. If a conflict is discovered, record an explicit decision before implementation; do not silently overwrite a safety/contract rule.
5. P1.5.10 explicitly decides whether compatibility aliases can retire. P1.5.11 is the final acceptance and human-approved freeze.

### Important distinction
The PREP package records DESIGNS as complete. It does not establish that runtime work for P1.5.3–P1.5.11 was implemented, that P1.2/P1.3 was frozen, or that the P1.5 full-suite gate passed. The prior P1.5.1 and R2-A/B/C extraction PASS results on implementation branches remain recorded, but are not automatically full P1.5.2 acceptance.

## 2. Cross-stage review matrix

| Stage | Existing design and ordered batch | Design alignment | Explicit reinforcement required before batch closure |
|---|---|---|---|
| P1.5.1 | Reporting unreachable tail and shadowed duplicate cleanup ONLY, original Reporting packet §8 | ALIGNED; narrow cleanup | Prove DEAD with reachability/last-definition and import/test search; preserve wrappers, outputs and baseline gate. No additional extraction under P1.5.1. |
| P1.5.2 | Reporting R2-A AI / R2-B Markdown / R2-C Story, Reporting packet v1.0 + v1.1 | ALIGNED, extraction checkpoints PASS; final acceptance OPEN | Classify each façade symbol and direct caller; existing single Owner, compact façade, protected monkeypatch/LLM/truth contracts, responsibility-organized test migration, full-suite and independent acceptance. Use v1.1 for residual actions. |
| P1.5.3 | Operator UI/Brief O1–O6, Operator UI packet v1.0 | ALIGNED; acceptance strengthening | `data_access.py` public façade; `data_access_core.py` only minimal dispatch; make canonical truth, LLM attempts, persistence/cache, Markdown rendering and UI read-model each single-owner. Keep Brief artifact v14. O6 visibility/period summary must remain separate from Brief LLM moves. |
| P1.5.4 | Strategist S1–S5, Strategist packet v1.0 | ALIGNED; acceptance strengthening | `StrategistAgentInput/Result`, `run_strategist` standalone fixture, state mutation only via adapter, LLM prompt/repair/context call parity, retained `strategist_node(state)` facade; Scanner ranking authority unchanged. |
| P1.5.5 | Scanner SC1–SC7, Scanner packet v1.0 | ALIGNED; acceptance strengthening | One deterministic candidate scoring/selection Owner; exact rank/score/tie-break/eligibility fixtures; `run_scanner` runnable without graph; `scanner_node` only adapter; Scanner soft chart-fit must never become Monitor hard entry veto. |
| P1.5.6 | Monitor MO1–MO8, Monitor packet v1.0 | ALIGNED; clarify signal-engine extraction | `run_monitor` standalone fixture; entry/exit evaluation owns deterministic signals, arbitration emits at most one intent, no broker IO; graph compatibility state writes owned by adapter. MO7 signal-engine **audit is required**; extra submodules conditional on proven responsibilities/size and no duplicate `monitor_exit` implementation. |
| P1.5.7 | Commander/runtime C1–C10, Commander packet v1.0 | ALIGNED; acceptance strengthening | `CommanderRuntimeInput/Result/RoutePlan`; policy composition, phase routing, state patch, reporter hooks, runtime ownership each distinct; service independently callable in fixture; no hidden Scanner/Monitor policy, new LLM or Supervisor/Executor mutation authority. |
| P1.5.8 | Runtime naming N1–N7, naming packet v1.0 | ALIGNED; migration discipline | Name-only canonicalization; preserve old API/env/state/CLI/deploy aliases until consumer proof. Never combine naming sweep with semantics extraction; no historical record rewrite or Step5/UEF/Q cosmetic rename. |
| P1.5.9 | Executor EX1–EX6, Executor packet v1.0 | ALIGNED **SAFETY EXCEPTION** | Only observability and canonical artifact coordination (optionally pure order views) may move. Do NOT force `execute_from_packet.py` to a thin 300-LOC façade. Keep Supervisor approval, guard/readiness/CAS, BrokerOutcome/UNKNOWN, cancel/recovery and `execute_owned_order` mutation sequencing auditable in one owner. |
| P1.5.10 | Wrapper cleanup CW1–CW7, compatibility packet v1.0 | ALIGNED; crucial cross-stage dependency | Every façade/alias from stages 1–9 receives active-consumer proof: KEEP_STABLE_FACADE / MIGRATE_THEN_REMOVE / HISTORICAL_COMPATIBILITY / CONTRACT_ALIAS / SAFETY_LOCK. Remove only ZERO_CONSUMER verified wrappers; a tiny stable wrapper can remain. No duplicate active implementation permitted. |
| P1.5.11 | Full regression + Docker + UEF replay + freeze, final packet v1.0 | ALIGNED; **ADD ARCHITECTURE PROOF GATE** | Beyond tests and safety checks, require reconciled end-to-end Owner ledger, independent Agent callable fixtures, no hidden cross-owner cycles, explicit unresolved wrapper/size exceptions, maintained unit/integration/regression suite inventory, audit evidence hashes and human freeze decision. |

Assessment terminology: ALIGNED means the *documented intent* is consistent. It is **not** evidence the implementation is done or the detailed design is mathematically optimal.

## 3. Fixed responsibilities across seven Agents and supporting subsystems

### Commander / Strategist / Scanner / Monitor / Supervisor / Executor / Reporter

- **Commander**: deterministic policy composition, route choice and runtime scheduling. It owns no candidate rank algorithm, no hard entry/exit timing, no broker mutation and no new LLM decision.
- **Strategist**: strategy framing and existing allowed LLM behavior. It owns no Scanner final ranked selection and no Monitor action intent.
- **Scanner**: deterministic candidate scoring/ranking, selection evidence and soft compatibility/chart-fit context. It does not own hard entry permission or broker side effects.
- **Monitor**: deterministic actionable entry/exit decision and at-most-one intent. It does not mutate broker state or acquire Supervisor authority.
- **Supervisor**: approval/safety authority remains exactly as before; P1.5 may clarify callable boundary/tests but not reimplement approval authority in an Agent adapter.
- **Executor**: sole controlled broker side-effect authority via the established mutation choke point. Safety-critical ordering is exempt from normal façade size reduction.
- **Reporter**: existing LLM report evaluation/generation role; Reporting AI/Markdown/Story backends have one implementation Owner per truth/section/assembly concern and stable public entrypoints.
- **Operator UI/Brief**: read model and presentation; no independent trading authority, and no new decision-making LLM role.

No framework-neutral contract can be accepted if it silently imports the complete graph runtime, mutates shared peer state outside the owned state adapter, or performs hidden production write/real broker operations in isolated tests.

## 4. Required per-symbol owner ledger (all P1.5.1–P1.5.10)

Create a versioned ledger per implementation stage, then consolidate them before P1.5.11. A row is required for each affected public API, real implementation body, graph-node private helper and compatibility/monkeypatch seam.

| Field | Required evidence |
|---|---|
| stage / subsystem / symbol / old location | file, line range and pinned baseline+candidate SHA |
| CLASS | KEEP / MOVE / WRAPPER / DEAD / SAFETY-LOCK |
| RESPONSIBILITY | one domain concept (policy, scoring, formatting, IO, evidence, orchestration, adapter, authority, compatibility) |
| CANONICAL_OWNER | one actual module/class/function that implements the behavior; no second active implementation |
| FACADE_REASON | public API / active dependency / test patching / historical seam / safety lock; NONE if truly removed |
| CONSUMERS | active production + test + CLI + Docker/scheduler + API/UI + docs/search references |
| CONTRACT / IO / AUTHORITY | input/output schema, side effects, allowed LLM role, writes, state mutations |
| DEPS / CYCLES | explicit imports and call-time injection, circular import risk and transitive graph/runtime dependence |
| TEST_PROOF | golden parity, direct core fixture, monkeypatch compatibility, targeted and full suite |
| DISPOSITION | stage-local closure or P1.5.10 waiver with owner, reason, removal proof and next review |

Reject a row with UNKNOWN canonical owner, two active implementers, orphan state mutation, undocumented production consumer, missing behavior parity or missing safety escalation.

Do not game façade LOC via module `__getattr__` magic, wildcard reexports, opaque dependency globals, circular imports, or blanket proxy reassignments. Explicit call-time dependency injection is permitted only for a listed compatibility requirement and should shrink after migration.

## 5. Minimum acceptance by implementation category

### Thin adapter / public façade
Public signatures, import paths and result schemas remain stable. Adapter may assemble typed input, call the component and apply owned state patch; it must not implement LLM retry, Scanner scoring, Monitor trading decision, policy authority, truth precedence, database/broker IO, report formatting or artifact derivation.

### Independently callable components
Strategist, Scanner, Monitor, Commander, Reporter, and authority-constrained Supervisor/Executor entrypoints must be testable through declared contract fixtures without running the entire custom top-level graph. For Executor, a dry mock/denied-order fixture proves its declared authority gate; do not run live broker IO. The exact public callable name follows the relevant stage packet; this addendum does not add new production entrypoints outside approved contracts.

### Contract and state ownership
Every state write has exactly one adapter/owner and a baseline parity fixture. New optional typed fields are allowed only where explicitly approved; do not alter serialized field meaning, precedence, schema versions or artifact locations. A compatibility alias is documented, not an independent second source of truth.

### Evidence, IO and LLM
Evidence provenance/UEF paths have one writer/derivation owner per responsibility. Read/pure policy/IO boundaries are explicit; report truth hierarchy, retries and prompt/LLM count stay exactly equivalent. Mock/test/replay never write production directories or dispatch broker mutations.

### Size and exception policy
Original constitution review guidance is retained: ordinary functions about 10–50 LOC, complex 50–80, orchestration 50–120; modules about 100–300, façade 150–350, orchestrator 200–400; >=500 REVIEW, >=800 normally disallowed, >=1000 targeted for elimination. The more specific reporting/operator/agent targets in each packet remain design targets. Record **exact file-size review** and any unsatisfied target; an explicit active-consumer-backed WRAPPER exception may be deferred to P1.5.10 but cannot be silently reported as target PASS. Executor safety coordinator is the explicit size exception; do not distribute authority to meet metrics.

## 6. Stage-boundary handoff checklist

For each P1.5.1–P1.5.10 batch, the next stage may consume only a versioned, reviewed snapshot with:
1. Baseline and candidate SHA plus accepted P1.2/P1.3 prerequisite status (or clearly marked NOT VERIFIED).
2. Symbol Owner ledger and architectural dependency graph, including façade/owner import-cycle scan.
3. Targeted regression and changed golden fixture parity with exact pass/fail/skip counts.
4. Independent service-call fixture and compatibility seam tests where relevant.
5. Security: no production-write/trading-authority leakage, no new LLM decision roles, no Step5/UEF drift.
6. Test suite accountability: old tests kept or reclassified with an explicit mapping; success temp artifacts cleaned, failure evidence bounded.
7. Canonical current docs, daily patch and UI-linked patch_notes.json / patch_notes.md synchronized.
8. Residual decisions: blocker or accepted carry to P1.5.10, not an untracked TODO.

No stage is declared fully accepted merely because its inner giant functions were copied to other files or a selected pytest subset passed.

## 7. P1.5.11 additional architecture freeze evidence

Keep every existing P1.5.11 Layers A–G, static/contracts, full pytest, Docker mock, UEF frozen-core/cross-day, Step5 authority, independent Claude audit and human approval exactly as designed.

Add required report sections to `docs/refactor/p1_5_freeze_report.md` and the corresponding hashed manifest references:
- **Responsibility conservation**: every audited original responsibility maps to ONE canonical current implementation, and no duplicate active owner.
- **Boundary fitness**: for each Agent/service, declared input/output and standalone fixture, explicit state adaptation, approved external IO/LLM/authority, and absence of cyclic graph dependence.
- **Façade debt**: measured final LOC/functions/dependency adapters, remaining size exceptions with consumer proof, compatibility waiver owner and P1.5.10 disposition.
- **Test conservation**: baseline tests vs candidate unit/integration/regression inventory, migrated-test mapping, no missing historical incident protection, full-suite exact results.
- **Safety exclusion proof**: Executor size exception does not leak mutation; Supervisor/CAS/idempotency/guard precedence/UNKNOWN unchanged; no mock/replay production writes.
- **Decision record**: Architecture PASS/FAIL separate from behavior PASS/FAIL. A safety failure or unidentified canonical owner is NOT a waivable cosmetic finding.

An incomplete owner ledger or architecture failure blocks formal P1.5 freeze even if a subset of pytest passes. The existing P1.5.11 human approval remains mandatory; do not set the tag based only on this design addendum.

## 8. Actual review vs implementation status (do not conflate)

- **DESIGN REVIEWED**: all 11 stages above, against the existing original detailed packets.
- **DESIGN REPLACED**: none. The authoritative constitution, master and original detailed packet versions are retained.
- **DESIGN SUPPLEMENTED**: common ownership/waiver/hand-off/freeze acceptance, and MO7 conditional module creation clarification.
- **REFACTOR IMPLEMENTATION VERIFIED THIS REVIEW**: none; prior R2-A/B/C CI results cited as historical evidence, not rerun by this design-only change.
- **P1.5.2 FINAL ACCEPTANCE**: NOT ESTABLISHED.
- **P1.5.3–P1.5.11 IMPLEMENTATION/FREEZE**: NOT ESTABLISHED.
- **P1.2/P1.3 BASELINE FREEZE**: must be independently checked before any further runtime implementation; not certified by this review.
- **PRODUCTION DEPLOYMENT / MAIN MERGE / BROKER TRADING**: NONE by this review.

## 9. Source map

- Master: `docs/refactor/p1_5_p1_6_master_plan.md`.
- Constitution: `docs/refactor/p1_5_refactor_constitution.md`.
- P1.5.1–2: `docs/refactor/p1_5_reporting_implementation_packet_v1_0.md`; residual P1.5.2 `p1_5_reporting_implementation_packet_v1_1.md`.
- P1.5.3: `p1_5_operator_ui_brief_implementation_packet_v1_0.md`.
- P1.5.4: `p1_5_strategist_implementation_packet_v1_0.md`.
- P1.5.5: `p1_5_scanner_implementation_packet_v1_0.md`.
- P1.5.6: `p1_5_monitor_implementation_packet_v1_0.md`.
- P1.5.7: `p1_5_commander_runtime_implementation_packet_v1_0.md`.
- P1.5.8: `p1_5_runtime_naming_implementation_packet_v1_0.md`.
- P1.5.9: `p1_5_executor_low_risk_implementation_packet_v1_0.md`.
- P1.5.10: `p1_5_compatibility_wrapper_cleanup_implementation_packet_v1_0.md`.
- P1.5.11: `p1_5_full_regression_docker_uef_freeze_implementation_packet_v1_0.md`.

All basename-only paths in this source map reside under `docs/refactor/`. The records are preserved, not superseded for their original detailed scope.
