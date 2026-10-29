# RF-027 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-027.md` blob `974d0984b13d03cd9ee22a37f6fc57c4fc45c049`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 77개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/runtime/strategy_horizon_feedback.py` | 42812 | `8336d03f41ea7157b6ab207f3829215464078a9a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/strategy_horizon_feedback_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/strategist_explanation.py` | 40326 | `823ef5283ff14efbce7ff33f9c48164024c2ca30` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/strategist_explanation_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/monitor_strategy_frame.py` | 32604 | `b791470b4149f33fa7c3884098ed8b518a011190` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/monitor_strategy_frame_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/monitor_minute_ohlcv.py` | 31411 | `ca2156aaa200b39361f5519b0ba9d7bae2b88f0c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/monitor_minute_ohlcv_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/opening_rank1_controlled_probe.py` | 30131 | `36170d4e170d8ea79888ddc093e9174a9a7c2ce7` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/opening_rank1_controlled_probe_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/strategy_memory_window_common.py` | 25452 | `0a945c4715af66f238ba9b962dbd16549383a477` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/strategy_memory_window_common_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/canonical_artifacts.py` | 25384 | `b6dd5764fa077d84cdd5d957f9996ceffa9e039b` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/canonical_artifacts_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/live_loop_runner.py` | 24520 | `da4543594ad597c922859c23364f4ce003620c64` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/live_loop_runner_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/monitor_entry_cost_filter.py` | 21947 | `4965e101cb46832bf96dab975385ff9b31039eee` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/monitor_entry_cost_filter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/live_loop_lock.py` | 21845 | `d8c824077b6655bea05d7e7e90dad092a2bc5512` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/live_loop_lock_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/runtime/__init__.py` → `libs/runtime/__init__.py` | 0 | `e69de29bb2d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/broker_cost_profile.py` → `libs/runtime/broker_cost_profile.py` | 7073 | `6cd15faca4d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/canonical_artifacts.py` → `libs/runtime/canonical_artifacts.py` | 25384 | `b6dd5764fa07` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/circuit_breaker.py` → `libs/runtime/circuit_breaker.py` | 6264 | `b378de2c15e9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander_memory_application_trace.py` → `libs/runtime/commander_memory_application_trace.py` | 10147 | `51f8d6697197` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/daily_strategy_memory_packet.py` → `libs/runtime/daily_strategy_memory_packet.py` | 7660 | `c7fe869dea80` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/dates.py` → `libs/runtime/dates.py` | 348 | `817bc9c4f1f1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/entrypoint_common.py` → `libs/runtime/entrypoint_common.py` | 2562 | `9582a34747ae` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/etf_deviation.py` → `libs/runtime/etf_deviation.py` | 6474 | `32802371c1e6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/host_supervisor.py` → `libs/runtime/host_supervisor.py` | 5678 | `ebab1f806787` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/kiwoom_market_status.py` → `libs/runtime/kiwoom_market_status.py` | 9761 | `f26bc5a985c0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/live_loop_config.py` → `libs/runtime/live_loop_config.py` | 891 | `93a2edd4ee8d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/live_loop_lock.py` → `libs/runtime/live_loop_lock.py` | 21845 | `d8c824077b66` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/live_loop_process_query.py` → `libs/runtime/live_loop_process_query.py` | 2828 | `b2771ea26ed1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/live_loop_runner.py` → `libs/runtime/live_loop_runner.py` | 24520 | `da4543594ad5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/live_session_summary_helpers.py` → `libs/runtime/live_session_summary_helpers.py` | 4622 | `14f787c07374` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/llm_report_classifier.py` → `libs/runtime/llm_report_classifier.py` | 13453 | `8c7376aaa897` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/market_hours.py` → `libs/runtime/market_hours.py` | 846 | `3510e1989921` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/market_status_closeout.py` → `libs/runtime/market_status_closeout.py` | 8925 | `9be08bdd9e11` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/memory_packet_loader.py` → `libs/runtime/memory_packet_loader.py` | 848 | `d54b3d60be62` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_candidate_cascade.py` → `libs/runtime/monitor_candidate_cascade.py` | 11829 | `e218d116ca3d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_directional_edge.py` → `libs/runtime/monitor_directional_edge.py` | 8526 | `d0e1819a43c7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_entry_blockers.py` → `libs/runtime/monitor_entry_blockers.py` | 4172 | `08d2b006917b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_entry_controls.py` → `libs/runtime/monitor_entry_controls.py` | 5788 | `e8660352a6f2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_entry_cost_filter.py` → `libs/runtime/monitor_entry_cost_filter.py` | 21947 | `4965e101cb46` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_entry_quality.py` → `libs/runtime/monitor_entry_quality.py` | 10655 | `81e89b0157a4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_entry_sizing.py` → `libs/runtime/monitor_entry_sizing.py` | 14695 | `4aa840322719` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_entry_state.py` → `libs/runtime/monitor_entry_state.py` | 3059 | `cd3a29209044` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit_confirmation.py` → `libs/runtime/monitor_exit_confirmation.py` | 186 | `00dfcfb75222` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit_inputs.py` → `libs/runtime/monitor_exit_inputs.py` | 168 | `fc007743bded` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_memory_bias.py` → `libs/runtime/monitor_memory_bias.py` | 7614 | `8043b8b28dcc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_memory_bias_reasons.py` → `libs/runtime/monitor_memory_bias_reasons.py` | 3044 | `157ace675126` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_memory_bias_rules.py` → `libs/runtime/monitor_memory_bias_rules.py` | 7362 | `edda2f741341` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_minute_ohlcv.py` → `libs/runtime/monitor_minute_ohlcv.py` | 31411 | `ca2156aaa200` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_runner_up_quality.py` → `libs/runtime/monitor_runner_up_quality.py` | 3542 | `5c0bc5370bc7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_strategy_frame.py` → `libs/runtime/monitor_strategy_frame.py` | 32604 | `b791470b4149` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monthly_strategy_memory_packet.py` → `libs/runtime/monthly_strategy_memory_packet.py` | 1306 | `196fab42ade9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/news_event_intelligence.py` → `libs/runtime/news_event_intelligence.py` | 14975 | `4828efbbf60a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/offhours_validation_runtime.py` → `libs/runtime/offhours_validation_runtime.py` | 2383 | `54a9b33cb6a8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/opening_rank1_controlled_probe.py` → `libs/runtime/opening_rank1_controlled_probe.py` | 30131 | `36170d4e170d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/opening_rank1_observation_price.py` → `libs/runtime/opening_rank1_observation_price.py` | 1835 | `f7c97c5850c3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/opening_rank1_probe_authority.py` → `libs/runtime/opening_rank1_probe_authority.py` | 2717 | `ffa3328d0a63` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/opening_rank1_probe_cost_edge.py` → `libs/runtime/opening_rank1_probe_cost_edge.py` | 6778 | `ef5aaaa44f54` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/opening_rank1_probe_discriminator.py` → `libs/runtime/opening_rank1_probe_discriminator.py` | 1254 | `e69813250f73` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/operator_summary_memory.py` → `libs/runtime/operator_summary_memory.py` | 4715 | `a6f45c6356c5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/portfolio_allocation.py` → `libs/runtime/portfolio_allocation.py` | 7114 | `04bd1befe071` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/portfolio_budget_guard.py` → `libs/runtime/portfolio_budget_guard.py` | 10127 | `41b99f77389b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/position_horizon_revision.py` → `libs/runtime/position_horizon_revision.py` | 16262 | `45f667dfb0f0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/position_sizing.py` → `libs/runtime/position_sizing.py` | 7649 | `98184588c56b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/process_tree_status.py` → `libs/runtime/process_tree_status.py` | 1657 | `c8193f0b585c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/regime.py` → `libs/runtime/regime.py` | 2805 | `1edc74ae5455` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/resilience_state.py` → `libs/runtime/resilience_state.py` | 3582 | `928d39ea0eb8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/runtime_lifecycle.py` → `libs/runtime/runtime_lifecycle.py` | 3566 | `c72bcca35a24` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/runtime_mode.py` → `libs/runtime/runtime_mode.py` | 4547 | `a02a16439671` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/runtime_output_helpers.py` → `libs/runtime/runtime_output_helpers.py` | 2165 | `d31c106e4c53` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/runtime_ownership.py` → `libs/runtime/runtime_ownership.py` | 15465 | `49ca20849d35` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/runtime_profile.py` → `libs/runtime/runtime_profile.py` | 6509 | `11b21338856d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/same_symbol_loss_reentry.py` → `libs/runtime/same_symbol_loss_reentry.py` | 5652 | `ea8ae5d6cf33` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner_bias.py` → `libs/runtime/scanner_bias.py` | 5402 | `d9ab25b1e43a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner_memory_bias.py` → `libs/runtime/scanner_memory_bias.py` | 4802 | `e2addcd78a5c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner_memory_bias_reasons.py` → `libs/runtime/scanner_memory_bias_reasons.py` | 2577 | `9043b0183cc7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner_memory_bias_rules.py` → `libs/runtime/scanner_memory_bias_rules.py` | 5176 | `4cc66a5abef1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/session_entry_dispatch.py` → `libs/runtime/session_entry_dispatch.py` | 1184 | `e33af6efcf94` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/shadow_loop_session.py` → `libs/runtime/shadow_loop_session.py` | 641 | `c75111435c24` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/stage3_horizon_lineage.py` → `libs/runtime/stage3_horizon_lineage.py` | 14055 | `0e279a73f802` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist_explanation.py` → `libs/runtime/strategist_explanation.py` | 40326 | `823ef5283ff1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist_feedback_trace.py` → `libs/runtime/strategist_feedback_trace.py` | 2658 | `0e760e7903bc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist_input_quality.py` → `libs/runtime/strategist_input_quality.py` | 6553 | `2e07b4c02593` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist_packet_visibility.py` → `libs/runtime/strategist_packet_visibility.py` | 15625 | `bc227d3966ee` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategy_horizon_feedback.py` → `libs/runtime/strategy_horizon_feedback.py` | 42812 | `8336d03f41ea` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategy_memory_support_artifacts.py` → `libs/runtime/strategy_memory_support_artifacts.py` | 7808 | `608cdc724e2c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategy_memory_window_common.py` → `libs/runtime/strategy_memory_window_common.py` | 25452 | `0a945c4715af` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategy_memory_window_sections.py` → `libs/runtime/strategy_memory_window_sections.py` | 19554 | `b3d99456d0e4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/symbol_memory_packet.py` → `libs/runtime/symbol_memory_packet.py` | 9466 | `6e437a97881d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/volume_confirmation.py` → `libs/runtime/volume_confirmation.py` | 4322 | `ca46f23d625a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/weekly_strategy_memory_packet.py` → `libs/runtime/weekly_strategy_memory_packet.py` | 1297 | `f6f9d446cc9c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/windows_subprocess.py` → `libs/runtime/windows_subprocess.py` | 1328 | `18fa7c4d4c2d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
