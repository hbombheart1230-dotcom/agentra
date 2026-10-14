# P15 Third Pass T3.2 — Failed-evidence security P2 closure (Claude)

BASE `b47d6ac731173de57abe63eae28d94f68b9dc009`. Accepted Codex T3.1 verdict: Behavioral/Safety PASS_WITH_FINDINGS, Architecture/Tree PASS, eight NamedTuple contracts PASS, caller/monkeypatch ABI PASS, scanner memory-id tolerance JUSTIFIED, **T3.1 CONDITIONAL_ACCEPT**, T3.5 CONDITIONAL_GO, no P0/P1, failed-session evidence confidentiality **P2 OPEN**. This stage: the security fix only (`scripts/refactor/p156_parity_differential.py`, `tests/test_p156_parity_harness.py`, one CI check line, docs). No `libs/`, `graphs/`, `apps/`, `sitecustomize.py`, `conftest.py`, Broker/LLM/Supervisor/Executor/Step5C, main, production data or Q12 touched; no structural cleanup; NTFS settle P2 UNRESOLVED; REAL_REPORT_PARITY_BLOCKED OPEN; T3.5/T4/T5/Wave D NOT STARTED.

## 1. P2 confirmed at BASE

`preserve_failed_evidence()` copied the *bodies* of created/changed files into `failed_sessions/<tag>/files/`, guarded only by a file-name pattern (`.env*`, `*.key`, `*secret*`...) plus size caps. Census with the real orchestrator (`census_before.json`), one session contaminated with the synthetic marker `FAKE_TEST_API_KEY_DO_NOT_USE` in a benign-named new file `harmless.txt`, in `.env.local`, and appended to the existing `README.md`:

| Surface | At BASE |
|---|---|
| `failed_sessions/f2/files/harmless.txt` | **marker copied** (benign name) |
| `failed_sessions/f2/files/README.md` | **marker copied** (changed existing file) |
| `.env.local` | not copied (name filter only) |
| `diff.json`, `manifest_*.json`, `containment_<tag>.json`, `summary.json` | no body; **paths, sizes, mtimes and SHA-256 present**; `summary.json` carried a raw-path `new_paths_sample`/`differences_sample` |
| `pytest_<tag>.out`, `raw_calls_<tag>.json` | arbitrary test output / recorder payloads (not sanitized; the marker appears only if a test prints it) |

Distinct exposure surfaces: (1) file bodies copied, (2) path names and content digests in manifests/diffs, (3) unsanitized pytest/recorder output, (4) retained complete clones with `--keep-sessions`.

## 2. Fix (removal, not detection)

* The automatic body-copy path is **removed**. `preserve_failed_evidence()` keeps its signature but never reads `root`; bundle = `diff.json` (classification + bounded difference list), `manifest_before/after.json` (path, type, size, mtime_ns, SHA-256, symlink target), `bundle.json` (`file_bodies_retained: false`, `copied: []`, `retention: metadata_only`), `LOCAL_ONLY.txt`, ownership marker. No credential detector was added; `_SECRET_NAME`/byte caps are gone. **No environment variable, flag or opt-in re-enables body copies** (test `test_security_no_environment_switch_re_enables_body_copies`).
* Export-safe view: `summary.json` now holds counts and `{kind, path_digest}` pairs only (`export_safe_differences`); raw paths, hashes and sizes stay in the local files. The old raw `new_paths_sample` was removed from the verdict.
* `--keep-sessions` help now states it is UNSAFE for real data (complete clones). The run output directory gets `LOCAL_ONLY.txt`.
* Unchanged: strict manifest reads and hashes every file body for verification; same-size restored-mtime, create/delete/type, scan-error fail-closed, interpreter preflight, four-session verdict, exit code 2, successful-session cleanup, ownership marker and `_remove_task_owned` / `prune_task_owned` safeguards.

## 3. Three different things (read / retained / exported)

| Class | Content |
|---|---|
| Data read for verification | every file body under the session root, SHA-256-hashed in memory (strict mode); never written anywhere |
| Metadata retained locally | classification, counts, path/type/size/mtime/SHA-256 manifests, pytest output, recorder logs — **local only** (`LOCAL_ONLY.txt`), bounded (2,000 listed differences; manifests above 50,000 entries are digest-only) with finite retention (`prune_task_owned`: count/age/size, marked bundles only) |
| Files uploaded or committed | nothing automatic. `summary.json` is the only export-safe file. The CI workflow references no harness run output (`test_security_ci_workflow_never_uploads_failed_session_bundles_or_run_outputs`); the Windows job uploads only the harness JUnit/pytest log/NTFS diagnostics of the *harness unit tests*, which contain no session bundles |

## 4. Residual exposure (explicit, not fixed here)

1. `pytest_<tag>.out` and `raw_calls_<tag>.json` can contain whatever a test prints or a recorder captures; classified local-only, **not sanitized** (`test_security_residual_exposure_arbitrary_test_output_is_local_only_not_sanitized` documents that a printed marker appears only in `pytest_*.out`).
2. Path names appear in local `diff.json` / manifests / `containment_<tag>.json`; a path digest in `summary.json` is a label, not a secrecy guarantee for guessable paths.
3. SHA-256 of a short or low-entropy file can be brute-forced; manifests are therefore local-only.
4. `--keep-sessions` keeps complete clones by explicit request.
5. A human can still upload the output directory manually; the harness cannot prevent that.

## 5. Verification

| Item | Result |
|---|---|
| New security tests against BASE harness | **7 failed, 2 passed** (`security_tests_BEFORE.txt`) |
| `tests/test_p156_parity_harness.py` after the fix (local Windows 11, Python 3.13) | **56 passed**, 0 skipped (BASE 47; the single body-copy test replaced by 10 security tests incl. an end-to-end run on a tiny disposable repo) |
| Historical p156/p157/p158, T3/T3.1 current gates, purity, matrix provenance, harness guards, ABI/authority, symbol ledger | 137 passed |
| Clean four-session strict-containment smoke (BASE=FEATURE=HEAD, real repo) | 4/4 PASS, 0 differences, 59/59 byte-identical, exit 0, clones cleaned (`control_t32_clean.json`) |
| Deliberately contaminated session (real orchestrator, tiny repo) | exit 2, `ISOLATION_VERDICT=FAIL`, f2 `CREATED=2 CONTENT_CHANGED=1`, bundle metadata-only, **marker found in 0 output files** (`census_after.json`) |
| Protected paths | `git diff b47d6ac -- libs graphs apps sitecustomize.py conftest.py` empty |
| Windows/Linux CI | see section 7 |

No full-suite or behavioral differential was run: no production code changed.

## 6. Changed paths

`scripts/refactor/p156_parity_differential.py`, `tests/test_p156_parity_harness.py`, `.github/workflows/p152-r2c-residual-regression.yml` (junit check: counts `test_security_*` and requires >= 32 containment/security tests PASSED on Windows), `docs/refactor/work_orders/CURRENT.md`, this evidence file, `docs/refactor/evidence/p159_third_pass_t3/t32/`, patch notes (JSON + MD), `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_2.md`.

## 7. Status

T3.2 P2 security fix **PENDING independent Codex security delta-audit**. T3.5 stays CONDITIONAL_GO until that review.
