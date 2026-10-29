# RF-035 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/01_PENDING/CLAUDE_A/RF-035.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 119개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/reporting/live_execution_bundle_runner.py` blob `df06f64556dd0468a067303a9555ce473228f4bc` (2788 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/reporting/live_execution_bundle_runner.py::main` L1425-2769 | KEEP_EFFECT_SPLIT_PURE | `libs/reporting/live_execution_bundle_runner.py::main` | 1345행 · IO, Clock/Env |
| `libs/reporting/live_execution_bundle_runner.py::_active_background_process` L458-579 | KEEP_EFFECT_SPLIT_PURE | `libs/reporting/live_execution_bundle_runner.py::_active_background_process` | 122행 · Clock/Env |
| `libs/reporting/live_execution_bundle_runner.py::_touch_background_job_lock` L726-766 | KEEP_EFFECT_SPLIT_PURE | `libs/reporting/live_execution_bundle_runner.py::_touch_background_job_lock` | 41행 · IO, Clock/Env |
| `libs/reporting/live_execution_bundle_runner.py::_pid_active` L386-413 | MOVE_BODY | `libs/reporting/live_execution_bundle_runner_pid_active.py::_pid_active` | 28행 · 순수 후보 |
| `libs/reporting/live_execution_bundle_runner.py::_existing_trade_run_ids` L1225-1248 | MOVE_BODY | `libs/reporting/live_execution_bundle_runner_existing_trade_run_ids.py::_existing_trade_run_ids` | 24행 · 순수 후보 |
| `libs/reporting/live_execution_bundle_runner.py::_build_parser` L1401-1424 | MOVE_BODY | `libs/reporting/live_execution_bundle_runner_build_parser.py::_build_parser` | 24행 · 순수 후보 |
| `libs/reporting/live_execution_bundle_runner.py::_terminate_process_tree` L600-621 | MOVE_BODY | `libs/reporting/live_execution_bundle_runner_terminate_process_tree.py::_terminate_process_tree` | 22행 · 순수 후보 |

