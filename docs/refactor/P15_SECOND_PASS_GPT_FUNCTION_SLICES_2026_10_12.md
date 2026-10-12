# P1.5 Second Pass — GPT function-level cut plan (Reporter excluded)
**Pinned source:** 1f7add2b0f9b5a33399da27edcdd2f390bdf911b. Design / not code. Ranges refer to actual source lines in this SHA. A range is an **analysis window**, not permission to blindly copy whole lines: AST/local captures, closures, early returns, statement order and exceptions must be verified. New Owner names below are proposed destinations, not existing files.

## 1. Function triage matrix
KEEP means a useful stable boundary; SPLIT means specific internal segments need ownership extraction; MOVE means pure existing helper body should move to canonical owner if not already there; REVIEW means consumer/effect evidence insufficient; SAFETY_LOCK means preserve body/ordering until independent fixtures. **DELETE: none proven. MERGE: none authorized.**

| Source / symbol | Approx line range and LOC | Decision | Target responsibility and non-negotiable proof |
|---|---|---|---|
| graphs/nodes/monitor_node.py::monitor_node | 961–3595, 2,635 | SPLIT P0 | entry cascade, exit policy, intent, state views; exact state/event order |
| same::_evaluate_monitor_entry_candidate | 301–960, 660 | SPLIT P0 | context, minute signal, sizing/cost/quant evidence, rank-1 probe state isolated |
| libs/runtime/intraday_monitor_signals.py::evaluate_intraday_entry_signal | 2379–3608, 1,230 | SPLIT P0 | candle facts, feature scoring, gate/reason assembly; preserve single policy-frame application |
| libs/runtime/exit_policy.py::evaluate_exit_policy | 370–1604, 1,235 | SPLIT P1 | pure condition breakdown; no trigger/hold precedence drift |
| libs/runtime/monitor_strategy_frame.py::apply_exit_policy_strategy_frame | 520–900, 381 | SPLIT_REVIEW | policy translation only; never reapply twice |
| libs/runtime/monitor_minute_ohlcv.py::_ensure_monitor_minute_ohlcv_for_symbol | 300–694, 395 | REVIEW / READ_ONLY | separate cache decision from loader only after source/freshness proof |
| graphs/nodes/scanner_node.py::scanner_node | 709–2653, 1,945 | SPLIT P0 | candidate source, score loop, stable rank, selected state, evidence |
| libs/runtime/scanner/candidate_selection.py::resolve_scanner_candidates | 350–455, 106 | KEEP | canonical candidate source adapter |
| same::build_kiwoom_candidates | 176–349, 174 | KEEP | Kiwoom pool provider, not rank authority |
| graphs/nodes/strategist_node.py::strategist_node | 3440–5145, 1,706 | SPLIT P1 | context and deterministic projections; preserve LLM invocation |
| same::_run_strategist_frame_llm | 2361–2710, 350 | SAFETY_LOCK | model/prompt/timeouts/retries/call-count and parser |
| same::_build_compact_strategist_llm_payload | 1875–2206, 332 | SAFETY_LOCK | prompt/size/token parity |
| same::_build_strategist_llm_messages | 1072–1348, 277 | SAFETY_LOCK | prompt construction |
| graphs/commander_runtime.py::_build_commander_decision | 1756–2614, 859 | SPLIT P0 | snapshot, preflight/shadow, cache refresh, decision, projection |
| same::_resolve_commander_behavior_policy | 514–1255, 742 | SPLIT P0 | precedence reads, normalization, policy output |
| same::_assess_open_position_commander_override | 3327–3765, 439 | SPLIT P1 | position snapshots, carry/review assessment, result |
| same::_attach_commander_applied_policy | 1276–1673, 398 | SPLIT P1 | provenance/merge projection with existing state owner |
| same::_run_commander_runtime_impl | 4383–4682, 300 | KEEP / SEQUENCER | current graph, ownership, phase ordering |
| same::_run_integrated_chain_impl | 4062–4293, 232 | KEEP / SEQUENCER | current integrated sequence |
| apps/operator_ui/data_access_core.py::_build_operator_brief_sections | 1376–2223, 848 | SPLIT P0 | canonical trade facts, evidence sections, ordered payload |
| same::_render_operator_brief_markdown | 3373–4024, 652 | SPLIT P0 | text mapping, deterministic section formatting, fallback |
| same::_load_operator_brief | 2791–3234, 444 | REVIEW / LLM_BOUNDARY | EXISTING chat/retry/finalize; preserve as coordinator pending frozen prompt parity |
| same::_build_operator_brief_input | 2257–2684, 428 | SPLIT P1 | source read/canonical DTO and compact inputs |
| same::load_overview | 809–1092, 284 | KEEP/REVIEW | existing UI read orchestration |
| same::load_run_detail | 4290–4563, 274 | KEEP/REVIEW | existing UI detail read API |
| libs/risk/supervisor.py::Supervisor | 17–206, 190 | SAFETY_LOCK | sole approval result; do not delegate verdict |
| libs/supervisor/two_phase.py::TwoPhaseSupervisor | 33–87, 55 | SAFETY_LOCK | legacy two-phase approval contract |
| libs/supervisor/intent_state_store.py::SQLiteIntentStateStore | 163–761, 599 | SAFETY_LOCK | database state CAS/transition durability |
| graphs/nodes/decide_trade.py::decide_trade | 1060–1516, 457 | REVIEW / SAFETY_LOCK | authority interface & decisions; no policy semantics moved by default |
| graphs/nodes/update_state_after_execution.py::update_state_after_execution | 1242–1374, 133 | SAFETY_LOCK | state reconciliation after possible broker action |
| libs/runtime/controlled_mock_lanes/coordinator.py::inject_controlled_mock_lane_intent | 281–477, 197 | SAFETY_LOCK | mock test lane and write isolation OPEN |
| graphs/nodes/execute_from_packet.py::execute_from_packet | 2915–4106, 1,192 | SAFETY_LOCK | one ordered submission coordinator |
| same::_normalize_execution | 2719–2901, 183 | SAFETY_LOCK | BrokerOutcome/UNKNOWN provenance |
| same::_evaluate_open_order_reconciliation_guard | 2046–2195, 150 | SAFETY_LOCK | broker guard result |
| same::_prepare_request | 2593–2718, 126 | SAFETY_LOCK | request fields, price/qty |
| same::_resolve_order_price_for_notional_with_source | 1660–1778, 119 | SAFETY_LOCK | live price source and freshness |
| libs/execution/readiness_evidence.py::record_pre_admission_evidence | 688–759, 72 | SAFETY_LOCK | R6.2 immutable evidence |
| libs/runtime/quant/shadow_candidates.py::build_quant_shadow_candidate_payload | 837–980, 144 | KEEP | read/observation projection; no rank authority |
| libs/runtime/strategy_horizon_feedback.py::build_commander_horizon_policy | 373–497, 125 | KEEP | existing named policy Owner |
| libs/runtime/decision_observability.py::build_monitor_no_trade_surface | 141–307, 167 | KEEP | existing output DTO assembler |
| same::build_entry_blocker_surface | 376–554, 179 | KEEP | existing blocker projection |
| apps/operator_ui/data_access_brief_monitor_notes.py::_brief_build_stop_policy_trace_r3_impl | 11–69, 59 | KEEP/RENAME_REVIEW | existing compatible section formatter |
| Existing 5 additive runtime alias modules | Wave C created | KEEP | existing canonical/legacy import and CLI entrypoints |

