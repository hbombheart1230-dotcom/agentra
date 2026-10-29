# RF-021 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-021.md` blob `351b7cc66fdc823189a38da6a882b0a6f3567d9b`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 32개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/runtime/monitor_exit/__init__.py` → `libs/runtime/monitor_exit/__init__.py` | 169 | `262a76c27d51` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/account_pnl_crosscheck.py` → `libs/runtime/monitor_exit/account_pnl_crosscheck.py` | 8369 | `2819e7cf9615` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/adapters/__init__.py` → `libs/runtime/monitor_exit/adapters/__init__.py` | 36 | `3ce55a69ae63` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/adapters/state_data.py` → `libs/runtime/monitor_exit/adapters/state_data.py` | 2132 | `629f5725740b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/exit_cycle_guards.py` → `libs/runtime/monitor_exit/exit_cycle_guards.py` | 9068 | `223c02d918cd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/exit_policy_bias.py` → `libs/runtime/monitor_exit/exit_policy_bias.py` | 3405 | `dea68b985516` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/exit_policy_chart_projection.py` → `libs/runtime/monitor_exit/exit_policy_chart_projection.py` | 14209 | `e7f5c2b41284` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/exit_policy_pnl_projection.py` → `libs/runtime/monitor_exit/exit_policy_pnl_projection.py` | 13354 | `c0f4d8661bcd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/exit_policy_trigger_inputs.py` → `libs/runtime/monitor_exit/exit_policy_trigger_inputs.py` | 7103 | `a8d485e831a9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/exit_profit_ladder.py` → `libs/runtime/monitor_exit/exit_profit_ladder.py` | 12798 | `7f21f3f2ea87` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/exit_trigger_ladder.py` → `libs/runtime/monitor_exit/exit_trigger_ladder.py` | 10317 | `8fd563655265` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/hold_controls.py` → `libs/runtime/monitor_exit/hold_controls.py` | 4444 | `5b30396608c5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/market_enrichment.py` → `libs/runtime/monitor_exit/market_enrichment.py` | 7375 | `2356c4bb3ddf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/numeric.py` → `libs/runtime/monitor_exit/numeric.py` | 208 | `8d70ca32605c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/observability.py` → `libs/runtime/monitor_exit/observability.py` | 219 | `38915f527ae9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/order_lifecycle.py` → `libs/runtime/monitor_exit/order_lifecycle.py` | 223 | `2a4653be257a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/overnight_carry.py` → `libs/runtime/monitor_exit/overnight_carry.py` | 14203 | `8bc8b9e12738` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/policy_config.py` → `libs/runtime/monitor_exit/policy_config.py` | 10170 | `b5cde7052d91` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/policy_map_builder.py` → `libs/runtime/monitor_exit/policy_map_builder.py` | 1594 | `a94cf82b88a1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/position_risk.py` → `libs/runtime/monitor_exit/position_risk.py` | 1885 | `e497a55b5442` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/position_state_enrichment.py` → `libs/runtime/monitor_exit/position_state_enrichment.py` | 2922 | `0a21686cd3f7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/position_tracking.py` → `libs/runtime/monitor_exit/position_tracking.py` | 5463 | `18f781849b6e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/post_exit_shadow.py` → `libs/runtime/monitor_exit/post_exit_shadow.py` | 4955 | `f538960155b3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/preview.py` → `libs/runtime/monitor_exit/preview.py` | 10985 | `8dd251be805a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/price_resolution.py` → `libs/runtime/monitor_exit/price_resolution.py` | 5520 | `f130d2dcc54d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/reasons.py` → `libs/runtime/monitor_exit/reasons.py` | 2511 | `a8735b6b5b74` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/runtime_clock.py` → `libs/runtime/monitor_exit/runtime_clock.py` | 4820 | `aec71bda5fef` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/selected_snapshot.py` → `libs/runtime/monitor_exit/selected_snapshot.py` | 4401 | `70d2bdbbc1fd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/selection.py` → `libs/runtime/monitor_exit/selection.py` | 2884 | `54f3e145d24d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/session_vwap.py` → `libs/runtime/monitor_exit/session_vwap.py` | 3194 | `0372ee9feec0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/vwap_confirmation.py` → `libs/runtime/monitor_exit/vwap_confirmation.py` | 2537 | `784c8a084bfe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/monitor_exit/vwap_state_adapter.py` → `libs/runtime/monitor_exit/vwap_state_adapter.py` | 1109 | `ca98740cfac9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
