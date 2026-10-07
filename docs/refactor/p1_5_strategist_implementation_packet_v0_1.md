# P1.5 Strategist Implementation Packet v0.1

Status: **DETAILED DESIGN / NO RUNTIME IMPLEMENTATION YET**  
Date: 2026-10-07  
Design branch: `design/p1.5-p1.6-modernization`  
Current source: `graphs/nodes/strategist_node.py` — 8,878 lines / 156 top-level functions

## 1. Objective

Restore the Strategist as an independently callable Agentra component without changing current trading behavior, LLM semantics, production topology, authority, artifact schemas, or Commander/Scanner/Monitor interaction.

North star:

```text
Agentra runtime state
        |
        v
Strategist runtime adapter
        |
        v
StrategistAgentInput
        |
        v
run_strategist(...)
        |
        v
StrategistAgentResult
        |
        v
state patch + canonical StrategistOutput
```

P1.5 does not enable a new graph ordering.

## 2. Current Structural Finding

`strategist_node()` is 1,705 LOC and currently owns all of the following in one function:

- candidate discovery/fallback
- global sentiment collection
- Kiwoom theme-strength hydration
- market/theme news-query construction
- news collection and sentiment scoring
- candidate reranking
- deterministic regime/playbook/risk framing
- Reporter feedback and Strategy Memory loading
- deterministic read-model loading
- LLM payload construction/call/repair/normalization
- Scanner/Monitor/exit policy construction
- Commander context and horizon handoff
- explanation/artifact/evidence surfaces
- direct state mutation
- event and decision-trace emission

This is the primary P1.5 Strategist boundary violation.

## 3. Existing Owners That Must Be Preserved

Do not duplicate these responsibilities.

| Existing owner | Current role | P1.5 rule |
|---|---|---|
| `libs/ai/strategist_config.py` | Strategist provider/model/timeout/token/retry configuration | KEEP as LLM provider configuration authority |
| `libs/agent/strategist.py` | explicitly documented legacy compatibility adapter | KEEP/WRAPPER; do not make it the new canonical core during this batch |
| `libs/ai/strategist.py` | legacy/tactical `StrategyInput -> StrategyDecision` strategist abstractions | KEEP; separate semantic role |
| `libs/strategies/contracts.py::StrategistOutput` | canonical normalized strategist-frame output | KEEP as P1.5 output compatibility authority |
| `libs/strategies/contracts.py::StrategyInput` | per-symbol tactical strategy input | KEEP; **do not repurpose as Agent-level Strategist input** |
| `libs/runtime/monitor_policy.py` | Monitor entry-policy normalization/contracts | KEEP; Strategist builds proposals but must reuse this owner |
| `libs/runtime/scanner_bias.py` | Scanner-bias contract/normalization | KEEP |
| `libs/runtime/strategy_horizon_feedback.py` | horizon/Commander handoff policy | KEEP |
| `libs/runtime/strategist_explanation.py` | structured strategist explanation | KEEP |
| `libs/runtime/strategist_feedback_trace.py` | feedback application trace | KEEP |
| `libs/runtime/strategist_input_quality.py` | input-quality/risk-off exception policy | KEEP |
| `libs/runtime/strategist_packet_visibility.py` | memory/input visibility | KEEP |
| `libs/contracts/agent_outputs.py` | canonical agent artifact projection | KEEP; evidence/output adapter, not Strategist core |

## 4. Contract Decision

### 4.1 Do not rename/reuse `StrategyInput`

The repository already has `libs/strategies/contracts.py::StrategyInput`, which represents a per-symbol tactical decision contract. Reusing that name for the high-level Strategist Agent would create semantic ambiguity.

New P1.5 names:

```text
StrategistAgentInput
StrategistAgentResult
```

### 4.2 P1.5 output compatibility

Do not replace `StrategistOutput` in P1.5.

```text
StrategistAgentResult
  ├ canonical_output    -> existing StrategistOutput-compatible dict
  ├ state_patch         -> exact compatibility patch for Agentra state
  ├ blocked
  ├ blocked_reason
  └ evidence_metadata
```

`coerce_strategist_output()` remains the final compatibility normalization step.

### 4.3 Proposed Agent input groups

The new typed input should group currently-read state instead of exposing a giant mutable dict:

