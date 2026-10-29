# C03 — 지팀장 | 구체 실행 설계·A/B 연속 작업 공급

## A/B 단일 문서 완결 필수 (2026-10-29, 이전 지시보다 우선)

**C03만** `docs/refactor/plan/rf_details/RF-xxx_IMPLEMENTATION.md`, INDEX, T00~T09, RF 원본, 원격 소스코드를 읽어 설계 판단한다. 매시 배정할 때 C01/C02의 인라인 큐를 **직접 수정·푸시**하여 각 개발자에게 4~6개 이상의 독립 실제 코드 MOVE 아이템을 공급한다. 작성 형식은 `RF | SOURCE_PATH::원함수 | TARGET_PATH::새함수 | 실제 이동할 본문/효과 보존 | 기존 wrapper/patch seam | targeted normal fixture/검증 | BLOCKED시 다음 ITEM`. KEEP_OK 항목에는 `경로 | 한줄 이유 | blob`만 넣는다. 두 개발자가 다른 문서를 열어 추가 맥락을 수집하도록 지시하지 않는다. **C01/C02 한 파일에 모든 작업 정보를 인라인 포함**, 파일 경로는 오직 실제 수정할 code/test 경로로만 제시한다. 이전의 index/RF 참조형 handoff와 충돌하면 이 절이 우선. 기존 C01/C02 항목의 이미 완료된 내용은 확인 후 제거하고 원격 commit SHA와 #36에 변경 큐만 보고한다. 원본 93개 전수 재독 금지, 신규 변화만 갱신.


## 최신 우선 계약 — 93개 RF 상세설계 기반 다중 개발 배정

`docs/refactor/plan/rf_details/INDEX.md`의 93개 상세설계와 각 RF SOURCE→TARGET, 독점 A/B 배정이 정본. 위 D00 2026-10-29 절 우선; 아래의 C01/C02 1~2개만 배정, KEEP-only 최대한 DONE으로 보낸다는 옛 지시는 이 절과 충돌 시 무효. **A/B 각 4~6개 이상의 실제 독립 함수 이동 item**을 C01/C02에 유지하고 1개 완료시 재보충. 다른 RF가 소유한 목적지 경로는 같은 Actor라도 새 Owner 계약/CSV 반영 근거가 있어야 한다. **함수명·목표 Owner가 미분석인 RF는 실제 원본을 열어 코드 분석 후 해당 RF 상세설계를 먼저 채워** A/B에 넘긴다. 이미 옳은 KEEP은 한 줄+blob으로 즉시 끝내고 다시 요구하지 않는다. 진짜 cloud push/pytest 장애만 복구; 긴급 별도 개발 트랙 계획 금지.


## STRUCTURAL-REALITY — 2026-10-29 홍사장 시정 지시: 실제 리팩터링과 KEEP 검증 분리
- **개발 DONE은 D00 §2 FAST-3 그대로 보존한다.** 그러나 C03/C05가 보고하는 구조 개선 실적은 `REFACTOR_CHANGED`(실제 모듈 책임 이동/함수 몸체 추출/의존성 감소), `KEEP_VERIFIED_ONLY`(대상 소스 변화 없이 동작·기존 구조 검증), `ALREADY_SPLIT_BEFORE_BASE`(main→P1.5 기준점 이전 분리)를 반드시 구별한다. **KEEP을 코드 구조 개선 건수·LOC 감소 실적에 더하지 말 것**. 실제 기준점은 main SHA·P1.5 baseline SHA·integration HEAD를 구분해 병기; 1개 RF의 성공을 다른 단계의 공으로 중복 집계 금지.
- **검증된 실측(2026-10-29):** main `058a6403` 대비 integration 시점의 `graphs/nodes/strategist_node.py` 422309→194854B, `apps/operator_ui/data_access_core.py` 358998→112756B, `libs/reporting/trade_report_ai.py` 440032→64646B, `libs/reporting/reporter_analysis.py` 93941→28062B. 이는 파일 크기 감소를 뜻하지 P1.5 **중간 baseline 이후** 이 분해를 새로 했다는 의미가 아님. 21 DONE RF의 소유 총 431경로 중 426개는 baseline `63182ab2`→integration `671306d0` Git blob 동일, 5개 상이; main에서 160경로 미존재. **기존 DONE 21/93은 역사 사실로 유지**, 그러나 '중간 baseline부터 실제 코드 개선 19 RF'로 주장 금지.
- **이번 최우선 실제 구조 변경:** Claude A RF-031 `libs/reporting/reporter_ai_review.py`의 `_build_compact_input` 약 110줄 + `_build_messages` 약 44줄을 같은 독점 패턴의 `libs/reporting/reporter_ai_review_input.py`(C03 책임 지정 승인)로 이동. 공개 `_build_*()` facade·use-time monkeypatch·output byte parity를 유지하고 새 단일 RF-031 테스트를 작성. 상세 고정 실행 계약은 **최신 C02**. **새 source 모듈+원본 source 각 Git blob 변화/140줄 이상 원본 LOC 순감/관련 정상 테스트 exit0/원격 A push**가 인수 조건; test-only·KEEP-only는 이 구조 개선 과제 실패.
- **다음 실질 구조 부채:** RF-008은 기존 FAST-3 DONE을 유지하되 긴급 `069dadd5`에서 **새 구조 변경 1건**이 확인됐다: `graphs/nodes/strategist_node.py` reporter-feedback 정책 함수 몸체를 `graphs/nodes/strategist_reporter_feedback.py`로 추출(원본 215줄 삭제·3줄 추가, 새 Owner 234줄, facade 3,628 LOC). 통합 `893ba9ba`~`afbfa33f`에 **3 source/test blob 모두 동일하게 이미 반영**됐다. 기존 DONE/KEEP 검증과 **이번 신규 구조 변경은 별도** 집계; 해당 새 테스트의 정상 exit 및 C05의 변경 범위 G2/G3 재확인은 아직 미확인이다. 실제 실패가 확인되지 않았으므로 C05의 무근거 REWORK 이동 금지. RF-044의 `libs/contracts/agent_outputs.py` 약 105KB도 후보이나 B push·pytest 환경 동시 차단 상태이므로 새 local-only 구현을 쌓지 않는다.
- **C03 실행 순서:** 안전한 실제 추출·기능 개선을 먼저 배정하고, 코드 변경 0인 검증은 소비자 보호에 의미가 있을 때만 DONE으로 인계. 매회 `MAIN_BASE_HEAD | OWNER_FILES_CHANGED | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | TEST_EXIT | DONE_TYPE`를 간결하게 판단한다. 전체 안전·상태·D00 변경 및 real mode 허가는 기존대로 금지.

