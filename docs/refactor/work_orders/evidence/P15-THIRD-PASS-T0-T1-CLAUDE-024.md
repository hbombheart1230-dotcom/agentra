# P15 Third Pass T0 + T1 — Reporter (Claude implementation evidence)

Branch `refactor/p1.5` only; isolated clones; no live `C:\Agentra`, Q12, broker, real LLM, production data/reports, scheduler, Docker; no ZIP. Baseline code `4cb92916c976f947613f52e8b0c0790addac7eb5` (design commit; code identical to `bf59c4d2941442fc2dff41c3c2888f053b4b1577`). Scope: T0 + T1 only (T2-T5, Wave D, main merge not started). Facades `trade_report_ai.py`, `trade_report_markdown_clean.py`, `trade_story_pipeline.py` were not edited, moved or renamed.

## T0 — Reporter baseline and consumer map (read-only)
[t0_reporter_consumer_map.json](../../evidence/p157_third_pass/t0_reporter_consumer_map.json): production consumers, importing modules, test files and monkeypatch files for the four targets and the three facades; 40 focused test files; representative scenario coverage by existing MOCK tests (open/HOLD 21, partial exit 11, closed BUY->SELL 10, LLM failure/fallback 41, regeneration/queue/lock 11, missing coverage/status 40; **no-execution scenario not found by name = gap, recorded, not fabricated**). Fixtures are MOCK/synthetic in-test only: **REAL_REPORT_PARITY_BLOCKED** (no lawfully available frozen production report/LLM artifacts), so effectful report/queue/lock/persist paths were not touched.

## T1 — Pure read-model / fallback / compact-input cuts
Method: the same dataflow-proven extract-method as the Second Pass (ledger [p1_5_third_pass_t1_moved_segments_ledger.json](../../p1_5_third_pass_t1_moved_segments_ledger.json), 16 segments / 1,824 LOC / 12 Owners). Reporter-specific rules: `name = deps[...]` dependency bindings stay in the original function and the callables are passed explicitly to the Owner (use-time resolution and the public monkeypatch surface unchanged); a clock callable (`_utc_now_iso`) is allowed only as an explicitly injected parameter of the fallback schema Owner; module globals resolve through the same TEMPORARY_COMPATIBILITY `facade`; ambiguous effect words are matched as whole tokens (`_compact_timeline_rows` is not a clock read).

| Function (file) | Before | After | Owners (package, LOC) | Retained in original |
|---|---:|---:|---|---|
| `build_trade_report_memory_surface` (`trade_memory_surface.py`) | 671 | **50** | `trade_memory_projection_parts/`: `memory_input_visibility` 189, `memory_feedback_rebuild` 93, `memory_status_summary` 74, `memory_surface_payload` 327 | sequencing, final return |
| `build_trade_read_model` (`trade_read_model.py`) | 563 | **80** | `trade_read_model_parts/`: `read_artifact_selection` 66, `read_truth_projection` 234, `read_display_context` 225 | `load_trade_report_payloads` call (I/O), early returns |
| `fallback_report` (`trade_report_ai_deterministic.py`) | 534 | **187** | `trade_report/ai_facade_parts/`: `fallback_seed_context` 64, `fallback_summary_status` 76, `fallback_sections_schema` 259 | dependency bindings, `_story_post_exit_shadow` call, final return |
| `compact_story_input_for_llm` (`trade_report_ai_compact_input.py`) | 408 | **51** | `trade_report/ai_facade_parts/`: `compact_input_facts` 62, `compact_input_payload` 329 | dependency bindings, return |

Largest function among the four: 671 -> 187. Owners: all <=350 LOC, import nothing but `__future__`, no filesystem/clock/LLM/broker/State/persistence, mutate only caller-fresh local containers; no in-place mutation of inputs (checked: 0).

## Gates and results
| Gate | Result |
|---|---|
| `tests/test_p157_third_pass_t1_extraction_gates.py` (inline-reconstruct to baseline AST, unmoved defs identical, no unresolved globals/imports, <=350 LOC, forbidden tokens, fresh-container mutation, scope/authority) | passed |
| Existing second-pass/Wave/ABI/inventory/moved-body/facade-ledger guards, patch-notes sync | see CI; Second-Pass scope guard re-pinned to its own end SHA `bf59c4d` |
| Isolated deterministic differential, baseline x2 + feature x2, 40 focused files / 672 tests, 2,912 recorded calls on 4 targets + 40 public facade functions (Markdown str and JSON dict outputs, post-call State hash) | **2,912 / 2,912 byte-identical**, 0 justified tolerance, 0 mismatch, 0 unresolved; per-test outcomes identical in all 4 sessions; write containment 0 new paths |
| The single failing test in that run (`test_ai_trade_report_hard_timeout_override_stops_slow_call`) | fails identically on BASE and FEATURE only because the deterministic plugin fakes `time.sleep`; in natural mode it passes in all four sessions (exit 0, isolation PASS) — a harness artifact, not a code difference |
| Production writes | 0 (`CONTROLLED_MOCK_LANE_LOG_ROOT` redirected into the session dir; project audit untouched) |

## BLOCKED / SAFETY_LOCK / deferred
REAL_REPORT_PARITY_BLOCKED (no frozen production artifacts; Markdown/JSON bytes are proven only on MOCK fixtures); LLM request/response parity needs a real/frozen provider fixture (prompt locks untouched: `compact_story_input_for_llm` output is byte-identical on fixtures); `trade_bundle_assembly::apply_entry_exit_holding_enrichment` and `trade_lifecycle_builder::_build_trade_lifecycles` need frozen lifecycle-ordering fixtures (not started); `live_execution_bundle_runner::main`, `closeout_maintenance`, `intraday_trade_reports` effect owners untouched (T2). Tuple/many-input seams and the `facade` injection remain T3 debt.
