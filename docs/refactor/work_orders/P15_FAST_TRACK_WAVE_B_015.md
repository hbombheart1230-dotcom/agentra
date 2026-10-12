# P15 FAST TRACK WAVE B 015 — P1.5.4 Strategist, P1.5.5 Scanner, P1.5.6 Monitor first pass

**Status:** IMPLEMENTED (Claude), CODEX WAVE B AUDIT PENDING. Preauthorized first-pass structural work on `refactor/p1.5` only; Git commit/push is the sole deliverable (no ZIP).
**Read order:** `CLAUDE.md` → `CURRENT.md` → this order → [Fast Track plan](../P15_FAST_TRACK_FIRST_PASS_2026_10_12.md) → `COMMON_RULES.md`; implementation packets (`p1_5_strategist_implementation_packet_v1_0.md`, `p1_5_scanner_implementation_packet_v1_0.md`, `p1_5_monitor_implementation_packet_v1_0.md`) interpreted under the 2026-10-12 Fast Track approval (older "no change" wording is stage-scoped, not permanent).
**Start SHA:** `877455db439e9e6f72af413216acc9758b91a2a9` (Wave A closed FIRST_PASS_WITH_DEBT; CI green at `2504d70`).

## Scope and frozen surfaces
- B1 Strategist (`graphs/nodes/strategist_node.py`), B2 Scanner (`graphs/nodes/scanner_node.py`), B3 Monitor (`graphs/nodes/monitor_node.py`).
- Frozen: Strategist LLM decision authority and every prompt/model/retry/timeout/call-count path; Scanner canonical ranking, tie-break order and soft-guidance role; Monitor intent-only role, entry/exit timing, stop/risk/sizing; Supervisor/Executor/Commander authority; Q10/Q12/UEF/Step5C/D/R6.2.
- Method (identical to Reporting/Operator UI waves): public `def` stays in the node module; IO-free, non-LLM-call, non-persistence function bodies move verbatim to responsibility-named Owners (<=350 LOC) that never import the node module; every former node global is qualified at its use site as `facade.NAME` (use-time lookup, mid-call monkeypatching preserved).
- Targets follow the packet trees: `libs/runtime/strategist/{context,policy,llm,output}/`, `libs/runtime/scanner/`, `libs/runtime/monitor/`.

## Gates (per agent boundary)
`tests/test_p154_wave_b_moved_bodies.py` (baseline AST equality after unqualification, exact qualified names, no unresolved global, wrapper injection, use-time oracle vs the pinned baseline function, module declarations retained, Owners <=350) and `tests/test_p154_wave_b_scope_and_authority_boundary.py` (diff scope + no execution/broker/supervisor/LLM-routing imports in Owners) plus the 60 existing Strategist/Scanner/Monitor consumer test files and a baseline-vs-feature call differential. Wave A guards stay pinned to the Wave A end commit.

## Result summary
See [evidence](evidence/P15-FAST-TRACK-WAVE-B-CLAUDE-016.md). Monitor (B3) was **only minimally decomposed** (2 helpers): `monitor_node.py` is dominated by two functions, `monitor_node` (2,634 LOC) and `_evaluate_monitor_entry_candidate` (658 LOC), plus helpers of <=43 LOC (only tiny ones left); splitting them needs real intra-function decomposition, which is not a safe mechanical move — recorded as SECOND_PASS_DEBT / B3_BLOCKED_BY_GIANT_FUNCTION.
