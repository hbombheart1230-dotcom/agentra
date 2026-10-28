# RunLab CURRENT — 관측 실행 / Issue #32 댓글 보고

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`. **실행·보호:** [R00](R00_RUNTIME_VALIDATION_RULES.md); **개발 인계:** [D04](D04_RUNTIME_VALIDATION_RULES.md). **실제 결과 보고: [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 댓글 한 곳만**. 지팀장은 #11·#12·#32의 최신 증거를 확인하며, RunLab은 RF 문서·OPEN 대장·개발 브랜치·STATUS를 수정하지 않는다. **모든 운영/규칙 문서 수정은 지팀장만** 수행한다.

## 평일 KST 역할 (새 예약을 만드는 지시 아님)
- **07:00 Codex START:** 기존 등록된 로컬 예약이 실제 동작했는지, 컨테이너/모의 서버/잠금, 이미지 digest·출처 확인. 07시 실행이 없으면 `UPSTREAM_NOT_RUN` / `SCHEDULE_NOT_CONFIGURED`; 과거 런을 뒤늦게 기동하지 않는다.
- **09:30 Claude MORNING:** 실제 07시 RUN_ID와 증거 기준 독립 읽기 전용 관측. 없는 실행을 PASS로 만들지 않는다.
- **17:00 Codex EOD:** 보존된 모의 브로커 주문·수락/체결/취소/잔고와 로컬 event/guard/Reporter를 읽기 전용 대조. 새 주문·취소/복구 금지.
- **19:00 Claude FINAL:** 같은 RUN_ID·이미지 출처에 대해 당일 신규 차이 독립 검토; #32 댓글에는 **새 사실**만 기록하고 기존 댓글은 링크로 재사용.

## 버전 귀속·안전
`REMOTE_HEAD`, `CHECKOUT_SHA`, `RUN_IMAGE_DIGEST`, `RUN_SOURCE_SHA`는 별개의 값이다. 구동 이미지 digest→OCI/빌드 provenance로 연결되지 않으면 **`RUN_SOURCE_SHA=UNKNOWN`** 및 버전별 검증 BLOCKED; Docker/모의 브로커 관측 사실 자체는 계속 구분·보존. 새 개발 HEAD와 다르다는 이유로 기존 건강한 런타임 이미지/프로세스·State·예약 변경 금지. `C:\AgentraRunLab` 관측용; `C:\Agentco`/실계좌·실주문/보호 계약·운영 DB·Docker 재배포·새 스케줄 무승인 변경 금지. R00 안전/소유권 계약 우선.

## 현재 사건의 연결
**정본 이슈:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32), **지팀장 인계:** [D04](D04_RUNTIME_VALIDATION_RULES.md) 및 [RUNLAB32 OPEN](../../refactor/plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md). SELL 제출 owner/모의 체결 vs 로컬 이벤트/Guard/Reporter 불일치와 OCI 출처 UNKNOWN은 원인 확정 전 `OPEN/RUNTIME_PENDING`이다. RF 코드 DONE과 실런 CLOSED를 혼용 금지; 보호 경계는 별도 승인 전 읽기 전용.

**Issue 댓글 포맷:** `KST_DATE/SLOT | RUN_ID(실제) | REMOTE_HEAD | CHECKOUT_SHA | RUN_IMAGE_DIGEST | RUN_SOURCE_SHA/UNKNOWN | START/EXIT | MOCK orders accepted/filled/cancelled | LOCAL_STATE/REPORTER | PASS/FAIL/BLOCKED/NOT_RUN | NEW_FINDING | EVIDENCE_PATH | NEXT`. 비밀/계좌 개인정보는 절대 기록하지 않는다.
