# Agentra HYBRID-7 V3 — TARGET TREE FROZEN

**Authority:** GPT architecture + user explicit freeze/implementation instruction, 2026-10-16.
**HISTORICAL EXECUTION CONTEXT ONLY:** The baseline branch and V1-052 rollout below document the 2026-10-16 design-freeze event, **not** current branches or startup work. The seven-role target and SAFETY_LOCK guarantees remain frozen. All current execution sequencing, owner roles and branch assignments come ONLY from [D00](../../ENGINEERING_DELIVERY_POLICY.md) and [#20](https://github.com/hbombheart1230-dotcom/agentra/issues/20); #16–#19 and V1-052 are completed historical evidence.

**Baseline (historical):** `e9a9a854c2696889da8af1f6f7ec02e936f7d924`; work branch `integration/p15-t4-pr5-convergence-20261015`; `main` remains untouched.
**State:** `USER_TARGET_FROZEN` / `MIGRATION_IN_PROGRESS` / **not** P1.5 FINAL_ACCEPTED.
**Design policy:** DO NOT propose V4, re-draw from scratch, or redo the completed 2,226-file AST inventory. The remaining work is implementation and differential safety verification.

## Non-negotiable visual acceptance

The canonical public role surface must eventually show **seven peers at one depth**, in this order:
`libs/agents/{commander,strategist,scanner,monitor,reporter,supervisor,executor}/`.
These are distinct PUBLIC ROLE ENTRY SURFACES, not permission to duplicate runtime engines. Do not create empty decorative placeholders. Source modules move to a role only when behavior has one real owner and real consumers.

Target top level keeps `apps/`, `graphs/`, `libs/`, `scripts/`, `tests/`, `docs/`, `deploy/`, `config/`, and `data/`. Under `libs/`, group `agents/`, `contracts/`, `runtime/`, `market/`, `market_data/`, `strategies/`, `research/`, `reporting/`, `kiwoom/`, `risk/`, `approval/`, `supervisor/`, `execution/`, `storage/`, and `agent/` (legacy) by ownership. Existing siblings with proven distinct responsibility stay separate.

Aesthetics are an ACCEPTANCE CRITERION: a developer can find role, owner and stable import in one navigation; sibling naming and depth are predictable; avoid `misc/`, `common2/`, `owner_XXX/`, `*_r3_parts/` in *new canonical public paths*; no second ranking, approval, order or truth authority; no package created merely to mirror a diagram.

## Authority is frozen

`graphs/trading_graph.py` is an M17 graph-shaped test baseline; `graphs/nodes/executor_node.py` is not the real broker executor. The operational route via `graphs/commander_runtime.py` and `graphs/nodes/execute_from_packet.py`, and `libs/risk/`, `libs/approval/`, `libs/supervisor/`, `libs/execution/`, `libs/kiwoom/`, Step5C CAS, UNKNOWN quarantine, UEF, operational Q10/Q12 and persistent write/LLM semantics are SAFETY_LOCK. Do not rehome these effects for symmetry. No real Broker, live LLM, trading, Docker/scheduler restart, production write, or `main` merge.

## Verified existing evidence — reuse, do not repeat

- `docs/refactor/architecture/consumer_inventory_findings_20261015.md`: baseline `b05b36a`, 2,226 parsed Python files, 4,486 static edges, 162 literal dynamic edges, 58 unknown dynamic sites.
- `docs/refactor/p1_5_third_pass_t3_ownership_matrix.md`: Owner/facade/contract classifications.
- `docs/refactor/architecture/{current_overview.md,current_modules.md,architecture_gap_matrix.md,dependency_scope.md}`.
- Source delta from inventory baseline to `e9a9a854c2696889da8af1f6f7ec02e936f7d924`: 7 commits and 44 changed paths (not 44 runtime files).
- Historical V3 detailed design and 57-row path ledger are retained in the GPT-provided changed-files-only package; this in-repo frozen specification is authoritative for implementation.
- The consumer inventory is incomplete for dynamic external/scheduler/monkeypatch behavior. For **each selected physical move only**, verify those exact consumers and ABIs before proceeding.

## Historical delivery sequence (2026-10-16; not a current task)

> **NON-EXECUTABLE HISTORY:** V1-052 Scanner pilot, subsequent step order and the fixed Claude→Codex workflow below record the original implementation sequence. These are **not** pending work orders; for new tasks use D00 + latest #20 only.


1. **V1 first REAL file movement:** the one-module Scanner pilot in `P15-TREE-MIGRATION-V1-052.md`, with compatibility, targeted safety and exact parity proof. No global scan or further target-tree debate.
2. Next migrate coherent verified pure role functions by responsibility, in one active integration branch only. Each group: source-to-target ledger, wrappers, role-callability, parity, CI, write isolation.
3. Reporter versus Research/Evaluation physical moves only after coupled consumers and artifact bytes are proven; avoid wholesale `libs/reporting/evaluation/` migration.
4. Scanner/Strategist/Monitor/Commander main surfaces then gradual compatibility debt removal; independent Supervisor/Executor authority changes remain out of scope.
5. Wave D/P1.5 freeze is separate and not implied by successful folder moves.

**Workflow (historical 2026-10-16):** GPT fixes target/scope → Claude implements on the existing branch in an isolated clone → Codex independent pinned-SHA audit → GPT/user acceptance. Approval of the V3 visual target is not blanket approval of high-risk code moves.

**Artifacts:** every meaningful commit updates BOTH UI patch-note JSON and MD plus daily evidence. No ZIP packaging in CI; user delivery bundles are **changed-files-only ZIP** outside CI, excluding secrets and production data.
