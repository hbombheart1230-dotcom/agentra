# RF-081 — 코드 구조/함수 재배치 설계 (T06)

## T06 roadmap OWNER 최종 판정
- docs/plan/ and docs/roadmap/: retained historical plans, not active execution authority over C01/C02.
- Historical document code examples are not operative source functions, and do not justify creating new Python modules.
- Path/link valid and single role yields KEEP_OK in one line with blob; no file moves just for tidiness.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-081.md` blob `fcb0e7674b8b0f450031cd7991db42e474403e31`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 198개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `docs/plan/M9_read_layer_summary.md` → `docs/plan/M9_read_layer_summary.md` | 1466 | `2b626c76d116` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/approval_env_notes.md` → `docs/plan/approval_env_notes.md` | 586 | `775e2a4ac9ce` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/README.md` → `docs/plan/archive/README.md` | 333 | `e9f65a042667` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m3_api_discovery.md` → `docs/plan/archive/m3_api_discovery.md` | 428 | `5f60c8f65f17` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m4_api_planner.md` → `docs/plan/archive/m4_api_planner.md` | 293 | `ba05db66b973` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m5_prepare_request.md` → `docs/plan/archive/m5_prepare_request.md` | 351 | `1a7948e5b762` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m6_closeout.md` → `docs/plan/archive/m6_closeout.md` | 379 | `fec4cfe7654b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m6_http_client.md` → `docs/plan/archive/m6_http_client.md` | 298 | `7e7da7cd429e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m6_readonly_account.md` → `docs/plan/archive/m6_readonly_account.md` | 351 | `06faa1bbdcf1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m6_settings.md` → `docs/plan/archive/m6_settings.md` | 541 | `71dc0dbc356c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m6_token_client.md` → `docs/plan/archive/m6_token_client.md` | 612 | `5aa467911028` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m7_closeout.md` → `docs/plan/archive/m7_closeout.md` | 947 | `26e5a2897ac1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m7_order_dry_run.md` → `docs/plan/archive/m7_order_dry_run.md` | 600 | `0a033e399ae0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m7_readme_append.md` → `docs/plan/archive/m7_readme_append.md` | 393 | `c854fb978904` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/archive/m7_supervisor.md` → `docs/plan/archive/m7_supervisor.md` | 579 | `9d83ee2a9752` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/default_rules.md` → `docs/plan/default_rules.md` | 602 | `b56f704d3cb9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/kiwoom_agentic_trader_plan.md` → `docs/plan/kiwoom_agentic_trader_plan.md` | 3344 | `4401abf87f0c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/kiwoom_agentic_trader_plan_v2.md` → `docs/plan/kiwoom_agentic_trader_plan_v2.md` | 4551 | `94f8b3dcc22a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m10_live_pipeline.md` → `docs/plan/m10_live_pipeline.md` | 2099 | `ec2632bb2068` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m11_2_scanner.md` → `docs/plan/m11_2_scanner.md` | 964 | `dadd5488f56a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m11_4_logging_and_reports.md` → `docs/plan/m11_4_logging_and_reports.md` | 1049 | `567bfe6b9c6a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m12_1_provider_routing.md` → `docs/plan/m12_1_provider_routing.md` | 1076 | `ba33cbbfdb94` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m12_2_llm_strategist_http.md` → `docs/plan/m12_2_llm_strategist_http.md` | 983 | `e92114128885` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m12_3_intent_schema_validation.md` → `docs/plan/m12_3_intent_schema_validation.md` | 881 | `ae11bc8b964c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m12_ai_hook.md` → `docs/plan/m12_ai_hook.md` | 775 | `60a254990397` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m13_runtime_loop.md` → `docs/plan/m13_runtime_loop.md` | 569 | `4b905431c14f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m14_after.md` → `docs/plan/m14_after.md` | 2434 | `cc8369078cde` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m14_mock_account_execution.md` → `docs/plan/m14_mock_account_execution.md` | 3059 | `1e78b86a2c59` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m14_mock_account_integration.md` → `docs/plan/m14_mock_account_integration.md` | 2564 | `47794018f27e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m15_structure.md` → `docs/plan/m15_structure.md` | 786 | `da65ea132f34` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m16_approval_api.md` → `docs/plan/m16_approval_api.md` | 2106 | `30273fa2e6e9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m17_graph_spine_and_risk.md` → `docs/plan/m17_graph_spine_and_risk.md` | 1942 | `564c394198c8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m18_1_market_scan_candidates.md` → `docs/plan/m18_1_market_scan_candidates.md` | 1313 | `df333e66897b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m18_2_top_picks.md` → `docs/plan/m18_2_top_picks.md` | 880 | `61d24ea6717b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m18_3_sentiment_integration.md` → `docs/plan/m18_3_sentiment_integration.md` | 1344 | `adad101c974e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m18_4_scanner_scoring.md` → `docs/plan/m18_4_scanner_scoring.md` | 1886 | `561bd6d1104e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m18_5_candidate_ranking.md` → `docs/plan/m18_5_candidate_ranking.md` | 1969 | `bec92252f20f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m18_6_news_plugin.md` → `docs/plan/m18_6_news_plugin.md` | 1608 | `4656c51e212b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m18_8_9_news_scorer_and_global_sentiment.md` → `docs/plan/m18_8_9_news_scorer_and_global_sentiment.md` | 1365 | `a61484f52329` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m18_strategist_signals.md` → `docs/plan/m18_strategist_signals.md` | 1698 | `7a15ced80e79` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m19_1_naver_news_provider.md` → `docs/plan/m19_1_naver_news_provider.md` | 1001 | `5c53580b1f4d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m19_2_global_sentiment.md` → `docs/plan/m19_2_global_sentiment.md` | 1970 | `0bd05b5a4817` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m19_4_openrouter_news_scorer.md` → `docs/plan/m19_4_openrouter_news_scorer.md` | 1603 | `ad3968a5eb4b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m19_5_llm_routing_openrouter.md` → `docs/plan/m19_5_llm_routing_openrouter.md` | 2184 | `b58bf5e1e023` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m19_6_llm_daily_report.md` → `docs/plan/m19_6_llm_daily_report.md` | 1089 | `dfdb7840bf68` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_10_circuit_metrics_report.md` → `docs/plan/m20_10_circuit_metrics_report.md` | 848 | `243aed5cb480` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_1_llm_smoke_and_fallback.md` → `docs/plan/m20_1_llm_smoke_and_fallback.md` | 2932 | `29bc37f55e9e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_2_schema_retry_telemetry.md` → `docs/plan/m20_2_schema_retry_telemetry.md` | 3179 | `0fa515fe3d68` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_3_legacy_llm_router_compat.md` → `docs/plan/m20_3_legacy_llm_router_compat.md` | 1375 | `f7854a3a0c65` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_4_smoke_and_llm_event_query.md` → `docs/plan/m20_4_smoke_and_llm_event_query.md` | 2056 | `96b922164a9a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_5_llm_metrics_dashboard.md` → `docs/plan/m20_5_llm_metrics_dashboard.md` | 1678 | `0829c9496169` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_6_prompt_schema_version_telemetry.md` → `docs/plan/m20_6_prompt_schema_version_telemetry.md` | 2387 | `5ad2ced76cf8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_7_token_cost_telemetry.md` → `docs/plan/m20_7_token_cost_telemetry.md` | 2571 | `9bafac2a19c3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_8_circuit_breaker_safe_fallback.md` → `docs/plan/m20_8_circuit_breaker_safe_fallback.md` | 1123 | `eadcb4d72504` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_9_circuit_event_visibility.md` → `docs/plan/m20_9_circuit_event_visibility.md` | 817 | `bc9bd97efa82` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m20_to_m30_master_plan.md` → `docs/plan/m20_to_m30_master_plan.md` | 9346 | `715810702618` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_10_docs_sync_closeout.md` → `docs/plan/m21_10_docs_sync_closeout.md` | 722 | `08e37c786373` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_1_canonical_runtime_entry.md` → `docs/plan/m21_1_canonical_runtime_entry.md` | 1097 | `f444b7403965` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_2_runtime_mode_resolution_policy.md` → `docs/plan/m21_2_runtime_mode_resolution_policy.md` | 979 | `6b9c568f1930` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_3_decision_packet_activation_guard.md` → `docs/plan/m21_3_decision_packet_activation_guard.md` | 987 | `dd4a3fecff17` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_4_runtime_transitions.md` → `docs/plan/m21_4_runtime_transitions.md` | 1225 | `a44ea11a26c2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_5_runtime_agent_chain_mapping.md` → `docs/plan/m21_5_runtime_agent_chain_mapping.md` | 1123 | `a8010e064d04` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_6_runtime_once_cli.md` → `docs/plan/m21_6_runtime_once_cli.md` | 1172 | `3e57ba6c543a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_7_commander_router_event_logging.md` → `docs/plan/m21_7_commander_router_event_logging.md` | 1070 | `ec7e77e144da` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_8_graph_spine_parity_tests.md` → `docs/plan/m21_8_graph_spine_parity_tests.md` | 760 | `765b4c696383` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m21_9_commander_bridge_to_canonical_runtime.md` → `docs/plan/m21_9_commander_bridge_to_canonical_runtime.md` | 975 | `ba19c8e7ac5a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_10_closeout_and_handover.md` → `docs/plan/m22_10_closeout_and_handover.md` | 951 | `cdcbd8430948` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_1_skill_native_scanner_monitor_baseline.md` → `docs/plan/m22_1_skill_native_scanner_monitor_baseline.md` | 1708 | `ba9a6d58a8f6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_2_monitor_order_lifecycle.md` → `docs/plan/m22_2_monitor_order_lifecycle.md` | 1206 | `cbaf78be2e78` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_3_skill_timeout_error_quality_gates.md` → `docs/plan/m22_3_skill_timeout_error_quality_gates.md` | 1640 | `46f5fd50da6c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_4_skill_dto_contract_standardization.md` → `docs/plan/m22_4_skill_dto_contract_standardization.md` | 1570 | `fd0fd0f62246` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_5_skill_hydration_node.md` → `docs/plan/m22_5_skill_hydration_node.md` | 1477 | `9340b713b2f0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_6_graph_hydration_wiring.md` → `docs/plan/m22_6_graph_hydration_wiring.md` | 1451 | `e1a2766a9799` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_7_hydration_smoke_gate.md` → `docs/plan/m22_7_hydration_smoke_gate.md` | 1025 | `bb34650d4976` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_8_auto_composite_runner_connection.md` → `docs/plan/m22_8_auto_composite_runner_connection.md` | 1377 | `d49aca3d28f9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m22_9_hydration_metrics_reporting.md` → `docs/plan/m22_9_hydration_metrics_reporting.md` | 1485 | `d3093447d78e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_10_closeout_and_m24_handover.md` → `docs/plan/m23_10_closeout_and_m24_handover.md` | 1434 | `529c746df810` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_1_runtime_resilience_state_contract.md` → `docs/plan/m23_1_runtime_resilience_state_contract.md` | 1303 | `ed4705563a63` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_2_runtime_circuit_breaker_core.md` → `docs/plan/m23_2_runtime_circuit_breaker_core.md` | 1462 | `5aa6c3bd9c98` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_3_strategist_runtime_circuit_integration.md` → `docs/plan/m23_3_strategist_runtime_circuit_integration.md` | 1265 | `d11acd509715` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_4_commander_incident_cooldown_routing.md` → `docs/plan/m23_4_commander_incident_cooldown_routing.md` | 1756 | `5477179abdbe` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_5_safe_degrade_execution_policy.md` → `docs/plan/m23_5_safe_degrade_execution_policy.md` | 1804 | `b9a54627d177` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_6_operator_intervention_resume_runbook.md` → `docs/plan/m23_6_operator_intervention_resume_runbook.md` | 2069 | `49a3650922cf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_7_commander_resilience_ops_visibility.md` → `docs/plan/m23_7_commander_resilience_ops_visibility.md` | 1668 | `c2fed786ae4d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_8_resilience_closeout_and_handover.md` → `docs/plan/m23_8_resilience_closeout_and_handover.md` | 1158 | `8b1702c334d4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m23_9_commander_resilience_metrics_reporting.md` → `docs/plan/m23_9_commander_resilience_metrics_reporting.md` | 1102 | `14860f3eabf6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m24_1_intent_journal_state_machine_sqlite.md` → `docs/plan/m24_1_intent_journal_state_machine_sqlite.md` | 1572 | `4ebc4cc90f8e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m24_2_approval_flow_sqlite_state_integration.md` → `docs/plan/m24_2_approval_flow_sqlite_state_integration.md` | 1589 | `4f92e84349a7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m24_3_duplicate_execution_claim_guard.md` → `docs/plan/m24_3_duplicate_execution_claim_guard.md` | 1422 | `0b78299e148b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m24_4_intent_state_reconciliation_tooling.md` → `docs/plan/m24_4_intent_state_reconciliation_tooling.md` | 1231 | `0670cb846f72` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m24_5_real_execution_preflight_denial_reasons.md` → `docs/plan/m24_5_real_execution_preflight_denial_reasons.md` | 1754 | `fc7b441e3625` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m24_6_guard_precedence_regression_bundle.md` → `docs/plan/m24_6_guard_precedence_regression_bundle.md` | 984 | `9f9b47bb2fd0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m24_7_intent_state_ops_visibility.md` → `docs/plan/m24_7_intent_state_ops_visibility.md` | 1469 | `10ed7b47bfe0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m24_8_closeout_and_m25_handover.md` → `docs/plan/m24_8_closeout_and_m25_handover.md` | 1720 | `529bf7545a28` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_10_notification_event_log_and_query.md` → `docs/plan/m25_10_notification_event_log_and_query.md` | 1377 | `f2ede3d00ab7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_1_metric_schema_freeze_v1.md` → `docs/plan/m25_1_metric_schema_freeze_v1.md` | 1745 | `b9c9a7f7956e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_2_alert_policy_threshold_gate.md` → `docs/plan/m25_2_alert_policy_threshold_gate.md` | 1553 | `cde732c47abb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_3_alert_reporting_closeout.md` → `docs/plan/m25_3_alert_reporting_closeout.md` | 1143 | `e9b63c79ae4e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_4_alert_policy_env_profile.md` → `docs/plan/m25_4_alert_policy_env_profile.md` | 1382 | `60bbba253f53` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_5_ops_batch_hook.md` → `docs/plan/m25_5_ops_batch_hook.md` | 1149 | `b2892751d065` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_6_alert_channel_adapter.md` → `docs/plan/m25_6_alert_channel_adapter.md` | 1510 | `478d96720324` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_7_notification_noise_control.md` → `docs/plan/m25_7_notification_noise_control.md` | 1789 | `c95ad76fde62` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_8_slack_webhook_provider.md` → `docs/plan/m25_8_slack_webhook_provider.md` | 1356 | `b7edb0845256` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m25_9_notification_retry_policy.md` → `docs/plan/m25_9_notification_retry_policy.md` | 1449 | `581fb00372ae` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m26_1_fixed_dataset_manifest_scaffold.md` → `docs/plan/m26_1_fixed_dataset_manifest_scaffold.md` | 1372 | `97c0e364d1c4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m26_2_replay_runner_scaffold.md` → `docs/plan/m26_2_replay_runner_scaffold.md` | 1299 | `391937ed6260` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m26_3_scorecard_metrics.md` → `docs/plan/m26_3_scorecard_metrics.md` | 1301 | `2c8eade4d8b4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m26_4_ab_evaluation_scaffold.md` → `docs/plan/m26_4_ab_evaluation_scaffold.md` | 1294 | `d5ee01f30777` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m26_5_promotion_gate_check.md` → `docs/plan/m26_5_promotion_gate_check.md` | 1199 | `71d7aded8670` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m26_6_closeout_and_m27_handover.md` → `docs/plan/m26_6_closeout_and_m27_handover.md` | 1658 | `1b60f6c67c1b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_10_closeout_and_m28_handover.md` → `docs/plan/m27_10_closeout_and_m28_handover.md` | 2053 | `9f072593f856` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_1_multi_strategy_allocation_policy_scaffold.md` → `docs/plan/m27_1_multi_strategy_allocation_policy_scaffold.md` | 1679 | `d8ddbed54b73` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_2_intent_conflict_resolution_policy.md` → `docs/plan/m27_2_intent_conflict_resolution_policy.md` | 1708 | `f6ee5fbcf0a6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_3_portfolio_budget_boundary_guard.md` → `docs/plan/m27_3_portfolio_budget_boundary_guard.md` | 1843 | `f88836e56e6b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_4_runtime_portfolio_guard_integration.md` → `docs/plan/m27_4_runtime_portfolio_guard_integration.md` | 2170 | `69f0140baf15` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_5_portfolio_guard_metrics_reporting.md` → `docs/plan/m27_5_portfolio_guard_metrics_reporting.md` | 1698 | `e2aa03d99605` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_6_portfolio_guard_alert_policy.md` → `docs/plan/m27_6_portfolio_guard_alert_policy.md` | 1697 | `848bb5208a59` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_7_portfolio_guard_notify_context.md` → `docs/plan/m27_7_portfolio_guard_notify_context.md` | 1825 | `f35b43876ad4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_8_portfolio_guard_notify_routing.md` → `docs/plan/m27_8_portfolio_guard_notify_routing.md` | 1773 | `befda9b60bd0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m27_9_portfolio_guard_notify_ops_query.md` → `docs/plan/m27_9_portfolio_guard_notify_ops_query.md` | 1475 | `32d3c37c8f4a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_1_runtime_profile_scaffold.md` → `docs/plan/m28_1_runtime_profile_scaffold.md` | 1883 | `49455700e838` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_2_runtime_lifecycle_hooks.md` → `docs/plan/m28_2_runtime_lifecycle_hooks.md` | 1588 | `a7305191af39` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_3_rollout_checklist_and_rollback_procedure.md` → `docs/plan/m28_3_rollout_checklist_and_rollback_procedure.md` | 1374 | `319735a2363f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_4_startup_preflight_gate.md` → `docs/plan/m28_4_startup_preflight_gate.md` | 1521 | `603c051a3126` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_5_scheduler_worker_launch_wrapper.md` → `docs/plan/m28_5_scheduler_worker_launch_wrapper.md` | 1553 | `0882220b0cfb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_6_launch_hook_integration.md` → `docs/plan/m28_6_launch_hook_integration.md` | 1950 | `4d9664661fd5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_7_deploy_target_launch_templates.md` → `docs/plan/m28_7_deploy_target_launch_templates.md` | 1685 | `d87af7bc0cb6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_8_deployment_registration_helpers.md` → `docs/plan/m28_8_deployment_registration_helpers.md` | 1796 | `213750694e82` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m28_9_closeout_and_m29_handover.md` → `docs/plan/m28_9_closeout_and_m29_handover.md` | 2316 | `2ea93ebb0258` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_1_feature_engine_regime_scaffold.md` → `docs/plan/m29_1_feature_engine_regime_scaffold.md` | 1553 | `c135cb78106b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_2_monitor_exit_logic_scaffold.md` → `docs/plan/m29_2_monitor_exit_logic_scaffold.md` | 1107 | `0ff56755381a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_3_position_sizing_scaffold.md` → `docs/plan/m29_3_position_sizing_scaffold.md` | 1162 | `3f05541dc0e2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_4_monitor_metrics_reporting.md` → `docs/plan/m29_4_monitor_metrics_reporting.md` | 1191 | `5c73a5b8a1b6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_5_audit_trail_completeness_check.md` → `docs/plan/m29_5_audit_trail_completeness_check.md` | 1509 | `72e297387378` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_6_log_archive_integrity_check.md` → `docs/plan/m29_6_log_archive_integrity_check.md` | 1283 | `3a0d4237ff21` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_7_incident_timeline_reconstruction.md` → `docs/plan/m29_7_incident_timeline_reconstruction.md` | 1771 | `1531d0ca5536` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_8_disaster_recovery_drill_restore_replay.md` → `docs/plan/m29_8_disaster_recovery_drill_restore_replay.md` | 1297 | `4f141da9b220` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m29_9_governance_closeout_check.md` → `docs/plan/m29_9_governance_closeout_check.md` | 999 | `24354892793d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m30_1_quality_gates_bundle.md` → `docs/plan/m30_1_quality_gates_bundle.md` | 1007 | `d31816877854` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m30_2_release_signoff_checklist.md` → `docs/plan/m30_2_release_signoff_checklist.md` | 1130 | `5191e05fd55f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m30_3_post_golive_monitoring_escalation_policy.md` → `docs/plan/m30_3_post_golive_monitoring_escalation_policy.md` | 1111 | `faa75f1faa8b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m30_4_final_golive_signoff_aggregator.md` → `docs/plan/m30_4_final_golive_signoff_aggregator.md` | 994 | `adb5f0b8ff10` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_10_operator_visibility_layer.md` → `docs/plan/m31_10_operator_visibility_layer.md` | 2941 | `61bbe831c9ba` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_11_feature_engine_regime_phase1_upgrade.md` → `docs/plan/m31_11_feature_engine_regime_phase1_upgrade.md` | 1470 | `0d026c95ed5a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_12_strategy_v1_multi_strategy_registry.md` → `docs/plan/m31_12_strategy_v1_multi_strategy_registry.md` | 1848 | `cb00c25fe7b0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_13_universe_scanner_source_weighting_upgrade.md` → `docs/plan/m31_13_universe_scanner_source_weighting_upgrade.md` | 1977 | `0a7e0fb7f078` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_14_data_quality_signal_state_propagation.md` → `docs/plan/m31_14_data_quality_signal_state_propagation.md` | 2024 | `491b89b986e7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_15_strategy_v1_exam_baseline.md` → `docs/plan/m31_15_strategy_v1_exam_baseline.md` | 1821 | `34c2a1ec9d21` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_16_output_quality_validation.md` → `docs/plan/m31_16_output_quality_validation.md` | 1754 | `9205311c25c1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_17_strategist_theme_candidate_flow_upgrade.md` → `docs/plan/m31_17_strategist_theme_candidate_flow_upgrade.md` | 3290 | `3ce2a2b84b3b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_18_offhours_validation_loop.md` → `docs/plan/m31_18_offhours_validation_loop.md` | 2480 | `33f5e0122b59` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_19_trade_reconciliation_and_exit_guard_harmonization.md` → `docs/plan/m31_19_trade_reconciliation_and_exit_guard_harmonization.md` | 2100 | `54028a560464` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_1_slo_baseline_and_incident_review_workflow.md` → `docs/plan/m31_1_slo_baseline_and_incident_review_workflow.md` | 4305 | `412d9c40ce85` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_2_mock_investor_exam_protocol.md` → `docs/plan/m31_2_mock_investor_exam_protocol.md` | 8187 | `62a65f710f0b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_3_weekly_health_summary_operator_script.md` → `docs/plan/m31_3_weekly_health_summary_operator_script.md` | 1867 | `4f36367c0990` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_4_strategy_v1_bootstrap.md` → `docs/plan/m31_4_strategy_v1_bootstrap.md` | 1236 | `2d9e5130bc59` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_5_universe_builder_upgrade.md` → `docs/plan/m31_5_universe_builder_upgrade.md` | 1228 | `9cdce5f8721a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_6_data_quality_signal_propagation.md` → `docs/plan/m31_6_data_quality_signal_propagation.md` | 1154 | `0a5919c6b8fd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_7_feature_engine_regime_upgrade.md` → `docs/plan/m31_7_feature_engine_regime_upgrade.md` | 1384 | `dc8bac2b014d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_8_sizing_exit_explainability_upgrade.md` → `docs/plan/m31_8_sizing_exit_explainability_upgrade.md` | 2726 | `7770e62c86f8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_9_strategy_validation_tests_bundle.md` → `docs/plan/m31_9_strategy_validation_tests_bundle.md` | 1718 | `ebc72265f505` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_operational_readiness_audit_2026-03-08.md` → `docs/plan/m31_operational_readiness_audit_2026-03-08.md` | 6782 | `329811fa13bc` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_plus_progress_summary_2026-03-06.md` → `docs/plan/m31_plus_progress_summary_2026-03-06.md` | 3743 | `2c2945d9f54f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_plus_runtime_safety_patch_2026-03-07.md` → `docs/plan/m31_plus_runtime_safety_patch_2026-03-07.md` | 1698 | `6f1861f28aa2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m31_to_m36_post_golive_plan.md` → `docs/plan/m31_to_m36_post_golive_plan.md` | 6101 | `972883d520c1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m32_1_performance_and_cost_baseline.md` → `docs/plan/m32_1_performance_and_cost_baseline.md` | 2523 | `b1b2d8539bef` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m8_decision_packet.md` → `docs/plan/m8_decision_packet.md` | 785 | `c8bb1c7c5b64` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m8_executors.md` → `docs/plan/m8_executors.md` | 552 | `e2c93a0e8c1c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/m8_wiring.md` → `docs/plan/m8_wiring.md` | 400 | `489dea548e2b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/plan/why_scripts_vs_tests.md` → `docs/plan/why_scripts_vs_tests.md` | 968 | `9bdaf95ee909` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/chart_structure_feature_candidates_5_3_2.md` → `docs/roadmap/chart_structure_feature_candidates_5_3_2.md` | 12752 | `846137c84a9b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/env_inventory_current_runtime.md` → `docs/roadmap/env_inventory_current_runtime.md` | 19841 | `389f9560da70` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/monitor_scoring_5_1_2_design.md` → `docs/roadmap/monitor_scoring_5_1_2_design.md` | 12731 | `b449580054e4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/monitor_scoring_defer_note.md` → `docs/roadmap/monitor_scoring_defer_note.md` | 5951 | `6721f0b88b87` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/monitor_scoring_shadow_go_live_criteria.md` → `docs/roadmap/monitor_scoring_shadow_go_live_criteria.md` | 6345 | `330d95b1fa57` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/monitor_scoring_shadow_validation_note.md` → `docs/roadmap/monitor_scoring_shadow_validation_note.md` | 3694 | `7a175fd0113c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/operator_ui_defer_note.md` → `docs/roadmap/operator_ui_defer_note.md` | 3464 | `bec9f272ef3b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_2_1_close_note.md` → `docs/roadmap/phase_5_2_1_close_note.md` | 3626 | `149734e63548` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_2_1_status_note.md` → `docs/roadmap/phase_5_2_1_status_note.md` | 3023 | `f5e69a880e44` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_2_2_addendum.md` → `docs/roadmap/phase_5_2_2_addendum.md` | 3048 | `da8ea3ded927` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_2_2_close_note.md` → `docs/roadmap/phase_5_2_2_close_note.md` | 3672 | `8ced69318739` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_2_3_close_note.md` → `docs/roadmap/phase_5_2_3_close_note.md` | 5860 | `5c363e3e1ccc` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_2_3_report_refinement.md` → `docs/roadmap/phase_5_2_3_report_refinement.md` | 2072 | `72b8ca2a7130` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_2_3_status_snapshot.md` → `docs/roadmap/phase_5_2_3_status_snapshot.md` | 8198 | `68831637546f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_2_close_note.md` → `docs/roadmap/phase_5_2_close_note.md` | 2161 | `40a2c95be42e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_3_2_chart_structure_feature_candidates.md` → `docs/roadmap/phase_5_3_2_chart_structure_feature_candidates.md` | 2528 | `56b87bb3008c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_3_2_chart_structure_feature_catalog.md` → `docs/roadmap/phase_5_3_2_chart_structure_feature_catalog.md` | 12164 | `c51a8c39b5b1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_3_close_note.md` → `docs/roadmap/phase_5_3_close_note.md` | 7101 | `817255fa6811` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_3_policy_driven_monitor.md.txt` → `docs/roadmap/phase_5_3_policy_driven_monitor.md.txt` | 5882 | `6450ca65b0cb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_4_ownership_and_wiring_design.md` → `docs/roadmap/phase_5_4_ownership_and_wiring_design.md` | 7446 | `b1ef8a3bd168` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/phase_5_to_6_roadmap.md` → `docs/roadmap/phase_5_to_6_roadmap.md` | 3587 | `f7391c23bd57` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/policy_schema_design.md` → `docs/roadmap/policy_schema_design.md` | 9854 | `82d294865414` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/policy_schema_design_draft.md` → `docs/roadmap/policy_schema_design_draft.md` | 9592 | `64f9ca95bde1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/pre_buy_strategist_refresh_note_5_2_1.md` → `docs/roadmap/pre_buy_strategist_refresh_note_5_2_1.md` | 5500 | `a6c8c3206796` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/report_model_env_cleanup_note.md` → `docs/roadmap/report_model_env_cleanup_note.md` | 3812 | `65d42af730e8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/scanner_liquidity_vs_volume_tuning_note.md` → `docs/roadmap/scanner_liquidity_vs_volume_tuning_note.md` | 6276 | `1a477d2e72e1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/trading_agent_phase_roadmap.md` → `docs/roadmap/trading_agent_phase_roadmap.md` | 2080 | `98603376b75d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/roadmap/unified_roadmap.md` → `docs/roadmap/unified_roadmap.md` | 2332 | `6ff67ad70e5b` | KEEP_IF: 문서 참조·경로·내용 정본 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
