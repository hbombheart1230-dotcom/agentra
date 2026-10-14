# P15 Third Pass T3.2.1 — Export-safe summary closure (Claude)

BASE `df9401c61485b036aab6084fadcd7da4b55b8890`. Independent Codex T3.2 audit: PASS_WITH_FINDINGS; automatic failed-session file-body copying removed and tested; **export-safe `summary.json`: GAP_CONFIRMED**; T3.2 acceptance REWORK; T3.5 BLOCKED; no P0/P1. Scope: `scripts/refactor/p156_parity_differential.py`, `tests/test_p156_parity_harness.py`, one CI junit-check line, docs. No `libs/`, `graphs/`, `apps/`, `sitecustomize.py`, `conftest.py`, Broker/LLM/Supervisor/Executor/Step5C, main, live workspace or Q12 touched. NTFS settle P2 UNRESOLVED; REAL_REPORT_PARITY_BLOCKED OPEN; T3.5/T4/T5/Wave D not started.

## 1. Gap confirmed

At BASE `run_sessions()` wrote the whole internal `evidence` object to `summary.json` (the T3.2 change only replaced the raw path samples inside `isolation.write_containment`). Real four-session run with a synthetic marker in every uncontrolled input (`export_census_BEFORE.json`): the marker substrings found in `summary.json` were the test directory (`dir_EXPMARK_TESTPATH`), the test file name, the failed-test name, the `pytest_unconfigure` output (via `sessions[].pytest_summary`) and the recorded function name (`names`, `per_function` key). Also exported at BASE: `names`, `test_files`, `reproduce` (command text with paths), `failed_tests`, `tolerance_rules`, log SHA-256/byte counts and `repo_head_for_harness`.

## 2. Fix: A (internal, local) and B (export-safe) are separate objects

* A. `local_evidence.json` — the unchanged internal evidence (comparison results, names, test files, pytest tails, reproduce text...). LOCAL ONLY.
* B. `summary.json` — built by `build_export_safe_summary(internal)`: a fresh object from a fixed allowlist; each value is re-validated (enum / 40-hex SHA / bounded non-negative int excluding bool / bool / 16-hex digest) and becomes `null` when invalid; unknown input fields are ignored; no recursive copy and no blacklist.

Export schema `p156_export_safe_summary.v1` (exact fields):

```
schema, baseline_sha, feature_sha, mode(det|natural), execution(parallel|sequential|same_path),
execution_order[b1,b2,f1,f2 subset],
containment{guarantee(fixed literal), manifest_mode(strict_sha256|fast_metadata_only), content_equivalence_proven(bool),
            verdict(PASS|FAIL), not_proven[fixed literals]},
comparison{total_calls, byte_identical, justified_tolerance, real_mismatch, unresolved, test_outcomes_identical},
failed_sessions[b1|b2|f1|f2],
sessions{b1,b2,f1,f2: {exit_code, containment_verdict, differences_total,
                       difference_counts{CREATED,DELETED,TYPE_CHANGED,CONTENT_CHANGED,METADATA_CHANGED,SCAN_ERROR},
                       differences[<=20 of {kind(enum), path_digest(16 hex)}], project_write_audit_banner}},
local_only_files[fixed literals]
```
An unknown/invalid containment verdict is never exported as PASS. Path digests are diagnostic labels, not secrecy guarantees.

## 3. Consumers and compatibility

Repository search for readers of the harness `summary.json` (`git grep` on `summary.json`, `write_containment`, `p156_parity_differential`): the only in-repo consumer is `tests/test_p156_parity_harness.py` (updated: it now reads `failed_sessions` from the new schema). The out-of-repo evidence helper scripts used in earlier stages read `isolation.write_containment` / `summary` from the old shape; they now read `local_evidence.json`, which has the **old shape unchanged**. The old `summary.json` shape is intentionally **not** preserved; committed historical evidence files are not rewritten.

## 4. Verification

| Item | Result |
|---|---|
| Security/export tests against BASE harness | **7 failed, 2 passed** (`export_tests_BEFORE.txt`; includes the earlier T3.2 end-to-end test, which reads the new schema) |
| `tests/test_p156_parity_harness.py` after fix | **63 passed**, 0 skipped locally (T3.2: 56) |
| Leak vectors, synthetic marker, whole serialized bytes | names JSON, test path, `pytest_unconfigure` output, failed-test name, recorder payload, dynamic function name/key, raw filesystem path, unknown field: **0 occurrences** (unit test over a hostile internal object + two real four-session end-to-end runs); the markers are asserted present in the local files so the test can detect a leak |
| Type/enum/SHA/bound validation | strings in count/enum/SHA/digest slots become `null`; >20 differences truncated; invalid verdict never PASS |
| Strict containment | same-size restored-mtime change still `CONTENT_CHANGED` / FAIL |
| Clean four-session e2e (tiny disposable repo) | exit 0, PASS, 4 sessions exit 0, `total_calls>=1` |
| Contaminated four-session e2e | exit 2, `failed_sessions == [b1, f2]` (failing test + filesystem contamination), f2 `CREATED=1 CONTENT_CHANGED=1`, safe summary |
| Local diagnostics after cleanup | clones removed; `failed_sessions/f2/diff.json`, `local_evidence.json` present |
| Real-repo clean four-session strict smoke (BASE=FEATURE=HEAD) | PASS, 59/59 byte-identical, exit 0 (`control_t321_clean_summary.json` is the new export-safe file) |
| Historical / T3 / T3.1 / purity / provenance / ABI gates | 137 passed |
| Protected paths | `git diff df9401c -- libs graphs apps sitecustomize.py conftest.py` empty |
| CI | Windows smoke requires >= 40 containment/security/export tests PASSED (>= 7 named `test_export_*`); see section 6 |

## 5. Remaining limitations

* `local_evidence.json`, `non_identical_details.json`, `containment_<tag>.json`, `pytest_<tag>.out`, `raw_calls_<tag>.json`, `failed_sessions/` can hold paths, digests, names and arbitrary test output; **LOCAL ONLY, not sanitized** (`LOCAL_ONLY.txt` in the output directory).
* A path digest is a label; guessable paths can be matched. SHA-256 of a low-entropy file in local manifests can be brute-forced.
* `--keep-sessions` keeps whole clones by explicit request (unsafe for real data).
* The harness cannot prevent a human uploading the output directory.
* File-body copy subissue: FIXED (T3.2). Export-safe summary issue: **PENDING independent Codex re-audit**. T3.5 stays BLOCKED until security acceptance.

## 6. CI

Run 38506076070 on `81a1429`: SUCCESS for Linux `regression` and the required `windows-harness-smoke`. Hosted Windows (Python 3.12.10): **62 passed, 1 skipped** (the skip is the Store-alias reproduction test; no Store alias on GitHub runners); the junit step requires >= 40 containment/security/export tests PASSED, including >= 7 `test_export_*`, and none skipped.