### main — 원본 1345행
- **확인된 책임:** `libs/reporting/live_execution_bundle_runner.py` L1425–2769; 직접 호출 helper `_build_parser`, `_bundle_role`, `_background_job_lock_path`, `_is_trueish`, `_active_background_job`, `_log_bundle_event`, `_write_background_job_lock`, `_latest_execution_day`. 감지된 효과: IO, Clock/Env.
- **목표:** `libs/reporting/live_execution_bundle_runner.py::main` (Owner Claude A, RF-035). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _active_background_process — 원본 122행
- **확인된 책임:** `libs/reporting/live_execution_bundle_runner.py` L458–579; 직접 호출 helper `_creation_epoch_from_wmi`, `_bundle_role`. 감지된 효과: Clock/Env.
- **목표:** `libs/reporting/live_execution_bundle_runner.py::_active_background_process` (Owner Claude A, RF-035). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _touch_background_job_lock — 원본 41행
- **확인된 책임:** `libs/reporting/live_execution_bundle_runner.py` L726–766; 직접 호출 helper `_bundle_role`. 감지된 효과: IO, Clock/Env.
- **목표:** `libs/reporting/live_execution_bundle_runner.py::_touch_background_job_lock` (Owner Claude A, RF-035). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _pid_active — 원본 28행
- **확인된 책임:** `libs/reporting/live_execution_bundle_runner.py` L386–413; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/reporting/live_execution_bundle_runner_pid_active.py::_pid_active` (Owner Claude A, RF-035). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _existing_trade_run_ids — 원본 24행
- **확인된 책임:** `libs/reporting/live_execution_bundle_runner.py` L1225–1248; 직접 호출 helper `_read_json_if_exists`. 감지된 효과: 없음.
- **목표:** `libs/reporting/live_execution_bundle_runner_existing_trade_run_ids.py::_existing_trade_run_ids` (Owner Claude A, RF-035). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _build_parser — 원본 24행
- **확인된 책임:** `libs/reporting/live_execution_bundle_runner.py` L1401–1424; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/reporting/live_execution_bundle_runner_build_parser.py::_build_parser` (Owner Claude A, RF-035). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/reporting/__init__.py` | `libs/reporting/__init__.py` | `ea2b38124808` / 1831B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/agent_pipeline_trace.py` | `libs/reporting/agent_pipeline_trace.py` | `ced3ee27e2f9` / 32198B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/alert_notifier.py` | `libs/reporting/alert_notifier.py` | `720ca2f038f7` / 18686B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_artifact_io.py` | `libs/reporting/baseline_artifact_io.py` | `4410080f4774` / 716B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_candle_reader.py` | `libs/reporting/baseline_candle_reader.py` | `36ad987e7784` / 4319B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/broker_alignment.py` | `libs/reporting/broker_alignment.py` | `6df88f9c3fe4` / 8222B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/broker_closed_trade_reconciler.py` | `libs/reporting/broker_closed_trade_reconciler.py` | `cf3b183a0720` / 40976B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/carryover_exit_reconciler.py` | `libs/reporting/carryover_exit_reconciler.py` | `4f176a9c4f57` / 15873B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/chart_structure_decision_hint_summary.py` | `libs/reporting/chart_structure_decision_hint_summary.py` | `89cee8c6776d` / 545B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/closeout_completion_authority.py` | `libs/reporting/closeout_completion_authority.py` | `4ed793302823` / 7164B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/closeout_maintenance.py` | `libs/reporting/closeout_maintenance.py` | `8d2ae15b8188` / 43661B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/closeout_residual_positions.py` | `libs/reporting/closeout_residual_positions.py` | `5e7145fd38b6` / 17634B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/controlled_mock_lane_report.py` | `libs/reporting/controlled_mock_lane_report.py` | `362d3ce13c7d` / 11682B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/controlled_validation_daily.py` | `libs/reporting/controlled_validation_daily.py` | `26f5c7c44620` / 9548B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/daily_report.py` | `libs/reporting/daily_report.py` | `0f350aaa2f4c` / 2053B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/daily_report_generator.py` | `libs/reporting/daily_report_generator.py` | `cfcc8fc70cd2` / 20375B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/daily_report_runtime/__init__.py` | `libs/reporting/daily_report_runtime/__init__.py` | `9d48db4f9f85` / 35B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/daily_report_runtime/build_model.py` | `libs/reporting/daily_report_runtime/build_model.py` | `2aca790cb3cc` / 7823B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/daily_report_runtime/freshness.py` | `libs/reporting/daily_report_runtime/freshness.py` | `83971af2cef7` / 4052B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/daily_report_runtime/markdown.py` | `libs/reporting/daily_report_runtime/markdown.py` | `8755975bc5d7` / 14965B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/daily_report_runtime/symbol_refresh.py` | `libs/reporting/daily_report_runtime/symbol_refresh.py` | `db56223ede31` / 3431B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/entry_blocker_read_model.py` | `libs/reporting/entry_blocker_read_model.py` | `865e82e682d4` / 10374B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/event_log_reader.py` | `libs/reporting/event_log_reader.py` | `e1d39ff2571e` / 9395B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/execution_truth_surface.py` | `libs/reporting/execution_truth_surface.py` | `35ea270497e0` / 4032B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/fact_narrative_report.py` | `libs/reporting/fact_narrative_report.py` | `b41bc7aa7577` / 5364B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/intraday_trade_reports.py` | `libs/reporting/intraday_trade_reports.py` | `819ce8b895d8` / 63940B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/json_array_stream.py` | `libs/reporting/json_array_stream.py` | `2dd6173de08e` / 5093B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/kiwoom_day_trade_diary_truth.py` | `libs/reporting/kiwoom_day_trade_diary_truth.py` | `79bca8d8ea46` / 3681B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/kiwoom_day_trade_match_estimate.py` | `libs/reporting/kiwoom_day_trade_match_estimate.py` | `564efdd7ed64` / 3446B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/kiwoom_day_trade_truth.py` | `libs/reporting/kiwoom_day_trade_truth.py` | `27c35f0d3956` / 21331B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/live_execution_bundle_runner.py` | `libs/reporting/live_execution_bundle_runner.py` | `df06f64556dd` / 130855B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/reporting/live_execution_event_evidence.py` | `libs/reporting/live_execution_event_evidence.py` | `af7cc5dd91e9` / 12115B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_execution_runs.py` | `libs/reporting/live_execution_execution_runs.py` | `7292694c9751` / 6806B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_lifecycle_recovery.py` | `libs/reporting/live_execution_lifecycle_recovery.py` | `d61a59ab3c1c` / 9255B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_llm_artifacts.py` | `libs/reporting/live_execution_llm_artifacts.py` | `44b93ece14e5` / 6145B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_open_monitor.py` | `libs/reporting/live_execution_open_monitor.py` | `d8aff7ff8081` / 6195B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_post_exit.py` | `libs/reporting/live_execution_post_exit.py` | `fa90a3518b90` / 5522B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_report_artifacts.py` | `libs/reporting/live_execution_report_artifacts.py` | `61f84a896cb0` / 5814B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_report_context.py` | `libs/reporting/live_execution_report_context.py` | `52f877f641d5` / 4484B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_scanner_evidence.py` | `libs/reporting/live_execution_scanner_evidence.py` | `4f0f8973d3f4` / 20003B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/live_execution_strategist_artifacts.py` | `libs/reporting/live_execution_strategist_artifacts.py` | `df9b71a48be3` / 18153B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/live_execution_trade_evidence.py` | `libs/reporting/live_execution_trade_evidence.py` | `7147c0d2c74f` / 10088B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/llm_artifacts.py` | `libs/reporting/llm_artifacts.py` | `06dd435f68ae` / 33278B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/llm_daily_summary.py` | `libs/reporting/llm_daily_summary.py` | `e847ee3941da` / 10381B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/market_regime_rail_review.py` | `libs/reporting/market_regime_rail_review.py` | `e6cfd5280d59` / 12780B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/metrics_report/__init__.py` | `libs/reporting/metrics_report/__init__.py` | `9d48db4f9f85` / 35B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/metrics_report/aggregators.py` | `libs/reporting/metrics_report/aggregators.py` | `d6c44ef68c1a` / 6032B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/metrics_report/event_extractors.py` | `libs/reporting/metrics_report/event_extractors.py` | `e60cab7156cd` / 4124B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/metrics_report/markdown.py` | `libs/reporting/metrics_report/markdown.py` | `035871ee0dff` / 12491B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/metrics_report_generator.py` | `libs/reporting/metrics_report_generator.py` | `1f0fa8dd454c` / 24420B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/monitor_timeline_reconciliation.py` | `libs/reporting/monitor_timeline_reconciliation.py` | `622b2341f46b` / 4919B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/narrative_axes.py` | `libs/reporting/narrative_axes.py` | `133b6009fc4a` / 495B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/phase_runtime_health.py` | `libs/reporting/phase_runtime_health.py` | `bc8c24db20a2` / 66823B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/policy_surface_summary.py` | `libs/reporting/policy_surface_summary.py` | `aa9133cc0862` / 515B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/post_exit_shadow_recap.py` | `libs/reporting/post_exit_shadow_recap.py` | `b536862b5996` / 22044B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/profitability_recovery_day1.py` | `libs/reporting/profitability_recovery_day1.py` | `c1b07665b62d` / 19232B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/q8_evaluation_contract.py` | `libs/reporting/q8_evaluation_contract.py` | `f6b08711f965` / 5486B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/q8_historical_review.py` | `libs/reporting/q8_historical_review.py` | `c96a8053ae39` / 40653B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/q8_lane_decision_table.py` | `libs/reporting/q8_lane_decision_table.py` | `d997eef97b2a` / 10819B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/q8_shadow_blocker_review.py` | `libs/reporting/q8_shadow_blocker_review.py` | `7e482261ae1d` / 14588B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/q8_trusted_reaggregation.py` | `libs/reporting/q8_trusted_reaggregation.py` | `47f5e9fcc30d` / 11779B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/q9_forward_candles.py` | `libs/reporting/q9_forward_candles.py` | `b6a08a089aa1` / 2229B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/quant_shadow_candidate_evaluation.py` | `libs/reporting/quant_shadow_candidate_evaluation.py` | `c46916f178b6` / 61232B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/quant_shadow_forward_outcomes.py` | `libs/reporting/quant_shadow_forward_outcomes.py` | `b28078090a76` / 15393B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/quant_tactic_evaluation.py` | `libs/reporting/quant_tactic_evaluation.py` | `f11bd1e71ded` / 9311B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/quant_tactic_report.py` | `libs/reporting/quant_tactic_report.py` | `1e837b5bf973` / 14836B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/reasoning_trace.py` | `libs/reporting/reasoning_trace.py` | `ae66c79fb0b0` / 497B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/report_maintenance.py` | `libs/reporting/report_maintenance.py` | `a22d5b9acb99` / 13614B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/report_metadata.py` | `libs/reporting/report_metadata.py` | `f16b72d38b13` / 501B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/report_source_helpers.py` | `libs/reporting/report_source_helpers.py` | `bfa1137b3219` / 11127B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/report_truth_surface.py` | `libs/reporting/report_truth_surface.py` | `6b2f77837756` / 4713B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/reporter_bundle_runtime_parts/__init__.py` | `libs/reporting/reporter_bundle_runtime_parts/__init__.py` | `056c7b82e441` / 117B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/reporter_bundle_runtime_parts/closed_sell_reconciliation.py` | `libs/reporting/reporter_bundle_runtime_parts/closed_sell_reconciliation.py` | `233d94aeeb63` / 2318B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/reporter_bundle_runtime_parts/lifecycle_evidence_context.py` | `libs/reporting/reporter_bundle_runtime_parts/lifecycle_evidence_context.py` | `68f976789f80` / 4178B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/reporter_bundle_runtime_parts/lifecycle_human_summaries.py` | `libs/reporting/reporter_bundle_runtime_parts/lifecycle_human_summaries.py` | `987321333ca9` / 3231B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/reporter_bundle_runtime_parts/lifecycle_story_context.py` | `libs/reporting/reporter_bundle_runtime_parts/lifecycle_story_context.py` | `b119ad62363b` / 3827B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/reporter_bundle_runtime_parts/report_generation_policy.py` | `libs/reporting/reporter_bundle_runtime_parts/report_generation_policy.py` | `da6acf006897` / 2637B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/reporter_bundle_runtime_parts/targeted_run_projection.py` | `libs/reporting/reporter_bundle_runtime_parts/targeted_run_projection.py` | `e53a0ca62392` / 1451B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/scheduled_intelligence/__init__.py` | `libs/reporting/scheduled_intelligence/__init__.py` | `13655fc43bdb` / 195B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/scheduled_intelligence/artifacts.py` | `libs/reporting/scheduled_intelligence/artifacts.py` | `28b12f6d3ad0` / 2014B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/scheduled_intelligence/closeout.py` | `libs/reporting/scheduled_intelligence/closeout.py` | `b04551777217` / 5226B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/scheduled_intelligence/preopen.py` | `libs/reporting/scheduled_intelligence/preopen.py` | `6ad02b0c4442` / 9320B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/single_trade_report.py` | `libs/reporting/single_trade_report.py` | `9426ebc31fb7` / 18240B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/strategist_llm_evaluation.py` | `libs/reporting/strategist_llm_evaluation.py` | `c9ad479f1e0a` / 9707B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/strategist_llm_summary.py` | `libs/reporting/strategist_llm_summary.py` | `18bba177d241` / 76059B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/strategist_quant_context_report.py` | `libs/reporting/strategist_quant_context_report.py` | `71c63f273d61` / 529B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/strategy_read_model.py` | `libs/reporting/strategy_read_model.py` | `0855833cab10` / 7477B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/symbol_read_model.py` | `libs/reporting/symbol_read_model.py` | `f7a253607e9b` / 12463B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/symbol_trade_report.py` | `libs/reporting/symbol_trade_report.py` | `099cdbd04c9f` / 25946B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_bundle_assembly.py` | `libs/reporting/trade_bundle_assembly.py` | `f5c61ac32748` / 57386B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_bundle_persistence.py` | `libs/reporting/trade_bundle_persistence.py` | `40bef0aba826` / 13637B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_bundle_state.py` | `libs/reporting/trade_bundle_state.py` | `5890bab2575c` / 29219B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_execution_outcome_text.py` | `libs/reporting/trade_execution_outcome_text.py` | `c6a8cb09ed13` / 523B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_execution_snapshot.py` | `libs/reporting/trade_execution_snapshot.py` | `c2356f4de34c` / 20433B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_execution_truth_merge.py` | `libs/reporting/trade_execution_truth_merge.py` | `ab71e8dccaad` / 2017B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_explain.py` | `libs/reporting/trade_explain.py` | `86418b535aa7` / 17486B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_fallback_text.py` | `libs/reporting/trade_fallback_text.py` | `aa0a34b1898b` / 505B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_fill_aggregator.py` | `libs/reporting/trade_fill_aggregator.py` | `5806490ed21a` / 2025B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_lifecycle_builder.py` | `libs/reporting/trade_lifecycle_builder.py` | `3fc48e4da049` / 38586B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_memory_application_surface.py` | `libs/reporting/trade_memory_application_surface.py` | `ff115b6a53aa` / 3522B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_memory_projection_parts/__init__.py` | `libs/reporting/trade_memory_projection_parts/__init__.py` | `dfc7d62782c9` / 97B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_memory_projection_parts/memory_feedback_rebuild.py` | `libs/reporting/trade_memory_projection_parts/memory_feedback_rebuild.py` | `c7157cab4e5d` / 7590B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_memory_projection_parts/memory_input_visibility.py` | `libs/reporting/trade_memory_projection_parts/memory_input_visibility.py` | `b63806dc1e09` / 13174B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_memory_projection_parts/memory_status_summary.py` | `libs/reporting/trade_memory_projection_parts/memory_status_summary.py` | `294e01186038` / 5722B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_memory_projection_parts/memory_surface_payload.py` | `libs/reporting/trade_memory_projection_parts/memory_surface_payload.py` | `a2545948a5ea` / 23075B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_memory_surface.py` | `libs/reporting/trade_memory_surface.py` | `ca876102d3d2` / 19138B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_pnl_estimate.py` | `libs/reporting/trade_pnl_estimate.py` | `3da290340829` / 507B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_price_truth.py` | `libs/reporting/trade_price_truth.py` | `f4948cee18e7` / 2691B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_read_model.py` | `libs/reporting/trade_read_model.py` | `783ccaaaab40` / 24679B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_regeneration_truth.py` | `libs/reporting/trade_regeneration_truth.py` | `bb21bd75a27a` / 7410B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report_markdown/__init__.py` | `libs/reporting/trade_report_markdown/__init__.py` | `8943aeb6f1b1` / 92B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report_markdown/monitor.py` | `libs/reporting/trade_report_markdown/monitor.py` | `4bce9673aba1` / 14430B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report_markdown/scanner.py` | `libs/reporting/trade_report_markdown/scanner.py` | `4a46472d8904` / 15195B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_reporter_status_text.py` | `libs/reporting/trade_reporter_status_text.py` | `8990f67614f6` / 519B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_scanner_fallback_anchor.py` | `libs/reporting/trade_scanner_fallback_anchor.py` | `29b1765e2a21` / 11572B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_symbol_context.py` | `libs/reporting/trade_symbol_context.py` | `dc2778753f5f` / 10912B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_symbol_integrity.py` | `libs/reporting/trade_symbol_integrity.py` | `7551a00d57e2` / 4804B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_truth_resolver.py` | `libs/reporting/trade_truth_resolver.py` | `fb43c037d130` / 4514B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/truth_source_labels.py` | `libs/reporting/truth_source_labels.py` | `adec089f65a9` / 505B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-035|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
