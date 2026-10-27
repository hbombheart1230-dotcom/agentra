# C01 — Codex B 실행 진입점

**역할:** B 브랜치 `work/p15-b-operator-structure-20261022`의 Owner 개발·푸시, A 브랜치의 독립 peer. **정본:** `integration/p1.5`. 공통 규칙은 [D00](D00_ENGINEERING_DELIVERY_POLICY.md), 실제 체크는 [RF 원본/STATUS](../plan/STATUS.md), 신규 증거는 [A HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md)와 [B HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md)에서 읽는다. 이 파일에 검증 이력을 복제하지 않는다.

## 지금 실행할 순서
1. **독립 peer [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md) → [RF-031](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md):** A의 기존 Owner 증거와 B의 scoped 결과를 정확 SOURCE·원래 전체 C2/C3/C4 계약에 대조한다. 부족하면 **첫 미충족 계약을 직접 검증하거나 구체적으로 제시**하고 다음 RF로 이동한다. 기존 성공 테스트 반복 금지.
2. **B Owner [RF-065](../plan/queue/02_DEVELOPING/CODEX_B/RF-065.md) → [RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md):** 아직 끝나지 않은 전체 C1 ACTION·원래 C2/C3 근거를 채운다. 이미 통과한 isolated/fake 검증은 재사용한다.
3. **남은 A Owner peer:** RF-014/016/028/029/032/033/034/050의 원본 `03_PEER_REVIEW/CLAUDE_A`에서 아직 검증하지 않은 첫 **안전한 원래 계약**을 선택한다. `SCOPED_PASS`를 full PASS로 쓰지 않는다.
4. **위 RF가 차단되거나 대기면 신규 B Owner:** [RF-044](../plan/queue/01_PENDING/UNASSIGNED/RF-044.md) → [RF-045](../plan/queue/01_PENDING/UNASSIGNED/RF-045.md) → RF-024/010/011/059. 실제 경로·Owner 중복 확인 후 B HANDOFF에 CLAIM하고, 최대 동시 CLAIM 2건을 지킨다. 물리 이동은 C05 담당이다.
5. 자기 기존 RF-066/070/071의 안전한 미완료 계약도 처리할 수 있다. 보호 경계는 D00대로 NOT_RUN/승인 대기한다.

## 매 예약의 실행 기준
**RF 원본 미체크 확인 → 검증/필요한 코드 수정 → B 브랜치 커밋·원격 푸시 확인 → 다음 READY RF.** 동일 SHA라도 미완료 peer·Owner 계약 또는 PENDING READY가 남으면 `할 일 없음/NO_DELTA`로 끝내지 않는다. Git 인증·pytest 등 환경 차단은 정확한 오류와 미푸시 SHA를 `BLOCKED`로 보고하고, 가능한 다른 안전 작업을 진행한다. 새 사실 없는 문서 커밋은 금지한다.

**보고:** `RF | 정확 SOURCE | 실제 코드/테스트 결과 | 첫 미충족 C | PUSH 여부 | NEXT`. 완료 인정·단계 이동·STATUS·CI·보호 권한은 D00에 따른다.
