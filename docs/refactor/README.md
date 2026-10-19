# Agentra P1.5/P1.6 — canonical document entry

**CURRENT NAVIGATION · 2026-10-19 · DOC_FREEZE PENDING.** This is a navigation document, **not a task that can launch itself**. Latest user decision: complete ALL documentation convergence and approval before creating new Codex/Claude development branches or resuming P1.5 code refactoring.

## Single authority chain

1. Non-negotiable trading safety: [AGENT_RULES.md](../ground_rules/AGENT_RULES.md).
2. **D00** common engineering rules: [ENGINEERING_DELIVERY_POLICY.md](../ENGINEERING_DELIVERY_POLICY.md).
3. **D01** Codex [AGENTS.md](../../AGENTS.md) / **D02** Claude [CLAUDE.md](../../CLAUDE.md) — CLI startup entrypoints, not alternate D-number filenames.
4. The sole live work and integration tracker: [GitHub #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20) with real GitHub SHA/CI.
5. [CURRENT.md](work_orders/CURRENT.md) is a short pointer, not a second live work-order queue. Old Issues #16–#19 are closed source/audit evidence, not fresh authorization.

## Canonical goals, design and historical evidence

| Question | Use this **one** source |
|---|---|
| Frozen target structure | [HYBRID-7 V3 TREE_V3_FROZEN](architecture/TREE_V3_FROZEN.md). Never create a cosmetically new V4. |
| P1.5.0–11 / P1.6–P8 program order | [P1.5/P1.6 master plan](p1_5_p1_6_master_plan.md). This plan is NOT live progress. |
| Architecture responsibilities | [P1.5 constitution](p1_5_refactor_constitution.md) and [stage alignment](p1_5_1_to_11_responsibility_alignment_v1_1.md). |
| Previous architecture state | [Tech Lead snapshot](architecture/P15_TECHLEAD_MASTER_20261018.md) and [root-to-leaf](architecture/P15_ROOT_TO_LEAF_REALITY_AND_CLEANUP_20261018.md), pinned at prior source `5cb90b39`. NOT today's HEAD. |
| P1.5 work-order status | [work_orders/README](work_orders/README.md) + [CURRENT](work_orders/CURRENT.md). All dated orders are inert unless newly issued. |
| Original 339-file governance registry | [DOC_REGISTRY.csv](DOC_REGISTRY.csv). Path classification only; content/link review is not yet complete. |
| Retired Reporter/Monitor work projects | [work_projects/README](work_projects/README.md), **historical / do not restart**. |
| P1.6 orchestration comparison | [P1.6 master](p1_6/MASTER_PLAN.md), future design only until P1.5 freeze. |

The older `architecture/target_architecture.drawio` is PROPOSAL_ONLY, not the frozen target. Frozen stage-specific acceptance, goldens and historical refs stay intact.

## 7-role structure versus actual operational authority

| Role | libs/agents/<role>/ code exists at source snapshot? | Actual authority and final acceptance |
|---|---|---|
| Commander | NO | Real `graphs/commander_runtime.py`; public callable contract **NOT_VERIFIED** |
| Strategist | YES | Node and runtime implementation, PARTIAL; full callable contract **NOT_VERIFIED** |
| Scanner | YES | Rank/Top-1 unique authority, PARTIAL; full callable contract **NOT_VERIFIED** |
| Monitor | YES | OrderIntent ONLY, PARTIAL; full callable contract **NOT_VERIFIED** |
| Reporter | YES | Reporting and evidence, PARTIAL; full callable contract **NOT_VERIFIED** |
| Supervisor | NO | Existing risk/approval SAFETY_LOCK; public callable contract **NOT_VERIFIED** |
| Executor | NO | Actual order path `execute_from_packet.py` SAFETY_LOCK; public callable contract **NOT_VERIFIED** |

Absent public role directory does NOT mean existing operational role is absent. Never duplicate order, approval, rank, Step5C or UEF authority for visual symmetry. Graph stub is not an operational broker executor.

## P1.5 stages — verified scope, NOT invented stage completion

| Stage | Evidence-aware status | Frozen detailed source |
|---|---|---|
| P1.5.0 | Baseline exists in older history; overall final verification NOT_DONE | [master plan](p1_5_p1_6_master_plan.md) |
| P1.5.1–2 Reporter | Source extraction exists; stage-wide acceptance NOT_VERIFIED | [Reporter v1.2](p1_5_reporting_implementation_packet_v1_2.md) |
| P1.5.3 Operator UI | `a50d6e47` scoped UI delta INTEGRATED / AUDITED; full stage NOT_VERIFIED | [Operator UI packet](p1_5_operator_ui_brief_implementation_packet_v1_0.md) |
| P1.5.4 Strategist | `a50d6e47` scoped parsing INTEGRATED / AUDITED; full stage NOT_VERIFIED | [Strategist packet](p1_5_strategist_implementation_packet_v1_0.md) |
| P1.5.5 Scanner | Physical moves documented; stage-wide acceptance NOT_VERIFIED | [Scanner packet](p1_5_scanner_implementation_packet_v1_0.md) |
| P1.5.6 Monitor | Physical moves documented; stage-wide acceptance NOT_VERIFIED | [Monitor packet](p1_5_monitor_implementation_packet_v1_0.md) |
| P1.5.7 Commander | Large module decomposition exists; full contract acceptance NOT_VERIFIED | [Commander packet](p1_5_commander_runtime_implementation_packet_v1_0.md) |
| P1.5.8 Naming | Historical work exists, stage acceptance NOT_VERIFIED | [Naming packet](p1_5_runtime_naming_implementation_packet_v1_0.md) |
| P1.5.9 Executor | SAFETY_LOCK; stage acceptance NOT_VERIFIED | [Executor packet](p1_5_executor_low_risk_implementation_packet_v1_0.md) |
| P1.5.10 Compatibility | Wrappers retained where needed; stage acceptance NOT_VERIFIED | [Compatibility packet](p1_5_compatibility_wrapper_cleanup_implementation_packet_v1_0.md) |
| P1.5.11 Freeze | **HOLD** full repo pytest, 24 real-data SKIPs, production JSON/HTML byte parity, UI build/visual, Docker lifecycle and final human acceptance | [Freeze packet](p1_5_full_regression_docker_uef_freeze_implementation_packet_v1_0.md) |

**Completed slice, do not redo:** exact source `a50d6e4780ddccd810fb0708e756e1bf63d8ede0`, approved 19-path Strategist/Operator UI selection, #18/#19 independent audit PASS, [CI 6/6](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39180253182). The newer docs commits do not inherit an automatic new CI PASS. User-provided analysis of that source snapshot observed six source groups 53,695→18,052 LOC (66.4% reduction), 7 role directories 4/7 and tracked files 2,610 main → 3,940 integration. These are historical snapshot metrics, NOT moving HEAD metrics.

## Documentation quarantine, no speculative deletion

Every **original** path under `docs/refactor/` is listed in [DOC_REGISTRY.csv](DOC_REGISTRY.csv) with its exact blob, classification, passive activation rule and pending reference checks. All original 339 files are preserved at their existing paths. Past `work_projects/`, `work_orders/P15-*.md`, `archive/` and `evidence/` cannot launch work; historical PASS/REWORK belongs to its SHA only. The old 2026-10-07 inventory is [here](documentation_inventory.md). Physical moves await inbound Markdown/CI/Python/patchnote source proof.

**DOC_FREEZE_PENDING:** exhaustive per-file content checks, cross-document inbound links, independent new-session review and user acceptance have not been performed. Until then NO P1.5 development restart or main promotion.
