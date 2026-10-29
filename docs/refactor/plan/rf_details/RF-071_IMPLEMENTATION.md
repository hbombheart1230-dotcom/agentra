# RF-071 — 코드 구조/함수 재배치 설계 (T08)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-071.md` blob `84cff4ce3ce0aa2a609be486347e0cce4bd08dd9`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 42개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `scripts/start_trading_day.py` | 27248 | `f0193844c36b932900ae07f20c57dd641a831088` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/start_trading_day_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `scripts/__init__.py` → `scripts/__init__.py` | 0 | `e69de29bb2d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/analyze_entry_blockers.py` → `scripts/analyze_entry_blockers.py` | 523 | `3b61253e9916` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/approval_cli.py` → `scripts/approval_cli.py` | 1678 | `c2f0af420300` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/benchmark_operator_visibility_memory.py` → `scripts/benchmark_operator_visibility_memory.py` | 565 | `f4d6cfd5d46c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/clean_evaluation_test_contamination.py` → `scripts/clean_evaluation_test_contamination.py` | 562 | `15f92063eb6e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/cleanup_pytest_artifacts.cmd` → `scripts/cleanup_pytest_artifacts.cmd` | 170 | `a9dcadcb34cb` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `scripts/cleanup_pytest_artifacts.ps1` → `scripts/cleanup_pytest_artifacts.ps1` | 875 | `3e82529a6e31` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `scripts/cleanup_pytest_artifacts.py` → `scripts/cleanup_pytest_artifacts.py` | 1112 | `f39e5e63d8b1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/compact_q9_decision_windows.py` → `scripts/compact_q9_decision_windows.py` | 538 | `5f10ffe4ef54` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/daily_profitability_scorecard.py` → `scripts/daily_profitability_scorecard.py` | 535 | `6eabe97be9aa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/demo_m14_mock_order.py` → `scripts/demo_m14_mock_order.py` | 4936 | `9ff62b5cb34e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/demo_m14_order_status.py` → `scripts/demo_m14_order_status.py` | 7062 | `e0b5a24f3b18` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/demo_m14_quote_then_order.py` → `scripts/demo_m14_quote_then_order.py` | 6623 | `c062b4440301` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/demo_m15_smoke.py` → `scripts/demo_m15_smoke.py` | 6839 | `dcb31f6f0f25` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/demo_m22_graph_with_hydration.py` → `scripts/demo_m22_graph_with_hydration.py` | 469 | `43643fb0f130` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/demo_m22_skill_flow.py` → `scripts/demo_m22_skill_flow.py` | 449 | `9280c778d9f9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/demo_m22_skill_hydration.py` → `scripts/demo_m22_skill_hydration.py` | 4343 | `764ba5110175` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/demo_m7_dry_run_pipeline.py` → `scripts/demo_m7_dry_run_pipeline.py` | 459 | `e8e282edeefa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/organize_llm_reports.py` → `scripts/organize_llm_reports.py` | 517 | `4e8d778dbf62` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/query_commander_resilience_events.py` → `scripts/query_commander_resilience_events.py` | 556 | `5c051bbc7157` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/query_intent_state_store.py` → `scripts/query_intent_state_store.py` | 529 | `19504d04f742` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/query_m25_notification_events.py` → `scripts/query_m25_notification_events.py` | 544 | `07312f07191d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/query_strategist_llm_events.py` → `scripts/query_strategist_llm_events.py` | 538 | `b091f3093aa4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/query_trade_reason_chain.py` → `scripts/query_trade_reason_chain.py` | 529 | `f67c4d04f57a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/reconcile_intent_state_store.py` → `scripts/reconcile_intent_state_store.py` | 541 | `acd1c041b10f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/reconstruct_incident_timeline.py` → `scripts/reconstruct_incident_timeline.py` | 544 | `ab1ad01d8388` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/repair_q9_day_artifacts.py` → `scripts/repair_q9_day_artifacts.py` | 526 | `f9955f1d08ff` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/repair_trade_symbol_context.py` → `scripts/repair_trade_symbol_context.py` | 538 | `3a624947dbda` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/restart_live_session.bat` → `scripts/restart_live_session.bat` | 195 | `ecfb868970ae` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `scripts/restart_live_session.ps1` → `scripts/restart_live_session.ps1` | 283 | `9c59fda945c6` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `scripts/restart_live_session.py` → `scripts/restart_live_session.py` | 12229 | `f9a69bbdf4c3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/smoke_m20_llm.py` → `scripts/smoke_m20_llm.py` | 496 | `7da80d8fa6ee` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/smoke_m22_hydration.py` → `scripts/smoke_m22_hydration.py` | 514 | `21aa3662d053` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/start_operator_ui.ps1` → `scripts/start_operator_ui.ps1` | 2118 | `f8dbf2ac62b1` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `scripts/start_q12_preopen.ps1` → `scripts/start_q12_preopen.ps1` | 1121 | `3da9c03646b8` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `scripts/start_trading_day.py` → `scripts/start_trading_day.py` | 27248 | `f0193844c36b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/step5d_crash_reconciliation.py` → `scripts/step5d_crash_reconciliation.py` | 538 | `458f603da89b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/stop_operator_ui.ps1` → `scripts/stop_operator_ui.ps1` | 746 | `4f6e4033237f` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `scripts/sync_legacy_brief_llm.py` → `scripts/sync_legacy_brief_llm.py` | 520 | `cf7478d01c4a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/sync_openrouter_model_catalog.py` → `scripts/sync_openrouter_model_catalog.py` | 544 | `06c7f1b08dbe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/unregister_mock_exam_tasks_example.bat` → `scripts/unregister_mock_exam_tasks_example.bat` | 435 | `5c7b1f692951` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `scripts/verify_uef_freeze_manifest.py` → `scripts/verify_uef_freeze_manifest.py` | 2990 | `7b82e084ae0e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
