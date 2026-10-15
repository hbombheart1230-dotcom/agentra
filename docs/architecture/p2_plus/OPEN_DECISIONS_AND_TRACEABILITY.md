# P2–P8 Design Decisions, Open Risks & Source Traceability

Status: ARCHITECTURE DRAFT; open matters require explicit decisions on accepted future baseline. Nothing here is automatically adopted by running code.

## A. Decision ledger (do not fabricate implementation or approval)

| ID | Decision | Recommendation now | Owner/gate |
|---|---|---|---|
| ARCH-001 | P1.6 graph engine | KEEP_CUSTOM/ADOPT_LANGGRAPH/ADOPT_PYDANTIC_GRAPH/DEFER **undecided** | P1.5.11 accepted, then P1.6 tests + ADR |
| ARCH-002 | P2 program-registry authority | One research ProgramEntry catalog; Q100-1 shares read view, no second authority | after P1.6 freeze |
| ARCH-003 | P2 source clock | Explicit captured/observed/as_of and market calendars incl. BTC/JPY | P2 input schema acceptance |
| ARCH-004 | Strategy policy promotion | Human-approved separate live policy change, no auto-promotion | P2/P6 safety gates |
| ARCH-005 | Step5D broker truth semantics | Read-first, UNKNOWN held, no late-order replay | P3 independent safety audit |
| ARCH-006 | Step5E recovery permissions | Operator role + CAS/version + second reviewer where configured | P3 audited implementation |
| ARCH-007 | Supervisor "modify" mismatch | DO NOT ASSUME implemented; separate ADR needed | real Supervisor API audit |
| ARCH-008 | Q100 authoritative source | UEF-7/8/9 only for canonical; Q100 derived read-only | P4 canonical checks |
| ARCH-009 | Memory storage | Index/store undecided; Obsidian is only export/view | P5 contract+privacy evaluation |
| ARCH-010 | P6 self-improvement ceiling | Level 4–5 only; Level 6/7 out of scope | P6 human review gate |
| ARCH-011 | P8 primary paper question | Decide after independent data feasibility / protocol review | P8 pre-registration |
| ARCH-012 | Older design branch merge policy | Approved design deltas only; no importing old P1.5 WIP ancestry | after each phase freeze |
| ARCH-013 | P7 freeze evidence retention | Immutable digest/source/candidate; bounded temp artifacts | P7 test/ops acceptance |

## B. Material architecture risks

| Risk | Likelihood before freeze | Mitigation |
|---|---|---|
| File paths / Agent contracts change in P1.5/P1.6 | HIGH | Do not lock P2 module names; post-freeze source/consumer/ABI audit |
| P1.6 engine choice changes state ownership and retries | MEDIUM–HIGH | Framework-neutral P2 ContextFrame; no new graph-specific DTO or authority |
| Double registries Q100/P2 | HIGH if uncoordinated | P2 owns program identity, Q100-1 is its research read model |
| Extra evaluation metrics conflict with UEF | HIGH consequence | Q100 references VALID UEF rows, never recomputes or upgrades status |
| UNKNOWN broker replay in P3 | CRITICAL consequence | Step5D read-first, Step5E reviewed CAS transitions, no implicit resubmit |
| Q12 delayed captures / hindsight | HIGH false-positive risk | frozen as_of/session, missingness as first-class, no retro-fill |
| Small N and multiple comparisons in Q-programs | HIGH | OOS/negative controls, independence accounting, research status not live edge |
| Knowledge poisoning/expired memory | MEDIUM–HIGH | provenance, review, TTL, supersession, empty memory fallback |
| Per-phase branch schema conflict | HIGH if blindly merged | ancestry review, patch-note reconciliation, no automatic force push |
| Test artifact growth | HIGH if unbounded | isolated per-run temp roots, auto clean pass, bounded failures |

## C. Precedence and sources (repo paths and snapshot)

