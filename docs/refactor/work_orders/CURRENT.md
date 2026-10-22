# Agentra P1.5 — CURRENT: ONE ACTIVE EXECUTION POINTER

**Active Product Owner decision (2026-10-22 KST): FULL_REPOSITORY_ROOT_TO_LEAF.** This file is the **single current work pointer**, not an additional redesign or a standalone grant to alter safety. Read the actual remote HEAD and exact approved source packet before any change. User's newest explicit approval and non-bypassable trading safety always prevail.

## 1. Fixed authority and full scope

- **Technical architecture FROZEN:** `docs/refactor/architecture/TREE_V3_FROZEN.md`, `docs/refactor/p1_5_refactor_constitution.md`, `docs/refactor/p1_5_p1_6_master_plan.md`, `docs/refactor/p1_5_1_to_11_responsibility_alignment_v1_1.md`. Reuse existing stage implementation packets; no V4, T00–T09 alternate implementation program, new architecture work order or AST reinventory.
- **Full-repository scope:** `.github/`, `apps/`, `config/`, `data/`, `deploy/`, `docs/`, `graphs/`, `libs/` **all 26 first-level packages**, `scripts/`, `tests/`, and tracked root controls. `libs/agents/` (seven real peer PUBLIC ROLE interfaces) is only one part; do not shrink P1.5 to `agents/` or move all runtime/research/reporting into it.
- **Existing entire-tree inventories; do not recreate:** `docs/refactor/architecture/P15_ROOT_TO_LEAF_REALITY_AND_CLEANUP_20261018.md`, `P15_ALL_LIBS_OWNERS_20261018.md`, `P15_TREE_ALL_PATHS_PINNED_20261018.txt`, `P15_ALL_FILES_OWNERSHIP_CANDIDATES_20261018.csv`. These records are pinned at historical `5cb90b39`; recheck only changed target paths at current HEAD. Per-path OWNER/KEEP/MOVE/WRAPPER/SAFETY_LOCK requires actual consumer and behavior evidence; no blanket folder deletion or move.
- **Priority:** existing validated unintegrated source → coherent real ownership/folder structure and compatibility across ALL roots → largest **safe eligible** multi-responsibility files/families → smaller residual naming/test/docs cleanup. Avoid isolated helper churn, new meta-validators, paper-only passes. Keep UEF, Step5C, Broker/Executor/Supervisor authority, production writers and frozen evidence intact.
- **Historical documents and #20 comments are evidence, NOT extra parallel task queues.** Specifically the 2026-10-20 BATCH03/04/05, 2026-10-22 T00–T09 plan staged only on PR #31 and old `CURRENT` headings are **INACTIVE AS FUTURE DISPATCH**. The exact existing P1.5.0–11 packets below govern implementation. Do not erase historical evidence or old Git commits.

## 2. Branch and integration lock

| Ref / owner | Rule |
|---|---|
| `main` / Product Owner | Release baseline: do not merge, push, deploy or enable real trades without separate explicit approval. |
| `integration/p1.5` / GPT | **Sole integration line.** Select exact reviewed code/test blobs, reconcile both UI-linked patch-note files; final INTEGRATED only on the new integration SHA with all required hosted CI PASS. |
| `work/p15-a-reporter-pure-20261021` / Claude DEV-A | Sole continuing A implementation branch; Reporter / Strategist / Scanner and assigned tests only. |
| `work/p15-b-operator-structure-20261022` / Codex DEV-B | Sole continuing B implementation branch; Monitor / Commander / Operator UI and assigned tests only. |

**Final live branch target: exactly 4 heads** including `main`. As observed before this docs change: 6 heads; draft PR #31 `stage/p15-large-first-a-composition-20261022` and obsolete B UI head `work/p15-b-operator-live-overview-20261020` are retirement candidates **only after independent exact-SHA provenance/consumer/worktree/safety checks**. Preserve previously verified immutable archive tags; do not blindly merge the draft PR, whose extra T00–T09 docs do not grant execution authority.

**Immediate ordered gate:** (1) commit THIS documentation lock on integration without altering runtime; (2) Codex DEV-B is sole authorized existing-local-CLI writer for one-time cleanup of the *obsolete B UI remote ref only*, after prior `WORKTREE_RELEASED` receipt and fresh SHA/tag/worktree verification; if blocked, leave it intact without polling; (3) GPT selectively accepts current A/B + distinct PR31 source and notes, with real normal/`python -O`, peer source verdict, historical frozen checks and CI on exact composed SHA; (4) retire PR31 staging ref **only once** preserved source/integration CI proven. This document does not start CLI processes or authorize Codex to integrate unreviewed source. The latest explicit PO instruction governs any changed owner.

