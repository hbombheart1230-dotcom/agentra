# P1.5 Second Pass — GPT Owner Interfaces, Guard Matrix and Bulk Delivery Packet
**Source SHA:** 1f7add2b0f9b5a33399da27edcdd2f390bdf911b. **Reporter implementation excluded.** This is a proposed ownership/interface design; all callable signatures and source line ranges must be verified against the pinned code before implementation. Design is not a safety acceptance.

## 1. New Owner contract proposals (no blanket facade capability)
Each proposed Owner below must be a named, narrow concern. FIRST look for an identical canonical responsibility in its existing package; reuse it instead of creating a new module. Names are suggestions for location, not orders to duplicate code.

| Interface proposal (pseudo-Python contract) | Allowlisted inputs | Return / state | Forbidden imports and behavior |
|---|---|---|---|
| monitor.entry_context.build_entry_candidate_context(view) | selected copy, existing-position copy, pending orders snapshot, entry policy, Commander hint, cooldown snapshot | EntryContextDraft (read-only computed facts) | broker/LLM, state assignment, clock, fetch, new veto |
| monitor.entry_evidence.build_entry_signal_view(signal, quote, minute_meta, policy) | already evaluated signal DTO, observed quote and minute metadata | EntryEvidenceView (dict exact original structure) | minute fetch, persist, recompute signal |
| monitor.entry_quality_projection.summarize_entry_constraints(result_parts) | already evaluated sizing/cost/quality/quant factors | copied constraint/evidence DTO | recalculating guard verdict, order sizing authority |
| monitor.entry_guard_evidence.project_entry_guard_facts(results) | existing rail, reentry, guard results | evidence only | hard buy block, rank1 probe persist |
| monitor.entry_probe_view.project_opening_probe_evidence(probe_result) | existing probe observation+verdict | read-only probe summary | load_probe_submissions, record_probe_evaluation, state writes |
| monitor.entry_cascade_projection.build_cascade_evidence(existing_sequence) | exact selected and runner-up evaluations | copied reason/rank evidence | reorder candidates, create new OrderIntent |
| monitor.cycle_output_projection.build_monitor_outputs(existing_facts) | frozen entry/exit/quant/current-position facts | ordered exact monitor_output/entry/exit/sizing dicts | apply patch to State, event writes |
| monitor.cycle_detail_projection.build_monitor_details(existing_facts) | evidence/threshold/posture snapshot | decision_detail and evaluation projection | new trading decisions or status changes |
| monitor.signal_features.compute_signal_features(candles, resolved_policy, quote) | compressed candles, already-resolved policy, observed quote | numeric feature DTO | reapply strategy frame, clock, fetch, gate verdict |
| monitor.signal_explanation.build_signal_explanation(scored, evidence) | already computed decision/feature/signal facts | evidence/labels/metrics in baseline shape | modify triggered/WAIT, attempt LLM |
| scanner.score_features.build_score_feature_inputs(candidate, feature_snapshot, policy) | copied candidate/features, effective score policy | intermediate score operands | market fetch or feature hydration |
| scanner.score_policy.apply_score_components(components, policy) | frozen partial scores + policy | exact numeric score record | environment, random seed, state rank write |
| scanner.ranking_core.project_canonical_rank(rows, overlay) | deterministic scored rows and baseline policy, stable original index | exact ordered rank records | external IO, hidden resort, API |
| scanner.selection_projection.build_selected_snapshot(rank, policy, history) | canonical ranked list + previous-selection readonly state | copied selected/runner-up projection | mutate State or evaluate new veto |
| commander.policy_inputs.resolve_existing_values(applied_policy_view, path_refs) | normalized copied policy/route/phase | precedence facts | getenv outside original provider boundary |
| commander.behavior_policy_projection.build_behavior_policy(effective_values) | already resolved env/overrides and defaults | exact original nested policy mapping | infer new route/approval, LLM |
| commander.decision_context.build_decision_inputs(snapshot) | preflight, fast-path, positions, strategist/shadow observation | view of existing route/risk facts | broker, graph execution, runtime lease |
| commander.decision_rules_projection.project_decision_rules(effective_facts) | existing eligibility, preference, risk flags | deterministic branch facts | changing source priority or role |
| commander.decision_output.build_decision_output(all_facts) | existing policy/decision facts | exact original commander decision dict | mutation, hidden guard |
| operator_ui.data_access_brief_facts.project_canonical_brief_facts(detail) | copied per-agent data and canonical trade read model | read-only OperatorBriefFacts | Reporter truth recalculation, writes, LLM |
| operator_ui.data_access_brief_market_sections.build_market_sections(facts) | selected rank, market/news/quote read DTO | exact section fragment | fetch external data, rank changes |
| operator_ui.data_access_brief_monitor_sections.build_monitor_sections(facts) | baseline Monitor and Supervisor evidence | exact section fragment | new risk approval or recalculation |
| operator_ui.data_access_brief_text_rules.render_brief_phrase(kind, frozen_value) | existing language maps/feature facts | exact Korean string | LLM, filesystem, date dependency |
| operator_ui.data_access_brief_render_sections.render_sections(brief) | frozen brief sections / status / language helpers | Markdown fragment | read report files or change truth |
| strategist.context.news_projection.project_collected_news(news, score) | already read news and computed score | normalized context and evidence | new provider calls, NLU/LLM |
| strategist.policy.candidate_rerank.project_candidate_order(candidates, news_scores, policy) | copied candidates and original policy | same order+reasons | external data, altered min-3 fallback |
| strategist.output.strategy_frame_projection.build_output_snapshot(facts) | already decided regime, playbook, LLM+fallback output | ordered exact output/metadata dict | LLM invocation, state writes, artifact persistence |
| execution.executor_observability.build_execution_trace_view(snapshot) | after-the-fact immutable result and evidence | read-only trace dict | broker/API submit, guard or CAS verdict |

