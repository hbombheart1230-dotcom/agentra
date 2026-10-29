# RF-012 — 코드 구조/함수 재배치 설계 (T07)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-012.md` blob `38c80304098229e3c136a72c7d729ab6edfca5ad`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 37개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `graphs/nodes/execute_from_packet.py` | 183181 | `1a10af59e5e9b4035f1c7403e5aeb814f65c8e3a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `graphs/nodes/execute_from_packet_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `graphs/nodes/decide_trade.py` | 65080 | `6fa69e96f7870ad8615f8b4f6ea8b4c65955dd78` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `graphs/nodes/decide_trade_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `graphs/nodes/update_state_after_execution.py` | 59649 | `100952d946fe4b38da627266a17885a90f212419` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `graphs/nodes/update_state_after_execution_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `graphs/nodes/build_portfolio_snapshot.py` | 21537 | `d6afacc15ef3cd9843ef56e28cb84d6237e7d771` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `graphs/nodes/build_portfolio_snapshot_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `graphs/nodes/assemble_decision_packet.py` → `graphs/nodes/assemble_decision_packet.py` | 2738 | `dbcae63ac548` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/build_decision_context.py` → `graphs/nodes/build_decision_context.py` | 19640 | `d5e6362add5f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/build_execution_readiness.py` → `graphs/nodes/build_execution_readiness.py` | 8049 | `a17d56a521b0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/build_market_snapshot.py` → `graphs/nodes/build_market_snapshot.py` | 4127 | `af11f9d64d6f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/build_open_order_snapshot.py` → `graphs/nodes/build_open_order_snapshot.py` | 2303 | `995c2931b439` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/build_portfolio_snapshot.py` → `graphs/nodes/build_portfolio_snapshot.py` | 21537 | `d6afacc15ef3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/build_risk_context.py` → `graphs/nodes/build_risk_context.py` | 1532 | `c3e466816184` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/build_snapshots.py` → `graphs/nodes/build_snapshots.py` | 802 | `a0e20a2084b8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/decide_trade.py` → `graphs/nodes/decide_trade.py` | 65080 | `6fa69e96f787` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/decision_node.py` → `graphs/nodes/decision_node.py` | 8203 | `172f5ac1243c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/ensure_token.py` → `graphs/nodes/ensure_token.py` | 786 | `d20d8b2ff32c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/execute_from_packet.py` → `graphs/nodes/execute_from_packet.py` | 183181 | `1a10af59e5e9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/execute_order.py` → `graphs/nodes/execute_order.py` | 6641 | `1e23bc4d3461` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/executor_node.py` → `graphs/nodes/executor_node.py` | 381 | `832c6a30e43b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/hydrate_skill_results_node.py` → `graphs/nodes/hydrate_skill_results_node.py` | 11820 | `a23a588a3e8f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/load_state.py` → `graphs/nodes/load_state.py` | 412 | `ceb1fb61542a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/log_decision_trace.py` → `graphs/nodes/log_decision_trace.py` | 1709 | `d74e0605fe92` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/plan_api.py` → `graphs/nodes/plan_api.py` | 572 | `c73adc21da72` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/portfolio_guard_node.py` → `graphs/nodes/portfolio_guard_node.py` | 4608 | `7ec264a1a52a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/prepare_api_call.py` → `graphs/nodes/prepare_api_call.py` | 1608 | `1529fa5897a5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/prepare_order_dry_run.py` → `graphs/nodes/prepare_order_dry_run.py` | 1995 | `75741376e535` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/read_account_balance.py` → `graphs/nodes/read_account_balance.py` | 1032 | `867bd3c1bb38` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/reporter_node.py` → `graphs/nodes/reporter_node.py` | 1501 | `214758d222cd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/risk_cash_truth.py` → `graphs/nodes/risk_cash_truth.py` | 2914 | `bc3bd5ea679e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/save_state.py` → `graphs/nodes/save_state.py` | 398 | `17d867a0de46` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/skill_contracts.py` → `graphs/nodes/skill_contracts.py` | 14604 | `bf0e50987cd6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/nodes/update_state_after_execution.py` → `graphs/nodes/update_state_after_execution.py` | 59649 | `100952d946fe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/eod_report.py` → `graphs/pipelines/eod_report.py` | 533 | `72ce931dc964` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/live_cycle.py` → `graphs/pipelines/live_cycle.py` | 638 | `6fdd06135875` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/m10_live_pipeline.py` → `graphs/pipelines/m10_live_pipeline.py` | 1403 | `f220b5769e71` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/m11_2_live_pipeline.py` → `graphs/pipelines/m11_2_live_pipeline.py` | 1175 | `41766fe275b2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/m11_live_pipeline.py` → `graphs/pipelines/m11_live_pipeline.py` | 1056 | `784b4a44a849` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/m13_eod_report.py` → `graphs/pipelines/m13_eod_report.py` | 4849 | `632214d0eab2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/m13_live_loop.py` → `graphs/pipelines/m13_live_loop.py` | 8571 | `72eb87ffd808` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/m13_tick.py` → `graphs/pipelines/m13_tick.py` | 2140 | `944e61a860f2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/offhours_validation.py` → `graphs/pipelines/offhours_validation.py` | 9295 | `9a5c7576f93c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `graphs/pipelines/runtime_tick.py` → `graphs/pipelines/runtime_tick.py` | 508 | `184a43571dbd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
