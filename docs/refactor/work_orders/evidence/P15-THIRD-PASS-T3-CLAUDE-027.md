# P15 Third Pass T3 — Architecture & Owner contract cleanup (Claude implementation evidence)

Start HEAD `ede47324e8db4be12c45e0a09ca3dcd22c68c5c1` (origin unchanged at start). Code commit `bb994fbc3d2e183478c03751dcf76b30b7757dbe` (T3-A/B); T3-0 prerequisite committed and CI-verified separately as `8522e6a` (CI run 38370435281: Success). Branch `refactor/p1.5` only; no live `C:\Agentra`, Q12, broker, real LLM, Docker, scheduler; no ZIP; T3.5 not started.

## T3-0 — mandatory safety foundation (separate commit `8522e6a`)
**A. Static purity checker** `scripts/refactor/p158_static_purity_closure.py` — rewritten as an explicit-root, tri-state, **ADVISORY** checker (13 positive/negative tests in `tests/test_p159_static_purity_closure.py`):
- no hard-coded path (`--root` required); results `PURE / IMPURE / UNKNOWN`, call chain kept in every finding;
- unresolved names, dynamic dispatch (`deps[...]`, local-variable calls, subscript/lambda calls), external imports outside a small reviewed known-pure table, `facade.X` without a supplied facade module, unparseable source and depth exhaustion (default 64) are **UNKNOWN**, never PURE; cycles terminate;
- relative imports, re-exports, aliases and `import *` are followed. An advisory PURE is necessary evidence only; AST moved-body equivalence and differential parity stay mandatory.
- Re-check of the 8 T2 segments with the strict checker (`t2_static_purity_recheck.json`): **5 PURE / 3 UNKNOWN / 0 IMPURE**. The UNKNOWN ones call helper callables bound through dependency-injection dicts (`safe_int = deps["safe_int"]` style) which cannot be resolved statically — "NOT PROVEN SAFE" by the checker; their safety rests on the AST/differential evidence (T2: 69/69 byte-identical incl. ordered effects; T3 rerun: 69/69).

**B. Historical vs current gates.** `p156/p157/p158` extraction gates now read **only immutable snapshots**: modules and Owners at the stage end SHA via `git show` (Second Pass `bf59c4d`, T1 `67e0dc0` with base `4cb92916`, T2 `d4a5364` with base `af0a448`) instead of the moving working tree; scope diffs were already pinned. New `tests/test_p159_current_owner_contract_gates.py` validates the **current** HEAD separately: every historical Owner function resolves through the T3 mapping, imports resolve (no cycles), Owner authority restrictions/<=350 LOC, record field order == legacy tuple order and tuple equality/hash/unpack, original modules keep public signatures since each stage end, facade-symbol breadth does not increase, no protected surface/numbered body touched. **Demonstrated:** the behavior-preserving T3 Owner cleanup passes the historical gates (28) and the current gates (7) simultaneously (48 tests incl. analyzer tests).

## T3-A — ownership matrix and tree alignment
Generated, source-grounded: [matrix JSON](../../p1_5_third_pass_t3_ownership_matrix.json) / [matrix MD](../../p1_5_third_pass_t3_ownership_matrix.md) — 207 modules, classes {'KEEP': 23, 'CANONICAL_OWNER': 139, 'RENAME_CANDIDATE': 30, 'COMPAT_FACADE': 14, 'SAFETY_LOCK': 1}. Canonical target overlay appended as section G of `P15_CANONICAL_TARGET_TREE_AND_REPORTER_ASIS_2026_10_13.md` (historical snapshot preserved): every `[P]` marker checked against the tree (existing packages promoted to [E]; `ranking_core.py` REJECTED as a second ranking authority; `data_access_brief_text_rules.py` not created) and a compact recommended tree with a responsibility reason per unit. Nothing was created for an old marker alone.

## T3-B — cohesive cleanup
| Change | Result |
|---|---|
| `lifecycle_report_policy.py` (mixed: closed-sell reconciliation + generation policy) | split into `closed_sell_reconciliation.py` and `report_generation_policy.py` (one responsibility each); module removed |
| mechanical `if True:` scaffolding | removed from every T2 Owner function that had it and from the converted functions (AST-identical statement lists, checked in the transformation) |
| positional tuple returns | 12 functions return immutable `NamedTuple` records (positional-compatible: every existing unpacking call-site unchanged) |
| generated names | 9 mechanically generated Owner function names replaced by semantic names; call sites updated in the original modules only |