## 2. Monitor — precise staged cut order
**M0 baseline fact:** monitor_node owns state mutations at lines 1545–1550 (entry cooldown, selected, scanner snapshot/cascade), 1910–1913 (exit confirm/sell cooldown/pending lock/previous qty), 2061–2062 (intents and monitor), 2333–2358 (output/entry/exit/sizing), 2585–2693 (posture/threshold/transitions/no-trade/handoff/blockers), 2874–3258 (decision detail/evaluation), 3583–3587 (quant shadow) and final artifact/log. The first state mutation in the entry helper includes opening_rank1_controlled_probe at 926.

### M1 — _evaluate_monitor_entry_candidate (301–960)
| Analysis window | Reads/calls seen in source | Proposed pure/read Owner | Must stay in orchestrator |
|---|---|---|---|
| 323–421 | selected/position map/pending buys, strategist sizing policy, cooldown, memory bias, Commander control | libs/runtime/monitor/entry_context.py: build_entry_candidate_context(view) -> EntryContextDraft | original policy merge precedence, any stateful minute data operation |
| 422–570 | minute OHLCV load, ETF deviation, evaluate_intraday_entry_signal, trace and sizing inputs | libs/runtime/monitor/entry_evidence.py: build_entry_signal_view(signal, quote, minute_meta, policy) -> EntryEvidenceView | _ensure_monitor_minute_ohlcv_for_symbol invocation and failure timing |
| 571–667 | sizing, directional edge, cost, quality, quant factor/decision/enforcement | libs/runtime/monitor/entry_quality_projection.py: summarize_entry_constraints(evaluated_snapshots) -> dict | original sizing/guard evaluation order and passed values |
| 668–825 | Commander rail, risk-off defensive observe, reentry check, entry_guard and rank-1 authority input | libs/runtime/monitor/entry_guard_evidence.py: project_entry_guard_facts(...) -> dict | guard decision and precedence, no new hard veto |
| 826–937 | probe observations/evaluation, state opening_rank1_controlled_probe and return payload | libs/runtime/monitor/entry_probe_view.py: project_opening_probe_evidence(...) -> dict | load/record probe I/O, exact state mutation at 926, return at 937 |

