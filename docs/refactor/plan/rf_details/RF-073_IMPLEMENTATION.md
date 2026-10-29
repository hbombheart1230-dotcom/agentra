# RF-073 — T09 tests/fixture target and protected callable identity

- SOURCE integration/p1.5@a7654f389fddbc2829f005ab247a96bf295228d8; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. Actor Codex B (tests code only, no oracle edits); peer read-only. 21 exclusive historical paths.

tests/apps/api + tests/deploy; test_runtime_status.py has 10 test functions, including read-only endpoints and public process-ID sanitization.

## Callable mapping: KEEP, not MOVE

- `tests/apps/api/test_runtime_status.py::test_runtime_endpoint_reads_artifacts_without_execution` → SAME SOURCE_PATH / SAME callable; KEEP_TEST_ORACLE. Existing test fixture names and assertions must remain stable.
- `tests/apps/api/test_runtime_status.py::test_public_runtime_endpoint_hides_process_identifiers` → SAME SOURCE_PATH / SAME callable; KEEP_TEST_ORACLE. Existing test fixture names and assertions must remain stable.

Test discovery requires root tests/test_*.py, tests/apps/api fixture scope, CI patterns, golden hashes. There is **no new production function body to extract** from these RFs. Correct tests/fixtures are one-line KEEP_OK with path, reason, blob; no rerun for unchanged file.

## Every owned file: source to target and decision

| SOURCE | TARGET | blob / bytes | reason |
|---|---|---|---|
| `tests/apps/api/artifact_fixtures.py` | `tests/apps/api/artifact_fixtures.py` | `884b49d8bae3` / 15729 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/conftest.py` | `tests/apps/api/conftest.py` | `9c51380616aa` / 716 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_anomalies.py` | `tests/apps/api/test_anomalies.py` | `b6140320df87` / 3548 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_bounded_reader.py` | `tests/apps/api/test_bounded_reader.py` | `1db8496be368` / 1018 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_health.py` | `tests/apps/api/test_health.py` | `39d76e837bb6` / 1603 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_isolation.py` | `tests/apps/api/test_isolation.py` | `e22d24d1d215` / 6058 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_jsonl_tail.py` | `tests/apps/api/test_jsonl_tail.py` | `ed3624528eac` / 582 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_llm_operations.py` | `tests/apps/api/test_llm_operations.py` | `72bb736b046c` / 4128 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_market.py` | `tests/apps/api/test_market.py` | `24dc205fca0d` / 1730 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_operations.py` | `tests/apps/api/test_operations.py` | `7c666af5d0d6` / 3161 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_opportunities.py` | `tests/apps/api/test_opportunities.py` | `1307eeece7c3` / 1851 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_patch_notes.py` | `tests/apps/api/test_patch_notes.py` | `ff46628735f4` / 3477 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_paths.py` | `tests/apps/api/test_paths.py` | `81f3aaf374cd` / 1640 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_performance.py` | `tests/apps/api/test_performance.py` | `4366dda5b110` / 4336 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_portfolio_overview.py` | `tests/apps/api/test_portfolio_overview.py` | `7dc62d8fc461` / 3291 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_public_profile.py` | `tests/apps/api/test_public_profile.py` | `f10f4ac498d4` / 3781 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_runtime_status.py` | `tests/apps/api/test_runtime_status.py` | `1a8d5f687caf` / 12614 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_strategies.py` | `tests/apps/api/test_strategies.py` | `a82c291d04a6` / 1685 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_trade_reports.py` | `tests/apps/api/test_trade_reports.py` | `e0eb3fc1f65d` / 1762 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/apps/api/test_trades.py` | `tests/apps/api/test_trades.py` | `3b1e14fb228f` / 4569 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/deploy/test_m7_compose_contract.py` | `tests/deploy/test_m7_compose_contract.py` | `a803109895dd` / 5464 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |

## Acceptance and delivery

- One-line source blob and correct test owner/path is KEEP_OK; test/fixture refactoring itself not a code-body MOVE metric.
- A/B do not read this RF file. C03 decides KEEP from file/consumers, and adds only new genuine source functions into C01/C02 text when needed.
- No modification to test assertions, skips, xfails, golden snapshots or staged deployment requirements as a shortcut to PASS. Historical prior tests retained; not rerun for identical blob.
