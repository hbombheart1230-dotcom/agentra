# P15-R3-FACADE-LOC-MAX-REDUCTION-008 — Claude implementation evidence

Branch `refactor/p1.5` only. Start HEAD `6760ab4abaf1a9bc6ec168f6c1daf9a727e19dfb`. Isolated clone `C:\AgentraEvidence\r3_seam_clone`, project venv, scrubbed env, `PYTHONDONTWRITEBYTECODE=1`. Live `C:\Agentra` and Q12 worktrees untouched; no real LLM/broker, no production writes.

## 1. Measurement (Guard-006 SHA family; AST classification of every façade top-level def)
| Façade | LOC | imports | non-delegating impl | thin delegations | dependency maps (`*_deps`) |
|---|---:|---:|---:|---:|---:|
| `trade_report_ai.py` | 1,958 | 211 | 577 LOC / 47 defs (≈13 LLM/prompt/retry/timeout/fallback safety-locked entrypoints) | 764 LOC / 132 | 77 |
| `trade_report_markdown_clean.py` | 1,891 | 183 | 645 LOC / 71 defs (all <=19 LOC) | 454 LOC / 124 | **242 LOC / 9 maps** |
| `trade_story_pipeline.py` | 562 | 146 | 2 LOC / 1 | 258 LOC / 41 | 75 |
Delegations are ABI surface (signature + one return) and cannot shrink without dropping contract; imports are patch surfaces. The only large pure-glue block that carries no public contract is the **dependency-map factories**, which build call-time name->global dicts for existing Owners.

Candidate slices evaluated by dry run (net façade change, owner LOC): Markdown dependency maps **-213 (268)**; operator narrative/translation builders -93 (159); memory/policy phase lines -65 (136); numeric/format primitives -55 (150, very hot, 17 tiny fns); time/duration -38; canonical-monitor resolution -41. AI/Story maps (-77 / -75 potential) and the AI deterministic helpers are next candidates; AI LLM-locked entrypoints (`build_ai_trade_report`, `build_separated_ai_trade_report`, `build_trade_summary_report`, `_router_chat_with_hard_timeout`, repair/concise-message builders, `_failure_report`, `_fallback_report`, `_merge_trade_report_candidate`, language/parse meta) deliberately untouched.

## 2. Implemented slice (one cohesive group)
Moved all 9 Markdown-clean dependency-map factories to `libs/reporting/trade_report/markdown_clean_dependency_maps.py` (responsibility-named, **268 LOC**, no numbered catch-all): `_markdown_diagnostics_deps`, `_summary_render_deps`, `_summary_input_deps`, `_strategy_memory_deps`, `_markdown_entry_visibility_deps`, `_markdown_signal_deps`, `_markdown_translation_deps`, `_markdown_truth_surface_deps`, `_markdown_strategy_deps`.
- Façade keeps every `def` name/signature; each body is now `return <name>_r3_impl(facade=_r3_sys.modules[__name__])`.
- In the Owner each former façade global is qualified at its use site as `facade.NAME` (same scheme as the 57 R3 bodies): the dict is still built when the map function is called, so values are the **current** façade globals exactly as before (use-time; monkeypatching before a call or from a callback is honoured). No `__getattr__`, exec, wildcard or re-export tricks; Owner imports nothing from façades.
- **`trade_report_markdown_clean.py`: 1,891 -> 1,678 LOC (-213, -11.3 %).** Sum of three façades 4,411 -> 4,198. Original 18,743 -> 4,198.

## 3. Verification (isolated clone)
| Gate | Result |
|---|---|
| Moved-body gate `tests/test_p152_r3_moved_bodies.py` (now 66 symbols: 57 + 9 maps; count pinned exactly) incl. AST-equality-after-unqualification vs baseline `ba6618d`, exact qualified-name set, lazy within-call lookup, façade wrapper contract | pass (with ledger + ABI tests: 358 passed) |
| New test: every map entry is the **current** façade global (patch each referenced global -> map returns the patched object) | pass, 9/9 maps |
| 436 ABI (independent AST: 436 baseline defs, 0 violations); import cycles in `libs.reporting` 0; no Owner imports a façade; Owner <=350 (268) | pass |
| Recorded differential vs baseline `ba6618d` with the guarded Guard-006 recorder (same 51 test files; 625 passed/1 skipped both trees) | outcomes identical; **96,565 vs 96,565 calls, 96,564 identical**; the 1 difference is the known wall-clock `latency_ms` record; **all 9 maps exercised (49,473 calls)** |
| Focused regression: all `tests/*p152*.py` + 42 façade-consumer files + patch-notes sync (incl. Markdown byte goldens, mock-LLM prompt/retry/timeout/fallback tests, Guard 006 tests) | **1,041 passed, 1 skipped** (Windows symlink privilege), production-path write banner 0 |
No test was weakened or deleted; the only test edits are the pinned count 57 -> 66 and the added dependency-map test.

## 4. Open / not run
- Real frozen Markdown/JSON/JSONL + LLM prompt/retry/timeout/call-count parity: **BLOCKED / NOT RUN** (no immutable authorized snapshots).
- Full native pytest not rerun (task rule); `controlled_mock_lanes` write isolation OPEN; façade size still SIZE_DEFERRED (AI 1,958 / Markdown 1,678 / Story 562); named-Owner cohesion debt for `bodies_01..05` OPEN.
- Residual semantic note (unchanged from R3): moved bodies are no longer byte-identical to baseline; the only difference is `facade.` qualification, proven by the gate.
- Next best candidates (not done): Story + AI dependency maps (~-75 each), Markdown operator-narrative builders (-93), memory/policy phase lines (-65).
- Codex independent audit pending; P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED; no main merge.
