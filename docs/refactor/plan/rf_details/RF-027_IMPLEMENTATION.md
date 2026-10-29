# RF-027 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-027.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 77개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/strategy_horizon_feedback.py` blob `8336d03f41ea7157b6ab207f3829215464078a9a` (1019 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/strategy_horizon_feedback.py::extract_commander_horizon_policy` L580-619 | MOVE_BODY | `libs/runtime/strategy_horizon_feedback_extract_commander_horizon_policy.py::extract_commander_horizon_policy` | 40행 · 순수 후보 |
| `libs/runtime/strategy_horizon_feedback.py::extract_strategy_horizon_feedback` L641-668 | MOVE_BODY | `libs/runtime/strategy_horizon_feedback_extract_strategy_horizon_feedback.py::extract_strategy_horizon_feedback` | 28행 · 순수 후보 |
| `libs/runtime/strategy_horizon_feedback.py::_epoch_seconds` L191-214 | MOVE_BODY | `libs/runtime/strategy_horizon_feedback_epoch_seconds.py::_epoch_seconds` | 24행 · 순수 후보 |
| `libs/runtime/strategy_horizon_feedback.py::extract_commander_horizon_policy_from_state` L620-640 | MOVE_BODY | `libs/runtime/strategy_horizon_feedback_extract_commander_horizon_policy_fro.py::extract_commander_horizon_policy_from_state` | 21행 · 순수 후보 |
| `libs/runtime/strategy_horizon_feedback.py::extract_strategy_horizon_feedback_from_state` L669-686 | MOVE_BODY | `libs/runtime/strategy_horizon_feedback_extract_strategy_horizon_feedback_fr.py::extract_strategy_horizon_feedback_from_state` | 18행 · 순수 후보 |

