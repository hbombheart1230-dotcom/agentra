# P15-R3-FACADE-LOC-NEXT-CANDIDATES-010 — Claude implementation evidence

Branch `refactor/p1.5` only. Start HEAD `24c0b2f80a0fba1938d6530f40d9b76ad038a43d`. Isolated clone `C:\AgentraEvidence\r3_seam_clone`, project venv, scrubbed env, `PYTHONDONTWRITEBYTECODE=1`; guarded Guard-006 recorder. Live `C:\Agentra`/Q12 untouched; no LLM/broker/production writes. LOC 008 results are not re-verified here.

## 1. Re-measured candidates (dry run, net façade LOC / Owner LOC)
| Candidate | Net | Owner | Decision |
|---|---:|---:|---|
| **Markdown operator narrative builders (20 fns)** | **-151** | 264 | **implemented** |
| Markdown narrative subset (11 fns, original estimate) | -93 | 159 | superseded by the larger cohesive set |
| AI dependency maps (`_section_builder_deps`, `_context_builder_deps`) | -69 | 89 | next candidate |
| Story dependency maps (3) | -64 | 89 | next candidate |
| Markdown memory/policy phase lines (12) | -65 | 136 | rejected now: truth/precedence-adjacent, stays for a dedicated slice |
| Markdown numeric/format primitives (17) | -55 | 150 | rejected now: hottest code, many consumers |
| Time/duration (7) | -38 | 83 | low value |
Consumer review of the 20 members: all remaining references outside the façade are via `deps` keys or same-named local helpers in other Owners; every façade symbol keeps a wrapper `def` (same object identity for deps maps), so no static or dynamic consumer changes. No member touches LLM prompt/router/retry/timeout/fallback or order/approval authority.

## 2. Implemented slice
Moved to **`libs/reporting/trade_report/markdown_clean_operator_narrative.py` (264 LOC)**: `_translate_watch_item`, `_translate_reason_phrase`, `_translate_invalidation_item`, `_humanize_reporter_recommendation`, `_bullet_lines`, `_section_summary`, `_build_entry_decision`, `_build_guard_approval`, `_build_timeline`, `_extract_metadata_from_texts`, `_monitor_delta_interpretation`, `_entry_reason_line`, `_entry_confidence_line`, `_normalize_entry_confidence_for_operator_summary`, `_correct_final_operator_summary`, `_reason_summary_line`, `_ensure_sentence`, `_noun_predicate_was`, `_first_nonempty`, `_market_context_summary_from_raw` — operator-facing sentence/translation helpers and entry/guard/timeline bullet composition.
Mechanism identical to R3/LOC 008: façade `def` (name/signature/defaults/annotations/docstring) retained, body `return <name>_r3_impl(..., facade=_r3_sys.modules[__name__])`; each former façade global is qualified at its use site as `facade.NAME` (lazy, use-time; no prelude, no `__getattr__`/exec/re-export; Owner imports no façade).

| BEFORE -> AFTER LOC | |
|---|---:|
| `trade_report_markdown_clean.py` | 1,678 -> **1,527** (-151, -9.0 %) |
| `markdown_clean_operator_narrative.py` (new) | 0 -> 264 |
| `trade_report_ai.py` / `trade_story_pipeline.py` | 1,958 / 562 unchanged |
| Three façades | 4,198 -> **4,047** (original 18,743) |

## 3. Verification (isolated clone)
| Gate | Result |
|---|---|
| Moved-body gate (ledger count pinned **86** = 57 + 9 + 20): baseline AST equality after unqualification, exact qualified-name set, no unresolved global, wrapper contract/injection, lazy before/within-call lookup; + symbol-ledger + 436 ABI tests | **459 passed** |
| Independent AST: 436 baseline defs, 0 ABI violations; import cycles 0; no Owner->façade import; Owner 264 <= 350 | pass |
| Differential vs baseline `ba6618d` (guarded recorder, same 51 test files incl. Markdown byte goldens and mock-LLM prompt/retry/timeout/fallback tests) | 625 passed/1 skipped in both trees; outcomes identical; **99,690 vs 99,690 calls, 99,689 identical** (1 = known wall-clock `latency_ms` record); **20/20 moved functions exercised** |
| Focused regression: all `tests/*p152*.py` + 42 consumer files + patch-notes sync + Guard 006 tests | **1,142 passed, 1 skipped** (symlink privilege), production-path write banner 0 |
No test was weakened/deleted; only the pinned moved-symbol count changed 66 -> 86.

## 4. Open / not run
- Real frozen Markdown/JSON/JSONL and LLM before/after parity BLOCKED / NOT RUN; full native pytest not rerun; `controlled_mock_lanes` isolation OPEN.
- Façade size SIZE_DEFERRED (AI 1,958 / Markdown 1,527 / Story 562); numbered `bodies_01..05` cohesion OPEN.
- Next ranked: AI maps (-69), Story maps (-64), Markdown memory/policy (-65, higher risk).
- Codex independent audit pending; P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED; no main merge.
