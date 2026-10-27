# C03 — 지팀장① 수용조건 판정·작업 배정
> 현재 노트 · 예약 직접 진입 파일 · 권장 시작 매시 05분 · `integration/p1.5`

**상위 공통 규칙:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md). 구 `CURRENT.md`를 열지 않는다.

## 이번 역할의 목표·쓰기 범위
- 신규 HANDOFF·관련 RF 원본 체크의 **C1~C5 수용 증거/최초 미충족 조건을 정밀 대조**하여 A/B에게 **해제 작업 한 개**를 명시한다. Owner 또는 peer가 이미 같은 SOURCE SHA/범위로 PASS한 것을 반복 검증하지 않는다.
- 수정: **C03**, C01/C02의 **지팀장 배정 델타 부분**, RunLab OPEN 대장의 **신규 접수·소유자 배정 부분**. A/B 개발 기록, 원본 RF 체크/큐, STATUS/CSV/LEAD_CURRENT, 통합 소스는 수정하지 않는다.
- C03의 판정은 **권고와 작업 배정**만. 실제 단계 이동·체크/STATUS는 C05, 코드 통합·CI는 C04가 수행한다. 이 경계는 D00 §1·§2.1을 따른다.

## 매회 실행
1. C01/C02의 마지막 **신규 HANDOFF delta**, C05가 유지한 STATUS의 **변경 RF**, 해당 원본 RF·SOURCE SHA 중 필요한 것만 확인한다.
2. Owner의 원래 수용 범위 완료 제출(C1~C3/해당 C5) 및 반대 peer full PASS(C4)를 **각기 다른 출처**로 대응시킨다. 불완전한 과거 scoped 검증은 해당 범위에만 재사용한다.
3. 원래 필수 C1~C5가 충족되었다고 판단한 RF는 아래 `LEAD_READY 제안`에 **실제 물리 단계·SHA·peer 증거**를 적어 C05가 재확인하게 한다. **C03은 RF 이동하지 않는다.**
4. 부족하면 `RF | 최초 C번호 | 원래 필수 누락 증거/안전 사유 | 정확 SOURCE SHA | 해제 담당 | NEXT`를 A/B 배정 델타에 기록한다. 원래 RF 범위 밖의 새로운 전수 테스트를 만들지 않는다.
5. 일반 RF는 막힌 RF와 독립 진행. 신규 델타가 없으면 `NO_DELTA`.

## 최우선 14건 — 첫 해제 항목 (2026-10-27 기준; 현행 STATUS가 바뀌면 해당 RF만 정정)
| 실물 단계 / RF | 원 Owner → Peer | 첫 해제 대상 |
|---|---|---|
| DEV 063 | B → A | C1: diagnostics 잔여 63-owner ACTION/CLI·효과 근거 |
| DEV 065 | B → A | C1: research 54-owner KEEP/CLI·효과 근거 |
| PEER 067 | B → A | C4: 14개 root wrapper 원래 필수 호출/argv 계약 대비 A scoped 2건 범위 |
| PEER 069 | B → A | C3: UEF5 historical snapshot 경로/SHA/use-scope·사용자/증거 소유자 승인 없으므로 SAFETY_BLOCKED |
| PEER 015 | A → B | C3: 역사 11 FAIL BASE/후보 비교; B-only frozen inventory 추가 1 FAIL 구분 |
| PEER 050 | A → B | C4: router/cache 8-owner ↔ B fake 10/10 원래 필수 범위 |
| PEER 031 | A → B | C2: Reporter writer/State/실패 원래 범위 ↔ B caller 8/8 |
| PEER 014 | A → B | C4: Scanner shim→RF-009 repeat/risk/NOOP |
| PEER 016 | A → B | C4: Strategist 외부 facade/nested State |
| PEER 028 | A → B | C4: trade_report rich schema 필수 소비자 |
| PEER 029 | A → B | C4: trade_story facade→bundle |
| PEER 033 | A → B | C4: Q10/Q12 input_worker→publish_input |
| PEER 034 | A → B | C4: alpha casebook→Scanner; 보호 UEF/closeout 제외 |
| PEER 032 | A → B | C2: evaluation writer/validation-id; 보호 UEF 제외 |

- **현재 실물 우선 14건:** DEV 2·PEER 12·LEAD 0. 완료 RF-043/053는 재검증/재배정 금지. RF-052 path scoped PASS≠원래 2-owner full PASS, RF-041은 RF-021 미통합 의존이 있음. 새 full PASS 증거가 오면 우선한다.
- 위 C번호는 **현재 최초 해제 후보**이지 수용 확정이 아니다. C05의 물리 RF/STATUS가 변경되면 새 스냅샷을 기준으로 한다.

## RunLab #32 접수·배정 담당
- [OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md)에는 **새 사실만** 중복 제거해 기록하고, `RL32-ORDER/GUARD`는 B read-only/temp fake, `RL32-REPORT`는 A read-only/temp fake, `RL32-IMAGE/OPS`는 별도 RunLab read-only 증거를 받는다.
- FILE_COVERAGE는 소유 파일 후보일 뿐 **`DEFECT_OWNER_PENDING`**. 적용 이미지 `RUN_SOURCE_SHA=UNKNOWN`인 이상 원인이나 운영 버전 확정/안전 코드 수정 지시 불가. RF 단계 또는 STATUS 변경이 필요하면 C05로 인계한다.

## LEAD_READY 제안 (C05가 반드시 독립 확인; 물리 이동 아님)
| RF / 현재 큐 | Owner SOURCE SHA | 반대 peer 전체 PASS 증거 | C1~C5 매칭 | C05 다음 조치 |
|---|---|---|---|---|
| 없음 | — | — | — | 신규 근거 도착 때만 갱신 |

