> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# PR #5 / Codex Cloud — Validate Scripts Bulk Migration Independently

**Status:** READY FOR CODEX, NOT EXECUTED. **Branch:** `refactor/agentra-target-tree`. **PR:** #5 (Draft/unmerged).
**Baseline:** 9cb5c28f729883e37f5d01d15bd66fcae0ecdd41 (before CI/work-order commit; always pin fresh origin HEAD on start).
**T4:** `refactor/p1.5` (Claude exclusive; changing independently). Do not checkout or mutate T4.

## Minimal context

Read this one file, then only the following as needed:
- `docs/refactor/2026-10-15_scripts_bulk_manifest.json` — full 157-candidate ledger, 138 moved/19 held.
- `scripts/diagnostics/audit_target_tree_compat.py` — static checker for 141 root wrappers.
- `tests/test_scripts_target_tree_compat_audit.py` — four isolated fixture tests.
- `docs/refactor/2026-10-15_scripts_bulk_migration.md` — migration acceptance summary.

Do **not** re-read T4-A/T4-B/T4-C archives or prior completed GPT/Reporting work orders.

## Execute these in order

1. Verify origin target branch SHA and working-tree cleanliness. Rebase/merge/force-push forbidden. Preserve any concurrent changes.
2. Run `python scripts/diagnostics/audit_target_tree_compat.py --json` against the **actual full checkout**. Require `ok: true`, `moved: 138`, `held: 19`, `root_wrappers: 141`, `checked: 141`, `issues: []`. Fail closed on any mismatch.
3. Run `python -m pytest tests/test_scripts_target_tree_compat_audit.py -q -p no:cacheprovider`; require 4 PASS. Verify GitHub Actions `Scripts Target Tree Contract` runs for Linux and Windows. If CI is pending, record pending instead of claiming PASS.
4. Run only **high-value** representative script smoke/parity tests from the prior 828 checks; include Research/Diagnostics/Maintenance and direct vs `-m` old/new entrypoints, repository root and external CWD. Respect running `--help` on potentially destructive tools: do not execute them without a safe fake.
5. Inspect the 19 held candidates for clear operational/Windows/safety reasons. **Report classification, no moves/deletions.** In particular retain daily UEF production-readiness checks and all scheduled Kiwoom-related launch paths.
6. Inventory the 141 compatibility wrappers, especially the 29 without observed static incoming refs. Mark `PRESERVE` / `REVIEW_AFTER_ARCH_GATE`; do not remove or rename any. No external usage evidence = UNKNOWN, not unused.
7. Verify all changed source paths have zero T4 overlap, except the two already-authorized append-only shared patch notes. Do not touch Reporting Batch 3.
8. Output a concise evidence summary. For actual bug fixes, edit only the checker, its fixture tests, this acceptance work order / daily patch / UI patch notes. Keep the same branch and update PR #5. No code changes if everything passes.

## Non-negotiables

- Real trading, broker/Executor/Supervisor/Step5C/CAS, risk/authority policy, Docker and live service changes forbidden.
- Never run actual market/order/research job for parity. Use mocked/offline fixtures and static safe checks.
- Tests use temporary isolated session directories outside repo; clear successful test artifacts; limit failed evidence retention.
- Claude owns `refactor/p1.5` and all T4 work. This task must remain fully independent.
- **Post-T4 architecture gate** must be approved before P1.5.10 wrapper retirement or bulk layout changes. No wrapper deletion or new directory migration in this work order.
- Keep PR #5 Draft; do not merge to main or attempt T4 convergence yet.
- Update `docs/daily_patch/`, UI JSON and Markdown append-only only if implementation/work-order status actually changes.

## Completion report

HEAD SHA; checker observed counts; Linux/Windows CI; 4 fixture pytest; representative parity; 19 hold classifications; remaining wrapper count; T4 overlap; any issues. If all pass, declare `PR5_SCRIPTS_INDEPENDENT_ACCEPT`, **not** `T4_PR5_MERGED`.