Note: candidate helper is NOT pure as a whole. Do not move it wholesale or inject a broker handle. New Owners can only format/copied facts computed by existing calls.

### M2 — monitor_node (961–3595)
| Analysis window | Responsibility | Proposed destination | Contract |
|---|---|---|---|
| 969–1170 | entry/portfolio/strategy context, policy contract, watchlist refresh | monitor/entry_cycle_context.py (pure snapshot subview only) | preserve original state refresh and record_raw_input |
| 1171–1552 | initial selected candidate, rank-1 and runner-up cascade, intent selection, entry cooldown map | monitor/entry_cascade_projection.py (evidence only) | no changing selected/intent ordering; state writes at 1545–1550 stay |
| 1553–1728 | exit selected symbol, monitor frame, policy, carry decision | existing monitor_exit modules, add only missing pure view | exit evidence and frame apply once |
| 1729–2061 | same-symbol buy suppression, pending orders, hold/stop/confirm, SELL construction | monitor/exit_decision_projection.py (read-only evidence) | preserve confirm map, pending lock and sell cooldown writes at 1910–1913 |
| 2062–2358 | monitor/monitor_output, sizing, quant result and entry/exit snapshots | monitor/cycle_output_projection.py | generate exact dict but apply state keys at original position |
| 2359–2693 | posture, threshold, handoff and blocker surfaces | reuse libs/runtime/decision_observability.py, no cloned policy | preserve original reference/object/copy ordering |
| 2694–3258 | focus, entry/exit decision detail and evaluation | monitor/cycle_detail_projection.py | textual reason and key order, no changed status |
| 3259–3595 | action decision, events, bridge/trace, shadow/artifact write | monitor/cycle_action_view.py for read DTO only | event sequence, save_quant_shadow_candidates_for_state, write_monitor_artifact stay |

### M3 — signal/exit engines, not just facade
- intraday_monitor_signals.py::evaluate_intraday_entry_signal (2379–3608): 2379–2533 compress candles and choose already-resolved MonitorEntryPolicy **without applying strategy frame twice**; 2534–2688 raw volume/VWAP/deviation feature metrics; 2689–2998 score and explanatory facts; 2999–3153 quality tier and gate descriptions; 3154–3463 structure/policy interpreter/evidence/human guard; 3464–3608 exact return. Proposed Owners under libs/runtime/monitor/signal_features.py, signal_score_projection.py, signal_explanation.py. Keep single public evaluator as orderly owner of triggered/WAIT verdict and policy precedence.
- exit_policy.py::evaluate_exit_policy (370–1604): split only pure chart/pnl/candidate condition and result-interpretation fragments after recording exact guard precedence/early returns; use libs/runtime/monitor_exit/{position_risk,hold_controls,market_enrichment,observability} existing Owners. Core trigger selection stays in one function until stop-loss, take-profit, minimum-hold and trailing replay passes.
- monitor_strategy_frame.py::apply_exit_policy_strategy_frame (520–900): no independent duplicate frame application; only extract stateless mapping construction if evidence proves same applied/default policy. No changed timeframe or threshold.

