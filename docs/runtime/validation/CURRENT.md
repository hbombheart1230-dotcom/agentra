# Agentra PC 런검증팀 — CURRENT

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**운영:** [R00](R00_RUNTIME_VALIDATION_RULES.md) · **증거:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)
**작업 PC:** `C:\\AgentraRunLab` — 기존 운영 PC·`C:\\Agentco`·개발 브랜치는 변경하지 않는다.

**Codex/Claude 런검증 담당은 매 회차 시작할 때 이 브랜치의 최신 런검증 CURRENT를 먼저 읽고, 여기서 연결한 R00만 필요한 범위로 읽어 실행하라.** 다른 브랜치/로컬 복사본 CURRENT를 지시 정본으로 사용하지 말고, Issue #32에는 신규 사실과 정확한 증거만 보고하라. 이 문서 개정은 예약 생성·실런 재시작을 뜻하지 않는다.

## 핵심 원칙 — Git 개발과 고정 버전 실런 분리

- 개발팀 A/B와 `integration/p1.5`는 계속 커밋·푸시한다. 런검증팀은 **실제로 구동 중인 이미지의 고정 소스 버전**을 관측한다. `RUN_SOURCE_SHA != REMOTE_HEAD`는 정상이며, 최신 HEAD가 바뀔 때마다 Docker를 재빌드·재배포·재시작하지 마라.
- `REMOTE_HEAD`, `CHECKOUT_SHA`, `RUN_IMAGE_DIGEST`, `RUN_SOURCE_SHA`를 따로 기록하라. `RUN_SOURCE_SHA`는 **실행 이미지 digest에 연결된 OCI revision/빌드 기록으로 검증된 경우에만** 값으로 인정한다. checkout SHA를 실행 SHA라고 주장하지 마라.
- 이미지 출처가 입증되지 않으면 `RUN_SOURCE_SHA=UNKNOWN`, 버전별 런타임 검증은 `BLOCKED`. 단, 실제 컨테이너 상태·모의 주문/체결·시장·LLM·Reporter의 **관측 사실은 항목별로 계속 판정**하라. SHA 미입증 자체를 코드 FAIL/REWORK로 분류하지 마라.
- 현재 이미지/State·운영 파일·소유권 lock은 보존하라. 실계좌·실주문, 무승인 소스/안전 계약 수정, 예약 설치/변경, 컨테이너 교체·재배포 금지. OCI revision 라벨은 다음 **승인된** 이미지 빌드에 반영할 개선안으로 제출하라.

## 실행 (평일 KST) — 담당자가 실제 수행할 순서

1. **07:00 Codex — START:** RunLab 등록/예약 활성 여부를 읽기 전용 확인하고 구동 프로세스·중복 소유권·모의투자 모드·실행 이미지 digest 및 증명된 RUN_SOURCE_SHA를 기록하라. 안전한 기존 런타임은 보존한다. 예약이 실행되지 않았으면 `UPSTREAM_NOT_RUN/SCHEDULE_NOT_CONFIGURED`를 기록하고 07시 RUN_ID를 지어내거나 늦게 재실행하지 마라.
2. **09:30 Claude — MORNING:** 실제 존재하는 07시 RUN_ID 및 실행 이미지 증거를 기준으로 시장/LLM/모의 주문을 독립 읽기 전용 관측하라. 07시 증거가 없으면 대체 실행 없이 `UPSTREAM_NOT_RUN`을 명시하라.
3. **17:00 Codex — EOD:** 공식 모의 브로커 주문·체결·취소·잔고 snapshot과 로컬 executor/intent/guard/portfolio/Reporter를 읽기 전용 대조하라. EOD 관측 RUN_ID는 07시 기동 RUN_ID와 구분하라. 새 주문·취소·주문 복구를 만들어 내지 마라.
4. **19:00 Claude — FINAL:** 당일 오전·EOD 증거의 신규 차이만 독립 검증하라. 동일 입력·기존 증거 반복 실행 없이 broker truth ↔ local State/Reporter/metrics 간 불일치를 SOURCE-CODE-REPRODUCED / ENV / SAFETY / UNKNOWN으로 분류하고 Issue #32에 최종 판정과 해제 조건을 제출하라. 코드 RF 판정·배정은 지팀장에게 넘겨라.

## 현재 신규 관측 — 2026-10-26 EOD 기준

- 공식 모의 브로커 15:37:21 KST 보존 snapshot에서 003780 BUY 1주 5,950원(0019354) 및 SELL 1주 5,900원(0020349) **양쪽 체결 확인**; 미체결 주문·잔고 없음. 17시 신규 브로커 조회로 표현하지 마라.
- **미해결:** broker 주문 2건 vs 로컬 1건, SELL 제출 owner UNKNOWN, BUY guard `filled_qty=-1 / remaining_qty=-1` 및 TTL 후 잔류. 원본 DB·State 수정 금지, 계좌 전체 주문 출처를 읽기 전용 조사.
- Reporter `trade_index` 비어 있음/실현 표본 누락, metrics 09:00 스냅샷 stale; 원인이 소스인지 환경/이벤트인지 확정되지 않았으므로 재현 전 코드 REWORK 금지.
- 07시 예약 실행 미입증(`SCHEDULE_NOT_CONFIGURED`), 현재 이미지 `RUN_SOURCE_SHA=UNKNOWN`; 기존 건강한 Docker/UI 관측과 버전별 PASS는 분리. 개발 최신 HEAD와 다르다는 이유로 교체 금지.
- 19:00 담당은 위 사실의 독립 확인과 새 근거만 제출하고, SELL 출처·local↔broker reconcile·Reporter 누락에 대한 정확한 관측 경계 및 다음 소유 RF 후보를 제시하라.

**제출:** `DATE_KST | SLOT | ROLE | RUN_ID | REMOTE_HEAD | CHECKOUT_SHA | RUN_IMAGE_DIGEST | RUN_SOURCE_SHA(or UNKNOWN) | START/EXIT | DOCKER/UI | MARKET/LLM | KIWOOM_PAPER | ORDERS/FILLS/CANCEL | LOCAL_STATE/REPORTER | PASS/FAIL/BLOCKED/NOT_RUN/UNKNOWN | NEW_FINDING | EVIDENCE_PATH | NEXT_ACTION`. 일반 보고는 19시 최종 검증에서 묶어 제출하되 안전·중대 이상은 즉시 Issue #32로 보고. 런검증팀은 RF/큐/개발 브랜치를 변경하지 않는다.
