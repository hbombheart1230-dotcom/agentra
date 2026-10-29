# P1.5 신규 테스트 exact-path 단일 Owner 예외 (2026-10-28 C03→C05)

**결정:** [C03 #36 댓글 6465609676](https://github.com/hbombheart1230-dotcom/agentra/issues/36#issuecomment-6465609676). **확인 소스:** Claude A 원격 `39eaa4a0df1ec3c6148960d0aa8c0a58720d6bae` (10개 신규 테스트 blob). RF-074 원래 BASE `63182ab27ecf889768003f637a40577ba1277f86`의 75개 TEST_ORACLE 및 정규식은 변경하지 않는다.

**소유권 우선순위:** (1) 아래 신규 exact path 10개는 RF-031/RF-040에 단일 귀속, (2) 기존 BASE FILE_COVERAGE CSV의 75개 RF-074 파일은 그대로 RF-074, (3) 그 외 RF-074 broad regex는 후보 매칭일 뿐 다른 RF exact-path 소유권을 덮어쓰지 않는다. 이 규칙은 [FILE_COVERAGE CSV](FILE_COVERAGE_63182ab2.csv) 10개 신규 행과 함께 적용한다. 새 파일의 CSV `baseline_sha` 열은 기존 BASE 매핑 기준을 표시하며 **그 파일이 BASE에 존재했다는 뜻이 아니다**. 신규 행의 `UNVERIFIED`는 전체 C5/CI 검증 완료를 뜻하지 않는다.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf031_reporter_ai_review_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_reporter_analysis_callers.py` | RF-031 / Claude A |
| `tests/test_rf031_reporter_analysis_writers.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_runtime_generation_plan.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_runtime_policy_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_story_human_payloads_contract.py` | RF-031 / Claude A |
| `tests/test_rf040_libs_agent_reporter_agent.py` | RF-040 / Claude A |
| `tests/test_rf040_libs_agent_reporter_dtos.py` | RF-040 / Claude A |
| `tests/test_rf040_libs_agent_reporter_hooks.py` | RF-040 / Claude A |
| `tests/test_rf040_libs_agent_reporter_result.py` | RF-040 / Claude A |

**C05 신규 exact-path 보강 (2026-10-28 20:52 KST):** A 원격 `3afbb9c6`의 RF-051 신규 테스트 2개 blob 확인, CSV 단일 Owner RF-051 귀속. RF-074 frozen 75 및 기존 10개 예외 불변. C03 [#36 `6468496083`](https://github.com/hbombheart1230-dotcom/agentra/issues/36#issuecomment-6468496083)에서 혼합 신규 테스트 2개 exact-path 단일 Owner 확정. 원격 A `3afbb9c6` blob `29a07609`/`b5d455e0` 확인, CSV 반영. validator NOT_RUN.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf051_libs_market_global_sentiment_signal_branches.py` | RF-051 / Claude A |
| `tests/test_rf051_libs_market_q10_collector_residual_contract.py` | RF-051 / Claude A |
| `tests/test_rf040_058_054_residual_gaps_contract.py` | RF-040 / Claude A |
| `tests/test_rf054_058_040_final_residual_contract.py` | RF-054 / Claude A |

**C05 신규 exact-path 3개 보강 (2026-10-28 23:50 KST):** A #11 `6471660140` 원격 `2445dbd5`의 3개 blob 확인. 기존 RF-031 exact-path 우선순위에 따라 RF-031 단일 Owner, RF-074 frozen 75개 불변. 정규식 validator 실제 실행은 NOT_RUN; 이 결정은 C5 전체 MET가 아니다.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf031_reporter_analysis_helpers_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_reporter_analysis_optional_writers_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_reporter_feedback_helpers_contract.py` | RF-031 / Claude A |

**C05 2026-10-29 00:50 KST 신규 exact-path 소유권:** A #11 `6473163851` 원격 `b203ad0108bc9f60b84c7f788a26b0c16ce83846` 신규 RF-031 3개와 B #12 `6472816538` 원격 `031de036ad826c92bb2c525012c22afe49b28c0c` 신규 RF-044 1개를 blob 조회 후 CSV 단일 소유로 확정. RF-031 세 경로는 RF-074 broad regex보다 exact-path가 우선하며 기존 frozen 75개 불변. RF-044 경로는 별도 owner로 귀속. 정규식 validator NOT_RUN, C5 전체 MET 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf031_trade_report_deterministic_seed_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_compact_input_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_strategy_memory_labels_contract.py` | RF-031 / Claude A |
| `tests/test_rf044_executor_error_serialization.py` | RF-044 / Codex B |

**C05 2026-10-29 01:50 KST 추가 exact-path 판정:** A #11 `6474598614`·`6474606575` exact `a17be883681b1bfeb7dcc9f8632b833d3cf4b5b5`에서 이전 `b203ad01` 대비 신규 **3파일**(보고의 '4파일'은 commit diff 기준 정정), B #12 `6474340889` exact `daf50d88d1086844e7d20a75e75e9d3beaf07ce6` 신규 1파일. 4개 GitHub blob 검증, CSV 단일 Owner 4행 추가. RF-074 기존 75개 frozen test·regex 변경 없음. 정규식 validator 실행 NOT_RUN; 전체 C5 MET 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf031_trade_report_ai_helpers_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_alias_modules_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_markdown_clean_wrappers_contract.py` | RF-031 / Claude A |
| `tests/test_rf066_temp_contamination_cleanup.py` | RF-066 / Codex B |

**C05 2026-10-29 02:50 KST 신규 exact-path 소유권:** B #12 `6475690024` 정확 `4b926c2e0544d6055356f78159d4c92b6f63f412`의 신규 테스트 1개(blob `5c15e24ccec16e9fcdf873328a225e92b7e10edc`)를 RF-066 단일 Owner로 확정. RF-074 frozen 75·기존 regex 불변, validator NOT_RUN, C5 전체 MET 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf066_q9_compaction_exception.py` | RF-066 / Codex B |

**C05 2026-10-29 03:49 KST RF-045 신규 exact-path:** B #12 `6476896617` source `bccefd46460bcfe307883d5a66b129e8422a053b` 신규 테스트 blob `fd535aa45c4f522bbe7a60f4fa548115893bd5d0` 확인. A #11 `6476966310` 동일 SHA scoped peer(전체 C4 아님). CSV 단일 RF-045 Owner; RF-074 기존 frozen 75·regex 불변. validator NOT_RUN, C5 전체 MET 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf045_http_retry_boundary.py` | RF-045 / Codex B |

**C05 2026-10-29 04:52 KST 신규 exact-path:** B #12 `6478221506` SOURCE `938ff945`의 두 테스트 blob 검증, A #11 `6478258552` scoped peer. RF-074 frozen 75·regex 변경 없음. validator NOT_RUN, 전체 C5 MET 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf044_supervisor_blocked_consumer.py` | RF-044 / Codex B |
| `tests/test_rf045_event_logger_compat_consumer.py` | RF-045 / Codex B |

**C05 2026-10-29 05:50 KST 신규 exact-path:** B #12 [6479456046](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6479456046) SOURCE `da64f7cde07895f81ba73ae2367b9cfea670f299`의 M7 fake OrderClient 테스트 blob `f0d1098e6324cc86d9ade81496de4537612f503f`를 원격 확인, A #11 [6479610575](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6479610575) 같은 SOURCE scoped peer. RF-066 단일 Owner, RF-074 frozen 75 불변. 전체 C5 MET·CI 승인 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf066_m7_fake_order_client_consumer.py` | RF-066 / Codex B |

**C05 2026-10-29 06:50 KST 신규 exact-path 소유권:** B #12 [6480837180](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6480837180) SOURCE `ca7f9af6`에서 신규 2파일 blob `890cadee`/`37c5cd51` 확인, A #11 [6480910762](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6480910762) exact-source scoped peer. CSV 단일 Owner 2행 추가, RF-074 기존 frozen 75·regex 불변. 전체 C5 MET/CI 승인 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf045_event_logger_compat_attribute_exception.py` | RF-045 / Codex B |
| `tests/test_rf066_m22_skill_demo_timeout_consumer.py` | RF-066 / Codex B |

**C05 2026-10-29 07:50 KST 신규 exact-path 8개 Owner:** #11 648193~648220, #12 6482066851/6482085416. 원격 A/B 파일 blob 확인. CSV 4039 unique, RF-074 frozen 75·regex 불변. 전체 C5 및 validator PASS 아님.

| 신규 exact path | 단일 Owner | 원격 blob |
|---|---|---|
| tests/test_rf031_reporter_ai_review_caller_contract.py | RF-031 / Claude A | a89ad4772aa8 |
| tests/test_rf051_market_owner_action_inventory.py | RF-051 / Claude A | 3474664d79bc |
| tests/test_rf051_market_import_surface_guard.py | RF-051 / Claude A | dfb60ef86c20 |
| tests/test_rf050_openrouter_client_fake_http_contract.py | RF-050 / Claude A | 11add9bd0ec0 |
| tests/test_rf050_model_catalog_store_fake_http_contract.py | RF-050 / Claude A | 25d0cd1d1a4b |
| tests/test_rf041_openai_provider_helpers_fake_http_contract.py | RF-041 / Claude A | a22fc6137ef5 |
| tests/test_rf066_m22_graph_offline_policy.py | RF-066 / Codex B | e728d97ea3d2 |
| tests/test_rf045_http_retry_method_backoff.py | RF-045 / Codex B | 749d64232bb7 |

**검증 경계:** C05가 위 원격 A 10개 blob·CSV 경로 유일성·RF 원본을 대조했다. 기존 75 frozen test/regex rename·rewrite 0. 별도의 정규식 기반 자동 검사기가 CSV 우선순위를 실제로 구현/준수하는지 실행 검증은 **NOT_RUN**이다. 해당 검증기가 exact-path 예외를 무시하면 소유권 검사 적용은 **BLOCKED**, 지팀장 승인 하에 validator 예외 처리를 별도 작업해야 한다. 이 예외 자체는 RF-031/040/054/058/074 C5 MET, full opposite peer, CI 또는 DONE을 승인하지 않는다.

**C05 2026-10-29 08:50 KST 신규 exact-path 18개:** A `46be5bea..a68acfc5`의 RF-033/034 신규 14파일, B `be28e9c1..4a329361`의 RF-044/066 신규 4파일 원격 compare에서 확인. A RF-041 `tests/test_rf041_openai_provider_helpers_fake_http_contract.py`는 이미 CSV에 RF-041로 귀속되어 있어 중복 추가하지 않음. CSV 4057 unique, RF-074 frozen 75 불변. 정규식 validator·공식 sync NOT_RUN, full C4/CI/DONE 승인 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf033_btc_data_provider_fake_yfinance_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_btc_historical_review_tmp_root_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_btc_vnext_equities_alignment_fake_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_btc_vnext_storage_pipeline_tmp_root_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_crypto_fear_greed_fake_http_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_samsung_forward_validation_capture_tmp_root_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_samsung_market_inputs_and_provider_fake_contract.py` | RF-033 / Claude A |
| `tests/test_rf034_alpha_board_writer_scope_tmp_root_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_five_session_review_tmp_root_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_latent_forward_tmp_root_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_latent_watch_tmp_root_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_pipeline_day_status_tmp_root_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_quant_trade_diagnosis_writer_tmp_root_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_short_alpha_pipeline_status_tmp_root_contract.py` | RF-034 / Claude A |
| `tests/test_rf044_executor_input_immutability.py` | RF-044 / Codex B |
| `tests/test_rf066_log_maintenance_temp_effects.py` | RF-066 / Codex B |
| `tests/test_rf066_m22_graph_temp_cwd_effects.py` | RF-066 / Codex B |
| `tests/test_rf066_report_maintenance_temp_effects.py` | RF-066 / Codex B |

**C05 2026-10-29 09:55 KST 신규 exact-path 21개:** A `a68acfc5..8bdbd5ab` 19개(RF-033 9/RF-034 10), B `4a329361..801ca211` 2개(RF-045 1/RF-066 1). GitHub 원격 compare의 added 파일만 반영. CSV 4078 unique, RF-074 frozen 75 불변. C5 PARTIAL이며 C1~C4 full, CI, DONE 승인 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf033_btc_hypothesis_features_daily_context_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_btc_input_worker_stubbed_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_btc_point_in_time_capture_paths_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_samsung_forward_reaction_reader_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_samsung_forward_report_render_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_samsung_forward_returns_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_samsung_forward_scoring_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_samsung_forward_shadow_comparison_contract.py` | RF-033 / Claude A |
| `tests/test_rf033_samsung_q9_comparison_stubbed_contract.py` | RF-033 / Claude A |
| `tests/test_rf034_alpha_board_canonical_status_tables_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_alpha_board_loaders_large_cap_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_alpha_board_runtime_validation_boundaries_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_alpha_board_sensitivity_remaining_reviews_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_candle_provider_fake_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_episodes_stubbed_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_extraction_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_metrics_promotion_gates_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_observability_contract.py` | RF-034 / Claude A |
| `tests/test_rf034_opening_snapshot_metadata_conditional_alpha_contract.py` | RF-034 / Claude A |
| `tests/test_rf045_event_logger_real_compat.py` | RF-045 / Codex B |
| `tests/test_rf066_sync_legacy_brief_llm_cli.py` | RF-066 / Codex B |
| `tests/test_p15_btc_forward_report_parity.py` | RF-033 / Claude A |
| `tests/test_p15_collector_observations_extraction.py` | RF-033 / Claude A |
| `tests/test_p15_forward_validation_parity_chain.py` | RF-033 / Claude A |
| `tests/test_p15_index_timeline_extraction.py` | RF-033 / Claude A |
| `tests/test_p15_stock_reaction_extraction.py` | RF-033 / Claude A |
| `tests/test_p15_event_logger_caller_bridge.py` | RF-045 / Codex B |
| `tests/test_p15_scanner_projection_extraction.py` | RF-044 / Codex B |
| `tests/test_p15_strategist_projection_extraction.py` | RF-044 / Codex B |

**C05 2026-10-29 13:39 KST 신규 exact-path 단일 Owner:** A 원격 SOURCE `32d86ba`에서 아래 5개 테스트 파일 blob 직접 확인. FILE_COVERAGE CSV 4092→4097 unique, RF-074 frozen 75 불변. 전체 C5/CI 승인 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_p15_q10_cumulative_malformed_inputs.py` | RF-033 / Claude A |
| `tests/test_p15_q10_cumulative_numeric_boundary.py` | RF-033 / Claude A |
| `tests/test_p15_q10_forward_pipeline_temp_contract.py` | RF-033 / Claude A |
| `tests/test_p15_q10_preopen_capture_temp_contract.py` | RF-033 / Claude A |
| `tests/test_p15_q10_report_missing_value_contract.py` | RF-033 / Claude A |

**C05 2026-10-29 15:39 KST 신규 exact-path 단일 Owner:** A `2bce7dca`, B `312a5161` 원격 blob 확인. 9개 신규 테스트 CSV 등록; RF-074 frozen 75 불변. B 새 4파일의 repository pytest normal/`-O` NOT_RUN.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_p15_event_logger_constructor_matrix.py` | RF-045 / Codex B |
| `tests/test_p15_latent_forward_cache_root_injection.py` | RF-034 / Claude A |
| `tests/test_p15_log_move_root_boundary.py` | RF-045 / Codex B |
| `tests/test_p15_model_catalog_malformed_cards.py` | RF-050 / Claude A |
| `tests/test_p15_q9_malformed_rank_contract.py` | RF-033 / Claude A |
| `tests/test_p15_q9_offline_optout.py` | RF-033 / Claude A |
| `tests/test_p15_quant_diagnosis_batch_alignment.py` | RF-034 / Claude A |
| `tests/test_p15_run_log_maintenance_temp_cli.py` | RF-066 / Codex B |
| `tests/test_p15_sync_legacy_brief_no_write_cli.py` | RF-066 / Codex B |
