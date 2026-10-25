# D04 — Agentra PC 실런 검증팀 운영 규칙

> **PC 런검증팀 단독 실행 계약.** [검증팀 CURRENT](CURRENT.md)만 먼저 읽고 이 문서를 따른다. D00/D01/D02/D03 및 개발팀 CURRENT·RF·HANDOFF를 매 회차 읽지 않는다. 이 문서의 안전·권한 경계는 개발팀 규칙에 의해 완화되지 않는다.

## 1. 목적·역할
- 개인 Agentco **PC의 자원만 사용**해 `C:\AgentraRunLab`에 독립 구성한 Agentra P1.5를 **기존 Agentra 운영 PC와 같은 실제 런타임 경로**로 구동·관측한다. `C:\Agentco`와 개발 A/B 작업장은 변경하지 않는다.
- 대상은 매 실행 확인한 `origin/integration/p1.5`의 **정확한 SHA**다. 기동 전에 로컬 checkout·원격 HEAD·기존 실행 프로세스·설정 출처를 확인하고 기존 데이터와 실행 결과를 보존한다. 운영 PC와 설정 차이가 확인되면 차이를 기록하며, 확인되지 않은 동등성을 PASS로 주장하지 않는다.
- **Codex:** PC 환경·기동·장중 루프·로그·오류/복구 등 런타임 증거 수집. **Claude:** 다른 세션에서 같은 exact-SHA 증거 독립 확인 및 장애 원인 검증. 두 작업자 모두 RF 재배정·DONE·Git 통합 권한이 없다.
- 예약 규칙·실행 분업·GitHub 보고는 아래 **§4**가 정본이다. Codex/Claude **자체 데스크톱 로컬 예약 기능**만 사용하고 Windows 작업 스케줄러·Hermes·Pi·별도 예약 래퍼를 만들지 않는다. **문서 기록 ≠ 로컬 예약 생성/활성화**. 설치·변경 상태는 실제 PC 증거로만 판정한다.

## 2. 실제 운영 동등 실행
- 검증의 기준은 공식 Agentra 운영 진입점·운영 설정·장중 실행 주기·에이전트 체인·보고 및 복구 흐름이다. 수동 `--probe`, `--simulated`, fixture, 로컬 `MockExecutor`의 PASS는 **실제 런 성공을 대체하지 않는다**.
- 기존 운영과 같은 실제 시장 데이터(키움·yfinance·뉴스) 및 실제 LLM API 호출을 허용한다. 외부 네트워크 호출 자체를 결함이나 BLOCKED로 취급하지 않는다. API 장애·지연·비용·fallback은 결과에 기록한다.
- **실제 키움 모의투자(Paper)만 허용:** 키움 모의투자 서버·모의 전용 인증정보·모의 계좌와 기존 운영 정책을 확인한다. 주문 호출 경로는 `EXECUTION_MODE=real`, `KIWOOM_MODE=mock`이며 주문 전송에는 `EXECUTION_ENABLED=true`가 필요할 수 있다. `ALLOW_REAL_EXECUTION=false`를 유지하고, 계좌·엔드포인트를 확인하지 못하면 **주문만 중단**한다. 사용자 승인 없이 안전 가드·주문 한도·승인 로직을 변경하거나 우회하지 않는다.
- `scripts/run_session.py`의 `--mode live`는 **운영 루프 선택**이지 실계좌 허가를 뜻하지 않는다. 실제 실행 명령은 기존 운영 PC의 검증된 실행 방식과 대조해 정하며 임의의 모드/환경변수만으로 동등하다고 가정하지 않는다. Paper 모드 주문·체결·취소·청산, Reporter·UI·재기동 증거를 수집한다.
- **실계좌 연결·실주문 금지.** 실계좌용 키·계좌·API 호스트 또는 허가되지 않은 실거래 경로가 발견되면 중단한다. 유출 위험이 있는 토큰·인증정보를 기록·출력·커밋하지 않는다.

## 3. 격리·결과
- 경로: `C:\AgentraRunLab\src`(소스), `venv`(독립 환경), `config`(PC별 설정), `state`, `logs`, `reports`, `tmp`(보존·격리). 추적되는 Agentra 코드·테스트·CI·안전 설정, Git 원격 브랜치·RF 상태를 임의 수정하지 않는다. **GitHub 전용 런검증 Issue에 증거와 개선 제안을 댓글로 남기는 권한만 예외적으로 허용**한다. Git commit/push 및 Issue를 통한 RF 판정은 금지한다. 런타임이 생성하는 로컬 상태·로그는 허용한다.
- 결과는 `RUN_ID | integration exact SHA | 실행 시각/기동·종료 명령·exit | 운영 모드·모의 서버 확인 | 실제 데이터·LLM | BUY/SELL/CANCEL/체결·NO_ORDER | 로그·state 위치 | PASS/FAIL/BLOCKED/NOT_RUN | 실패 원인·다음 행동` 형식으로 최신 회차 중심 보고한다.
- 정상 구동/외부 호출/모의투자 주문/체결/재시작/종료를 **서로 별도 증거로 판정**한다. 주문이 없는 회차는 NO_ORDER이며, 실제 미검증 단계는 NOT_RUN이다. 신규 회귀와 기존 운영/환경 실패를 분리해 지팀장에게 보고한다.
- 런검증 결과는 P1.5 출시 판단의 독립 증거이나, 개발팀 peer PASS·GitHub exact-SHA CI·RF DONE이나 `main` 병합을 자동 승인하지 않는다. 오류 수정은 지팀장이 승인한 개발 RF 원소유자에게 반환한다.

