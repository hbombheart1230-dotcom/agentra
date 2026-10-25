# Agentra P1.5 — CURRENT (작업 포인터 전용)

> 정본 브랜치: `integration/p1.5`. **A/B는 아래 자기 실행 순서대로 수행한다.** 신규 증거 없는 BLOCKED·동일 SHA 재검증은 건너뛰고 다음 순서로 진행한다. 과거 실행 로그는 Git 이력에서 확인한다.

- **공통 규칙:** [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D01 / Codex](../../../AGENTS.md) · [D02 / Claude](../../../CLAUDE.md)
- **Claude A 2순위 · 개발:** [RF-019](../plan/pending/RF-019.md) · [RF-017](../plan/pending/RF-017.md) · [HANDOFF_A](HANDOFF_A.md) — `work/p15-a-reporter-pure-20261021`
- **Claude A 1순위 · 독립 검증:** [RF-063](../plan/verification/codex/RF-063.md) · [RF-065](../plan/verification/codex/RF-065.md) · [RF-001](../plan/verification/codex/RF-001.md) · [RF-020](../plan/verification/codex/RF-020.md) · [RF-007](../plan/verification/codex/RF-007.md) · [RF-008](../plan/verification/codex/RF-008.md) · [RF-009](../plan/verification/codex/RF-009.md)
- **Codex B 2순위 · 개발:** [RF-066](../plan/pending/RF-066.md) → [RF-064](../plan/pending/RF-064.md) **(BLOCKED, 신규 증거 있을 때만 복귀)** · [HANDOFF_B](HANDOFF_B.md) — `work/p15-b-operator-structure-20261022`
- **Codex B 1순위 · 독립 검증:** [RF-013](../plan/verification/claude/RF-013.md) · [RF-014](../plan/verification/claude/RF-014.md) · [RF-015](../plan/verification/claude/RF-015.md) · [RF-018](../plan/verification/claude/RF-018.md) · [RF-016](../plan/verification/claude/RF-016.md)
- **실행 규칙:** 1순위는 **새 후보 SHA·근거가 있는 RF만** 왼쪽부터 처리. 없거나 차단 중이면 즉시 2순위 개발을 왼쪽부터 진행. 남은 작업과 차단 사유는 HANDOFF에 기록. RF 판정·재배정·큐 이동은 지팀장 담당.
- **지팀장 상황판:** [STATUS](../plan/STATUS.md) · [검증 큐](../plan/verification/) · [차단 이슈](../plan/troubleshooting/open/) · [RF-021 안전 HOLD](../plan/pending/RF-021.md)

> `main` 수정 금지. 새 브랜치 금지. 지팀장만 RF 큐 이동·최종 DONE·선별 통합 판정. Quick Fix는 D00 및 사전 CURRENT 승인 범위만. 이 문서는 작업 배정 변경 때 **해당 경로 한 줄만** 고친다.
