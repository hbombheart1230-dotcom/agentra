> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# P15-R3-AUDIT-HARNESS-GUARDS-006 — fail-closed offline harnesses

**Implementer:** Claude → Codex independent audit → GPT/user decision.
**Branch:** `refactor/p1.5` ONLY, in separate isolated clone. Never touch live `C:\Agentra` or two dirty Q12 worktrees. No new feature/task branches.
**Source:** [Closeout 005](evidence/P15-R3-CLAUDE-LIVE-RUN-TRIAGE-005.md). Do not reread archived tasks.
**Allowed code:** `scripts/refactor/p152_r3_seam_challenge.py`, `scripts/refactor/p152_r3_call_recorder.py`, directly relevant offline guard tests. Docs, evidence and UI patch notes permitted. No `libs/`, `apps/`, `graphs/`, production `conftest.py`.

## Requirements
1. Fail before importing Reporting, collecting pytest, scanning source trees or opening outputs when root/config invalid. Seam script requires explicit absolute `--root`. Recorder plugin requires explicit absolute `R3_ROOT`. Neither infers root from `os.getcwd()`.
2. Normalize realpath and Windows case. Require supplied root and process cwd to match and the root to be an isolated separate Git clone. Always deny live `C:\Agentra` and its descendants, even when root is at the historical baseline commit. Support an extra user-specified protected root. No symlink bypass or probing of live tree.
3. Inputs `R3_MOVED_FREE` / `R3_NAMES`, outputs `R3_OUT` / `R3_LOG` must be explicit absolute paths. Reject output under protected live root, input overwrite or ambiguous relative paths. Preserve result semantics when guards succeed.
4. Require/document `PYTHONDONTWRITEBYTECODE=1` before Python invocation. Provide copyable Windows PowerShell templates setting isolated cwd/root, safe input/output paths. No runner cwd of `C:\Agentra`.
5. Test missing/relative root, wrong cwd, live/nested path, symlink/case normalization, missing bytecode env, output collision/protected destinations, and success in disposable isolated mini-repo. **For live paths, test pure path validation on supplied strings only: no running/importing/stat/hashing the actual live checkout.** Ensure fail before production imports and writes.
6. Run only focused isolated guard tests plus safe R3 offline smoke; 0 production writes, clear PASS/FAIL/SKIP/NOT RUN. No full pytest reruns or invalid live comparison. Do not weaken 436 ABI/57 seam tests.
7. Update BOTH canonical UI patch notes, daily patch/evidence, and changed-files-only ZIP. Push only `refactor/p1.5` after remote SHA check; stop for Codex independent audit.

## Separate open items — NOT in scope
- `controlled_mock_lanes` full-suite test CWD write isolation OPEN; do not patch production runtime.
- Historical real-report/LLM parity BLOCKED, façade SIZE_DEFERRED and numbered Owner cohesion OPEN.
- P1.5.2 final PASS/main rollout/P1.5.3 NOT AUTHORIZED.