| Historical function | New name | Record | Module | Arity |
|---|---|---|---|---:|
| `fb_seed_action_entry_decision_seed` | `fallback_report_seed` | `FallbackReportSeed` | `fallback_seed_context.py` | 30 |
| `memory_input_commander_memory_policy_daily_pac` | `memory_packets_and_visibility` | `MemoryPacketsAndVisibility` | `memory_input_visibility.py` | 30 |
| `memory_input_monitor_guidance_monthly_packet` | `memory_prompt_visibility` | `MemoryPromptVisibility` | `memory_input_visibility.py` | 30 |
| `read_select_artifacts_bundle` | `selected_trade_artifacts` | `SelectedTradeArtifacts` | `read_artifact_selection.py` | 30 |
| `cp_facts_commander_route_diagnostics` | `compact_story_facts` | `CompactStoryFacts` | `compact_input_facts.py` | 25 |
| `behavior_input_block_buy_when_open_position_bu` | `commander_behavior_policy_inputs` | `CommanderBehaviorPolicyInputs` | `policy_inputs_projection.py` | 24 |
| `signal_feature_breakout_buffer_pct_breakout_le` | `breakout_level_features` | `BreakoutLevelFeatures` | `signal_features.py` | 24 |
| `scan_feature_candidate_rank_score_candidate_un` | `candidate_rank_inputs` | `CandidateRankInputs` | `score_feature_projection.py` | 24 |
| `brief_facts_canonical_monitor_snapshot_executi` | `operator_brief_canonical_facts` | `OperatorBriefCanonicalFacts` | `data_access_brief_facts.py` | 24 |
| `lifecycle_exit_monitor_context` | `lifecycle_exit_monitor_context` | `LifecycleExitMonitorContext` | `lifecycle_story_context.py` | 8 |
| `closed_sell_execution_details` | `closed_sell_execution_details` | `ClosedSellExecutionDetails` | `closed_sell_reconciliation.py` | 8 |
| `report_generation_policy_gate` | `report_generation_policy_gate` | `ReportGenerationPolicyGate` | `report_generation_policy.py` | 8 |

Positional contract metrics (segments with > 8 outputs):
| Pass | segments | > 8 outputs (before) | max arity (before) | > 8 still unconverted | max arity (after) |
|---|---:|---:|---:|---:|---:|
| second_pass | 120 | 40 | 24 | 36 | 24 |
| t1 | 16 | 10 | 30 | 5 | 30 |
| t2 | 8 | 0 | 0 | 0 | 0 |

Façade breadth: unchanged by design (assertion: converted Owners' `facade.*` symbol set is a subset of the previous one); eager binding was **not** introduced — all module dependencies still resolve at call time through the injected runner/original module. `lifecycle_bundle` mutation semantics, aliasing and later persistence are untouched (statement bodies are byte-identical apart from indentation).

## Behavior parity (baseline `ede4732` x2 vs feature `bb994fb` x2, isolated sessions)
| Run | mode | calls | byte-identical | justified | mismatch | unresolved | tests |
|---|---|---:|---:|---:|---:|---:|---|
| A: T2 anchors incl. ordered file effects (same-path, pid pinned) | det | 69 | 69 | 0 | 0 | 0 | 1 failed, 109 passed, 1 warning in 1 |
| B: Reporter 40 files (T1 targets + facades) | det | 2912 | 2912 | 0 | 0 | 0 | 1 failed, 671 passed, 1 warning in 5 |
| C: second-pass consumers (140 files) | det | 1131 | 1020 | 91 | 0 | 20 | 1 failed, 2949 passed, 2 warnings in |
| D: C-unresolved strategist tests re-run (same-path, pinned) | det | 20 | 20 | 0 | 0 | 0 | 20 passed, 1 warning in 4.82s, 20 passed, 1 warning in 4.85s, 20 passed, 1 warning in 5.06s, 20 passed, 1 warning in 5.70s |

- **Touched functions are byte-identical:** `_resolve_commander_behavior_policy` 62/62, `evaluate_intraday_entry_signal` 70/70, `_build_operator_brief_sections` 39/39, Reporter fallback/compact/memory/read-model 2,912/2,912; `scanner_node` 74/79 identical + 5 justified (`R-MEMORY-PACKET-ID`, the same memory-packet-id temp-path artifact seen in every earlier pass).
- **Run C unresolved (20) = `strategist_node.prompt_hash`**: Strategist code is untouched in T3; the cause is the PID-bearing temp path in prompt payloads (known since the second pass). Run D re-executes exactly those tests same-path/pinned: **20/20 byte-identical**.
- Failures: C shows only the known baseline `test_api_routes_are_get_only`; A's known harness-induced lock-test failure is the pid-pin artifact documented in T2 (passes natural).
- Honest process note: the first B/C attempt used a local commit that omitted `graphs/` call-site renames (`git add` scope); the harness failed closed at import (exit 2 / 2,912 mismatches) before anything was pushed; the local commits were squashed (soft reset, unpushed) and all runs were redone against `bb994fb`. A harness normalisation artifact (pid substring splitting a ns mtime in effect hashing) was also found and fixed before the final effect run.
- Raw logs outside the repo; SHA-256 in [manifest](../../evidence/p159_third_pass_t3/raw_evidence_manifest.json) (manifest SHA-256 `16dd5d494026dfcd2954023beef7c686abd24bdf0adc09791710a7892d410f03`).

## Compatibility / deletion debt (remaining)
30 Owner modules still carry unconverted positional returns > 8 (RENAME_CANDIDATE rows in the matrix; highest: 30 in `memory_feedback_rebuild`, 24 in operator-brief market/monitor sections, `signal_features`, `score_feature_projection`); remaining generated `*_projection_*` names; broad `facade` injection (42/45 second-pass Owners) not narrowed — proving identical use-time resolution per Owner is T3.1 work; `deps`-dict dependency injection in Reporter parts prevents static proof (UNKNOWN); numbered `bodies_*.py`, legacy facades and `libs/agent/*` untouched pending consumer proof; REAL_REPORT_PARITY_BLOCKED OPEN; `controlled_mock_lanes` operational root OPEN (T5); Wave D not started.
