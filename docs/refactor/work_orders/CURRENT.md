# Agentra P1.5 — CURRENT 작업 큐

> 정본: `integration/p1.5`. [D00 안전·권한](../../ENGINEERING_DELIVERY_POLICY.md) · [D03 실행·검증](D03_DEV_TEAM_RULES.md) · [D01 B](../../../AGENTS.md) · [D02 A](../../../CLAUDE.md) · [STATUS](../plan/STATUS.md)

| 담당 | 지금 실행할 작업 | 다음 작업·해제 조건 |
|---|---|---|
| Claude A ([HANDOFF_A](HANDOFF_A.md)) | [RF-019](../plan/pending/RF-019.md) 잔여 21 owner 소비자/State/효과 검토(기존 PASS 반복 금지); B 신규 코드 SHA만 peer | [RF-017](../plan/pending/RF-017.md); B [RF-001](../plan/verification/codex/RF-001.md) 수정 SHA 도착 시 우선 peer |
| Codex B ([HANDOFF_B](HANDOFF_B.md)) | [RF-019](../plan/pending/RF-019.md) A의 신규 owner/consumer 증거 read-only peer; [RF-070](../plan/pending/RF-070.md) 잔여 25개 기타 구현 read-only 소비자·효과 경계 정리 | [RF-001](../plan/verification/codex/RF-001.md) 신규 owner-local 결함 SHA 도착 시만 재개; 32개 위험 launcher 실행 금지 |
| 지팀장 | 신규 SHA·peer 판정, [RF-001](../plan/verification/codex/RF-001.md) KEEP 복귀 후 남은 전체 인수조건·교차 RF 차단 판정, [RF-013](../plan/verification/claude/RF-013.md) 소유권 HOLD 유지 | 인수조건 충족 RF만 선별 통합 및 통합 SHA normal/-O 검증 |

**기록 위치:** RF = 개별 결정·실패·검증·차단·재개 조건. HANDOFF_A/B = 이번 실행의 신규 코드 SHA·명령·결과. STATUS = RF 집계. CURRENT = 담당·우선순위·링크만. 기존 증거는 재사용한다.

**런검증:** [별도 CURRENT](../../runtime/validation/CURRENT.md) · [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) · [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). 코드 수정·RF 판정·통합 권한 없음.
