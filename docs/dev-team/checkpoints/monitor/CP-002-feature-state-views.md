# Monitor CP-002: M-002 observation views

PREVIOUS_PUSHED_SHA: 0735c67ceae04de407b41c8b2b01b3b30fc66ced
BASE: d773709ba2f70471fad9badba4f92400f7818319
STATE: ACTIVE_PARTIAL_NOT_ROLE_READY, independent Work review pending

Moved five named bodies from selected_snapshot and monitor_entry_state into
feature_context_views and entry_state_views. Existing signatures/module names
remain as explicit wrappers. Only _optional_float is injected at use time;
unchanged clock, save/load, feature computation, price and symbol resolution stay
in their existing owners. No threshold, readiness equation or policy changed.

Full module AST proof includes every UNMOVED function and module-level statement;
strict expected wrapper/import/Owner ASTs precede BASE reconstruction. No entire
facade exemption. Twelve independent mutations (six per source, including untouched
body/top-level/Owner/wrapper edits) are rejected in NORMAL and Python -O processes.
Owner imports are typing/future only; no reverse import or new effects.

46 small frozen cases produced from Git BASE, not FEATURE; fixture stores producer
and source SHA-256 plus Python version. Reproduction compares entire inventory,
ordered output hashes, exception types/messages, before/after inputs and aliases.
Use-time converter mid-call repatching and nested payload identity tested.

Fresh combined own-role run: 273 PASS / 0 FAIL / 0 SKIP, 28.27s.
Raw JUnit/log: C:/AgentraWork/tmp/monitor_m002_ac4765ad2503426da0156e7c8e9101e1/.
Then Owner source was reformatted to preserve original readable multiline bodies;
no AST change. Final AST/signature/import rerun: 2 PASS, 0.88s at
C:/AgentraWork/tmp/monitor_m002_format_605a16612fe64a96a3bbe3490e6b7576/.
Remaining test results explicitly reused after that formatting-only change.
Isolated external TEMP/TMP/cache/basetemp, mock only, production write audit full;
no audit finding. One cache_dir config warning; successful scratch retained because
manual cleanup is denied by local policy, not silently deleted elsewhere.

Shared gates/official UI untouched. Work integration mapping proposals are the exact
five registered function pairs in work_monitor_current_tree.BODY_MOVES; no wildcard
or historical snapshot changes. New owners <=350 LOC, broad facade object remains
an explicit capability debt, with permitted actual attribute loads proven exactly.

Proposed paired UI note: continuous/m002_patch_notes.json and .md.
NEXT_READY: M-003 observation defaults, then M-004 exit display text; continue.
Actual checkpoint SHA posted to Issue #12 after push, not self-referenced here.