```text
StrategistAgentInput
  identity
    run_id
    day
    runtime_phase

  control
    policy
    applied_policy
    commander_decision
    strategist_runtime_input

  market
    market_context
    macro_context
    kiwoom_market_summary

  candidates
    candidates
    universe
    candidate_symbols

  themes
    themes
    top_themes
    theme_scores
    theme_map
    sector_map

  feedback
    strategist_feedback_packet
    reporter_feedback_packet
    reporter_feedback_mode
    reporter_feedback_mode_source

  paths
    reports_root
```

Test mocks and concrete clients are dependencies, not business input fields.

During migration, a bounded compatibility context may be used only for providers that still require the legacy state shape. It must be explicitly named and reduced over time; it must not become a permanent hidden state bag.

## 5. Target Package Tree v0.1

Lowest-risk target consistent with existing `libs/runtime/scanner/` and `libs/runtime/commander/` extraction:

```text
libs/runtime/strategist/
  __init__.py
  common.py
  config.py
  service.py
  state_adapter.py
  observability.py

  context/
    __init__.py
    feedback.py
    memory.py
    read_models.py
    market.py
    news.py
    themes.py

  llm/
    __init__.py
    parsing.py
    stage_contracts.py
    adjustments.py
    prompting.py
    payload.py
    runner.py

  policy/
    __init__.py
    market.py
    scanner.py
    monitor.py
    exit.py
    assembly.py

  output/
    __init__.py
    frame.py
    commander.py
    plan.py
```

Agent-level contract:

```text
libs/contracts/agents/strategist.py
```

Important:
- `graphs/nodes/strategist_node.py` remains the public runtime adapter.
- `libs/agent/strategist.py` remains the legacy compatibility surface.
- P1.5 does not perform a repository-wide `libs/agent -> libs/agents` namespace migration.

## 6. Compatibility Seams Proven by Tests

These paths are directly imported or monkeypatched and must survive early extraction batches.

### Direct private-helper imports

`tests/test_strategist_frame_llm_integration.py` directly imports:

- `_build_commander_context_summary`
- `_build_compact_strategist_llm_payload`
- `_build_strategist_llm_messages`
- `_attach_quant_context_to_strategy_refresh_trace`
- `strategist_node`

`tests/test_strategist_reasoning_quality.py` directly imports:

- `_exit_policy`
- `_global_sentiment_breakdown_payload`
- `strategist_node`

Therefore these moved helpers require temporary re-export wrappers from `graphs/nodes/strategist_node.py`.

### Monkeypatch seams

Current tests monkeypatch these exact node-module symbols:

- `graphs.nodes.strategist_node.LLMRouter`
- `graphs.nodes.strategist_node._run_strategist_frame_llm`
- `graphs.nodes.strategist_node.build_symbol_read_model`
- `graphs.nodes.strategist_node.compute_global_sentiment_signal`
- `graphs.nodes.strategist_node.collect_news_items`
- `graphs.nodes.strategist_node.score_news_sentiment_signal`

Do not silently move the patch target during the first extraction. Either preserve aliases in the node module or migrate the relevant tests in the same audited batch.

### Commander runtime seam

`tests/test_m21_commander_runtime_entry.py` repeatedly monkeypatches:

`graphs.nodes.strategist_node.strategist_node`

The function path and `state -> state` façade behavior must remain stable throughout P1.5.

## 7. Test Baseline / Decomposition Targets

Current key suites:

| Test file | Size | Tests | Role |
|---|---:|---:|---|
| `tests/test_strategist_frame_llm_integration.py` | ~2,125 LOC | 43 | main LLM/context/integration characterization |
| `tests/test_strategist_reasoning_quality.py` | ~601 LOC | 12 | deterministic reasoning/news/policy behavior |
| `tests/test_strategist_output_schema.py` | ~208 LOC | 8 | canonical contract baseline |
| `tests/test_m21_commander_runtime_entry.py` | ~4,667 LOC | 84 total / ~18 Strategist-focused | runtime/Commander integration seam |

Target eventual layout:

```text
tests/unit/strategist/
  context/
  llm/
  policy/
  output/

tests/integration/strategist/
  test_service.py
  test_feedback_memory.py
  test_llm_flow.py

tests/integration/runtime/
  test_strategist_adapter.py

tests/regression/strategist/
  test_legacy_import_seams.py
  test_llm_fallback_and_repair.py
```

Do not bulk-move all tests first. Move tests with the production responsibility they characterize.

