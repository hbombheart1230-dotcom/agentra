# P1.5 Strategist Decomposition

Status: DETAILED DESIGN IN PROGRESS  
Implementation: NOT AUTHORIZED BY THIS DOCUMENT

Current detailed packet: `p1_5_strategist_implementation_packet_v0_1.md`

## 1. Why Strategist Is the Design Reference

`graphs/nodes/strategist_node.py` is currently about 8,879 LOC and contains multiple responsibilities:
- graph/runtime adaptation
- context hydration
- feedback and memory loading
- LLM payload construction
- prompt construction
- LLM invocation
- parsing/normalization
- scanner policy
- monitor policy
- exit policy
- commander-facing summaries
- strategy-plan construction
- evidence/artifact handling

Strategist is therefore the best subsystem for proving the P1.5 agent-boundary model before applying it to Scanner, Monitor and Commander.

## 2. Known High-LOC Functions

Current inventory seed:

| Function | Approx LOC | Initial responsibility |
|---|---:|---|
| `strategist_node` | 1706 | mixed orchestration |
| `_run_strategist_frame_llm` | 350 | LLM runner |
| `_build_compact_strategist_llm_payload` | 332 | LLM input/payload |
| `_build_strategist_llm_messages` | 277 | prompting |
| `_load_reporter_feedback_packet` | 219 | feedback context |
| `_scanner_source_policy` | 192 | scanner policy |
| `_exit_policy` | 187 | exit policy |
| `_normalize_strategy_adjustment_directives` | 168 | normalization |
| `_build_strategic_answers` | 168 | output |
| `_derive_stage_specific_common_overrides` | 165 | stage policy |
| `_build_commander_context_summary` | 141 | commander output |
| `_normalize_llm_overrides` | 134 | LLM parsing/normalization |
| `_operator_summary_for_llm` | 131 | LLM context |
| `_build_llm_commander_refresh_context` | 129 | refresh context |
| `_extract_contract_from_prose` | 118 | parsing |
| `_build_strategy_policy` | 114 | policy assembly |
| `_build_strategist_llm_repair_messages` | 112 | prompt repair |
| `_compact_global_signal_for_llm` | 111 | context compaction |
| `_merge_theme_packet_into_state` | 101 | state update |
| `_apply_strategist_llm_token_budget` | 100 | LLM budget |
| `_load_strategy_memory_advisory` | 96 | memory context |

This inventory is a starting point only. Final relocation requires call/import/test/state analysis.

## 3. Existing Modules Must Be Reused

Before creating new modules, inspect and reuse responsibilities already represented by:
- `libs/ai/strategist.py`
- `libs/ai/strategist_config.py`
- `libs/ai/strategist_factory.py`
- `libs/agent/strategist.py`
- `libs/runtime/strategist_explanation.py`
- `libs/runtime/strategist_feedback_trace.py`
- `libs/runtime/strategist_input_quality.py`
- `libs/runtime/strategist_packet_visibility.py`
- `libs/reporting/strategist_llm_summary.py`
- `libs/reporting/strategist_llm_evaluation.py`
- `libs/reporting/live_execution_strategist_artifacts.py`

P1.5 must not create parallel modules that duplicate an existing owner.

## 4. Tentative Responsibility Map

Potential responsibilities, subject to deep analysis:

```text
strategist/
  context/
    market
    news
    feedback
    memory
    stage
  llm/
    payload
    prompting
    parsing
    runner
  policy/
    scanner
    monitor
    exit
    candidate_watch
    assembly
  output/
    commander_context
    plan
    answers
    evidence
  normalization
  state_updates
  contracts
```

This is not yet the approved final tree.

## 5. Initial Relocation Hypotheses

| Current function | Initial class | Tentative target |
|---|---|---|
| `_build_compact_strategist_llm_payload` | MOVE | LLM payload owner |
| `_build_strategist_llm_messages` | MOVE | LLM prompting owner |
| `_build_strategist_llm_repair_messages` | MOVE | LLM prompting owner |
| `_run_strategist_frame_llm` | MOVE | LLM runner owner |
| `_extract_json_object` | MOVE/WRAPPER | LLM parsing owner |
| `_extract_contract_from_prose` | MOVE/WRAPPER | LLM parsing owner |
| `_normalize_llm_overrides` | MOVE/WRAPPER | parsing/normalization owner |
| `_load_reporter_feedback_packet` | MOVE | feedback context owner |
| `_load_recent_strategy_feedback` | MOVE | feedback context owner |
| `_load_strategy_memory_advisory` | MOVE | memory context owner |
| `_build_symbol_refresh_memory_excerpt` | MOVE | memory context owner |
| `_scanner_source_policy` | MOVE | scanner policy owner |
| `_monitor_policy` | MOVE | monitor policy owner |
| `_apply_macro_stress_to_monitor_frame` | MOVE | monitor policy owner |
| `_exit_policy` | MOVE | exit policy owner |
| `_build_strategy_policy` | MOVE | policy assembler |
| `_build_commander_context_summary` | MOVE | commander-facing output |
| `_build_strategist_plan` | MOVE | plan output |
| `_build_strategic_answers` | MOVE | answer output |
| `_key_events` | MOVE | answer/evidence output |
| `strategist_node` | SPLIT/KEEP FACADE | thin runtime adapter/orchestration |

## 6. Required Deep-Dive Before Codex Implementation

For every top-level Strategist function, produce:

```text
function
start/end line
LOC
responsibility
direct callees
direct callers
state reads
state writes
environment reads
filesystem IO
network/LLM IO
artifact writes
Scanner dependency
Monitor dependency
Reporter dependency
Commander dependency
test consumers
monkeypatch/import compatibility
classification
target owner
canonical name
risk
migration batch
```

## 7. Target Agent Boundary

Desired conceptual surface:

```text
runtime state
   |
   v
build_strategist_input(...)
   |
   v
run_strategist(StrategistInput)
   |
   v
StrategistOutput
   |
   v
apply_strategist_output(...)
   |
   v
runtime state patch
```

The agent core should be testable without invoking the full live runtime.

## 8. Contract Questions To Resolve

Before implementation, freeze:
- which market/global/news fields are required vs optional
- memory and reporter-feedback representation
- runtime/timestamp context
- strategy-frame schema
- scanner-policy schema
- monitor-policy schema
- exit-guidance schema
- candidate-guidance schema
- evidence/provenance references
- compatibility with existing `StrategistOutput`

Existing DTO semantics must not be silently changed.

## 9. Codex Handoff Threshold

Do not hand Strategist implementation to Codex until:
- >=95% function ownership is classified
- state mutation points are mapped
- LLM/IO boundaries are explicit
- public/monkeypatch compatibility seams are identified
- target package tree is frozen
- agent input/output contracts are frozen
- existing test consumers are mapped
- characterization gaps are listed
- migration batches are small enough to audit independently

## 10. Next Analysis Step

Deep-read `strategist_node.py`, the existing Strategist-related modules, and Strategist tests.

The output will be the first full **P1.5 Implementation Packet** containing:
1. scope/non-goals
2. target tree
3. complete function relocation table
4. naming map
5. contracts
6. state read/write map
7. IO/side-effect boundaries
8. compatibility requirements
9. test relocation map
10. characterization-test requirements
11. acceptance criteria
12. forbidden changes
13. Codex Cloud implementation prompt
14. Claude Cloud audit prompt
