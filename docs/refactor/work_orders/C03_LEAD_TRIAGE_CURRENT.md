# C03 — 지팀장① 수용조건 판정·작업 배정
> 현재 노트 · 예약 직접 진입 파일 · 권장 시작 매시 05분 · `integration/p1.5`

**상위 공통 규칙:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md). 구 `CURRENT.md`를 열지 않는다.

## 이번 역할의 목표·쓰기 범위
- **RF 원본 직접 처리 원칙:** C03은 `integration/p1.5`의 실제 큐에 있는 `RF-XXX.md`의 `## DONE 체크` C1~C5 및 최신 검증 이력을 읽고, 현재 미충족 조건 **하나와 담당**만 선택해 배정한다. C03에서 RF별 작업명세·남은 테스트 목록·수용 조건을 다시 요약하거나 새로 만들지 않는다.
- **C01/C02 실행 원칙:** A/B는 C03 설명이 아니라 **배정된 원본 RF 파일의 실제 미완료 체크와 원래 수용 범위**를 직접 확인하여 잔여 작업을 처리한다. 완료 주장·반대 peer 검증은 정확 SOURCE SHA와 HANDOFF 증거로 분리한다. 이미 같은 SHA/범위로 PASS한 검증은 반복하지 않는다.
- 수정: **C03**, C01/C02의 **지팀장 배정 델타 부분**, RunLab OPEN 대장의 **신규 접수·소유자 배정 부분**만. A/B 개발 기록, 원본 RF 체크/큐, STATUS/CSV/LEAD_CURRENT, 통합 소스는 수정하지 않는다.
- C03의 판정은 **권고와 배정**만. RF 체크·단계·STATUS/C7은 C05, 코드 선별 통합·필수 CI/C6 근거는 C04가 소유한다(D00 §1·§2.1).

## 매회 실행 — RF 원본에서 잔여 조건 직접 판독
1. C01/C02 최신 **신규 HANDOFF delta**와 C05의 STATUS 변경 RF만 확인하고, 해당 **실물 경로의 RF 원본** `## DONE 체크` 및 최신 검증 기록을 먼저 읽는다. 과거 RF 본문의 LEAD/HOLD 문구는 이력으로 취급하며 D00·최신 실물 단계가 우선이다.
2. C1~C5에서 실제 미완료(`[ ]`, PARTIAL/MISSING/SAFETY_BLOCKED)를 식별한다. Owner 완료 주장(C1~C3/해당 C5)과 **반대 peer의 원래 전체 범위 PASS(C4)**를 SOURCE SHA별로 대조해 재사용 가능한 증거를 제외한다. `[x]`도 SOURCE/범위 불일치 시 C05에 판정 요청한다.
3. 미충족이면 C01/C02의 배정 델타에 **`RF 실물 경로 | 현재 Owner→Peer | 최초 미충족 C번호 | 증거 부족/보호 사유 한 줄 | SOURCE SHA(확인된 경우) | 해제 담당 | NEXT=원본 RF 잔여 체크 직접 수행`**만 남긴다. **C03에 파일별 테스트·구현 세부내용을 복제하지 않는다.**
4. 원래 C1~C5 전부 수용 가능하면 아래 `LEAD_READY 제안`에 실물 단계·SHA·반대 peer 전체 PASS 증거만 기입해 **C05 독립 확인**으로 넘긴다. C03은 RF를 옮기거나 체크하지 않으며 C04 통합·CI를 선행 승인하지 않는다.
5. 불충분한 RF는 첫 원래 미충족 조건 하나만 해당 Owner/Peer에게 반환하고, 다른 일반 RF는 독립 진행한다. 기존 증거 재실행·원래 범위 외 전수검증 금지. 신규 delta 없으면 `NO_DELTA`.

## 최우선 14건 — RF 원본 직접 실행 인덱스 (2026-10-27 실물 기준)
**이 목록은 담당·실물 경로만 제공한다.** 첫 C번호·현재 잔여 조건·실행 범위는 배정 시 **각 RF 원본 `## DONE 체크`와 최신 HANDOFF 증거에서 직접 다시 판독**한다. 아래 링크 밖의 별도 C03 작업명세는 없다.

- **B Owner → A Peer · DEV:** [RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md), [RF-065](../plan/queue/02_DEVELOPING/CODEX_B/RF-065.md).
- **B Owner → A Peer · PEER:** [RF-067](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-067.md), [RF-069](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-069.md).
- **A Owner → B Peer · PEER:** [RF-014](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md), [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md), [RF-016](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md), [RF-028](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md), [RF-029](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md), [RF-031](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md), [RF-032](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md), [RF-033](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md), [RF-034](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md), [RF-050](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md).