### extract_commander_horizon_policy — 원본 40행
- **확인된 책임:** `libs/runtime/strategy_horizon_feedback.py` L580–619; 직접 호출 helper `_as_dict`. 감지된 효과: 없음.
- **목표:** `libs/runtime/strategy_horizon_feedback_extract_commander_horizon_policy.py::extract_commander_horizon_policy` (Owner Claude A, RF-027). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### extract_strategy_horizon_feedback — 원본 28행
- **확인된 책임:** `libs/runtime/strategy_horizon_feedback.py` L641–668; 직접 호출 helper `_as_dict`. 감지된 효과: 없음.
- **목표:** `libs/runtime/strategy_horizon_feedback_extract_strategy_horizon_feedback.py::extract_strategy_horizon_feedback` (Owner Claude A, RF-027). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _epoch_seconds — 원본 24행
- **확인된 책임:** `libs/runtime/strategy_horizon_feedback.py` L191–214; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/strategy_horizon_feedback_epoch_seconds.py::_epoch_seconds` (Owner Claude A, RF-027). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### extract_commander_horizon_policy_from_state — 원본 21행
- **확인된 책임:** `libs/runtime/strategy_horizon_feedback.py` L620–640; 직접 호출 helper `_as_dict`. 감지된 효과: 없음.
- **목표:** `libs/runtime/strategy_horizon_feedback_extract_commander_horizon_policy_fro.py::extract_commander_horizon_policy_from_state` (Owner Claude A, RF-027). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### extract_strategy_horizon_feedback_from_state — 원본 18행
- **확인된 책임:** `libs/runtime/strategy_horizon_feedback.py` L669–686; 직접 호출 helper `_as_dict`. 감지된 효과: 없음.
- **목표:** `libs/runtime/strategy_horizon_feedback_extract_strategy_horizon_feedback_fr.py::extract_strategy_horizon_feedback_from_state` (Owner Claude A, RF-027). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/__init__.py` | `libs/runtime/__init__.py` | `e69de29bb2d1` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/broker_cost_profile.py` | `libs/runtime/broker_cost_profile.py` | `6cd15faca4d1` / 7073B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/canonical_artifacts.py` | `libs/runtime/canonical_artifacts.py` | `b6dd5764fa07` / 25384B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/circuit_breaker.py` | `libs/runtime/circuit_breaker.py` | `b378de2c15e9` / 6264B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander_memory_application_trace.py` | `libs/runtime/commander_memory_application_trace.py` | `51f8d6697197` / 10147B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/daily_strategy_memory_packet.py` | `libs/runtime/daily_strategy_memory_packet.py` | `c7fe869dea80` / 7660B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/dates.py` | `libs/runtime/dates.py` | `817bc9c4f1f1` / 348B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoint_common.py` | `libs/runtime/entrypoint_common.py` | `9582a34747ae` / 2562B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/etf_deviation.py` | `libs/runtime/etf_deviation.py` | `32802371c1e6` / 6474B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/host_supervisor.py` | `libs/runtime/host_supervisor.py` | `ebab1f806787` / 5678B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/kiwoom_market_status.py` | `libs/runtime/kiwoom_market_status.py` | `f26bc5a985c0` / 9761B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/live_loop_config.py` | `libs/runtime/live_loop_config.py` | `93a2edd4ee8d` / 891B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/live_loop_lock.py` | `libs/runtime/live_loop_lock.py` | `d8c824077b66` / 21845B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/live_loop_process_query.py` | `libs/runtime/live_loop_process_query.py` | `b2771ea26ed1` / 2828B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/live_loop_runner.py` | `libs/runtime/live_loop_runner.py` | `da4543594ad5` / 24520B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/live_session_summary_helpers.py` | `libs/runtime/live_session_summary_helpers.py` | `14f787c07374` / 4622B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/llm_report_classifier.py` | `libs/runtime/llm_report_classifier.py` | `8c7376aaa897` / 13453B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/market_hours.py` | `libs/runtime/market_hours.py` | `3510e1989921` / 846B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/market_status_closeout.py` | `libs/runtime/market_status_closeout.py` | `9be08bdd9e11` / 8925B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/memory_packet_loader.py` | `libs/runtime/memory_packet_loader.py` | `d54b3d60be62` / 848B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_candidate_cascade.py` | `libs/runtime/monitor_candidate_cascade.py` | `e218d116ca3d` / 11829B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_directional_edge.py` | `libs/runtime/monitor_directional_edge.py` | `d0e1819a43c7` / 8526B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_entry_blockers.py` | `libs/runtime/monitor_entry_blockers.py` | `08d2b006917b` / 4172B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_entry_controls.py` | `libs/runtime/monitor_entry_controls.py` | `e8660352a6f2` / 5788B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_entry_cost_filter.py` | `libs/runtime/monitor_entry_cost_filter.py` | `4965e101cb46` / 21947B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/monitor_entry_quality.py` | `libs/runtime/monitor_entry_quality.py` | `81e89b0157a4` / 10655B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_entry_sizing.py` | `libs/runtime/monitor_entry_sizing.py` | `4aa840322719` / 14695B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_entry_state.py` | `libs/runtime/monitor_entry_state.py` | `cd3a29209044` / 3059B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit_confirmation.py` | `libs/runtime/monitor_exit_confirmation.py` | `00dfcfb75222` / 186B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit_inputs.py` | `libs/runtime/monitor_exit_inputs.py` | `fc007743bded` / 168B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_memory_bias.py` | `libs/runtime/monitor_memory_bias.py` | `8043b8b28dcc` / 7614B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_memory_bias_reasons.py` | `libs/runtime/monitor_memory_bias_reasons.py` | `157ace675126` / 3044B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_memory_bias_rules.py` | `libs/runtime/monitor_memory_bias_rules.py` | `edda2f741341` / 7362B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_minute_ohlcv.py` | `libs/runtime/monitor_minute_ohlcv.py` | `ca2156aaa200` / 31411B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/monitor_runner_up_quality.py` | `libs/runtime/monitor_runner_up_quality.py` | `5c0bc5370bc7` / 3542B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_strategy_frame.py` | `libs/runtime/monitor_strategy_frame.py` | `b791470b4149` / 32604B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/monthly_strategy_memory_packet.py` | `libs/runtime/monthly_strategy_memory_packet.py` | `196fab42ade9` / 1306B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/news_event_intelligence.py` | `libs/runtime/news_event_intelligence.py` | `4828efbbf60a` / 14975B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/offhours_validation_runtime.py` | `libs/runtime/offhours_validation_runtime.py` | `54a9b33cb6a8` / 2383B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/opening_rank1_controlled_probe.py` | `libs/runtime/opening_rank1_controlled_probe.py` | `36170d4e170d` / 30131B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/opening_rank1_observation_price.py` | `libs/runtime/opening_rank1_observation_price.py` | `f7c97c5850c3` / 1835B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/opening_rank1_probe_authority.py` | `libs/runtime/opening_rank1_probe_authority.py` | `ffa3328d0a63` / 2717B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/opening_rank1_probe_cost_edge.py` | `libs/runtime/opening_rank1_probe_cost_edge.py` | `ef5aaaa44f54` / 6778B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/opening_rank1_probe_discriminator.py` | `libs/runtime/opening_rank1_probe_discriminator.py` | `e69813250f73` / 1254B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/operator_summary_memory.py` | `libs/runtime/operator_summary_memory.py` | `a6f45c6356c5` / 4715B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/portfolio_allocation.py` | `libs/runtime/portfolio_allocation.py` | `04bd1befe071` / 7114B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/portfolio_budget_guard.py` | `libs/runtime/portfolio_budget_guard.py` | `41b99f77389b` / 10127B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/position_horizon_revision.py` | `libs/runtime/position_horizon_revision.py` | `45f667dfb0f0` / 16262B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/position_sizing.py` | `libs/runtime/position_sizing.py` | `98184588c56b` / 7649B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/process_tree_status.py` | `libs/runtime/process_tree_status.py` | `c8193f0b585c` / 1657B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/regime.py` | `libs/runtime/regime.py` | `1edc74ae5455` / 2805B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/resilience_state.py` | `libs/runtime/resilience_state.py` | `928d39ea0eb8` / 3582B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/runtime_lifecycle.py` | `libs/runtime/runtime_lifecycle.py` | `c72bcca35a24` / 3566B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/runtime_mode.py` | `libs/runtime/runtime_mode.py` | `a02a16439671` / 4547B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/runtime_output_helpers.py` | `libs/runtime/runtime_output_helpers.py` | `d31c106e4c53` / 2165B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/runtime_ownership.py` | `libs/runtime/runtime_ownership.py` | `49ca20849d35` / 15465B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/runtime_profile.py` | `libs/runtime/runtime_profile.py` | `11b21338856d` / 6509B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/same_symbol_loss_reentry.py` | `libs/runtime/same_symbol_loss_reentry.py` | `ea8ae5d6cf33` / 5652B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner_bias.py` | `libs/runtime/scanner_bias.py` | `d9ab25b1e43a` / 5402B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner_memory_bias.py` | `libs/runtime/scanner_memory_bias.py` | `e2addcd78a5c` / 4802B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner_memory_bias_reasons.py` | `libs/runtime/scanner_memory_bias_reasons.py` | `9043b0183cc7` / 2577B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner_memory_bias_rules.py` | `libs/runtime/scanner_memory_bias_rules.py` | `4cc66a5abef1` / 5176B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/session_entry_dispatch.py` | `libs/runtime/session_entry_dispatch.py` | `e33af6efcf94` / 1184B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/shadow_loop_session.py` | `libs/runtime/shadow_loop_session.py` | `c75111435c24` / 641B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/stage3_horizon_lineage.py` | `libs/runtime/stage3_horizon_lineage.py` | `0e279a73f802` / 14055B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist_explanation.py` | `libs/runtime/strategist_explanation.py` | `823ef5283ff1` / 40326B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/strategist_feedback_trace.py` | `libs/runtime/strategist_feedback_trace.py` | `0e760e7903bc` / 2658B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist_input_quality.py` | `libs/runtime/strategist_input_quality.py` | `2e07b4c02593` / 6553B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist_packet_visibility.py` | `libs/runtime/strategist_packet_visibility.py` | `bc227d3966ee` / 15625B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategy_horizon_feedback.py` | `libs/runtime/strategy_horizon_feedback.py` | `8336d03f41ea` / 42812B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/strategy_memory_support_artifacts.py` | `libs/runtime/strategy_memory_support_artifacts.py` | `608cdc724e2c` / 7808B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategy_memory_window_common.py` | `libs/runtime/strategy_memory_window_common.py` | `0a945c4715af` / 25452B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/strategy_memory_window_sections.py` | `libs/runtime/strategy_memory_window_sections.py` | `b3d99456d0e4` / 19554B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/symbol_memory_packet.py` | `libs/runtime/symbol_memory_packet.py` | `6e437a97881d` / 9466B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/volume_confirmation.py` | `libs/runtime/volume_confirmation.py` | `ca46f23d625a` / 4322B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/weekly_strategy_memory_packet.py` | `libs/runtime/weekly_strategy_memory_packet.py` | `f6f9d446cc9c` / 1297B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/windows_subprocess.py` | `libs/runtime/windows_subprocess.py` | `18fa7c4d4c2d` / 1328B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-027|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
