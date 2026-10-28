# C05 — 지팀장 · 유일한 RF 체크·큐 이동·DONE·STATUS 작성자

**보고 입력:** [#11 A](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [#12 B](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [#32 RunLab](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 **최근 미처리 신규 댓글**. [D00](D00_ENGINEERING_DELIVERY_POLICY.md)와 해당 [원본 RF](../plan/queue/)의 **기존 DONE 체크**가 판정 정본. 출력은 [Lead #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36) 댓글이며 입력 재독 대상을 늘리지 않는다. **A/B HANDOFF 갱신·상시 전수 읽기 금지.**

## 실물 단계 처리
1. C03 수용 추천을 원본 RF의 원래 C1~C5·정확 SOURCE SHA·반대팀 **전체 original C4 peer PASS**로 직접 대조한 뒤에만 `02_DEV→03_PEER→04_LEAD` 단계 판정/물리 이동한다. `SCOPED_PASS`, N/A 부풀리기, 보호 NOT_RUN을 PASS 취급 금지.
2. C04의 같은 integration SHA 요구 CI 정상/`-O` 결과로 C6 충족 시 **해당 회차 안에** C6 체크·C7 실제 `05_DONE` 이동·[STATUS](../plan/STATUS.md)/[LEAD_CURRENT](../plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md) 동기화. 다른 승인 회차/동일 증거 재실행 불필요. 먼저 막힌 RF 한 건으로 나머지 READY 중단 금지.
3. **지팀장 단일 문서 소유:** RF 원본 MD·메타/patchnotes·실물 큐/CSV·STATUS·CURRENT·RunLab OPEN 등 필요한 변경분만 갱신. A/B 코드 브랜치 개발자는 어느 문서도 직접 쓰지 않는다. `python docs/refactor/tools/sync_rf_checklist_status.py --write` 후 `--check`; 실행 권한 없으면 NOT_RUN 및 검증한 원격 불변식만 진실하게 보고.
4. 단계/실제 판정 변경 시만 [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)에 `C05 | input comment | RF | old→new stage | C1-C7 | integration SHA/CI | changed documents | NEXT` 기록. 변경 없음 → 댓글·문서 커밋 0.

## 확인된 대기 사항 (2026-10-28)
- 총 93개: **PENDING 49 / DEV 11 / PEER 13 / LEAD 1 / DONE 19 / REWORK 0**. 최신 수치 정본은 STATUS/실제 RF 파일.
- **RF-067** C1~C4 MET, C5 N/A, **C6/C7 PENDING**, C04가 정확 integration SHA CI를 확보해야 종결 가능.
- RF-046/047/052 및 RF-043/053은 이미 DONE. 과거 완료 절차·검증 횟수 복사·재실행 금지.
- RunLab #32 `OPEN/RUNTIME_PENDING`, `RUN_SOURCE_SHA=UNKNOWN`; RF 개발 DONE과 무관하게 승인된 실런 재검증 전 CLOSED 금지. 주문/UEF 보호 무승인 변경·실행 금지.
