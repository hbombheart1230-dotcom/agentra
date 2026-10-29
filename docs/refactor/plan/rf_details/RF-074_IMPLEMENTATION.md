# RF-074 — 코드 구조/함수 재배치 설계 (T09)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-074.md` blob `a35e3a05101f3acec6d22be39851f4d9de537139`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 75개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `tests/test_trade_report_ai.py` | 294281 | `abceef7124166e384dc77b4ba6e5597c16db60a3` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_trade_report_ai_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_live_execution_bundle_report.py` | 173419 | `46de2909ae1e625d50f3788b0ad77c3086413be7` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_live_execution_bundle_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_operator_ui.py` | 128647 | `b3cdc94ee1cf7c89012188e22116cfe9716d065d` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_operator_ui_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_trade_story_pipeline_enrichment.py` | 82879 | `431ea2f0f6b7ea8b28502492159ac73d1c9390cb` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_trade_story_pipeline_enrichment_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_operator_summary_reports.py` | 48860 | `2efe3ab833efa192e76d8920242d4d395ad0f4a6` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_operator_summary_reports_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_intraday_trade_reports.py` | 40160 | `2d66ca3a47fd638c7ad1d81b2edc06924fa00923` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_intraday_trade_reports_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_operator_ui_data_access_phase2.py` | 38694 | `f0e7e7c57973ec66ef85cf1760c1548cf821f584` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_operator_ui_data_access_phase2_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_operator_visibility_reports.py` | 35072 | `3c6e82b06c0f706e7f2a183f6bf1d4a73d61a8af` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_operator_visibility_reports_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_work_reporter_seed_migration.py` | 32261 | `cabcecfeeaf8ed5c5e830a713362d30507be0904` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_work_reporter_seed_migration_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_agent_pipeline_trace_report.py` | 31273 | `a2fe99d63ef7ff2227006957878b716768cfb472` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_agent_pipeline_trace_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_daily_report.py` | 29438 | `48b39c669e62071fa17cda96b68beb76440ee143` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_daily_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_run_ai_trade_report_batch.py` | 28088 | `57a6f127682ffe3905e72c70d2c857f858f39979` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_run_ai_trade_report_batch_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_reporter_analysis_report.py` | 26595 | `0f8049d81f4d98d3d9c92eb3f8afce278c508bed` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_reporter_analysis_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_generate_metrics_report.py` | 26315 | `1a76aa1451acdd9c199702070a12f19bcbeb1164` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_generate_metrics_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_trade_explain_report.py` | 21699 | `367eac53167660f155ec77b18dbabc8f42d7e3f7` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_trade_explain_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_symbol_trade_report.py` | 20616 | `6970af20dbf6b42594e54dc343535f26c16b534c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_symbol_trade_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `tests/test_agent_pipeline_trace_report.py` → `tests/test_agent_pipeline_trace_report.py` | 31273 | `a2fe99d63ef7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_benchmark_operator_visibility_memory.py` → `tests/test_benchmark_operator_visibility_memory.py` | 2756 | `73a3d344752d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_check_reporter_upgrade_regression.py` → `tests/test_check_reporter_upgrade_regression.py` | 3793 | `15138ccc8815` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_check_reports_trades_health.py` → `tests/test_check_reports_trades_health.py` | 6320 | `68dc4024678c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_check_trade_report_runtime_regression.py` → `tests/test_check_trade_report_runtime_regression.py` | 10407 | `49a86ae3be4a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_controlled_mock_lane_report.py` → `tests/test_controlled_mock_lane_report.py` | 3558 | `f79163c91111` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_daily_report.py` → `tests/test_daily_report.py` | 29438 | `48b39c669e62` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_evaluation_lens_report.py` → `tests/test_evaluation_lens_report.py` | 6302 | `22d549570e53` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_generate_metrics_report.py` → `tests/test_generate_metrics_report.py` | 26315 | `1a76aa1451ac` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_generate_ops_diagnostic_report.py` → `tests/test_generate_ops_diagnostic_report.py` | 6127 | `a03a8059abb2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_intraday_trade_reports.py` → `tests/test_intraday_trade_reports.py` | 40160 | `2d66ca3a47fd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_history_receipt_lifecycle.py` → `tests/test_kiwoom_history_receipt_lifecycle.py` | 15632 | `d7e7a2d2331f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_live_execution_bundle_report.py` → `tests/test_live_execution_bundle_report.py` | 173419 | `46de2909ae1e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_live_execution_bundle_report_runtime_recovery.py` → `tests/test_live_execution_bundle_report_runtime_recovery.py` | 8417 | `c054c0e6b7bd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_live_execution_report_context.py` → `tests/test_live_execution_report_context.py` | 606 | `d0821bafdca8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m13_eod_report.py` → `tests/test_m13_eod_report.py` | 2580 | `5602fb001b75` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m19_6_llm_daily_report.py` → `tests/test_m19_6_llm_daily_report.py` | 6316 | `889749423627` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_6_operator_intervention_resume.py` → `tests/test_m23_6_operator_intervention_resume.py` | 2749 | `de938f561e08` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_9_commander_resilience_metrics_report.py` → `tests/test_m23_9_commander_resilience_metrics_report.py` | 3481 | `5a6cff0f0469` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m25_3_alert_reporting_closeout.py` → `tests/test_m25_3_alert_reporting_closeout.py` | 2297 | `b7f57d39992f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_5_portfolio_guard_metrics_report.py` → `tests/test_m27_5_portfolio_guard_metrics_report.py` | 2304 | `512717d0ad9e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_5_monitor_metrics_report.py` → `tests/test_m29_5_monitor_metrics_report.py` | 4471 | `f0992cf3903e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_operator_summary_broker_day_reconciliation.py` → `tests/test_operator_summary_broker_day_reconciliation.py` | 5005 | `1e31118f25c5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_operator_summary_memory_linkage.py` → `tests/test_operator_summary_memory_linkage.py` | 4735 | `a8d6da06e2c0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_operator_summary_mining.py` → `tests/test_operator_summary_mining.py` | 3711 | `73dd18a60fae` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_operator_summary_refresh.py` → `tests/test_operator_summary_refresh.py` | 2308 | `3873fd70a7a9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_operator_summary_reports.py` → `tests/test_operator_summary_reports.py` | 48860 | `2efe3ab833ef` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_operator_ui.py` → `tests/test_operator_ui.py` | 128647 | `b3cdc94ee1cf` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_operator_ui_data_access_phase2.py` → `tests/test_operator_ui_data_access_phase2.py` | 38694 | `f0e7e7c57973` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_operator_visibility_reports.py` → `tests/test_operator_visibility_reports.py` | 35072 | `3c6e82b06c0f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_direct_story_owner.py` → `tests/test_p152_direct_story_owner.py` | 1085 | `76daf6448b5c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_markdown_clean_operator_labels_owners.py` → `tests/test_p152_markdown_clean_operator_labels_owners.py` | 3665 | `359e300665da` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_operator_language_owner.py` → `tests/test_p152_operator_language_owner.py` | 1412 | `680ab375de76` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_operator_phrase_owners.py` → `tests/test_p152_operator_phrase_owners.py` | 1697 | `dc85959812b8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_story_facade_compatible_owners.py` → `tests/test_p152_story_facade_compatible_owners.py` | 4203 | `64b25cd5850a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_story_facade_contract_owners.py` → `tests/test_p152_story_facade_contract_owners.py` | 2911 | `ced4ce78d968` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_story_facade_human_owners.py` → `tests/test_p152_story_facade_human_owners.py` | 3183 | `1ae6b205d8da` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_story_reasoning_owner.py` → `tests/test_p152_story_reasoning_owner.py` | 2274 | `255303cd07fb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p153_operator_ui_moved_bodies.py` → `tests/test_p153_operator_ui_moved_bodies.py` | 9725 | `4fcbac6b6c83` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_b_operator_brief_boundaries.py` → `tests/test_p15_b_operator_brief_boundaries.py` | 7103 | `75c0850453fb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_b_operator_brief_pure_parity.py` → `tests/test_p15_b_operator_brief_pure_parity.py` | 9732 | `2b104e85ebd1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_operator_run_detail_projection.py` → `tests/test_p15_operator_run_detail_projection.py` | 13383 | `8298fad7ae57` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_operator_trade_index_projection.py` → `tests/test_p15_operator_trade_index_projection.py` | 8465 | `db70b4575b17` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_tactic_report.py` → `tests/test_quant_tactic_report.py` | 9786 | `61f9c18f122b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_report_maintenance.py` → `tests/test_report_maintenance.py` | 4613 | `d40ad9eb82bb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_report_metadata_alignment.py` → `tests/test_report_metadata_alignment.py` | 7627 | `070f61e56ff7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_report_trades_continuity.py` → `tests/test_report_trades_continuity.py` | 1775 | `8deed3d744d3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporter_agent_trade_entrypoint.py` → `tests/test_reporter_agent_trade_entrypoint.py` | 2540 | `b4d3054a38e8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporter_analysis_report.py` → `tests/test_reporter_analysis_report.py` | 26595 | `0f8049d81f4d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporter_commander_hooks.py` → `tests/test_reporter_commander_hooks.py` | 5711 | `9e0949f92640` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporter_feedback.py` → `tests/test_reporter_feedback.py` | 15399 | `bf7695542688` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporter_node.py` → `tests/test_reporter_node.py` | 2790 | `03d65a937fb1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporter_script_wrappers.py` → `tests/test_reporter_script_wrappers.py` | 6509 | `0a1c846b76e0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporter_service.py` → `tests/test_reporter_service.py` | 9115 | `359434d14873` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporting_provenance_preference.py` → `tests/test_reporting_provenance_preference.py` | 6343 | `c691080c3341` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reporting_relocation_imports.py` → `tests/test_reporting_relocation_imports.py` | 1939 | `39703f9ddb45` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_ai_trade_report_batch.py` → `tests/test_run_ai_trade_report_batch.py` | 28088 | `57a6f127682f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_operator_brief_batch.py` → `tests/test_run_operator_brief_batch.py` | 359 | `b264f014558c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_shared_reporter_facade_guard.py` → `tests/test_shared_reporter_facade_guard.py` | 4477 | `85e822b13bb4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_single_trade_report.py` → `tests/test_single_trade_report.py` | 14098 | `506baa7be181` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategist_quant_context_report.py` → `tests/test_strategist_quant_context_report.py` | 4676 | `269525221a75` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_symbol_trade_report.py` → `tests/test_symbol_trade_report.py` | 20616 | `6970af20dbf6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_explain_report.py` → `tests/test_trade_explain_report.py` | 21699 | `367eac531676` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_report_ai.py` → `tests/test_trade_report_ai.py` | 294281 | `abceef712416` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_report_ai_separated_adapter.py` → `tests/test_trade_report_ai_separated_adapter.py` | 2390 | `eee38a8208b4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_story_pipeline_enrichment.py` → `tests/test_trade_story_pipeline_enrichment.py` | 82879 | `431ea2f0f6b7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_reporter_r10_artifact_parity.py` → `tests/test_work_reporter_r10_artifact_parity.py` | 9705 | `980e2f3fe8af` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_reporter_r10_retained_io_contracts.py` → `tests/test_work_reporter_r10_retained_io_contracts.py` | 14337 | `6332d2650693` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_reporter_r11_repo_hygiene.py` → `tests/test_work_reporter_r11_repo_hygiene.py` | 7145 | `dbfc9940f47a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_reporter_r4_facade_bodies.py` → `tests/test_work_reporter_r4_facade_bodies.py` | 12433 | `3c8821e9c544` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_reporter_r8_read_contracts.py` → `tests/test_work_reporter_r8_read_contracts.py` | 4946 | `851bff2fef23` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_reporter_r8_read_via_callback_parity.py` → `tests/test_work_reporter_r8_read_via_callback_parity.py` | 9075 | `10eddc7dc323` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_reporter_renderer_bytes.py` → `tests/test_work_reporter_renderer_bytes.py` | 3797 | `f17f475cb849` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_reporter_seed_migration.py` → `tests/test_work_reporter_seed_migration.py` | 32261 | `cabcecfeeaf8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/uef9_synthetic_reports.py` → `tests/uef9_synthetic_reports.py` | 2301 | `6fbbbae5d3fa` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
