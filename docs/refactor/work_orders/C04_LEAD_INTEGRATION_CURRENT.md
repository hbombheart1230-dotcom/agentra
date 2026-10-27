# C04 — 지팀장② 선별 통합·필수 CI
> 현재 노트 · 예약 직접 진입 파일 · 권장 시작 매시 40분 · `integration/p1.5`

**상위 공통 규칙:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md). 구 `CURRENT.md`를 열지 않는다.

## 이번 역할의 목표·쓰기 범위
- **C05가 실물 `04_LEAD_ACCEPTANCE`에 옮긴 RF만** 받아, 정확한 Owner SOURCE SHA·반대 peer 전체 원래 범위 PASS·C1~C5 게이트와 통합 대상 diff를 확인하고 **C6 통합/KEEP 및 요구 CI 증거**를 완성한다.
- 수정: **C04**와 허용된 `integration/p1.5` 소스 변경만. **원본 RF 체크·큐·STATUS/CSV·LEAD_CURRENT·C01/C02/C03/C05는 건드리지 않는다.** C04의 결과가 C05의 최종 수용을 대신하지 않는다.

## 매회 통합 알고리즘
1. [LEAD 물리 큐](../plan/queue/04_LEAD_ACCEPTANCE/)에서 **새로운 후보만** 조회한다. C03의 `LEAD_READY` 권고나 과거 LEAD 기록만으로 사전 통합하지 않는다. C05가 완료한 C1~C5 게이트를 중복 재판정하지 않는다.
2. C05의 LEAD 판정에 적힌 **정확 SOURCE SHA와 독립 full PASS 식별자**가 통합할 소스와 일치하는지만 확인한다. 신규 SHA 불일치·보호 침해·gate 기록 누락이면 **통합 금지**, C05에 첫 blocker를 반환한다. C1~C5를 새로 테스트/수용하지 않는다.
3. **KEEP_VERIFIED:** 대상 소스의 Owner/peer/integration 바이트 동일성 확인, 기존 **해당 integration SHA**의 원래 요구 CI PASS가 재사용 가능한지 증거 링크 확보. 문서 변경을 소스 실적이라 표기 금지.
4. **코드 변경:** 정확 SOURCE SHA의 **검증된 파일/패치만 선별 반영**한다. A/B 브랜치 전체 무검토 병합 금지. 기존 통합 diff·충돌·원래 계약·안전 경계를 확인하고, 관련 UI 소스 변경 시 patchnotes 조건 준수.
5. 필요한 integration CI 결과를 **정확한 통합 commit SHA**에 매칭한다. 실제 성공 결과가 없으면 `CI_PENDING/FAIL/NOT_RUN`이라고 기록하고 C05에 DONE 가능하다고 넘기지 않는다. 원래 불필요한 CI는 근거가 있는 `NOT_REQUIRED`만 인정한다.
6. 후보 없으면 `NO_DELTA`. 승인 필요/보호영역이 나오면 해당 RF만 `BLOCKED`, 다른 정상 후보를 계속 처리한다.

## 현재 작업 (2026-10-27 확인 기준)
- 우선 14건은 **DEV 2·PEER 12·LEAD 0**, 즉 즉시 통합 후보 **0건**. C03의 수용 권고와 C05의 실제 LEAD 이동이 도착한 경우에만 시작한다.
- RF-043/053은 이미 C05가 `KEEP_VERIFIED` DONE 처리한 범위로, 같은 SHA 통합·CI 재실행 금지.
- RF-041은 RF-021 lazy-import patch가 포함된 격리 A tree에서 B 11/11 peer 증거가 있으나 현 integration에는 의존 패치가 아직 없다는 기록이다. **해당 RF가 LEAD에 실제 진입하고** 원래 조건/의존·안전 게이트를 충족하기 전에는 임의 통합 금지.
- RF-063 일부 diagnostics 수정은 이미 통합·offline safety CI 근거가 있으나 원래 76-owner 전체 C1~C5는 미충족. 기존 부분 통합을 전체 C6/DONE 승인으로 확대하지 않는다.

## C05 인계 — C6 정확 SHA 장부
| RF | Owner SOURCE SHA / 전체 peer 근거 | integration commit SHA | 통합 방식·diff | 요구 CI 실행/결과 | C6 상태 |
|---|---|---|---|---|---|
| 없음 | — | — | — | — | 신규 후보 대기 |

**다음 실행:** 신규 LEAD 실물 → 유효한 원래 범위 PASS 대조 → 안전한 PATCH/KEEP + 필요 CI → C05에 SHA 단위 인계. 보고: `RF | SOURCE SHA | integration SHA | KEEP/INTEGRATED/BLOCKED | CI PASS/FAIL/PENDING/NOT_REQUIRED | NEXT`.
