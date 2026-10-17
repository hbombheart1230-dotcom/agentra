# P1.5 harness performance: first measured slice

User priority override, 2026-10-16: Reporter R1-059 / Monitor M1-060 deferred. Test infrastructure only, based on c5aa8dbfc16beda8cdb62d8c27b05abe52ae5c6e in an isolated clone. Subsequent user authorization permits PERF-1 commit/push on perf/p15-harness-perf1-20261016 only, and a changed-files-only user ZIP outside CI. No integration/main modification or changes to another worker's workspace.

## Measurement and implementation

Python C:/Agentra/venv/Scripts/python.exe, CPython 3.14.2, Windows. Commands use `-m pytest -q -p no:cacheprovider tests/test_p154_wave_b_moved_bodies.py tests/test_p159_current_owner_contract_gates.py --durations=30 --junitxml=<external session XML>`. Each invocation has a separate absolute TEMP/TMP and PID-specific pytest basetemp. HASHSEED=0 for measurement only; no operating runtime setting changes.

| Run | PASS | FAIL / ERROR / SKIP | pytest seconds | exit |
|---|---:|---|---:|---:|
| Before | 782 | 0 / 0 / 0 | 157.67 | 0 |
| After, warm bytecode prefix | 782 | 0 / 0 / 0 | 44.37 | 0 |
| After, fresh bytecode prefix | 782 | 0 / 0 / 0 | 49.07 | 0 |

Cold-prefix comparison: 68.88% lower elapsed time, 3.21x speedup. Exact test-ID/verdict multisets match, not only totals. Single-host paired measurement; OS file cache is not flushed and no cross-host or complete-P1.5 claim is made. Top 30 measured test cases before/after, JUnit hashes and limitations are in C:/AgentraWork/tmp/p15_perf/timing_summary.json. That ranking covers these 782 cases only, not the full repository. Before leaders: T3 caller scan 1.908s; public signatures 1.371s; Monitor module declarations 1.126s. Most total time is accumulated repeated subsecond Wave B metadata work, not one slow test.

Wave B caches fixed Git SHA/path source strings and immutable source-derived function text, bound-name sets and global-reference sets. Bounded, process-local caches only; no persisted result cache, no mutable AST cache, no current Owner/shim source cache. Runtime reference functions are rebuilt against current facade globals. All 20 existing assertion ASTs, test names and parametrization are unchanged. No frozen fixture or expected output changed.

## TEMP safety

The old Windows liveness probe called os.kill(pid, 0). Executed ONLY against an owned disposable child, it returned True while the child terminated. A second reproduction after a child readiness handshake emitted KeyboardInterrupt from that child's stdin read and the probe command exited 1, without producing a reliable child exit-status report. On Windows zero also equals CTRL_C_EVENT; console-control delivery and fallback process termination are not read-only liveness queries. Python documents these Windows-specific signal semantics: https://docs.python.org/3/library/os.html#os.kill . The exact Win32 branch was not traced, and no further signaling probes are performed. This demonstrates a dangerous interference mechanism, not the cause of every historical TEMP error.

Windows now uses PROCESS_QUERY_LIMITED_INFORMATION / GetExitCodeProcess and always closes handles. Access/query uncertainty means retain, not delete. POSIX keeps signal-zero behavior. New infrastructure tests cover immutable SHA-keyed caching, failed-read non-caching, immutable/source-sensitive metadata, live child survival, dead PID, Windows dispatch and denied/query-failed/active/exited API outcomes. Existing production-write audit is not relaxed. Two concurrent isolated smoke processes each passed their initial five infrastructure cases; broad parallel pytest/xdist remains unproven. Never run thread-parallel monkeypatch/State suites or share a mutable replay tree.

Final safety run: 63 PASS / 0 FAIL / 0 ERROR / 0 SKIP, exit 0, 2.52s (10 new infrastructure tests + 48 existing strict-shim negatives including optimized child + 5 patch-note/API tests). Earlier five-test infrastructure run passed; the final suite adds five Win32 API branch cases without skips. No additional whole-suite run was made.

## PERF-1 publication evidence closure

Original 782/63 runs are reused, not repeated. All three 782-case JUnit test-ID/result multisets are identical; 63-case JUnit contains 63 PASS with no skip/error/failure. Raw XML remains external; independently rechecked SHA-256 values:

