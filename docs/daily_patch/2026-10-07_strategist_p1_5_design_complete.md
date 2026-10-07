# 2026-10-07 Strategist P1.5 Design Complete

## Summary

Completed the detailed P1.5 design for Strategist modularization.

This is a design/documentation change only. No Strategist runtime behavior, LLM prompt, strategy policy, Scanner/Monitor handoff, Commander cache/refresh semantics, execution authority, or broker path changed.

## Current Finding

- `graphs/nodes/strategist_node.py`: 8,878 LOC
- `strategist_node()`: approximately 1,705 LOC
- current node directly writes 66 compatibility state keys
- current node mixes candidate/context hydration, global/news/theme IO, LLM work, policy construction, output assembly, shared-state mutation, observability and artifact emission

## Frozen P1.5 Design

Target flow:

```text
runtime state
  -> build_strategist_agent_input
  -> StrategistAgentInput
  -> run_strategist
  -> StrategistAgentResult
  -> state_adapter
  -> same compatibility state/output
```

New Agent-level contract names:
- `StrategistAgentInput`
- `StrategistAgentResult`

The existing tactical `StrategyInput` is not reused because it represents a different per-symbol strategy contract.

The existing `StrategistOutput` remains the canonical normalized output compatibility contract.

## Compatibility

Early P1.5 batches must preserve:
- `graphs.nodes.strategist_node.strategist_node`
- tested node-level LLM/provider monkeypatch seams
- tested private helper re-exports until their tests migrate
- Commander Strategist cache/fingerprint/refresh behavior
- current artifact/evidence paths and schemas

## Planned Implementation Batches

1. S1 LLM extraction
2. S2 deterministic policy/output extraction
3. S3 context/IO extraction
4. S4 Agent contract/service/state adapter
5. S5 tests/wrapper cleanup

Runtime implementation remains blocked until P1.2/P1.3 freeze and baseline SHA/tag capture.

## Authority

- `docs/refactor/p1_5_strategist_implementation_packet_v1_0.md`

## Next

Return to the planned P1.5 work order and design Reporting P1.5.1/P1.5.2 before implementation.
