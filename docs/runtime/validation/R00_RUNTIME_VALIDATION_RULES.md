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

## 4. 개발팀 인계

**트러블슈팅·STATUS:** 런검증팀은 Issue #32에 신규 증거만 남긴다. 지팀장이 예약 회차마다 [troubleshooting/open](../../refactor/plan/troubleshooting/open/)·[closed](../../refactor/plan/troubleshooting/closed/)를 정리하고 RF·[STATUS](../../refactor/plan/STATUS.md)의 실제 변경만 갱신한다.

런검증팀은 **관측·증거·개선 제안**까지만 한다. RF 생성·판정·큐 이동·Git 통합 금지.

- 안전·중대 이상은 즉시 Issue #32로 알리고 지팀장에게 전달한다.
- 일반 발견은 19시 독립 최종 결과로 묶는다. 코드 문제는 재현 근거와 소유 경로 후보를 제시하되 개발 판정은 지팀장이 한다.
- 환경·예약 복구는 런검증팀이 맡고, 코드 문제만 지팀장이 기존 RF에 연결해 A/B에게 배정한다. 증거 부족은 UNKNOWN으로 유지한다.
