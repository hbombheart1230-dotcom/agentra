# R00 — Agentra PC 런검증팀 운영 규칙

**시작:** [런검증 CURRENT](CURRENT.md) · **정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**PC:** `C:\AgentraRunLab` · **원본 결과:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)

## 1. 실제 운영 검증

기존 Agentra 운영 PC의 진입점·설정과 대조해 독립 PC에서 Docker, 시장 데이터, LLM, 키움 **모의투자**, Agent 체인, 주문·체결·취소·청산, Reporter/UI, 종료·복구를 관측한다. Probe/fixture만의 PASS는 실런 PASS가 아니다.

- 실행 전 `origin/integration/p1.5` HEAD와 checkout, 실제 **구동 중인 이미지의 소스 SHA**, 모드·설정 출처, 기존 프로세스와 소유권 lock을 확인한다. 이미 구동 중인 이미지를 SHA로 입증하지 못하면 **소스 버전별 런타임 PASS는 UNKNOWN**이다.
- 실데이터·LLM 외부 호출은 허용하되 실제 호출·실패를 구별해 기록한다.
- **실계좌·실주문 금지.** `KIWOOM_MODE=mock`·모의 서버/계좌를 확인한다. `EXECUTION_MODE=real`은 실제 운영 루프일 수 있고 실계좌 허가가 아니다. `ALLOW_REAL_EXECUTION=false` 유지. 모의 계좌 확인이 안 되면 주문만 중단한다.
- 기존 장중 프로세스가 작동 중이면 HEAD 변경만으로 재시작·재배포하지 않는다. 기존 데이터·로그·잠금·프로필을 보존한다. `C:\Agentco`, 개발 A/B 브랜치, 운영 PC 소스·상태 변경 금지.

### 실행 이미지 SHA와 개발 HEAD를 분리하라

- 매 회차 `REMOTE_HEAD`(조회 당시 원격 integration HEAD), `CHECKOUT_SHA`(RunLab 로컬 소스), `RUN_IMAGE_DIGEST`(구동 컨테이너 이미지), `RUN_SOURCE_SHA`(해당 이미지에 실제 포함된 소스)를 **서로 다른 필드**로 기록하라. 예약 07:00 실행이 없으면 `UPSTREAM_NOT_RUN`으로 남기고 EOD 관측 RUN_ID를 07시 RUN_ID로 대체하지 마라.
- 개발 A/B 및 integration의 커밋·푸시는 계속 허용된다. `RUN_SOURCE_SHA != REMOTE_HEAD`는 **정상적인 고정 버전 실런**이며 결함, 코드 REWORK, 재빌드/재배포 사유가 아니다. 원격 HEAD는 조회값으로만 기록하고 하루 동안 실행 중인 Docker를 HEAD 변경에 맞춰 자동 교체하지 마라.
- 구동 이미지의 `RUN_SOURCE_SHA`는 해당 **실행 이미지 digest와 연결되는** OCI revision 라벨 또는 검증 가능한 빌드 provenance/manifest로 입증하라. 로컬 checkout SHA, 마지막 검증 SHA, 최신 Git HEAD, 이미지 생성 시간으로 실행 소스 SHA를 추정·대체하지 마라.
- 소스 귀속이 불가능하면 `RUN_SOURCE_SHA=UNKNOWN`, `VERSION_SCOPED_PASS=BLOCKED`로 기록하되, Docker/API 상태·시장/LLM 관측·공식 모의 브로커 체결 사실은 **관측 항목별 PASS/FAIL/UNKNOWN**으로 그대로 보존하라. SHA 미입증만으로 기존 실런 전체를 FAIL로 뒤집지 마라.
- 새로운 OCI revision 표기는 **차기 승인된 빌드**에 반영할 개선안이다. 지금 실행 중인 이미지·프로세스·DB/State·예약을 라벨 보강이나 HEAD 동기화 목적으로 무승인 변경하지 마라. 주문/SELL owner/Guard/Reporter 불일치는 공식 브로커 증거와 로컬 이벤트를 읽기 전용으로 대조하고 코드 결함 재현은 지팀장이 소유 RF에 배정한다.

## 2. 실행 담당·시간 (평일 KST)

| 시각 | 담당 | 기존 예약명·작업 |
|---|---|---|
| 07:00 | Codex | `P15-RUNLAB-START` — RunLab 기동·RUN_ID·대상 SHA 기록 |
| 09:30 | Claude | `P15-RUNLAB-MORNING-REVIEW` — 같은 RUN_ID의 장초반 read-only 검증 |
| 17:00 | Codex | `P15-RUNLAB-EOD` — 당일 주문·체결·취소·종료/복구 종합 |
| 19:00 | Claude | `P15-RUNLAB-FINAL-REVIEW` — 당일 독립 최종 검증·지팀장 전달 |