## FAST-3 최우선 운영 (2026-10-29 홍사장 속도 지시)
- D00 §2 FAST-3가 이 문서 내 과거 C1~C7/전체 Owner C4/매-RF normal -O/hosted 전체 CI/30분 업무량 강제 규칙보다 우선한다. RF 개발 DONE의 필수는 **G1 소스·Owner**, **G2 변경 부분 테스트 1회**, **G3 최소 통합·상태 반영**뿐. 원래 RF 7개는 이력 자료.
- A/B에게는 1~3개 실질적으로 가장 빠르게 끝낼 수 있는 코드/호환 수정만 먼저 지정하고, 기존 4~6 패키지+full peer 목록을 무조건 모두 처리하게 강제하지 않는다. 이전 C01/C02의 7번 등 동결/상대 전수 peer를 개발 DONE의 BLOCKER로 재전달 금지.
- 변경 없는 KEEP 파일·기존 정상 실행 증거를 최대한 재사용하고, 기능에 직접 영향을 주는 단일 실패/테스트에 집중한다. 상대팀 독립 probe는 선택적인 병렬 검토이고 완료 선행 조건이 아니다. 실제 mock/paper 런검증은 P1.5 개발 DONE 후 별도 수행.
- **현재 최우선:** **A는 RF-031의 실제 코드 추출(상단 STRUCTURAL-REALITY/C02 계약)을 먼저** 완료하고, C04/C05는 A가 이미 완료·푸시한 RF-051/054/058 G1/G2를 별도 병렬로 인수해 G3/DONE 처리한다. RF-016은 이미 05_DONE(21/93), 재인계·동일 94건 재실행 금지. 기존 RF-014/015 KEEP 검증은 코드 구조개선 실적으로 세지 않는다. real mode 금지.
- 문서와 STATUS의 옛 7칸 텍스트를 새로운 필수 요구로 재해석하지 않는다. C05가 migrate_rf_fast3.py --write 및 sync_rf_checklist_status.py --write/--check를 인수하도록 #36에 지시한다.

**핵심 원칙:** 지팀장이 코드·아키텍처·RF 계약·소유권·안전·독립 검증을 모두 판단한다. Codex B는 C01, Claude A는 C02 **단 한 개의 이번 회차 작업 명령서**만 읽고 이전 채팅 문맥 없이 그대로 구현한다. A/B에게 프로젝트 상황 파악, 큐·RF·D00·CURRENT 재독, '무엇을 할지 알아서 결정', 과거 PASS 반복을 맡기지 않는다. 이 문서와 D00은 지팀장용이다. C04(선별 통합/CI)와 C05(최종 수용/DONE/STATUS)는 예약과 역할을 유지한다.

## 매회 지팀장이 직접 수행할 일

