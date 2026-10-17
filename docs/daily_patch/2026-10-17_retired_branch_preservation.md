# Retired branch preservation

Preserve 7 historical heads and unique objects in a 76134-byte incremental bundle before UI ref deletion. Independent bare recovery test PASS; S1 and PERF selected code matches integration. Keep main + integration + two active role branches. No runtime/test/workflow import/change, main merge or operational action. See docs/refactor/retired_branches/2026-10-17/manifest.json. CI runtime suites not rerun for archival-only changes; this is not a new CI PASS claim.
