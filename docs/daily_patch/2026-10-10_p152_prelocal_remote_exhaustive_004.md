# P1.5.2 Remote Prelocal Coverage 004 — 2026-10-10

## Direction and scope
User approved GPT remote-first source and integration audit before any user-local Claude/Codex verification. Branch `refactor/p1.5`. Prior Owner38 runtime source remains frozen; no P1.5.3.

## New tests and audits
- Existing 709 selected offline CI PASS on SHA `4db23efbc69c176d0901bf8f4a7dbc9f6d234bf8`.
- Build `scripts/refactor/p152_prelocal_consumer_debt.py`: automatically list all 436 public Reporting facade symbols, names, current disposition, static consumer files/reference types, conservative KEEP/WRAPPER recommendation and dynamic hazard. Missing static reference is NOT an inference of DEAD.
- Add `tests/test_p152_prelocal_consumer_debt.py` guaranteeing no deletion authority, no automatic waiver and still OPEN.
- GitHub separate remote `broad_remote_offline` job runs `pytest -q tests -m "not heavy and not docker and not benchmark" --maxfail=12` in clean ephemeral CI under mock/DRY_RUN without Kiwoom/OpenRouter credentials; always retain JUnit evidence.
- Results may reveal out-of-scope baseline/environment failures; report them honestly and do not modify unrelated trading/authority code just to force CI green.
- Actual C:\Agentra real Markdown/JSON and prompt parity, local complete full pytest, independent verification and human final decision remain NOT RUN. Q12 dirty worktrees, UEF, Step5C/D, R6.2, Docker and real orders untouched.

CI results for this tranche must be added to separate follow-up evidence after the remote runs conclude.

## Broad sweep first results and narrower rerun
- First remote GitHub Actions: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38035524693. Regression job SUCCESS, broad mock non-heavy suite **FAIL**: 2,114 passed / 12 failed / 9 deselected before --maxfail 12.
- Failure groups: CI-wide DRY_RUN masked expected fake LLM paths (3), old AST commits not fetched in separate job (3), Windows style path and process-lock assertions on Linux (5), API route APIRoute emptiness (1). These are diagnostic categories, NOT independently confirmed as pre-existing.
- Correct CI harness only: remove global DRY_RUN, retain TRADING_MODE=mock and blank credentials; fetch pinned AST commits before broad run; raise maxfail to 25 to expose additional failures. Add independent API route test to test cross-test contamination. Do NOT alter production app/locking/path/trading code.
- Full Windows regression, actual C:\\Agentra snapshots and independent verifiers still NOT RUN.

## Remote 004 second sweep (still FAIL)
- [38035913347](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38035913347): 4,607 passed / 25 failed / 25 skipped / 9 deselected after maxfail25; isolated API route test also failed. LLM mock and missing AST checkout failures from the first run disappeared after CI-only fix.
- Scoped failure analysis `docs/refactor/work_orders/evidence/P15-R2-GPT-PRELOCAL-004-BROAD-SWEEP-SECOND.md`. Original/updated source file blob equality confirmed for observed API, lock, path, Step5B, Scanner, UEF5 modules; baseline runtime equality remains unproven.
- Next run remove only maxfail early abort to inventory full remaining eligible Linux tests without changing any production safety code.
