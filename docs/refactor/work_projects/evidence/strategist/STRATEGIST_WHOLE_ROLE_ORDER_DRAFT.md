# DRAFT — Strategist whole-role P1.5 work order (for Work review; NOT an approval)

**Status:** DRAFT_FOR_WORK_REVIEW. Read-only analysis; no Strategist source, test, shared gate or workflow was changed.
**Author lane:** Claude (Reporter principal), relay step "Strategist READ-ONLY ownership/consumer/test design" per
`docs/dev-team/assignments/10_P15_CONTINUOUS_ROLE_RELAY.md`. Implementation requires an exact Work
`NEXT_ROLE_SOURCE_APPROVED` charter on GitHub and a new writer branch.
**Analysed tree:** `d773709ba2f70471fad9badba4f92400f7818319` (runtime BASE). `origin/integration/p15-t4-pr5-convergence-20261015`
@ `d269c906` has **no** `libs/ graphs/ apps/ scripts/ tests/` diff against it, so the inventory applies to the current integration line.
**Machine-readable inventory:** `strategist_readonly_inventory.json` (same directory; generator `strategist_readonly_inventory.py`, byte-reproduced from a fresh `git archive d773709`,
pure AST + text scan, effect labels are token heuristics, not proofs).

## 1. What already exists (do not redo)

| Item | State at BASE | Evidence |
|---|---|---|
| R3-style facade wrappers in `graphs/nodes/strategist_node.py` | 104 wrappers (581 LOC) call `*_r3_impl(..., facade=_r3_sys.modules[__name__])` | inventory `node.functions[].r3_wrapper` |
| Owner modules `libs/runtime/strategist/{context,llm,output,policy}` | 39 implementation modules (all <= 350 physical LOC) + 5 identity shims | inventory `packages` |
| S1-057 canonical owners `libs/agents/strategist/{context,output}` | 5 modules / 16 functions moved; legacy paths are strict `sys.modules` identity shims; integrated by `c5aa8dbf` (p1.5-058) | `tests/test_p172_strategist_s1_057_migration.py`, fixture `p1_5_strategist_s1_057` |
| T4-C node contract freeze | whole-State + ordered effect digests (mock frame-LLM ok/error/timeout/raises/strict), golden at `8acedae`, native Windows replay, portable BASE-vs-FEATURE elsewhere | `tests/test_p164_strategist_contract_freeze.py`, `tests/fixtures/p1_5_t4c_strategist/` |
| Shared gates pinning Strategist paths | Wave B moved bodies / scope, Wave C scope, second-pass gates, p058 integration contracts | `tests/test_p154_wave_b_moved_bodies.py`, `test_p154_wave_b_scope_and_authority_boundary.py`, `test_p155_wave_c_scope_and_authority_boundary.py`, `test_p156_second_pass_extraction_gates.py`, `test_p173_p058_integration_contracts.py` |
| CI | `p15-integration-t4-regression.yml`, `p15-integration-crossbranch-compat.yml`, `p152-r2c-residual-regression.yml` reference `test_p164_strategist_contract_freeze.py` / `test_p172_strategist_s1_057_migration.py` | workflows (Work-owned) |

## 2. Residual scope in `graphs/nodes/strategist_node.py` (4053 physical lines)

52 non-wrapper top-level definitions, 2683 LOC. Module level: 14 assignments (constants/config) besides imports.

**A. Authority / effect bodies — 23 functions, 2290 LOC — keep in place unless separately approved (NEEDS_AUTHORITY):**

| Function | LOC | Why held |
|---|---:|---|
| `strategist_node` | 502 | graph entry; LLM, news/global-sentiment network providers, clock, env, decision trace write, policy output; consumed by `graphs/trading_graph.py`, `graphs/commander_runtime.py`, `libs/runtime/commander/nodes.py`, `graphs/pipelines/offhours_validation.py`, p164 freeze tools, 24+ tests |
| `_run_strategist_frame_llm` | 326 | model routing / retry / env enable; LLM authority (16-category rule from Reporter R10-D applies) |
| `_build_strategist_llm_messages`, `_build_strategist_llm_repair_messages`, `_stage_specific_*` (4), `_build_compact_strategist_llm_payload`, `_apply_strategist_llm_token_budget`, `_resolve_strategist_llm_call_kind` | 1000+ | prompt text / token budget / call-kind = LLM routing & cost semantics; any byte change alters requests (T4-C request digests) |
| `_load_reporter_feedback_packet`, `_load_strategy_memory_advisory`, `_load_deterministic_read_models`, `_load_recent_strategy_feedback` | 389 | env-gated persisted-artefact readers (Reporter / strategy memory truth inputs) |
| `_emit_strategist_event`, `_make_event_logger`, `_log_strategist_*` | ~44 | log/event side effects |
| `_resolve_strategist_frame_llm_enabled`, `_env_bool`, `_iso_day_from_value`, `_resolve_state_day` | ~28 | env / clock |

