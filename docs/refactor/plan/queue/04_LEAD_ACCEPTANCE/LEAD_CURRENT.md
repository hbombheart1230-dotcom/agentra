# LEAD — P1.5 최종 인수·종결 작업표 (2026-10-27)

**정본:** `integration/p1.5`의 [D00](../../../work_orders/D00_ENGINEERING_DELIVERY_POLICY.md) · [C05 최종 종결](../../../work_orders/C05_LEAD_CLOSEOUT_CURRENT.md) · [STATUS](../../STATUS.md). 이 문서는 **LEAD의 현재 실행 지침**이다. 아래 개별 RF 문서의 이전 날짜 `LEAD_HOLD`와 '다음 전수검증' 지시는 해당 시점의 **증거 이력**으로 읽고, 이 문서와 D00의 최신 규칙을 우선한다. 단 **개별 RF의 본래 작업 목표·DONE 체크·보호 경계는 폐기하지 않는다**.

## LEAD 입구 원본 체크 게이트 (D00 §2.1)

- **C1~C5의 원래 필수 조건 `MET` 또는 사유 있는 `N/A` + 반대 peer 전체 원래 범위 `PASS` + SHA 대응**이 확인되지 않으면 `04_LEAD_ACCEPTANCE` 물리 이동 금지. 기존 `SCOPED_PASS`, 단독 Owner 제출, 오래된 HOLD 처리만으로 입구를 열지 않는다.
- 현재 `04_LEAD_ACCEPTANCE` 실물 **0건**이다. 14개 과거 LEAD 후보는 `02_DEVELOPING` 2건, `03_PEER_REVIEW` 12건. 현재 누락은 각 RF·[STATUS](../../STATUS.md)에서 읽고, 필요한 C조건 1개만 Owner/Peer에 지정한다.
- **지팀장만 RF 원본 체크·STATUS 동기화 책임**이 있다. A/B는 SOURCE SHA 범위·독립 근거 제출. LEAD 입장 후 C6 요구 CI·통합, C7 `05_DONE` 이동을 같은 회차에 처리한다.

## 종결 알고리즘 (한 번만)

1. **원래 RF 수용 조건**과 최신 SOURCE SHA/독립 peer 범위 대조. 이미 PASS한 동일 SHA·동일 경계 반복 검증 금지.
2. **원래 필수 범위를 독립 peer가 PASS**했다면 지팀장은 직접 Python/Windows/IO/State를 재검증하지 않는다. 코드 변경이면 선택적으로 integration 반영, 무변경 KEEP이면 byte-identical 여부 확인. 통합 diff/충돌·계약 보호·**요구되는 integration SHA CI**만 확인.
3. 충족 즉시 `04_LEAD_ACCEPTANCE → 05_DONE` **같은 회차** 수행. 물리 파일 이동/큐 유일성 및 STATUS **변경 항목만** 정리. 별도 지팀장 승인 왕복 없음.
4. peer가 `SCOPED_PASS`면 그것을 전체 PASS라고 바꾸지 않는다. **본래 수용 조건에 필요한 미충족 항목 한 개와 해제 담당**만 적는다. 동적 전체 소비자, 모든 owner별 CLI/Windows/State/예외 전수 검증을 새로운 공통 DONE 게이트로 추가 금지.
5. **기존 BASE와 동일한 실패는 신규 회귀로 취급 금지.** RF의 실제 구현이 일으킨 신규 실패/원래 필수 계약 위반만 REWORK. 무관한 후속 품질/운영 문제는 별도 RF/이슈로 분리하되, 실제 보호 경계 침해는 분리해도 해제하지 않는다.
6. `RF-032/034/069` 및 RunLab #32에서 **UEF/closeout/실거래·운영 경계는 사용자 승인 없이 실행·수정하지 않는다.** 그 보호 대상만 SAFETY_HOLD; 무관한 읽기 전용 일반 RF의 판단은 계속한다.

## 우선 14 — 수용 조건 재확인 순서 (실제 DEV 2·PEER 12·LEAD 0, 아직 DONE 아님)

