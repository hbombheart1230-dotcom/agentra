# Agentra P1.5 — CURRENT (지팀장 배정, 이번 턴)

| 담당 | 지금 턴에 실행할 RF와 작업 |
|---|---|
| **A Claude** | PEER_REVIEW/CLAUDE_A RF-007/008/063/065/067: 기존 증거로 종결 가능한 범위 우선, 새 source SHA 또는 최초 미검증 격리 조합만 read-only peer. RF-029 증거 반복 금지. |
| **B Codex** | PEER_REVIEW/CODEX_B RF-028의 최초 미검증 동적 소비자·IO/State·예외 경계, RF-018 잔여 계약 peer. LEAD_ACCEPTANCE RF-001 최신 integration exact-SHA normal/-O 검증. |
| **지팀장** | RF-029 KEEP/FIX0 인수 판정, RF-028/018 peer 결과 인수, RF-001 exact-SHA 검증 결과 최종 판정, RF-066/070 KEEP/HOLD 및 남은 게이트 결정. 물리 큐와 STATUS 정합화. |


**큐 우선순위:** REWORK(0) → PEER_REVIEW(10) / LEAD_ACCEPTANCE(2) → DEVELOPING(2) → PENDING(68). RF-030/031/071은 01_PENDING/UNASSIGNED 유지, 신규 착수 지시 철회.

**연속 실행:** 예약 한도까지 현재 RF를 진행하고 다음 회차에 그대로 이어간다. 동일 SHA·동일 경계 반복 금지. 신규 source SHA·증거와 미완료 지점만 HANDOFF에 기록.

**정본:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) → [D03](D03_DEV_TEAM_RULES.md) → [A 역할](../../../CLAUDE.md) / [B 역할](../../../AGENTS.md) · [D05 큐](D05_RF_PHYSICAL_QUEUE_20261026.md) · [STATUS](../plan/STATUS.md).

**안전:** main·실거래·안전 계약·동결 오라클·예약 무승인 변경 금지. 부분 PASS/BLOCKED/NOT_RUN ≠ DONE.
