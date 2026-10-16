# P15 V2-053 rework 054 — evidence (Claude)

```
BASE_CODE_SHA: 1f7d1df7fe828315f44de18b1b1f88ba0e4beebc
COMPARISON_PRE_V2_SHA: 73f2277bfe95fda6d548572e48764966d01661e4
REWORK_CODE_SHA (broad FINAL run): f476f160fa66d778b576e48a630cfa1f5878db93
STRICT_SHIM_ALLOWLIST_AND_AST: tests/test_p154_wave_b_moved_bodies.py SHIM_ALLOWLIST (version "V2-053/054", the five
  legacy->canonical V2 paths, hard-coded, never read from shim text) + _verify_identity_shim_source: parses source only
  (no import), accepts optional docstring + exactly [Import sys as _sys, ImportFrom libs.agents.scanner.context
  <same basename> as _canonical level 0, Assign _sys.modules[__name__] = _canonical]; exact node classes, names, aliases,
  target/slice/value; fails closed on anything else. Non-allowlisted owners keep the original behavior (no auto-follow).
NEGATIVE_MUTATIONS_PASS_TOTAL: 22/22 rejected (tests/test_p168_wave_b_shim_verifier_negatives.py, disposable strings +
  one temp-file case through _owner_file). Codex counterexamples raise RuntimeError(123), import subprocess and wrong
  canonical target are rejected. The previous substring/regex helper would have ACCEPTED 12 of the 22 (incl. all 3).
  Positive: 5/5 real shims verified; comment/docstring variants accepted; verifier does not import the shim. 31 tests.
WAVE_B_768_RESULT: 768 collected, 768 passed (unchanged parametrization; no skips added)
V1_V2_CONTRACTS: V1-052 (8) + candidate_risk (5) + V2-053 (23) + T4-A gates/freeze + Wave B scope + patch-note tests:
  859 passed together with Wave B
```

## Broad baseline comparison (Part B)

Two separate scratch clones of the local repository, checked out detached at the two SHAs, run once each with the same
command on the same host (concurrently):

```
host: Windows 11, CPython 3.13.14, venv pip-freeze sha256 prefix 361d5fe8763802ae
env:  PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 TZ=Asia/Seoul TRADING_MODE=mock OPENROUTER_API_KEY= KIWOOM_APP_KEY=
      KIWOOM_APP_SECRET= KIWOOM_ACCESS_TOKEN= PYTEST_ADDOPTS=
cmd:  python -m pytest -q -p no:cacheprovider tests -m "not heavy and not docker and not benchmark" --disable-warnings --junitxml=<out>
```

| Tree | SHA | passed | failed | errors | skipped | deselected | exit |
|---|---|---:|---:|---:|---:|---:|---:|
| BASE (pre-V2) | 73f2277 | 7,945 | 36 | 2 | 27 | 9 | 1 |
| FINAL (rework code) | f476f16 | 8,000 | 35 | 2 | 27 | 9 | 1 |

The FINAL tree has 55 more passing tests because it contains the V1/V2/rework contract tests. No collection errors.
Signatures = (failure/error, exception type, last test-file location, first message line with tree root, user temp
paths, hex addresses and long numbers normalized). Full sanitized manifest:
`docs/refactor/evidence/P15-V2-053-REWORK-054-broad-failure-manifest.json`.

| Class | Count | Node IDs |
|---|---:|---|
| FINAL_ONLY | **0** | - |
| SAME_ID_DIFFERENT_CAUSE | **0** | - |
| SAME_FAILURE_SIGNATURE | **37** | table below |
| BASE_ONLY | 1 | `tests/test_closeout_memory_bounds.py::test_daily_summary_payload_identical_with_streamed_and_materialised_rows` |

BASE_ONLY classification: `generated_at` '...02:02:13' != '...02:02:14' (wall-clock second boundary between the two
payload builds); the single node re-run once in each tree passes in both. Timing flake in BASE, not a FINAL change.

The 37 FINAL failures/errors (35 failed + 2 errors) are therefore identical by node ID and signature to BASE failures;
they are pre-existing quality debt (missing local `reports/` fixtures, Windows host, execution-disabled guard, etc.),
not caused by V2-053 or this rework. They stay open and are not fixed here.

