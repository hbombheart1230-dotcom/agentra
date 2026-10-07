# 2026-10-07 P1.5 Strategist Deep Design

## Summary

Completed the first detailed P1.5 decomposition pass for the Strategist without changing runtime code.

## Findings

- `graphs/nodes/strategist_node.py` is 8,878 lines with 156 top-level functions.
- `strategist_node()` itself is approximately 1,705 lines and combines candidate sourcing, global/news/theme context, memory/feedback, LLM orchestration, policy construction, state mutation and observability.
- All 156 top-level functions now have a proposed P1.5 owner.
- Existing canonical/compatibility owners were identified so the refactor does not duplicate contracts or policy modules.

## Contract Decision

The existing `libs/strategies/contracts.py::StrategyInput` is a per-symbol tactical-strategy contract and will not be repurposed.

The high-level agent boundary will use distinct names:

- `StrategistAgentInput`
- `StrategistAgentResult`

The existing `StrategistOutput` / `coerce_strategist_output` remains the P1.5 output compatibility authority.

## Compatibility Findings

Current tests directly import private helpers from `graphs.nodes.strategist_node` and monkeypatch node-module dependencies including:

- `LLMRouter`
- `_run_strategist_frame_llm`
- `build_symbol_read_model`
- `compute_global_sentiment_signal`
- `collect_news_items`
- `score_news_sentiment_signal`

These are explicit compatibility seams. Early extraction batches must preserve wrappers/aliases or migrate the tests in the same audited batch.

Commander integration tests also monkeypatch `graphs.nodes.strategist_node.strategist_node`; the façade path and state-in/state-out behavior remain stable through P1.5.

## First Implementation Slice

S1 is defined as LLM mechanical extraction only:

- parsing
- stage contracts
- adjustment normalization
- prompting
- compact payload
- LLM runner

No prompt, retry/fallback, LLM-call, strategy, candidate, runtime-topology or execution semantic change is allowed.

## Implementation Gate

Runtime implementation remains blocked until the P1.2/P1.3 baseline/freeze gate is satisfied.

## Source

- `docs/refactor/p1_5_strategist_implementation_packet_v0_1.md`
