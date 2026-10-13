# P1.5 canonical target architecture — actual Git tree + Reporter status

> **Current Git actual-tree reconciliation (2026-10-13):** [P15_ACTUAL_TREE_LARGE_FUNCTION_DELETE_AUDIT_2026_10_13.md](P15_ACTUAL_TREE_LARGE_FUNCTION_DELETE_AUDIT_2026_10_13.md). The [P]/[E] markers below describe the older inspected SHA; second-pass files under Monitor, Commander, Scanner and Operator UI now exist. The latest audit also discovers giant cross-agent output builders and a potential shadowed rendering function. No deletes are approved.

> **Third Pass source-verified design (2026-10-13):** [P15_THIRD_PASS_GPT_REPORTER_INCLUSIVE_DESIGN_2026_10_13.md](P15_THIRD_PASS_GPT_REPORTER_INCLUSIVE_DESIGN_2026_10_13.md). Following the user-supplied Codex PASS_WITH_FINDINGS for the parity P1 fix, Reporter pure read-model and guarded bundle-runtime work, second-pass Owner facade/tuple debt, and remaining agent giants precede Wave D. Older Reporter exclusion was only for the completed S1-S6 second pass.

> **Authoritative delivery order (2026-10-13):** [P1.5 pre-Wave-D structural closure](P15_PRE_WAVE_D_STRUCTURAL_CLOSURE_ORDER_2026_10_13.md). After 2nd-pass S1–S6 and Codex checkpoint, GPT re-examines **all seven agents including Reporter**. Claude performs third-and-later bulk decomposition **including Reporter**, Codex performs structural closure audit, and **only then Wave D**. References below implying Reporter follow-up occurs after Wave D are superseded; Reporter is excluded from the initial S1–S6 pass *only*.

**Status:** ARCHITECTURE TARGET (not yet implemented) · **Reporter:** FIRST_PASS_WITH_DEBT, second-pass code EXCLUDED · **Inspected HEAD:** 60dfa1c4cd7ca62d127251a4051b3404a86f6932 · **Date:** 2026-10-13 KST.
**Authority:** this target tree fixes architectural intent for the Claude bulk second pass, but not a permission to delete or rename existing modules. GPT designs; Claude implements; Codex audits; GPT/user decide acceptance.

**Legend:** [E] = physically EXISTING at inspected HEAD; [P] = PLANNED module/owner candidate, not yet on Git; [L] = existing locked safety/compatibility boundary. This is a representative **architecture tree**, NOT an exhaustive literal listing of all repository files. Proposed modules may be absorbed by a current canonical Owner if that creates better cohesion. Existing unlisted files remain.

## A. Agentra top level and seven agents

~~~
Agentra/
├── graphs/                                         [E] LangGraph/ordered orchestration
│   ├── trading_graph.py                            [L] graph order
│   ├── commander_runtime.py                        [E] Commander runtime/fast paths
│   ├── nodes/
│   │   ├── commander_node.py                       [E] Commander node
│   │   ├── strategist_node.py                      [E] Strategist + its existing LLM path
│   │   ├── scanner_node.py                         [E] Scanner candidate and rank facade
│   │   ├── monitor_node.py                         [E] Monitor; intent-only
│   │   ├── reporter_node.py                        [E] Reporter thin bundle entry
│   │   ├── decide_trade.py                         [L] decision bridge
│   │   ├── executor_node.py                        [E] Executor graph entry
│   │   ├── execute_from_packet.py                  [L] single ordered submission coordinator
│   │   └── update_state_after_execution.py         [L] order state reconciliation
│   └── pipelines/
│       ├── live_cycle.py                           [E] canonical additive alias
│       ├── runtime_tick.py                         [E] canonical additive alias
│       ├── eod_report.py                           [E] canonical additive alias
│       └── m10_*, m11_*, m13_*                      [L] legacy compatibility (selected)
│
├── libs/
│   ├── runtime/
│   │   ├── commander/                               [E] Commander small Owners
│   │   ├── strategist/                              [E] context/policy/LLM helpers/output
│   │   ├── scanner/                                 [E] candidates/features/selection/rank
│   │   ├── monitor/                                 [E] entry-side pure Owners
│   │   ├── monitor_exit/                            [E] exit-side policy Owners
│   │   ├── intraday_monitor_signals.py              [E] giant signal function / public API
│   │   ├── exit_policy.py                           [E] giant exit function / public API
│   │   ├── decision_observability.py                [E] read-only views
│   │   ├── controlled_mock_lanes/                   [L] isolation NOT YET PROVEN
│   │   └── entrypoints/                             [E] canonical/legacy live entrypoints
│   ├── risk/supervisor.py                           [L] sole Supervisor verdict authority
│   ├── supervisor/
│   │   ├── two_phase.py                             [L] existing approval compatibility
│   │   ├── intent_store.py                          [L] intent persistence
│   │   └── intent_state_store.py                    [L] SQLite CAS durability
│   ├── execution/                                   [L] readiness/admission/broker single owner
│   └── reporting/                                   [E] Reporter core + other research/UEF
│
├── apps/operator_ui/                               [E] UI / brief / read-model
├── config/                                         [E] configs
├── scripts/                                        [E] CLIs and diagnostics
├── deploy/                                         [E] deploy and Docker
├── tests/                                          [E] contract/regression/safety
├── docs/
│   ├── refactor/                                   [E] source of truth for P1.5
│   ├── daily_patch/                                [E]
│   └── trading_agent_patch_notes_detailed_update/
│       ├── patch_notes.json                        [E] UI-linked
│       └── patch_notes.md                          [E] companion
└── data/                                           [E] existing runtime data
~~~

