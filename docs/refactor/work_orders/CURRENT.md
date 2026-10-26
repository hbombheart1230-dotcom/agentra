# Agentra P1.5 — CURRENT (2026-10-26 B 실행)

**POLICY_REREAD_REQUIRED:** CURRENT 실행 지시 변경 anchor commit `fdb4239e655d9dda11643fc4e995cf4269fc58b0` / 이전 blob `7733998c19d95f505a3ebf0683be8c1701c9fde2`; A/B 모두 **PENDING**. 실행 시작·종료 시 `integration/p1.5` CURRENT **최신 blob SHA**를 직접 조회·전문 재독하고 HANDOFF에 `POLICY_READ_SHA`/`POLICY_APPLIED_OR_DEFERRED`를 제출한다. B는 D03 `d281c4dd351d606959acd58b83126c3d484bcfe4` 전문 재독 미확인, A는 이전 HANDOFF에서 D03 수신 확인. 지팀장은 실제 peer·owner 작업 없이는 ACK만으로 수신 완료 처리하지 않는다.

| 담당 | 지금 턴에 실행할 RF와 작업 |
|---|---|
| **A Claude** | PEER_REVIEW/CLAUDE_A RF-008 `graphs/nodes/strategist_node.py` 1 owner 최초 독립 State patch/monkeypatch/예외 소비자 offline/mock normal/-O peer(명령·exit·SHA). 이어 RF-007/063/065/067은 최초 미검증 경계만. RF-029 증거 반복 금지. |
| **B Codex** | PEER_REVIEW/CODEX_B [RF-028](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-028.md) 최초 미검증 동적 소비자·IO/State·예외 경계 peer → [RF-029](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-029.md) `trade_story_pipeline.py`/`trade_read_model_parts/read_artifact_selection.py` 입력·예외·부작용 최초 read-only offline/mock normal/-O peer. RF-018 잔여 계약은 새 경계만. [RF-001](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-001.md): 최신 integration HEAD read-only 격리에서 `tests/test_p153_operator_ui_moved_bodies.py`, `tests/test_operator_ui_data_access_phase2.py`, `tests/test_operator_ui.py` normal/-O, 정확 SHA·exit 제출(기존 격리 734×2, UI 53×2 반복 금지). 이어 RF-070 미검증 안전한 25 consumer/CLI 경계만 진행, 32 SAFETY_HOLD 실행 금지. |
| **지팀장** | RF-029 KEEP_NOOP_CANDIDATE→PEER 판정·큐 이동, RF-028/018 peer 결과 인수, RF-001 exact-SHA 검증 결과 최종 판정, RF-066/070 KEEP/HOLD 및 남은 게이트 결정. 물리 큐와 STATUS 정합화. |


**큐 우선순위:** REWORK(0) → PEER_REVIEW(11) / LEAD_ACCEPTANCE(2) → DEVELOPING(2) → PENDING(67). RF-030/031/071은 01_PENDING/UNASSIGNED 유지, 신규 착수 지시 철회.

**연속 실행:** 예약 한도까지 현재 RF를 진행하고 다음 회차에 그대로 이어간다. 동일 SHA·동일 경계 반복 금지. 신규 source SHA·증거와 미완료 지점만 HANDOFF에 기록.

**정본:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) → [D03](D03_DEV_TEAM_RULES.md) → [A 역할](../../../CLAUDE.md) / [B 역할](../../../AGENTS.md) · [D05 큐](D05_RF_PHYSICAL_QUEUE_20261026.md) · [STATUS](../plan/STATUS.md).

**안전:** main·실거래·안전 계약·동결 오라클·예약 무승인 변경 금지. 부분 PASS/BLOCKED/NOT_RUN ≠ DONE.
