# R00 — Agentra PC 런검증팀 운영 규칙

**시작:** [런검증 CURRENT](CURRENT.md) · **정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**PC:** `C:\AgentraRunLab` · **원본 결과:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)

## 1. 실제 운영 검증

기존 Agentra 운영 PC의 진입점·설정과 대조해 독립 PC에서 Docker, 시장 데이터, LLM, 키움 **모의투자**, Agent 체인, 주문·체결·취소·청산, Reporter/UI, 종료·복구를 관측한다. Probe/fixture만의 PASS는 실런 PASS가 아니다.

- 실행 전 `origin/integration/p1.5` HEAD와 checkout, 실제 **구동 중인 이미지의 소스 SHA**, 모드·설정 출처, 기존 프로세스와 소유권 lock을 확인한다. 이미 구동 중인 이미지를 SHA로 입증하지 못하면 **소스 버전별 런타임 PASS는 UNKNOWN**이다.
- 실데이터·LLM 외부 호출은 허용하되 실제 호출·실패를 구별해 기록한다.
- **실계좌·실주문 금지.** `KIWOOM_MODE=mock`·모의 서버/계좌를 확인한다. `EXECUTION_MODE=real`은 실제 운영 루프일 수 있고 실계좌 허가가 아니다. `ALLOW_REAL_EXECUTION=false` 유지. 모의 계좌 확인이 안 되면 주문만 중단한다.
- 기존 장중 프로세스가 작동 중이면 HEAD 변경만으로 재시작·재배포하지 않는다. 기존 데이터·로그·잠금·프로필을 보존한다. `C:\Agentco`, 개발 A/B 브랜치, 운영 PC 소스·상태 변경 금지.

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

런검증팀은 **관측·증거·개선 제안**까지만 한다. RF 생성·판정·큐 이동·Git 통합 금지.

- 안전·중대 이상은 즉시 Issue #32로 알리고 지팀장에게 전달한다.
- 일반 발견은 19시 독립 최종 결과로 묶는다. 코드 문제는 재현 근거와 소유 경로 후보를 제시하되 개발 판정은 지팀장이 한다.
- 환경·예약 복구는 런검증팀이 맡고, 코드 문제만 지팀장이 기존 RF에 연결해 A/B에게 배정한다. 증거 부족은 UNKNOWN으로 유지한다.