**Use existing Python functions and shapes whenever adequate.** The table is an **interface intent**; it is not authorization to replace 30 stable ABI functions with new DTOs or to change serialized contract versions. For each actual implementation, copy original names/keywords/defaults/return types and field order exactly.

## 2. Privilege dependency allowlist (target)
- monitor pure Owners: allow libs/runtime/monitor*, monitor_exit pure calculators, typing/contracts only; prohibit graphs/nodes, libs/execution, broker, API, LLM, storage. A needed original facade/monkeypatch seam is resolved in the node and the specific value passed in.
- scanner pure Owners: allow scanner calculators and contracts; prohibit libs/execution, libs/risk/supervisor, broker/LLM and storage; no direct market provider.
- strategist context/policy/output pure Owners: prohibit real LLM routing, direct API/broker/execute, persistence, graph node imports; existing LLM helper call stays strategist_node.
- commander pure Owners: prohibit broker, Executor mutation, Supervisor verdict, LLM; canonical existing Commander runtime controls phase and IO.
- UI brief facts/renderers: prohibit LLM, report generator, filesystem writes, market fetching; only the existing _load_operator_brief orchestration path may retain old LLM, and existing explicit artifact saving stays separate.
- Supervisor/Executor: prohibit creation of any new mutation-capable adapter in second pass; read-only views may not import executors/real_executor or intent_execution_owner.
- Tests enforce transitive imports/capability not only direct import strings. Avoid import cycles and misleading indirect re-export privilege.

## 3. How to preserve mutation and monkeypatch semantics
1. For each original giant function, obtain ordered operations with source line, AST node type and reads/writes: State assignments, nested dict mutations, events, artifact writes, providers, clock calls, exceptions, early returns, context managers.
2. Copy only truly pure segments into Owner. Call the Owner at the **same exact position**; evaluate expression arguments at the same time and in the same order. Beware Python keyword-default evaluation and dict insertion order.
3. Keep every side-effectful step in orchestrator and never aggregate delayed writes into an end-of-function patch across observable boundaries. OrderedStatePatch is allowed only for contiguous original writes where no intervening effect/exception/branch exists.
4. Old public/private facade function can delegate but must maintain default args, imported names, resolved globals at use time, and monkeypatch interception. After migration, compare bound callable signatures and patch-at-use scenarios with pinned baseline; do not rewrite tests only to make a broken seam pass.
5. Avoid transferring a module object or entire mutable graph state into a PURE Owner; if absolutely required as a first-pass compatibility shim, explicitly label TEMPORARY_COMPATIBILITY and do not claim least-privilege completion for that slice.
6. When separating an inner nested helper, inspect lexical captures. Do not promote side-effect-bearing closures to global functions or alter nonlocal update ordering without differential evidence.
7. Keep one canonical rank calculator, one runtime owner, one verdict authority, one broker mutation authority.

## 4. Frozen differential fixture matrix
**Fixture identifiers here describe required cases, not claims that these tests already exist.** Codex/Claude must locate real frozen inputs or create deterministic synthetic tests WITHOUT claiming real provenance parity; carry the distinction into evidence.

