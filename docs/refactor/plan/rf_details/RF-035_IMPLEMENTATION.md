# RF-035 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/CLAUDE_A/RF-035.md` blob `d812ede2594dee5a865e4582124aeb733f595359`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 119개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/reporting/live_execution_bundle_runner.py` | 130855 | `df06f64556dd0468a067303a9555ce473228f4bc` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/live_execution_bundle_runner_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/strategist_llm_summary.py` | 76059 | `18bba177d241299a32aa6d95a49f712148ffe78d` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/strategist_llm_summary_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/phase_runtime_health.py` | 66823 | `bc8c24db20a26b81cef047362266d6dcbe06fbd5` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/phase_runtime_health_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/intraday_trade_reports.py` | 63940 | `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/intraday_trade_reports_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/quant_shadow_candidate_evaluation.py` | 61232 | `c46916f178b600cef3729d65e197e7e971d851cd` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/quant_shadow_candidate_evaluation_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_bundle_assembly.py` | 57386 | `f5c61ac32748c05e5070004e68fac96e2034119b` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_bundle_assembly_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/closeout_maintenance.py` | 43661 | `8d2ae15b818820f7a317022e3b66b20c36534154` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/closeout_maintenance_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/broker_closed_trade_reconciler.py` | 40976 | `cf3b183a07209689b5de6ff47727a2e8a232e1fb` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/broker_closed_trade_reconciler_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/q8_historical_review.py` | 40653 | `c96a8053ae393dc5cf0618bb774e59afa1074b37` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/q8_historical_review_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_lifecycle_builder.py` | 38586 | `3fc48e4da0493383770fc462d1c88e45e398e632` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_lifecycle_builder_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/llm_artifacts.py` | 33278 | `06dd435f68aeae0043e43f27f0b1600fa3e61b0c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/llm_artifacts_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/agent_pipeline_trace.py` | 32198 | `ced3ee27e2f9ad27933242419dc2d5303ab61176` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/agent_pipeline_trace_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_bundle_state.py` | 29219 | `5890bab2575c3ffab337f5e03986fb13f1503d54` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_bundle_state_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/symbol_trade_report.py` | 25946 | `099cdbd04c9fca68115413ce4d4d4b52c4653946` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/symbol_trade_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_read_model.py` | 24679 | `783ccaaaab405b30341d49cb1ef69a8e63ad2f14` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_read_model_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/metrics_report_generator.py` | 24420 | `1f0fa8dd454ce0d32645bbe6de7a6e1f3c587954` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/metrics_report_generator_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_memory_projection_parts/memory_surface_payload.py` | 23075 | `a2545948a5ea77f4aa50b53823906ee4e35df71b` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_memory_projection_parts/memory_surface_payload_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/post_exit_shadow_recap.py` | 22044 | `b536862b59964141ccbcc55c9e0352254176c625` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/post_exit_shadow_recap_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/kiwoom_day_trade_truth.py` | 21331 | `27c35f0d39569423c61a48ff77463c4e68b47c4a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/kiwoom_day_trade_truth_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_execution_snapshot.py` | 20433 | `c2356f4de34c9017a229644f13013ed837c7fc8f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_execution_snapshot_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/daily_report_generator.py` | 20375 | `cfcc8fc70cd2b72168dcea4f40a3f01d1b1cdfbf` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/daily_report_generator_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/live_execution_scanner_evidence.py` | 20003 | `4f0f8973d3f4b780a37c6de7b47cb0e42a83ab1c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/live_execution_scanner_evidence_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/reporting/__init__.py` → `libs/reporting/__init__.py` | 1831 | `ea2b38124808` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/agent_pipeline_trace.py` → `libs/reporting/agent_pipeline_trace.py` | 32198 | `ced3ee27e2f9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alert_notifier.py` → `libs/reporting/alert_notifier.py` | 18686 | `720ca2f038f7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_artifact_io.py` → `libs/reporting/baseline_artifact_io.py` | 716 | `4410080f4774` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_candle_reader.py` → `libs/reporting/baseline_candle_reader.py` | 4319 | `36ad987e7784` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/broker_alignment.py` → `libs/reporting/broker_alignment.py` | 8222 | `6df88f9c3fe4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/broker_closed_trade_reconciler.py` → `libs/reporting/broker_closed_trade_reconciler.py` | 40976 | `cf3b183a0720` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/carryover_exit_reconciler.py` → `libs/reporting/carryover_exit_reconciler.py` | 15873 | `4f176a9c4f57` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/chart_structure_decision_hint_summary.py` → `libs/reporting/chart_structure_decision_hint_summary.py` | 545 | `89cee8c6776d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/closeout_completion_authority.py` → `libs/reporting/closeout_completion_authority.py` | 7164 | `4ed793302823` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/closeout_maintenance.py` → `libs/reporting/closeout_maintenance.py` | 43661 | `8d2ae15b8188` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/closeout_residual_positions.py` → `libs/reporting/closeout_residual_positions.py` | 17634 | `5e7145fd38b6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/controlled_mock_lane_report.py` → `libs/reporting/controlled_mock_lane_report.py` | 11682 | `362d3ce13c7d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/controlled_validation_daily.py` → `libs/reporting/controlled_validation_daily.py` | 9548 | `26f5c7c44620` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/daily_report.py` → `libs/reporting/daily_report.py` | 2053 | `0f350aaa2f4c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/daily_report_generator.py` → `libs/reporting/daily_report_generator.py` | 20375 | `cfcc8fc70cd2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/daily_report_runtime/__init__.py` → `libs/reporting/daily_report_runtime/__init__.py` | 35 | `9d48db4f9f85` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/daily_report_runtime/build_model.py` → `libs/reporting/daily_report_runtime/build_model.py` | 7823 | `2aca790cb3cc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/daily_report_runtime/freshness.py` → `libs/reporting/daily_report_runtime/freshness.py` | 4052 | `83971af2cef7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/daily_report_runtime/markdown.py` → `libs/reporting/daily_report_runtime/markdown.py` | 14965 | `8755975bc5d7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/daily_report_runtime/symbol_refresh.py` → `libs/reporting/daily_report_runtime/symbol_refresh.py` | 3431 | `db56223ede31` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/entry_blocker_read_model.py` → `libs/reporting/entry_blocker_read_model.py` | 10374 | `865e82e682d4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/event_log_reader.py` → `libs/reporting/event_log_reader.py` | 9395 | `e1d39ff2571e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/execution_truth_surface.py` → `libs/reporting/execution_truth_surface.py` | 4032 | `35ea270497e0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/fact_narrative_report.py` → `libs/reporting/fact_narrative_report.py` | 5364 | `b41bc7aa7577` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/intraday_trade_reports.py` → `libs/reporting/intraday_trade_reports.py` | 63940 | `819ce8b895d8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/json_array_stream.py` → `libs/reporting/json_array_stream.py` | 5093 | `2dd6173de08e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/kiwoom_day_trade_diary_truth.py` → `libs/reporting/kiwoom_day_trade_diary_truth.py` | 3681 | `79bca8d8ea46` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/kiwoom_day_trade_match_estimate.py` → `libs/reporting/kiwoom_day_trade_match_estimate.py` | 3446 | `564efdd7ed64` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/kiwoom_day_trade_truth.py` → `libs/reporting/kiwoom_day_trade_truth.py` | 21331 | `27c35f0d3956` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_bundle_runner.py` → `libs/reporting/live_execution_bundle_runner.py` | 130855 | `df06f64556dd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_event_evidence.py` → `libs/reporting/live_execution_event_evidence.py` | 12115 | `af7cc5dd91e9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_execution_runs.py` → `libs/reporting/live_execution_execution_runs.py` | 6806 | `7292694c9751` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_lifecycle_recovery.py` → `libs/reporting/live_execution_lifecycle_recovery.py` | 9255 | `d61a59ab3c1c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_llm_artifacts.py` → `libs/reporting/live_execution_llm_artifacts.py` | 6145 | `44b93ece14e5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_open_monitor.py` → `libs/reporting/live_execution_open_monitor.py` | 6195 | `d8aff7ff8081` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_post_exit.py` → `libs/reporting/live_execution_post_exit.py` | 5522 | `fa90a3518b90` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_report_artifacts.py` → `libs/reporting/live_execution_report_artifacts.py` | 5814 | `61f84a896cb0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_report_context.py` → `libs/reporting/live_execution_report_context.py` | 4484 | `52f877f641d5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_scanner_evidence.py` → `libs/reporting/live_execution_scanner_evidence.py` | 20003 | `4f0f8973d3f4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_strategist_artifacts.py` → `libs/reporting/live_execution_strategist_artifacts.py` | 18153 | `df9b71a48be3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/live_execution_trade_evidence.py` → `libs/reporting/live_execution_trade_evidence.py` | 10088 | `7147c0d2c74f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/llm_artifacts.py` → `libs/reporting/llm_artifacts.py` | 33278 | `06dd435f68ae` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/llm_daily_summary.py` → `libs/reporting/llm_daily_summary.py` | 10381 | `e847ee3941da` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/market_regime_rail_review.py` → `libs/reporting/market_regime_rail_review.py` | 12780 | `e6cfd5280d59` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/metrics_report/__init__.py` → `libs/reporting/metrics_report/__init__.py` | 35 | `9d48db4f9f85` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/metrics_report/aggregators.py` → `libs/reporting/metrics_report/aggregators.py` | 6032 | `d6c44ef68c1a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/metrics_report/event_extractors.py` → `libs/reporting/metrics_report/event_extractors.py` | 4124 | `e60cab7156cd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/metrics_report/markdown.py` → `libs/reporting/metrics_report/markdown.py` | 12491 | `035871ee0dff` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/metrics_report_generator.py` → `libs/reporting/metrics_report_generator.py` | 24420 | `1f0fa8dd454c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/monitor_timeline_reconciliation.py` → `libs/reporting/monitor_timeline_reconciliation.py` | 4919 | `622b2341f46b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/narrative_axes.py` → `libs/reporting/narrative_axes.py` | 495 | `133b6009fc4a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/phase_runtime_health.py` → `libs/reporting/phase_runtime_health.py` | 66823 | `bc8c24db20a2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/policy_surface_summary.py` → `libs/reporting/policy_surface_summary.py` | 515 | `aa9133cc0862` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/post_exit_shadow_recap.py` → `libs/reporting/post_exit_shadow_recap.py` | 22044 | `b536862b5996` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/profitability_recovery_day1.py` → `libs/reporting/profitability_recovery_day1.py` | 19232 | `c1b07665b62d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/q8_evaluation_contract.py` → `libs/reporting/q8_evaluation_contract.py` | 5486 | `f6b08711f965` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/q8_historical_review.py` → `libs/reporting/q8_historical_review.py` | 40653 | `c96a8053ae39` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/q8_lane_decision_table.py` → `libs/reporting/q8_lane_decision_table.py` | 10819 | `d997eef97b2a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/q8_shadow_blocker_review.py` → `libs/reporting/q8_shadow_blocker_review.py` | 14588 | `7e482261ae1d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/q8_trusted_reaggregation.py` → `libs/reporting/q8_trusted_reaggregation.py` | 11779 | `47f5e9fcc30d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/q9_forward_candles.py` → `libs/reporting/q9_forward_candles.py` | 2229 | `b6a08a089aa1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_shadow_candidate_evaluation.py` → `libs/reporting/quant_shadow_candidate_evaluation.py` | 61232 | `c46916f178b6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_shadow_forward_outcomes.py` → `libs/reporting/quant_shadow_forward_outcomes.py` | 15393 | `b28078090a76` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_tactic_evaluation.py` → `libs/reporting/quant_tactic_evaluation.py` | 9311 | `f11bd1e71ded` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_tactic_report.py` → `libs/reporting/quant_tactic_report.py` | 14836 | `1e837b5bf973` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reasoning_trace.py` → `libs/reporting/reasoning_trace.py` | 497 | `ae66c79fb0b0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/report_maintenance.py` → `libs/reporting/report_maintenance.py` | 13614 | `a22d5b9acb99` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/report_metadata.py` → `libs/reporting/report_metadata.py` | 501 | `f16b72d38b13` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/report_source_helpers.py` → `libs/reporting/report_source_helpers.py` | 11127 | `bfa1137b3219` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/report_truth_surface.py` → `libs/reporting/report_truth_surface.py` | 4713 | `6b2f77837756` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_bundle_runtime_parts/__init__.py` → `libs/reporting/reporter_bundle_runtime_parts/__init__.py` | 117 | `056c7b82e441` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_bundle_runtime_parts/closed_sell_reconciliation.py` → `libs/reporting/reporter_bundle_runtime_parts/closed_sell_reconciliation.py` | 2318 | `233d94aeeb63` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_bundle_runtime_parts/lifecycle_evidence_context.py` → `libs/reporting/reporter_bundle_runtime_parts/lifecycle_evidence_context.py` | 4178 | `68f976789f80` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_bundle_runtime_parts/lifecycle_human_summaries.py` → `libs/reporting/reporter_bundle_runtime_parts/lifecycle_human_summaries.py` | 3231 | `987321333ca9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_bundle_runtime_parts/lifecycle_story_context.py` → `libs/reporting/reporter_bundle_runtime_parts/lifecycle_story_context.py` | 3827 | `b119ad62363b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_bundle_runtime_parts/report_generation_policy.py` → `libs/reporting/reporter_bundle_runtime_parts/report_generation_policy.py` | 2637 | `da6acf006897` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_bundle_runtime_parts/targeted_run_projection.py` → `libs/reporting/reporter_bundle_runtime_parts/targeted_run_projection.py` | 1451 | `e53a0ca62392` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/scheduled_intelligence/__init__.py` → `libs/reporting/scheduled_intelligence/__init__.py` | 195 | `13655fc43bdb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/scheduled_intelligence/artifacts.py` → `libs/reporting/scheduled_intelligence/artifacts.py` | 2014 | `28b12f6d3ad0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/scheduled_intelligence/closeout.py` → `libs/reporting/scheduled_intelligence/closeout.py` | 5226 | `b04551777217` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/scheduled_intelligence/preopen.py` → `libs/reporting/scheduled_intelligence/preopen.py` | 9320 | `6ad02b0c4442` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/single_trade_report.py` → `libs/reporting/single_trade_report.py` | 18240 | `9426ebc31fb7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/strategist_llm_evaluation.py` → `libs/reporting/strategist_llm_evaluation.py` | 9707 | `c9ad479f1e0a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/strategist_llm_summary.py` → `libs/reporting/strategist_llm_summary.py` | 76059 | `18bba177d241` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/strategist_quant_context_report.py` → `libs/reporting/strategist_quant_context_report.py` | 529 | `71c63f273d61` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/strategy_read_model.py` → `libs/reporting/strategy_read_model.py` | 7477 | `0855833cab10` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/symbol_read_model.py` → `libs/reporting/symbol_read_model.py` | 12463 | `f7a253607e9b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/symbol_trade_report.py` → `libs/reporting/symbol_trade_report.py` | 25946 | `099cdbd04c9f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_bundle_assembly.py` → `libs/reporting/trade_bundle_assembly.py` | 57386 | `f5c61ac32748` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_bundle_persistence.py` → `libs/reporting/trade_bundle_persistence.py` | 13637 | `40bef0aba826` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_bundle_state.py` → `libs/reporting/trade_bundle_state.py` | 29219 | `5890bab2575c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_execution_outcome_text.py` → `libs/reporting/trade_execution_outcome_text.py` | 523 | `c6a8cb09ed13` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_execution_snapshot.py` → `libs/reporting/trade_execution_snapshot.py` | 20433 | `c2356f4de34c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_execution_truth_merge.py` → `libs/reporting/trade_execution_truth_merge.py` | 2017 | `ab71e8dccaad` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_explain.py` → `libs/reporting/trade_explain.py` | 17486 | `86418b535aa7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_fallback_text.py` → `libs/reporting/trade_fallback_text.py` | 505 | `aa0a34b1898b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_fill_aggregator.py` → `libs/reporting/trade_fill_aggregator.py` | 2025 | `5806490ed21a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_lifecycle_builder.py` → `libs/reporting/trade_lifecycle_builder.py` | 38586 | `3fc48e4da049` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_memory_application_surface.py` → `libs/reporting/trade_memory_application_surface.py` | 3522 | `ff115b6a53aa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_memory_projection_parts/__init__.py` → `libs/reporting/trade_memory_projection_parts/__init__.py` | 97 | `dfc7d62782c9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_memory_projection_parts/memory_feedback_rebuild.py` → `libs/reporting/trade_memory_projection_parts/memory_feedback_rebuild.py` | 7590 | `c7157cab4e5d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_memory_projection_parts/memory_input_visibility.py` → `libs/reporting/trade_memory_projection_parts/memory_input_visibility.py` | 13174 | `b63806dc1e09` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_memory_projection_parts/memory_status_summary.py` → `libs/reporting/trade_memory_projection_parts/memory_status_summary.py` | 5722 | `294e01186038` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_memory_projection_parts/memory_surface_payload.py` → `libs/reporting/trade_memory_projection_parts/memory_surface_payload.py` | 23075 | `a2545948a5ea` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_memory_surface.py` → `libs/reporting/trade_memory_surface.py` | 19138 | `ca876102d3d2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_pnl_estimate.py` → `libs/reporting/trade_pnl_estimate.py` | 507 | `3da290340829` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_price_truth.py` → `libs/reporting/trade_price_truth.py` | 2691 | `f4948cee18e7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_read_model.py` → `libs/reporting/trade_read_model.py` | 24679 | `783ccaaaab40` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_regeneration_truth.py` → `libs/reporting/trade_regeneration_truth.py` | 7410 | `bb21bd75a27a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_markdown/__init__.py` → `libs/reporting/trade_report_markdown/__init__.py` | 92 | `8943aeb6f1b1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_markdown/monitor.py` → `libs/reporting/trade_report_markdown/monitor.py` | 14430 | `4bce9673aba1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_markdown/scanner.py` → `libs/reporting/trade_report_markdown/scanner.py` | 15195 | `4a46472d8904` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_reporter_status_text.py` → `libs/reporting/trade_reporter_status_text.py` | 519 | `8990f67614f6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_scanner_fallback_anchor.py` → `libs/reporting/trade_scanner_fallback_anchor.py` | 11572 | `29b1765e2a21` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_symbol_context.py` → `libs/reporting/trade_symbol_context.py` | 10912 | `dc2778753f5f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_symbol_integrity.py` → `libs/reporting/trade_symbol_integrity.py` | 4804 | `7551a00d57e2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_truth_resolver.py` → `libs/reporting/trade_truth_resolver.py` | 4514 | `fb43c037d130` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/truth_source_labels.py` → `libs/reporting/truth_source_labels.py` | 505 | `adec089f65a9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
