# Monitor CP-008: M9-C proof packet; M9 continues

PREVIOUS_PUSHED_SHA:efdab64f33b34be6ab26fd8edb9aba9ec4ebd479
RUNTIME_CODE:800841f229606c419dae67b0d6f794b9238676e9 (UNCHANGED)
DESIGN_READ_ONLY_SHA:658a8b99c4e47d59658ddf89e48508573bf52ab0
FEEDBACK_ACK:#12/6232543190 and6232625562; CP-007 is NOT global completion.
STATE:ACTIVE_M9, not parking/ROLE_READY

Closed the specifically unrun native mod1 gap:149 inputs/2879 variants/1541 ordered
effects,0 mismatches, Windows Python3.14.2,1 PASS,212.26s. This is exact existing
golden/native comparison and full variant-ID conservation, not old mod4 repetition.
The first new in-process harness attempt failed. Controlled first-record probes
identified explicit pytest session-root quant-shadow artifact paths as the cause;
the clean child first record matches. Reuse of the ORIGINAL native gate child
bootstrap fixes context without changing golden, assertions, tolerances or runtime.
Failed original execution and hashes retained honestly in m9_c_proof.json.

New bounded synthetic persisted DTO/artifact/error tests plus semantic mutation
oracles:17 PASS/0 FAIL/0 SKIP,5.53s. Includes exact intent dict field/key order,
tuple/reference and nested-alias contracts, missing/stale/partial/null inputs,
real unchanged Monitor artifact writer under fake external reports roots, exact
persisted bytes, and failed-write nonpublication. This is synthetic persisted
consumer parity, NOT REAL_REPORT_PARITY or genuine production snapshots.
Seven realistic protected-source AST mutants are killed normally and under -O:
exit priority, hard-stop boundary, cooldown precedence, forced guard, sizing opt-out,
runner rank cap and Broker-capability leakage. Actual protected files stay untouched.
Retained cooldown callback before/mid-call patch behavior matches BASE slices.
First -O child import setup failed; adding explicit repository import root fixed
it, no semantic oracle changes. Initial14 PASS/1 FAIL and final17 PASS separated.

Linux3.12 NOT_RUN: only Docker's private WSL distro exists; py launcher shows only
Windows3.14/3.13. Did not enter/restart Docker. Exact requirements/command contract
for Work and UI-source reconciliation in M9_LINUX_AND_UI_CONTRACT.md.
The native proof test now also PREPARES the unchanged original portable helper
branch and default external evidence output. That Linux branch was NOT executed;
Windows native computation/comparator core unchanged after recorded full PASS.

Actual UI JSON consumer identified at apps/api/adapters/patch_notes.py:10;
official store has288 entries at starting SHA. Proposed M9 JSON/MD only; Work owns
both official formats and actual entry-count/API validation on assembled tree.
No production-path write audit violation reported. Unique TEMP/TMP/TMPDIR/cache
per command. One cache_dir warning; no skip/xfail or source expectation change.

NEXT_READY:M9-A finish bounded per-symbol caller/effect/decision review for all59
retained modules plus mixed-facade unmoved definitions; M9-B only if actual
observation-only group is proven, otherwise precise Work decisions, not busywork.
Shared T3/T4 five reds are Work's separate task, not a reason to stop M9-A.
Actual pushed SHA goes to Issue12 after commit, not self-referenced here.