**B. Candidate helpers (SAFE_MOVE_CANDIDATE, proof required) — 29 functions, 393 LOC:** `_extract_contract_from_prose` (108),
`_extract_json_object` (74), `_build_symbol_refresh_memory_excerpt` (64), `_parse_text_list_fragment`, `_strip_fenced_block`,
`_classify_llm_parse_failure`, `_messages_to_prompt_text`, `_clip_text_for_llm`, `_quant_trace_stage_for_call_kind`,
`_quant_trace_label_for_stage`, `_risk_regime_label`, `_market_sentiment_label`, `_trade_aggressiveness`, `_risk_tone`,
`_monitor_guidance`, `_report_focus`, `_norm_playbook`, `_default_tactical_strategy`, `_normalize_tactical_strategy`,
`_normalize_tactical_subtype`, `_theme_packet_symbol_map_is_authoritative`, `_to_int`, `_to_float`, `_round_optional`, `_clamp`,
`_unit_score`, `_is_trueish`, plus two to verify first: `_resolve_strategist_frame_llm_strict_enabled` (probably env through
`_env_bool` -> likely NEEDS_AUTHORITY) and `_condition_search_source_enabled` (NETWORK_DATA token). Labels/aggressiveness/guidance
derive from risk numbers: movable only byte-identical, never re-tuned. Moving all of B shrinks the node by < 10 %; the
residual is dominated by A, so Strategist "whole-role" completion is mainly classification + contracts, not bulk movement.

## 3. Owner modules `libs/runtime/strategist/**` — classification

- **POLICY owners (protected semantics, structure only):** `policy/monitor_entry_policy.py` (BROKER/ENV tokens), `policy/scanner_policy.py`,
  `policy/exit_and_defaults.py` (ENV), `policy/node_policy_projection.py`, `policy/global_risk_adjustment.py`,
  `policy/llm_override_application.py`, `policy/strategy_policy_annotation.py`, `policy/monitor_entry_policy_seed.py`,
  `llm/override_normalization.py` (BROKER token), `llm/adjustment_directives.py`, `llm/candidate_watch_overrides.py`, `llm/stage_reviews.py`.
  These encode strategy / risk policy. P1.5 may only relocate them with identity shims and byte-identical bodies; thresholds,
  defaults, precedence and override rules are out of scope (operator-only policy change).
- **CONTEXT / read-model owners:** `context/*` (13 implementation modules; `market_inputs`, `theme_packet`, `commander_refresh_context`
  carry NETWORK_DATA tokens -> verify actual calls before calling them pure).
- **OUTPUT / trace projection owners:** `output/*` (9 implementation modules; `commander_context_and_plan` has a FILE_READ token).
- Every owner today has exactly one importer (`strategist_node`) and no direct test importer: tests reach them through the node,
  so owner-level contract tests are a coverage gap.

## 3a. Contracts a Strategist refactor must preserve (cited at d773709)

- **LangGraph entry:** `strategist_node(state) -> state` (single `return state`); bound by `graphs/trading_graph.py:17/52`,
  `libs/runtime/commander/nodes.py:33/41` (lazy import), `graphs/commander_runtime.py:2260-2338` (callable injection) and
  `graphs/pipelines/offhours_validation.py:194` (lazy import). Function identity at `graphs.nodes.strategist_node.strategist_node`
  is a contract (24 test files reference it).
- **State keys:** the node body reads 10 keys directly (`candidate_symbols, mock_global_sentiment, mock_news_items,
  mock_news_sentiment, policy, reports_root, run_id, sector_map, strategist_llm, theme_map`; helpers read more) and writes 66
  keys (e.g. `strategist_output, strategist_plan, strategist_decision_frame, strategist_policy_resolution, strategy_policy,
  monitor_entry_policy, monitor_policy, scanner_bias, scanner_guidance, strategist_exit_policy, playbook, market_regime,
  risk_tone, trade_aggressiveness, candidates, universe_candidates, strategist_blocked(_reason)`; full list in the inventory).
  Key set, insertion order and values are frozen by T4-C whole-State digests.
- **Output DTO:** `libs/strategies/contracts.py` `StrategistOutput` (dataclass, line 125) + `coerce_strategist_output` (line 333);
  owned by `libs/strategies`, NOT by the Strategist node -> out of scope for relocation, consumers must see identical dicts.
- **Persisted artefact:** `write_strategist_artifact(state)` (from `libs.runtime.canonical_artifacts`, node line 4050) and
  `append_decision_trace` — writer effects, keep call order and arguments.
