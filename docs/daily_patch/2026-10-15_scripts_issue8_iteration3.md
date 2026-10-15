# Issue #8 iteration 3 — source-only task names and cleanup CLI

Status: SCRIPTS_CONTINUATION_IN_PROGRESS. Baseline 1fda8d2c10dc27d2322f55838baedf3f46e41a15.
Implemented only issuecomment-6184337860 and issuecomment-6184356507.

Task prefix resolution accepts preceding per-file literal assignments only;
dynamic/undefined prefixes remain UNRESOLVED. Original raw task/mismatch fields
are preserved. Optional --assert-mockexam-known-contract freezes source names,
not scheduler success or approval of the two unmatched tasks.

Registered (6):
- TradingAgent-MockExamDay-Closeout
- TradingAgent-MockExamDay-Preopen
- TradingAgent-MockExamDay-Q12-BTC-0855
- TradingAgent-MockExamDay-Q12-Preopen
- TradingAgent-MockExamDay-Session
- TradingAgent-MockExamDay-SessionWatchdog

Unregistered (4):
- TradingAgent-MockExamDay-Closeout
- TradingAgent-MockExamDay-Preopen
- TradingAgent-MockExamDay-Session
- TradingAgent-MockExamDay-SessionWatchdog

Unmatched (2), operational owner review; NO deletion:
- TradingAgent-MockExamDay-Q12-BTC-0855
- TradingAgent-MockExamDay-Q12-Preopen

Cleanup now parses arguments before any enumeration/deletion: --help exits0;
unknown option exits2. Zero-argument patterns, keep set and cleanup algorithm unchanged.
All cleanup fixtures use fake repositories and deletion spies; no real cleanup run.
No schtasks, batch/PowerShell launchers, run_m15_matrix or live order executed.
No existing .bat/.cmd/.ps1, T4, Reporting, runtime or Config changes.

Validation: isolated fixtures23 PASS (launcher12, cleanup4, ABI7).
Actual-checkout launcher audit20, PowerShell sources6, issues[]; wrapper audit141,
issues[]. Existing Windows native ParseFile and both OS CI gates retained.
Exact commit CI results are available on PR #5 / Actions after push; a pending
run is not a PASS. Final response records observed outcome.

Historical disposition JSON left unchanged. Latest held delta remains17 KEEP /
1 TEST_BLOCKED (historical recompute requires genuine admissible evidence) /
1 RELOCATION_CANDIDATE_AFTER_GATE. Empty --no-write success proves no authority.
Bulk moves/renames/public wrapper retirement remain BLOCKED pending explicit
ARCH_CONVERGENCE_APPROVED and usage proof. All141 wrappers retained.
Q12 cleanup and partial-registration/hidden-delete errors remain operational review
items, not fixed here. PR #5 Draft; Issue #9 not started.
