# P15 SECOND PASS 020 — bulk intra-function modularization of the non-Reporter giants (S1 Monitor, S2 Scanner, S3 Commander, S4 Operator UI, S5 Strategist, S6 Supervisor/Executor)

**Status:** IMPLEMENTED (Claude), CODEX INDEPENDENT AUDIT PENDING. Preauthorized work on `refactor/p1.5` only; Git commit/push is the sole deliverable (no ZIP). Final P1.5 acceptance, main merge, live deployment and Wave D are **not** part of this order.
**Start SHA:** code `1f7add2b0f9b5a33399da27edcdd2f390bdf911b` + design commit `60dfa1c4cd7ca62d127251a4051b3404a86f6932` (GPT second-pass design: [slices](../P15_SECOND_PASS_GPT_FUNCTION_SLICES_2026_10_12.md), [owner contracts and gates](../P15_SECOND_PASS_GPT_OWNER_CONTRACTS_AND_GATES_2026_10_12.md), [master design](../P15_SECOND_PASS_GPT_MASTER_DESIGN_2026_10_12.md)).

## What was done
Intra-function extract-method on 13 giant functions. A segment is moved only when a dataflow analysis proves it is (a) a contiguous run of statements (or the pure right-hand side of a `state[...] = expr` assignment) with no `return/break/continue/yield/await/global/del`, no state write, no event/log/IO/LLM/clock/env/uuid/random call, and (b) every input local is definitely defined before it and every output is explicitly returned. Segments copy the original statements verbatim; module globals are resolved at use time through the injected module (`facade.NAME`, TEMPORARY_COMPATIBILITY, keeps monkeypatch seams). Owners mutate only caller-fresh local containers (never a parameter or a state alias) and import nothing. Effectful statements — state writes, events, artifact writes, provider/LLM calls, clock and environment reads, early returns and trigger precedence — stay in the original function, which is now a thinner sequencer.

| Stage | Function(s) | Owners |
|---|---|---|
| S1 Monitor | `monitor_node`, `_evaluate_monitor_entry_candidate`, `evaluate_intraday_entry_signal`, `evaluate_exit_policy` | `libs/runtime/monitor/*`, `libs/runtime/monitor_exit/exit_policy_*` |
| S2 Scanner | `scanner_node` (canonical ranking window 1629–1788 untouched) | `libs/runtime/scanner/*_projection.py` |
| S3 Commander | `_build_commander_decision`, `_resolve_commander_behavior_policy`, `_assess_open_position_commander_override`, `_attach_commander_applied_policy` | `libs/runtime/commander/*_projection.py` |
| S4 Operator UI | `_build_operator_brief_sections`, `_build_operator_brief_input`, `_render_operator_brief_markdown` (`_load_operator_brief` LLM coordinator untouched) | `apps/operator_ui/data_access_brief_*` |
| S5 Strategist | `strategist_node` outside the LLM boundary (SAFETY_LOCK functions untouched) | `libs/runtime/strategist/{context,policy,output}/node_*_projection.py` |
| S6 Supervisor/Executor/common | **SAFETY_LOCK / DEFERRED** — no immutable real fixtures, no provably pure read-model | none |

## Gates
`tests/test_p156_second_pass_extraction_gates.py` (ledger completeness; inlining every Owner call reconstructs the pinned baseline function AST; unmoved definitions and constants baseline-identical; no unresolved Owner globals / no imports; Owners ≤350 LOC; no authority/env/clock/IO tokens; only fresh-container mutation; scope and authority path guard), consumer suites, and a concurrent baseline×2 + feature×2 call differential with post-call argument hashing. Wave C scope guard is now pinned to its own end SHA.

Result: [evidence](evidence/P15-SECOND-PASS-CLAUDE-021.md).
