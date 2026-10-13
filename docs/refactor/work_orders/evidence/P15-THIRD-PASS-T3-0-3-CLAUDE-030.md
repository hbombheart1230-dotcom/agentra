# P15 Third Pass T3-0.3 — Session write-containment P1 closure (Claude)

BASE `910afd25491cbbc5c9aa451873b4b6816f9572ff` (Codex T3-0.2: SYSTEMDRIVE isolation P1 CLOSED, Windows smoke PASS_WITH_FINDINGS, **write containment GAP_CONFIRMED — P1**, NTFS settle workaround UNRESOLVED — P2). Scope: parity-harness source, harness tests, the Windows smoke CI gate and documentation only. **No** change to `libs/`, `graphs/`, `apps/`, `sitecustomize.py`, `conftest.py`; no Broker/LLM/Docker/scheduler/Q12, no production write, no main merge, T3.1/T3.5/T4/T5/Wave D not started. REAL_REPORT_PARITY_BLOCKED remains OPEN.

## 1. Reproduction before any patch (independent temp dirs, current harness at BASE)

`snapshot_tree()` returned path *names* only and `audit_session()` tested `after - before`; therefore only creations were visible.

| Mutation of an existing/clean tree | Verdict before (`repro_BEFORE_path_name_only_snapshot.json`) | Verdict after (`repro_AFTER_structured_manifest.json`) |
|---|---|---|
| new file | FAIL | FAIL (CREATED) |
| existing file content modification | **PASS (gap)** | FAIL (CONTENT_CHANGED) |
| existing file deletion | **PASS (gap)** | FAIL (DELETED) |
| existing empty directory deletion | **PASS (gap)** | FAIL (DELETED) |
| existing file mtime-only change | **PASS (gap)** | FAIL (METADATA_CHANGED) |
| same-size content change | **PASS (gap)** | FAIL (CONTENT_CHANGED) |
| same-size content change, mtime restored | **PASS (gap)** | FAIL (CONTENT_CHANGED, via SHA-256) |
| no filesystem change | PASS | PASS (no false differences) |

6 of the 8 required cases were false PASS (the six gaps); the creation case and the no-change control were already correct.

## 2. Manifest schema (`p156_tree_manifest.v1`)

```
{ "schema": "p156_tree_manifest.v1",
  "mode": "strict_sha256" | "fast_metadata_only",
  "entries": { "<relpath>": { "type": "file"|"dir"|"symlink",
                              "size": int, "mtime_ns": int,
                              "sha256": "<hex>"        # strict mode, files only
                              "target": "<link>" } },  # symlinks (never followed)
  "errors":  [ { "path": "...", "error": "..." } ],     # unreadable / unlistable / unstable / unsupported type
  "stats":   { entries, files, dirs, bytes, scan_seconds },
  "manifest_sha256": "<hex of the canonical entries JSON>" }
```
Difference kinds: `CREATED, DELETED, TYPE_CHANGED, CONTENT_CHANGED, METADATA_CHANGED, SCAN_ERROR`. `audit_session()` lists **every** difference (`differences`, plus per-session `containment_<tag>.json`) and still applies the project-banner and exit-code checks unchanged. Top-level `.git` is excluded as before; ordinary ignored files, empty directories and tracked files are never excluded. Entries use `os.lstat` (symlinks are not followed; Windows reparse points are classified as links or fail closed). Nothing tolerates a path or an mtime.

Fail-closed: unreadable file, unlistable directory, unsupported file type, a file that changes while it is being hashed (stat before/after the hash), manifests of different modes, or a legacy path-name-only snapshot (`TypeError`) can never produce PASS.

## 3. Strict vs fast coverage

| | strict (default, `--containment strict`) | fast (`--containment fast`) |
|---|---|---|
| Per file | size, mtime_ns, **SHA-256** | size, mtime_ns |
| Content equivalence | **proven** (`content_equivalence_proven: true`) | **not proven** (`false`, labelled in the evidence) |
| Same-size change with restored mtime | detected | **not detected** (documented limit; test `test_containment_fast_mode_is_labelled_...`) |
| Size change / mtime change / create / delete / type | detected | detected |

Acceptance evidence in this stage is always strict.

## 4. Cost

Clone at BASE: 3,177 files, 233 directories, 33.9 MB (`containment_*.json`). Strict scan after the run: 0.57–0.77 s; fast scan of the working tree: 0.13 s versus strict 0.74 s on the same tree (3,371 files, 36.8 MB). The *before* scan taken right after the clone was written took ~18–20 s per session in the four-way parallel run (cold file cache / host file scanning while four clones were being created; not CPU hashing) — a one-time cost per session that is small against the ~100 s session run. Decision: full hashing everywhere; a selective-hash tier would not prove content equivalence and is therefore not offered for acceptance.

## 5. Containment semantics (named guarantee)

`PRE_POST_END_STATE_MANIFEST_EQUIVALENCE`: the end state of the session root equals its start state down to file content. **Not proven** (recorded as `containment_not_proven` in every evidence file): a transient write-and-restore during execution; writes outside the session root; OS-wide write interception. `preflight_interpreter()` now uses the same strict manifest diff; SYSTEMDRIVE, per-session absolute TEMP/TMP/PYTHONPYCACHEPREFIX, placeholder rejection, child cwd isolation and fail-closed interpreter start are unchanged.

## 6. Negative evidence retained