| Node ID | kind | exception | location |
|---|---|---|---|
| `tests/apps/api/test_isolation.py::test_api_routes_are_get_only` | failure | - | `-` |
| `tests/test_diagnostic_queries_work_order01.py::test_all_four_public_cli_forms_match[json-query_m25_notification_events]` | failure | - | `-` |
| `tests/test_step5b_fix4.py::test_t1_real_executor_post_response_parser_exception_returns_unknown_not_raise` | failure | - | `-` |
| `tests/test_step5b_fix4.py::test_t1_real_executor_token_invalid_check_exception_also_returns_unknown_not_raise` | failure | - | `-` |
| `tests/test_step5b_fix4.py::test_t2_runner_blocks_second_mutation_after_real_post_response_parse_exception` | failure | - | `-` |
| `tests/test_step5b_fix4.py::test_t3_upper_limit_cancel_real_post_response_parser_exception` | failure | - | `-` |
| `tests/test_step5b_fix4.py::test_t4_unfilled_order_recovery_cancel_real_post_response_parser_exception` | failure | - | `-` |
| `tests/test_step5b_fix4.py::test_t5_explicit_accepted_unaffected_by_fix4` | failure | - | `-` |
| `tests/test_step5b_fix4.py::test_t6_explicit_rejected_unaffected_by_fix4` | failure | - | `-` |
| `tests/test_step5b_fix4.py::test_t8_post_dispatch_transport_failure_is_unknown_one_physical_call` | failure | - | `-` |
| `tests/test_uef2a_forward_policy_contract.py::test_calculator_12_opening_shadow_entry_and_forward_price_chains_differ` | failure | - | `-` |
| `tests/test_uef2a_forward_policy_contract.py::test_calculator_14_opening_shadow_d1_d3_d5_bounded_sessions_and_insufficient_future` | failure | - | `-` |
| `tests/test_uef2a_forward_policy_contract.py::test_calculator_1_horizon_exit_exact_price_chain_and_session_close_fallback` | failure | - | `-` |
| `tests/test_uef2a_forward_policy_contract.py::test_calculator_8_q11_zero_offset_eod_no_excursion_and_cost_semantics` | failure | - | `-` |
| `tests/test_uef2a_forward_policy_contract.py::test_calculator_9_q12_shared_engine_reuse_produces_all_seven_checkpoints` | failure | - | `-` |
| `tests/test_uef2a_forward_policy_contract.py::test_calculators_2_3_4_q10_semiconductor_reference_fallback_and_exact_windows` | failure | - | `-` |
| `tests/test_uef2a_forward_policy_contract.py::test_calculators_5_6_q10_index_single_authorities_and_collector_three_states` | failure | - | `-` |
| `tests/test_uef2a_forward_policy_contract.py::test_opening_controlled_has_no_program_specific_forward_policy` | failure | - | `-` |
| `tests/test_uef5_1_clean_evidence_registry.py::test_freeze_manifest_stays_11_of_11` | failure | - | `-` |
| `tests/test_uef5_1_clean_evidence_registry.py::test_uef5_package_is_stdlib_only_and_not_imported_by_production_or_core` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_clean_and_eligible_is_recomputed` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_identity_collision_fails_closed` | error | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_invalid_required_field_prevents_recompute` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_isolated_snapshot_determinism` | error | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_missing_and_excluded_are_not_zero` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_missing_candle_file_gaps_stay_fail_closed` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_no_frozen_uef_mutation` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_no_production_imports` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_q10_index_fg_creates_no_cost_policy_and_calls_no_costed_entrypoint` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_q10_index_fg_episodes_produced_but_no_fg_aggregate` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_q10_index_fg_partial_stage_model_never_complete` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_q10_index_h_unchanged_and_no_double_cost` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_q11_v2_preserved` | failure | - | `-` |
| `tests/test_uef5_2_historical_recompute.py::test_untracked_member_counts_are_flagged` | failure | - | `-` |
| `tests/test_uef6c_historical_validation.py::test_e_baseline_vs_instrumented_canonical_parity` | failure | - | `-` |
| `tests/test_uef6c_historical_validation.py::test_f_witness_to_output_aggregate_mapping` | failure | - | `-` |
| `tests/test_uef9_formal_authority.py::test_a_valid_current_authority` | failure | - | `-` |

Raw logs/JUnit are kept outside the repository (bounded failure evidence); scratch clones removed after the run.
