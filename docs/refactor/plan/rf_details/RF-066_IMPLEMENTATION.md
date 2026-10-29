# RF-066 — 코드 구조/함수 재배치 설계 (T08)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-066.md` blob `e8992be97751010679f33b599921f536c7d71f29`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 30개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `scripts/examples/__init__.py` → `scripts/examples/__init__.py` | 75 | `833c826d069a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/examples/demo_m22_graph_with_hydration.py` → `scripts/examples/demo_m22_graph_with_hydration.py` | 4228 | `4c544d49f4b3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/examples/demo_m22_skill_flow.py` → `scripts/examples/demo_m22_skill_flow.py` | 4941 | `c5510e781364` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/examples/demo_m7_dry_run_pipeline.py` → `scripts/examples/demo_m7_dry_run_pipeline.py` | 3108 | `cf0e6e3929e7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/__init__.py` → `scripts/maintenance/__init__.py` | 80 | `8b3797d86d1b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/clean_evaluation_test_contamination.py` → `scripts/maintenance/clean_evaluation_test_contamination.py` | 6706 | `3bd1c8bec10f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/compact_q9_decision_windows.py` → `scripts/maintenance/compact_q9_decision_windows.py` | 3588 | `e6d675039516` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/organize_llm_reports.py` → `scripts/maintenance/organize_llm_reports.py` | 1485 | `280cdbf991f0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/reconcile_intent_state_store.py` → `scripts/maintenance/reconcile_intent_state_store.py` | 8740 | `17fed37f03f7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/repair_q9_day_artifacts.py` → `scripts/maintenance/repair_q9_day_artifacts.py` | 760 | `d95a0cce870c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/repair_trade_symbol_context.py` → `scripts/maintenance/repair_trade_symbol_context.py` | 907 | `a1cec15948b2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/run_broker_trade_reconciliation.py` → `scripts/maintenance/run_broker_trade_reconciliation.py` | 4274 | `4351b9fe03d3` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/maintenance/run_log_maintenance.py` → `scripts/maintenance/run_log_maintenance.py` | 2981 | `75dfb1b5f2bb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/maintenance/run_report_maintenance.py` → `scripts/maintenance/run_report_maintenance.py` | 4169 | `4263595565f9` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/maintenance/step5d_crash_reconciliation.py` → `scripts/maintenance/step5d_crash_reconciliation.py` | 10820 | `0b2cac5dc97b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/sync_legacy_brief_llm.py` → `scripts/maintenance/sync_legacy_brief_llm.py` | 2219 | `187276a645fd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/maintenance/sync_openrouter_model_catalog.py` → `scripts/maintenance/sync_openrouter_model_catalog.py` | 1146 | `5ae494a79390` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `tests/test_p15_run_log_maintenance_temp_cli.py` → `tests/test_p15_run_log_maintenance_temp_cli.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_sync_legacy_brief_no_write_cli.py` → `tests/test_p15_sync_legacy_brief_no_write_cli.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_log_maintenance_temp_effects.py` → `tests/test_rf066_log_maintenance_temp_effects.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_m22_fake_graph_consumer.py` → `tests/test_rf066_m22_fake_graph_consumer.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_m22_graph_offline_policy.py` → `tests/test_rf066_m22_graph_offline_policy.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_m22_graph_temp_cwd_effects.py` → `tests/test_rf066_m22_graph_temp_cwd_effects.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_m22_skill_demo_timeout_consumer.py` → `tests/test_rf066_m22_skill_demo_timeout_consumer.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_m7_fake_order_client_consumer.py` → `tests/test_rf066_m7_fake_order_client_consumer.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_owner_c1_inventory.py` → `tests/test_rf066_owner_c1_inventory.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_q9_compaction_exception.py` → `tests/test_rf066_q9_compaction_exception.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_report_maintenance_temp_effects.py` → `tests/test_rf066_report_maintenance_temp_effects.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_sync_legacy_brief_llm_cli.py` → `tests/test_rf066_sync_legacy_brief_llm_cli.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf066_temp_contamination_cleanup.py` → `tests/test_rf066_temp_contamination_cleanup.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
