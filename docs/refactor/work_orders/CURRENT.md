# Agentra P1.5 — CURRENT (배정 포인터)

> 정본 `integration/p1.5`. 실행 규칙은 [D03](D03_DEV_TEAM_RULES.md), 안전은 [D00](../../ENGINEERING_DELIVERY_POLICY.md), 역할은 [D01 Codex](../../../AGENTS.md)·[D02 Claude](../../../CLAUDE.md). **한 회차 1→2→3 전부 순회**, 변경된 RF 증거만 처리.

- **규칙 변경 알림 — A/B 다음 실행 시 1회 재독:** D01 `81daa098 → 28779e2b`, D02 `c6a5cf3c → e5ecd133`, D03 `8ee3e385 → b99533ca`: 중복 규칙을 D03으로 통합하고 D01/D02는 역할 포인터로 축소; 기존 안전·검증·통합 게이트 유지, 새 증거가 있으면 빠르게 peer로 전환. **A는 D02·D03, B는 D01·D03을 재독하고 HANDOFF에 확인 기록**. D00 `442247ea` 불변이므로 재독 불필요. 지팀장은 확인 뒤 이 알림을 제거한다.
- **Claude A / 1 REWORK:** 없음.
- **Claude A / 2 독립 검증:** [067](../plan/verification/codex/RF-067.md) · [066](../plan/verification/codex/RF-066.md) · [063](../plan/verification/codex/RF-063.md) · [065](../plan/verification/codex/RF-065.md) · [007](../plan/verification/codex/RF-007.md) · [008](../plan/verification/codex/RF-008.md).
- **Claude A / 3 개발:** [019](../plan/pending/RF-019.md) → [017](../plan/pending/RF-017.md). [HANDOFF_A](HANDOFF_A.md) · `work/p15-a-reporter-pure-20261021`.
- **Codex B / 1 REWORK:** [001](../plan/rework/codex/RF-001.md) → [009](../plan/rework/codex/RF-009.md) → [020](../plan/rework/codex/RF-020.md). **각 RF 마지막 '빠른 검증 전환' 절의 미충족 경계만** 증명하고 기존 PASS 재실행 금지.
- **Codex B / 2 독립 검증:** [018](../plan/verification/claude/RF-018.md) · [014](../plan/verification/claude/RF-014.md) · [015](../plan/verification/claude/RF-015.md) · [016](../plan/verification/claude/RF-016.md) · [013](../plan/verification/claude/RF-013.md). RF-013은 교차 Owner BLOCKED: B는 기존 `a21401db` 9+4 경로 read-only 소비자·부작용 검증만; RF-030/035 writer 미배정, RF-074 오라클 동결.
- **Codex B / 3 개발:** [068](../plan/pending/RF-068.md) → [064](../plan/pending/RF-064.md) (BLOCKED, 신규 증거 있을 때만). [HANDOFF_B](HANDOFF_B.md) · `work/p15-b-operator-structure-20261022`.

> 지팀장: 신규 증거 즉시 RF 판정·검증 전환·선별 통합·CI 확인. 상세 사유는 RF, 집계는 [STATUS](../plan/STATUS.md), 런검증은 별도 D04. `main`·안전·CI 오라클 무승인 변경 금지.
