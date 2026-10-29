# RF-078 — 코드 구조/함수 재배치 설계 (T09)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-078.md` blob `b20c39ba7f60a8c6a37064854b1ea5167b8050e6`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 375개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `tests/test_execute_from_packet.py` | 78014 | `ddb7c219685a82d583b7050bb1e42a1f88fef521` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_execute_from_packet_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_phase1_agent_artifact_quality.py` | 77870 | `e9777761d46a7c2831b8e1e3ff79aa038f0a3016` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_phase1_agent_artifact_quality_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_p156_parity_harness.py` | 57329 | `1060b092c59156a6b1befb4efd8e2e5109491d7e` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_p156_parity_harness_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_closeout_memory_bounds.py` | 52686 | `5d27e49e2dc3b031500436d850a0fb215ba0aec0` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_closeout_memory_bounds_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_closeout_single_owner_guard.py` | 43809 | `f8e770984dc314ef450885e6b7b409253046072d` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_closeout_single_owner_guard_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_alpha_research_board.py` | 38299 | `61bf22b7053f61a5963f1665cd0f922678efad22` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_alpha_research_board_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_run_mock_exam_day.py` | 38122 | `08c4b3bd04f01b18b4c78b296b8cc9870d6bcf3d` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_run_mock_exam_day_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_m20_2_decide_trade_llm_flow.py` | 31982 | `be008b7ead4612048a4dcadba126496c3aec5a55` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_m20_2_decide_trade_llm_flow_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_strategy_sizing_exit_upgrade.py` | 31810 | `62026aea3705ed75783a2bc76208dd6ddb624c69` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_strategy_sizing_exit_upgrade_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_check_phase_5_2_5_3_runtime_health.py` | 31644 | `8d6cd0e8bc6b05d7243ed8a33cbf94cd50174cdf` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_check_phase_5_2_5_3_runtime_health_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_kiwoom_day_trade_truth.py` | 30015 | `b13efbf799584d180b19e2036679b378f802df20` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_kiwoom_day_trade_truth_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_update_state_after_execution.py` | 28911 | `feb0df41f9898e7c5c1d1536551ecae332497d61` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_update_state_after_execution_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_q9_evaluation.py` | 28887 | `e7732ebeb1e8a73fd8829780169950dd2077e0e9` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_q9_evaluation_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_r61_scope_fix.py` | 28284 | `d955df60008c84e52905a6dee47a4e1ef31ca9eb` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_r61_scope_fix_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_p159_current_owner_contract_gates.py` | 27901 | `80f3d4b4309f133c8152279efdcbbce24ae80a3f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_p159_current_owner_contract_gates_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_q10_collector_fix3.py` | 25317 | `9285fa1f41240a408330e5ae0cb5cca5d86f5261` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_q10_collector_fix3_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_m20_1_openai_provider_smoke.py` | 25276 | `220f87de5759cef3dc83d631e9292c8cefcef1ab` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_m20_1_openai_provider_smoke_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_p15_integration_completion.py` | 25123 | `449446d0d2180e108a515545e4f313cd1c17c0df` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_p15_integration_completion_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_quant_shadow_candidates.py` | 24514 | `58a89f33b571b42092f888e3de51d1e6c4967561` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_quant_shadow_candidates_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_r62_attempt_and_lock.py` | 24332 | `c324f3566f94f7b10bbae77c30957d6de832fb3b` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_r62_attempt_and_lock_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_strategy_performance_feedback.py` | 24311 | `86b05aafa606cbb2b36e864ce3965545df12f3b4` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_strategy_performance_feedback_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_trade_memory_surface.py` | 22856 | `98bde173a706f89f12e82ab8627c09bfeffb7903` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_trade_memory_surface_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_r6_readiness_evidence.py` | 22746 | `edadb55d0359b7bec835ea9fe10c6b03d88b07ef` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_r6_readiness_evidence_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_opening_rank1_controlled_probe.py` | 22182 | `568fa93ed5371afc9b404e9ce66f74ffe7c43e2f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_opening_rank1_controlled_probe_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_baseline_samsung_hynix.py` | 21349 | `36608cde09164b3441d7e768bbd1231f22830344` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_baseline_samsung_hynix_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_m31_17_theme_candidate_flow_upgrade.py` | 21247 | `0b1ca8d3cfd0afabc5ea1ef2abac7cd8ea48bb97` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_m31_17_theme_candidate_flow_upgrade_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_opening_alpha_executable_quote_refresh.py` | 20749 | `504bb6099d6961568120e697adbd822cc29b3892` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_opening_alpha_executable_quote_refresh_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_trade_bundle_assembly.py` | 20087 | `251f599498d3d9e8442caaf19876acbd05fea6a2` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_trade_bundle_assembly_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `tests/_r6_helpers.py` → `tests/_r6_helpers.py` | 3188 | `9f6c4b53ea1e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/p15_agent_tree_allowlist.py` → `tests/p15_agent_tree_allowlist.py` | 2015 | `bc7c02546789` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_account_client.py` → `tests/test_account_client.py` | 4290 | `a62618938ced` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_agent_effectiveness_scorecard.py` → `tests/test_agent_effectiveness_scorecard.py` | 6395 | `bae76a709b0b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_ai_effectiveness_provenance.py` → `tests/test_ai_effectiveness_provenance.py` | 3705 | `39c6d1eb57ef` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_ai_strategy_v1_bridge.py` → `tests/test_ai_strategy_v1_bridge.py` | 1910 | `42582b495251` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_alpha_hypothesis_competition.py` → `tests/test_alpha_hypothesis_competition.py` | 5882 | `0cd693eb918a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_alpha_research_board.py` → `tests/test_alpha_research_board.py` | 38299 | `61bf22b7053f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_asset_universe_policy.py` → `tests/test_asset_universe_policy.py` | 12445 | `8064c995d6d0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_attribution_score_range.py` → `tests/test_attribution_score_range.py` | 2957 | `add0268436e0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_attribution_score_v0.py` → `tests/test_attribution_score_v0.py` | 4174 | `933179f22375` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_attribution_score_window.py` → `tests/test_attribution_score_window.py` | 3135 | `86f99b4ba4bc` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_baseline_btc_woori_tech.py` → `tests/test_baseline_btc_woori_tech.py` | 15063 | `bd933acb121b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_baseline_samsung_hynix.py` → `tests/test_baseline_samsung_hynix.py` | 21349 | `36608cde0916` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_baseline_shared_owners.py` → `tests/test_baseline_shared_owners.py` | 6638 | `3982fae4faf0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_canonical_agent_artifacts.py` → `tests/test_canonical_agent_artifacts.py` | 14166 | `8ac13cab2f0b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_canonical_artifact_validation.py` → `tests/test_canonical_artifact_validation.py` | 14601 | `6016036eabe2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_carryover_exit_reconciler.py` → `tests/test_carryover_exit_reconciler.py` | 4600 | `87a712463dec` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_chart_structure_decision_hint_summary.py` → `tests/test_chart_structure_decision_hint_summary.py` | 6281 | `3eee59054c40` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_chart_structure_features.py` → `tests/test_chart_structure_features.py` | 4059 | `9991401e155c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_check_phase_5_2_5_3_runtime_health.py` → `tests/test_check_phase_5_2_5_3_runtime_health.py` | 31644 | `8d6cd0e8bc6b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_cleanup_pytest_artifacts_cli.py` → `tests/test_cleanup_pytest_artifacts_cli.py` | 2245 | `f5bd26cb6a93` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_closeout_diagnostic_hardening.py` → `tests/test_closeout_diagnostic_hardening.py` | 10252 | `1702419a8849` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_closeout_durable_completion_authority.py` → `tests/test_closeout_durable_completion_authority.py` | 19708 | `d06f2e31bc78` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_closeout_maintenance.py` → `tests/test_closeout_maintenance.py` | 3798 | `56096b626920` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_closeout_memory_bounds.py` → `tests/test_closeout_memory_bounds.py` | 52686 | `5d27e49e2dc3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_closeout_payload_projection.py` → `tests/test_closeout_payload_projection.py` | 10391 | `00558c98fde2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_closeout_residual_positions.py` → `tests/test_closeout_residual_positions.py` | 7248 | `9f40af7f3343` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_closeout_single_owner_guard.py` → `tests/test_closeout_single_owner_guard.py` | 43809 | `f8e770984dc3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_conditional_alpha_diagnosis.py` → `tests/test_conditional_alpha_diagnosis.py` | 5245 | `79f90081d08f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_conditional_alpha_quant_bridge.py` → `tests/test_conditional_alpha_quant_bridge.py` | 4175 | `43b76a079b00` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_conditional_alpha_reactivation.py` → `tests/test_conditional_alpha_reactivation.py` | 2249 | `46387cd645f1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_controlled_mock_lane_execution_integration.py` → `tests/test_controlled_mock_lane_execution_integration.py` | 5542 | `1d8a5ad6594c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_controlled_mock_lanes.py` → `tests/test_controlled_mock_lanes.py` | 17894 | `f29118661177` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_controlled_validation_daily_submission_provenance.py` → `tests/test_controlled_validation_daily_submission_provenance.py` | 6018 | `51ad13438f8b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_cost_basis_comparison.py` → `tests/test_cost_basis_comparison.py` | 2726 | `b1d1a86d646a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_cumulative_improvement_review.py` → `tests/test_cumulative_improvement_review.py` | 7118 | `1760a05cf379` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_daily_strategy_memory_packet.py` → `tests/test_daily_strategy_memory_packet.py` | 6523 | `c11697840bbf` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_data_quality_state_propagation.py` → `tests/test_data_quality_state_propagation.py` | 9249 | `cb95b6f7b27c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_decision_observability.py` → `tests/test_decision_observability.py` | 11083 | `6ae07dd24968` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_decision_packet_explainability_contract.py` → `tests/test_decision_packet_explainability_contract.py` | 1029 | `46565226595a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_decision_trace_ledger.py` → `tests/test_decision_trace_ledger.py` | 3860 | `5527d30f9f59` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_diagnostic_queries_work_order01.py` → `tests/test_diagnostic_queries_work_order01.py` | 8352 | `590dfe03c57f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_diagnostics_shared_owners.py` → `tests/test_diagnostics_shared_owners.py` | 7288 | `021d61248259` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_docker_healthcheck_ownership_liveness.py` → `tests/test_docker_healthcheck_ownership_liveness.py` | 9046 | `844de365c3e7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_entry_blocker_read_model.py` → `tests/test_entry_blocker_read_model.py` | 14567 | `58d5273e73e4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_entry_timing_attribution.py` → `tests/test_entry_timing_attribution.py` | 7297 | `421086a5c076` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_etf_deviation.py` → `tests/test_etf_deviation.py` | 1131 | `6226a8826fe2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_event_log_reader.py` → `tests/test_event_log_reader.py` | 3489 | `5a0810078258` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_event_logger.py` → `tests/test_event_logger.py` | 6481 | `10a1312f0723` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_evidence_ledger_trace_layer.py` → `tests/test_evidence_ledger_trace_layer.py` | 6975 | `4de9e83218dc` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_execute_from_packet.py` → `tests/test_execute_from_packet.py` | 78014 | `ddb7c219685a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_execution_plan_closeout_docs.py` → `tests/test_execution_plan_closeout_docs.py` | 1352 | `a7f5c008eb13` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_execution_trace_completeness.py` → `tests/test_execution_trace_completeness.py` | 13867 | `0d91932ebf1f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_existing_evidence_mining.py` → `tests/test_existing_evidence_mining.py` | 12063 | `83ccec46e47c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_fact_narrative_separation.py` → `tests/test_fact_narrative_separation.py` | 5643 | `29b67a072ca1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_full_chain_component_review.py` → `tests/test_full_chain_component_review.py` | 6815 | `c1b4c82fae56` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_global_sentiment_unavailable_behavior.py` → `tests/test_global_sentiment_unavailable_behavior.py` | 8708 | `269ced2e8ad3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_historical_q9_prior.py` → `tests/test_historical_q9_prior.py` | 2785 | `94a0236e67af` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_horizon_alignment.py` → `tests/test_horizon_alignment.py` | 2672 | `a238b9339a13` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_horizon_revision_backtest.py` → `tests/test_horizon_revision_backtest.py` | 1730 | `b5aa79a1b863` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_http_client.py` → `tests/test_http_client.py` | 1265 | `ad9dda2d54f2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_integrated_trade_diagnosis.py` → `tests/test_integrated_trade_diagnosis.py` | 7188 | `9539e37f5a64` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_intent_packet.py` → `tests/test_intent_packet.py` | 681 | `56ff1623b1c5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_account_snapshot_collector.py` → `tests/test_kiwoom_account_snapshot_collector.py` | 2277 | `e177891b1b3d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_candidate_provider.py` → `tests/test_kiwoom_candidate_provider.py` | 19891 | `5c1278aca975` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_day_pnl_reader.py` → `tests/test_kiwoom_day_pnl_reader.py` | 2829 | `a0f72e99292d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_day_trade_truth.py` → `tests/test_kiwoom_day_trade_truth.py` | 30015 | `b13efbf79958` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_market_index_reader.py` → `tests/test_kiwoom_market_index_reader.py` | 3813 | `3be9ebc43f68` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_market_status.py` → `tests/test_kiwoom_market_status.py` | 3521 | `3a994e9f25ad` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_orderable_cash_reader.py` → `tests/test_kiwoom_orderable_cash_reader.py` | 2620 | `62245455c95e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_theme_reader.py` → `tests/test_kiwoom_theme_reader.py` | 4826 | `3d5cc63e2119` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_token_client.py` → `tests/test_kiwoom_token_client.py` | 3236 | `28c225065e66` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_korea_bond_yields.py` → `tests/test_korea_bond_yields.py` | 1549 | `49ffd1331a2a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_korea_market_indices_context.py` → `tests/test_korea_market_indices_context.py` | 2783 | `eb05e8d18b3e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_latent_reactivation_forward.py` → `tests/test_latent_reactivation_forward.py` | 1451 | `fb91e4658e3c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_live_loop_config.py` → `tests/test_live_loop_config.py` | 1184 | `9ed7aa0b0a96` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_live_loop_lock.py` → `tests/test_live_loop_lock.py` | 1310 | `3a0680fc694c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_live_loop_process_query.py` → `tests/test_live_loop_process_query.py` | 1336 | `93383e3afc86` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_live_loop_runner.py` → `tests/test_live_loop_runner.py` | 2188 | `c910b14a68e4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_llm_json_parse_shared.py` → `tests/test_llm_json_parse_shared.py` | 1106 | `2b0bcc2b1c71` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_llm_model_policy.py` → `tests/test_llm_model_policy.py` | 19338 | `bc5735ba64ed` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_llm_status_semantics.py` → `tests/test_llm_status_semantics.py` | 4457 | `87c09e3b5fb2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_llm_status_semantics_phase2.py` → `tests/test_llm_status_semantics_phase2.py` | 3534 | `96160082cf5d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_load_save_state_nodes.py` → `tests/test_load_save_state_nodes.py` | 505 | `c9dfdc476d6e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_log_maintenance.py` → `tests/test_log_maintenance.py` | 2579 | `f43fdb59c349` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_loss_decomposition.py` → `tests/test_loss_decomposition.py` | 1131 | `b26c279a630e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m10_6_decision_context_hydration.py` → `tests/test_m10_6_decision_context_hydration.py` | 5333 | `f6a9196532dd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m10_live_pipeline.py` → `tests/test_m10_live_pipeline.py` | 1893 | `87fcc3fce734` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m11_live_pipeline.py` → `tests/test_m11_live_pipeline.py` | 1364 | `5578815bd115` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m12_1_provider_routing.py` → `tests/test_m12_1_provider_routing.py` | 1955 | `3ff96b0053f0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m12_2_openai_http_provider.py` → `tests/test_m12_2_openai_http_provider.py` | 1115 | `88d1cbce09d5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m12_3_intent_normalization.py` → `tests/test_m12_3_intent_normalization.py` | 1190 | `91eac7d1c545` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m13_e2e_once.py` → `tests/test_m13_e2e_once.py` | 2132 | `c5cd0f3db067` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m13_lease_heartbeat_fix.py` → `tests/test_m13_lease_heartbeat_fix.py` | 10280 | `26e2f772fb74` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m13_live_loop.py` → `tests/test_m13_live_loop.py` | 4933 | `fd84783b1453` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m13_ownership_lease_bounded_wait_fix.py` → `tests/test_m13_ownership_lease_bounded_wait_fix.py` | 9679 | `f3e41d2fa37d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m13_shutdown_during_lease_wait.py` → `tests/test_m13_shutdown_during_lease_wait.py` | 6360 | `94cc110fce65` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m13_strict_owner_identity_restart_fix.py` → `tests/test_m13_strict_owner_identity_restart_fix.py` | 13554 | `352707f10e16` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m13_tick.py` → `tests/test_m13_tick.py` | 2080 | `322bbb34a92b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m15_smoke.py` → `tests/test_m15_smoke.py` | 7133 | `aaf647381cb7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m17_candidates_to_selected.py` → `tests/test_m17_candidates_to_selected.py` | 1245 | `906533ea741f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_3_global_sentiment_policy_adjust.py` → `tests/test_m18_3_global_sentiment_policy_adjust.py` | 1023 | `42ff9b85e4c7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_3_news_sentiment_pass_through.py` → `tests/test_m18_3_news_sentiment_pass_through.py` | 612 | `5b394917806c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_5_candidate_rerank_by_news.py` → `tests/test_m18_5_candidate_rerank_by_news.py` | 644 | `72f3fe4c953e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_6_news_plugin_contract.py` → `tests/test_m18_6_news_plugin_contract.py` | 1027 | `1db81587e853` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_8_news_scorer_plugin.py` → `tests/test_m18_8_news_scorer_plugin.py` | 1771 | `9afeff0767df` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_9_global_sentiment_compute.py` → `tests/test_m18_9_global_sentiment_compute.py` | 519 | `6704b6b300e8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_market_scan_candidates.py` → `tests/test_m18_market_scan_candidates.py` | 13106 | `0b23998fca02` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_top_picks_candidates.py` → `tests/test_m18_top_picks_candidates.py` | 1253 | `cdec3588c1aa` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m19_4_openrouter_news_scorer.py` → `tests/test_m19_4_openrouter_news_scorer.py` | 1133 | `81792100c2c0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m20_1_openai_provider_smoke.py` → `tests/test_m20_1_openai_provider_smoke.py` | 25276 | `220f87de5759` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m20_2_decide_trade_llm_flow.py` → `tests/test_m20_2_decide_trade_llm_flow.py` | 31982 | `be008b7ead46` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m20_3_legacy_llm_router_compat.py` → `tests/test_m20_3_legacy_llm_router_compat.py` | 4277 | `34ebdee39973` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m20_3_llm_event_logging.py` → `tests/test_m20_3_llm_event_logging.py` | 8384 | `7fef572bddc5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m20_4_llm_ops_scripts.py` → `tests/test_m20_4_llm_ops_scripts.py` | 5130 | `798edf652192` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m21_runtime_once_script.py` → `tests/test_m21_runtime_once_script.py` | 2059 | `4295eb290952` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m22_10_closeout_check.py` → `tests/test_m22_10_closeout_check.py` | 1488 | `d764273a07e0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m22_7_hydration_smoke_script.py` → `tests/test_m22_7_hydration_smoke_script.py` | 1162 | `bf9061232610` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m22_skill_contracts.py` → `tests/test_m22_skill_contracts.py` | 5716 | `7aa400dafd1d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m22_skill_hydration_node.py` → `tests/test_m22_skill_hydration_node.py` | 8961 | `5d42232834cd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_10_closeout_check.py` → `tests/test_m23_10_closeout_check.py` | 2413 | `2e7781456c47` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_1_runtime_resilience_state_contract.py` → `tests/test_m23_1_runtime_resilience_state_contract.py` | 2413 | `5218bcb4362a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_2_runtime_circuit_breaker_core.py` → `tests/test_m23_2_runtime_circuit_breaker_core.py` | 2633 | `ae7fb1bc467f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_3_decide_trade_runtime_circuit_integration.py` → `tests/test_m23_3_decide_trade_runtime_circuit_integration.py` | 4310 | `3c9a76dbc319` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_5_safe_degrade_execution_policy.py` → `tests/test_m23_5_safe_degrade_execution_policy.py` | 4514 | `1f167f3e6dc5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m23_8_resilience_closeout_check.py` → `tests/test_m23_8_resilience_closeout_check.py` | 1154 | `03cb11d73a05` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m24_1_intent_state_store.py` → `tests/test_m24_1_intent_state_store.py` | 3162 | `3cb19dc9c36b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m24_2_approval_state_store_integration.py` → `tests/test_m24_2_approval_state_store_integration.py` | 4381 | `ac03c3304e9b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m24_3_duplicate_execution_claim_guard.py` → `tests/test_m24_3_duplicate_execution_claim_guard.py` | 4329 | `e06e51fc8ed2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m24_4_intent_state_reconcile_script.py` → `tests/test_m24_4_intent_state_reconcile_script.py` | 3071 | `6accf9f85291` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m24_5_real_execution_preflight.py` → `tests/test_m24_5_real_execution_preflight.py` | 3342 | `1b77cb15d7c7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m24_6_guard_precedence_check.py` → `tests/test_m24_6_guard_precedence_check.py` | 2704 | `235602d4a3d2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m24_7_intent_state_ops_query.py` → `tests/test_m24_7_intent_state_ops_query.py` | 3527 | `833e86e22599` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m24_8_closeout_check.py` → `tests/test_m24_8_closeout_check.py` | 3249 | `403414d20d2a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m25_10_notification_events_query.py` → `tests/test_m25_10_notification_events_query.py` | 5900 | `2261e34f4aaf` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m25_1_metrics_schema_freeze_v1.py` → `tests/test_m25_1_metrics_schema_freeze_v1.py` | 3540 | `382328134601` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m25_2_alert_policy_threshold_gate.py` → `tests/test_m25_2_alert_policy_threshold_gate.py` | 10657 | `7c43ccdb72d6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m25_5_ops_batch_hook.py` → `tests/test_m25_5_ops_batch_hook.py` | 8330 | `761d61cf1959` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m25_6_alert_notification_adapter.py` → `tests/test_m25_6_alert_notification_adapter.py` | 8336 | `31cc46e661f9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m26_1_dataset_manifest_check.py` → `tests/test_m26_1_dataset_manifest_check.py` | 1304 | `23aac21f70b3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m26_2_replay_runner.py` → `tests/test_m26_2_replay_runner.py` | 2229 | `005f0ad6adb5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m26_3_scorecard.py` → `tests/test_m26_3_scorecard.py` | 3164 | `dd3a8875c926` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m26_4_ab_evaluation.py` → `tests/test_m26_4_ab_evaluation.py` | 3087 | `25173d621422` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m26_5_promotion_gate_check.py` → `tests/test_m26_5_promotion_gate_check.py` | 3405 | `ff17e54fed57` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m26_6_closeout_check.py` → `tests/test_m26_6_closeout_check.py` | 2341 | `aa0f1a16eca5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_10_closeout_check.py` → `tests/test_m27_10_closeout_check.py` | 2330 | `ae438e2042e4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_1_allocation_policy.py` → `tests/test_m27_1_allocation_policy.py` | 2211 | `4ba24efc2925` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_2_conflict_resolution.py` → `tests/test_m27_2_conflict_resolution.py` | 3334 | `9c89a962813e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_3_portfolio_budget_boundary.py` → `tests/test_m27_3_portfolio_budget_boundary.py` | 3989 | `bcb1280f4b2c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_4_runtime_portfolio_guard_integration.py` → `tests/test_m27_4_runtime_portfolio_guard_integration.py` | 4956 | `9894c3f9caf9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_6_portfolio_guard_alert_policy.py` → `tests/test_m27_6_portfolio_guard_alert_policy.py` | 6275 | `c9d6d2e59a0c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_7_portfolio_guard_notify_context.py` → `tests/test_m27_7_portfolio_guard_notify_context.py` | 3346 | `5af5028126c3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_8_portfolio_guard_notify_routing.py` → `tests/test_m27_8_portfolio_guard_notify_routing.py` | 1267 | `02bdef830cb2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m27_9_portfolio_guard_notify_query.py` → `tests/test_m27_9_portfolio_guard_notify_query.py` | 1641 | `a7ad8f2e3480` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_1_runtime_profile_scaffold.py` → `tests/test_m28_1_runtime_profile_scaffold.py` | 4971 | `0a4ff7547f85` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_2_runtime_lifecycle_hooks.py` → `tests/test_m28_2_runtime_lifecycle_hooks.py` | 2876 | `6a2a35d348cb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_3_rollout_rollback_check.py` → `tests/test_m28_3_rollout_rollback_check.py` | 2293 | `f724f2cff5e3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_4_startup_preflight_check.py` → `tests/test_m28_4_startup_preflight_check.py` | 4304 | `03b6fc55a018` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_5_scheduler_worker_launch_wrapper_check.py` → `tests/test_m28_5_scheduler_worker_launch_wrapper_check.py` | 4253 | `936db7eb8d36` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_6_launch_hook_integration_check.py` → `tests/test_m28_6_launch_hook_integration_check.py` | 4213 | `5d5b3e619da0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_7_deploy_launch_templates.py` → `tests/test_m28_7_deploy_launch_templates.py` | 2690 | `ee4deb1e0ded` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_8_registration_helpers.py` → `tests/test_m28_8_registration_helpers.py` | 4051 | `2318c0550a95` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m28_9_closeout_check.py` → `tests/test_m28_9_closeout_check.py` | 2486 | `631eff720ec7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_10_governance_closeout_check.py` → `tests/test_m29_10_governance_closeout_check.py` | 2484 | `afa04721aae0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_1_feature_engine.py` → `tests/test_m29_1_feature_engine.py` | 1925 | `7fd85df71b71` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_6_audit_trail_check.py` → `tests/test_m29_6_audit_trail_check.py` | 2412 | `e36c8201e799` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_7_log_archive_integrity_check.py` → `tests/test_m29_7_log_archive_integrity_check.py` | 2389 | `3401bc2b5148` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_8_incident_timeline_check.py` → `tests/test_m29_8_incident_timeline_check.py` | 2266 | `f13099c6c5ef` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m29_9_disaster_recovery_drill.py` → `tests/test_m29_9_disaster_recovery_drill.py` | 2939 | `82436da09bc7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m30_1_quality_gates_bundle.py` → `tests/test_m30_1_quality_gates_bundle.py` | 2390 | `e2ed3868cba3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m30_2_release_signoff_checklist.py` → `tests/test_m30_2_release_signoff_checklist.py` | 2665 | `e151ae021f9c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m30_4_final_golive_signoff.py` → `tests/test_m30_4_final_golive_signoff.py` | 3716 | `59ea5f5addc9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m31_17_theme_candidate_flow_upgrade.py` → `tests/test_m31_17_theme_candidate_flow_upgrade.py` | 21247 | `0b1ca8d3cfd0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m31_1_slo_incident_review_check.py` → `tests/test_m31_1_slo_incident_review_check.py` | 7697 | `b655cfa3a470` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m31_2_mock_investor_exam_check.py` → `tests/test_m31_2_mock_investor_exam_check.py` | 10406 | `154b482f02ff` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m31_3_weekly_health_summary.py` → `tests/test_m31_3_weekly_health_summary.py` | 6575 | `2b5d3f8c3a5d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m31_agent_chain_probe.py` → `tests/test_m31_agent_chain_probe.py` | 1060 | `9acbcc9befc7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m31_strategy_baseline_snapshot_yaml.py` → `tests/test_m31_strategy_baseline_snapshot_yaml.py` | 462 | `606da8a5baaf` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m7_demo_catalog.py` → `tests/test_m7_demo_catalog.py` | 1015 | `430723acf393` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m9_build_snapshots.py` → `tests/test_m9_build_snapshots.py` | 732 | `31bf23f5fc49` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m9_real_portfolio_reader.py` → `tests/test_m9_real_portfolio_reader.py` | 7016 | `0f4553b50f8e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m9_real_price_reader.py` → `tests/test_m9_real_price_reader.py` | 2702 | `a35e50fe5831` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m9_snapshots.py` → `tests/test_m9_snapshots.py` | 17324 | `e331285be4a1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_market_data_receipts.py` → `tests/test_market_data_receipts.py` | 10635 | `e415f08dfda8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_market_rail_translation.py` → `tests/test_market_rail_translation.py` | 2794 | `2c43e50d00d9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_market_regime_rail_review.py` → `tests/test_market_regime_rail_review.py` | 3022 | `99afacd08e89` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_memory_contamination_review.py` → `tests/test_memory_contamination_review.py` | 7888 | `62d5fc4deb96` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_model_catalog_store.py` → `tests/test_model_catalog_store.py` | 5051 | `ebbbbda9cea0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_news_pipeline_provider_shape_compat.py` → `tests/test_news_pipeline_provider_shape_compat.py` | 5592 | `97d828bb44c3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_no_trade_attribution.py` → `tests/test_no_trade_attribution.py` | 3641 | `a955bb3387e4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_offhours_full_trace_bundle.py` → `tests/test_offhours_full_trace_bundle.py` | 6531 | `f3eeb183f3e9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_offhours_validation_loop.py` → `tests/test_offhours_validation_loop.py` | 4961 | `4c402c8448fd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_offhours_validation_runtime.py` → `tests/test_offhours_validation_runtime.py` | 2002 | `78ea0f181f74` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opening_alpha_executable_quote_refresh.py` → `tests/test_opening_alpha_executable_quote_refresh.py` | 20749 | `504bb6099d69` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opening_macro_snapshot_collector.py` → `tests/test_opening_macro_snapshot_collector.py` | 2322 | `686f211b4be9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opening_rank1_controlled_probe.py` → `tests/test_opening_rank1_controlled_probe.py` | 22182 | `568fa93ed537` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opening_rank1_deep_dive.py` → `tests/test_opening_rank1_deep_dive.py` | 6546 | `ae51f2969e3c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opening_rank1_longitudinal.py` → `tests/test_opening_rank1_longitudinal.py` | 9487 | `f5fee5445678` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opening_rank1_market_snapshot.py` → `tests/test_opening_rank1_market_snapshot.py` | 4987 | `04787b8db364` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opening_rank1_observation_price.py` → `tests/test_opening_rank1_observation_price.py` | 1620 | `c442447263ea` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opening_rank1_shadow.py` → `tests/test_opening_rank1_shadow.py` | 14669 | `d7583280ace3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_openrouter_client_extract_text.py` → `tests/test_openrouter_client_extract_text.py` | 1982 | `09bb373faab9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_opportunity_engine_shadow.py` → `tests/test_opportunity_engine_shadow.py` | 9918 | `d2ecb6dc92e5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p0_crash_matrix.py` → `tests/test_p0_crash_matrix.py` | 19503 | `85adcf18ea0f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p0_pytest_isolation_fix2.py` → `tests/test_p0_pytest_isolation_fix2.py` | 8048 | `82f89a6e39b0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p0c_graceful_shutdown.py` → `tests/test_p0c_graceful_shutdown.py` | 6574 | `638968a1c2fd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p0d_cutover_rollback_simulation.py` → `tests/test_p0d_cutover_rollback_simulation.py` | 7012 | `7b6480639c7b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p0d_runtime_ownership.py` → `tests/test_p0d_runtime_ownership.py` | 14427 | `915c54ea4ec4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_ai_duration_language_owner.py` → `tests/test_p152_ai_duration_language_owner.py` | 3030 | `695e08e6d3a1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_ai_facade_text_helpers.py` → `tests/test_p152_ai_facade_text_helpers.py` | 2064 | `d6a79187b230` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_facade_abi_and_authority_boundary.py` → `tests/test_p152_facade_abi_and_authority_boundary.py` | 4051 | `d29e42b16b18` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_facade_consumer_static_index.py` → `tests/test_p152_facade_consumer_static_index.py` | 2197 | `ab81d8d4d179` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_facade_symbol_ledger.py` → `tests/test_p152_facade_symbol_ledger.py` | 3144 | `2e4c0d6192d6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_integration_acceptance_inventory.py` → `tests/test_p152_integration_acceptance_inventory.py` | 1774 | `63302531c8d3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_lifecycle_evidence_owner.py` → `tests/test_p152_lifecycle_evidence_owner.py` | 2609 | `dcc856491199` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_lifecycle_human_owner.py` → `tests/test_p152_lifecycle_human_owner.py` | 3292 | `1d60916849ac` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_markdown_clean_news_headlines_owner.py` → `tests/test_p152_markdown_clean_news_headlines_owner.py` | 4562 | `4e4ac59728dd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_markdown_clean_summary_language_owner.py` → `tests/test_p152_markdown_clean_summary_language_owner.py` | 2574 | `3d85c0001a53` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_markdown_render_section_owners.py` → `tests/test_p152_markdown_render_section_owners.py` | 8361 | `961d39f3f63d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_new_owner_dependency_gate.py` → `tests/test_p152_new_owner_dependency_gate.py` | 4323 | `dd2cf6eccb60` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_prelocal_consumer_debt.py` → `tests/test_p152_prelocal_consumer_debt.py` | 1718 | `2a2d1707e819` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_r2c_helper_seams.py` → `tests/test_p152_r2c_helper_seams.py` | 3187 | `45b5399b819d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_r3_harness_guards.py` → `tests/test_p152_r3_harness_guards.py` | 17515 | `3ea32387eb90` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_r3_moved_bodies.py` → `tests/test_p152_r3_moved_bodies.py` | 12044 | `0b7f46cbd5b7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_render_diagnostics_owner.py` → `tests/test_p152_render_diagnostics_owner.py` | 3074 | `820299693d2f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_snapshot_parity.py` → `tests/test_p152_snapshot_parity.py` | 4727 | `1e6eb70fab0c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_summary_findings_owner.py` → `tests/test_p152_summary_findings_owner.py` | 2390 | `27634d67f110` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p152_summary_input_part_owners.py` → `tests/test_p152_summary_input_part_owners.py` | 3249 | `88be37ca326e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p154_wave_b_moved_bodies.py` → `tests/test_p154_wave_b_moved_bodies.py` | 15164 | `bb5cd5e83046` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p154_wave_b_scope_and_authority_boundary.py` → `tests/test_p154_wave_b_scope_and_authority_boundary.py` | 4234 | `bf5bbb75a753` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p155_runtime_naming_aliases.py` → `tests/test_p155_runtime_naming_aliases.py` | 4133 | `f69cde2f4954` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p155_wave_c_moved_bodies.py` → `tests/test_p155_wave_c_moved_bodies.py` | 9580 | `243ca4880549` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p155_wave_c_scope_and_authority_boundary.py` → `tests/test_p155_wave_c_scope_and_authority_boundary.py` | 6856 | `2813bf7854d6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p156_parity_harness.py` → `tests/test_p156_parity_harness.py` | 57329 | `1060b092c591` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p156_second_pass_extraction_gates.py` → `tests/test_p156_second_pass_extraction_gates.py` | 13634 | `2632c74ea0b4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p157_third_pass_t1_extraction_gates.py` → `tests/test_p157_third_pass_t1_extraction_gates.py` | 14145 | `ffa15eddbd27` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p158_third_pass_t2_extraction_gates.py` → `tests/test_p158_third_pass_t2_extraction_gates.py` | 15912 | `00f359ccf961` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p159_current_owner_contract_gates.py` → `tests/test_p159_current_owner_contract_gates.py` | 27901 | `80f3d4b4309f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p159_ownership_matrix_provenance.py` → `tests/test_p159_ownership_matrix_provenance.py` | 3443 | `a4195fb29239` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p159_static_purity_closure.py` → `tests/test_p159_static_purity_closure.py` | 12133 | `ed9a187aa0dd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_b_versioned_contract.py` → `tests/test_p15_b_versioned_contract.py` | 5273 | `f5631b3583cc` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_consumer_inventory.py` → `tests/test_p15_consumer_inventory.py` | 1154 | `f3603df078e8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_harness_performance_safety.py` → `tests/test_p15_harness_performance_safety.py` | 4327 | `0117e70c3795` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_integration_completion.py` → `tests/test_p15_integration_completion.py` | 25123 | `449446d0d218` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_overview_live_projection.py` → `tests/test_p15_overview_live_projection.py` | 10522 | `212b93585e84` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_perf2a_variant_inventory_equivalence.py` → `tests/test_p15_perf2a_variant_inventory_equivalence.py` | 7218 | `1d64a5a630f6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p161_agent_output_contract_freeze.py` → `tests/test_p161_agent_output_contract_freeze.py` | 15524 | `8deb3a6b4190` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p161_t35_extraction_gates.py` → `tests/test_p161_t35_extraction_gates.py` | 12376 | `35d1ff646c7a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p162_t4a_extraction_gates.py` → `tests/test_p162_t4a_extraction_gates.py` | 11060 | `4f4e7baa1c58` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p163_t4b_extraction_gates.py` → `tests/test_p163_t4b_extraction_gates.py` | 15765 | `205db8f231cf` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p164_t4c_extraction_gates.py` → `tests/test_p164_t4c_extraction_gates.py` | 16492 | `0de2a4563953` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p165_t4d_extraction_gates.py` → `tests/test_p165_t4d_extraction_gates.py` | 17615 | `111bbace6299` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p168_wave_b_shim_verifier_negatives.py` → `tests/test_p168_wave_b_shim_verifier_negatives.py` | 8690 | `0364d00cdeea` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p169_broad_failure_evidence.py` → `tests/test_p169_broad_failure_evidence.py` | 2585 | `9b8b4d6ba584` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p173_p058_integration_contracts.py` → `tests/test_p173_p058_integration_contracts.py` | 2825 | `189e5a74978f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p1_e2e_execution_readiness_integrated_chain.py` → `tests/test_p1_e2e_execution_readiness_integrated_chain.py` | 7478 | `4c99c1f3018e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p1_execution_readiness.py` → `tests/test_p1_execution_readiness.py` | 16432 | `e4e85bd3ba9a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_paper_trading_execution_finalization.py` → `tests/test_paper_trading_execution_finalization.py` | 14747 | `6b9735962153` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_patch_notes_sync.py` → `tests/test_patch_notes_sync.py` | 3534 | `57791e5b54cd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_phase1_agent_artifact_quality.py` → `tests/test_phase1_agent_artifact_quality.py` | 77870 | `e9777761d46a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_phase3_lifecycle_bundle.py` → `tests/test_phase3_lifecycle_bundle.py` | 5421 | `6f51c4d87097` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_phase_6_2_consumption.py` → `tests/test_phase_6_2_consumption.py` | 1734 | `f211fcd30fbc` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_policy_surface_summary.py` → `tests/test_policy_surface_summary.py` | 5385 | `da2ac1e84f55` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_position_horizon_revision.py` → `tests/test_position_horizon_revision.py` | 7696 | `872a7e4f8ed6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_post_exit_shadow_recap.py` → `tests/test_post_exit_shadow_recap.py` | 19766 | `0b5605886688` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_post_reclaim_offline_research.py` → `tests/test_post_reclaim_offline_research.py` | 9783 | `372cee70b6a9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_preopen_macro_snapshot.py` → `tests/test_preopen_macro_snapshot.py` | 1444 | `a1cad0a5073b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_process_tree_status.py` → `tests/test_process_tree_status.py` | 1478 | `51f713a4892e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_profitability_recovery_day1.py` → `tests/test_profitability_recovery_day1.py` | 8379 | `93776233694c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_pytest_artifact_hygiene.py` → `tests/test_pytest_artifact_hygiene.py` | 6181 | `501a7444b928` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q10_collector_fix3.py` → `tests/test_q10_collector_fix3.py` | 25317 | `9285fa1f4124` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q10_incident_price_integrity.py` → `tests/test_q10_incident_price_integrity.py` | 1583 | `106b0958f222` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q10_index_close_fallback.py` → `tests/test_q10_index_close_fallback.py` | 6393 | `80169cf4969e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q10_index_observation_collector.py` → `tests/test_q10_index_observation_collector.py` | 11648 | `b9d268e5d9de` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q10_lead_market_forward_validation.py` → `tests/test_q10_lead_market_forward_validation.py` | 10241 | `b8f14e4c3e43` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q10_reaction_reader_collector_integration.py` → `tests/test_q10_reaction_reader_collector_integration.py` | 11507 | `3fd90183d89d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q10_readiness_forward_validation.py` → `tests/test_q10_readiness_forward_validation.py` | 1072 | `08a8d4fde690` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q12_btc_0855_capture.py` → `tests/test_q12_btc_0855_capture.py` | 5115 | `cea380cf665b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q12_btc_woori_hypothesis_validation.py` → `tests/test_q12_btc_woori_hypothesis_validation.py` | 6173 | `230ae8a8562a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q12_delivery_alignment.py` → `tests/test_q12_delivery_alignment.py` | 8271 | `36413f94cdd2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q12_historical_policy_review.py` → `tests/test_q12_historical_policy_review.py` | 3543 | `3f64f86fce7f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q12_vnext.py` → `tests/test_q12_vnext.py` | 7887 | `6a74184a6140` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q13_q14_validation.py` → `tests/test_q13_q14_validation.py` | 3478 | `f372c8fb3563` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q16_proxy_rejection_review.py` → `tests/test_q16_proxy_rejection_review.py` | 10721 | `dba5274829e9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q8_evaluation_contract.py` → `tests/test_q8_evaluation_contract.py` | 2037 | `c1b33e7c3e57` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q8_lane_decision_table.py` → `tests/test_q8_lane_decision_table.py` | 1113 | `5243132c1e8b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q8_shadow_blocker_review.py` → `tests/test_q8_shadow_blocker_review.py` | 3474 | `c45e27dd7f12` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q9_artifact_repair.py` → `tests/test_q9_artifact_repair.py` | 7721 | `915424b202b9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q9_day_validity.py` → `tests/test_q9_day_validity.py` | 16458 | `d1c51ed4600e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q9_decision_snapshots.py` → `tests/test_q9_decision_snapshots.py` | 10472 | `982cfd61c2f3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q9_evaluation.py` → `tests/test_q9_evaluation.py` | 28887 | `e7732ebeb1e8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_q9_start_gate.py` → `tests/test_q9_start_gate.py` | 6113 | `d991533b3e27` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_context.py` → `tests/test_quant_context.py` | 4676 | `f7ffb378cdcd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_decision.py` → `tests/test_quant_decision.py` | 10678 | `a2155a404c9d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_factors.py` → `tests/test_quant_factors.py` | 4407 | `f6be4ba33c16` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_memory_scorecard.py` → `tests/test_quant_memory_scorecard.py` | 4812 | `9e80a41739dc` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_shadow_candidate_evaluation.py` → `tests/test_quant_shadow_candidate_evaluation.py` | 15405 | `8c9a7617d8e4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_shadow_candidates.py` → `tests/test_quant_shadow_candidates.py` | 24514 | `58a89f33b571` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_shadow_forward_outcomes.py` → `tests/test_quant_shadow_forward_outcomes.py` | 7875 | `936834cbf8dc` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_suitability.py` → `tests/test_quant_suitability.py` | 2103 | `1c95bda61105` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_tactic_evaluation.py` → `tests/test_quant_tactic_evaluation.py` | 4061 | `b27efa062090` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_tactics.py` → `tests/test_quant_tactics.py` | 2637 | `715f5245ae06` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_quant_trade_diagnosis.py` → `tests/test_quant_trade_diagnosis.py` | 8597 | `cf900093a70d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_query_trade_reason_chain.py` → `tests/test_query_trade_reason_chain.py` | 6930 | `0c4549f5df39` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_r61_scope_fix.py` → `tests/test_r61_scope_fix.py` | 28284 | `d955df60008c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_r62_attempt_and_lock.py` → `tests/test_r62_attempt_and_lock.py` | 24332 | `c324f3566f94` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_r6_readiness_evidence.py` → `tests/test_r6_readiness_evidence.py` | 22746 | `edadb55d0359` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rank1_feature_mart.py` → `tests/test_rank1_feature_mart.py` | 17822 | `41c2a926d71f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_reasoning_trace.py` → `tests/test_reasoning_trace.py` | 1251 | `957fe64ff346` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_restart_live_session.py` → `tests/test_restart_live_session.py` | 372 | `416a4017d96b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_live_session_summary.py` → `tests/test_run_live_session_summary.py` | 5442 | `f1e997243986` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_live_session_watch.py` → `tests/test_run_live_session_watch.py` | 2859 | `f13ffcfaf8d1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_m13_live_loop_lock.py` → `tests/test_run_m13_live_loop_lock.py` | 5450 | `721591d6338a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_mock_exam_day.py` → `tests/test_run_mock_exam_day.py` | 38122 | `08c4b3bd04f0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_phase5_validation_bundle.py` → `tests/test_run_phase5_validation_bundle.py` | 12332 | `97bdbced97a6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_q10_index_observation_collector.py` → `tests/test_run_q10_index_observation_collector.py` | 11225 | `00811183c456` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_run_session.py` → `tests/test_run_session.py` | 1636 | `e128b8e54233` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_runtime_entrypoint_common.py` → `tests/test_runtime_entrypoint_common.py` | 1066 | `7d77039fea3a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_runtime_entrypoint_import_boundaries.py` → `tests/test_runtime_entrypoint_import_boundaries.py` | 1377 | `a2586606ff54` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_runtime_mode_gate.py` → `tests/test_runtime_mode_gate.py` | 11254 | `b7c73c61a535` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_same_symbol_loss_reentry.py` → `tests/test_same_symbol_loss_reentry.py` | 4266 | `1b2e0e36ab33` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_same_symbol_sequences.py` → `tests/test_same_symbol_sequences.py` | 3008 | `c8db7085efe3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scan_candidates_universe_upgrade.py` → `tests/test_scan_candidates_universe_upgrade.py` | 1129 | `c2ec78f5a5c7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scheduled_intelligence.py` → `tests/test_scheduled_intelligence.py` | 3753 | `036c9ef3240c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scripts_issue8_followup.py` → `tests/test_scripts_issue8_followup.py` | 4242 | `aa26bb1c79f9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_scripts_target_tree_compat_audit.py` → `tests/test_scripts_target_tree_compat_audit.py` | 4561 | `4d256c4b09da` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_sell_cooldown_env_alias_decide_trade.py` → `tests/test_sell_cooldown_env_alias_decide_trade.py` | 1603 | `02fd3d5c6963` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_session_entry_dispatch.py` → `tests/test_session_entry_dispatch.py` | 1113 | `ba4fcc3150e2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_settings.py` → `tests/test_settings.py` | 1385 | `0c31aa0eb9bb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_shadow_loop_session.py` → `tests/test_shadow_loop_session.py` | 762 | `f81d3909f869` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_shared_role_contracts.py` → `tests/test_shared_role_contracts.py` | 4067 | `7b9ef1f32685` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_shared_stage_provenance.py` → `tests/test_shared_stage_provenance.py` | 940 | `5d534013e770` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_short_alpha_discriminator.py` → `tests/test_short_alpha_discriminator.py` | 10825 | `4e1a506a7dfb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_smoke_m20_llm_script.py` → `tests/test_smoke_m20_llm_script.py` | 494 | `4c63e095e978` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_stage2_authority_review.py` → `tests/test_stage2_authority_review.py` | 6873 | `68cabdf19f73` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_stage3_horizon_lineage.py` → `tests/test_stage3_horizon_lineage.py` | 12132 | `c6faca4a06b1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_start_trading_day.py` → `tests/test_start_trading_day.py` | 16336 | `5b312db953f8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_state_store.py` → `tests/test_state_store.py` | 3054 | `3b297ac57cab` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_data_quality_signal_contract.py` → `tests/test_strategy_data_quality_signal_contract.py` | 4646 | `800419ea9c29` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_evolution_learning.py` → `tests/test_strategy_evolution_learning.py` | 0 | `e69de29bb2d1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_feature_engine_upgrade.py` → `tests/test_strategy_feature_engine_upgrade.py` | 2637 | `33651439ede9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_feedback_builder.py` → `tests/test_strategy_feedback_builder.py` | 4861 | `4c694e981d9c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_horizon_feedback.py` → `tests/test_strategy_horizon_feedback.py` | 11754 | `ddfdd0145913` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_horizon_operational_policy.py` → `tests/test_strategy_horizon_operational_policy.py` | 4224 | `9f3e89905856` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_memory_store.py` → `tests/test_strategy_memory_store.py` | 5210 | `9a3790ec62b6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_memory_window_packets.py` → `tests/test_strategy_memory_window_packets.py` | 10902 | `9df03b189308` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_performance_feedback.py` → `tests/test_strategy_performance_feedback.py` | 24311 | `86b05aafa606` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_policy_contract.py` → `tests/test_strategy_policy_contract.py` | 3327 | `4314a48f650e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_read_model.py` → `tests/test_strategy_read_model.py` | 10232 | `4b8cf060e616` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_sizing_exit_upgrade.py` → `tests/test_strategy_sizing_exit_upgrade.py` | 31810 | `62026aea3705` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_universe_builder.py` → `tests/test_strategy_universe_builder.py` | 3805 | `448a127254d1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_v1_multi_strategy_selection.py` → `tests/test_strategy_v1_multi_strategy_selection.py` | 6293 | `3aaaf877fbaa` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_strategy_v1_regime_momentum.py` → `tests/test_strategy_v1_regime_momentum.py` | 6395 | `05442d390568` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_structural_alpha_batch1.py` → `tests/test_structural_alpha_batch1.py` | 6360 | `51923bd3ae48` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_structural_alpha_batch2.py` → `tests/test_structural_alpha_batch2.py` | 4822 | `176dc8879f59` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_symbol_allowlist_guard.py` → `tests/test_symbol_allowlist_guard.py` | 2093 | `7a5284fc31ff` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_symbol_read_model.py` → `tests/test_symbol_read_model.py` | 12468 | `f1b165c49b44` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_token_cache.py` → `tests/test_token_cache.py` | 801 | `994f1086cb72` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_bundle_assembly.py` → `tests/test_trade_bundle_assembly.py` | 20087 | `251f599498d3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_bundle_persistence.py` → `tests/test_trade_bundle_persistence.py` | 11800 | `7fecd89dedcf` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_bundle_state.py` → `tests/test_trade_bundle_state.py` | 18302 | `f3a63eada7ef` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_execution_snapshot.py` → `tests/test_trade_execution_snapshot.py` | 6488 | `f2158296471a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_lifecycle_builder.py` → `tests/test_trade_lifecycle_builder.py` | 12540 | `a09e0288d934` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_memory_application_surface.py` → `tests/test_trade_memory_application_surface.py` | 15850 | `870d711689e7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_memory_surface.py` → `tests/test_trade_memory_surface.py` | 22856 | `98bde173a706` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_read_model.py` → `tests/test_trade_read_model.py` | 11542 | `709b5337c5ff` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_regeneration_truth.py` → `tests/test_trade_regeneration_truth.py` | 8637 | `127f168397ee` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_summary_symbol_metadata.py` → `tests/test_trade_summary_symbol_metadata.py` | 13420 | `37a92b6cc175` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_symbol_context.py` → `tests/test_trade_symbol_context.py` | 6918 | `dcdcbc3bf490` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_trade_symbol_integrity.py` → `tests/test_trade_symbol_integrity.py` | 1829 | `852d67f83972` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_update_state_after_execution.py` → `tests/test_update_state_after_execution.py` | 28911 | `feb0df41f989` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_windows_launcher_contracts.py` → `tests/test_windows_launcher_contracts.py` | 6824 | `f760a90021fa` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_windows_subprocess.py` → `tests/test_windows_subprocess.py` | 1271 | `441e62fb89ae` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_yfinance_dependency_integrity.py` → `tests/test_yfinance_dependency_integrity.py` | 17715 | `b56dda4c461b` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
