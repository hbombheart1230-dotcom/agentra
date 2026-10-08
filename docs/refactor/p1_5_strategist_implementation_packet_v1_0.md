# P1.5 Strategist Implementation Packet v1.0

Status: **DESIGN COMPLETE / IMPLEMENTATION GATED**  
Date: 2026-10-07  
Design branch: `design/p1.5-p1.6-modernization`  
Implementation authorization: **NO — wait for P1.2/P1.3 frozen baseline**

This document closes the Strategist design phase for P1.5. The earlier v0.1 packet remains historical design evidence.

## 1. Frozen Objective

Refactor the 8,878-line `graphs/nodes/strategist_node.py` so the Strategist becomes an independently callable, framework-neutral component while preserving all current behavior.

```text
Agentra runtime state
        |
        v
build_strategist_agent_input(state)
        |
        v
StrategistAgentInput
        |
        v
run_strategist(input, deps)
        |
        v
StrategistAgentResult
        |
        v
apply_strategist_result(state, result)
        |
        v
same externally observable state / artifacts / handoffs
```

The production node remains:

```python
def strategist_node(state):
    agent_input = build_strategist_agent_input(state)
    result = run_strategist(agent_input, deps=...)
    apply_strategist_result(state, result)
    return state
```

P1.5 does not change graph order or enable new compositions.

## 2. Final Contract Decision

Do **not** reuse `libs/strategies/contracts.py::StrategyInput`.

That existing type is a per-symbol tactical strategy contract and has a different semantic role.

Add:

```text
libs/contracts/agents/strategist.py

StrategistAgentInput
StrategistAgentResult
```

Existing `libs/strategies/contracts.py::StrategistOutput` remains the canonical normalized output compatibility contract.

### StrategistAgentInput

Freeze these semantic groups:

```text
StrategistAgentInput
├ identity
│  ├ run_id
│  ├ day
│  └ runtime_phase
│
├ control
│  ├ policy
│  ├ applied_policy
│  ├ commander_decision
│  └ strategist_runtime_input
│
├ market
│  ├ market_context
│  ├ macro_context
│  ├ kiwoom_market_summary
│  └ global_sentiment_signal
│
├ candidates
│  ├ candidates
│  ├ universe
│  └ candidate_symbols
│
├ themes
│  ├ themes
│  ├ top_themes
│  ├ theme_scores
│  ├ theme_map
│  └ sector_map
│
├ feedback
│  ├ strategist_feedback_packet
│  ├ reporter_feedback_packet
│  ├ reporter_feedback_mode
│  └ reporter_feedback_mode_source
│
└ runtime_paths
   └ reports_root
```

Mock-only inputs such as `mock_global_sentiment`, `mock_news_sentiment`, and `mock_news_items` remain compatibility/test injection surfaces during migration; they are not promoted to long-term business-contract fields.

### StrategistAgentResult

```text
StrategistAgentResult
├ canonical_output
│  └ existing StrategistOutput-compatible payload
├ state_patch
│  └ compatibility patch for Agentra shared state
├ blocked
├ blocked_reason
├ llm_meta
└ evidence_metadata
```

The core returns data. It does not mutate the caller's shared state.

## 3. State Adapter Freeze

The current node directly writes 66 compatibility keys.

P1.5 preserves their externally observable values but centralizes mutation in `libs/runtime/strategist/state_adapter.py`.

Exact current write surface:

```text
strategist_fallback_source
universe_candidates
global_sentiment
global_sentiment_signal
theme_strength_packet
available_themes
news_query_targets
news_query_reasoning
news_collection_policy
news_collection_symbols
news_theme_component_symbols
policy
candidates
news_items
news_sentiment
news_sentiment_signal
candidate_news_items
candidate_news_context
market_news_items
market_news_sentiment
market_news_sentiment_signal
market_news_context
themes
candidate_symbols
theme_map
sector_map
recent_strategy_feedback
reporter_feedback_packet
strategy_memory
read_model_facts_summary
selected_themes
theme_strategy
market_regime
market_sentiment
market_structure
market_context_inputs
regime_factors
theme_strength
key_events
news_event_intelligence
avoid_themes
playbook
scanner_bias
scanner_bias_context
scanner_priority
trade_aggressiveness
risk_tone
monitor_guidance
macro_stress_overlay
monitor_entry_policy
monitor_policy
strategist_exit_policy
strategy_policy
strategist_plan
commander_horizon_policy
report_focus
scanner_guidance
strategist_output
strategist_blocked
strategist_blocked_reason
strategist_llm
strategist_policy_resolution
strategist_global_sentiment_breakdown
strategist_news_evidence_ranked
strategist_candidate_symbols_hint
strategist_decision_frame
```