| RF | Owner → Peer | 이미 수용한 사실 / 먼저 내릴 판정 | 미충족일 때 딱 필요한 것 |
|---|---|---|---|
| **063** | B → A | 1행 TEXT NameError 수정 통합, A 4/4 peer, 해당 integration offline safety CI 양 모드 PASS. **우선 원래 76-owner의 MOVE/KEEP/SAFETY_HOLD 분류와 검증 범위가 충족됐는지 판정.** | 원래 RF가 요구하는 실제 미충족 항목만 특정. 전체 76 CLI·Windows Scheduler 재실행은 자동 조건 아님; 보호 실행 금지 |
| **067** | B → A | 14개 공개 루트 wrapper 및 A 독립 일부 fake peer 수용. wrapper와 위임 대상 diagnostics(RF-063)의 책임 분리 후 KEEP 종결 가능성 심사 | wrapper 자신의 호출/import/argv 계약의 실제 누락만. 보호 target·Windows 운영 테스트를 공통 추가 조건으로 삼지 않음 |
| **015** | A → B | 기존 Monitor 19 owner 동등; A가 B 신규 코드 검증. A 최신 독립 기준선 비교: BASE/integration 253 PASS·11 FAIL, B 252 PASS·12 FAIL, **추가 1건은 B-only Commander frozen inventory 문제** | B-only 비통합 코드 제외·추가 실패 소유권 확정 후 기존 Monitor 원래 조건 판단. frozen oracle 변경 금지 |
| **050** | A → B | 라우터/클라이언트 scoped peer + B fake caller 10/10. 변경 없는 8 owner의 KEEP 수용 조건 판정 | 원 RF에서 반드시 요구하는 호출/캐시 계약만 확인. UI 3-stage·캐시 OSError 전수는 임의 추가 게이트 금지 |
| **031** | A → B | B Reporter 실제 caller 8/8 및 partial OSError 단위 peer. 원개발 미변경·BASE 동일 | 원래 writer/State/실패 계약과 증거를 1회 매칭, 실제 누락 시 해당 소비자만 검증 |
| **014** | A → B | Scanner 20 owner blob 일치; Top1 B scoped peer·dynamic mapping A 근거 | 본래 scanner shim/NOOP 계약 중 검증되지 않은 **필수** 경계만 |
| **016** | A → B | Strategist/news query·node projection·nested State 관련 증거 다수 수용 | 기존 수용 조건의 외부 facade가 실제 미검증인 경우만 B 독립 peer |
| **028** | A → B | trade_report 85 owner KEEP 후보, rich schema A 증거, B 기존 facade scoped peer | 원래 정식 스키마 소비자 중 **필수** 독립 검증 누락만 |
| **029** | A → B | trade_story 38 owner KEEP 후보, truth-root B scoped peer | 원래 story assembly facade→bundle의 필수 독립 peer 여부만 |
| **033** | A → B | Q10/Q12 45 owner evidence·입력 가설 증거 보존 | 원래 input_worker/publish_input 경계 실제 수용 조건 확인, 보호·운영 효과 분리 |
| **034** | A → B | alpha/Rank1 40 owner evidence, latent/casebook/pipeline 일부 scoped 수용 | 원래 casebook→Scanner 필수 독립 peer라면 해당 범위만. closeout/UEF 보호 실행 금지 |
| **032** | A → B | evaluation 135 owner evidence/writer 일부 PASS | 원래 필수 writer·validation-id 범위 중 미충족 1개만; UEF 보호 사항은 승인 대기 |
| **065** | B → A | research 54 owner KEEP 후보, A import 및 안전 CLI 일부 독립 peer | owner CLI 사용/효과 분류가 본래 체크를 만족하는지 먼저 판단. 54개 운영 CLI·Scheduler 전수 실행 금지 |
| **069** | B → A | capture/build 7 owner KEEP 후보, A 2 CLI scoped peer | **승인된 UEF5 historical snapshot 경로·SHA·use-scope가 없음. 이 보호 경계는 승인 전 BLOCKED/NOT_RUN**. 다른 RF로 이동 |

**이 표는 이전 LEAD 14건의 수용 조건 추적이다. 현재 파일은 02/03 큐에 있으며 [STATUS](../../STATUS.md)의 실물 링크가 우선한다.** 종료 순서는 PASS/DONE 선언이 아니다. RF별 최초 완료 여부는 원래 DONE 체크 및 기존 증거의 실제 범위로 결정한다. *지팀장 검증팀의 중복 작업 금지*는 *원래 필수 조건 면제*와 다르다.

## 짧은 인계 형식

`RF | Owner/peer SOURCE SHA | ORIGINAL_SCOPE: MET / MISSING(정확 1개) / SAFETY_BLOCKED | CI 통합 SHA: PASS/NOT_RUN/NOT_REQUIRED | 실제 큐 이동 | NEXT`

- 같은 증거가 있으면 지팀장 리뷰에서 새로운 일반 목적 하네스를 만들지 않는다.
- 외부 worker PASS는 `PEER_PASS`로 인수하고 지팀장 `DIRECT_PASS`라고 기록하지 않는다.
- 전체 93건 전수 점검/STATUS 전체 교체/Issue 중복 댓글은 변경 발생 시에도 하지 않는다.
