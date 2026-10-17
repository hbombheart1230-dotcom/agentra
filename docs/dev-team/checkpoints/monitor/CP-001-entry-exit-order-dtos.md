# Monitor CP-001: M-001 implemented, independent review pending

PREVIOUS_PUSHED_SHA: 6b2a91340262e1e7e221582646da2beb0b1965f8
BASE: d773709ba2f70471fad9badba4f92400f7818319
STATE: ACTIVE_PARTIAL_NOT_ROLE_READY

Three full BASE blobs (415 LOC / 5 functions) now live under
libs/agents/monitor/projections; exact legacy identity shims preserve package,
private/public objects, bidirectional patching and legacy pickle resolution.
entry_evidence, observability and order_lifecycle contain no new policy or effects.
Entry callbacks retain the real unchanged offline skill/context/ETF readers.
No shared T3/T4/Wave B gate, official UI notes or production authority changed.

BASE-first synthetic fixture: 59 cases, 26165 bytes, SHA-256
e8426fa0040b8d915fab939bbd102e5f245e44c88b57ce60fa665b450b49b17b.
Fixture embeds BASE source SHA-256 and producer source digest, Python 3.14.2.
Observations include ordered keys/callbacks, exact errors, inputs and nested aliases.

Fresh initial combined run: 359 PASS / 1 FAIL / 0 SKIP, 55.46s.
Failure: UTF-8 BOM stripping in the NEW retained-source verifier, not runtime.
UTF-8 raw reads fixed it without changing runtime bodies.
Targeted final-state rerun: 8 PASS / 0 FAIL / 0 SKIP, 17.22s.
Final entire new cohort: 73 PASS / 0 FAIL / 0 SKIP, 12.49s.
Unchanged consumer results from the initial run are reused, not a fresh whole rerun.
All TEMP/cache/runtime/basetemp paths were external per-run. One unknown cache_dir
configuration warning; no skip or production-write finding.
Scratch remains local: manual cleanup denied by OS policy; no deletion bypass.

Raw root: C:/AgentraWork/tmp/monitor_m001_238f7c1aab484883a5dcb10bdee55f55/
initial: pytest_0b0be1be544248da9cb99b517ebcaa85;
targeted: targeted_e09432776e30417b85115702e9a5eecf;
final: final_dae21b799d1942438778094caa3ab31b.

Work exact shared mapping addition:
libs/runtime/monitor/entry_evidence.py -> libs/agents/monitor/projections/entry_evidence.py.
Both monitor_exit pairs are also registered literally in work_monitor_current_tree.py.
Never use a wildcard follow rule. Historical five shared failures remain Work-owned.
No new broad/shared/native result or hosted CI PASS claimed.

UI paired proposal: continuous/m001_patch_notes.json and m001_patch_notes.md.
program.json remains the immutable initial inventory/queue; status.json advances it.
NEXT_READY: M-002 feature/state views, then M-003 and M-004; continue immediately.
Actual new SHA is posted to Issue #12 after push; this file names its parent.
