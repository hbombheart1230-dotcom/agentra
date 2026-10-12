# P15-R3-FACADE-LOC-MAX-REDUCTION-008 — queued after Guard 007

**Status: QUEUED FOR ARCHITECTURE/CONSUMER PROOF, NOT YET AUTHORIZED TO MODIFY RUNTIME.**
**Direction:** Reduce all remaining safely reducible code. `SIZE_DEFERRED` is an unmet target, not permission to stop. One refactor branch `refactor/p1.5`; no trading/LLM behavior change.

## Direct source inventory at `f6cc71b25d9f3aadd356ee6509b629778861ce32` (physical lines)
| Façade | Original | Pre-R3 | Now | Top-level functions | Preamble before first def | Functions <=5 lines |
|---|---:|---:|---:|---:|---:|---:|
| AI Reporter | 8354 | 2761 | **1958** | 182 | 217 | 93 |
| Markdown | 5862 | 2658 | **1891** | 209 | 187 | 107 |
| Story | 4527 | 636 | **562** | 45 | 150 | 25 |
| TOTAL | 18743 | 6055 | **4411** | 436 | 554 | 225 |

R3 reduced the façade files by 1644 LOC, with 57 moved implementation functions in 11 small Owners. Those lines mostly moved, not disappeared from the repository.

## Why large, and high-yield candidates
- AI has 182 function contracts plus import/dependency wiring. Larger remaining candidates (physical spans): `_fallback_report` ~64, `build_separated_ai_trade_report` ~61, `_section_builder_deps` ~59, `_trade_report_language_meta` ~45, `build_ai_trade_report` ~39, `_router_chat_with_hard_timeout` ~32. Protect LLM timeout/retry/fallback and truth precedence with explicit proof; don't blindly move.
- Markdown has 209 preserved function contracts. Dependency adapters consume many lines: `_summary_render_deps` ~59, `_summary_input_deps` ~50, `_markdown_strategy_deps` ~35, `_strategy_memory_deps` ~34. Look for coherent canonical ownership and reduced wiring.
- Story: `_story_assembly_deps` ~46, `build_lifecycle_bundle` ~27, `build_report_section_seeds` ~23, `_human_payload_deps` ~22, `build_timeline` ~23. Smaller baseline means another bounded split may help.
- Most functions already act as short compatibility surfaces: 225 of 436 are <=5 lines. Even if every AI/Markdown public function were only 2 lines, 182 AI defs require at least 364 lines and 209 Markdown defs require at least 418 lines, **before imports or wiring**. Thus the strict 350-line target contradicts retaining all original defs. Shrink through proven consumer migration and P1.5.10 wrapper retirement, not minification or hiding exports.

## Proposed future tranches (not approved yet)
1. Read-only per-function LOC/owner/caller/monkeypatch ledger: KEEP/MOVE/WRAPPER/SAFETY-LOCK/DEAD. Mark whether each nontrivial body or dependency adapter can move to an *existing cohesive Owner* and preserve use-time `facade.NAME` semantics.
2. After GPT/user acceptance of a bounded slice, Claude moves highest safe-yield pure/reporting glue first, preserving **436 ABI**, result/schema/order/Unicode, LLM prompts/retry/call count, import DAG, and no production writes. Never create a giant catch-all, duplicate business Owner, or expand a new Owner beyond 350 LOC. Codex audits exact SHA.
3. Consider legacy public-wrapper deletions only with complete dynamic/static consumer and patch evidence, ordinarily at P1.5.10. Static absence is not proof of dead code.
4. Record actual before/after LOC and *why each remaining long function cannot be safely moved*, including consumer-proven compatibility exceptions; don't treat size exception as PASS.

**Open:** Actual historical report/LLM parity BLOCKED/NOT RUN, native full-suite controlled_mock_lanes write isolation OPEN, numbered Owner domain cohesion debt; P1.5.2 OPEN/P1.5.3 forbidden.
