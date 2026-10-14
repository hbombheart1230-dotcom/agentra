# P15 Third Pass T3.2.2 — Export validator closure (Claude)

BASE `aceff82af7b76a9c02f81e33cf646547abf4cf23`. Codex T3.2.1 audit: PASS_WITH_FINDINGS; export-safe summary OPEN; **file-body retention CLOSED**; internal evidence compatibility PASS; strict containment PASS; CI/Windows PASS; T3.2 security gate REWORK; T3.5 BLOCKED. Scope: exactly two export-validation defects in `scripts/refactor/p156_parity_differential.py`, tests, one CI threshold, docs. No `libs/`, `graphs/`, `apps/`, `sitecustomize.py`, `conftest.py`, Broker/LLM/Supervisor/Executor/Step5C, production write or Docker.

## 1. Validator changes

| Defect | Before | After |
|---|---|---|
| SHA / path digest | `re.compile(r"^[0-9a-f]{40}$").match()` — `$` accepts a trailing newline | `re.compile(r"[0-9a-f]{40}")` / `{16}` with **`.fullmatch()`**, no strip/normalize; non-strings rejected. Invalid SHA -> `null`; invalid digest -> difference entry omitted (new helper `_ex_digest`) |
| `execution_order` | valid ids kept, others filtered, duplicates preserved | `_ex_order`: must be a `list` of exactly four `str` entries that are exactly {b1,b2,f1,f2} (order kept, so parallel `b1,b2,f1,f2` and same-path `b1,f1,b2,f2` pass); anything else -> `null` (never filtered or deduplicated) |

`summary.json` field allowlist, `local_evidence.json` schema, containment verdict computation (an invalid order does not change the PASS/FAIL derived from the sessions) and exit codes are unchanged.

## 2. Tests (before = T3.2.1 harness, after = this change)

New parameterized tests: SHA (14 cases: valid, +LF, +CRLF, +space, leading space, embedded LF, 41 chars, 39 chars, uppercase, non-hex, None, int, list, bytes), path digest (11 cases), execution order (18 cases: valid parallel, valid same-path, permutation, duplicate, missing, unknown, extra fifth, string, tuple, empty, malformed entries, None, dict), a marker/validator-input test and a real contaminated four-session run asserting exact validated values.

| Item | Result |
|---|---|
| New validator tests against T3.2.1 harness | **31 failed, 14 passed** (the 14 are the valid-value cases) — `validator_tests_BEFORE.txt` |
| `tests/test_p156_parity_harness.py` after | **108 passed**, 0 skipped locally (T3.2.1: 63) |
| Synthetic marker in whole serialized export (SHA/digest/order carrying markers + newline) | 0 occurrences |
| Clean four-session smoke (real repo, parallel, strict) | PASS, 59/59 identical, `execution_order = [b1,b2,f1,f2]` |
| Contaminated four-session smoke (`--same-path`) | exit 2, f2 FAIL `CREATED=1 DELETED=1 CONTENT_CHANGED=1`, `execution_order = [b1,f1,b2,f2]`, safe summary |
| Historical / T3 / T3.1 / purity / provenance / ABI gates | 137 passed |
| Protected paths | `git diff aceff82 -- libs graphs apps sitecustomize.py conftest.py` empty |
| CI | Windows junit step now requires >= 85 containment/security/export tests PASSED, >= 52 `test_export_*`, none skipped; see section 3 |

## 3. CI

Run 38513619584 on `832d125`: SUCCESS for Linux `regression` and the required `windows-harness-smoke`. Hosted Windows (Python 3.12.10): **107 passed, 1 skipped** (the skip is the Store-alias reproduction test; no Store alias on GitHub runners); the junit step requires >= 85 containment/security/export tests PASSED and >= 52 `test_export_*`, none skipped.

## 4. Remaining

Export-safe summary validator P2: **PENDING independent Codex re-audit**. File-body retention P2 CLOSED. Local logs/manifests/pytest output remain potentially sensitive, LOCAL ONLY. NTFS settle causality P2 UNRESOLVED. REAL_REPORT_PARITY_BLOCKED OPEN. T3.5 BLOCKED until security acceptance. Wave D NOT STARTED.