| Evidence | SHA-256 |
|---|---|
| before.xml | e1f8302abf2d586ad751dcc00004f8c20791860866778c66ba3721758d1f08dc |
| after.xml | aa288237af0b9d41d099d6fafee836c14ce3c76bc5338e225d8baa3c41b99f15 |
| after_cold.xml | a7e34226bd25c032f1edd402e3e4eadfe2a76a5c411ede8fd49a44133222e8cd |
| safety_final.xml | b6437b7fd5a4ed740653e6917e83e800d733dddf93350fc41b18709f9c399ecc |

Final LF-normalized source SHA-256: conftest.py `1ff878863a24547a52c6b696089515131d7579e4b519843dea172282627b1c37`; Wave B gate `9d0d0a6ae047fade58cd4f745993603b2de02fe8596869ee73b0dab8c00ca32c`; new infrastructure tests `c8a500be5cd115f5df4fb6bea7c69c832b5cce51d3ffefeb1e98f1d2e5b0eb09`. Only explanatory comments/docs changed after the recorded safety run. No immutable BASE or original expected-value/assertion/skip changes.

Cache invalidation: Git source key includes SHA and path; source-derived caches key the full source string (and function name where applicable), so changed source cannot reuse a previous entry. Failed Git reads are not cached. Current owner/shim reads and strict-AST verification still execute on every access; `_reference` reconstructs a fresh function against current facade globals. Windows branch uses only OpenProcess(QUERY_LIMITED_INFORMATION), GetExitCodeProcess and CloseHandle; no signal/TerminateProcess capability is requested. POSIX retains its original signal-zero query.

Publication-targeted recheck: 8 PASS / 0 FAIL / 0 SKIP, exit 0, 0.56s: two cache tests, the live-child survival/dead-child test and five UI/API patch-note tests. Original 782 and 63 cases were not repeated. A disposable fake owner changed from global A to B and immediately produced new metadata; changing its previously valid shim to append a raise was rejected on the next read. No real project source was mutated for this probe. No further old signaling-helper reproduction was performed.

Successful pytest basetemp is automatically cleaned; failed evidence stays task-local. Measurement XML/JSON is compact local evidence, not committed raw logs or new large fixtures. Only task-owned, completed successful temporary/cache directories may be removed; other agents' paths are outside scope.

Post-run bytecode-cache deletion was rejected by the execution policy; no alternative deletion mechanism was attempted. Those external task-local cache directories remain pending cleanup, while successful pytest basetemp cleanup is handled by the unchanged successful-session teardown. The interrupted second old-helper probe is not counted as a passing regression test or evidence of a specific child exit code.

## Proposed validation tiers (not a CI coverage reduction)

- Focused: changed infrastructure regressions plus affected ABI/import/negative/-O and consumer seams. For Wave B helper changes retain all 768 Wave B and 14 current T3 gates. Local feedback, never substitutes for merge gates.
- Integration: retain required Linux and native Windows P0/P1, historical/current T3, Wave B, T3.5/T4 contracts, full inventory/negative checks and protected-write audits. Use independent process/TEMP roots. Preserve required job names and native-vs-portable semantics.
- Full: explicit pre-acceptance/nightly/manual complete safe mock suite, retaining and classifying failures; not silently converted into a reduced integration suite. No live Broker/LLM or operational dataset writes.

Static current workflow review finds five test files mentioned across multiple workflows: patch-note API, patch-note sync, Operator UI, trade_report_ai, scripts_target_tree_compat_audit. These are overlap candidates, not proven redundant execution: platform differences and job environments must be retained. T4 replay tests also regenerate/extract pinned BASE trees in subprocesses per boundary. No cross-process fixture/result cache is enabled: a future artifact cache must key source/tool hashes, OS/Python/dependencies, seed/config, validate full record/variant IDs and digests, remain immutable, and re-run negative/ordered-effect checks.

Future safe CI improvement: one explicit owner per same-platform suite and parallel disjoint process shards, joined by an accounting gate proving identical node-ID/result coverage; retain separate Windows native replay. Do not change hosted jobs until that equivalence is measured. Current workflows are untouched. Whole-P1.5 top 30, complete T4 timing, Linux execution and hosted post-change CI are NOT RUN / pending; no whole-harness completion claim.
