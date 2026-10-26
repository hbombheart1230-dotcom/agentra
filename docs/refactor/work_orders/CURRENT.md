# Agentra P1.5 — CURRENT (이번 턴)

| 담당 | 지금 턴에 할 일 |
|---|---|
| **A Claude** | **새 A 소유 미완료 RF 착수.** RF-029는 38 owner KEEP/FIX0 제출 완료이므로 재검증·재보고 금지. 지팀장이 물리 큐에서 소유권과 비동결 조건을 확인해 다음 번호를 배정한다. |
| **B Codex** | **새 B 소유 미완료 RF 착수.** RF-070의 85 scoped PASS·57 정적 분류, RF-066의 17 AST·정적 peer·7 표적 PASS를 재실행하지 않는다. 이 두 RF의 미충족 인수조건은 지팀장이 판정하고, 새 재현 결함이나 특정 최초 미검증 경계가 있을 때만 별도 지시한다. |
| **지팀장** | **RF-029 KEEP/FIX0 인수 판정·peer 이동 여부 결정. RF-070/066 기존 증거로 KEEP/HOLD/peer 판정. RF-001 통합 SHA 검증 및 RF-028 B 최초 peer의 남은 게이트 관리.** A/B 다음 소유 RF를 물리 큐에서 실제 번호까지 확정·배정하고 큐/STATUS를 동기화한다. |

**예약 운영:** 매 회차 하던 일을 이어간다. 1시간 안에 모든 작업을 끝낼 필요 없다. 동일 SHA·동일 범위 검증 반복 금지. 새 재현 결함이 없으면 이미 제출한 KEEP/FIX0을 개발자에게 재배정하지 않는다.

**정본:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [D03](D03_DEV_TEAM_RULES.md) · [A 역할](../../../CLAUDE.md) · [B 역할](../../../AGENTS.md) · [RF 큐 D05](D05_RF_PHYSICAL_QUEUE_20261026.md) · [STATUS](../plan/STATUS.md) · [A HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md) · [B HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md).

**안전:** main·실거래·안전 계약·동결 오라클·예약 무승인 변경 금지. 부분 PASS·BLOCKED·NOT_RUN은 DONE이 아니다. GitHub 쓰기 실패 시 원인별 허용된 방법으로 재시도하고 원격 SHA를 확인한다.
