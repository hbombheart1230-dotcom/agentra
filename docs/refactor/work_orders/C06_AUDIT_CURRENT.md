# C06 — Agentra P1.5 독립 실행·성과 감사 지시서

## 최신 우선 계약 — RF 93개 실제 구조 진척 감사

`rf_details/INDEX.md`/상세설계의 `SOURCE::function→TARGET::function`과 B/A 원격 **실제 변경 Git blob**을 대조. `BODY_MOVED/ORIGINAL_LOC_REDUCED/TARGET_OWNER_EXISTS/TEST_EXIT/PUSH/INTEGRATION`와 `KEEP_OK`/과거 기존 split·test-only를 분리 계량. 93개 문서 존재만으로 93개 함수 설계 완성 주장 금지(미실측 항목은 C03 보강 후 실행). 옳은 KEEP 반복 테스트·첫 PASS 후 개발 중단·문서만 DONE 감사 지적. C06 read-only, 새 delta만 #37.


## FAST-3 감사 우선 (2026-10-29 승인)
- 구 C1~C7·full independent peer·모든 RF -O/전체 hosted CI는 DONE 조건이 아니다. D00 §2의 G1/G2/G3만 검사한다. 기존 7칸 일부 미충족을 이유로 STOP/UNDERUTILIZED 판정을 금지한다.
- 마이그레이션 후 93개 RF 중 FAST-3 실제 변환 수와 신규 G3 DONE 증가를 관측한다. C05가 3칸을 7칸으로 되돌리거나 전체 C4 검증을 재강제하면 시정한다. 속도 중심 평가: 새 원격 코드, 정상 targeted smoke, 신속 통합, DONE, 차단 복구.
- 원격 실제 코드/테스트와 모의투자 상태를 분리 기록하고 실계좌 real 활성화 위험만 별도 차단한다. RunLab 실증은 개발 DONE 후 별도 검증.

**역할:** 독립 읽기 전용 감사관. 원격 정본 integration/p1.5 및 D00_ENGINEERING_DELIVERY_POLICY.md §6 준수. 기존 C01~C05의 Owner·수용·안전 권한을 변경하지 않는다. C06은 코드, RF, STATUS, CI/workflow, 예약, D00/C문서, 운영 런타임에 쓰지 않는다. 감사 의견이 개발/CI/DONE 증거를 대신하지 않는다.

## 매회 시작과 증거
1. 실제 KST START/END가 확인되면 기록하고 추정하지 않는다. 정본 integration HEAD, 본인 이 지시서 blob SHA, 마지막 감사 댓글 ID를 확인한다.
2. 직전 감사 이후의 Issue #11(Claude A), #12(Codex B), #32(RunLab), #36(LEAD), #37(감사 원장) 신규 댓글과 각 실제 A/B/integration/emergency 원격 코드 SHA/경로·CI 결과만 확인한다. 새 사실이 없으면 중복 댓글·문서 쓰기 0.
3. A/B의 ORDER_FILE_BLOB_SHA, ORDER_ID, ITEM_STATUS, 변경된 코드/테스트, normal 및 python -O 실제 exit, 원격 push HEAD/blob, 정확 SOURCE의 반대 peer 범위를 독립 대조한다. LOCAL_IMPLEMENTED·compile·smoke·부분 scoped peer는 full C4나 PUSH_VERIFIED가 아니다.
4. C03의 C01/C02 공급 최신성·작업 누락·권한 준수, C05의 사전 C1~C5 수용·LEAD 승격, C04의 실제 LEAD만 최소 통합/정확 SHA CI, C05 사후 C6/C7/DONE/STATUS를 구분해서 점검한다.
5. C05의 첫 미충족 C와 작업 실제 진전을 우선 평가한다. A/B 실행시간·테스트 개수·커밋량은 보조 지표이며 조기 종료 자체가 위반은 아니다. 환경 pytest 부재, Git 인증/외부 export, 플랫폼 한도와 안전 HOLD는 실제 증거가 있는 영향 부분만 BLOCKED로 인정한다. 나머지 허용 안전 작업이 있었는데 실행하지 않았다면 UNDERUTILIZED로 정확히 기록한다.
6. RunLab의 RUN_SOURCE_SHA가 UNKNOWN이면 runtime 검증은 UNKNOWN/BLOCKED; DEV_RESOLVED·mock unit PASS로 RUNTIME_VERIFIED·실거래 안전을 주장하지 않는다.

## 감사 판정·출력
- 각 대상: PASS / ATTENTION / CORRECTIVE_ACTION / IN_PROGRESS / BLOCKED / UNKNOWN 중 하나. 상태를 특정 담당의 실제 변경 SHA와 최초 미달 계약 C조건에 귀속한다.
- 새 결함만 Issue #37에 한 번: AUDIT_START/END_KST | REVIEW_WINDOW | CANONICAL_SHA | SUBJECT | EVIDENCE_LINK | WHAT_CHANGED | FIRST_UNMET_C | OWNER | REQUIRED_ACTION | NEXT_CHECK. 대상 #11/#12 시정 댓글은 진짜 새 실패가 있을 때만; C03/C04/C05 시정은 #37을 통해 인계. 중복 이슈·루프 생성 금지.
- 정기 감사 기준은 **신규 remote CODE_PUSHED, 양 모드 테스트, full peer C4, CI C6, DONE/C7 증가, BLOCKER 복구**다. 근거 없는 PASS/FAIL·추정 실측시간 금지.
- 기존 D00 §1~§5, protected files, frozen/CI security, broker/UEF/Step5C, 운영 DB·State/주문 등 금지 영역은 변경·재실행하지 않는다.
