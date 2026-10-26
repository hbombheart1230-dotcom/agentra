# Agentra P1.5 — CURRENT (2026-10-26 지팀장 A 실행, RF-030 신규 A 코드 작업 배정)

**POLICY_REREAD_REQUIRED:** 최신 실행 지시 변경 anchor `b106384ee151c0db2a1820f2b893d12ee45d1a46` (RF-030 A owner 배정·B RF-001 exact-SHA 최우선); 이전 정책 변경 anchor `fdb4239e655d9dda11643fc4e995cf4269fc58b0`. A/B 모두 **PENDING**. 실행 시작·종료 시 `integration/p1.5` CURRENT **실제 최신 blob SHA**를 조회·전문 재독하고 HANDOFF에 `POLICY_READ_SHA`/`POLICY_APPLIED_OR_DEFERRED`와 실제 실행 증거를 제출한다. B의 D03 `d281c4dd351d606959acd58b83126c3d484bcfe4` 전문 재독 미확인, A는 D03 수신 확인이나 **새 RF-030 지시 미수신**. ACK만으로 완료 처리하지 않는다.

| 담당 | 지금 턴에 실행할 RF와 작업 |
|---|---|
| **A Claude** | **최우선 실제 owner 코드:** [RF-030](../plan/queue/01_PENDING/CLAUDE_A/RF-030.md) `operator_visibility.py`/`operator_period_summary.py`의 구체적 IO·pure 혼합 경계를 확인하고, 독점 16파일 내 최소 의미 있는 코드 FIX 1건 + source SHA + focused normal/-O exit 제출. 이미 분리된 함수 재추출/형식적 diff 금지; 구조상 KEEP가 옳다면 소비자·patchability·IO 반례를 증명하고 **다음 RF 배정 요청**, 같은 KEEP 반복 금지. 이어 [RF-008](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-008.md) `strategist_node.py` 최초 미검증 State/monkeypatch/예외 경계만 독립 peer. RF-028/029 self 증거 반복 금지. |
| **B Codex** | **우선 1:** [RF-001](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-001.md) 최신 integration exact HEAD read-only checkout에서 `tests/test_p153_operator_ui_moved_bodies.py`, `tests/test_operator_ui_data_access_phase2.py`, `tests/test_operator_ui.py` 정상/-O 명령·exit·실제 HEAD SHA 제출(기존 후보 734×2·UI 53×2 반복 금지). **우선 2:** [RF-028](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-028.md) 최초 동적 소비자·IO/State/예외 독립 peer; 이어 [RF-029](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-029.md) `trade_story_pipeline.py`/`read_artifact_selection.py` read-only offline/mock 위험 경계. RF-066 fake `OrderClient`·RF-070 안전한 25 CLI 계속; 위험 32 launcher 실행 금지. B는 D03 `d281c4dd`·최신 CURRENT 재독 후 HANDOFF에 명령·exit·POLICY_READ_SHA 필수. |
| **지팀장** | **RF-030 16 owner BASE/integration/A blob 16/16 동일 확인, A 전담 물리 배정 완료** (move commit `f73d7360`, source code 변경 없음). RF-001 exact SHA 증거 도착 즉시 최종 판정, RF-028/029 신규 B peer 결과 인수·KEEP/INTEGRATE 결정, RF-066/070 미검증 경계 분리. 93 RF 유일 경로 및 STATUS 정합성. |


**큐 우선순위:** REWORK(0) → PEER_REVIEW(11) / LEAD_ACCEPTANCE(2) → DEVELOPING(2) → PENDING(67). **RF-030만** `01_PENDING/CLAUDE_A`로 이동·A 착수 승인; RF-031/071은 UNASSIGNED 유지. A `NO_EXECUTABLE_OWNER` 차단은 RF-030 배정으로 해소(실제 A 착수·코드 SHA는 아직 NOT_RUN).

**연속 실행:** 예약 한도까지 현재 RF를 진행하고 다음 회차에 그대로 이어간다. 동일 SHA·동일 경계 반복 금지. 신규 source SHA·증거와 미완료 지점만 HANDOFF에 기록.

**정본:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) → [D03](D03_DEV_TEAM_RULES.md) → [A 역할](../../../CLAUDE.md) / [B 역할](../../../AGENTS.md) · [D05 큐](D05_RF_PHYSICAL_QUEUE_20261026.md) · [STATUS](../plan/STATUS.md).

**안전:** main·실거래·안전 계약·동결 오라클·예약 무승인 변경 금지. 부분 PASS/BLOCKED/NOT_RUN ≠ DONE.