Rules:

1. domain/policy/LLM helpers return values; no shared-state mutation
2. `state_adapter.py` owns application of compatibility state patches
3. no existing key is removed in early P1.5 batches
4. removal/renaming of state keys is a later consumer-migration task, not mechanical extraction
5. persisted/replay-facing keys require explicit compatibility evidence before cleanup

## 4. Final Target Package Tree

```text
libs/contracts/agents/
  strategist.py

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

graphs/nodes/strategist_node.py
  -> thin runtime adapter + temporary compatibility re-exports only
```

Do not create a new canonical implementation under `libs/agent/strategist.py`; that module is already explicitly a legacy compatibility adapter.

## 5. Existing Owners To Reuse

Do not duplicate:

- `libs/ai/strategist_config.py` — provider/model/retry/token/timeout authority
- `libs/strategies/contracts.py::StrategistOutput` — canonical output compatibility
- `libs/runtime/monitor_policy.py` — Monitor entry-policy contract/normalization
- `libs/runtime/scanner_bias.py` — Scanner bias contract/normalization
- `libs/runtime/strategy_horizon_feedback.py` — horizon handoff
- `libs/runtime/strategist_explanation.py` — structured explanation
- `libs/runtime/strategist_feedback_trace.py`
- `libs/runtime/strategist_input_quality.py`
- `libs/runtime/strategist_packet_visibility.py`
- `libs/contracts/agent_outputs.py` — artifact projection
- Commander strategist cache/fingerprint/refresh modules — Commander ownership

## 6. Compatibility Seams To Preserve

Early extraction must preserve these import/patch paths:

```text
graphs.nodes.strategist_node.strategist_node
graphs.nodes.strategist_node.LLMRouter
graphs.nodes.strategist_node._run_strategist_frame_llm
graphs.nodes.strategist_node.build_symbol_read_model
graphs.nodes.strategist_node.compute_global_sentiment_signal
graphs.nodes.strategist_node.collect_news_items
graphs.nodes.strategist_node.score_news_sentiment_signal
```

Private helpers currently imported directly by tests must be temporarily re-exported:

```text
_build_commander_context_summary
_build_compact_strategist_llm_payload
_build_strategist_llm_messages
_attach_quant_context_to_strategy_refresh_trace
_exit_policy
_global_sentiment_breakdown_payload
```

Remove wrappers only after tests and runtime consumers migrate.

## 7. Frozen Implementation Sequence

### S1 — LLM extraction

Move without semantic changes:

- parsing / salvage
- stage contracts
- adjustment normalization
- payload compaction
- prompt construction
- repair messages
- LLM runner

No structured-output modernization yet.

### S2 — deterministic policy/output extraction

Move:

- market/regime/playbook helpers
- Scanner proposal helpers
- Monitor proposal helpers
- exit-policy builder
- strategy-policy assembly
- Commander-facing summary/plan/frame builders
- pure evidence payload builders

### S3 — context and IO extraction

Move:

- Reporter feedback context
- Strategy Memory context
- deterministic read models
- market context
- news query/collection context
- theme context

Provider behavior and fallback behavior remain identical.

### S4 — Agent contract/service/state adapter

Add:

- `StrategistAgentInput`
- `StrategistAgentResult`
- `run_strategist()`
- input builder
- state adapter

Then reduce `strategist_node()` to the thin façade.

### S5 — test and compatibility cleanup

After behavior-equivalent service is green:

- split large Strategist tests by responsibility
- migrate monkeypatch targets to canonical owners
- remove unused private wrappers only with proof
- retain public `strategist_node(state) -> state` runtime seam

## 8. Pytest Gate

### S1 targeted