**Actual base of this architecture branch:** `main@2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb` (2026-10-12 branching). Main currently contains historical stable architecture/evaluation/Step5C documents. **Moving source:** `refactor/p1.5` latest inspected when planning, plus the P1.6 design branch; neither is frozen here.

| Source | What it supports | Do not infer |
|---|---|---|
| `refactor/p1.5:docs/refactor/p1_5_p1_6_master_plan.md` | P1.5→P1.6→P2→P3→P4→P5→P6→P7→P8 sequence; Q10/Q12/JPY and safety relationships | that P1.5 or P1.6 already accepted |
| `design/p1.6-orchestration:docs/refactor/p1_6/*` | candidate engine, exact (unfrozen) future code blueprint | frozen P1.5 ABI or LangGraph adoption |
| `docs/architecture/architecture_v2.md` | seven-role reclassification, 6 layers, memory, Reporter lifecycle, modify API gap | an implemented Experience Vault or memory-learning pipeline |
| `docs/research/q100_research_and_learning_roadmap.md` | Q100-1 through 6, four memory tiers, Levels 1–7/4–5 target | an actual Q100 registry or automatic tuning |
| `docs/research/research_portfolio_freeze_2026-09-16.md` | exact as-of-2026-09-16 research KEEP/WATCH/controls and EDGE_CONFIRMED=0 | current market alpha or live promotion |
| `docs/research/uef9_formal_evaluation_authority_freeze.md` | VALID/exception, UEF-7/8/9 binding, not UEF-10 | extra confidence/partial validity, current day counts |
| `docs/research/uef_freeze_manifest.md` | immutable UEF hash authority, read-only verifier | permission to regenerate frozen hashes |
| `docs/development/step5c_execution_owner.md` | Step5B/C at-most-once/UNKNOWN/CAS, Step5D/5E reserved work | Step5D/E already safe to run or implicit auto retry |
| `docs/en/12_roadmap.md` | earlier milestone history and general evaluation/no premature learning principles | that its dated "in progress" claims remain latest truth |

**Conflict handling:** `docs/architecture/architecture_v2.md` requires Step6 safety acceptance before operational V2 activation, consistent with P3 before P4–P6. P2 source inventory/context planning **precedes** P3; it must stay research/adapter/read-only unless separately gated. The older Q100 design mentions UEF-3/4 future dependencies; current UEF-9 freeze is later evidence, but missing per-program adapters and actual binding validity are still case-by-case, not automatically solved.

## D. Source-to-workstream trace

| Workstream | Main input | Main output | Hard dependency |
|---|---|---|---|
| P2 | Q-series research + market captures | program & timed-context registry; no promotion | P1.5/P1.6 frozen ABI |
| P3 | Step5B/C intent/broker evidence | reconciliation and operator recovery safety | existing execution ownership freeze |
| P4 | accepted P2 catalog, UEF-9 canonical truth | Q100 evidence views + Reporter attribution | Step6 + valid UEF binding |
| P5 | P4 attribution + source record refs | reviewed Experience memory + retrieval | provenance and privacy |
| P6 | P5 lessons + P4 OOS controls | reviewed research status suggestions | Level <=5 and no live policy mutation |
| P7 | P2–6 audited artifacts | accepted V2 freeze manifest/tag | full integration gates |
| P8 | P7 frozen stack + approved dataset | controlled experimental results/paper | time split, negative control, reproducibility |

## E. Short handoff checklist to future architect/implementer

1. Start from this `README.md` and the **actual latest accepted GitHub SHA** (not historical ChatGPT text).
2. Identify just one workstream and its frozen predecessor, source contracts and open decision IDs.
3. Reinspect affected current files/callers/tests; classify KEEP/ADD/MODIFY/SAFETY_LOCKED based on **actual** code.
4. Generate a separate implementation-grade plan on an authorized active phase branch, preserving historical docs and UI patch notes.
5. Claude implements; Codex independently audits the pinned delta; GPT + user accept or send back.
6. On each acceptance, reconcile safely to main without importing stale design branch ancestors; register next freeze and refresh dependent architecture.

No task in this architecture branch is executable production work.
