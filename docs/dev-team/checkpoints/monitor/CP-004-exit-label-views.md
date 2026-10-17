# Monitor CP-004: display-only exit labels

PREVIOUS_PUSHED_SHA: ce8703c378cfb171893462750b257012f809187a
STATE: ACTIVE_PARTIAL_NOT_ROLE_READY, independent review pending
BASE: d773709ba2f70471fad9badba4f92400f7818319

friendly_exit_axis and monitor_watch_axes moved to exit_axis_labels, same public
signatures and original per-use to_float/_is_trueish lookup. Priority/emergency/
hard/soft classifiers remain in legacy reasons.py and are covered by complete
module AST reconstruction. New Owner has only typing imports, no policy/effects.

97 BASE-only frozen variants cover empty/null/malformed inputs, numeric boundaries,
all watch-list fields, ordering and Unicode labels. Full inventory and producer /
BASE source digests reproduced; numeric converter remains byte-identical to BASE.
Six negative corruptions are rejected normally and under -O, including actual
priority/classifier body changes and attempted Broker capability substitution.
Mid-call converter repatching and ordered callback trace match BASE exactly.

Fresh M-004 + exit guard + native skill Monitor consumers: 227 PASS / 0 FAIL /
0 SKIP, 23.16s. Raw JUnit/log:
C:/AgentraWork/tmp/monitor_m004_4adfd99945e6418f8aa0655e2cdd11a4/.
Unique TEMP/TMP/TMPDIR/cache/runtime; mock/full production audit; no audit finding.
One cache_dir configuration warning. Manual scratch cleanup remains denied locally.
No shared gate/CI/official UI changes; paired proposed m004_patch_notes JSON/MD.

NEXT_READY: M-005 181-line policy trace observation view; then M-006 comprehensive
current-role accounting, native replay and consumer freeze. Do not relabel the
historical shared failures as PASS or broaden source pins; Work owns exact mapping.
Actual new SHA is published to Issue #12 after push, not in its own commit.
