# D04 — RunLab #32 → Agentra P1.5 개발/지팀장 인계

**정본:** [R00](R00_RUNTIME_VALIDATION_RULES.md) · [런검증 CURRENT](CURRENT.md) · [D00](../../refactor/work_orders/D00_ENGINEERING_DELIVERY_POLICY.md). **외부 입력은 Issue [#11](https://github.com/hbombheart1230-dotcom/agentra/issues/11) (Claude A), [#12](https://github.com/hbombheart1230-dotcom/agentra/issues/12) (Codex B), [#32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) (RunLab)의 신규 댓글 3곳만**. 지팀장 판정 출력은 [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36).

## 신규 런 사건 처리
1. RunLab 작업자는 새 관측만 **#32 댓글**에 기록: 실제 RUN_ID·`RUN_IMAGE_DIGEST`·증명된 `RUN_SOURCE_SHA` 또는 UNKNOWN, 주문/수락/체결/취소/잔고 vs 로컬 event/guard/Reporter 구분, 증거 경로, 신규 증상과 추정/증명 정도. 안전 심각도 높으면 즉시, 나머지 일일 최종 검증 시. **RunLab은 OPEN/MD/RF/STATUS 수정 금지**.
2. 지팀장 C03이 #32의 새 댓글 ID를 기존 [RUNLAB32 OPEN 사건 대장](../../refactor/plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md)과 중복 대조한 후 **실제 신규 발견/상태 변화만** 접수한다. 인계는 `RL32-ORDER/GUARD/REPORT/IMAGE` 등 정확한 범위로 분리하고, 원래 RF 소유자가 확인될 때만 Owner에게 맡긴다. `FILE_OWNER`와 코드 결함 원인은 동의어가 아니다. 미확정 `OWNER_MAPPING_PENDING`.
3. 개발 소스 원인 재현/최소 코딩은 A 또는 B **본인 작업 브랜치**에서만; 독립 peer는 상대팀. **개발자는 코드·테스트만 수정**, 결과는 각각 **#11·#12 댓글**로 보고. 원본 RF·접수대장·문서/patchnotes·상태·통합은 지팀장 전담.
4. 코드 소스가 원인임이 증명된 경우 [D00](../../refactor/work_orders/D00_ENGINEERING_DELIVERY_POLICY.md) 원래 RF 계약을 적용하고 지팀장 C04만 최소 통합/필수 CI, C05만 RF 체크/DONE/STATUS. 환경/OCI/예약/운영 문제는 RunLab 읽기 전용 조사; 컨테이너·운영 설정·주문/취소/재배포·예약 변경은 사용자 명시 승인 전 BLOCKED.
5. 사건 종료는 별개: `DEV_RESOLVED`는 승인된 소스 근거·CI, `RUNTIME_VERIFIED`는 승인 적용된 **실제 이미지 digest↔source SHA**와 해당 증상의 독립 재관측. 양 조건 전 코드 사건은 `OPEN/RUNTIME_PENDING`; 보호 승인 없이 CLOSED 주장 금지.

**현재:** RunLab #32 주문 SELL provenance, local↔broker/guard, Reporter, OCI 귀속 증거는 최초 사건 대장 및 최신 #32 댓글에서만 확인한다. 오래된 C00·A/B HANDOFF·일일 기록 표를 계속 복사하지 않는다. RunLab 공통 `RUN_SOURCE_SHA=UNKNOWN`을 전면 코드 REWORK 또는 재배포 명령으로 해석하지 않는다.

**안전:** 실계좌/실주문·운영 데이터 수정·보호 UEF/Executor/Broker/Supervisor 규칙 변경·모의 주문을 이용한 사후 조작 금지. 새로운 실행 허용 권한을 이 문서에서 만들지 않는다.
