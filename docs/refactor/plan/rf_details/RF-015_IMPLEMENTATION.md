# RF-015 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Claude A 구현, Codex B 읽기 전용 독립 검증. 파일 19개. 원본 RF `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**실제 함수 분석 대상 없음:** Python 원본이 없거나 원격 본문 조회가 안 됨. 추측 함수명을 새 코드로 구현하지 않는다. 모든 소유 파일의 위치/책임·공개 소비자가 적절하면 KEEP_OK. 구조 부채 확인 시 실제 Git blob 함수명을 지정하고 그 함수만 분리.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `libs/agents/monitor/events/cycle_event_payloads.py` | `libs/agents/monitor/events/cycle_event_payloads.py` | 7613B `633f9afbb422` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/events/cycle_log_trace_payloads.py` | `libs/agents/monitor/events/cycle_log_trace_payloads.py` | 13508B `51fa078349e0` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/cycle_detail_projection.py` | `libs/agents/monitor/projections/cycle_detail_projection.py` | 13136B `9630c66ffd9b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/cycle_detail_projection_exit_decision_detail.py` | `libs/agents/monitor/projections/cycle_detail_projection_exit_decision_detail.py` | 20528B `fe67e0012d72` | 큰 Python 함수 추가 실사: 서로 다른 실제 책임 확인 후 이름 붙여 분리 |
| `libs/agents/monitor/projections/cycle_output_projection.py` | `libs/agents/monitor/projections/cycle_output_projection.py` | 19939B `26db1a162a9e` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/cycle_output_projection_value_state_monitor.py` | `libs/agents/monitor/projections/cycle_output_projection_value_state_monitor.py` | 2402B `97831983e7d5` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/cycle_posture_projection.py` | `libs/agents/monitor/projections/cycle_posture_projection.py` | 19039B `2ed727fb946b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/entry_evidence.py` | `libs/agents/monitor/projections/entry_evidence.py` | 2816B `fa5a9a66e799` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/entry_focus_output_projection.py` | `libs/agents/monitor/projections/entry_focus_output_projection.py` | 1921B `21326cb26e59` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/entry_state_views.py` | `libs/agents/monitor/projections/entry_state_views.py` | 6581B `61e3f2c2ec77` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/exit_axis_labels.py` | `libs/agents/monitor/projections/exit_axis_labels.py` | 3063B `d640b83ad49e` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/feature_context_views.py` | `libs/agents/monitor/projections/feature_context_views.py` | 3942B `77c79d96af93` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/observability.py` | `libs/agents/monitor/projections/observability.py` | 20893B `66fdfb39f5b2` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `libs/agents/monitor/projections/order_lifecycle.py` | `libs/agents/monitor/projections/order_lifecycle.py` | 2574B `e87b0c2c8044` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/policy_output_projection.py` | `libs/agents/monitor/projections/policy_output_projection.py` | 10817B `fe6c9ebf5668` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/policy_trace_views.py` | `libs/agents/monitor/projections/policy_trace_views.py` | 19952B `95e3e8c2070b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/scanner_monitor_handoff_projection.py` | `libs/agents/monitor/projections/scanner_monitor_handoff_projection.py` | 1478B `d7c3f8afd63f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/signal_evidence_defaults.py` | `libs/agents/monitor/projections/signal_evidence_defaults.py` | 5266B `d53de4e425e0` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/monitor/projections/signal_explanation.py` | `libs/agents/monitor/projections/signal_explanation.py` | 5733B `be74bc5f7ea6` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |

## 3. 개발자 독점 순서와 최소 검증

1. Claude A만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 A 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-015|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