- 월~금 고정, 역할 교대 없음. 휴장·누락 예약은 `MARKET_CLOSED`·`SCHEDULE_MISSED`/NOT_RUN. 늦게 깬 실행이 과거 거래를 재실행하거나 주문해서는 안 된다.
- 당일 RUN_ID·TESTED_SHA를 유지하고 원격 HEAD 변경은 별도 기록한다. 07/17시 실행 증거가 없으면 검증자는 없는 실행을 PASS로 꾸미거나 런타임을 대신 재기동하지 않는다.
- Codex/Claude **PC 자체 로컬 예약**만 사용한다. 일정 설치·변경은 사용자 승인 후 실제 활성 상태를 확인한다. 문서 기록은 예약 생성 증거가 아니다.

## 3. 증거와 오류 처리

로컬 `C:\AgentraRunLab`의 `reports`·`logs`·`state`에 원본을 보존하고 [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)에 **새 결과만** 남긴다.

`날짜/슬롯 | RUN_ID | 실제 구동 SHA 또는 UNKNOWN | 실행·exit | 시장/LLM | PAPER 주문·체결·취소·NO_ORDER | PASS/FAIL/BLOCKED/NOT_RUN/UNKNOWN | 신규 증상 | 증거 위치 | 다음 행동`

주문 수락은 체결 입증이 아니다. 거래 중복·미체결/취소·TTL·가드 상태를 구분한다. 기존 발견은 댓글 링크만 참조한다. 장애는 원인 확인 → 허용 범위 복구 → 결과 확인; 안전·운영 차단은 우회하지 않는다. 키·토큰·계좌 식별정보 기록 금지.

**문서 단일 작성자:** RunLab 담당자는 R00/D04/CURRENT·RF·STATUS·사건 대장을 수정하지 않는다. 관측 결과는 **Issue #32 댓글만** 제출한다. 세 개발·런 Issue(#11/#12/#32)의 신규 사실은 지팀장이 인수하고, 지팀장 판정 출력은 [Issue #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)에 기록한다. 예약/운영 변경 권한은 이전과 동일하며 이 항목이 새 실행 승인을 뜻하지 않는다.

## 4. 개발팀 인계 — D04 공통 작업

**RunLab → 지팀장 → 개발 A/B → 독립 검증 → 승인된 런검증 재확인**의 정본은 [D04](D04_RUNTIME_VALIDATION_RULES.md), 개발측 [D00](../../refactor/work_orders/D00_ENGINEERING_DELIVERY_POLICY.md)·[C03 지팀장 배정](../../refactor/work_orders/C03_LEAD_TRIAGE_CURRENT.md)이다.

- 런검증팀은 [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)에 **신규 사실·원본 증거 위치·RUN_IMAGE_DIGEST와 입증된 RUN_SOURCE_SHA(또는 UNKNOWN)·모의 브로커/로컬 불일치·다음 확인 범위**만 기록한다. **중대한 주문/안전 이상은 즉시**, 일반 발견은 19시 최종 독립 검증과 함께 제출한다.
- 지팀장이 **새로운 발견이 있는 회차에만** [troubleshooting/open](../../refactor/plan/troubleshooting/open/)에서 중복을 확인하고 사건을 접수한다. **C03에서 사건 ID·임시 조사 담당·정확한 원래 RF 후보 및 다음 증거를 배정**, RF 소유 미확정은 `OWNER_MAPPING_PENDING`으로 유지한다. 기존 사건의 새 관측은 delta만 추가하고 매회 과거 증거 재점검은 하지 않는다.
- 환경·예약·OCI 출처는 **RunLab 읽기 전용 조사**. 코드 경계는 지팀장이 **원래 RF 소유자**에 배정, 상대 개발자가 독립 peer한다. RunLab은 코드 수정·RF 큐 이동·통합·DONE을 수행하지 않는다.
- **개발 RF DONE은 런타임 증상 CLOSED가 아니다.** RunLab은 사용자 승인 하 적용된 고정 이미지의 provenance와 실제 증상 재관측을 확인할 때만 `RUNTIME_VERIFIED`를 제출한다. 적용 승인이 없다면 `RUNTIME_PENDING/OPEN`; RunLab에서 임의 주문·재배포·예약 수정을 하지 않는다.
- **현재 공동 OPEN:** [RunLab #32 사건 대장](../../refactor/plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md). ORDER/GUARD는 개발 Codex B의 소스 조사, REPORT는 개발 Claude A의 소스 조사, IMAGE/OPS는 RunLab 관측, 소유 RF 확정과 최종 우선순위는 지팀장이 맡는다. 보호/운영 변경은 승인 전 금지.
