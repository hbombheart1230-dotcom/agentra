# Monitor CP-006: complete the cohesive observation boundary (packet M-008)

PREVIOUS_PUSHED_SHA: 315c68a56a9d4356afd1d86373bbc0e9ac26b924
BASE: d773709ba2f70471fad9badba4f92400f7818319
STATE: ACTIVE_PARTIAL_NOT_ROLE_READY, Work review pending
FEEDBACK_ACK: #12 / 6232295660; no assertion of fresh hosted/whole-role green

Remaining-scope inspection found two observation annotators in entry_candidate_annotation.
They are now grouped with the three traces in the EXISTING policy_trace_views
Owner: 5 functions, 337 LOC, no extra Owner file. Actual policy, signal/guard,
threshold, ranking, intent, sizing and persistence code remains unmoved.
These functions mutate caller-owned entry_info/metrics. They are NOT PURE.
Original input identity, nested sharing, callback args, return None, key write order
and partial mutation before callback failure are preserved. Original graph facade
is forwarded unchanged; only the established read-model callback is used.

43 BASE-only cases (33346 bytes), full original/helper SHA-256 and producer hash.
Independent BASE module/helper bodies execute from Git, not FEATURE. FEATURE uses
the unchanged actual read callback after full BASE byte verification. Normal/-O
negatives reject body/return/Broker-substitution/new-import corruption.
Complete original-module reconstruction and grouped Owner templates remain exact.
Prior M-005 test now expects precisely these two additional functions and one
read-model callback, not a wildcard. Historical frozen files unchanged.

Fresh affected annotation + policy trace + original role: 259 PASS / 0 FAIL /
0 SKIP, 49.74s at C:/AgentraWork/tmp/monitor_m008_3b2d7c1e737c48dd8a15ed7d2ca290ed/.
Added callback alias/exception-object identity test then ran separately:
1 PASS, 0.41s at C:/AgentraWork/tmp/monitor_m008_alias_f0990faa17dc4ebeb431d1e4d337c700/.
No runtime source change between these runs. All isolated TEMP/TMP/TMPDIR/cache/
runtime; full production audit found no violation. One cache_dir warning per run.

Earlier role/WaveB/T3/T4 contract freeze at EXACT 315c68a5:
1296 PASS / 5 FAIL / 0 SKIP, 107.52s. JUnit/log:
C:/AgentraWork/tmp/monitor_m006_contracts_d2ff1947fc1d4f60abf0b91d28ea47ef/.
The five same test IDs fail on direct legacy Shim AST reads (missing function or
plain sys import), NOT proven behavior regressions. They short-circuit; do not
claim they exhaust the shared integration work. Work owns strict exact mappings.
This is prior-SHA evidence, not a fresh final-state full contract run.

No shared gate/CI/official UI edit. Proposed m008_patch_notes JSON/MD paired.
NEXT_READY: M-006 final native T4-B + intent/guard/cascade/freshness consumers;
M-007 current whole-role accounting, exact shared repair proposal and bounded
changed-files delivery. Native replay was deliberately deferred until this last
cohesive source boundary was finalized, avoiding a redundant replay.
Actual new SHA is posted to Issue #12 after push; this document records its parent.