**다음 실행:** 새로운 증거가 도착한 우선 14건의 *최초 미충족 조건 1개* 해결부터. 보고는 `RF | 신규 근거 | 첫 부족 C | 배정 대상 | LEAD_READY 제안 여부 | NEXT`만 남긴다.

## 2026-10-27 신규 HANDOFF 증거 인수 · C03 배정 델타 (A `b7da8bab` / B `7af57e8e`)

> 이 델타는 **권고/배정**이다. RF 원본 C체크·실물 큐·STATUS·C6/C7은 C05/C04만 처리한다. 과거 성공 테스트 재실행 금지.

| RF / 실물 큐 | 신규 SOURCE SHA·반대 peer 증거 | 최초 원래 조건/담당 | 다음 최소 조치·C05 인계 |
|---|---|---|---|
| **052 / PEER(A)** | A `f9176623`, `receipts.py@10283d8f`; B `B-20261027-RF052-FULL-PEER` 40/40 normal/-O, 기존 Windows/UNC peer까지 합쳐 **원래 2-owner C1~C4 PEER_PASS 주장**. 현재 integration receipts blob `e59febed`로 **코드 아직 미통합** | **C1 / A Owner:** 원본 RF 표의 `KEEP_CANDIDATE` 2파일을 최종 ACTION(KEEP+수정 1파일)·소비자·예외/효과·정확 blob으로 명시해 C05에 인계 | B 전체 peer 반복 금지. A Owner ACTION 도착 시 C05가 C1~C5 독립 수용 확인 후 **LEAD 진입 여부** 판정; C04 사전 통합 금지 |
| **046·047 / PEER(A)** | A=integration=B exact blobs: RF-046 `0d046552/9206f801`, RF-047 `edeb5378/299d328c/adc8a568/e584b141`; B `B-20261027-RF046-047-KEEP` 63/63 normal/-O **원래 최소 KEEP API 범위 PEER_PASS 주장** | **C1 / A Owner:** 원본의 `KEEP_CANDIDATE` 2+4파일을 각각 최종 `KEEP_VERIFIED` ACTION·caller/효과·blob으로 정리 | C05가 기존 A owner·B full peer 범위와 C1~C5를 대조해 LEAD 판단. B 테스트 반복·새 소스 변경 금지 |
| **015 / PEER(A)** | A run145 `aa00bcd9`: BASE/integration 253 PASS·11 FAIL의 **정확 11 node 모두 동일 B-stage composed-inventory 원인**; B 이전 `252 PASS/12 FAIL`의 추가 1개는 B-only Commander frozen inventory | **C3 / B Peer:** 새 node 근거를 기존 B baseline 증거에 대조해 **RF-015 원래 실패·경계 C3** 충족 범위만 판정. frozen oracle 수정/재실행 금지 | BASE 실패를 Monitor 신규 회귀로 분류하지 않는다. C1/C2 등 다른 미체크를 자동 MET로 승격하지 않는다 |
| **050 / PEER(A)** | A run146 `b7da8bab`: 8-owner exact blob 및 ACTIVE/COMPAT caller·cache/write 계약 제출; B 기존 fake 10/10은 일부 Strategist/Reporter 경계만 | **C4 / B Peer:** 새 A caller 목록 중 기존 10/10이 **덮지 못한** 실제 필수 `LLMRouter.chat` caller 실패·State·캐시 경계만 isolated fake normal/-O로 독립 판정 | 전체 8-owner/외부 동적 소비자 추정 금지. C4 full PASS 전 LEAD 제안 금지 |
| **067 / PEER(B)** | B `44d0c52d`: 14 wrapper의 정확 위임 매핑, 기존 A 2 wrapper full boundary만 명시; A run138 다수 delegated target scoped CLI 증거도 기존 HANDOFF에 있음 | **C4 / B Owner→A Peer:** A run138 **실제 target별** 기존 증거와 B scope-map을 먼저 매칭해 빠진 **원래 필수 안전 경계 1개**만 요청 | 보호 UEF/real preflight/Windows 실호출은 승인 전 NOT_RUN. wrapper 14 fake·이미 수행된 target 재실행 금지 |
| **063 / DEV(B)** | B `8f899efc`: 잔여 25 read-static 후보 caller 정적 매핑; 63-owner 중 효과형 38은 아직 ACTION/효과 근거 없음 | **C1 / B Owner:** 25 KEEP 후보 최종 ACTION 및 나머지 38의 effect/SAFETY_HOLD 근거 | 기존 A TEXT/JSON 4/4와 hosted CI 재사용. C1 전체 충족 전 PEER/LEAD 승격 금지 |

**추가 P0 RunLab #32:** B `7af57e8e` read-only 소스 추적에서 주문 제출 후 execution JSONL 기록 전 실패가 broker/local 불일치를 만들 **수 있는 경로**와 guard `-1` 보존/후속 갱신 시 pruning 구조를 보고. **실제 SELL 원인 확정 아님**, `RUN_SOURCE_SHA=UNKNOWN`·`DEFECT_OWNER_PENDING` 유지. OPEN 대장에 신규 근거만 접수; 보호 fake는 승인 전 NOT_RUN.

**LEAD_READY 제안: 없음.** RF-052/046/047은 B full peer 근거가 신규 도착했지만 원본 RF의 최종 C1 ACTION/전체 C1~C5 수용 체크가 미완료다. C05만 판정/이동한다. **다음:** A 최종 C1 ACTION 3건 → C05, B RF-015 C3 대조·RF-050 C4 최소 peer, RF-067 기존 target peer 증거 매칭.
