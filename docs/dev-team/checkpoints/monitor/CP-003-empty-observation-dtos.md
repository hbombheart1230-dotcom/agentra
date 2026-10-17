# Monitor CP-003: M-003 implemented, not whole-role completion

PREVIOUS_PUSHED_SHA: a0ea6ff31eaebd90f9414d34fd7c6858b1ab3aa1
BASE: d773709ba2f70471fad9badba4f92400f7818319
STATE: ACTIVE_PARTIAL_NOT_ROLE_READY, Work review pending
FEEDBACK_ACK: Issue #12 / 6232241207 (WORK_REVIEW)

Eight empty observation DTO builders moved into signal_evidence_defaults with
original facade signatures and fresh containers. _empty_human_chart_buy_guard,
_empty_human_chart_entry_setup, scoring/threshold computation and every other
unmoved definition remain covered by full original-module AST reconstruction.
Only the original builder plus three reclaim metadata constants are read through
the facade at use time. Callback return identity and all 28 kwargs are tested;
no new entry/exit/admission, Broker, guard or persistence capability is used.

BASE-only fixture: 14 cases / 3840 bytes, producer/source SHA-256 embedded.
Malformed threshold and missing/null cases included; no expectation adjustment.
Seven corruptions including retained buy guard/setup/scoring bodies, tuning
constant, new import and Broker-call substitution rejected normally and under -O.
Fresh nested dict/list identities are pairwise disjoint between calls.

Fresh combined M-003/M-002/old-role/minute/cascade run: 235 PASS / 0 FAIL / 0 SKIP,
27.39s. Raw JUnit/log at
C:/AgentraWork/tmp/monitor_m003_cea978d90f5f487ba632682fe18ec595/.
TEMP/TMP/TMPDIR all unique before Python startup, external bytecode cache and runtime,
mock mode and full production-path write audit; no write audit finding. One cache_dir
configuration warning. Scratch cleanup denial remains explicit, no foreign cleanup.

Work feedback disposition: earlier KEEP_WITH_REASON for the three M-001 DTO modules
is superseded by Work's exact scoped whole-blob acceptance (not blanket monitor_exit
authority). Raw blobs, callback arguments/order and exception/alias proof are in
CP-001. Work's Linux evidence is independent and REUSED, not our fresh Windows run.
P15-WORK-002 acknowledged: unique TMPDIR/TEMP/TMP is required, --basetemp alone is
insufficient. No shared conftest change.

NEXT_READY: M-004 exit display labels; M-005 policy trace read model (181-line
build_monitor_policy_trace, copies already-decided inputs; no policy normalization
or threshold/intent authority). M-006 whole-role frozen consumer/authority review
follows implementation. All three packets are registered in ready_followup.json.
The chart-context summary stays SAFETY_LOCK: it computes structure_breakdown_signal
consumed by exit decisions, despite its innocuous summary name.

Paired proposed UI notes: continuous/m003_patch_notes.json and .md.
No shared gate/CI/official UI changes; actual SHA posted to Issue #12 after push.
