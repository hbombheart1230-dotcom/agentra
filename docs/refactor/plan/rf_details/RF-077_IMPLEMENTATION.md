# RF-077 — T09 tests/fixture target and protected callable identity

- SOURCE integration/p1.5@a7654f389fddbc2829f005ab247a96bf295228d8; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. Actor Claude A (tests code only, no oracle edits); peer read-only. 7 exclusive historical paths.

API and other frontend consumer tests: 7 files; keep imports/scoping.

## Callable mapping: KEEP, not MOVE


Test discovery requires root tests/test_*.py, tests/apps/api fixture scope, CI patterns, golden hashes. There is **no new production function body to extract** from these RFs. Correct tests/fixtures are one-line KEEP_OK with path, reason, blob; no rerun for unchanged file.

## Every owned file: source to target and decision

| SOURCE | TARGET | blob / bytes | reason |
|---|---|---|---|
| `tests/test_api_catalog.py` | `tests/test_api_catalog.py` | `069dbc9d1e8d` / 1293 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_api_discovery.py` | `tests/test_api_discovery.py` | `921f6e114018` / 1059 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_api_planner.py` | `tests/test_api_planner.py` | `179981ea78c7` / 863 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_api_request_builder.py` | `tests/test_api_request_builder.py` | `65c0b54a3b83` / 954 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_api_response.py` | `tests/test_api_response.py` | `f29407a1ce21` / 499 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_build_api_catalog.py` | `tests/test_build_api_catalog.py` | `9e4607ec4938` / 708 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m16_approval_api.py` | `tests/test_m16_approval_api.py` | `f6c67187f967` / 2359 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |

## Acceptance and delivery

- One-line source blob and correct test owner/path is KEEP_OK; test/fixture refactoring itself not a code-body MOVE metric.
- A/B do not read this RF file. C03 decides KEEP from file/consumers, and adds only new genuine source functions into C01/C02 text when needed.
- No modification to test assertions, skips, xfails, golden snapshots or staged deployment requirements as a shortcut to PASS. Historical prior tests retained; not rerun for identical blob.
