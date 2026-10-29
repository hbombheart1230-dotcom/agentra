# RF-076 — T09 tests/fixture target and protected callable identity

- SOURCE integration/p1.5@a7654f389fddbc2829f005ab247a96bf295228d8; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. Actor Claude A (tests code only, no oracle edits); peer read-only. 59 exclusive historical paths.

Executor/UEF: test_uef1_work_package_a_canonical_contract.py 1798 LOC with 126 tests; keep identities/golden.

## Callable mapping: KEEP, not MOVE

- `tests/test_uef1_work_package_a_canonical_contract.py::test_normalize_enum_value_equates_member_and_raw_string` → SAME SOURCE_PATH / SAME callable; KEEP_TEST_ORACLE. Existing test fixture names and assertions must remain stable.
- `tests/test_uef1_work_package_a_canonical_contract.py::test_two_different_events_can_share_a_link_key_and_this_is_correct` → SAME SOURCE_PATH / SAME callable; KEEP_TEST_ORACLE. Existing test fixture names and assertions must remain stable.

Test discovery requires root tests/test_*.py, tests/apps/api fixture scope, CI patterns, golden hashes. There is **no new production function body to extract** from these RFs. Correct tests/fixtures are one-line KEEP_OK with path, reason, blob; no rerun for unchanged file.

## Every owned file: source to target and decision