## 3. Scanner — canonical rank conservation
**S0 state writes:** scanner source-universe L736; candidate pool L1007; scan_results L1789, ranked_candidates L1790, selected L1837, top_stock L1838, scanner_output L1848, risk/scanner_skill/scanner_feature around 2022–2041; ranking evidence L2219–2468, artifact at end.

| Lines | Responsibility | Owner and interface | Frozen boundary |
|---|---|---|---|
| 709–1015 | source eligibility, soft strategist guidance, skill hydration, quote diagnostics, pool reduction | reuse candidate_selection.py, guidance.py, practical_filters.py; candidate_context.py optional | source/fallback order and live equity exclusion; hydration I/O stays node |
| 1016–1188 | candidate features and deterministic defaults | scanner/score_features.py: build_score_feature_inputs(candidate, observed_features, policy) -> copied map | scoring scale, floating order, risk cap and default values |
| 1189–1628 | memory/compatibility/macro score, tactical suitability | scanner/score_policy.py: apply_score_components(current_score, frozen_components) -> score record | use same rounding/clamps, guidance soft not hard |
| 1629–1788 | primary score/confidence/risk stable sorting, Commander overlay, blocker concentration and final selection | scanner/ranking_core.py: project_canonical_rank(prepared_rows, existing_policies) -> ordered rows | **single canonical ranking owner**; no extra sort or change in Python stable tie order |
| 1789–2020 | selected/scan output and repeat guard fields | scanner/selection_projection.py: build_selected_snapshot(ordered_rows, prior, ...)
 | original state-write order, rank carried on selected |
| 2021–2468 | risk field, feature coverage, runner-ups, ranking table, Q9 decision snapshot | reuse output_snapshots.py and output_payloads.py; scanner/rank_evidence.py if missing | Q9 snapshot capture I/O remains node |
| 2469–2653 | events, trace, decision bridge and scanner artifact | original node | exact event/artifact order |

Do not interpret adjusted score as permission to alter top-1 semantics. Fixtures must include equal-score tie, stale quote, missing/NaN features, negative market sentiment, rank-1 opening probe, BUY pending and reentry/avoid_recent cases.

## 4. Commander — policy and decisions
| Function & lines | Slice / proposed Owner | Must stay |
|---|---|---|
| _resolve_commander_behavior_policy 514–663 | existing value resolution, route/phase/context -> commander/policy_inputs.py | source precedence, env/default reads at original locations |
| same 664–963 | route, model/execution profile, stop/size and posture values -> commander/policy_normalizers.py | exact fallbacks, _runtime_float/_coerce_int semantics |
| same 964–1255 | canonical scanner/monitor/execution policy mapping -> commander/behavior_policy_projection.py | result key schema/order and historical settings |
| _build_commander_decision 1756–1897 | snapshots/preflight/risk-off/fast path -> commander/decision_context.py | hard runtime/preflight veto |
| same 1898–1985 | shadow assessment, no-trade, refresh/cache preference -> reuse strategist_cache_decision.py/strategist_refresh_decision.py | no forced fresh LLM decision |
| same 1986–2261 | applied policy, memory policy and overlays -> reuse applied_policy.py, memory policy Owners | advisory cannot become hard order authority |
| same 2262–2516 | deterministic strategy choice, monitor feedback -> commander/decision_rules_projection.py | same rule order/branch guards |
| same 2517–2614 | final commander decision dict -> commander/decision_output.py | exact shape, source priority, reasons |
| _assess_open_position_commander_override 3327–3486 | inventory/position/age source -> commander/open_position_inputs.py | now epoch read and position source |
| same 3487–3646 | carry/review/cooldown/refresh assessment -> reuse carry_review_policy.py + session_assessments.py | same review eligibility and cooldown |
| same 3647–3765 | selected refresh candidate/result + persisted_state mutation | commander/open_position_projection.py (result only) | persisted_state write remains existing owner |
| _attach_commander_applied_policy 1276–1673 | applied-policy merge/provenance/horizon -> reuse applied_policy.py, candidate_watch_policy.py | state field assignment timing and merge precedence |
| _run_commander_runtime_impl 4383–4682 | KEEP sequencing | no extraction simply for LOC |
| _run_integrated_chain_impl 4062–4293 | KEEP sequencing | phase/fast path/executor hook order |

