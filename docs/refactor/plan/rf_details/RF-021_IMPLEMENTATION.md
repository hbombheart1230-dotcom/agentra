# RF-021 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-021.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 32개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/monitor_exit/exit_policy_chart_projection.py` blob `e7f5c2b412848493ea77761697853a71a61c2c9d` (273 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/monitor_exit/exit_policy_chart_projection.py::exit_chart_out` L12-273 | MOVE_BODY | `libs/runtime/monitor_exit/exit_policy_chart_projection_exit_chart_out.py::exit_chart_out` | 262행 · 순수 후보 |

### exit_chart_out — 원본 262행
- **확인된 책임:** `libs/runtime/monitor_exit/exit_policy_chart_projection.py` L12–273; 직접 호출 helper `_clamp_non_negative`, `_to_float`, `_to_float_list`, `_to_bool`. 감지된 효과: 없음.
- **목표:** `libs/runtime/monitor_exit/exit_policy_chart_projection_exit_chart_out.py::exit_chart_out` (Owner Claude A, RF-021). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/monitor_exit/__init__.py` | `libs/runtime/monitor_exit/__init__.py` | `262a76c27d51` / 169B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/account_pnl_crosscheck.py` | `libs/runtime/monitor_exit/account_pnl_crosscheck.py` | `2819e7cf9615` / 8369B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/adapters/__init__.py` | `libs/runtime/monitor_exit/adapters/__init__.py` | `3ce55a69ae63` / 36B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/adapters/state_data.py` | `libs/runtime/monitor_exit/adapters/state_data.py` | `629f5725740b` / 2132B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/exit_cycle_guards.py` | `libs/runtime/monitor_exit/exit_cycle_guards.py` | `223c02d918cd` / 9068B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/exit_policy_bias.py` | `libs/runtime/monitor_exit/exit_policy_bias.py` | `dea68b985516` / 3405B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/exit_policy_chart_projection.py` | `libs/runtime/monitor_exit/exit_policy_chart_projection.py` | `e7f5c2b41284` / 14209B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/monitor_exit/exit_policy_pnl_projection.py` | `libs/runtime/monitor_exit/exit_policy_pnl_projection.py` | `c0f4d8661bcd` / 13354B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/exit_policy_trigger_inputs.py` | `libs/runtime/monitor_exit/exit_policy_trigger_inputs.py` | `a8d485e831a9` / 7103B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/exit_profit_ladder.py` | `libs/runtime/monitor_exit/exit_profit_ladder.py` | `7f21f3f2ea87` / 12798B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/exit_trigger_ladder.py` | `libs/runtime/monitor_exit/exit_trigger_ladder.py` | `8fd563655265` / 10317B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/hold_controls.py` | `libs/runtime/monitor_exit/hold_controls.py` | `5b30396608c5` / 4444B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/market_enrichment.py` | `libs/runtime/monitor_exit/market_enrichment.py` | `2356c4bb3ddf` / 7375B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/numeric.py` | `libs/runtime/monitor_exit/numeric.py` | `8d70ca32605c` / 208B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/observability.py` | `libs/runtime/monitor_exit/observability.py` | `38915f527ae9` / 219B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/order_lifecycle.py` | `libs/runtime/monitor_exit/order_lifecycle.py` | `2a4653be257a` / 223B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/overnight_carry.py` | `libs/runtime/monitor_exit/overnight_carry.py` | `8bc8b9e12738` / 14203B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/policy_config.py` | `libs/runtime/monitor_exit/policy_config.py` | `b5cde7052d91` / 10170B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/policy_map_builder.py` | `libs/runtime/monitor_exit/policy_map_builder.py` | `a94cf82b88a1` / 1594B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/position_risk.py` | `libs/runtime/monitor_exit/position_risk.py` | `e497a55b5442` / 1885B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/position_state_enrichment.py` | `libs/runtime/monitor_exit/position_state_enrichment.py` | `0a21686cd3f7` / 2922B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/position_tracking.py` | `libs/runtime/monitor_exit/position_tracking.py` | `18f781849b6e` / 5463B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/post_exit_shadow.py` | `libs/runtime/monitor_exit/post_exit_shadow.py` | `f538960155b3` / 4955B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/preview.py` | `libs/runtime/monitor_exit/preview.py` | `8dd251be805a` / 10985B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/price_resolution.py` | `libs/runtime/monitor_exit/price_resolution.py` | `f130d2dcc54d` / 5520B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/reasons.py` | `libs/runtime/monitor_exit/reasons.py` | `a8735b6b5b74` / 2511B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/runtime_clock.py` | `libs/runtime/monitor_exit/runtime_clock.py` | `aec71bda5fef` / 4820B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/selected_snapshot.py` | `libs/runtime/monitor_exit/selected_snapshot.py` | `70d2bdbbc1fd` / 4401B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/selection.py` | `libs/runtime/monitor_exit/selection.py` | `54f3e145d24d` / 2884B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/session_vwap.py` | `libs/runtime/monitor_exit/session_vwap.py` | `0372ee9feec0` / 3194B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/vwap_confirmation.py` | `libs/runtime/monitor_exit/vwap_confirmation.py` | `784c8a084bfe` / 2537B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_exit/vwap_state_adapter.py` | `libs/runtime/monitor_exit/vwap_state_adapter.py` | `ca98740cfac9` / 1109B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-021|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
