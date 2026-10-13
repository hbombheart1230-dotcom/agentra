# P15 Third Pass T3-0.2 — Windows harness isolation P1 closure (Claude)

BASE `afa10947662671673c1c932a8a2c2a8e0e05af22` (Codex T3-0.1 delta audit: FAIL on Windows harness isolation; analyzer P1 CLOSED, matrix provenance PASS, NamedTuple PASS). Scope: parity-harness environment, harness tests, CI and documentation only; **no production source, no `sitecustomize.py` change** (read-only), T3.1/T3.5/Wave D not started, no real Broker/LLM/Docker/scheduler/Q12, no production writes.

## 1. Reproduction before any change
Independent clean clone of `afa1094` (fresh `git clone`, detached) on this Windows 11 (10.0.26200) host. The failing test was run with two interpreters:
| Interpreter | Result of `test_unresolved_placeholder_creates_clone_local_debris_but_the_harness_env_does_not` |
|---|---|
| python.org CPython 3.14 venv (`Scripts\python.exe`) | PASS (not reproduced) |
| **Microsoft Store CPython 3.13.14** (`WindowsApps\python.exe`, MSIX app-execution alias; has pytest 9.1.1 in its user site) | **FAIL** at the second assertion: `['%SystemDrive%', 'm.py', 'run.py'] != ['m.py', 'run.py']` — a `%SystemDrive%` directory in the *clean* clone although the child had an absolute resolved `PYTHONPYCACHEPREFIX` |

## 2. Root cause (CONFIRMED)
A Microsoft Store CPython started with a scrubbed environment **that has no `SYSTEMDRIVE`** creates, at interpreter startup and before any user code runs, a literal tree in its *current working directory*:
```
    %SystemDrive%
    %SystemDrive%/ProgramData
    %SystemDrive%/ProgramData/Microsoft
    %SystemDrive%/ProgramData/Microsoft/Windows
    %SystemDrive%/ProgramData/Microsoft/Windows/Caches
    %SystemDrive%/ProgramData/Microsoft/Windows/Caches/cversions.2.db
    %SystemDrive%/ProgramData/Microsoft/Windows/Caches/{0A9FE8E7-7F6D-43E9-9055-49CB0F1E68C2}.2.ver0x0000000000000001.db
    %SystemDrive%/ProgramData/Microsoft/Windows/Caches/{6AF0698E-D558-4F6E-9B3C-3716689AF493}.2.ver0x0000000000000001.db
    %SystemDrive%/ProgramData/Microsoft/Windows/Caches/{DDF571F2-BE98-426D-8288-1A9A39C3FDA2}.2.ver0x0000000000000001.db
```
(`%SystemDrive%\ProgramData\Microsoft\Windows\Caches\*.db` — Windows/app-model cache files whose registry path `%SystemDrive%\ProgramData\...` is not expanded without `SYSTEMDRIVE`, so it is treated as a relative path under cwd.) It is independent of `PYTHONPYCACHEPREFIX`, bytecode writing, `sitecustomize.py` (not loaded: the child reports `sitecustomize=False`) and of the placeholder test. Decisive minimal proof on the Store interpreter, scrubbed env `{SYSTEMROOT, PATH}`: `python -c pass` → `%SystemDrive%` appears in cwd; adding only `SYSTEMDRIVE=C:` → no debris; adding USERPROFILE/APPDATA/LOCALAPPDATA on top changes nothing. Both the existing minimal test env **and the real `session_env()`** lacked `SYSTEMDRIVE`, so a real session started with this interpreter would have written the tree into the session clone root (the P1).

## 3. A / B / C experiments (independent fresh clone + session dir per run; child pid/ppid/cwd/exe/version/pycache_prefix/sitecustomize recorded; env values limited to 5 non-sensitive path variables; sensitive values never recorded)
Store interpreter, **before** the fix (`probe_store_python_BEFORE_fix.json`):
| Run | version | sitecustomize loaded | new paths in clone | literal `%…` dir |
|---|---|---|---:|---|
| A unresolved %SystemDrive% prefix (hazard) | 3.13.14 | no | 46 | yes |
| B minimal env + absolute prefix | 3.13.14 | no | 9 | yes |
| C real session_env() as returned | 3.13.14 | no | 9 | yes |
| C2 real session_env() with bytecode writing enabled | 3.13.14 | no | 9 | yes |
Store interpreter, **after** the fix (`probe_store_python_AFTER_fix.json`):
| Run | version | sitecustomize loaded | new paths in clone | literal `%…` dir |
|---|---|---|---:|---|
| A unresolved %SystemDrive% prefix (hazard) | 3.13.14 | no | 46 | yes |
| B minimal env + absolute prefix | 3.13.14 | no | 9 | yes |
| C real session_env() as returned | 3.13.14 | no | 0 | no |
| C2 real session_env() with bytecode writing enabled | 3.13.14 | no | 0 | no |
- **A** (intentional `%SystemDrive%\pyc` relative prefix) is the hazard by design and still creates debris — it is rejected by `assert_resolved_env` before a session can start.
- **B** (minimal env + absolute prefix) still creates the Store-python debris: B is *not* representative of the harness and was the weakness of the old test.
- **C** (the real `session_env()` as returned) created 9 paths before the fix and **0 after**; **C2** (same env with bytecode writing enabled) 0 after, bytecode lands in `<session>/pycache`.
- Existence before the child ran: the clone had no `%…` entry or `__pycache__` before any run (recorded as `existed_before_child`); the tree was created *during* the child process (present after `python -c pass`, i.e. at startup). The python.org venv interpreter produced 0 clone-root paths in B/C/C2 both before and after.

