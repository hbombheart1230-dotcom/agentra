# P15-R3-SEAM-RESTORATION-003 — Claude implementation evidence

Branch: `refactor/p1.5` only. Starting HEAD `4e94ea97324bb618eade69a7cd295bf1bd71f927`; baseline `ba6618d483e6d617f4ee56b2cb5647392c777071`. Isolated clone `C:\AgentraEvidence\r3_seam_clone`; project venv Python 3.14.2; scrubbed env (no credentials); no LLM/broker/Docker/live access. Runtime SHA = the commit that carries this file (reported in chat).

## Branch hygiene (done first)
Verified `1c6e603` (old `feature/p152-facades-r3` tip) is an ancestor of `origin/refactor/p1.5`; feature worktree had only ignored `__pycache__` (no tracked/untracked changes). Removed only that worktree without force, `git branch -d` the local branch, `git push origin --delete feature/p152-facades-r3`. Live `C:\Agentra` (still at `ba6618d`, untracked R2 audit file untouched) and both Q12 worktrees untouched.

## Change
- 11 R3 Owner files (57 functions): removed the entry-time prelude `x = facade.x`; each former façade global is now referenced at its original use site as `facade.NAME` (507 loads). Scope-aware rewrite (function/lambda/comprehension/class scopes, locals, parameters and shadowing respected); formatting/comments/Unicode untouched. Owner signatures, façade wrappers, ledger, façade files: unchanged. No `__getattr__`, exec, globals reflection, or Owner→façade import.
- Gate `tests/test_p152_r3_moved_bodies.py` rewritten (not weakened): (1) body equals pinned baseline AST once `facade.NAME` is stripped; (2) qualified-name set == baseline symtable globals bound in the façade; (3) no entry-time capture, no bare `facade` use, no unresolved global; (4) behavioural lazy-lookup test per function x 3 argument shapes — pre-call patch uses stubs, and a callback that re-patches ALL façade globals mid-call must be followed only by new bindings; (5) Owner <=350 and no façade import; façade wrapper contract/injection test kept. Verified as a reproducer: against the previous entry-binding Owners **140 cases fail**; with the fix 298 pass.

## Results
| Check | Result |
|---|---|
| Seam challenge vs baseline (same harness/inputs as evidence 002) | pre-call 57/57 identical; **within-call 57/57 identical (was 21/57)**; 0 differing runs |
| Direct synthetic cases (357, incl. the two functions no test exercised) | identical |
| Recorded synthetic differential (625 passed/1 skipped, 51 files, mock LLM/retry/timeout/fallback tests incl.) | 47,092 vs 47,092 calls, 47,091 identical; 1 = wall-clock `latency_ms` (`test_ai_trade_report_hard_timeout_override_stops_slow_call`, same record as evidence 002); per-test outcomes identical |
| Focused regression: all `tests/*p152*.py` + 42 façade-consumer files + patch-note sync | **925 passed, 1 skipped** (Windows symlink privilege); production-path write banner 0 |
| ABI (independent AST) | 436 baseline defs, 0 violations |
| Import DAG / Owners | 0 cycles in `libs.reporting`; 11 Owners, max 257 LOC (<=350); no Owner imports a façade |
| Scope | changed paths only under `libs/reporting`, `tests`, `docs` |

Commands: `python -m pytest -q -p no:cacheprovider tests/test_p152_r3_moved_bodies.py`; the differential with `scripts/refactor/p152_r3_call_recorder.py` (`-p`) and `scripts/refactor/p152_r3_seam_challenge.py`; `python -m pytest -p no:cacheprovider -q tests/*p152*.py <consumer list> tests/test_patch_notes_sync.py`.

## Not run / open
- Real frozen Markdown/JSON/JSONL and LLM prompt/retry/timeout/call-count parity: **BLOCKED / NOT RUN** (no immutable authorized snapshots).
- Full native pytest not rerun (per task); prior 35F+2E set identical to baseline and out of scope. `data/logs/controlled_mock_lanes` test-originated write finding stays **OPEN** (not fixed here); no zero-write full-suite claim.
- Façade size SIZE_DEFERRED (562/1,891/1,958); `bodies_01..05` source-order cohesion debt untouched (not authorized).
- Residual caveats: functions are no longer byte-identical to baseline (only qualification differs, proven by gate); a module global *deleted* from a façade now raises `AttributeError` instead of falling through to a builtin of the same name (no such name exists among the 57 — qualified names are exactly those bound at façade module level).
- Codex independent audit pending; P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED; no `main` merge.