## 8. Strategist Documentation Classification

| Document | Classification | Action |
|---|---|---|
| `docs/strategist_output/README.md` | CURRENT_SUPPORTING | update with new P1.5 boundary when implementation lands |
| `docs/tactics/strategist_effectiveness_review.md` | CURRENT_SUPPORTING / EVALUATION | preserve; this is evaluation methodology |
| `docs/execution_plan/strategist_llm_guide.md` | SUPERSEDED/CORRUPTED CANDIDATE | do not delete until inbound references are mapped |
| `docs/kiwoom_truth/kiwoom_scanner_strategist_inventory_2026-04-20.md` | HISTORICAL_AUDIT/INVENTORY | preserve dated truth |
| `docs/runtime_memory/strategist_memory_packet_visibility_2026-04-20.md` | HISTORICAL_AUDIT + CONTRACT EVIDENCE | preserve; link from current docs if still applicable |
| `docs/plan/m12_2_llm_strategist_http.md`, `m18_*`, `m23_*`, `m31_*` | HISTORICAL_PLAN | preserve milestone names |

## 9. Function Ownership Inventory

Classification counts from the current 8,878-line source:

```json
{
  "MOVE": 58,
  "MOVE/WRAPPER": 97,
  "KEEP/WRAPPER": 1
}
```