## 4. Minimal fix (harness only)
- `session_env()` now always carries a resolved `SYSTEMDRIVE` (parent value, else the drive of `SYSTEMROOT`, else `C:`) — with the existing per-session resolved `TEMP`/`TMP`/`PYTHONPYCACHEPREFIX`, `PYTHONDONTWRITEBYTECODE=1` and placeholder/relative-path fail-closed validation.
- New `preflight_interpreter()` runs the session interpreter once, with the exact scrubbed session environment, in a scratch directory before any clone is created; any file/directory created in its cwd aborts the run (`SystemExit`: "interpreter preflight: … clone-local debris"). The existing before/after `snapshot_tree` containment audit (empty and ignored directories included) remains the per-session verdict.
- Tests (`tests/test_p156_parity_harness.py` 17 -> 22; the old B-like test was replaced because it validated a hand-made minimal env instead of C): resolved `SYSTEMDRIVE`; placeholder hazard demonstration + fail-closed; **real `session_env()` x every available interpreter x bytecode on/off leaves the clone root unchanged**; Store-python root-cause reproduction + preflight pass; preflight fails closed with a fake interpreter that writes into cwd; preflight passes for a well-behaved interpreter. No assertion was weakened, nothing is skipped to hide a failure, no failing path is allow-listed.

## 5. Verification
| Check | Result |
|---|---|
| Failing test before | FAIL (Store CPython 3.13.14) — see §1 |
| `tests/test_p156_parity_harness.py` after, Windows, Store CPython 3.13 (full user env) | **22 passed** (3 Windows-only tests ran) |
| same, python.org CPython 3.14 venv | **22 passed** |
| python.org venv python, **scrubbed** env (`env -i`: no LOCALAPPDATA) | 21 passed, 1 skipped (Store alias not discoverable without `LOCALAPPDATA`) — the skip is reported, not counted as PASS |
| pytest-only venv (CI-like minimal packages) created from the Store interpreter, full env | **22 passed** |
| Real orchestrator end-to-end (baseline x2 / feature x2 same-path sessions, preflight on) | 4/4 exit 0, isolation verdict PASS, **0 new paths in every session root** |
| Linux (CI) | Windows-only tests are accounted as SKIPPED in a dedicated step; **never counted as Windows PASS** |
| CI | new required job `windows-harness-smoke` on `windows-latest` (python.org CPython 3.12, pytest only): runs the harness tests and fails if the two required Windows tests did not RUN and PASS |
| `sitecustomize.py` | **unchanged** (`git diff` empty; file read-only in this task) |
| Production writes / changed paths | none under `libs/`, `graphs/`, `apps/`, `conftest.py`, `sitecustomize.py` |

Cleanup: only this task's disposable work directories were removed; bounded failure evidence is preserved under `docs/refactor/evidence/p159_third_pass_t3/t302/` (sanitised: user profile paths replaced).

## 6. Remaining P1/P2
- P1: none known after this change; closure stays **PENDING_CLOSURE** until the independent Codex delta re-audit and the first green `windows-harness-smoke` run.
- P2: Store-python user-site packages are invisible in a scrubbed session (pytest may be missing for sessions run with the Store alias; python.org/venv interpreters are the supported session interpreters); `sitecustomize.py` global default prefix (`<repo>/__pycache__`) still needs a separate approval; T3.1 naming/contract cleanup, T3.5, REAL_REPORT_PARITY_BLOCKED, Wave D unchanged.

## 7. Second source of clone-root debris found by bisection (same root cause)
After the harness fix, running the harness test file with the Store interpreter from the repository root **still re-created `%SystemDrive%\ProgramData\...` in the repo root** (observed once as an untracked directory in this task's own working clone and removed there; it was never staged or committed). A per-test bisect (`22` tests, one pytest process each, Store CPython 3.13.14) isolated exactly one test: `test_determinism_plugin_clock_uuid_and_network_are_repeatable`. Its helper `_run_plugin` spawned `sys.executable` with a scrubbed environment that had **no `SYSTEMDRIVE` and no `cwd`** (inherited cwd = repository root) — the identical root cause, in the test suite instead of the session environment.
Fix: `_run_plugin(code, cwd)` now passes a resolved `SYSTEMDRIVE` and an explicit disposable `tmp_path`; and a module-scoped autouse fixture `_repository_root_must_stay_clean` fails the module if ANY entry appears at the top level of the checkout while the harness tests run (clone-root write containment as a standing guard, not a one-off check).
Result after the fix (PowerShell, repo-root cwd, full user env, then `Test-Path .\%SystemDrive%`): Store CPython 3.13.14 **22 passed, no debris**; python.org CPython 3.14 venv **22 passed, no debris**; pytest-only venv (CI-like) **22 passed, no debris**; per-test bisect afterwards: **22/22 clean**.
Other spawning tests were audited: `test_p152_r3_harness_guards.py::_run` inherits the full parent environment (so SYSTEMDRIVE is present) and always sets an explicit temp `cwd`; the stage-gate tests only call `git` with `cwd=ROOT`.
