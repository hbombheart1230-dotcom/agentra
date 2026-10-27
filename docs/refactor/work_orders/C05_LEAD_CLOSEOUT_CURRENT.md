# C05 — 지팀장③ | RF 체크·실물 큐·DONE 최종 보드

> 진입점 **C05 + [D00](D00_ENGINEERING_DELIVERY_POLICY.md)**. 구 `CURRENT.md` 사용 금지. **원본 RF의 C1~C7, 물리 큐, [STATUS](../plan/STATUS.md) 갱신은 C05 단독 책임.**

## 지금 하는 일

| 우선 | 실물 RF 링크 | 상태 | C05 즉시 처리 |
|---|---|---|---|
| 1 | [RF-046](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-046.md) | LEAD · C1~C5 수용, C6/C7 미완료 | C04 source/CI 증거 인수 → 충족 즉시 DONE |
| 2 | [RF-047](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-047.md) | LEAD · C1~C5 수용, C6/C7 미완료 | C04 KEEP/CI 증거 인수 → 충족 즉시 DONE |
| 3 | [RF-052](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-052.md) | LEAD · C1~C5 수용, C6/C7 미완료 | C04 검증된 통합 SHA/CI 인수 → 충족 즉시 DONE |
| 4 | [C03 수용 후보](C03_LEAD_TRIAGE_CURRENT.md) / [A HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md) / [B HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md) | DEV/PEER | **RF 원본 C1~C5·SOURCE SHA·반대 peer full PASS 확인** 시 LEAD 실물 이동 |

**마지막 확인된 물리 현황:** 총 93건 · PENDING 51 · DEV 9 · PEER 14 · **LEAD 3** · DONE 16 · REWORK 0. 우선 14건(DEV 2 + PEER 12)은 C1~C7 **MET 4, N/A 14, 미완료 80**. 최신 수치는 실제 큐와 [STATUS](../plan/STATUS.md)가 우선한다. RF-043/053은 DONE이며 재실행 금지.

## 매회 반드시 실제 처리

1. C04에서 새 C6 결과가 왔으면 **같은 회차에** 해당 RF 원본 C6 MET(정확 SHA CI 또는 근거 있는 NOT_REQUIRED) → C7 체크 → 실물 `05_DONE` 이동 → STATUS 반영까지 끝낸다. 후속 승인 회차 생성 금지.
2. C03 신규 후보는 **실제 RF 원본 `## DONE 체크`와 최신 기록**을 먼저 열고, C1~C5 전체 MET/적법 N/A 및 반대팀 정확 SHA full PEER_PASS일 때만 `03→04` 이동한다. `SCOPED_PASS`, 미검증, SAFETY_BLOCKED는 승격 금지.
3. DEV/PEER 미충족 RF는 **처음 부족한 C 하나 + 해제 담당만** C03에 돌려주고 다음 RF 진행. 이미 같은 SHA/범위의 증거 재실행 지시 금지.
4. 실물 이동할 때 **원본 RF 체크/증거 메타 + STATUS/CSV + LEAD_CURRENT**를 함께 맞추고 `python docs/refactor/tools/sync_rf_checklist_status.py --write` 후 `--check`로 실물 93 유일성과 단계 수 확인한다.
5. **한 RF 대기·차단으로 회차 종료 금지.** 다음 READY RF를 처리한다. 증거 없이 DONE 수를 늘리거나 N/A를 PASS로 세지 않는다.

**쓰기 권한:** C05는 원본 RF·물리 단계·STATUS·LEAD_CURRENT·본 C05만 변경한다. C03 권고는 실제 승인이 아니며 C04 통합도 자동 DONE이 아니다. [RunLab #32 OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md)은 개발 DONE과 별도 `RUNTIME_PENDING`이며 보호/운영 변경은 별도 승인.

**보고 1줄/RF:** `RF 링크 | Owner/peer SHA | C1~C5 | C6 integration SHA·CI | 체크/물리 이동/STATUS | 남은 최초 차단`.