Commander MUST remain deterministic. Its policy projection cannot invoke Strategist LLM, Reporter LLM, Supervisor verdict or broker mutation. Do not move runtime lease, hook, incident recovery or shadow lifetime into a policy Owner.

## 5. Operator UI / Brief (not Reporter)
| Function & lines | Slice | Proposed module | Proof |
|---|---|---|---|
| _build_operator_brief_sections 1376–1501 | canonical trade, Strategist/Scanner/Monitor/Supervisor/Executor/Reporter facts | data_access_brief_facts.py | read-only provenance, no Reporter recompute |
| same 1502–1695 | market/news/selected-rank/source and feature evidence | data_access_brief_market_sections.py | selected rank and textual facts exact |
| same 1696–2015 | monitor/position/exit/watch/guard/entry details | data_access_brief_monitor_sections.py | guard interpretation not changed |
| same 2016–2223 | risk/next step/decision, final section dict | data_access_brief_sections_output.py | section keys/order, missing semantics |
| _build_operator_brief_input 2257–2456 | normalized source extraction and evidence compaction | reuse brief_canonical_input.py/brief_compaction.py | no alternate truth |
| same 2457–2684 | strategist/monitor reasoning and normalized input schema | data_access_brief_input_projection.py | prompt payload exact |
| _load_operator_brief 2791–3234 | KEEP controlled existing LLM orchestration; possible finalize sanitization-only cut | reuse brief_sanitation.py only if frozen request/response parity | existing chat(), retry, errors, elapsed time, dates and fallback unchanged |
| _render_operator_brief_markdown 3373–3555 | nested Korean reason/axis/action/fallback format helpers | data_access_brief_text_rules.py | exact Unicode, every space/newline |
| same 3556–3800 | status, section snapshots, early rendering mode | data_access_brief_render_sections.py | exact status sanitization |
| same 3802–4024 | fallback narratives, metrics, output lines | data_access_brief_render_fallback.py | exact order, trailing newline and language |
| load_overview 809–1092 | KEEP/REVIEW existing UI read API | data_access_core remains facade | routes and read paths unchanged |
| load_run_detail 4290–4563 | KEEP/REVIEW | data_access_core remains facade | no storage side-effect added |

The data_access_core module contains a brief-generation path with LLM chat; do NOT label the entire Operator UI as inherently PURE/read-only. Keep the existing LLM capable path under one explicit allowed adapter and disallow that dependency from facts/renderer modules.

## 6. Strategist — preserve decision LLM boundary
| Lines | Content | Destination / exact constraint |
|---|---|---|
| 3440–3500 | candidates, fallback rank/source | existing context/symbol_read_models.py + candidate_context.py if needed; fallback provider call remains controlled |
| 3501–3605 | global sentiment, theme packet, market/news target setup | existing context/{market_inputs,theme_packet,news_context}.py; state writes remain ordered |
| 3605–3699 | news collector/signal scoring, policy and news context | read provider remains node; context/news_projection.py for already-collected immutable facts |
| 3700–3734 | deterministic news-adjusted candidate score/rerank | policy/candidate_rerank.py; identical float arithmetic and minimum-pool fallback |
| 3735–3890 | themes, regime/playbook/policy seeds, feedback and memory | reuse policy/scan/monitor/exit Owners; no LLM calls |
| 3890–4039 | frame preparation and _run_strategist_frame_llm invocation | EXISTING NODE LLM BOUNDARY KEEP, source/prompt/call semantics locked |
| 4040–4437 | bounded overrides, monitor entry/exit policy, theme/strategy plan | reuse policy/monitor_entry_policy.py, output/commander_context_and_plan.py; exact frame application |
| 4438–4789 | output and graph state fields, strategist_llm status | output/strategy_frame_projection.py builds pure dict; original state apply order preserved |
| 4790–5145 | explanation, trace, events, artifact persistence | reuse output/explanation helper; emit and write stay existing node |