- **Module-level policy vocabularies:** `_PLAYBOOK_ACTIONS`, `_ENTRY_POLICY_ACTIONS`, `_MONITOR_FOCUS_ACTIONS`,
  `_SELECTED_SYMBOL_BIAS_ACTIONS`, `_REFRESH_ACTIONS`, `_MONITOR_FOCUS_AXES`, `_TACTICAL_STRATEGY_BY_PLAYBOOK`,
  `_CANDIDATE_WATCH_*` (14 module assignments) are LLM-directive/policy vocabularies: POLICY_PROTECTED, unchanged values and names.
- **Use-time patch points (tests monkeypatch the node module; a moved body must still resolve these through the facade at call
  time):** `LLMRouter` (25 sites), `collect_news_items` (8), `score_news_sentiment_signal` (8), `compute_global_sentiment_signal` (7),
  `build_symbol_read_model` (4), `_run_strategist_frame_llm` (3), `write_strategist_artifact`, `build_recent_strategy_feedback`,
  `_clamp`; 16 test files patch the node module. These are the negative-fixture anchors for S-5.

## 4. Proposed whole-role program (S-1 .. S-6)

| Packet | Content | Gate to pass | Authority |
|---|---|---|---|
| S-1 Inventory freeze | commit the read-only inventory + per-function triage rows (legacy path, LOC, effects verified by AST call graph, consumers, tests, disposition SAFE_MOVE / RETAIN_FACADE / NEEDS_AUTHORITY / POLICY_PROTECTED) | Work review | none (docs) |
| S-2 Owner contract tests | offline BASE-vs-HEAD replay for every `libs/runtime/strategist` owner function through a pinned BASE archive (Reporter R10 runner pattern: fresh interpreter, frozen clock, ordered fs log, temp cwd, inherited env) | normal + `-O`, Linux 3.12, Windows 3.13 | tests only |
| S-3 Canonical package decision | Work decides target `libs/agents/strategist/{context,llm,output,policy}` vs. keeping `libs/runtime/strategist` as owner; exact agent-package allowlist entry | Work charter | Work |
| S-4 Module relocation | S1-057 pattern (strict 3-statement identity shim, blob-equal body, old/new import order, pickle, signature, globals) in batches of <= 8 modules; POLICY owners last and only byte-identical | own migration test + T4-C freeze + Wave B/C + T3 mappings by Work | approved scope only |
| S-5 Node residual pure helpers | R3/R4 facade-injection moves of the SAFE_MOVE_CANDIDATE helpers (use-time facade resolution, monkeypatch before/mid-call, AST restore vs BASE, LOC <= 350) | R4-style body proof + T4-C freeze unchanged digests | approved scope only |
| S-6 Role acceptance | coverage ledger of all 156 node defs + 44 owner modules, NEEDS_AUTHORITY map (LLM/news/env/trace), CI list proposal, patch-note proposal NOT_PUBLISHED | Work independent run | Work |

## 5. Test targets (must stay green and unmodified by the writer lane)

- Role: `tests/test_p164_strategist_contract_freeze.py` (T4-C, native + portable), `tests/test_p172_strategist_s1_057_migration.py`,
  `tests/test_strategist_*.py` (8 files: explanation contract, frame LLM integration, input-quality risk-off, LLM summary,
  output schema, quant context report, reasoning quality, refresh decision), `tests/test_strategy_*.py` consumers.
- Shared (Work-owned, path mappings only by Work): `test_p154_wave_b_moved_bodies.py`, `test_p154_wave_b_scope_and_authority_boundary.py`,
  `test_p155_wave_c_scope_and_authority_boundary.py`, `test_p156_second_pass_extraction_gates.py`, `test_p173_p058_integration_contracts.py`, T3 current-owner gate.
  Known hazard (S1-057 handoff): Wave B `_owner_file()` follows only allowlisted paths, so a new identity shim makes
  `_func()` raise `StopIteration` — every relocated path needs a Work mapping *before* the writer lane can be green.
- Consumers to smoke: `graphs/trading_graph.py`, `graphs/commander_runtime.py`, `libs/runtime/commander/nodes.py`, `graphs/pipelines/offhours_validation.py`.

## 6. Hard boundaries (proposal)

No change to strategy decisions, thresholds, defaults, risk policy, truth precedence, LLM model routing/retry/token budget/prompt
bytes, news/global providers, Broker/Executor/Supervisor/approval, Q10/Q12, scheduler or production data. No real LLM or network.
Strategist T4-C golden is not regenerated by the writer lane. No Reporter or Monitor branch edits; no main merge.

## 7. Open questions for Work

1. Target package for the 39 `libs/runtime/strategist` owners (move under `libs/agents/strategist` or keep)?
2. Are POLICY owners in scope for P1.5 relocation at all, or RETAIN until a policy-owner review?
3. Which writer (Claude / Codex) and branch name; base SHA (proposed: current integration tip after Reporter/Monitor gates).
4. Should S-2 owner contract tests start before S-3 (they are useful regardless of the target path)?
