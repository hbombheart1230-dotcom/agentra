# 2026-10-15 — GPT Source Work Order03

Branch: refactor/agentra-target-tree
Base: 9c31416d25eb5ca37e25ab9327cb6dfcaec04f7c (local/remote matched, clean).
T4 observed: ad3659131e804f9fa84b67f3bf6a0a0b2017a064.
Status: SCRIPTS_CONTINUATION_IN_PROGRESS. Inline user specification only.

## Before / after ownership and actual reduction

| Responsibility | Prior local bodies | Owner after | Reduction |
| --- | --- | --- | --- |
| broker-code observation | Ops report and trade reason query (2; Ops had truncation bug) | libs/diagnostics/observations.py::broker_code_success | Bug corrected, two implementations converge to one |
| numeric summary | Ops report and incident reconstruction (2) | libs/diagnostics/observations.py::numeric_summary | 1 redundant copy removed |
| CLI JSON capture | M23(1), M24(2), M26(1), M27(1), M29 closeout(1), M29 archive check(1) | libs/diagnostics/cli_capture.py::capture_cli_json | 6 redundant copies removed |
| JSONL reading | Ops _iter_events, incident _iter_rows, M31 _iter_jsonl (3) | Existing libs/reporting/event_log_reader.py::iter_jsonl_events | 3 redundant local loops removed; reader unchanged |
| SHA-256 | Archive integrity and M29 archive check (2) | libs/diagnostics/archive_inspection.py::sha256_file | 1 redundant copy removed |
| line count | Archive integrity and M29 archive check (2) | libs/diagnostics/archive_inspection.py::line_count | 1 redundant copy removed |

18 local bodies now delegate. Existing identical/equivalent redundant copies
removed:12; broker correctness/convergence adds one fewer implementation after
fixing its differing behavior (not described as an already identical old copy).
All original function names, signatures, invocation argv and CLI wrappers retained.
libs/diagnostics/__init__.py exports the five pure helpers. No live CLI selected
or executed by these owners except the callable explicitly supplied by a caller.

## Contracts preserved / intentional fix

Ops report now uses finite Decimal exact-zero, matching the prior trade query
fix: fractions, NaN, Infinity, tiny nonzero strings are not successful. Text
codes, None and blanks preserve their meanings. Observation only, no approval,
order, retry, broker-outcome or authority changes.

Numeric count/avg/p50/p95/max, negative-value exclusion, nearest-index selection
and Python round (including half-to-even ties) unchanged. JSON capture preserves
StringIO/redirect_stdout behavior, stderr propagation, int(rc), JSON scalars/lists/
null as well as dictionaries, empty/invalid JSON fallback, and child exceptions.
M23/M24 argv assembly is unchanged. 1MiB hash reads and UTF-8 errors=ignore line
count unchanged. JSONL retains lazy Ops/M31 and eager incident return behavior;
missing-file list behavior, malformed/non-dictionary skips, unicode, duplicate
rows and order retained. No day argument/cache, no shared reader modification.
All main, _utc_day and _to_epoch ASTs unchanged in affected scripts.

## Verification and limits

- 119 distinct focused pytest PASS:52 new helper/facade cases and67 existing Ops,
  M31, trade reason and WO01 diagnostic cases. Initial combined run117 PASS;
  adding two percentile-tie cases gave52 PASS in the new suite on final code.
- M23/M24/M26/M27/M29 capture regressions invoke only stub child main functions;
  expected exact argv, exit values and non-dictionary JSON results verified.
- Ops summary: zero success1, fraction/tiny/nonfinite failures5, unknown1.
- Baseline pure-function differential scenarios63 PASS: numeric14, seven capture
  functions x six output fixtures42, JSONL3, hash/count4. Only selected historical
  function ASTs executed, not historical closeout workflows.
- Baseline CLI comparisons22 PASS (11 scripts x help/unknown-option). Each compares
  historical canonical source and root direct/module + canonical direct/module:
  110 subprocesses with identical stdout/stderr/exit0/exit2. Help/error parsing
  stops before operational work. All inputs/cwd are isolated OS-temp.
- Hash fixtures exceed1MiB and contain invalid UTF-8; missing-file errors retained.
  Lazy reading does not open before iteration; eager reading does. No JSONL cache.
- Existing M23/M24/M26/M27/M29 full-closeout end-to-end tests and disaster-recovery
  Drill tests intentionally NOT run: those execute real child workflow bodies,
  contrary to this work order's no-Closeout/Drill constraint. Helper regressions
  cover the changed seams instead. No full-repository or native Windows claim.
- Successful pytest temp automatically cleaned; differential TemporaryDirectory
  cleaned. Nonfatal pytest warning: cache_dir with cacheprovider disabled.

## Scope / residual risk

11 specified canonical diagnostic scripts, four new owner files, one new test
file and three change-history files only (19 total). All141 public wrappers and
shared event reader unchanged. T4 code overlap0; approved append-only shared UI
notes may overlap as documents. No T4 checkout/merge/cherry-pick, Graph/Runtime/
Supervisor/Executor/Broker/UEF/Config/Web/API/Operator UI/scheduler changes, no
actual Closeout/Drill, live events/DB, network or real order calls.

UI JSON preserves all old entries/order and correct entry_count; Markdown prefix
unchanged. PR #5 Draft, no main merge. ZIP contains changed files only.
Residual limits: full child-workflow execution and native Windows behavior are
unverified by design; inherited diagnostic fallbacks remain unchanged. No new
scope is proposed or implemented.