| Function | Current lines | LOC | Class | Target owner |
|---|---:|---:|---|---|
| `_is_trueish` | 97-100 | 4 | MOVE | `libs/runtime/strategist/common.py` |
| `_env_bool` | 101-107 | 7 | MOVE/WRAPPER | `libs/runtime/strategist/config.py (provider settings stay in libs/ai/strategist_config.py)` |
| `_strategy_memory_usage_disabled` | 108-139 | 32 | MOVE/WRAPPER | `libs/runtime/strategist/config.py` |
| `_to_int` | 140-146 | 7 | MOVE | `libs/runtime/strategist/common.py` |
| `_env_int` | 147-156 | 10 | MOVE/WRAPPER | `libs/runtime/strategist/config.py (provider settings stay in libs/ai/strategist_config.py)` |
| `_nested_mapping_value` | 157-165 | 9 | MOVE | `libs/runtime/strategist/common.py` |
| `_neutralize_ambiguous_playbook_memory` | 166-185 | 20 | MOVE | `libs/runtime/strategist/context/memory.py` |
| `_load_recent_strategy_feedback` | 186-248 | 63 | MOVE | `libs/runtime/strategist/context/feedback.py` |
| `_iso_day_from_value` | 249-261 | 13 | MOVE | `libs/runtime/strategist/common.py` |
| `_resolve_state_day` | 262-268 | 7 | MOVE | `libs/runtime/strategist/common.py` |
| `_load_strategy_memory_advisory` | 269-364 | 96 | MOVE | `libs/runtime/strategist/context/memory.py` |
| `_resolve_top_n_candidates` | 365-380 | 16 | MOVE/WRAPPER | `libs/runtime/strategist/config.py (provider settings stay in libs/ai/strategist_config.py)` |
| `_strip_fenced_block` | 381-393 | 13 | MOVE/WRAPPER | `libs/runtime/strategist/llm/parsing.py` |
| `_parse_text_list_fragment` | 394-415 | 22 | MOVE/WRAPPER | `libs/runtime/strategist/llm/parsing.py` |
| `_extract_contract_from_prose` | 416-533 | 118 | MOVE/WRAPPER | `libs/runtime/strategist/llm/parsing.py` |
| `_extract_json_object` | 534-610 | 77 | MOVE/WRAPPER | `libs/runtime/strategist/llm/parsing.py` |
| `_classify_llm_parse_failure` | 611-619 | 9 | MOVE/WRAPPER | `libs/runtime/strategist/llm/parsing.py` |
| `_resolve_strategist_frame_llm_enabled` | 620-628 | 9 | MOVE/WRAPPER | `libs/runtime/strategist/config.py (provider settings stay in libs/ai/strategist_config.py)` |
| `_resolve_strategist_frame_llm_strict_enabled` | 629-632 | 4 | MOVE/WRAPPER | `libs/runtime/strategist/config.py (provider settings stay in libs/ai/strategist_config.py)` |
| `_stage_text_list` | 633-649 | 17 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_stage_bool` | 650-660 | 11 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_stage_float` | 661-669 | 9 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_normalize_stage2_selected_symbol_review` | 670-757 | 88 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_normalize_stage3_hold_review` | 758-803 | 46 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_normalize_stage4_carry_review` | 804-842 | 39 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_derive_stage_specific_common_overrides` | 843-1007 | 165 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_stage_specific_role_boundary` | 1008-1026 | 19 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_stage_specific_task_requirement` | 1027-1048 | 22 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_stage_specific_user_requirement` | 1049-1076 | 28 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_stage_specific_llm_contract` | 1077-1164 | 88 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_normalize_llm_overrides` | 1165-1298 | 134 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_summarize_monitor_entry_policy_for_adjustment` | 1299-1312 | 14 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_monitor_entry_policy_adjustment_delta_fields` | 1313-1330 | 18 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_infer_policy_adjustment_direction` | 1331-1369 | 39 | MOVE/WRAPPER | `libs/runtime/strategist/llm/stage_contracts.py` |
| `_symbol_memory_model_has_signal` | 1370-1389 | 20 | MOVE | `libs/runtime/strategist/context/memory.py` |
| `_build_symbol_refresh_memory_excerpt` | 1390-1459 | 70 | MOVE | `libs/runtime/strategist/context/memory.py` |
| `_build_llm_commander_refresh_context` | 1460-1588 | 129 | MOVE/WRAPPER | `libs/runtime/strategist/llm/adjustments.py` |
| `_normalize_policy_adjustment_surface` | 1589-1641 | 53 | MOVE/WRAPPER | `libs/runtime/strategist/llm/adjustments.py` |
| `_clean_directive_reason` | 1642-1651 | 10 | MOVE | `libs/runtime/strategist/common.py` |
| `_focus_axes_from_strings` | 1652-1675 | 24 | MOVE/WRAPPER | `libs/runtime/strategist/llm/adjustments.py` |
| `_normalize_strategy_adjustment_directives` | 1676-1843 | 168 | MOVE/WRAPPER | `libs/runtime/strategist/llm/adjustments.py` |
| `_build_strategist_llm_messages` | 1844-2120 | 277 | MOVE/WRAPPER | `libs/runtime/strategist/llm/prompting.py` |
| `_compact_news_sample_for_llm` | 2121-2146 | 26 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_round_optional` | 2147-2153 | 7 | MOVE | `libs/runtime/strategist/common.py` |
| `_compact_global_signal_for_llm` | 2154-2264 | 111 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_top_metric_map` | 2265-2284 | 20 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_performance_summary_map` | 2285-2317 | 33 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_recent_strategy_feedback_for_llm` | 2318-2374 | 57 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_load_reporter_feedback_packet` | 2375-2593 | 219 | MOVE | `libs/runtime/strategist/context/feedback.py` |
| `_compact_reporter_feedback_for_llm` | 2594-2638 | 45 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_strategy_memory_for_llm` | 2639-2725 | 87 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_pattern_performance_for_llm` | 2726-2753 | 28 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_news_signal_label` | 2754-2762 | 9 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_news_item_title_for_llm` | 2763-2775 | 13 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_news_signal_summary_for_llm` | 2776-2813 | 38 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_selected_symbol_news_signal_for_llm` | 2814-2826 | 13 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_clip_text_for_llm` | 2827-2833 | 7 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_scalar_mapping_for_llm` | 2834-2852 | 19 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_pattern_rows_for_llm` | 2853-2880 | 28 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_operator_summary_for_llm` | 2881-3011 | 131 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_trade_read_model_for_llm` | 3012-3042 | 31 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_symbol_read_model_for_llm` | 3043-3077 | 35 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_read_model_facts_for_llm` | 3078-3100 | 23 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_load_deterministic_read_models` | 3101-3136 | 36 | MOVE | `libs/runtime/strategist/context/read_models.py` |
| `_resolve_strategist_llm_call_kind` | 3137-3178 | 42 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_hide_stage1_symbol_memory` | 3179-3207 | 29 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_monitor_entry_policy_baseline_for_llm` | 3208-3225 | 18 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_theme_strength_for_llm` | 3226-3237 | 12 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_theme_packet_summary_for_llm` | 3238-3251 | 14 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_compact_candidate_context_for_refresh` | 3252-3283 | 32 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_slim_refresh_context_for_llm` | 3284-3311 | 28 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_apply_strategist_llm_token_budget` | 3312-3411 | 100 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_build_compact_strategist_llm_payload` | 3412-3743 | 332 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_quant_trace_stage_for_call_kind` | 3744-3756 | 13 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_quant_trace_label_for_stage` | 3757-3768 | 12 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_attach_quant_context_to_strategy_refresh_trace` | 3769-3799 | 31 | MOVE/WRAPPER | `libs/runtime/strategist/llm/payload.py` |
| `_build_strategist_llm_repair_messages` | 3800-3911 | 112 | MOVE/WRAPPER | `libs/runtime/strategist/llm/prompting.py` |
| `_messages_to_prompt_text` | 3912-3920 | 9 | MOVE/WRAPPER | `libs/runtime/strategist/llm/prompting.py` |
| `_run_strategist_frame_llm` | 3921-4270 | 350 | MOVE/WRAPPER | `libs/runtime/strategist/llm/runner.py` |
| `_extract_themes` | 4271-4315 | 45 | MOVE | `libs/runtime/strategist/context/news.py` |
| `_append_unique_text` | 4316-4326 | 11 | MOVE | `libs/runtime/strategist/common.py` |
| `_theme_to_news_queries` | 4327-4373 | 47 | MOVE | `libs/runtime/strategist/context/news.py` |
| `_theme_news_query_terms` | 4374-4388 | 15 | MOVE | `libs/runtime/strategist/context/news.py` |
| `_theme_component_symbols_for_news` | 4389-4436 | 48 | MOVE | `libs/runtime/strategist/context/news.py` |
| `_merge_news_collection_symbols` | 4437-4450 | 14 | MOVE | `libs/runtime/strategist/context/news.py` |
| `_build_market_news_query_targets` | 4451-4539 | 89 | MOVE | `libs/runtime/strategist/context/news.py` |
| `_build_market_news_query_reasoning` | 4540-4609 | 70 | MOVE | `libs/runtime/strategist/context/news.py` |
| `_default_policy` | 4610-4646 | 37 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_candidates_from_state` | 4647-4668 | 22 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_signal_score` | 4669-4677 | 9 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_to_float` | 4678-4684 | 7 | MOVE | `libs/runtime/strategist/common.py` |
| `_clamp` | 4685-4688 | 4 | MOVE | `libs/runtime/strategist/common.py` |
| `_risk_regime_label` | 4689-4696 | 8 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_market_sentiment_label` | 4697-4704 | 8 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_extract_market_context_inputs` | 4705-4764 | 60 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_market_structure_label` | 4765-4793 | 29 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_extract_theme_symbol_index` | 4794-4817 | 24 | MOVE | `libs/runtime/strategist/context/themes.py` |
| `_merge_theme_symbol_map` | 4818-4864 | 47 | MOVE | `libs/runtime/strategist/context/themes.py` |
| `_theme_packet_symbol_map_is_authoritative` | 4865-4870 | 6 | MOVE | `libs/runtime/strategist/context/themes.py` |
| `_merge_theme_packet_into_state` | 4871-4971 | 101 | MOVE/WRAPPER | `libs/runtime/strategist/state_adapter.py` |
| `_extract_theme_names_from_any` | 4972-4992 | 21 | MOVE | `libs/runtime/strategist/context/themes.py` |
| `_theme_packet_available_themes` | 4993-5056 | 64 | MOVE | `libs/runtime/strategist/context/themes.py` |
| `_resolve_selected_themes_from_api` | 5057-5105 | 49 | MOVE | `libs/runtime/strategist/context/themes.py` |
| `_build_theme_strategy_surface` | 5106-5165 | 60 | MOVE | `libs/runtime/strategist/context/themes.py` |
| `_news_context_summary` | 5166-5208 | 43 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_merge_news_contexts` | 5209-5232 | 24 | MOVE | `libs/runtime/strategist/context/market.py` |
| `_theme_strength_map` | 5233-5262 | 30 | MOVE | `libs/runtime/strategist/context/themes.py` |
| `_compose_regime_score` | 5263-5275 | 13 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_pick_playbook` | 5276-5287 | 12 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_scanner_priority` | 5288-5301 | 14 | MOVE/WRAPPER | `libs/runtime/strategist/policy/scanner.py` |
| `_scanner_bias` | 5302-5313 | 12 | MOVE/WRAPPER | `libs/runtime/strategist/policy/scanner.py` |
| `_build_scanner_bias_context_seed` | 5314-5338 | 25 | MOVE/WRAPPER | `libs/runtime/strategist/policy/scanner.py` |
| `_avoid_themes` | 5339-5348 | 10 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_trade_aggressiveness` | 5349-5356 | 8 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_risk_tone` | 5357-5364 | 8 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_monitor_guidance` | 5365-5409 | 45 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_norm_playbook` | 5410-5413 | 4 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_default_tactical_strategy` | 5414-5417 | 4 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_normalize_tactical_strategy` | 5418-5421 | 4 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_normalize_tactical_subtype` | 5422-5425 | 4 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_unit_score` | 5426-5432 | 7 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_deterministic_strategy_scores` | 5433-5473 | 41 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_normalize_strategy_scores` | 5474-5497 | 24 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_normalize_rejected_strategy_reasons` | 5498-5534 | 37 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_sanitize_reason_list` | 5535-5545 | 11 | MOVE | `libs/runtime/strategist/common.py` |
| `_normalize_candidate_watch_policy` | 5546-5615 | 70 | MOVE | `libs/runtime/strategist/policy/market.py` |
| `_macro_stress_overlay` | 5616-5642 | 27 | MOVE/WRAPPER | `libs/runtime/strategist/policy/monitor.py` |
| `_apply_macro_stress_to_monitor_frame` | 5643-5718 | 76 | MOVE/WRAPPER | `libs/runtime/strategist/policy/monitor.py` |
| `_condition_search_source_enabled` | 5719-5722 | 4 | MOVE/WRAPPER | `libs/runtime/strategist/config.py (provider settings stay in libs/ai/strategist_config.py)` |
| `_monitor_policy` | 5723-5808 | 86 | MOVE/WRAPPER | `libs/runtime/strategist/policy/monitor.py` |
| `_exit_policy` | 5809-5995 | 187 | MOVE/WRAPPER | `libs/runtime/strategist/policy/exit.py` |
| `_scanner_source_policy` | 5996-6187 | 192 | MOVE/WRAPPER | `libs/runtime/strategist/policy/scanner.py` |
| `_strategy_policy_score_weights` | 6188-6202 | 15 | MOVE/WRAPPER | `libs/runtime/strategist/policy/assembly.py` |
| `_strategy_policy_entry_policy` | 6203-6222 | 20 | MOVE/WRAPPER | `libs/runtime/strategist/policy/assembly.py` |
| `_build_strategy_policy` | 6223-6336 | 114 | MOVE/WRAPPER | `libs/runtime/strategist/policy/assembly.py` |
| `_build_commander_context_summary` | 6337-6477 | 141 | MOVE/WRAPPER | `libs/runtime/strategist/output/commander.py` |
| `_build_strategist_plan` | 6478-6563 | 86 | MOVE | `libs/runtime/strategist/output/plan.py` |
| `_build_market_regime_summary` | 6564-6580 | 17 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_build_strategist_monitor_entry_policy_seed` | 6581-6600 | 20 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_build_monitor_entry_policy_rationale` | 6601-6622 | 22 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_build_strategy_policy_provenance` | 6623-6644 | 22 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_report_focus` | 6645-6652 | 8 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_augment_strategy_fields` | 6653-6693 | 41 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_key_events` | 6694-6785 | 92 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_extract_ai_overrides` | 6786-6795 | 10 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_merge_override_text_list` | 6796-6811 | 16 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_build_strategic_answers` | 6812-6979 | 168 | MOVE/WRAPPER | `libs/runtime/strategist/output/frame.py` |
| `_make_event_logger` | 6980-6988 | 9 | MOVE/WRAPPER | `libs/runtime/strategist/observability.py` |
| `_emit_strategist_event` | 6989-7015 | 27 | MOVE/WRAPPER | `libs/runtime/strategist/observability.py` |
| `_log_strategist_summary` | 7016-7024 | 9 | MOVE/WRAPPER | `libs/runtime/strategist/observability.py` |
| `_log_strategist_llm_result` | 7025-7033 | 9 | MOVE/WRAPPER | `libs/runtime/strategist/observability.py` |
| `_sample_news_for_evidence` | 7034-7058 | 25 | MOVE/WRAPPER | `libs/runtime/strategist/observability.py` |
| `_rank_news_evidence_rows` | 7059-7102 | 44 | MOVE/WRAPPER | `libs/runtime/strategist/observability.py` |
| `_global_sentiment_breakdown_payload` | 7103-7158 | 56 | MOVE/WRAPPER | `libs/runtime/strategist/observability.py` |
| `_merge_news_samples` | 7159-7173 | 15 | MOVE/WRAPPER | `libs/runtime/strategist/observability.py` |
| `strategist_node` | 7174-8878 | 1705 | KEEP/WRAPPER | `graphs/nodes/strategist_node.py (thin runtime adapter)` |

## 10. State Boundary

The current node directly reads at least these state families:

- identity: `run_id`, `day`, `runtime_phase`
- control: `policy`, `applied_policy`, `commander_decision`
- candidates: `candidate_symbols`, `candidates`, `universe`
- themes: `themes`, `top_themes`, `theme_scores`, `theme_map`, `sector_map`
- market: `market_context`, `macro_context`, `kiwoom_market_summary`, `global_sentiment_signal`
- feedback: `strategist_feedback_packet`, `reporter_feedback_packet`, feedback mode fields
- runtime paths: `reports_root`
- testing/compatibility injection: mock sentiment/news fields

The current node writes more than 50 state keys, including candidate/news/theme intermediates, policies, canonical Strategist output, decision-frame evidence and LLM status.

P1.5 must centralize these mutations in `state_adapter.py`; domain helpers must return values instead of mutating the shared state.

## 11. IO Boundary

Current direct/indirect side effects in the giant node include:

- global sentiment provider
- news collection
- Kiwoom theme-strength reader
- report/read-model access
- strategy-memory / Reporter-feedback access
- LLM routing
- evidence ledger / artifact paths
- event logger
- decision trace
- canonical strategist artifact writing

Target:

```text
context/service layer -> reads/providers
LLM runner            -> model IO only
observability         -> evidence/event/artifact writes
policy/output          -> pure or deterministic
state_adapter          -> Agentra shared-state mutation only
```

No broker/order side effect belongs in Strategist.

## 12. LLM Boundary

P1.5 preserves current Strategist LLM semantics.

- no extra Agent LLM role
- no new model call stage
- no prompt semantic redesign
- no retry/fallback semantic redesign
- no removal of prose/repair compatibility until separate evidence proves it unnecessary

A later modernization audit may replace custom JSON/prose recovery with typed structured output, but that is **not** part of the first mechanical extraction.

## 13. Implementation Batches

### S1 — LLM Pure Extraction

Move:
- parsing
- stage contracts
- payload compaction
- prompting
- repair-message builder
- LLM runner

Keep node-level compatibility re-exports/aliases for tested private seams.

Acceptance:
- exact existing Strategist tests green
- no prompt/payload/normalization semantic change
- LLM call count and fallback path unchanged

### S2 — Deterministic Policy + Output Extraction

Move:
- market/playbook/risk helpers
- Scanner proposal helpers
- Monitor proposal helpers
- exit-policy builder
- strategy-policy assembly
- Commander context / plan / frame builders
- evidence-payload pure builders

Existing `monitor_policy.py`, `scanner_bias.py`, horizon and explanation modules remain authorities and are reused.

### S3 — Context / IO Extraction

Move:
- Reporter feedback
- Strategy Memory
- deterministic read models
- market context
- news
- theme context

Preserve current provider calls and fallback behavior exactly.

Introduce explicit provider boundaries only where they reduce hidden coupling without changing semantics.

### S4 — Agent Contract + Service + State Adapter

Add:
- `StrategistAgentInput`
- `StrategistAgentResult`
- `run_strategist(...)`
- `state_adapter.py`

Transform `strategist_node(state)` into:

```python
agent_input = build_strategist_agent_input(state)
result = run_strategist(agent_input)
apply_strategist_result(state, result)
return state
```

The actual implementation may retain a small compatibility dependency bundle while old provider APIs still accept state-shaped context.

### S5 — Test / Wrapper Cleanup

Only after all consumers have migrated:

- split giant Strategist test files by responsibility
- migrate monkeypatch targets to their canonical modules
- remove private node wrappers proven unused
- leave `strategist_node` itself as runtime adapter until P1.6 or later

## 14. Safety / Behavior Locks

For every S1-S5 batch:

```text
production topology                 SAME
Strategist LLM role                 SAME
Strategist call stage semantics     SAME
prompt semantic contract            SAME
candidate source behavior           SAME
news query/collection behavior      SAME
memory/reporter-feedback behavior   SAME
Scanner handoff semantics           SAME
Monitor handoff semantics           SAME
Commander cache/refresh semantics   SAME
StrategistOutput compatibility      SAME
artifact/evidence schema            SAME
broker/order side effect            NONE
```

## 15. No-Go / Escalation Conditions

Stop the batch and report instead of improvising if implementation appears to require:

- changing `StrategistOutput` semantics
- changing Commander cache/fingerprint/refresh behavior
- changing stage-2/3/4 LLM contracts
- changing news source/requery semantics
- deleting prose/repair recovery behavior
- moving authority into Strategist from Scanner/Monitor/Commander
- adding a new dependency
- changing artifact paths/schemas
- changing runtime graph order

## 16. Current Readiness

```text
Global P1.5 principles              FROZEN
Strategist responsibility map       156/156 FUNCTIONS OWNED
Existing owner map                  MAPPED
Primary compatibility seams         MAPPED
Primary test consumers              MAPPED
Target package tree                 v0.1 FROZEN CANDIDATE
Agent contract naming               DECIDED
Full field-level AgentInput schema  NEXT
Full state-write exact patch map    NEXT
S1 exact move list                  READY FOR FINALIZATION
Runtime implementation              BLOCKED BY P1.2/P1.3 BASELINE GATE
```

## 17. Next Design Work

Before implementation authorization:

1. derive exact `StrategistAgentInput` field schema from all state reads
2. derive exact `StrategistAgentResult.state_patch` key schema from all state writes
3. identify all current artifact/event writes and which are required vs best-effort
4. freeze S1 exact file/function move list
5. define S1 targeted pytest command set
6. prepare GPT-first implementation procedure and Cloud escalation threshold


## 18. S1 Exact First Implementation Slice

The first Strategist implementation slice after the P1.2/P1.3 baseline gate is intentionally mechanical.

Move only these responsibilities:

```text
llm/parsing.py
  _strip_fenced_block
  _parse_text_list_fragment
  _extract_contract_from_prose
  _extract_json_object
  _classify_llm_parse_failure

