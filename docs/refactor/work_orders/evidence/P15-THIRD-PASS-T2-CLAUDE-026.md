# P15 Third Pass T2 — Reporter bundle runner PURE extraction (Claude implementation evidence)

Branch `refactor/p1.5` only; isolated clones, no live `C:\Agentra`, Q12, broker, real LLM, Docker, scheduler, production logs/reports; no ZIP. Start HEAD `af0a4489dc250d804854e27917d5e2d881261537` (T1 closure); code commit `d4a5364bae817504c253e06b9150ee49c692e120`. T3/T3.5/T4/T5, Wave D, main merge not started. Authority used: CONDITIONAL GO, PURE extractions only.

## T2-0 prerequisites
- **CI shallow history:** new step `Ensure full commit ancestry for stage-pinned gates` runs after the pinned fetch steps: unshallow (fallback: deepen to 5,000) and then asserts that `4cb92916...` (T1 BASE), `67e0dc0...` (T1 END) and `af0a448...` (T2 BASE) are ancestors of HEAD, so stage gates keep working after any number of future commits. Simulated: a `--depth 2` clone of a history with 5 further commits reproduces the gap (`67e0dc0` NOT an ancestor) and the step fixes it; T1 gate (9 tests) and Second-Pass gate stay green and their meaning/allowed paths are unchanged.
- **CURRENT.md:** obsolete "T0 first / T1 next / design ready, Claude not started" instructions replaced by the current state (T0/T1 completed, Codex T1 PASS_WITH_FINDINGS, previous P1 CLOSED, T2 ACTIVE PURE only, T3/T3.5/T4/T5 NOT STARTED, REAL_REPORT_PARITY_BLOCKED OPEN, Wave D NOT STARTED); older text is explicitly labelled historical.

## T2 — `live_execution_bundle_runner.py::main`
Before / after (function): **1527 -> 1343 LOC** (-184); file 2,950 -> 2,786 (+ import block). `main()` and `run_live_execution_bundle_inprocess()` signatures unchanged (AST-checked). Protected residual: 1343 LOC of lock/queue/PID/CLI, per-run hydration, artifact/evidence writes, LLM generation, persistence, summary and spawn sequence — all SAFETY_LOCK.

### Source regions (refreshed against the current source)
| Region | Decision |
|---|---|
| L1404-1524 CLI/lock/PID/env/policy | KEEP effect owner |
| L1525-1721 target filtering, run selection | one PURE seam extracted (targeted day rows); the remaining statements call lock-touch / artifact generation / env reads (static closure analysis) -> retained |
| L1722-2197 per-lifecycle projections | 6 PURE seams extracted; segments touching `_touch_background_job_lock`, `_resolve_lifecycle_bundle_sources` (reads artifacts), evidence/strategist-input `write_json`, `.exists()` probes retained |
| L2198-2336 generation policy / deterministic report | 1 PURE seam (policy gate); deterministic report build reads the clock, plan/diagnostics read files -> retained |
| L2337-2434 LLM | SAFETY_LOCK (untouched) |
| L2435-2662 rendering/artifact writing | SAFETY_LOCK (untouched) |
| L2663-2867 persistence/operator summary/backfill | SAFETY_LOCK (untouched) |
| L2869-2932 summary/queue/lock release/spawn | SAFETY_LOCK (untouched) |

### Extracted PURE segments (ledger: [p1_5_third_pass_t2_moved_segments_ledger.json](../../p1_5_third_pass_t2_moved_segments_ledger.json))
Each segment was admitted only after a **static transitive purity closure** (new `scripts/refactor/p158_static_purity_closure.py`): the run's call closure, through module-local and imported project functions, contains no file I/O, `os.getenv`, clock, logging or lock call. Name heuristics alone were not trusted (the first planner pass would have admitted `_remove_deferred_trade_report_artifacts`, `plan_live_trade_report_generation`, `_build_run_snapshots`; the closure analysis rejected them).
| Owner function | Original lines | LOC | inputs | outputs |
|---|---|---:|---:|---:|
| `targeted_day_rows` | L1545-1557 | 13 | 5 | 2 |
| `lifecycle_exit_monitor_context` | L1776-1820 | 45 | 12 | 8 |
| `lifecycle_outcome_and_reporter_summaries` | L1821-1835 | 15 | 7 | 3 |
| `lifecycle_operator_conclusion_fallback` | L1840-1854 | 15 | 9 | 2 |
| `lifecycle_commander_market_evidence` | L2006-2025 | 20 | 1 | 5 |
| `lifecycle_scanner_filter_enrichment` | L2061-2099 | 39 | 7 | 1 |
| `closed_sell_execution_details` | L2154-2172 | 19 | 4 | 8 |
| `report_generation_policy_gate` | L2196-2221 | 26 | 10 | 8 |

### Owners (new package `libs/reporting/reporter_bundle_runtime_parts/`, [P] -> actual)
| Module | LOC | Functions |
|---|---:|---|
| `lifecycle_evidence_context.py` | 79 | `lifecycle_commander_market_evidence`, `lifecycle_scanner_filter_enrichment` |
| `lifecycle_human_summaries.py` | 50 | `lifecycle_outcome_and_reporter_summaries`, `lifecycle_operator_conclusion_fallback` |
| `lifecycle_report_policy.py` | 65 | `closed_sell_execution_details`, `report_generation_policy_gate` |
| `lifecycle_story_context.py` | 60 | `lifecycle_exit_monitor_context` |
| `targeted_run_projection.py` | 28 | `targeted_day_rows` |
All Owners import nothing but `__future__`, are <=350 LOC, mutate only caller-fresh local containers (0 in-place input mutation), and receive module dependencies through the explicit TEMPORARY_COMPATIBILITY `facade` (use-time resolution, monkeypatch seams intact). The first extraction also contained a 30-LOC segment that appended into the caller's `run_bundle_rows`/`run_story_type_counts`; it was **dropped** (an Owner must not own aggregation side effects). Segments with 8 outputs are the upper bound (no giant tuple interfaces); larger interleaved seams were left in `main()`.

