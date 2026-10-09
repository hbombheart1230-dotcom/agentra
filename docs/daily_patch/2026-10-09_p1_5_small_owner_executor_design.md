# 2026-10-09 — P1.5 strict small Owner and Executor design update

## Decision
**CONTINUE** the P1.5.1/R2-A/R2-B/R2-C implementation line without rolling back the entire Reporting tree. Existing small-owner extraction is preserved and the formerly oversized extracted modules are explicitly scheduled for further responsibility separation. The local C:\Agentra implementation state must be reconciled BEFORE any new Python edits; two Q12 dirty worktrees must remain untouched.

## Revised implementation gates
- New/moved/materially expanded implementation Owner files: <=350 physical LOC hard maximum, 150–300 preferred. No large new "helpers" dumping ground.
- Already extracted Reporting owners over 350 are technical debt, not end-state modularity PASS.
- Executor execute_from_packet.py currently 4,189 LOC / 101 functions, with an ~1,192-line orchestration function.
- Executor intermediate target 2,600–3,200, aspirational 1,200–1,800; only after precise R6.2/Step5C/D/guard/UNKNOWN/order-output parity; do not reorder safety or duplicate broker mutation.
- Original EX1–EX6 low-risk stages remain, with optional EX7–EX10 detailed safety-gated small-owner stages added.
- Baselines per handoff: P1.2 CLOSED; P1.3 FULL_DOCKER_FROZEN, Docker 2 GiB. Do not reopen for cosmetic refactor.

## Source of truth
- docs/refactor/p1_5_small_owner_policy_and_rollback_decision_v1_2.md
- docs/refactor/p1_5_reporting_implementation_packet_v1_2.md
- docs/refactor/p1_5_executor_safe_decomposition_packet_v1_1.md
- Original v1.0/v1.1 documents remain unchanged historical implementation/safety instructions.
- refactor/p1.5 is the only development branch. main is frozen.

## Design-only scope
No runtime Python, live order, Docker restart, Step5, UEF semantics or dirty local worktree touched. UI-linked patch_notes.json and patch_notes.md updated. Use CI on canonical branch and changed-files-only ZIP for this patch.
