# P1.5.2 Owner26–31 — Local read-only acceptance checklist

## Preconditions / no mutation
- User-local root `C:\\Agentra`. Before anything, record active HEAD, active branch, `git status --porcelain=v1 -uall`, `git worktree list --porcelain` and `execution_enabled` effective status. Do not assume local checkout equals remote `refactor/p1.5`.
- **NO** checkout/reset/clean, force pull, dependency upgrade, Docker restart, live request to Broker or LLM, order placement, scheduler restart, UI production write, or modification/deletion of local Q12 dirty worktree.
- Claude and Codex independently verify **READ-ONLY LOCAL VERIFICATION; NO RUNTIME PYTHON EDITS**. If local test fixtures write, use copied/isolated evidence outside repo with bounded retention and no production DB.
- Remote accepted code SHA: `a65d3e47e5a0de3eb801c4a12ee364cbe98270dd`; compare your local git object to it, but no unsafe reconciliation of dirty worktrees.

## Independent verifier A — Claude
1. Inventory 436 public symbols in three façade files against `docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json`. Check imports, public monkeypatch consumers, `getattr`, `patch`, runtime registered entrypoints and plugin/extension integrations in local project. Static scanner output `scripts/refactor/p152_facade_consumer_scan.py` is **not** evidence of no consumers.
2. Against **read-only COPIES** of real historical trade-report input and final Markdown/JSON artifacts, compare before-vs-refactor byte equality (`utf-8`, line endings, ordered fields), canonical trade truth, key fields, Korean operator text, Scanner rank/fallback, EOD Carry, recovered partial, PnL and cost. Record hashes; report unmatched files verbatim. Never amend outputs to make parity pass.
3. Using captured historical, already existing LLM artifacts only, compare rendered messages/prompt bytes, model selection, retries and error/fallback contracts; **do not invoke live LLM endpoints**.
4. Verify no production write/trading authority leakage in modified Reporting paths, Docker/scheduler/UEF/R6.2/Step5C/D/Executor/Broker untouched; preserve local Q12 dirty state.
5. Return a signed PASS/FAIL/INCONCLUSIVE report with exact tested commits, fixture count, equality stats, test environment and failures. **No source edits**.

## Independent verifier B — Codex
1. Independently inspect code/source AST/small-owner <=350 and 31-owner import DAG; all 436 callable names/signatures remain, compare monkeypatch seams and any runtime import consumer outside the 1,763-file remote index.
2. Run approved pytest on an isolated disposable copy with `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`, `--basetemp` set to a unique out-of-repo session path. Do not run tests in operational production root if they can write, send network requests or mutate Scheduler/DB. Preserve failure evidence for limited period, clean success temporary output automatically.
3. Report full repository pytest PASS/FAIL/SKIP vs **independently measured** baseline, reproducibility of synthetic golden fixtures, any unknown or environment-dependent failure and anything requiring live authorization. Do not fabricate a baseline or mark skipped checks PASS.
4. Verify read-only branch safety, no runtime trading authority changes and no Q12 worktree deletion. Give an independent code and consumer-proof verdict, not a copy of Claude's.
5. Return independent PASS/FAIL/INCONCLUSIVE with exact commands, code SHAs, case counts, log paths, fixture provenance, no live execution confirmation. **No source edits**.

## Final stage gate
- GPT review reconciles both independent reports against `docs/refactor/work_orders/CURRENT.md` and `docs/refactor/work_orders/evidence/P15-R2-GPT-P152-OWNER26-31-REMOTE-CI.md`; any failed, unavailable or unrun gate remains OPEN.
- No GPT_ACCEPTED/merge into frozen main/P1.5.3, trading enablement or production rollout without explicit user approval after local evidence.
