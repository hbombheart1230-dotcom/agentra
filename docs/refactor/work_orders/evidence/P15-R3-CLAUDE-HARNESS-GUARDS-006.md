# P15-R3-AUDIT-HARNESS-GUARDS-006 — Claude implementation evidence

Branch `refactor/p1.5` only; isolated clone `C:\AgentraEvidence\r3_seam_clone`; start HEAD `85049a40fca8e9723946ed8482396cb774bfe332`; audited R3 runtime SHA `651220191e4e61506984e6020355d1c411100204` (no `libs/`, `apps/`, `graphs/`, `conftest.py` change). Live `C:\Agentra` and the Q12 worktrees were never touched; no live path was run, imported, stat-ed, listed or hashed (live cases are string-only).

## Changed
| File | Change |
|---|---|
| `scripts/refactor/p152_r3_seam_challenge.py` | Real CLI: **requires `--root`** (absolute), never `os.getcwd()`; guard runs first, then `sys.path.insert(root)`, only then imports Reporting; imported modules must resolve under root; output opened with `"x"` (no overwrite); exit 2 + `R3-GUARD-FAIL` on refusal. Part A/B logic unchanged. |
| `scripts/refactor/p152_r3_call_recorder.py` | Guard runs at plugin **import** (pytest `-p` plugins load before conftest/collection): requires `R3_ROOT`, `R3_NAMES` (existing input), `R3_LOG` (NEW output outside the clone); raises `pytest.UsageError`; hooks inert unless armed; log opened with `"x"`. |
| `tests/test_p152_r3_harness_guards.py` (new) | 61 guard tests (below). |
| `evidence/P15-R3-HARNESS-POWERSHELL-TEMPLATES-006.md` (new) | Copyable PowerShell templates; none uses `C:\Agentra` as cwd/root. |

## Guard rules (identical code in both tools; a test asserts identical behaviour)
1. Lexical checks first (no filesystem): root/inputs/outputs absolute with drive/UNC root (rejects empty, relative, `D:clone`, `\rooted`, `..`, NUL, 8.3 short names such as `AGENTR~1`); `\\?\` and `\\.\` prefixes stripped; `normcase`+`normpath` so case/slash variants match.
2. Always protected: `C:\Agentra`, its descendants **and its ancestors** (e.g. `C:\`) for the root; inputs/outputs may not be inside any protected root. Extra roots via `--protected-root` / `R3_PROTECTED_ROOTS`.
3. cwd must equal root (normalised); `PYTHONDONTWRITEBYTECODE` must be `1`.
4. Only after 1-3: every component of root/inputs/output parents is `lstat`-ed and any symlink/junction/reparse point is refused (aliases are never resolved, so a link to live is never followed); root needs a real `.git` **directory** with `HEAD` (a linked-worktree `.git` file is refused).
5. Inputs must exist; outputs must be new, outside the root, distinct from every input/output, parent existing.

## Tests / results (isolated clone, project venv, scrubbed env, `PYTHONDONTWRITEBYTECODE=1`)
- `tests/test_p152_r3_harness_guards.py`: **61 passed, 0 skipped** (61 passed also unscrubbed). Covers: live root/descendant/ancestor/`\\?\`/case/slash variants with a filesystem stub that fails on any access; an os.* spy proving no stat/list call on `C:\Agentra*` strings; missing/relative root, `..`, 8.3 alias, extra protected root, wrong cwd, missing bytecode env, output==input, duplicate outputs, output inside root/protected, protected input; mini-clone success incl. upper-cased cwd; existing output, missing parent/input, missing/invalid `.git`, **junction alias refused**; subprocess proofs that a sentinel `libs` package / `conftest.py` is **not imported** when refused; success semantics and no-overwrite on a second run; no `__pycache__` written into the audited clone.
- Safe R3 smoke from the isolated clone: guarded seam script exit 0 (`done 357 57`) and its JSON equals the baseline seam output (direct 357 equal, seam 57 equal); `--root C:\Agentra` refused (exit 2, output not created); guarded recorder over `test_trade_report_ai.py` + `test_p152_story_facade_human_owners.py`: 144 passed, 8,406 calls recorded.
- Regression: all `tests/*p152*.py` + `test_patch_notes_sync.py` **656 passed, 1 skipped**, production-path write banner 0. The 57 moved-body gate (298), ABI and ledger tests are unchanged and not weakened.
- Harness note: child processes under `-I` ignore `PYTHONUTF8`, so tests decode child output with `errors="replace"` (found when a Korean temp path made child output undecodable).

## Limits / not in scope
- The guard cannot stop an operator pointing `PYTHONPATH` or another interpreter at live source; it governs root, I/O paths, cwd and (seam script) the location of imported Reporting modules. Bytecode of the recorder module can still be written into the chosen clone's `scripts/refactor` if the env var / `-B` is omitted before launch (documented).
- 8.3 aliases and reparse points are refused, not resolved. Case-insensitivity follows the platform `normcase`.
- OPEN, unchanged: `controlled_mock_lanes` CWD write isolation; real frozen snapshot/LLM parity BLOCKED/NOT RUN; façade SIZE_DEFERRED (562/1,891/1,958); numbered Owner cohesion; full native pytest not rerun. Writer of the earlier live-root changes remains UNKNOWN.
- P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED; no main merge; awaiting Codex independent audit of the pinned SHA.
