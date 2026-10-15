# Agentra P2–P8 — Architecture-First Program

**STATUS: ARCHITECTURE BLUEPRINT / NOT IMPLEMENTED / NOT MERGE-APPROVED**  
**Date:** 2026-10-12 | **Branch:** `design/p2plus-architecture` | **Base:** `main@2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb`

## Purpose

Design **stable boundaries, goals, contracts, dependencies and evidence gates** for P2–P8 while the P1.5 major refactor is in flight and P1.6's graph-engine decision is not final. Do **not** freeze future file locations, new Python function signatures, exact module names or runtime framework. Implementation packets are created **only after** the predecessor freeze + new code audit.

The four **managed program branches**:
1. `main` — accepted/released baseline.
2. `refactor/p1.5` — P1.5 implementation & freeze.
3. `design/p1.6-orchestration` — P1.6 design (candidate engines, NOT a live cutover).
4. `design/p2plus-architecture` — this P2–P8 architecture-only track.

This counts **managed branches**, not a claim that arbitrary local/temp Git branches or worktrees do not exist. The existing P1.5 active-work-order authority in `docs/refactor/work_orders/CURRENT.md` is unaffected.

## Read order / deliverables

| Document | Authority and content |
|---|---|
| [00_SYSTEM_ARCHITECTURE.md](00_SYSTEM_ARCHITECTURE.md) | 7 roles, architecture layers, truth vs policy/data/memory, end-to-end flows |
| [01_DEPENDENCIES_AND_BRANCH_GOVERNANCE.md](01_DEPENDENCIES_AND_BRANCH_GOVERNANCE.md) | 4-branch lifecycle, freeze/merge/reconcile, source drift and cross-phase gates |
| [02_CONTRACTS_AND_DATA_LINEAGE.md](02_CONTRACTS_AND_DATA_LINEAGE.md) | framework-independent concepts, immutable evidence provenance, statuses and temporal correctness |
| [P2_STRATEGY_PROGRAM_INTEGRATION.md](P2_STRATEGY_PROGRAM_INTEGRATION.md) | strategy registry and research-to-runtime isolation, Q10/Q12/JPY/global context |
| [P3_EXECUTION_SAFETY.md](P3_EXECUTION_SAFETY.md) | Step5D broker truth → Step5E controlled recovery → Step6 safety freeze |
| [P4_Q100_REPORTER_V2.md](P4_Q100_REPORTER_V2.md) | Q100-1/2/3 and structured Reporter attribution without parallel UEF authority |
| [P5_EVIDENCE_MEMORY.md](P5_EVIDENCE_MEMORY.md) | Q100-4/5, Experience/Knowledge vault and advisory retrieval |
| [P6_SELF_IMPROVEMENT.md](P6_SELF_IMPROVEMENT.md) | Q100-6 bounded Level 1–5 improvement, Level 6–7 prohibited |
| [P7_V2_FREEZE.md](P7_V2_FREEZE.md) | V2 system acceptance, operators, Docker, audit, rollback |
| [P8_PAPER_RESEARCH.md](P8_PAPER_RESEARCH.md) | experiment protocol, controls, ablations, reproducibility; final claims post-freeze |
| [OPEN_DECISIONS_AND_TRACEABILITY.md](OPEN_DECISIONS_AND_TRACEABILITY.md) | unresolved ADRs, contradictions, evidence chain, architectural source index |

## Architecture vs implementation: mandatory separation

```text
NOW: P2–P8 requirements + component ownership + conceptual DTOs + guards + tests + dependency gates
     (docs only; no Python/config/schema migration, no orders, no new model calls)
AFTER P1.5.11 formal freeze: refresh P1.6 implementation blueprint on frozen source.
AFTER P1.6 engine decision / freeze: refresh P2 file-by-file implementation design.
AFTER each phase acceptance: refresh NEXT phase concrete paths/ABI and execute separately.
```

- `docs/refactor/p1_5_p1_6_master_plan.md` on `refactor/p1.5` sets program ordering. `design/p1.6-orchestration` has a **snapshot-dependent** file-level blueprint, not a runtime change.
- Main source authority used here: `docs/architecture/architecture_v2.md`, `docs/research/q100_research_and_learning_roadmap.md`, `docs/research/research_portfolio_freeze_2026-09-16.md`, `docs/research/uef9_formal_evaluation_authority_freeze.md`, `docs/development/step5c_execution_owner.md`, `docs/research/uef_freeze_manifest.md` (see traceability).
- Historical documents sometimes describe earlier phase orders or capabilities as planned; no source description is converted into a claim of present implementation.
- `main`, P1.5 and P1.6 are not modified by this branch. No branch merge, rebasing or production deployment is performed in this preparation.

**Meaning of DONE here:** P2–P8 architecture prepared for review; **not** P2–P8 implementation, freeze, test pass, trading readiness or measured research finding.
