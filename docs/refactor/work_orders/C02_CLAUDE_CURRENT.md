# C02 — Claude A 실행 진입점

**역할:** A 브랜치 `work/p15-a-reporter-pure-20261021`의 Owner 개발·푸시, B 브랜치의 독립 peer. **정본:** `integration/p1.5`. 공통 규칙은 [D00](D00_ENGINEERING_DELIVERY_POLICY.md), 수용 조건은 [RF 원본/STATUS](../plan/STATUS.md), 상세 증거는 [A HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md)와 [B HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md)에만 보존한다.

## 지금 실행할 순서
1. **A Owner [RF-040](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-040.md)·[RF-061](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-061.md):** 현재 CLAIM 2건의 남은 원래 C2/C3와 B full peer에 필요한 정확 SOURCE/미검증 경계를 정리한다. RF-040 기존 5 FAIL의 정적 출처 분류는 제출 완료; 같은 분석 반복 금지. RF-061 Step5C 보호 실행 금지.
2. **B Owner 독립 peer:** [RF-065](../plan/queue/02_DEVELOPING/CODEX_B/RF-065.md)·[RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md) 및 RF-066/070/071 중 **기존 scoped 증거가 없는 원래 안전 계약**을 확인한다. 새 B 커밋이 없어도 기존 SOURCE에서 미완료 peer 수행 가능.
3. **A Owner [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md)·[RF-031](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md):** B가 특정한 첫 원래 미충족 C에만 응답한다. 기존 Owner ACTION·성공 테스트 반복 금지.
4. **남은 A Owner:** RF-014/016/028/029/032/033/034/050, RF-051/054/058의 원본 미완료 계약을 계속 처리한다. RF-067 및 RF-046/047/052는 현재 LEAD/DONE이므로 재검증하지 않는다.
5. **CLAIM 슬롯이 비면 신규 READY:** [RF-036](../plan/queue/01_PENDING/UNASSIGNED/RF-036.md) → [RF-037](../plan/queue/01_PENDING/UNASSIGNED/RF-037.md) → RF-039/038. 현재 CLAIM 2/2를 넘기지 않는다. RF-057 보호 인접 경계는 별도 승인 전 SKIP.

## 매 예약의 실행 기준
**RF 원본 미체크 확인 → Owner 구현/반대 peer → A 브랜치 커밋·원격 푸시 확인 → 다음 READY RF.** 다른 쪽 SHA가 불변이거나 지팀장 새 배정이 없다는 이유만으로 `NO_DELTA` 종료 금지. 안전하게 진행할 수 있는 기존 RF부터 처리한다. 환경 장애는 구체적 오류와 미완료를 `BLOCKED`로 남긴다. 새 증거 없는 HANDOFF 반복 커밋 금지.

**보고:** `RF | 정확 SOURCE | 실제 코드/테스트 결과 | 첫 미충족 C | PUSH 여부 | NEXT`. RF 체크·물리 큐·STATUS 및 보호 규칙은 D00을 따른다.
