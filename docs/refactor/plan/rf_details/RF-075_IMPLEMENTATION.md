# RF-075 — 코드 구조/함수 재배치 설계 (T09)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-075.md` blob `064c19ed3c00040584455f3b2c36b13f76737aff`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 88개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `tests/test_monitor_exit_guard.py` | 213847 | `c47099961381da03f749ba0bed5a648e4105606b` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_monitor_exit_guard_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_m21_commander_runtime_entry.py` | 188918 | `889ed4686578ed60b130fc09b3aa1b9aeaf61c2f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_m21_commander_runtime_entry_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_strategist_frame_llm_integration.py` | 97383 | `efd9c438915a9df686ebe5377700aeee91919473` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_strategist_frame_llm_integration_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_intraday_monitor_signals.py` | 89986 | `abf157bfa16c904457828951be174c7e9a5f23fd` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_intraday_monitor_signals_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_scanner_strategy_frame_integration.py` | 27777 | `4e74858cb473a741b7c01694de67424d9f476b0a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_scanner_strategy_frame_integration_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_m29_3_monitor_exit_policy.py` | 25619 | `20b8bcc4c6458a062c6e912a43e699f3f7fc4813` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_m29_3_monitor_exit_policy_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_scanner_monitor_compatibility.py` | 23765 | `505454fea6678331607ea752ae40eae38811181c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_scanner_monitor_compatibility_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_strategist_reasoning_quality.py` | 23130 | `01240fa94e4bda2e4d2ab67a2ce75a3881a440e5` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_strategist_reasoning_quality_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `tests/p15_strategist_s5_cases.py` → `tests/p15_strategist_s5_cases.py` | 5726 | `ef66859f5e48` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_check_monitor_gate_patterns.py` → `tests/test_check_monitor_gate_patterns.py` | 3904 | `421712927a3a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_commander_contract.py` → `tests/test_commander_contract.py` | 3204 | `85019c322b1c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_commander_env_migration_phase1.py` → `tests/test_commander_env_migration_phase1.py` | 10109 | `bda05f38da7a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_commander_env_migration_phase2.py` → `tests/test_commander_env_migration_phase2.py` | 8732 | `b7661aec2889` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_commander_memory_policy.py` → `tests/test_commander_memory_policy.py` | 13575 | `e566b269e87f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_commander_post_scanner_context.py` → `tests/test_commander_post_scanner_context.py` | 2036 | `42e9c962c832` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_intraday_monitor_signals.py` → `tests/test_intraday_monitor_signals.py` | 89986 | `abf157bfa16c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m11_2_scanner.py` → `tests/test_m11_2_scanner.py` | 749 | `f87b8778e1a8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m12_strategist_hook.py` → `tests/test_m12_strategist_hook.py` | 536 | `d9430c18590f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m17_monitor_emits_intent_only.py` → `tests/test_m17_monitor_emits_intent_only.py` | 812 | `74ee86b328e5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_4_scanner_sentiment_weighting.py` → `tests/test_m18_4_scanner_sentiment_weighting.py` | 1798 | `cb6fcf4d114b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_scanner_global_sentiment_contract.py` → `tests/test_m18_scanner_global_sentiment_contract.py` | 1377 | `4c2f39525435` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m21_commander_runtime_entry.py` → `tests/test_m21_commander_runtime_entry.py` | 188918 | `889ed4686578` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m21_graph_spine_parity.py` → `tests/test_m21_graph_spine_parity.py` | 3935 | `4b47d0b6f5c8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m22_graph_hydration_wiring.py` → `tests/test_m22_graph_hydration_wiring.py` | 3525 | `09a486b4bf2b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m22_skill_native_scanner_monitor.py` → `tests/test_m22_skill_native_scanner_monitor.py` | 10936 | `02ca10bd3a30` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_4_commander_incident_cooldown_routing.py` → `tests/test_m23_4_commander_incident_cooldown_routing.py` | 3603 | `3a4bcda97b3a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_7_commander_resilience_ops_script.py` → `tests/test_m23_7_commander_resilience_ops_script.py` | 4146 | `e07070ee427c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_2_scanner_feature_integration.py` → `tests/test_m29_2_scanner_feature_integration.py` | 2475 | `74590409ddee` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_3_monitor_exit_policy.py` → `tests/test_m29_3_monitor_exit_policy.py` | 25619 | `20b8bcc4c645` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_4_monitor_position_sizing.py` → `tests/test_m29_4_monitor_position_sizing.py` | 5769 | `b01b1fc60b7b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m30_3_post_golive_monitoring_policy.py` → `tests/test_m30_3_post_golive_monitoring_policy.py` | 3145 | `6af5098ae7d6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_candidate_cascade.py` → `tests/test_monitor_candidate_cascade.py` | 12100 | `576ac37c5cde` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_cash_truth.py` → `tests/test_monitor_cash_truth.py` | 299 | `13ff89af9fe7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_directional_edge.py` → `tests/test_monitor_directional_edge.py` | 7393 | `03c2ef3910e1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_evidence_ast.py` → `tests/test_monitor_evidence_ast.py` | 1567 | `6895c30ce63d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_exit_guard.py` → `tests/test_monitor_exit_guard.py` | 213847 | `c47099961381` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_exit_price_freshness.py` → `tests/test_monitor_exit_price_freshness.py` | 7504 | `1ffc047be5e2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_fallback_quality_gate.py` → `tests/test_monitor_fallback_quality_gate.py` | 3309 | `4768a93c1a6a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_feedback_adaptive_policy.py` → `tests/test_monitor_feedback_adaptive_policy.py` | 11888 | `7ff445e6cedd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_memory_bias.py` → `tests/test_monitor_memory_bias.py` | 13936 | `eea30fc765c2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_minute_ohlcv_resilience.py` → `tests/test_monitor_minute_ohlcv_resilience.py` | 834 | `0dc245be059b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_noop_attribution.py` → `tests/test_monitor_noop_attribution.py` | 4510 | `8c6bfabd2d89` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_monitor_price_source_resolution.py` → `tests/test_monitor_price_source_resolution.py` | 713 | `961187ae11c1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_ai_facade_market_scanner_labels.py` → `tests/test_p152_ai_facade_market_scanner_labels.py` | 3703 | `79d8b382c420` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_monitor_context_owner.py` → `tests/test_p152_monitor_context_owner.py` | 2741 | `b479329960a8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_monitor_diagnostics_owner.py` → `tests/test_p152_monitor_diagnostics_owner.py` | 1539 | `a0ef101c5ff4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_monitor_entry_review_owner.py` → `tests/test_p152_monitor_entry_review_owner.py` | 2154 | `9a590ffe7f95` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_monitor_policy_bullets_owner.py` → `tests/test_p152_monitor_policy_bullets_owner.py` | 1376 | `56e43ff67dbb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_monitor_trace_wrappers.py` → `tests/test_p152_monitor_trace_wrappers.py` | 2236 | `08d1808fac17` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_b_commander_monitor_boundaries.py` → `tests/test_p15_b_commander_monitor_boundaries.py` | 6652 | `0bf3dcf867a2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_b_commander_monitor_pure_parity.py` → `tests/test_p15_b_commander_monitor_pure_parity.py` | 10997 | `75fc54f2d928` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_commander_pure_v1_admission.py` → `tests/test_p15_commander_pure_v1_admission.py` | 9612 | `3b46831ecdcd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_strategist_contract_parsing_move.py` → `tests/test_p15_strategist_contract_parsing_move.py` | 13312 | `19efe4a8cd68` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_strategist_s5_helper_moves.py` → `tests/test_p15_strategist_s5_helper_moves.py` | 18695 | `f70281e541bb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p162_scanner_node_contract_freeze.py` → `tests/test_p162_scanner_node_contract_freeze.py` | 14055 | `adb011d03d02` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p163_monitor_contract_freeze.py` → `tests/test_p163_monitor_contract_freeze.py` | 7449 | `8e72f8ddb834` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p164_strategist_contract_freeze.py` → `tests/test_p164_strategist_contract_freeze.py` | 7782 | `df5367b9c0c1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p165_commander_ui_contract_freeze.py` → `tests/test_p165_commander_ui_contract_freeze.py` | 7953 | `f401f539ab26` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p167_v2053_scanner_context_migration.py` → `tests/test_p167_v2053_scanner_context_migration.py` | 6726 | `4fafef4ae4ec` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p171_v3055_scanner_projection_migration.py` → `tests/test_p171_v3055_scanner_projection_migration.py` | 9924 | `2c948370f2ac` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p172_strategist_s1_057_migration.py` → `tests/test_p172_strategist_s1_057_migration.py` | 8008 | `26fa5bfd5957` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p172_v4056_scanner_policy_migration.py` → `tests/test_p172_v4056_scanner_policy_migration.py` | 9230 | `f436fbcf147f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q9_scanner_quality.py` → `tests/test_q9_scanner_quality.py` | 2857 | `975d13bae4f6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_alignment_root_cause.py` → `tests/test_scanner_alignment_root_cause.py` | 5494 | `008ba6cabd9e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_bias_integration.py` → `tests/test_scanner_bias_integration.py` | 3754 | `96dc6927a871` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_candidate_risk.py` → `tests/test_scanner_candidate_risk.py` | 3995 | `72373d00df9a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_fallback_policy.py` → `tests/test_scanner_fallback_policy.py` | 12846 | `eb5d03ad8c3f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_feature_hydration.py` → `tests/test_scanner_feature_hydration.py` | 8124 | `809f7b8a2d08` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_live_symbol_filter.py` → `tests/test_scanner_live_symbol_filter.py` | 943 | `8d461e2c96a8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_memory_bias.py` → `tests/test_scanner_memory_bias.py` | 8173 | `c8fcd9daaa33` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_monitor_compatibility.py` → `tests/test_scanner_monitor_compatibility.py` | 23765 | `505454fea667` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_policy_overlay.py` → `tests/test_scanner_policy_overlay.py` | 17670 | `6cdf91108ea0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_practical_selection_engine.py` → `tests/test_scanner_practical_selection_engine.py` | 7979 | `97ea007ae717` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_quote_hydration_runtime.py` → `tests/test_scanner_quote_hydration_runtime.py` | 2174 | `2f89453038d5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_rank_plumbing_fix.py` → `tests/test_scanner_rank_plumbing_fix.py` | 12482 | `377cd5426c5a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_strategy_frame_integration.py` → `tests/test_scanner_strategy_frame_integration.py` | 27777 | `4e74858cb473` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scanner_universe_candidate_metadata.py` → `tests/test_scanner_universe_candidate_metadata.py` | 1542 | `d7814b1d53fb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_shared_strategist_contracts.py` → `tests/test_shared_strategist_contracts.py` | 8218 | `3d79529ea12e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategist_explanation_contract.py` → `tests/test_strategist_explanation_contract.py` | 10467 | `4ca8c59bfe1c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategist_frame_llm_integration.py` → `tests/test_strategist_frame_llm_integration.py` | 97383 | `efd9c438915a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategist_input_quality_risk_off.py` → `tests/test_strategist_input_quality_risk_off.py` | 1014 | `6934e842a008` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategist_llm_summary.py` → `tests/test_strategist_llm_summary.py` | 12692 | `1fdceb50a7ba` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategist_output_schema.py` → `tests/test_strategist_output_schema.py` | 8945 | `40da1bc574ab` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategist_reasoning_quality.py` → `tests/test_strategist_reasoning_quality.py` | 23130 | `01240fa94e4b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategist_refresh_decision.py` → `tests/test_strategist_refresh_decision.py` | 4661 | `4d3b409f228c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_annotation_views.py` → `tests/test_work_monitor_annotation_views.py` | 4839 | `b56336e49d6a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_body_views.py` → `tests/test_work_monitor_body_views.py` | 5202 | `eb5f9a270456` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_continuous.py` → `tests/test_work_monitor_continuous.py` | 7757 | `8a881ad6c99d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_exit_labels.py` → `tests/test_work_monitor_exit_labels.py` | 4493 | `29fc0ee1dd4e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_m9_native.py` → `tests/test_work_monitor_m9_native.py` | 3118 | `b876040777da` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_m9_offline.py` → `tests/test_work_monitor_m9_offline.py` | 12196 | `38965b74a0a3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_observation_views.py` → `tests/test_work_monitor_observation_views.py` | 5525 | `1efbfc9dc72e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_policy_trace_views.py` → `tests/test_work_monitor_policy_trace_views.py` | 7484 | `80ae52915f7f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_retained_boundary.py` → `tests/test_work_monitor_retained_boundary.py` | 1496 | `f4d63d9706e5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_role_contracts.py` → `tests/test_work_monitor_role_contracts.py` | 9408 | `a5250ec49814` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_work_monitor_scope_accounting.py` → `tests/test_work_monitor_scope_accounting.py` | 4141 | `076bee7dad1f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
