# P1.5.2 Owner36 — Local read-only acceptance checklist

**Latest remotely verified CODE SHA:** `46e4e7439d146ffdc6135b5b483c04dc78ce0cfa` on `refactor/p1.5`. **Last CI:** `37888641327` SUCCESS. Evidence: `docs/refactor/work_orders/evidence/P15-R2-GPT-P152-OWNER32-36-REMOTE-CI.md`.

## 1. Safe preflight — both Claude and Codex independently
- Local `C:\\Agentra` is **NOT ACCESSED** by remote GPT. Record exact local branch, HEAD, `git status --porcelain=v1 -uall`, `git worktree list --porcelain`, config `execution_enabled`, production data paths and Q12 dirty status. No assumptions that local and remote are synchronized.
- **READ-ONLY LOCAL VERIFICATION; NO RUNTIME PYTHON EDITS.** No reset/clean/checkout/pull, commit, Docker/scheduler restart, Broker/LLM network calls, trading enablement, order placement, production database/report output writes or Q12 dirty data mutation.
- Work on isolated copies of historical fixtures only, external to live repo/production roots, with session-scoped temp paths, automatic cleanup of PASS runs and bounded failure evidence retention.

## 2. Reporter/Story consumer and ABI verification
- Verify all **436** original top-level façade callables against ledger and public ABI test; new 35 Owner modules each <=350 LOC, no cycles or reverse trading imports. Confirm dynamic `getattr`, `patch`, monkeypatch and external plugins in the local workspace. A static-reference absence does **not** justify DEAD classification.
- Focus on 21 Markdown Clean labels (Owners 32–33), 21 AI Reporter labels (Owners 35–36), and call-time dependency injection. Confirm Korean phrasing, Scanner rank/fallback, Entry confirmation, EOD carry/recovered partial, PnL/price truth unaffected.
- Verify no modified files outside Reporting/test/docs/refactor-script/CI path scope and no runtime authority leak to Broker/Executor/Supervisor/UEF/R6.2/Step5C/D/Docker.

## 3. Actual immutable historical artifacts
- On **read-only copies** only, compare pre/post markdown and JSON byte-by-byte including Unicode, line endings, key presence/type/order, trace source precedence, LLM prompt/message bytes, model IDs, retries, fallback and exception behavior using already captured files. **No live LLM invocations.** Record before/after code SHAs, fixture names, hashes, exact mismatch details.
- Run full repository pytest against accepted pre/post baselines only in safe nonproduction isolation; include environment restrictions and result counts. Remote 337+234 tests do not substitute for entire repo tests or live production parity.

## 4. Independent reports and stage gate
- Claude and Codex independently report PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED with code SHA, tested case count, artifact hashes, retained bounded logs, untested gates and explicit no-live-execution confirmation. Store evidence as separate read-only reports in `docs/refactor/work_orders/evidence/` only after user-authorized handling of verifier artifacts; do not change Python runtime sources.
- GPT reconciles reports and safety acceptance. Until both reviews plus real-report proof pass and operator approves, **P1.5.2 OPEN; P1.5.3 NOT STARTED; no main merge or live enablement.**