Explicitly SAFETY_LOCK: _run_strategist_frame_llm 2361–2710; _build_compact_strategist_llm_payload 1875–2206; _build_strategist_llm_messages 1072–1348; repair messages/token budget/model profile and parse-failure classification. They can be revisited only with immutable prompt request/response provenance and independent oracle, not just mock output.

## 7. Supervisor / Executor / state backend — no cosmetic split
- Supervisor class libs/risk/supervisor.py 17–206: KEEP SAFETY_LOCK. libs/supervisor/two_phase.py::TwoPhaseSupervisor 33–87: compatibility contract KEEP. libs/supervisor/intent_state_store.py::SQLiteIntentStateStore 163–761 includes DB lifecycle, durable state transitions and CAS semantics: splitting methods purely on file length is prohibited; change only with transaction-level replay.
- graphs/nodes/decide_trade.py::decide_trade 1060–1516: REVIEW/SAFETY_LOCK, as approval/decision boundary may consume Strategist, Scanner and Monitor. Verify actual consumers and guard before considering pure read extraction.
- graphs/nodes/update_state_after_execution.py::update_state_after_execution 1242–1374, _apply_mock_fill 522–671, _build_reasoning_trace_snapshot 1013–1168: keep reconciliation/write authority. Only read-only trace view can be proposed with byte parity.
- graphs/nodes/execute_from_packet.py::execute_from_packet 2915–4106: keep unique ordered coordinator; _normalize_execution 2719–2901, reconciliation guard 2046–2195, _prepare_request 2593–2718, price notional source 1660–1778 all SAFETY_LOCK. Existing submission_dispatched state must not leak out of coordinator.
- libs/execution/readiness_evidence.py::_EvidenceLock 286–455; record_pre_admission_evidence 688–759; require_readiness_evidence_for_order 673–687; libs/execution/intent_execution_owner.py and unknown_quarantine.py: SAFETY_LOCK. No alternate mutation/choke.
- libs/runtime/controlled_mock_lanes/coordinator.py::{inject_controlled_mock_lane_intent,finalize_controlled_mock_lane_submission}: protect mock lane authority and write isolation; full write-audit OPEN.
- safe optional next cut: existing libs/execution/executor_observability.py pure result/trace projection if frozen real-case fixture verifies its import and call ordering. Default defer, not mandatory tranche.

## 8. Smaller Owners and duplicate helpers
The preexisting 20 scanner/27 strategist/25 commander/24 monitor_exit/19 execution Python files are already responsibility-oriented. Their default action is **KEEP**, with dependency/side-effect inspection whenever one receives a new function. Do not re-copy existing pure functions to renamed modules. Existing _to_int/_to_float/_read_json/_make_event_logger repeated tiny helpers are at most ~57 gross LOC; MERGE only if proof shows both semantic/precision equivalence and actual maintenance gain. Wave C AST-identical 114-group/395-def inventory is NOT evidence of safe deletion. Legacy M10/M11 and new canonical naming aliases KEEP, preserve existing state/env names.

## 9. Deliverable contract
Each SPLIT implementation record: source SHA, function + exact AST statement range, before/after local-variable binding map, read-only inputs, output schema, originally observed state writes/events, exception path, monkeypatch seam, proposed Owner, 350-LOC size, and named differential fixture. Do not leave an opaque facade/globals full-power argument to a pure Owner. If the selected segment is inherently effectful, move only its calculation and **leave the effect statement at the original orchestrator boundary**. An UNKNOWN consumer or missing fixture makes the target REVIEW/SAFETY_LOCK, not DELETE.
