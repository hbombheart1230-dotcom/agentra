# Agentra P1.5 — CURRENT (작업 포인터 전용)

> 정본: `integration/p1.5`. A/B는 아래 **1 → 2 → 3순위**로 수행한다. 같은 SHA·동일 실패 반복 검증이나 신규 근거 없는 BLOCKED는 건너뛴다.

- **규칙 변경 알림 (상시):** 지팀장은 D00·D01·D02·D03의 정본 blob SHA를 직전 확인값과 비교하고, **변경이 확인된 경우에만** CURRENT에 해당 문서명·이전/신규 SHA·변경 핵심·영향받는 A/B의 재독 지시를 직접 명시한다. 미변경 시 재독 강제 금지. 변경 안내는 해당 A/B가 읽고 HANDOFF에 반영한 뒤 지팀장이 CURRENT에서 제거한다. 이번 확인 SHA: D00 `442247ea`, D01 `81daa098`, D02 `c6a5cf3c`, D03 `8ee3e385` (각 blob SHA 앞 8자리; 정본 전체 SHA는 Git으로 조회).
- **개발팀 규칙:** [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D03 / 개발 공통](D03_DEV_TEAM_RULES.md) · [D01 / Codex](../../../AGENTS.md) · [D02 / Claude](../../../CLAUDE.md)
- **Claude A 1순위 · 반려 재작업:** 현재 없음 ([rework/claude](../plan/rework/claude/) **0건**).
- **Claude A 2순위 · 독립 검증:** [RF-067](../plan/verification/codex/RF-067.md) · [RF-066](../plan/verification/codex/RF-066.md) · [RF-063](../plan/verification/codex/RF-063.md) · [RF-065](../plan/verification/codex/RF-065.md) · [RF-007](../plan/verification/codex/RF-007.md) · [RF-008](../plan/verification/codex/RF-008.md)
- **Claude A 3순위 · 나머지 개발:** [RF-019](../plan/pending/RF-019.md) → [RF-017](../plan/pending/RF-017.md) · [HANDOFF_A](HANDOFF_A.md) — `work/p15-a-reporter-pure-20261021`
- **Codex B 1순위 · 반려 재작업:** [RF-001](../plan/rework/codex/RF-001.md) → [RF-009](../plan/rework/codex/RF-009.md) → [RF-020](../plan/rework/codex/RF-020.md) — 각 RF 원소유 범위의 미충족 인수조건만 보완·실증. 타 RF·실거래·안전·오라클 수정 금지. [rework/codex](../plan/rework/codex/) **3건**.
- **Codex B 2순위 · 독립 검증:** [RF-018](../plan/verification/claude/RF-018.md) · [RF-014](../plan/verification/claude/RF-014.md) · [RF-015](../plan/verification/claude/RF-015.md) · [RF-016](../plan/verification/claude/RF-016.md) · [RF-013](../plan/verification/claude/RF-013.md) **(교차 Owner BLOCKED, 신규 승인·증거 전 재검증 금지)**
- **Codex B 3순위 · 나머지 개발:** [RF-068](../plan/pending/RF-068.md) → [RF-064](../plan/pending/RF-064.md) **(BLOCKED, 신규 증거 있을 때만 복귀)** · [HANDOFF_B](HANDOFF_B.md) — `work/p15-b-operator-structure-20261022`
- **실행:** **각 순위는 복수 RF 대기열이며 시간당/회차당 1건 제한 없음**. 같은 실행 회차에 해당 순위의 실행 가능한 RF를 순서대로 여러 건 처리하고, 막힌 RF만 건너뛴다. 1순위는 지팀장이 **rework/원개발자 폴더**로 이동시키고 허용 경로·수정 행동을 확정한 RF를 모두 순서대로 수행; 없으면 2순위의 **새 후보 SHA 또는 새 검증 근거**를 여러 건 검증(기존 PASS_SCOPED 반복 금지), 없으면 3순위. 검증자는 상대 RF를 고치지 않고 지팀장이 원개발자 1순위로 반환한다.
- **지팀장 정체 자가 조치:** A/B가 신규 코드·검증·REWORK 진척 없이 종료하면 지팀장이 해당 회차에 HEAD·HANDOFF·RF 인수조건·소유권·차단 증거를 직접 확인하고, 승인된 권한 안에서 원인을 해소(배정·범위·REWORK 지시·큐/CURRENT 수정 등)한 뒤 재실행 가능 상태로 만든다. 권한 밖 변경은 임의 수행하지 않고 필요한 승인·차단 근거를 명시한다.
- **지팀장:** 새 검증 결과를 해당 회차에 PASS/REWORK/BLOCKED로 판정하고 반려·재배정/선별 통합·exact-SHA CI·DONE까지 처리. [STATUS](../plan/STATUS.md) · [검증 큐](../plan/verification/) · [반려 큐](../plan/rework/) · [차단 이슈](../plan/troubleshooting/open/) · [RF-021 안전 HOLD](../plan/pending/RF-021.md)

> `main`·안전·CI 오라클 무승인 변경 금지. 신규 브랜치 금지. RF 큐 이동·최종 DONE·선별 통합은 지팀장만. 배정 변경 시 해당 RF 링크/줄만 갱신한다.