llm/stage_contracts.py
  _stage_text_list
  _stage_bool
  _stage_float
  _normalize_stage2_selected_symbol_review
  _normalize_stage3_hold_review
  _normalize_stage4_carry_review
  _derive_stage_specific_common_overrides
  _stage_specific_role_boundary
  _stage_specific_task_requirement
  _stage_specific_user_requirement
  _stage_specific_llm_contract
  _normalize_llm_overrides

llm/adjustments.py
  _summarize_monitor_entry_policy_for_adjustment
  _monitor_entry_policy_adjustment_delta_fields
  _infer_policy_adjustment_direction
  _build_llm_commander_refresh_context
  _normalize_policy_adjustment_surface
  _focus_axes_from_strings
  _normalize_strategy_adjustment_directives

llm/prompting.py
  _build_strategist_llm_messages
  _build_strategist_llm_repair_messages
  _messages_to_prompt_text

llm/payload.py
  current compact/payload helpers between the prompt and runner boundaries

llm/runner.py
  _run_strategist_frame_llm
```

Keep re-export compatibility in `graphs/nodes/strategist_node.py` for every currently imported private helper.

Keep node-module aliases for currently monkeypatched dependencies until tests are migrated.

### S1 required tests

Targeted minimum:

```bash
pytest -q tests/test_strategist_frame_llm_integration.py
pytest -q tests/test_strategist_output_schema.py
pytest -q tests/test_m21_commander_runtime_entry.py -k strategist
```

Affected-regression extension:

```bash
pytest -q tests/test_strategist_reasoning_quality.py
pytest -q tests/test_strategist_explanation_contract.py
```

Then run the repository's normal full regression gate before S1 is accepted.

No test may be deleted or weakened merely to accommodate moved imports.

## 19. GPT-first Implementation Policy

Default execution after the baseline gate:

```text
GPT
  design
  -> GitHub implementation
  -> CI/pytest triage
  -> repair
```

Escalate S1 to Codex Cloud only if repository-wide mechanical work or repeated local/CI repair is materially more efficient there.

Claude Cloud is not required for low-risk S1 extraction if behavior tests and CI are fully green; reserve independent Cloud audit for higher-risk Strategist service/state-adapter completion or the P1.5 freeze gate.