### 1. 입력·진도 판단 (반복 조사 최소화)
- `integration/p1.5` 최신 원격 HEAD, Issue #11(A)·#12(B)·#32(RunLab)의 **최근 신규 결과**, A/B 브랜치의 실제 SOURCE SHA 및 변경 코드·테스트만 확인한다. 신규 결과가 없다면 진행 중인 지시의 미완료 번호와 실제 중단점만 확인하고 이전 코드·PASS 전체를 매번 재독하지 않는다.
- C01/C02 **명령 번호별** 완료(정확 변경 파일/원격 SHA와 양 모드 증거 존재)·진행·차단·미수행을 판정한다. 테스트 PASS만으로 소스 변경 완료라고 판정하지 않는다. 작업이 실제로 수행됐는지 diff/LOC/caller 연결까지 확인한다.

### 1.1 직접 원격 RF 큐 스냅샷·ACTIVE/차단 관리 (C03 단독 책임)

- **책임 정합화:** D00 §1.1에 따라 **C03/C05만** RF 원본·큐를 탐색한다. C03은 원격 `integration/p1.5`의 단일 SHA를 먼저 고정하여 `QUEUE_SCAN_SHA`로 기록하고, `docs/refactor/plan/queue/{01_PENDING,02_DEVELOPING,03_PEER_REVIEW,05_DONE,06_REWORK}/{CLAUDE_A,CODEX_B}/` **10개 폴더의 RF Markdown 파일 경로만** 열거한다(비어 있는 폴더는 0). 추가 `UNASSIGNED`·`04_LEAD_ACCEPTANCE`도 지팀장이 별도 집계한다. 유일 RF ID·중복·실제 단계/소유자·CLAIM 여부·원본 첫 미충족 C1~C5를 대조한다. **A/B에게 QUEUE_SCAN_SHA, 폴더 열거, RF/D00 독해를 요구하거나 C01/C02에 스캔 지시를 삽입하지 않는다.** A/B는 파일·함수·격리 명령이 완결된 개별 작업 명령서만 수행한다.
- **현재 고정 큐 스냅샷:** `QUEUE_SCAN_SHA=88152c15ba4f0ada74bdecde20d3d71a7e4c2a02` (2026-10-29 21:46 KST HEAD 조회), 93 unique: PENDING47, DEV10, PEER10, LEAD3, DONE23, REWORK0. A DEV `021/040/061`(3), PEER `014/015/031/032/033/034/041/050`(8), LEAD `051/054/058`(3), DONE11; B DEV `044/045/063/065/066/070/071`(7), PEER `018/069`(2), DONE12. PENDING `030/035`은 CLAIM 전 read-only. 이 스냅샷은 C03의 **읽기 전용 상태 인덱스**이며 C05만 큐/STATUS를 수정한다.
- **ACTIVE/차단:** B RF-045의 `libs/core/event_logger_compat.py::_NodeEventLogger.__getattr__`는 정확 B `617c8429`에 A #11 `6495308964` copy/deepcopy 각각 RecursionError(정상/-O 2 FAIL+2 PASS), **B 새 안전 코드 결함**. B `pytest` 부재 + 승인 owner-branch push 인증 실패가 동시 지속(#12 `6495081990`), 원격 소스 0 → C01은 승인 push/테스트 환경 복구 시 최소 수정+stdlib unittest, 그전 새 로컬-only 커밋 금지. RF-045 로그 이동 symlink/TOCTOU·RF-066 비임시 apply는 SAFETY_HOLD, B RF-069 UEF snapshot은 승인 전 BLOCKED. A RF-021 보호 exit, RF-032 validation-id 정책은 C05/안전 담당 해제 전 HOLD. 다른 안전 KEEP/테스트는 계속.
- **D00 §6 인수·재개:** A/B는 시작 원격 `CANONICAL_HEAD`, `ORDER_FILE_BLOB_SHA`, `OWNER_REMOTE_SHA`, 번호별 `ORDER_ID`를 고정하고 도중 새 발행을 소급 실패 처리하지 않는다. pytest 부재는 G2에 사용 가능한 stdlib smoke와 구분, 인증 실패는 PUSH만 BLOCKED; 로컬 commit은 G1 아님. C03은 C01/C02만 발행하고 C04 통합·targeted smoke, C05 G1/G2/G3·DONE/STATUS 판정에 정확 SHA를 인계한다. 과거 full peer/모든 -O/hosted 전체 CI는 필수 아님.
- **신규 delta/인계 (22:00 KST):** #11 최신 `6495308964`, #12 `6495081990`, #32 `6493735258` 뒤 **새 댓글 0**. A 원격 `bed173058613ad97f830001771d0bd7b3c191f30`, B 원격 `617c8429c69c98ac6f707a820d0e6825766f8642` **변화 0**. 긴급 `73731c8e→069dadd5`는 새 RF-008 실구현: `strategist_node.py` -215/+3, 새 `strategist_reporter_feedback.py` +234, 새 `test_rf008_strategist_reporter_feedback_split.py` +117. blob 각각 `0f6cda31/ef9e00ee/4b8da6dd`가 통합 `88152c15`과 동일, 원래 RF-008은 이미 DONE; **새 변경의 G1 통합 소스 VERIFIED, G2 정상 exit NOT_VERIFIED, C05 변경 범위 G3 재판정 필요**. C04는 integration exact SHA에서 `python -m unittest discover -s tests -p 'test_rf008_strategist_reporter_feedback_split.py' -v` 정상 exit0 또는 기존 동일 소스 성공 증거를 확인하고 C05에 인계. C03은 C04/C05 코드/문서/STATUS를 쓰지 않는다. RF-051/054/058은 LEAD 3건으로 C04 최소 통합·targeted smoke→C05 DONE 대기(동일 증거 반복 금지).
- **A 다음 실행 (C02 유지):** RF-031 `libs/reporting/reporter_ai_review.py` A 원격 blob `a8c2507f` **500 LOC**. `_build_compact_input` 110줄+`_build_messages` 44줄 실제 이동을 지시한 C02 blob `a7207c3a` 유효. 새 `reporter_ai_review_input.py` A 원격 404, AFTER_LOC/신규 owner blob/정상 exit/푸시 **모두 NOT_VERIFIED**. KEEP/기준점 전 분리/테스트-only를 실제 구조 실적으로 세지 않는다. A는 facade wrapper/호출시점 monkeypatch parity와 새 Owner/targeted normal exit0를 제출한 뒤 본인 브랜치 정상 push·blob 검증; C04/C05 G1/G2 인계.
- **B 다음 실행 (C01 유지):** RF-045 `libs/core/event_logger_compat.py::_NodeEventLogger.__getattr__`에서 copy/deepcopy RecursionError 2건(A #11 `6495308964`)을 막는 `self.__dict__.get("_logger")` 기반 AttributeError 방어와 `tests/test_p15_event_logger_copy_guard.py` stdlib unittest normal exit0를 요구. C01 blob `1b3bc67f`에 함수·fixture·명령·푸시/차단 재개점이 이미 정확히 기재돼 있다. B 원격 신규 코드 0, 로컬 `2055bc6f`는 pytest 부재 및 Git 인증/승인 push 차단으로 **원격 G1/G2 미충족**. 승인 경로 복구 전 로컬-only 새 커밋 금지, 실제 안전 작업/환경 차단을 분리한다.
- **RunLab:** #32 신규 delta 0, `RUN_SOURCE_SHA=UNKNOWN`과 health timeout·과거 ORDER/GUARD/REPORT 불일치 지속. 실행 이미지 SHA 회귀 귀속 불가, 운영 재시작·실주문·비격리 apply 금지.
- **경로/시각 충돌 처리:** `QUEUE_SCAN_SHA`는 이 스냅샷의 **조회 원격 commit SHA**이지 A/B 자신의 스캔 실적이나 C04 CI SHA가 아니다. 문서만 순차 반영한 후에는 RF 경로가 바뀌지 않았는지 HEAD에서 재확인한다. 실제 새 큐 stage/CLAIM이 발견되면 새 원격 SHA에서 다시 산정한다. 이 지시의 변경을 A/B 개발 완료로 세지 않는다.

### 1.2 감사 시정 제안·실측시간 근거 판정 (이번 회차 추가)

- #11/#12의 `[C06_AUDIT_ACTION]`은 **외부 신규 입력이 아닌 그 이슈 내 시정 제안**으로만 접수한다. C06 #37을 직접 필수 입력으로 열지 않는다. 원격 D00/소스/댓글로 교차 확인한 사실만 반영하고, 감사 댓글을 구현·검증 완료로 세지 않는다.
- #12 `6489972722`의 지적대로 이전 C03의 **B 개발 브랜치 직접 코드·테스트 푸시**에 대한 D00 §1.1 예외 승인 원본·정확 범위는 독립 입증되지 않았다. **추가 타인 브랜치 코드 쓰기 중지, 이미 적용된 보안 containment 보존, C05에 권한·수용 판정 요청**, 운영 apply/DONE HOLD. 기존 긴급 사용자 요청이 D00을 자동 개정했다고 가정하지 않는다. C03은 C01/C02/C03 문서만 수정한다.
- #12 `6489973488`의 0.02분은 **테스트 하위 구간**이지 B 전체 세션이 아니다. B 전체 `ELAPSED_MIN=NOT_VERIFIED`; 초 단위 END가 없는 12:10/14:08 보고도 정밀 중앙시간에서 제외한다. **유효 work interval** 08:37:32~08:46:19(8.8분), 08:57:42~09:01:26(3.7분), 09:11:35~09:17:06(5.5분), 10:13:32~10:19:25(정정 5.9분)는 **서로 다른 기록의 부분/관측 구간**, `SAMPLE_N=4, MEDIAN_WORK_INTERVAL_MIN=5.7`; 전체 실행 중앙값은 `NOT_VERIFIED`. A 마지막 5개 **시작·종료가 초 단위로 확인된** 별개 세션(#11 `6482201950/6483670720/6484147965/6484564454/6485399799`)은 `SAMPLE_N=5, MEDIAN_ELAPSED_MIN=23.63`, 30분 미만 4/5. 이후 #11 `6487113514/6488643694`의 END는 게시 시각 보정 추정이 섞여 있어 정밀 중앙값에서 제외한다. 조기 종료는 **그 시점에 실제 미완료 안전 과제가 있었고 차단/한도 없었는지**와 함께 판단하며 빠른 전부 완료를 위반으로 보지 않는다.
- **최근 실측·조정 (2026-10-29 17:56 KST, #11/#12 최신 직접 대조):** A는 **최근 유효한 별개 5세션** `10.42/30.38/24.42/23.63/19.08`분(원시 START/END·초 검산), **SAMPLE_N=5, MEDIAN_ELAPSED_MIN=23.63, 30분 미만 4/5**. 그 뒤 A #11 `6487113514/6488643694/6490543459`의 END는 게시 시각 추정 혼입으로 정밀 표본 제외. **현재 A SOURCE `2bce7dca`, 최근 신규 코드/테스트 0**, 최신 C02 신규 #1~#5 개발 + #6 긴급 정확 SHA peer는 **전부 새 수행 증거 없음(5 DEV+1 PEER)**. 앞선 A 조기 종료 당시 새 패키지가 아직 배정 전이었으므로 **현재 미수행을 과거 조기 종료 위반으로 소급하지 않는다**. 다음 회차는 현재 C02 전 번호를 안전한 fake/temp·normal/-O·A 본인 push·독립 peer로 계속.

B는 최근 전체 세션의 원시 시작/종료를 검산할 수 있는 **SAMPLE_N=2**: #12 `6490623337` `16:13:46~16:23:00=9.23분`, `6491988675` `17:36:06~17:38:59=2.88분`, **MEDIAN_ELAPSED_MIN=6.06**(반올림, 두 세션 합산 아님), **30분 미만 2/2**. 과거 부분 작업구간 **N=4/중앙 5.7분**과 테스트 0.02분은 전체 세션 표본에 혼합하지 않는다. B 17:36 회차는 **이미 17:33 갱신된 C01을 읽지 않고 구 integration `c78e2657` 기준**으로 1개 scoped caller test만 로컬 `f893628f`에 커밋했고 **HANDOFF 문서 혼입 + Git HTTPS push 실패**, B 원격 SOURCE는 여전히 `617c8429`. **새 C01 #1~#5 DEV 전부 NOT_RUN, #6 정확 A 여섯 Owner peer NOT_RUN, #7 frozen은 실증 단일 명령 30.5초 한도만 BLOCKED**. C06 #12 `6492263485`의 **정본 미반영 시정 제안은 사실 확인·수용**, C06 댓글은 코드 완료 증거 0. Git 인증은 **push에 대한 실제 ENV_BLOCKED**이므로 B의 2.88분 자체를 시간 위반으로 취급하지 않되, **안전한 로컬 코드/격리 테스트·peer까지 전부 차단된 것은 아니므로 잔여 수행률 UNDERUTILIZED(부분)**. 정확 새 C01 원격 blob을 먼저 읽고 기존 미푸시 테스트는 **test-only로만** 분리/검증/정상 push, 금지 HANDOFF 커밋 직접 푸시 금지. #1~#6은 각자 실제 실행 또는 개별 근거 있는 BLOCKED로 보고. 안전 업무 소진 없이 새 댓글·첫 PASS·한 번호·상대 SHA 부재를 전체 종료 사유로 쓰지 않는다. **30분은 경보 기준이지 시간 채우기 지시가 아니다.**

### 1.3 EMERGENCY — 런검증 PC 긴급 브랜치 점검·충돌 방지·통합 인계 (매회 필수, D00 §1.2)

**홍사장 명시 승인(2026-10-29):** 예약 A/B와 **별개로**, 런검증 PC의 격리 클론에서 **단일 `emergency/p15-fixes` 브랜치**를 로컬 Codex 개발·로컬 Claude 독립 검증에 사용한다. 기존 C01/C02 예약 작업은 계속 진행하고, 긴급 로컬 실행자에게 CURRENT/C01/C02를 진입점으로 강요하지 않는다. **홍사장의 추가 직접 지시로 C03이 기존 단일 긴급 브랜치 `emergency/p15-fixes`에 한해 안전한 code/test를 직접 수정·정상 푸시할 수 있다**(D00 §1.2). **예약 A/B 개발 브랜치에 코드를 푸시할 권한은 생기지 않는다.** 로컬 Codex와 같은 파일을 건드리기 전 원격 HEAD/blob 및 미커밋 변경 충돌을 확인한다.

**C03 매회 확인 순서 — 원격 신규 변화만:**
1. `integration/p1.5` 기준 최신 HEAD를 확인한 뒤 GitHub에서 `emergency/p15-fixes` 브랜치 존재를 질의한다. **404/미생성은 `EMERGENCY=NOT_CREATED`**, 오류 추정이나 개발 지연 단정 금지. 로컬 런검증 PC 접속·클론 생성·운영 실행을 임의 수행하지 않는다. 신규 상태 변화가 없다면 댓글·문서 수정 0.
2. 생성된 경우 `EMERGENCY_HEAD`, 확인 가능한 `BASE_SHA`, **이전 접수 이후 신규 commit/변경 source/test path**를 기록하고, `integration/p1.5`·예약 A/B 최신 SHA의 수정 경로와 비교한다. **같은 파일·함수, 이미 해결된 결함, 선행 통합, 재작업 위험**이 보이면 `OVERLAP`을 표시한다. 단순 파일 교집합만으로 충돌 확정하지 않고 실제 diff/호출자·동작을 대조한다. 무분별한 `merge`/cherry-pick/force-push 금지.
3. 긴급 code/test는 원격 commit·실제 함수 diff, 대상 정상 pytest/stdlib smoke, 선택적 peer, C04 G3 통합, C05 DONE, RunLab RUNTIME_VERIFIED를 **서로 별도** 판정한다. 매번 -O/full peer/hosted 전체 CI를 필수로 만들지 않는다. 로컬 테스트·미푸시 코드는 G1/G2 통합 성공으로 승격하지 않는다.
4. 신규 코드 변경이 확인되면 기존 RF Owner/보호 파일 범위·원본 계약과 교차 검증한다. Codex 및 C03 직접 수정 범위는 **긴급 브랜치의 안전한 code/test**, Claude는 별도 격리 checkout의 **독립 read-only peer**다. 같은 작업 트리 동시 수정 금지. RunLab 운영 checkout/컨테이너·실계좌/주문·운영 State·DB·로그·실네트워크·비격리 `--apply`·UEF/Step5C/Guard 및 frozen/CI 정책 변경은 승인 없이는 `SAFETY_HOLD`다.
5. 안전 통합 후보가 생기면 `EMERGENCY_SHA | BASE_SHA | CHANGED_PATHS | A/B_OVERLAP | NORMAL_EXIT | G1/G2 | NEXT_G3`를 **신규 사실이 있을 때만 #36**에 남겨 C04 최소 통합·targeted smoke, C05 G1/G2/G3·DONE에 인계한다. C04/C05 문서·소스·RF·STATUS는 C03이 수정하지 않는다.
6. **최소 상태 보고:** `EMERGENCY=NOT_CREATED | NO_REMOTE_DELTA | IN_PROGRESS | REVIEW_READY | OVERLAP | BLOCKED | INTEGRATED` 중 실제 근거 있는 상태와 최신 SHA만 선택한다. **원격 diff 없는 경우 신규 댓글/감사 반복 금지**. 긴급 브랜치 인수 때문에 기존 #11/#12/#32 신규 검토, C01/C02 공급, C04/C05 게이트를 중단하지 않는다.

**문서 권한:** D00 개정은 이번 홍사장의 명시 승인으로 **이미 1회 수행된 별도 정책 변경**이다. 이후 C03 예약 회차는 D00을 자동 개정하지 않으며 본인 담당 C01/C02/C03에만 기록이 필요할 때 반영한다. 새로운 브랜치·PR/별도 A·B 긴급 브랜치 생성은 승인 아님.

**2026-10-29 신규 긴급 실제 수정·전담 인계:** `emergency/p15-fixes`에서 `libs/core/log_maintenance.py::write_log_inventory` 외부 symlink 쓰기 방지 + 6 tests (`241b2990`), `libs/ai/intent_schema.py::_to_float` 비유한 지정가 fail-closed + 18 param tests (`1f372f2f`). 원격 파일 확인은 `CODE_PUSHED`이고 **저장소 원본 pytest normal/-O·Claude exact 긴급 SHA peer·CI/운영 검증은 아직 `NOT_VERIFIED`**. 이전 B `312a5161`의 경로 이동 보호와 내용·오너 충돌 여부를 별개로 점검한다. A `2bce7dca`의 RF-041 원본 6-owner blob은 통합/B와 동일; **긴급 intent_schema patch만 그와 다르므로 A 기존 독립 C4·KEEP source 동일성 증거에 섞지 않는다**. C01 신규 7번 RF-041 정확 A 원본 6 owner peer, C02 신규 7번 전체 A Owner/효과 + 8번 긴급 정확 SHA 독립 검증을 제공했으며 완료 전까지 C05 RF-041/066 DONE 0. 새 안전 성과가 들어오면 C04/C05에 **파일 단위** 선별 통합/CI·수용 인계하고 큰 미배정 문서/테스트/배포 RF는 근거 없는 CLAIM/종결 금지.

### 1.4 RunLab 최신 17시 EOD 안전 인계 (읽기 전용, 새 운영 작업 금지)

- #32 `6491497848`(2026-10-29 17:12 KST 최종 관측): 실행 이미지 digest 불변, `RUN_SOURCE_SHA=UNKNOWN`; **runtime unhealthy(healthcheck 5초 timeout 연속 9회), API unhealthy(readiness 3초 timeout 연속 3회), web healthy**. 앞선 UI/API HTTP200·일시 회복을 현재 전체 HEALTHY로 해석 금지. 신규 주문 0, 이전 SELL guard fill_truth=false/-1/-1 잔류, broker↔local 누락·Reporter PnL/링크 불일치 지속. 실행 소스 귀속 없는 상태에서 새 SHA 회귀로 단정하지 않는다.
- **판정/인계:** `RUNLAB=BLOCKED / HEALTH_REGRESSION_OBSERVED / SOURCE_UNPROVEN`, C04/C05/RunLab 운영 증거 담당에게 **읽기 전용 healthcheck timeout 시각/경로·최근 health 로그·OCI revision/실행 소스 귀속** 확인 요청. 재시작·배포·실계좌/주문·Guard/Step5C/UEF 수정·health timeout 완화 지시 금지. 개발 A/B의 새 진단 fake/temp 범위와 운영 RunLab 사건을 혼합하지 않는다. CI·DONE·RUNTIME_VERIFIED 모두 미승인.

### 2. 작업 설계 전에 지팀장이 확인할 것
- 활성 원본 계약, 파일 Owner, 목표 배치, 호출자와 import/런타임 참조, IO/State/예외/부작용 및 fake/temp 가능한 범위. **큰 파일의 함수 본문과 의존성을 직접 확인한 후** 어느 함수를 어느 새 Owner로 MOVE하고 어느 기존 facade에 wrapper를 남길지 결정한다.
- **DONE은 영구 면책이 아니다.** DONE 상태의 파일도 (a) 실제 계약 위반, (b) 보호·효과·데이터 보존 결함, (c) 목표 트리·Owner/LOC 제한 위반, (d) 다른 작업의 안전한 완수에 반드시 필요한 구조적 의존성이 **증거로 확인되면** 재작업 대상으로 다시 판정한다. 단순히 파일이 크다는 이유로 이전 통합을 무조건 원복하지 않는다.
- DONE 재작업 시 **C05가 먼저 해당 RF를 근거와 함께 REWORK/적절한 단계로 재분류**하고 원래 acceptance·CI 증거를 구분해 기록하도록 인계한다. A/B에게 상태·큐를 수정시키지 않는다. 승인된 코드 이력을 무조건 되돌리는 `git revert`/force push를 지시하지 않으며, 변경 필요 부분을 좁혀 정상 커밋으로 보정한다.
- 재작업이 장래 다른 모듈 이동과 함께 하는 편이 더 효율적·안전하거나 즉시 수정하지 않아도 실위험이 없다면 **DEFER**: 정확 파일/함수, 현재 결함·목표 불일치, 왜 나중이 유리한지, 후속 작업 선행조건을 #36/C05에 남기고 현재 정상 동작은 보존한다. 보안·데이터 손실·실거래 보호 위험은 편의 때문에 보류하지 않고 즉시 안전 차단/에스컬레이션한다. DONE 유지와 결함 은폐를 혼동하지 않는다.

### 3. C01/C02 — FAST-3 실행 가능한 소수의 필수 실구현

- 다음 회차에 **A/B 각각 안전한 실제 코드 수정 1~2개**를 파일·함수·BEFORE blob·기대 diff·입력/negative fixture·호출자 호환·정상 pytest/stdlib smoke **exit0**·본인 브랜치 정상 push·원격 blob 확인까지 완결형으로 지정한다. -O, full peer, 매-RF hosted CI, C1~C7 전수는 **선택/역사**이며 필수 게이트가 아니다. 추가 안전 작업이 필요해지면 다음 회차에 실증된 새 결함/소스 근거로 보충한다.
- **RF-031 실구현은 KEEP과 구분:** 원본 facade BEFORE_LOC=500, 이동할 두 함수 154줄, 신규 Owner 및 실제 delegation wrapper, AFTER_LOC/변경 전후 source blob·새 owner blob·정상 테스트 exit0·A 원격 push를 모두 확인해야 `REFACTOR_CHANGED`. 기존 분리나 테스트-only는 `KEEP_VERIFIED_ONLY`/기준점 이전으로 별도 표기. 기존 함수가 이미 새 SHA에서 이동했다면 중복 MOVE 금지.
- **B 실결함 수정은 승인 경로 복구를 전제로:** `_NodeEventLogger.__getattr__`의 미초기화 복사본 접근에 한정하고 운영 logger/JSONL 포맷·실제 로그를 건드리지 않는다. stdlib unittest로 G2 가능하지만 Git 인증 실패는 G1 원격 반영과 분리. pytest 부재 자체는 stdlib smoke를 막지 않는다.
- **A/B preflight:** `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID`를 시작 시 고정. 도중 새 문서 발행은 기존 실행을 소급 실패 처리하지 않는다. 번호별 `IMPLEMENTED | TEST_BLOCKED | PUSH_BLOCKED | SAFETY_BLOCKED | NOT_RUN`을 분리하고, 정확 명령·exit·SHA·다음 재개점을 #11/#12에 남긴다. 지팀장은 C01/C02에 RF/큐/D00 탐색·자율 선정·이전 PASS 재실행을 지시하지 않는다.
- **증거/권한:** A/B는 자기 code/test 브랜치만 수정, C03은 본인 C문서 및 D00 §1.2의 제한된 긴급 예외만. C04 최소 통합·targeted smoke, C05 G1/G2/G3·RF/STATUS/DONE 독점. 보호 Broker/Step5C/UEF/frozen/RunLab 운영·실계좌/실주문·force push는 승인 없이는 금지.

### 4. FAST-3 delta·재개·중복 억제

- #11/#12/#32의 **지난 인수 댓글 이후 신규** 사실과 긴급 브랜치 신규 SHA만 검토. 코드/테스트 원격 diff, 실제 normal exit, 원격 push와 로컬-only·환경 차단을 구별. 실측 START/END/ELAPSED는 있는 그대로 보고하고 예약 간격·댓글 시각으로 추정하지 않는다. **30분은 경보 기준일 뿐 최소 수행시간/업무량 목표가 아니다.**
- 한 과제만 완료/차단됐더라도 남은 **안전하게 실행 가능한** 지정 과제를 계속 진행한다. 실제 실행 한도·안전/권한/환경 차단이면 정확 SHA·함수·명령·오류·해제 담당·재개점을 남긴다. 기존 PASS·동일 SHA·동일 입력 범위 재검증, 무의미한 NO_DELTA, 빈 문서 커밋은 금지.
- G1/G2 충족 RF는 즉시 C04/C05에 정확 SOURCE/TEST SHA·targeted normal exit·첫 G3 차단을 인계. 이미 DONE RF의 새 구조 변경은 과거 KEEP 실적과 분리하고, 새 결함이 확인되지 않으면 C05의 무근거 REWORK 이동을 요청하지 않는다. C04/C05 문서/코드/STATUS 직접 수정 금지.
- 실제 배정·차단·통합 근거 변화가 있을 때만 C01/C02/C03 해당 문서를 갱신하고 #36에 새 결정 1회 보고. **변경이 없으면 문서 커밋 0·댓글 0.** 기존 실행 버전 소급 무효화 금지.

### 5. GitHub 쓰기·보고
- 문서 작성자는 C03: `docs/refactor/work_orders/C01_CODEX_CURRENT.md`, `C02_CLAUDE_CURRENT.md`의 **이전 본문을 완전 교체**한다. 변경한 문서를 `integration/p1.5`에 정상 커밋/푸시하고 **원격 본문과 HEAD/Blob SHA를 재조회**한다. C04/C05 문서·업무·예약은 직접 바꾸지 않고 필요한 재분류·통합은 해당 담당에게 근거를 인계한다.
- 변경된 업무가 있을 때만 Issue **#36**에 적용한 C01/C02 원격 SHA, A/B의 마지막 실제 완료 번호/미완료, 현재 위험·DEFER/REWORK 근거, 다음 명령을 간단히 보고한다.

**보호:** 실계좌·Broker·Supervisor/Executor/Step5C·UEF·RunLab 운영 효과, 실네트워크/운영 DB·상태 파일, frozen test/oracle, Git 이력 재작성/force push, 타인 브랜치 쓰기 금지. 안전한 정적 코드/격리 mock/temp 테스트까지 불필요하게 막지 않는다.
