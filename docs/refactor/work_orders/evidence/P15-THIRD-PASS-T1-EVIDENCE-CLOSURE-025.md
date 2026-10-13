# P15 Third Pass T1 — Evidence closure (Claude, harness/gate/CI/docs only)

Verified BASE `4cb92916c976f947613f52e8b0c0790addac7eb5`; verified FEATURE exactly `67e0dc0ee0b91d45d242ccbfb3e1133d3a06e5ea` (the T1 completion commit; each session is a fresh clone checked out at that SHA). No production source changed; T0/T1 extraction and its 16 segments / 12 Owners were not reworked; T2 not started. Results below are NEW executions; the earlier run (feature SHA `4fcb325...`, a pre-rebase local checkpoint with identical `libs/`) is kept only as past evidence and is not presented as the current result.

## Task A — behavioral evidence (new runs, same harness and same targets)
Same 40 Reporter focused test files (672 tests), same recorded targets (4 T1 functions + 40 public facade functions), BASE x2 / FEATURE x2 isolated sessions (own clone, TEMP, log; `CONTROLLED_MOCK_LANE_LOG_ROOT` per session).

| Mode | Calls | Byte-identical | Justified tol. | Real mismatch | Unresolved | Tests (each session) | Write containment |
|---|---:|---:|---:|---:|---:|---|---|
| Deterministic | 2,912 | **2,912** | 0 | 0 | 0 | 671 passed + 1 known harness-induced failure, identical in b1/b2/f1/f2 | PASS x4 |
| Natural | 2,912 | 2,911 | 0 | 0 | **1** | 672 passed, exit 0 in all four | PASS x4 |

| Session | Deterministic summary | Natural summary | SHA |
|---|---|---|---|
| b1 | 1 failed, 671 passed, 1 warning in 89.71s  | 672 passed, 1 warning in 93.37s (0:01:33) | 4cb92916 |
| b2 | 1 failed, 671 passed, 1 warning in 90.06s  | 672 passed, 1 warning in 93.32s (0:01:33) | 4cb92916 |
| f1 | 1 failed, 671 passed, 1 warning in 89.81s  | 672 passed, 1 warning in 93.21s (0:01:33) | 67e0dc0e |
| f2 | 1 failed, 671 passed, 1 warning in 89.71s  | 672 passed, 1 warning in 93.08s (0:01:33) | 67e0dc0e |

- Deterministic known failure: `tests/test_trade_report_ai.py::test_ai_trade_report_hard_timeout_override_stops_slow_call`, same test and same cause in BASE and FEATURE: the deterministic plugin replaces `time.sleep`, so the hard-timeout assertion cannot observe a real wait. The same test **passes in all four natural sessions**. No other failure occurred (harness `--expect-failures 1` requires exactly one).
- Natural `UNRESOLVED=1`: `trade_report_ai.build_ai_trade_report`, test `test_ai_trade_report_hard_timeout_override_stops_slow_call`, call #2. The only differing leaf paths are `llm_response_artifact.latency_ms` and `llm_response_artifact.attempts[1].latency_ms` (109 vs 106 ms): wall-clock elapsed time of the simulated slow call; BASE#1 and BASE#2 (and FEATURE#1/#2) also differ from each other, so it is intrinsic nondeterminism of a real-time measurement, not a BASE/FEATURE difference. No tolerance rule was added (no decision, report-text or prompt field is involved). The identical record is byte-identical in the deterministic run (fake clock), which is the resolving evidence.

Raw logs (outside the repository, SHA-256 in [manifest](../../evidence/p157_third_pass/raw_evidence_manifest.json); manifest SHA-256 `3cf37be179096c886c326dc11552206734b7071d957941cc446287160631f0ba`):

| Raw log | SHA-256 |
|---|---|
| raw_calls_b1.json | `eecb947d6cba9dd38d4b97f81abd726e34ceb21dbc9e821fc0db768d996107c4` |
| raw_calls_b2.json | `eecb947d6cba9dd38d4b97f81abd726e34ceb21dbc9e821fc0db768d996107c4` |
| raw_calls_f1.json | `eecb947d6cba9dd38d4b97f81abd726e34ceb21dbc9e821fc0db768d996107c4` |
| raw_calls_f2.json | `eecb947d6cba9dd38d4b97f81abd726e34ceb21dbc9e821fc0db768d996107c4` |
| raw_calls_b1.json | `96b8216fb638f4f9f4f12deaf5728495e46859359c2f812555aeadaf2233676a` |
| raw_calls_b2.json | `6986a029386311ae7a59e5a8571891da08c2a17fa7f59f3bdbcb3f0609dfaf09` |
| raw_calls_f1.json | `a4270ad4d17bc287635a8775c37cc0d67eb455cca734c4d9a6c7b54c95d1f45e` |
| raw_calls_f2.json | `96b8216fb638f4f9f4f12deaf5728495e46859359c2f812555aeadaf2233676a` |

## Task B — T1 scope gate
`tests/test_p157_third_pass_t1_extraction_gates.py` now compares `BASE..T1_END_SHA` (`67e0dc0...`) instead of `BASE..HEAD`, and asserts that `T1_END_SHA` is an ancestor of HEAD. AST inline-reconstruct, Owner purity, authority/forbidden-prefix, ledger and PACKAGE_MARKERS checks are unchanged; the allowed-path list was not widened. T2+ changes need their own gate. Result: 9 passed.

## Task C — CI
Separate step `Gate P1.5 Third Pass T1 — pinned extraction parity` (`gate_third_pass_t1_junit.xml` is collected by the existing `gate_*_junit.xml` upload); the T1 gate was removed from the Second-Pass step to avoid double execution; `67e0dc0...` is added to the pinned fetch list so the shallow CI checkout can resolve it.

## Task D — state
`CURRENT.md`: T0+T1 IMPLEMENTED / EVIDENCE REVALIDATION; Codex prior BLOCKED, re-audit required; T2-T5 NOT STARTED; Wave D NOT STARTED; REAL_REPORT_PARITY_BLOCKED OPEN. Stale "DESIGN_READY / Claude not started" markers removed or marked historical.

## Remaining
REAL_REPORT_PARITY_BLOCKED (no frozen production artifacts), T2-T5, Wave D, `controlled_mock_lanes` operational root (T5). Production writes: 0.