## 4. 평일 고정 예약 운영·GitHub 증거 루프

- **대상일:** 매주 월~금(Asia/Seoul, KST), **날짜 홀짝·요일에 따른 담당 교대 없이 동일한 4개 예약**을 실행한다. 한국 장 휴장일이면 실제 거래 루프를 강제로 실행하지 않고 `MARKET_CLOSED`/NOT_RUN로 기록한다. 07:00/09:30/17:00/19:00은 **KST 목표 시각**이다. 예약 제품의 지연 실행·PC 절전·앱 종료를 고려해 실행 시 실제 날짜·시간·휴장 여부를 재검사한다.
- **07:00 — Codex / `P15-RUNLAB-START`:** 독립 RunLab checkout에서 `origin/integration/p1.5` fetch/fast-forward 후 **당일 TESTED_SHA와 RUN_ID를 고정**. 기존 실행·소유권 lock·Docker Engine·UI/API·Paper 전용 endpoint/계좌를 확인하고 기존 운영 PC와 동일한 공식 장전/장중 기동 경로를 준비·가동한다. 장전에는 preopen 및 운영 준비만; 장중 시작은 기존 세션 시작 정책을 따른다. 시장시간 가드 강제 우회·미검증 임의 신규 주문 금지. 시작 결과를 댓글로 보고한다.
- **09:30 — Claude / `P15-RUNLAB-MORNING-REVIEW`:** **07:00과 동일한 RUN_ID·TESTED_SHA**의 프로세스/컨테이너·시장데이터·LLM·키움 모의투자·주문/체결·안전 가드·오류를 읽기 전용으로 독립 점검한다. 누락된 선행 실행은 결함으로 꾸미지 않고 `UPSTREAM_NOT_RUN` 또는 BLOCKED로 보고하며, 검증자가 런타임을 새로 띄우지 않는다.
- **17:00 — Codex / `P15-RUNLAB-EOD`:** 당일 07시 이후 전체 실행 로그·중복 주문·보유/청산·미체결/취소·API/LLM 오류·Reporter/UI·state/종료/회복을 점검한다. 당일 코드가 이미 구동 중이면 최신 HEAD가 바뀌어도 **장중 재배포·재시작하지 않는다**. 운영 종료는 기존 EOD 절차대로 하며 증거를 보존한다. 한 번의 EOD 종합 결과를 게시한다.
- **19:00 — Claude / `P15-RUNLAB-FINAL-REVIEW`:** 17시의 당일 증거를 독립 재검토해 `PASS/FAIL/BLOCKED/NOT_RUN`별 확정 범위, 신규 회귀/기존 운영·환경 결함, 개선 제안 및 후속 개발 필요성을 정리해 게시한다. 17시 보고가 없거나 실제 증거가 없으면 전체 PASS 금지. 개선 **제안**은 코드 변경 허가가 아니다.
- **GitHub 기록 정본:** [런검증 전용 Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)에 4개 슬롯의 최신 증거 댓글을 추가한다. `DATE_KST | SLOT | ROLE | RUN_ID | TESTED_SHA | REMOTE_HEAD | START/EXIT | DOCKER/UI | KIWOOM_PAPER | MARKET/LLM | ORDERS/FILLS | REPORTER/STATE | VERDICT | NEW_FINDING | IMPROVEMENT_PROPOSAL | EVIDENCE_PATH | NEXT_ACTION` 형식으로 기록한다. GitHub 게시 불가 시 로컬 보존 후 `GITHUB_POST_NOT_RUN`을 보고한다. 중복 댓글·비밀 값·대용량 원시 로그 업로드 금지. 개발이 필요한 사항은 지팀장에게 전달한다.
- **버전·재시작 안전:** 당일 TESTED_SHA는 고정하고 변경된 원격 HEAD는 별도 기록한다. 다음 유효 예약일에 새 SHA를 가져온다. 동작 중인 런타임·다른 운영 PC 인스턴스와 모의계좌가 겹칠 수 있으면 소유권·중복 주문 위험을 확인하고 안전하게 BLOCKED 처리한다. 앱/PC 절전으로 예약을 놓친 경우 `SCHEDULE_MISSED` 기록만; 장 마감 후 지연 예약이 과거 세션을 재실행하거나 새 주문을 내지 않는다.
- **예약 실현 게이트:** Codex/Claude의 해당 **월~금 PC 설치형 예약 작업 4개**를 별도로 생성하고, 각 프로그램의 활성·로컬 폴더·권한·스케줄·첫 실행 증거를 확인한 뒤에만 `SCHEDULE_ACTIVE` 판정. 자동화 미설치·미검증은 `SCHEDULE_NOT_CONFIGURED`. 설치·수정은 사용자 별도 승인 범위만 수행한다.