| Gate | Required cases and asserts | Existing tests worth reusing |
|---|---|---|
| Monitor entry | held symbol/pending BUY/max positions; post-exit cooldown; no/minute OHLCV; stale quote; rank-1 opening probe; quant/quality constraints; with/without memory observation | tests/test_m17_monitor_emits_intent_only.py; test_monitor_candidate_cascade.py; test_intraday_monitor_signals.py; test_monitor_memory_bias.py; test_monitor_minute_ohlcv_resilience.py |
| Monitor exit | flat/open, min hold, stop/take/trailing, closeout, confirmed sell/cooldown, UNKNOWN/pending exit; identical intent order/state | tests/test_m29_3_monitor_exit_policy.py; test_monitor_exit_guard.py; test_monitor_exit_price_freshness.py; test_same_symbol_loss_reentry.py |
| Scanner rank | tie score/confidence/risk; top1 propagation, missing features, guidance, blocker overlays, fallback; byte-identical ranking evidence, same selected | tests/test_scanner_rank_plumbing_fix.py; test_scanner_policy_overlay.py; test_scanner_practical_selection_engine.py; test_scanner_memory_bias.py; test_q9_scanner_quality.py |
| Commander | preflight blocked, cached strategist, monitor-only fast path, open-carry review, closeout, ownership loss, reason/source priority; same path and events | tests/test_commander_contract.py; test_m21_commander_runtime_entry.py; test_m23_4_commander_incident_cooldown_routing.py; test_commander_post_scanner_context.py |
| Operator Brief | every source version fallback, missing/null/empty fields, malformed LLM, language-mixed retry, all Markdown exact bytes including final newline, stable artifact paths | tests/test_run_operator_brief_batch.py and available operator UI/brief tests discovered from tree |
| Strategist | candidate/fallback/news negative filter, preopen, market rail, recent memory, partial/invalid LLM, no-LLM fallback; identical prompt request/response and call count | tests/test_strategist_frame_llm_integration.py; test_strategist_input_quality_risk_off.py; test_strategist_explanation_contract.py; test_m12_strategist_hook.py |
| Supervisor + Executor | approval deny, readiness disabled, duplicate order claim, broker dispatched before exception, outcome UNKNOWN, new owner/generation, post-submit recovery; same submit count and ordering | tests/test_supervisor.py; test_step5b_fix4.py; test_step5c_execution_owner.py; test_step5c_fix5_mutation_failclosed_and_consumer_only.py; test_execution_trace_completeness.py |
| Aliases & temp writes | canonical env precedence; legacy CLI import/usage; only isolated tmp writes, no reports/data in production-shaped roots | tests/test_p155_runtime_naming_aliases.py; test_runtime_entrypoint_import_boundaries.py; test_controlled_mock_lanes.py |

Use tests as named in pinned tree; do not assume the table proves all cases already exist. New tests should target only missing cases. Record identical baseline failures separately; eight Step5B Fix4 EXECUTION_DISABLED failures were independently BASELINE_CONFIRMED. Tests that use yfinance public market data should use a frozen/injected provider for differential determinism.

## 5. Actionable acceptance checklist and STOP rules
For each implementation batch:
- [ ] baseline SHA, pinned exact files/functions and source-line ranges
- [ ] before/after function LOC and total facade LOC (both, to avoid misleading “deletion”)
- [ ] number of moved pure segments and newly introduced Owners <=350 LOC
- [ ] no broad facade-capability injection in any claimed pure Owner
- [ ] import DAG, direct/transitive authority and writes audit
- [ ] original return/error/default/order/call signatures and monkeypatch seams preserved
- [ ] strict differential: ordered rank/intent/State/event, UI Markdown/JSON, LLM request count and effect order
- [ ] no actual broker/LLM, no production writes
- [ ] newly failed tests 0; baseline failures explicitly established under same environment
- [ ] UI JSON/MD patch-note sync and concise daily patch after material code changes
- [ ] success pytest scratch cleaned; failure evidence retention bounded
- [ ] mark anything lacking immutable baseline proof BLOCKED or DEFERRED, never claim PASS
- [ ] one consolidated wave-level Codex audit after all S1–S6 (stop immediately for suspected authority leak)
- [ ] no main merge, production deployment, or P1.5 final acceptance before Wave D

## 6. Bulk Claude implementation handoff
Read only this document, the GPT Master Design, GPT Function Slices, CURRENT.md and changed source files. Reuse prior Wave A–C gates and existing Owners. Avoid re-reading completed work orders or rewriting old design documentation. Execute S1→S6 in reusable isolated dev, checking critical guards at each risk boundary; do not ask for human approval every 100 lines. If one slice is blocked, proceed to independent unrelated low-risk slice; note exact obstacle and next fixture requirement. Do not fill the repository with speculative Owners or rename legacy files without consumer evidence. Finish with one concise evidence matrix and a pinned SHA for Codex; if not all P0 functions materially improve, report PARTIAL rather than saying SECOND_PASS_COMPLETE.

**Important: this design is a spec, not an instruction to start implementation without the user's subsequent activation.** No CI green status or real fixture parity is asserted here.