## Gates and parity
| Gate / run | Result |
|---|---|
| `tests/test_p158_third_pass_t2_extraction_gates.py` (inline-reconstruct to baseline AST, unmoved defs identical, no unresolved globals/imports, <=350 LOC, forbidden tokens, fresh-container mutation, scope/authority, size reduction, public signatures, retained effect calls stay in `main()` and never in Owners) | passed |
| Existing T1 / Second-Pass gates, inventory, patch-notes guards, CI contract | see CI |

| Run (BASE `af0a448` x2, FEATURE `d4a5364` x2, isolated same-path sessions) | mode | calls | byte-identical | justified | mismatch | unresolved | tests |
|---|---|---:|---:|---:|---:|---:|---|
| t2c_baseline_control_det_pinned | det | 69 | 69 | 0 | 0 | 0 | 1 failed, 109 passed, 1 warning in |
| t2f_feature_det_pinned | det | 69 | 69 | 0 | 0 | 0 | 1 failed, 109 passed, 1 warning in |
| t2g_feature_natural | natural | 69 | 40 | 0 | 0 | 29 | 110 passed, 1 warning in 13.94s, 110 passed, 1 warning in 14.44s, 110 passed, 1 warning in 14.89s, 110 passed, 1 warning in 15.30s |
| t2h_feature_wide_det | det | 69 | 41 | 0 | 0 | 28 | 207 passed, 2 warnings in 19.90s, 207 passed, 2 warnings in 19.91s, 207 passed, 2 warnings in 19.97s, 207 passed, 2 warnings in 22.04s |

- **Decisive run `t2f`:** 29 recorded `main()` calls + 40 `_build_trade_lifecycles` calls, including the **ordered file-effect stream** of every `main()` (open/write-digest/close/mkdir/replace/remove per path, with TEMP/ROOT-relative path identity, content SHA-256, PID/PPID/ns-mtime normalised) and the post-call argument hash: **69/69 byte-identical**, BASE vs FEATURE, 0 mismatch, 0 unresolved. `t2c` is the same-SHA control proving the harness itself is deterministic (69/69).
- **Known harness-induced failure:** `test_intraday_trade_reports_dedupes_when_background_job_is_already_running` (queue/lock contention) fails identically in all four pinned sessions because pinning `os.getpid` defeats pid-liveness; it **passes in all four natural sessions (`t2g`, 110 passed)** and in the wide run (`t2h`, 207 passed). Contention behavior is therefore covered only by outcome equality, not by effect-stream equality.
- **Natural / unpinned runs (`t2g`, `t2h`):** all tests pass in every session; `main()` effect streams are `UNRESOLVED` because wall-clock-named temp directories (`trd_<ts>`), process-id digit counts embedded in cache `source_size`, and ns mtimes make even BASE#1 vs BASE#2 differ. The set of differing effect kinds between BASE and FEATURE is a subset of those between BASE#1 and BASE#2 (no BASE-vs-FEATURE-only category). No tolerance rule was added; this is evidence of outcome equality, not byte equality.
- Raw logs (outside the repo) and SHA-256: [manifest](../../evidence/p158_third_pass_t2/raw_evidence_manifest.json), manifest SHA-256 `7c0b368f4ae8e359cb9cf595d589721e8461b102e7886aaed67b4a970bf5b02e`.

## Fixture coverage (honest map)
Existing MOCK anchors cover: open BUY/HOLD, partial SELL, closed BUY->SELL, recovered/cross-day lifecycle (runtime-recovery file), LLM failure/fallback and generation-disabled, targeted regeneration, queue/lock contention (outcome only), artifact reuse, missing evidence/linkage. **No-execution-day with zero rows** and **zero-fill SELL** have no dedicated anchor by name — recorded as BLOCKED fixtures, not as PASS. Real frozen production report/LLM artifacts do not exist -> REAL_REPORT_PARITY_BLOCKED stays OPEN; operational parity is not claimed from synthetic fixtures.

## No-production-write confirmation
Every run used per-session clones/TEMP with `CONTROLLED_MOCK_LANE_LOG_ROOT` redirected; write-containment verdict PASS in all sessions (0 new paths in any clone root, no project-audit banner). Live `C:\Agentra`, Q12 worktrees, production logs/reports untouched.

## Remaining SAFETY_LOCK / BLOCKED
L1404-1524 and L2337-2932 effect regions; the interleaved per-lifecycle statements that read artifacts or write evidence; deterministic-report build (clock); queue/lock contention effect-stream equality (needs a non-pinned deterministic pid strategy); no-execution/zero-fill fixtures; REAL_REPORT_PARITY_BLOCKED; `_build_trade_lifecycles`, `apply_entry_exit_holding_enrichment`, `build_live_trade_bundle_payloads` (T3 candidates, need frozen ordering fixtures). The static purity closure is a **follow-up debt for earlier passes**: second/third-pass Owners were admitted by token heuristics plus differential parity, not by transitive closure.