The seven roles are **Commander, Strategist, Scanner, Monitor, Supervisor, Executor, Reporter**. The real Supervisor authority is in libs/risk/supervisor.py and libs/supervisor/*; **graphs/nodes/supervisor_node.py does not exist** at the inspected HEAD. decide_trade is an existing bridge, not an invented eighth role.

## B. Target detailed Owners for second pass (Reporter EXCLUDED from modifications)

### B1. Commander

~~~
libs/runtime/commander/
├── applied_policy.py, fast_path_policy.py           [E]
├── carry_review_policy.py, entry_control_policy.py  [E]
├── candidate_watch_policy.py, event_projection.py   [E]
├── position_projection.py, session_assessments.py   [E]
├── fast_paths.py, shadow_runtime.py                 [E]
├── policy_readers.py, policy_surface.py             [E]
├── output_frames.py, strategist_cache_decision.py  [E]
├── policy_inputs.py                                [P; prefer reuse policy_readers.py]
├── policy_normalizers.py                           [P]
├── behavior_policy_projection.py                   [P; prefer reuse policy_surface.py]
├── decision_context.py, decision_rules_projection.py [P]
└── decision_output.py, open_position_inputs.py     [P; prefer reuse existing projection owners]
~~~

Commander runtime still owns route, phase, transitions, fast-path order and preflight. Pure policy Owners cannot import Executor mutation, broker, Supervisor verdict or LLM.

### B2. Strategist

~~~
libs/runtime/strategist/
├── context/
│   ├── market_inputs.py, news_context.py            [E]
│   ├── theme_packet.py, theme_strength.py           [E]
│   ├── memory.py, symbol_read_models.py             [E]
│   └── news_projection.py                           [P]
├── policy/
│   ├── scanner_policy.py, monitor_entry_policy.py   [E]
│   ├── exit_and_defaults.py                         [E]
│   └── candidate_rerank.py                          [P]
├── llm/
│   ├── stage_reviews.py, adjustment_directives.py   [E]
│   └── override_normalization.py                    [E]
└── output/
    ├── commander_context_and_plan.py               [E]
    ├── strategy_scores_and_summary.py               [E]
    └── strategy_frame_projection.py                 [P]
~~~

The existing LLM orchestration, prompt, model, timeout, retry and parser stay frozen in strategist_node.py; do not duplicate LLM authority inside pure Owners.

### B3. Scanner

~~~
libs/runtime/scanner/
├── candidate_selection.py, scoring_inputs.py        [E]
├── guidance.py, compatibility.py, repeat_guard.py   [E]
├── candidate_risk.py, practical_filters.py          [E]
├── market_representative_guard.py                   [E]
├── output_payloads.py, output_snapshots.py          [E]
├── score_features.py, score_policy.py               [P]
├── ranking_core.py                                  [P; single canonical rank owner]
└── selection_projection.py                          [P; preserve selected rank propagation]
~~~

Tie-break, rank-1, score precision, sorting order, Commander overlay, source selection, state writes and emitted snapshots are invariant.

### B4. Monitor

~~~
libs/runtime/monitor/
├── entry_carry_guard.py                             [E]
├── entry_context.py, entry_evidence.py              [P]
├── entry_quality_projection.py                      [P]
├── entry_guard_evidence.py, entry_probe_view.py     [P]
├── entry_cycle_context.py                           [P]
├── entry_cascade_projection.py                      [P]
├── exit_decision_projection.py                      [P]
├── cycle_output_projection.py, cycle_detail_projection.py [P]
├── signal_features.py, signal_score_projection.py   [P]
└── signal_explanation.py                            [P]

libs/runtime/monitor_exit/
├── hold_controls.py, position_risk.py               [E]
├── price_resolution.py, order_lifecycle.py          [E]
├── overnight_carry.py, policy_config.py             [E]
├── observability.py, selected_snapshot.py           [E]
└── ... existing 24 Python modules retained

libs/runtime/intraday_monitor_signals.py             [E; split pure internals]
libs/runtime/exit_policy.py                          [E; keep trigger precedence]
~~~

Monitor emits OrderIntent only. Keep all entry/exit guards, cooldowns, size, post-exit and rank-1 controlled probe semantics unchanged. Signal policy must not be applied twice.

### B5. Supervisor and Executor — intentionally protected

~~~
libs/risk/supervisor.py                             [L] approval / deny
libs/supervisor/two_phase.py                         [L]
libs/supervisor/intent_store.py                      [L]
libs/supervisor/intent_state_store.py                [L] Step5C SQLite CAS
libs/execution/
├── execution_readiness.py                           [L]
├── readiness_evidence.py                            [L] R6.2
├── executor_observability.py                        [E] pure result views
├── intent_admission.py, intent_identity.py          [L]
├── intent_execution_owner.py                        [L]
├── guards/broker_mutation.py                        [L]
├── guards/unknown_quarantine.py                     [L]
└── executors/{base,factory,mock_executor,real_executor}.py [L]
~~~

The sole broker-mutation choke is preserved, with admission/guard/CAS/UNKNOWN/BrokerOutcome and submission_dispatched ordering. Executor's 1,192-line coordinator remains SAFETY_LOCK until immutable real-case fixtures can prove safe decomposition.

## C. Reporter: VERIFIED AS-IS, not “fully refactored”

**Direct entry proven from source:** graphs/nodes/reporter_node.py → libs/reporting/intraday_trade_reports.generate_intraday_trade_artifacts. The thin Reporter node forces live intraday reporting into bundle mode, records requested mode and delegates. The underlying **intraday_trade_reports.py is still ~1,850 lines**, containing bundle synchronization, queue/process handling, state cache invalidation and report artifact IO. It is not merely a thin pure output function.

The following tree shows *related physical modules by responsibility*; nesting below intraday_trade_reports is explanatory and does not assert that every edge is a literal Python import:

~~~
graphs/nodes/reporter_node.py                        [E] thin Reporter graph node
libs/reporting/
├── intraday_trade_reports.py                        [E] bundle runtime/queue/process/IO (large)
├── trade_story_pipeline.py                          [E] public compatibility facade
├── trade_story_pipeline_story_assembly.py           [E] story composition
├── trade_story_assembly_parts/                      [E]
│   ├── lifecycle_bundle.py, lifecycle_evidence.py
│   ├── lifecycle_human.py, reasoning_provenance.py
│   ├── report_seeds.py, timeline.py
│   └── ... other existing Owners
├── trade_story_human_parts/                         [E]
│   ├── monitor_context.py, monitor_traces.py, scanner_reason.py
│   └── ... other existing Owners
├── trade_story_facade_parts/                        [E] compatibility helpers
│
├── trade_report_ai.py                               [E] existing public AI report facade
├── trade_report_ai_llm.py                           [E] reporting LLM helper
├── trade_report_ai_prompting.py                     [E] prompts
├── trade_report_ai_deterministic.py                 [E] deterministic fallback
├── trade_report_markdown_clean.py                   [E] public Markdown facade
├── trade_report/
│   ├── service.py                                   [E] compatibility service
│   ├── services/{ai_report,trade_summary}.py         [E] named services
│   ├── sections.py                                 [E] compatibility surface
│   ├── section_parts/                              [E] section building Owners
│   │   ├── entry_decision.py, market_context.py
│   │   ├── scanner_selection.py, strategist.py, execution_quality.py
│   │   └── ... 
│   ├── section_seed_parts/                         [E] per-agent evidence seed
│   ├── summary_input_parts/                        [E] source/evidence inputs
│   ├── summary_render_parts/                       [E] Markdown section rendering
│   ├── markdown_clean_parts/                       [E] Markdown normalization
│   ├── markdown_signal_parts/                      [E] entry/exit evidence strings
│   ├── ai_facade_parts/                            [E] topic-specific deterministic helpers
│   ├── ai_facade_r3_parts/                         [E] bodies_01..05 technical debt
│   └── markdown_clean_r3_parts/                    [E] bodies_01..05 technical debt
│
├── daily_report.py, daily_report_generator.py       [E] scheduled/daily reports
├── daily_report_runtime/                           [E] build_model/freshness/markdown
├── operator_period_summary.py                      [E] periodic operator summary
├── operator_period_summary_parts/                  [E] summary Owners
├── operator_visibility.py                          [E] visibility/readouts
├── operator_visibility_parts/                      [E] visibility Owners
│
├── evaluation/                                      [E] UEF, forward/effectiveness validation
├── baseline_btc_woori_tech/                        [E] BTC ↔ 우리기술투자 research
├── baseline_samsung_hynix/                         [E] US semiconductor / Korea research
├── alpha_research_board/                           [E] alpha research
└── opening_rank1_shadow/                           [E] controlled rank-1 research
~~~

**Very important:** libs/reporting/ has **466 Python files** at inspected HEAD, but includes independent Q10/Q12 hypothesis analysis, Alpha Board and **evaluation/ (135 Python files)** as well as Reporter trade reporting and daily readouts. Never present all 466 as “Reporter agent files” or assert the folder was newly created by P1.5 refactoring.

**Documented split completed:** Wave A A1 moved 55 deterministic Reporting bodies to 10 additional Owners; previous P1.5.2 passes had already created multiple named section/story/AI/Markdown Owners. Reporter does have real modular parts; prior diagram's section/services/summary folders mostly **already exist**, not proposed future folders.

**Reporter remaining debt at Wave C:**
- Public facades still physically present: trade_report_ai.py ~1,657 LOC; trade_report_markdown_clean.py ~1,326 LOC; trade_story_pipeline.py ~499 LOC.
- Intraday report bundle runtime ~1,850 LOC remains large and IO/queue sensitive.
- Reporting ABI 436 symbols, 330 UNKNOWN consumer-reachability; numbered body Owners exist; DELETE/MERGE proof absent.
- Actual frozen report Markdown/JSON/JSONL parity and LLM prompt/model/timeout/retry/call-count parity **BLOCKED/NOT RUN**.
- P1.5.2 is **FIRST_PASS_WITH_DEBT / not FINAL_ACCEPTED**; no report runtime rewrite in current second pass.
- Reporter follow-up only after evidence-backed consumer parity and separately approved scope. Wave D must independently validate existing reports even though their code is unchanged this pass.

## D. Operator UI: distinct from Reporter

~~~
apps/operator_ui/
├── main.py, data_access.py, data_access_core.py     [E] routes/facade/source
├── data_access_brief.py                            [E]
├── data_access_brief_canonical_input.py            [E]
├── data_access_brief_compaction.py                 [E]
├── data_access_brief_fallback.py, data_access_brief_sanitation.py [E]
├── data_access_brief_prompts.py                    [E]
├── data_access_brief_monitor_notes.py              [E]
├── data_access_reports.py                          [E]
├── data_access_run_read_models.py                  [E]
├── data_access_trade_read_models.py                [E]
├── data_access_brief_facts.py                      [P]
├── data_access_brief_market_sections.py            [P]
├── data_access_brief_monitor_sections.py           [P]
├── data_access_brief_input_projection.py           [P]
├── data_access_brief_text_rules.py                 [P]
├── data_access_brief_render_sections.py            [P]
└── data_access_brief_render_fallback.py            [P]
~~~

UI facts/renderers are readonly; _load_operator_brief currently has **existing LLM chat/retry**, so do not call the whole UI read-only. Artifact writes stay at explicitly authorized persistence sites. No parallel source-of-truth recreation: Reporter facts are read, not independently recomputed.

## E. Frozen ownership graph / invariant

~~~
Commander [route/phase]
   ├── Strategist [market + deterministic policy; existing LLM only]
   ├── Scanner [single canonical candidate/rank owner]
   └── Monitor [entry/exit intent ONLY]
                ↓
      decision bridge → Supervisor verdict
                              ↓
            execute_from_packet [ordered admission + CAS + guards]
                              ↓
                sole broker mutation owner
                              ↓
            BrokerOutcome + UNKNOWN quarantine

All agents' evidence and traces → Reporter bundle/read models → Operator UI
Existing Operator Brief LLM and artifact writer remain independently controlled
~~~

This conceptual ownership graph DOES NOT authorize changing the actual graph execution order/fast paths. Keep semantics, result schema, state/event write order, monkeypatch and legacy aliases. Reuse existing modules before adding any proposed file. New named Owner <=350 physical LOC; avoid cosmetic wrapper proliferation.

## F. Adoption and evidence

- GPT detailed decomposition: docs/refactor/P15_SECOND_PASS_GPT_FUNCTION_SLICES_2026_10_12.md
- Owner I/O and guards: docs/refactor/P15_SECOND_PASS_GPT_OWNER_CONTRACTS_AND_GATES_2026_10_12.md
- Master: docs/refactor/P15_SECOND_PASS_GPT_MASTER_DESIGN_2026_10_12.md
- Wave A implementation: docs/refactor/work_orders/evidence/P15-FAST-TRACK-WAVE-A-CLAUDE-014.md
- Wave A independent audit: docs/refactor/work_orders/evidence/P15-FAST-TRACK-WAVE-A-CODEX-AUDIT-015.md
- Wave C wrapper inventory: docs/refactor/p1_5_wrapper_cleanup_inventory_2026_10_12.json
- Reporter actual entry: graphs/nodes/reporter_node.py and libs/reporting/intraday_trade_reports.py

Claude S1 Monitor → S2 Scanner → S3 Commander → S4 Operator UI → S5 Strategist → S6 low-risk Supervisor/Executor, all one second-pass delivery with a single integrated Codex audit. Then Wave D full regression, Docker mocked, UEF, exact frozen report and LLM parity, executor real fixtures and mock-lane isolation. No main merge, live deployment, final acceptance or ZIP.

**Maintenance rule:** When new modules actually land, update this [E]/[P] map in the same code commit; never mark proposed paths as implemented before they exist. Update UI-linked patch_notes.json + patch_notes.md and concise daily patch for meaningful updates.


## G. Current status overlay (T3, verified against the physical Git tree at `bcb83a6`, 2026-10-13)

*The sections above are a historical design snapshot and are intentionally not rewritten.* Machine-readable matrix:
[p1_5_third_pass_t3_ownership_matrix.json](p1_5_third_pass_t3_ownership_matrix.json) (207 modules; classes {'KEEP': 23, 'CANONICAL_OWNER': 139, 'RENAME_CANDIDATE': 30, 'COMPAT_FACADE': 14, 'SAFETY_LOCK': 1}).

### G.1 Packages that now EXIST ([P] -> [E])
- `libs/reporting/reporter_bundle_runtime_parts/` - T2 bundle-runner pure projections (6 modules after the T3 policy split)
- `libs/reporting/trade_memory_projection_parts/` - T1 memory surface projections
- `libs/reporting/trade_read_model_parts/` - T1 read-model projections
- `libs/reporting/trade_report/ai_facade_parts/ (fallback_*, compact_input_*)` - T1 fallback/compact-input projections

### G.2 Every `[P]` marker above, checked against the tree
| Planned path | Actual | Match | Decision |
|---|---|---|---|
| `policy_normalizers.py` | NOT PRESENT | - | [P] keep planned; do NOT create without a genuine responsibility and consumer evidence |
| `decision_context.py` | NOT PRESENT | - | [P] keep planned; do NOT create without a genuine responsibility and consumer evidence |
| `decision_rules_projection.py` | EXISTS | libs/runtime/commander/decision_rules_projection.py | [E] promote marker |
| `news_projection.py` | NOT PRESENT | - | [P] keep planned; do NOT create without a genuine responsibility and consumer evidence |
| `candidate_rerank.py` | NOT PRESENT | - | [P] keep planned; do NOT create without a genuine responsibility and consumer evidence |
| `strategy_frame_projection.py` | NOT PRESENT | - | [P] keep planned; do NOT create without a genuine responsibility and consumer evidence |
| `score_features.py` | NOT PRESENT | - | [P] keep planned; do NOT create without a genuine responsibility and consumer evidence |
| `score_policy.py` | NOT PRESENT | - | [P] keep planned; do NOT create without a genuine responsibility and consumer evidence |
| `entry_context.py` | EXISTS | libs/runtime/monitor/entry_context.py | [E] promote marker |
| `entry_evidence.py` | EXISTS | libs/runtime/monitor/entry_evidence.py | [E] promote marker |
| `entry_quality_projection.py` | EXISTS | libs/runtime/monitor/entry_quality_projection.py | [E] promote marker |
| `entry_guard_evidence.py` | EXISTS | libs/runtime/monitor/entry_guard_evidence.py | [E] promote marker |
| `entry_probe_view.py` | NOT PRESENT | - | [P] keep planned; do NOT create without a genuine responsibility and consumer evidence |
| `entry_cycle_context.py` | EXISTS | libs/runtime/monitor/entry_cycle_context.py | [E] promote marker |
| `entry_cascade_projection.py` | EXISTS | libs/runtime/monitor/entry_cascade_projection.py | [E] promote marker |
| `exit_decision_projection.py` | EXISTS | libs/runtime/monitor/exit_decision_projection.py | [E] promote marker |
| `cycle_output_projection.py` | EXISTS | libs/runtime/monitor/cycle_output_projection.py | [E] promote marker |
| `cycle_detail_projection.py` | EXISTS | libs/runtime/monitor/cycle_detail_projection.py | [E] promote marker |
| `signal_features.py` | EXISTS | libs/runtime/monitor/signal_features.py | [E] promote marker |
| `signal_score_projection.py` | EXISTS | libs/runtime/monitor/signal_score_projection.py | [E] promote marker |
| `signal_explanation.py` | EXISTS | libs/runtime/monitor/signal_explanation.py | [E] promote marker |
| `data_access_brief_facts.py` | EXISTS | apps/operator_ui/data_access_brief_facts.py | [E] promote marker |
| `data_access_brief_market_sections.py` | EXISTS | apps/operator_ui/data_access_brief_market_sections.py | [E] promote marker |
| `data_access_brief_monitor_sections.py` | EXISTS | apps/operator_ui/data_access_brief_monitor_sections.py | [E] promote marker |
| `data_access_brief_input_projection.py` | EXISTS | apps/operator_ui/data_access_brief_input_projection.py | [E] promote marker |
| `data_access_brief_text_rules.py` | NOT PRESENT | - | [P] not created: no genuine responsibility proven |
| `data_access_brief_render_sections.py` | EXISTS | apps/operator_ui/data_access_brief_render_sections.py | [E] promote marker |
| `data_access_brief_render_fallback.py` | EXISTS | apps/operator_ui/data_access_brief_render_fallback.py | [E] promote marker |

### G.3 Locked / protected (unchanged): [L]
`graphs/trading_graph.py`, legacy `libs/agent/*`, Reporter facades `trade_report_ai.py` / `trade_report_markdown_clean.py` / `trade_story_pipeline.py`, numbered `bodies_*.py`, `execute_from_packet.py`, `live_execution_bundle_runner.py::main` effect coordinator, `controlled_mock_lanes/`.

### G.4 Recommended tree (responsibility-based; no file is created for an old marker alone)
~~~
libs/runtime/{commander,strategist,scanner,monitor,monitor_exit}/   [E] keep; rename generated *_projection_* modules only after consumer mapping (RENAME_CANDIDATE rows in the matrix)
libs/reporting/
  reporter_bundle_runtime_parts/   [E] one responsibility per module: targeted rows | exit/monitor context | human summaries | evidence+enrichment | closed-sell reconciliation | generation policy
  trade_memory_projection_parts/   [E] memory input + visibility | feedback rebuild | status summary | payload
  trade_read_model_parts/          [E] artifact selection | truth projection | display context
  trade_report/ai_facade_parts/    [E] fallback seed/summary/sections | compact input facts/payload
apps/operator_ui/                  [E] data_access_core (coordinator, LLM path SAFETY_LOCK) + data_access_brief_* owners
~~~
Reasoning: each proposed unit has one read/projection responsibility, one contract (named record where arity > 8), and no I/O capability; folders exist only where a cohesive group of at least two Owners already lives.