```bash
pytest -q   tests/test_strategist_frame_llm_integration.py   tests/test_strategist_output_schema.py
```

### S2 targeted

```bash
pytest -q   tests/test_strategist_reasoning_quality.py   tests/test_strategist_output_schema.py   tests/test_scanner_strategy_frame_integration.py
```

### S3 targeted

```bash
pytest -q   tests/test_strategist_frame_llm_integration.py   tests/test_strategist_input_quality_risk_off.py   tests/test_strategist_explanation_contract.py
```

### S4/S5 integration

```bash
pytest -q   tests/test_strategist_frame_llm_integration.py   tests/test_strategist_reasoning_quality.py   tests/test_strategist_output_schema.py   tests/test_strategist_explanation_contract.py   tests/test_strategist_input_quality_risk_off.py   tests/test_strategist_refresh_decision.py   tests/test_scanner_strategy_frame_integration.py   tests/test_m21_commander_runtime_entry.py
```

Then required affected regression/full suite according to the frozen P1.5 baseline procedure.

## 9. Test Refactor Target

Do not reorganize tests before their corresponding implementation moves.

Eventual structure:

```text
tests/unit/strategist/
  llm/
  policy/
  context/
  output/

tests/integration/strategist/
  test_service.py
  test_llm_flow.py
  test_feedback_memory.py

tests/integration/runtime/
  test_strategist_adapter.py

tests/regression/strategist/
  test_legacy_import_seams.py
  test_llm_fallback_and_repair.py
```

Historical Commander integration tests remain regression assets even if their filenames contain M21/M31 until the broader naming batch migrates them safely.

## 10. Documentation Disposition

- `docs/strategist_output/README.md` — CURRENT_SUPPORTING; update when implementation lands
- `docs/tactics/strategist_effectiveness_review.md` — CURRENT evaluation methodology; preserve
- `docs/runtime_memory/strategist_memory_packet_visibility_2026-04-20.md` — historical contract evidence; preserve
- `docs/kiwoom_truth/kiwoom_scanner_strategist_inventory_2026-04-20.md` — dated historical inventory; preserve
- `docs/execution_plan/strategist_llm_guide.md` — corrupted/superseded candidate; reference-map before any deletion
- M12/M18/M23/M31 Strategist plan documents — historical plans; retain historical names

## 11. Explicit Non-goals

P1.5 Strategist refactor does not:

- add/remove an LLM role
- add a new LLM call stage
- redesign prompts
- change model routing
- change repair/fallback semantics
- change candidate sourcing/ranking behavior
- change news re-query policy
- change Reporter feedback semantics
- change Strategy Memory semantics
- change Scanner authority
- change Monitor authority
- change Commander cache/fingerprint/refresh semantics
- change artifact schema/path
- change graph order

## 12. Acceptance

Strategist P1.5 is complete only when:

```text
strategist_node façade target      <= ~350 LOC
core standalone callable           YES
explicit AgentInput                YES
explicit AgentResult               YES
shared state mutation in core      NO
state adapter owns compatibility   YES
existing StrategistOutput shape    PRESERVED
LLM decision roles                 2 -> 2 system-wide
new Strategist LLM calls           0
Scanner final symbol authority     PRESERVED
Monitor execution authority        NONE
Commander refresh/cache semantics  PRESERVED
artifact/evidence semantics        PRESERVED
targeted tests                     GREEN
full required regression           GREEN
```

## 13. Implementation Gate

Do not implement S1 until:

```text
P1.2 FROZEN
P1.3 FROZEN
FULL BASELINE REGRESSION GREEN
PRODUCTION-WRITE LEAKAGE NONE
TRADING-AUTHORITY LEAKAGE NONE
BASELINE SHA/TAG RECORDED
```

Implementation branch must be cut from that frozen SHA, not from this design branch.

## 14. Design Verdict

```text
Strategist architecture design       COMPLETE
Contract naming                      FROZEN
Target package tree                  FROZEN
State mutation boundary              FROZEN
Compatibility seams                  MAPPED
Implementation batches               FROZEN
Targeted pytest gates                DEFINED
Runtime implementation               NOT STARTED
Next P1.5 design target              REPORTING
```