| SOURCE | TARGET | blob / bytes | reason |
|---|---|---|---|
| `tests/test_broker_alignment.py` | `tests/test_broker_alignment.py` | `c57d6c711203` / 1396 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_broker_closed_trade_reconciler.py` | `tests/test_broker_closed_trade_reconciler.py` | `f09335312c5e` / 14850 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_broker_cost_profile.py` | `tests/test_broker_cost_profile.py` | `2defe185602f` / 4558 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_broker_outcome_fallback_truth.py` | `tests/test_broker_outcome_fallback_truth.py` | `ff67aeca804d` / 9766 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_broker_trade_reconciliation.py` | `tests/test_broker_trade_reconciliation.py` | `9a41946e7828` / 2063 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_build_risk_context.py` | `tests/test_build_risk_context.py` | `f5bdb9023e72` / 1936 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_daily_uef_pipeline.py` | `tests/test_daily_uef_pipeline.py` | `8cd223b95035` / 35699 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_daily_uef_run_status.py` | `tests/test_daily_uef_run_status.py` | `c72476fb5949` / 7530 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_host_supervisor.py` | `tests/test_host_supervisor.py` | `0607876ce1a0` / 2310 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_kiwoom_order_fill_reader.py` | `tests/test_kiwoom_order_fill_reader.py` | `63b1f682c09a` / 4188 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m17_risk_decision.py` | `tests/test_m17_risk_decision.py` | `988650476873` / 4545 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m18_5_risk_off_candidate_count.py` | `tests/test_m18_5_risk_off_candidate_count.py` | `4af5023f47d8` / 598 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_mock_executor.py` | `tests/test_mock_executor.py` | `99a4384402f9` / 519 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_order_client.py` | `tests/test_order_client.py` | `bcdc8ec4f8b2` / 1461 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p0a_e2e_open_order_guard_integrated_chain.py` | `tests/test_p0a_e2e_open_order_guard_integrated_chain.py` | `d26a74827784` / 7335 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p0a_open_order_reconciliation_guard.py` | `tests/test_p0a_open_order_reconciliation_guard.py` | `d7f19be16b99` / 11513 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p0b_step5d_crash_reconciliation.py` | `tests/test_p0b_step5d_crash_reconciliation.py` | `33e87d168852` / 6946 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p166_v1052_candidate_risk_migration.py` | `tests/test_p166_v1052_candidate_risk_migration.py` | `eb6367fa9292` / 7443 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p1_3_broker_read_write_gate.py` | `tests/test_p1_3_broker_read_write_gate.py` | `70ae363aa3d5` / 6777 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_pre_step5c_owner_regressions.py` | `tests/test_pre_step5c_owner_regressions.py` | `7ef763f327f5` / 4109 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_real_executor_disabled.py` | `tests/test_real_executor_disabled.py` | `69010cd8f845` / 696 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_real_executor_mock_mode_allowed.py` | `tests/test_real_executor_mock_mode_allowed.py` | `8b6553ef6d37` / 5283 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5b_broker_submission_safety.py` | `tests/test_step5b_broker_submission_safety.py` | `1f16f431bed8` / 15230 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5b_fix3.py` | `tests/test_step5b_fix3.py` | `152e8b872e38` / 14109 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5b_fix4.py` | `tests/test_step5b_fix4.py` | `46b3f4b7974c` / 20817 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5b_fix5.py` | `tests/test_step5b_fix5.py` | `74fc93f4da68` / 15467 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5b_safety_fix.py` | `tests/test_step5b_safety_fix.py` | `d2f01220f090` / 25108 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5c_execution_owner.py` | `tests/test_step5c_execution_owner.py` | `068fac993a23` / 12635 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5c_fix1_shared_ownership.py` | `tests/test_step5c_fix1_shared_ownership.py` | `a9917fcacd8f` / 18611 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5c_fix2_ownership_capability.py` | `tests/test_step5c_fix2_ownership_capability.py` | `0dfbd83431b7` / 26021 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5c_fix3_authoritative_intent.py` | `tests/test_step5c_fix3_authoritative_intent.py` | `1c868a245834` / 31535 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5c_fix4_broker_semantics_authority.py` | `tests/test_step5c_fix4_broker_semantics_authority.py` | `fd0159e432b1` / 5197 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_step5c_fix5_mutation_failclosed_and_consumer_only.py` | `tests/test_step5c_fix5_mutation_failclosed_and_consumer_only.py` | `1eb1ef388a3d` / 23489 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_supervisor.py` | `tests/test_supervisor.py` | `675d90cc8336` / 4727 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef1_work_package_a_canonical_contract.py` | `tests/test_uef1_work_package_a_canonical_contract.py` | `5496edd06fd2` / 102520 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef2a_boundary_closure_profiles.py` | `tests/test_uef2a_boundary_closure_profiles.py` | `316286bf4091` / 14351 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef2a_forward_policy_contract.py` | `tests/test_uef2a_forward_policy_contract.py` | `7ad443b01983` / 58660 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef2b_engine_primitives.py` | `tests/test_uef2b_engine_primitives.py` | `a08ac5783131` / 24414 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef2b_fix1_regressions.py` | `tests/test_uef2b_fix1_regressions.py` | `2861e1693cca` / 19542 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef2b_profile_execution.py` | `tests/test_uef2b_profile_execution.py` | `ee87832e27c6` / 30833 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef3a_cost_metric_contract.py` | `tests/test_uef3a_cost_metric_contract.py` | `b5b335308fbd` / 53246 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef3b_cost_metric_engine.py` | `tests/test_uef3b_cost_metric_engine.py` | `febb46005fc4` / 24176 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef3c_aggregation_pipeline.py` | `tests/test_uef3c_aggregation_pipeline.py` | `039ce83bf4c8` / 29198 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef4b1_q10_semiconductor_adapter.py` | `tests/test_uef4b1_q10_semiconductor_adapter.py` | `0fcd00dd2152` / 23022 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef4b2_q12_adapter.py` | `tests/test_uef4b2_q12_adapter.py` | `164f4be88894` / 39621 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef4b3_opening_shadow_adapter.py` | `tests/test_uef4b3_opening_shadow_adapter.py` | `8ea308eeb17c` / 45091 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef4b4_q10_index_adapter.py` | `tests/test_uef4b4_q10_index_adapter.py` | `955dfa87f102` / 38279 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef4b5_q11_adapter.py` | `tests/test_uef4b5_q11_adapter.py` | `30469ffeb61a` / 26454 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef4b6_q9_adapter.py` | `tests/test_uef4b6_q9_adapter.py` | `b73e6af5f92a` / 28010 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef5_1_clean_evidence_registry.py` | `tests/test_uef5_1_clean_evidence_registry.py` | `2e8172df1afe` / 45576 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef5_2_historical_recompute.py` | `tests/test_uef5_2_historical_recompute.py` | `cfe89854f9b5` / 48661 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef5_2_session_policy.py` | `tests/test_uef5_2_session_policy.py` | `225bff7a25de` / 5709 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef5_3_dual_run.py` | `tests/test_uef5_3_dual_run.py` | `c72326496c4e` / 42174 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef6_dedup_detection.py` | `tests/test_uef6_dedup_detection.py` | `ce966cc7ac09` / 21563 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef6_lineage_sidecar.py` | `tests/test_uef6_lineage_sidecar.py` | `28755c58478f` / 15674 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef6c_historical_validation.py` | `tests/test_uef6c_historical_validation.py` | `38afbc21a504` / 27285 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef7_alpha_board_normalization.py` | `tests/test_uef7_alpha_board_normalization.py` | `0e5dabc99563` / 26373 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef8_fair_comparison_validation.py` | `tests/test_uef8_fair_comparison_validation.py` | `5d8e8971daf2` / 30273 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_uef9_formal_authority.py` | `tests/test_uef9_formal_authority.py` | `c351ee2a1d4a` / 11526 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |

## Acceptance and delivery

- One-line source blob and correct test owner/path is KEEP_OK; test/fixture refactoring itself not a code-body MOVE metric.
- A/B do not read this RF file. C03 decides KEEP from file/consumers, and adds only new genuine source functions into C01/C02 text when needed.
- No modification to test assertions, skips, xfails, golden snapshots or staged deployment requirements as a shortcut to PASS. Historical prior tests retained; not rerun for identical blob.