* `finish()` records the classification and writes `containment_<tag>.json` **before** any cleanup (including `--same-path`, which removes the clone immediately after each run).
* For a failed session a bounded bundle `failed_sessions/<tag>/` is written: `diff.json`, both manifests (paths, sizes, SHA-256), and a bounded copy of created/changed files (caps: 64 files, 1 MiB per file, 8 MiB total; secret-looking names such as `.env*`, `*.key`, `*token*` are never copied and are listed as skipped).
* Cleanup uses `_remove_task_owned()`: only directories strictly inside the run's own work root (marker `.p156_task_owned`); anything else raises. `prune_task_owned()` gives a finite retention (count, age, total size) and removes only marked bundles; unmarked directories (Codex clones, user workspaces) are never touched (tests).
* Successful disposable sessions are cleaned automatically (control run: only `_harness` and the marker remained in the work root).
* `ISOLATION_VERDICT=FAIL` / exit 2 and `isolation.containment_verdict` / `failed_sessions` are produced whenever any BASE/FEATURE session fails.

## 7. Control runs (focused; harness change only — no 140-file differential)

Harness source = this commit; sessions cloned at `910afd25491cbbc5c9aa451873b4b6816f9572ff` (BASE×2 and FEATURE×2 share the identical code SHA); names `par_names_t2.json`, test `tests/test_live_execution_bundle_report.py` (59 recorded calls). These runs prove the *updated harness* only; earlier 69/69 or 2912/2912 results (stage SHAs `4cb92916…67e0dc0`, `af0a448…d4a5364`) are not reused.

| Run | Mode | Result |
|---|---|---|
| `control_ctl_parallel.json` | parallel 4 sessions | exit 0, `ISOLATION_VERDICT=PASS`, 4/4 containment PASS with 0 differences, 59/59 BYTE_IDENTICAL, outcomes identical, ~115 s |
| `control_cont_parallel.json` | parallel, intentional contamination in **f2 only** (same-size README change with restored mtime + deleted `AGENTS.md` + new file) | exit **2**, `ISOLATION_VERDICT=FAIL`, f2 FAIL `CREATED=1 DELETED=1 CONTENT_CHANGED=1`; b1/b2/f1 PASS; f2 bundle retained (README.md + new file copied, 1.35 MB incl. manifests) |
| `control_cont_samepath.json` | `--same-path` (clone deleted after each run), same contamination in the 4th run | exit **2**, identical classification; evidence preserved although the clone no longer exists |

The same-size/restored-mtime contamination is exactly what the T3-0.2 harness reported as clean.

## 8. Verification counts

| Item | Result |
|---|---|
| `tests/test_p156_parity_harness.py` local Windows 11 / Python 3.13 | 47 passed, 0 skipped (BASE: 23 passed; +24: 9 parametrized mutation cases + 15 other containment/retention/diagnostic tests) |
| Windows smoke job (must RUN and PASS, skips fail it) | see CI section 11 |
| Historical/Third-Pass/T3 gates (p156 second pass, p157, p158, p159 owner contracts / purity / matrix provenance, harness guards, ABI/authority) | 134 passed |
| Production-path changes | none (`git diff` of `libs/ graphs/ apps/ sitecustomize.py conftest.py` is empty) |

Full local suite (`tests`, excluding `tests/apps`, no fastapi in this interpreter): 7493 passed, 26 skipped, **35 failed + 3 errors**. The identical 35 failures + 2 errors (files `test_q12_delivery_alignment`, `test_step5b_fix4`, `test_uef2a_*`, `test_uef5_1_*`, `test_uef5_2_*`, `test_uef6c_*`, `test_uef9_*`) were reproduced on a pristine clone of BASE `910afd2` (35 failed, 188 passed, 2 errors) - pre-existing, unrelated to this change; `test_operator_ui.py` errors only because `fastapi` is not installed locally (Linux CI installs it). These are NOT counted as PASS.

## 9. NTFS directory-mtime issue — P2, **UNRESOLVED**

* The workaround in the Windows job (a throw-away `--collect-only` session with `|| true`) is **preserved unchanged in effect** and is not a fix. Causality is not established: an earlier interpretation (lazily settled NTFS directory timestamps on a fresh checkout) is a hypothesis only.
* Local reproduction attempt (`ntfs_dir_mtime_probe_local_windows11.json`): 3 fresh clones, directory mtimes sampled at +0/0.2/1/5 s with both `os.lstat` and `scandir DirEntry.stat`: **0 changes, 0 lstat/DirEntry mismatches** — not reproducible on this host.
* New read-only diagnostics (`scripts/refactor/p160_ntfs_dir_mtime_diagnostics.py`) run in the Windows job before and after the settle session: `ntfs_probe_before_settle.json` (sampled directory mtimes by both APIs) and `ntfs_settle_summary.json` (exit code, banner, MODIFIED entries of the settle session) are emitted as `::notice` annotations and uploaded with the job's artifacts, so reproducibility is visible on every hosted run.
* Containment is **not** weakened: directory mtimes are part of the manifest and any change fails. `conftest.py` is untouched (separate authorization required).

## 10. Remaining

P1 write containment: PENDING_CLOSURE until independent Codex audit. P2 NTFS settle: UNRESOLVED. T3.1 CONDITIONAL_GO (not started), T3.5 BLOCKED, REAL_REPORT_PARITY_BLOCKED OPEN, Wave D NOT STARTED. Known limits: end-state equivalence only (no transient-write detection); file permissions/ACLs/xattrs are not part of the manifest; writes outside the session root are covered only by the project's own audit and the per-session TEMP/log redirects.

## 11. CI

Recorded below after the hosted run (see the delivery commit).
