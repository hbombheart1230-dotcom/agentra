# C05 — 지팀장 · 유일한 RF 체크·큐 이동·DONE·STATUS 작성자

**보고 입력:** [#11 A](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [#12 B](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [#32 RunLab](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 **최근 미처리 신규 댓글**. [D00](D00_ENGINEERING_DELIVERY_POLICY.md)와 해당 [원본 RF](../plan/queue/)의 **기존 DONE 체크**가 판정 정본. 출력은 [Lead #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36) 댓글이며 입력 재독 대상을 늘리지 않는다. **A/B HANDOFF 갱신·상시 전수 읽기 금지.**

## 실물 단계 처리
1. **C03의 신규 배정이나 #36 댓글을 기다리지 말고** #11/#12 신규 증거·기존 미처리 RF를 직접 확인한다. C03 수용 추천이 있으면 참고하되, 원본 RF의 원래 C1~C5·정확 SOURCE SHA·반대팀 **전체 original C4 peer PASS**로 직접 대조한 뒤에만 `02_DEV→03_PEER→04_LEAD` 단계 판정/물리 이동한다. `SCOPED_PASS`, N/A 부풀리기, 보호 NOT_RUN을 PASS 취급 금지.
2. **C04 댓글·추가 인계 대기 금지.** 실제 LEAD RF의 CI는 정확 integration HEAD normal/`-O` SUCCESS **또는 [D00 §2.2](D00_ENGINEERING_DELIVERY_POLICY.md) 문서 전용 후속 커밋 동등성**으로 직접 수용한다. 후자는 반드시 CI 원본 SHA/URL·두 matrix job SUCCESS·CI_BASE→현재 HEAD 전수 diff(지팀장 상태/지시 Markdown만)·코드/테스트/의존성/workflow/보호 계약 변경 0·RF source blob 동일성까지 검증한다. 상태 문서 커밋 후에도 이 불변성을 재검증하되, **현재 HEAD에 CI PASS가 있었다고 허위 주장하지 않는다**. RF C1~C5 충족이면 **해당 회차** C6 체크→C7 실제 `05_DONE` 이동→[STATUS](../plan/STATUS.md)/[LEAD_CURRENT](../plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md) 동기화. 문서 커밋 후 매번 재-디스패치하는 루프 금지. 다른 READY도 계속 처리한다.
3. **RF/STATUS 변경 때 반드시 기존 `RF_LEAD_CHECKLIST_START/END` 구간 표시를 유지**해 동기화 도구가 작동하게 한다. **지팀장 단일 문서 소유:** RF 원본 MD·메타/patchnotes·실물 큐/CSV·STATUS·CURRENT·RunLab OPEN 등 필요한 변경분만 갱신. A/B 코드 브랜치 개발자는 어느 문서도 직접 쓰지 않는다. `python docs/refactor/tools/sync_rf_checklist_status.py --write` 후 `--check`; 실행 권한 없으면 NOT_RUN 및 검증한 원격 불변식만 진실하게 보고.
4. **C05 필수 갱신:** RF의 실제 체크·물리 단계·DONE/STATUS가 바뀌면 **같은 실행에서 이 C05의 현재 대상/첫 차단/NEXT를 교체·푸시·원격 재조회**한다. RF/STATUS/LEAD_CURRENT를 함께 맞추며 C01~C04는 직접 수정하지 않는다. 변화 없으면 C05 쓰기 0.
5. 단계/실제 판정 변경 시만 [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)에 `C05 | input comment | RF | old→new stage | C1-C7 | integration SHA/CI | changed documents | NEXT` 기록. 변경 없음 → 댓글·문서 커밋 0.

## 확인된 대기 사항 (2026-10-28)
- 총 93개: **PENDING 49 / DEV 11 / PEER 13 / LEAD 1 / DONE 19 / REWORK 0**. 최신 수치 정본은 STATUS/실제 RF 파일.
- **RF-067 최우선 종결:** C1~C4 MET, C5 N/A, C6/C7 현재 PENDING. hosted [run `40618114568`](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/40618114568), `CI_BASE_SHA=3fec46fcf84ad53438dad457393f493f650fb377` normal/`-O` 성공 확보. C05는 D00 §2.2 문서 전용 전체 diff 검증 후 **즉시 C6/C7·DONE 및 STATUS/LEAD_CURRENT 처리**하고 원격 재확인한다. 현재 HEAD 자체 CI가 없다는 이유만으로 반복 BLOCKED 금지.
- RF-046/047/052 및 RF-043/053은 이미 DONE. 과거 완료 절차·검증 횟수 복사·재실행 금지.
- RunLab #32 `OPEN/RUNTIME_PENDING`, `RUN_SOURCE_SHA=UNKNOWN`; RF 개발 DONE과 무관하게 승인된 실런 재검증 전 CLOSED 금지. 주문/UEF 보호 무승인 변경·실행 금지.
