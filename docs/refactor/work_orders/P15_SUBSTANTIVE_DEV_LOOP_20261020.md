# P1.5 — substantial dual-developer work block and candidate integration gate

**Established 2026-10-20 under operator directive.** This is a **living, executable instruction for sizing and showing work in the existing remote-viewed CLI sessions**, but **not new source-write/branch authorization**. Authority: [D00 §3B](../../ENGINEERING_DELIVERY_POLICY.md), root D01/D02, [Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20), DOC D7 freeze. Historical closed issues do not activate themselves.

## 1. User-required execution character: 60–120-minute-class PER owner

The 60–120 minutes describes an appropriately substantive *engineering work package*, NOT a wall-clock minimum, artificial wait, fake review iterations, or permission to start unapproved work. Tech Lead assembles 2–4 connected implementation outcomes with exact owner and source allowlist **before launch**. First extract a real coherent responsibility cluster with callers, follow it through original-output/ordering contracts, focused hostile tests, peer CLI code review and bounded REWORK if genuinely required. Do not stop the primary developer after a tiny change if the same already-authorized coherent packet has more READY work. If unexpectedly finished early and no READY authorized scope remains, stop with a specific undersized-packet report to GPT; do not invent the next task.

**Interactive output visible via user's remote desktop:** each developer comments in its current primary terminal/chat before/after material steps, labeled `[DEV-A/B][PLAN|EDIT|TEST|PEER_REQUEST|PEER_RESPONSE|REWORK|HANDOFF]`. Preview actual peer questions, reproduce the review findings or genuine `findings=[]`, explicitly decide fix/no-fix, and display new SHA when changing code. Opposite CLI is a **fresh read-only child**, not the other primary developer chat. Stream child progress only if its installed CLI supports it; otherwise announce pending child and present exact result immediately upon completion. No local status observer or source instrumentation.

## 2. First two approved candidates — readback only, NO false release

| Lane | Exact candidate and tests (operator/CLI reports) | Peer review | Current gate |
|---|---|---|---|
| A · Reporter | `ad4eed21d8303d4d8cb99f4097b4812cf2522f97` (from `7d647493`); 139 normal, 25 -O focused PASS | fresh Codex REVIEW 1 REWORK (early `exists()`), code fix and new SHA, REVIEW 2 PASS; reviewer pytest NOT_RUN | **PEER_PASS_WITH_INTEGRATION_BLOCKER** — old guard failures |
| B · Operator UI | `c0c3f808967dc921a956d01a879fe489674cad71`; 100 normal, 98 -O focused PASS | fresh Claude initial PASS with two-source coverage gap → supplemental PASS; zero runtime-code REWORK | **PEER_PASS / INTEGRATION_PENDING** |
| Integration | `integration/p1.5` prior HEAD `4b0c3e0b5f8f24fa3c10d9082b85fab63f15c4c3` | Composed check absent | **NOT_INTEGRATED** |

These counts and local peer exits are **developer-reported**; their original Windows CLI receipts are not remotely replayed by GPT. Candidate Git commits and paths can be verified through connected GitHub. The two candidates each touch the paired UI notes. Serially reconcile their 320th entries against **latest** integration HEAD; never replace 319 historical entries with a branch-specific copy.

## 3. Immediate Tech Lead gate — original contracts before selection

A needs deliberate ownership adjudication for these separate historical contracts:

1. `tests/test_work_reporter_seed_migration.py::test_target_tree_discipline_and_no_forbidden_surface`: original strict Reporter read_models directory inventory does not include new `analysis_report_projection.py`; scope identity and old file hashes remain protected. Inspect shared script/checker's own Reporter whitelist and all consuming gates, not only the failing assertion.
2. `tests/test_shared_reporter_facade_guard.py::test_all_registered_facades_restore_to_base`: previous pinned facade AST/source-restoration contract includes `libs/reporting/reporter_analysis.py` in its frozen baseline. Changing its callable body invalidates that oracle. A new facade-to-owner migration contract must prove signature/import/use-time helper injection, return bytes, effect order, negative mutations, and all unmodified frozen facades still match pinned BASE.
3. `tests/test_shared_role_contracts.py` locally reports old missing Git object errors even on BASE: separately distinguish environment history incompleteness from candidate regressions. Hosted CI must fetch all required history; never waive, silently xfail/skip, change expected counts to make green, or mutate pinned historical fixture/ledger.

**Contract-changing tests/allowlists are not within either Batch01 developer's original five-file allowlist.** Approval of D7 freeze and the two developer source candidates did NOT automatically authorize a guard rewrite. GPT must propose a bounded exact-file versioned contract change and obtain source-scope authorization; then run BASE-good/candidate-good and truly hostile mutant-bad, normal and -O, separate independent review. Until that happens, A is not integration-ready.

**B's selected source may be promoted separately** only by GPT checking exact changed paths, serialized notes and required checks on the **new composed integration SHA**. Do not wait on A forever or falsely promote A. No `main`, Docker, live Broker/LLM/orders.

## 4. Next substantial work blocks — design slots only, NOT yet authorized for source writes

**A next engineering packet** should be a *single coherent Reporter ownership/consumer transaction*, with 2–4 linked outcomes: resolve existing analysis read-model integration contract, enumerate specific real consumer/guard behavior affected by facade change, cover BASE-byte/effect-order parity and negative mutations, reduce original function responsibility where proved. Assign exact allowable paths, real acceptance tests and branch/base **after** freeze-guard approval. No duplicate owner, cosmetic rename, UEF, broker or memory-write relocation.

**B next engineering packet** should be a *single coherent Operator UI read-only data-access transaction*, with linked adapter projection, callsite/ABI behavior, stale/live reconciliation parity, negative tests and independent peer review (not a single helper extraction). Choose real candidate paths with no A conflict; pin base and allowlist after actual integration HEAD is reviewed. Existing Monitor 11 owner modules and effectful Commander/Executor/Step5C gates stay frozen.

**Activation conditions for each future packet:** Issue #20 states `AUTHORIZED` explicitly and includes **BASE_SHA, owner, allowed source and test paths, numbered concrete implementation outcomes and integration tests**. Existing primary developers can execute each separately READY step within the same already approved packet without a new approval *per micro-step*. New branch, additional workspace, cross-owner source, frozen guard contract mutation or separate 1–2-hour code work remains operator-scoped. No automatic background CLI launches.

## 5. Phase gates — candidate PASS is not final PASS

`IMPLEMENTING → SELF_TEST → PEER_REVIEW → REWORK if findings → PEER_PASS → CONTRACT_GATE → INTEGRATION_READY → SELECTIVE_PICK → COMPOSED_SHA_CI → INTEGRATED`.
If blocked at CONTRACT_GATE, keep A and B statuses separate. Report only actual commands/exit and list unperformed full pytest, 24 real-data SKIPs, frozen production JSON/HTML, UI build/visual, Docker. All safety-locked paths remain unaffected, even when the human expects longer development sessions.
