> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# P15-R3-CODEX-GUARD-AUDIT-007 — independent, read only

**Target code:** `f6cc71b25d9f3aadd356ee6509b629778861ce32`. **Branch:** ONLY `refactor/p1.5`.
**Role:** Codex audits Claude's Guard 006; no implementation, merge, new branch or live-root access.
**Read:** AGENTS.md → CURRENT.md → this file → `evidence/P15-R3-CLAUDE-HARNESS-GUARDS-006.md`. Do not reread old history.

1. Independently verify the Guard 006 diff only changes the two audit tools, guard tests, docs and patch notes; runtime `libs/`, `apps/`, `graphs/`, `conftest.py` unchanged.
2. In an isolated clone, test explicit absolute `--root` / `R3_ROOT`, cwd==root, mandatory bytecode-disable, protected live `C:\Agentra` and descendants/ancestors, 8.3/case/path-prefix/symlink/junction protections, inputs/outputs and fail-before-import/collection. **Test live paths as pure strings only; do not stat/probe the actual live root.**
3. Review Windows path handling, duplicate guard logic, plugin import order, PYTHONPATH caveats and output races; distinguish true blockers from documented limits.
4. Run focused guard tests and guarded offline smoke only, with exact counts/SHA/write audit. Claude reports 61 guard PASS, 656 regression PASS/1 SKIP and 357 direct cases/57 functions, but do not adopt counts without rerun. Do not run native full pytest.
5. Return PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED and minimal findings. Report only; no commit. Real report/LLM parity BLOCKED, controlled_mock_lanes test-write finding OPEN, façade size debt unresolved. **P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED.**