**Snapshot for orientation ONLY (not future SHA authorization):** main `2f95bba4`; previously green integration `51bb7130` (hosted six required CI PASS on that SHA only); A `a21401db`; B had advanced beyond `21fe1366` to `a3d60e37`; PR31 `8b98fe74` DRAFT; old B UI `70843da4`. Every action MUST re-fetch actual origin refs, approved diff/peer receipt and exact CI; this docs-only commit does **not** inherit prior hosted CI.

## 3. Existing P1.5.0–11 delivery packets — no new phases

| Existing stage | Exact inherited implementation scope / roots | Closure rule |
|---|---|---|
| P1.5.0 | Repo baseline, root test/CI controls, artifact hygiene | Historical baseline exists; final acceptance rechecked on actual HEAD. |
| P1.5.1–2 | Reporter R2 / `libs/reporting/`, report/evaluation/read models and corresponding tests | Existing source first; remaining large responsibility debt assessed, no repeating already accepted slices. |
| P1.5.3 O1–O6 | `apps/operator_ui/`, Brief/read models + linked Reporter visibility/period summary | Existing B source reviewed and selectively integrated before duplicating modules. |
| P1.5.4 S1–S5 | `graphs/nodes/strategist_node.py`, `libs/runtime/strategist/`, role contracts/adapter, LLM parity | Claude A, exact original Strategist packet and owner proof. |
| P1.5.5 SC1–SC7 | Scanner node, runtime/role/strategies candidate ranking and evidence | Claude A, exact rank/tie-break and Monitor soft/hard boundary parity. |
| P1.5.6 MO1–MO8 | Monitor node, `libs/runtime/monitor*`, intraday signal engine, OrderIntent only | Codex B, no Broker execution; owner/State parity. |
| P1.5.7 C1–C10 | `graphs/commander_runtime.py`, `libs/runtime/commander/`, entrypoints and orchestration | Codex B, stable runtime order, deterministic routing. |
| P1.5.8 N1–N7 | **Full repo** active runtime naming, `scripts/`, env/state/config, deploy launchers, current docs | Historical records untouched; migration with aliases and consumer proof. |
| P1.5.9 EX1–EX6 | Executor safe observability/artifact/pure view only | SAFETY_LOCK; approval/order guards and Broker mutation path remain unchanged without separate PO approval. |
| P1.5.10 CW1–CW7 | **Full repo** compatibility: legacy `libs/agent`, API/UI/import/CLI/script/deploy wrappers and tests | Zero-consumer evidence before removal; KEEP safe/historical facades. |
| P1.5.11 FZ1–FZ9 | **Full repo** regression/UEF/Step5C/Docker/Windows+Linux CI/UI/build/documentation/security/architecture freeze | exact new integration SHA, full required evidence, independent verification, Product Owner freeze decision. |

**Status semantics:** per packet item `DONE / NOT_DONE / BLOCKED` requires the actual code SHA and source/peer evidence; historical slice PASS does NOT certify entire stage. `SELF_PASS / PEER_DEFERRED` on a credit/time/permission-blocked opposite CLI means code may continue separately approved work but **must not integrate** until genuine independent PASS or separately PO-approved equivalent. A peer CLI must be new, independent, read-only, exact-SHA and invoked by the primary developer; record real exit and verdict, and normal/`python -O` parity. Never waive old gates, skip/xfail regressions, or treat source push as release.

## 4. Rules for new chats and handoffs

1. Read THIS pointer first, then exact real `integration`, A/B refs, PR31 and saved reviewed SHA receipts; check latest explicit PO approval and safety lock.
2. Use the linked frozen architecture and **existing** P1.5 per-stage implementation packet only for the first incomplete authorized item; parallel A/B files must be disjoint.
3. Before proposing any coding task, give a five-field checkpoint: **current stage / A+B SHAs / integration SHA / actual CI & peer verdict / blocker & next accepted action**. No new planning documents, new branch, or extra Issue comment to compensate for an unchanged state.
4. Commit only the approved source/test/docs paths; synchronize `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and `patch_notes.md` with unique count and all A/B histories. User never manually forwards developer review receipts.
5. Temporary CLI credit limits change available executor, NOT ownership/security/proof: use approved independent work and `PEER_DEFERRED`, no polling/forced permissions, no invented completion.

**Historical CURRENT as of pre-lock integration:** `integration/p1.5@51bb7130b2ba627be50800fa89c6108dd1a5018c:docs/refactor/work_orders/CURRENT.md`, plus the immutable dated `work_orders/` packets, Issue #20 and prior commit trees. The previous 18K-character CURRENT work logs remain in Git history; their dated assignments are not currently executable.
