# Agentra P1.5 — CURRENT (작업 포인터 전용)

> 정본: `integration/p1.5`. A/B는 아래 **1 → 2 → 3순위**로 수행한다. 같은 SHA·동일 실패 반복 검증이나 신규 근거 없는 BLOCKED는 건너뛴다.

- **공통 규칙:** [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D01 / Codex](../../../AGENTS.md) · [D02 / Claude](../../../CLAUDE.md)
- **Claude A 1순위 · 반려 재작업:** 현재 **실행 가능한 확정 REWORK 없음**. [RF-013](../plan/verification/claude/RF-013.md)은 교차 소유권·오라클 BLOCKED이므로 지팀장 해제 전 소스 수정 금지.
- **Claude A 2순위 · 독립 검증:** [RF-066](../plan/verification/codex/RF-066.md) · [RF-063](../plan/verification/codex/RF-063.md) · [RF-065](../plan/verification/codex/RF-065.md) · [RF-001](../plan/verification/codex/RF-001.md) · [RF-020](../plan/verification/codex/RF-020.md) · [RF-007](../plan/verification/codex/RF-007.md) · [RF-008](../plan/verification/codex/RF-008.md) · [RF-009](../plan/verification/codex/RF-009.md)
- **Claude A 3순위 · 나머지 개발:** [RF-019](../plan/pending/RF-019.md) → [RF-017](../plan/pending/RF-017.md) · [HANDOFF_A](HANDOFF_A.md) — `work/p15-a-reporter-pure-20261021`
- **Codex B 1순위 · 반려 재작업:** 현재 **실행 가능한 확정 REWORK 없음**. [RF-001](../plan/verification/codex/RF-001.md)은 PASS_SCOPED/계약 근거 미완으로, 지팀장이 소유 범위·수정 행동을 확정할 때만 이 순위로 반환.
- **Codex B 2순위 · 독립 검증:** [RF-018](../plan/verification/claude/RF-018.md) · [RF-014](../plan/verification/claude/RF-014.md) · [RF-013](../plan/verification/claude/RF-013.md) · [RF-015](../plan/verification/claude/RF-015.md) · [RF-016](../plan/verification/claude/RF-016.md)
- **Codex B 3순위 · 나머지 개발:** [RF-067](../plan/pending/RF-067.md) → [RF-064](../plan/pending/RF-064.md) **(BLOCKED, 신규 증거 있을 때만 복귀)** · [HANDOFF_B](HANDOFF_B.md) — `work/p15-b-operator-structure-20261022`
- **실행:** 1순위는 지팀장이 RF에 원개발자·허용 경로·수정 행동을 확정한 건만 수행. 없으면 2순위의 **새 후보 SHA 또는 새 검증 근거**만 검증(기존 PASS_SCOPED 반복 금지); 없으면 3순위. 결함은 검증자가 고치지 않고 지팀장이 원개발자 1순위로 반환한다.
- **지팀장:** 새 검증 결과를 해당 회차에 PASS/REWORK/BLOCKED로 판정하고 반려·재배정/선별 통합·exact-SHA CI·DONE까지 처리. [STATUS](../plan/STATUS.md) · [검증 큐](../plan/verification/) · [차단 이슈](../plan/troubleshooting/open/) · [RF-021 안전 HOLD](../plan/pending/RF-021.md)

> `main`·안전·CI 오라클 무승인 변경 금지. 신규 브랜치 금지. RF 큐 이동·최종 DONE·선별 통합은 지팀장만. 배정 변경 시 해당 RF 링크/줄만 갱신한다.