현재 STATUS 기준 **DEV 2·PEER 12·LEAD 0**. RF-043/053은 DONE이므로 재배정·재검증 금지. RF-069 UEF5 historical snapshot 및 RF-032/034 보호 경계는 D00 승인 규칙 유지. **실물 이동·체크 상태가 바뀌면 C05의 RF/STATUS를 우선하고, 이 인덱스는 그때만 갱신**한다.

## RunLab #32 접수·배정 담당
- [OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md)에는 **새 사실만** 중복 제거해 기록하고, `RL32-ORDER/GUARD`는 B read-only/temp fake, `RL32-REPORT`는 A read-only/temp fake, `RL32-IMAGE/OPS`는 별도 RunLab read-only 증거를 받는다.
- FILE_COVERAGE는 소유 파일 후보일 뿐 **`DEFECT_OWNER_PENDING`**. 적용 이미지 `RUN_SOURCE_SHA=UNKNOWN`인 이상 원인이나 운영 버전 확정/안전 코드 수정 지시 불가. RF 단계 또는 STATUS 변경이 필요하면 C05로 인계한다.

## LEAD_READY 제안 (C05가 반드시 독립 확인; 물리 이동 아님)
| RF / 현재 큐 | Owner SOURCE SHA | 반대 peer 전체 PASS 증거 | C1~C5 매칭 | C05 다음 조치 |
|---|---|---|---|---|
| 없음 | — | — | — | 신규 근거 도착 때만 갱신 |

**다음 실행:** 아래 최신 인덱스 및 우선 14건 중 신규 증거가 도착한 **RF 원본 미완료 체크**를 직접 처리하도록 배정한다. 보고는 `RF 경로 | 첫 미충족 C | 배정 담당 | LEAD_READY 제안 여부 | NEXT`만 남긴다.

## 2026-10-27 최신 HANDOFF — 원본 RF 실행 라우팅 (증거 복사 금지)

> A 최신 검토 `b7da8bab`, B 신규 조사 `7af57e8e`에서 수용한 **증거의 정본은 각 HANDOFF_A/B와 해당 RF 최신 검증 기록**이다. 기존 C03의 상세 증거 복사표는 제거했다. 이 라우팅은 현재의 **실행 대상**만 가리키며, 개별 원래 조건의 충족 판정은 아니다.

- **A Owner → B Peer:** [RF-052](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-052.md), [RF-046](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-046.md), [RF-047](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-047.md). A는 각 RF 원본의 잔여 Owner 체크를 직접 판독해 최종 ACTION·SOURCE 증거를 HANDOFF에 제출한다. B의 최신 전체/부분 peer 근거는 **재실행하지 않고** C05에 연결한다. C05 판정 전 C04 사전 통합 금지.
- **B Peer(A Owner):** [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md), [RF-050](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md). B는 A의 최신 제출과 원본 RF 미완료 체크만 매칭해 **최초 누락 조건**을 처리한다. 기준선 테스트·기존 fake 검증을 재실행하지 않는다.
- **B Owner → A Peer:** [RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md), [RF-067](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-067.md). B는 원본 잔여 Owner 체크를 채울 수 있는 새 근거를 제출하고, A는 기존 독립 peer의 **실제 포괄 범위와 미검증 경계**만 대조한다. 동일 SOURCE·범위 재검증 금지.
- **그 외 우선/일반 RF:** 위 `최우선 14건`의 실제 RF 파일과 C01/C02 HANDOFF를 기준으로, 신규 delta 또는 미충족 체크가 있는 RF를 계속 진행한다. 막힌 RF 하나 때문에 다른 RF를 대기시키지 않는다.
- **P0 RunLab #32:** B read-only source trace는 broker/local 불일치를 설명할 수 있는 경로이지 실제 원인 확정이 아니다. `RUN_SOURCE_SHA=UNKNOWN`·`DEFECT_OWNER_PENDING` 유지. 새로운 사실만 [OPEN 대장](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md)에 접수하고 승인 없는 보호 fake/운영 실행은 `NOT_RUN`.

**LEAD_READY는 현재 제안 없음.** C03의 과거 고정 C번호·테스트 요약보다 **RF 실제 미완료 체크 + 검증 출처/SHA + C05 최신 상태**가 우선한다. **원본 RF 체크·큐·STATUS 수정은 C05만 수행**한다.
