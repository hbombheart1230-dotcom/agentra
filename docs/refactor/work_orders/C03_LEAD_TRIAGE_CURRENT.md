# C03 — 지팀장 | 구체 실행 설계·A/B 연속 작업 공급

## FAST-3 최우선 운영 (2026-10-29 홍사장 속도 지시)
- D00 §2 FAST-3가 이 문서 내 과거 C1~C7/전체 Owner C4/매-RF normal -O/hosted 전체 CI/30분 업무량 강제 규칙보다 우선한다. RF 개발 DONE의 필수는 **G1 소스·Owner**, **G2 변경 부분 테스트 1회**, **G3 최소 통합·상태 반영**뿐. 원래 RF 7개는 이력 자료.
- A/B에게는 1~3개 실질적으로 가장 빠르게 끝낼 수 있는 코드/호환 수정만 먼저 지정하고, 기존 4~6 패키지+full peer 목록을 무조건 모두 처리하게 강제하지 않는다. 이전 C01/C02의 7번 등 동결/상대 전수 peer를 개발 DONE의 BLOCKER로 재전달 금지.
- 변경 없는 KEEP 파일·기존 정상 실행 증거를 최대한 재사용하고, 기능에 직접 영향을 주는 단일 실패/테스트에 집중한다. 상대팀 독립 probe는 선택적인 병렬 검토이고 완료 선행 조건이 아니다. 실제 mock/paper 런검증은 P1.5 개발 DONE 후 별도 수행.
- **다음 최우선:** RF-016 기존 G1/G2 MET 상태를 받아 C04에 KEEP 또는 최소 통합 smoke를 지시, C05 G3 DONE. 다음으로 RF-014/015/031 등 G1/G2의 변경 범위 테스트를 빠르게 승인해 연속 진행. 실계좌 real 활성화는 금지.
- 문서와 STATUS의 옛 7칸 텍스트를 새로운 필수 요구로 재해석하지 않는다. C05가 migrate_rf_fast3.py --write 및 sync_rf_checklist_status.py --write/--check를 인수하도록 #36에 지시한다.

**핵심 원칙:** 지팀장이 코드·아키텍처·RF 계약·소유권·안전·독립 검증을 모두 판단한다. Codex B는 C01, Claude A는 C02 **단 한 개의 이번 회차 작업 명령서**만 읽고 이전 채팅 문맥 없이 그대로 구현한다. A/B에게 프로젝트 상황 파악, 큐·RF·D00·CURRENT 재독, '무엇을 할지 알아서 결정', 과거 PASS 반복을 맡기지 않는다. 이 문서와 D00은 지팀장용이다. C04(선별 통합/CI)와 C05(최종 수용/DONE/STATUS)는 예약과 역할을 유지한다.

## 매회 지팀장이 직접 수행할 일

### 1. 입력·진도 판단 (반복 조사 최소화)
- `integration/p1.5` 최신 원격 HEAD, Issue #11(A)·#12(B)·#32(RunLab)의 **최근 신규 결과**, A/B 브랜치의 실제 SOURCE SHA 및 변경 코드·테스트만 확인한다. 신규 결과가 없다면 진행 중인 지시의 미완료 번호와 실제 중단점만 확인하고 이전 코드·PASS 전체를 매번 재독하지 않는다.
- C01/C02 **명령 번호별** 완료(정확 변경 파일/원격 SHA와 양 모드 증거 존재)·진행·차단·미수행을 판정한다. 테스트 PASS만으로 소스 변경 완료라고 판정하지 않는다. 작업이 실제로 수행됐는지 diff/LOC/caller 연결까지 확인한다.

### 1.1 직접 원격 RF 큐 스냅샷·ACTIVE/차단 관리 (C03 단독 책임)

- **책임 정합화:** D00 §1.1에 따라 **C03/C05만** RF 원본·큐를 탐색한다. C03은 원격 `integration/p1.5`의 단일 SHA를 먼저 고정하여 `QUEUE_SCAN_SHA`로 기록하고, `docs/refactor/plan/queue/{01_PENDING,02_DEVELOPING,03_PEER_REVIEW,05_DONE,06_REWORK}/{CLAUDE_A,CODEX_B}/` **10개 폴더의 RF Markdown 파일 경로만** 열거한다(비어 있는 폴더는 0). 추가 `UNASSIGNED`·`04_LEAD_ACCEPTANCE`도 지팀장이 별도 집계한다. 유일 RF ID·중복·실제 단계/소유자·CLAIM 여부·원본 첫 미충족 C1~C5를 대조한다. **A/B에게 QUEUE_SCAN_SHA, 폴더 열거, RF/D00 독해를 요구하거나 C01/C02에 스캔 지시를 삽입하지 않는다.** A/B는 파일·함수·격리 명령이 완결된 개별 작업 명령서만 수행한다.
- **현재 고정 큐 스냅샷:** `QUEUE_SCAN_SHA=bee316282fef4de1489d3653d7e8da86b52ff262` (2026-10-29 14시 KST 정본). 총 **93 unique, 중복 0**, PENDING **47**, DEVELOPING **13**, PEER_REVIEW **13**, LEAD **0**, DONE **20**, REWORK **0**. **CLAUDE_A:** PENDING `030/035`(2, CLAIM 전 read-only), DEV `021/040/051/054/058/061`(6), PEER `014/015/016/028/029/031/032/033/034/041/050`(11), DONE 8, REWORK 0 → **ACTIVE=17**. **CODEX_B:** PENDING 0, DEV `044/045/063/065/066/070/071`(7), PEER `018/069`(2), DONE 12, REWORK 0 → **ACTIVE=9**. 물리 단계·CSV/STATUS는 C05 단독 변경; 이 스냅샷은 C03의 **읽기 전용 진도 인덱스**이며 RF C1~C5 충족 선언이 아니다. 원격 큐가 실제 바뀐 때만 `QUEUE_SCAN_SHA`와 이 행을 교체하고 C01/C02에는 해당 안전 작업의 구체 소스 함수만 반영한다.
- **ACTIVE의 첫 차단/다음 작업은 C03이 직접 관리:** B `044/045/063/065/066/070/071`은 각 원래 **C1 ACTION/효과·소비자**와 일부 C2/C3 및 A full C4 미충족. **B `libs/core/log_maintenance.py::apply_log_move_candidates`는 과거 B SHA `44b36a23`에서 루트 탈출 3 FAIL, 최신 B `312a5161`에 경로 containment 코드·12 변형 테스트가 원격 반영됨.** 최신 SHA의 저장소 원본 normal/-O와 A 독립 C4는 미검증이므로 **구현 완료와 검증 완료를 분리**하고 C01 #2·C02 #6으로 인계한다. 운영 `--apply`는 HOLD. B `018`은 기존 scoped C4만, 원래 전체 C4 별개; `069`은 UEF snapshot C3 **SAFETY_BLOCKED**, 해제 C05/안전 담당. A DEV `040/051/054/058/061` 첫 C1 및 보호 경계, `021` exit C2/C3 **SAFETY_BLOCKED**(안전 담당); A PEER `031` writer/state C2·B full C4, `032` validation-id C2 **정책 BLOCKED**(C05), 기타 peer 정확 SHA 전체 범위 미완료. PENDING `030/035`은 C05의 CLAIM/보호 승인 전 read-only. DONE 20은 증거 있는 새 결함에서만 C05 REWORK 판정 인계; 동일 범위 재실행 금지.
- **D00 §6 새 예약·인수·재개 계약 적용 (2026-10-29 20시 KST 신규 판정):** 현재 integration HEAD를 읽고 C01/C02 **원격 ORDER_FILE_BLOB_SHA, CANONICAL_HEAD, OWNER_REMOTE_SHA, 번호별 ORDER_ID**를 실행자가 시작 시 고정하며, 진행 중 지시서 갱신을 소급 실패 처리하지 않는다. pytest 부재/비공개 export·인증 차단은 해당 TEST/PUSH만 BLOCKED, 다른 안전 번호/읽기 전용 peer 계속. C03의 문서 발행·#36 댓글은 코드/테스트/독립 C4/hosted CI/DONE 실적으로 세지 않는다. C05 사전 C1~C5/LEAD, C04 정확 SHA 통합/CI, C05 사후 C6/C7/DONE의 예약 인수는 **실제 원격 증거가 있을 때만** 진행.
- **가장 빠른 안전 종결 후보:** RF-016 8-owner Strategist 원래 C1/C2/C3 MET, C5 N/A, **첫 미충족 C4 PARTIAL**(반대팀 독립 검증 주체·원래 8 owner full coverage/새 node policy 소비자 negative). A 고정 SOURCE `2bce7dcaaadebe9fe825dcf9d2f5e1b1f667ad33`, A 최신 `8e370ccafade4dbb7689536791e4b89f5fdc033f`, B `617c8429c69c98ac6f707a820d0e6825766f8642`, integration `109b4b55faa266b50af78612c813a199bb2b02f5`의 **원래 8 owner blob 8/8 동일** GitHub tree 직접 대조. C01 **#8**에 `news_compaction→strategic_answers facade→node_policy_projection→strategy_policy_annotation`의 첫 누락 nested alias/State mutation·malformed·use-time patch 독립 tmp/fake negative, 정확 A SOURCE·normal/-O·B reviewer ID/8-owner matrix·원격 push/차단·C05 인계까지 완결 지시. 기존 94/2/3/isolated PASS 재실행 금지. **B 최신 #12 `6492418735`은 로컬 `7cf68e33/f833ec44` 코드·테스트만, pytest 없음·private export로 B 원격 SOURCE 변화 0**. B의 새 #1~#5를 원격 완료로 인정하지 않고 C01에 그대로 유지; #6 A 고정 peer는 pytest BLOCKED, #7 frozen은 실증 단일 명령 한도 BLOCKED. B 독립 #8의 pytest/원격 증거도 아직 NOT_RUN.
- **A 신규 SOURCE 인수·다음 작업:** #11 `6493240523`의 A 원격 `8e370ccafade4dbb7689536791e4b89f5fdc033f`는 구 `2bce7dca` 대비 **11 paths(+968/-15)**: `openai_provider._is_retryable_error` HTTPError 400/404 분기 수정 + market/performance safe finite + 신규 fake/temp tests. A의 해당 신규 파일 자체 정상/-O PASS는 **작업자 보고**, 선택 회귀 **344 PASS/57 ERROR**(guard baseline 미분류), full CI PASS 아님. 긴급 `1f372f2f` 24+30 양 모드 독립 scoped peer는 C4 full 아님. 기존 C02 개발을 중복 재배정하지 않고 **새 C02 #1~#4**에 provider decision/signal 2형태, korea_index_sanity finite, playbook_stats finite/recent_window, ProposalStore append serialization 안전 구현과 **#5 B 고정 `617c8429` EventLogger copy/deepcopy 독립 peer**를 새 입력·normal/-O로 제공. A 기존 nonfinite BUY/SELL actionable은 긴급 patch만 존재, 원래 RF-041 C2 SAFETY_BLOCKED/통합 미승인. A 새 작업 아직 NOT_RUN, 과거 18:13~18:40 종료는 게시시각 보정 혼입으로 정확 실측 종료 `NOT_VERIFIED`.
- **긴급/RunLab 별도:** emergency HEAD `457ca9f890e1773f4fcb6abe9179199f567c76c1`은 `1f372f2f` 이후 **7개 테스트 경로만 변경, production code 0**; 과거 긴급 peer를 새 코드 PASS로 중복 계상하지 않는다. #32 최신 `6493735258` 19:03 KST runtime healthcheck 5초 timeout 지속 unhealthy, API/web docker healthy, restart0, `RUN_SOURCE_SHA=UNKNOWN`, historical ORDER/GUARD/REPORT 및 stale readiness 미해결. 운영 재시작/배포/실주문/health timeout 완화·비격리 apply 금지, C04/C05/RunLab 담당에 read-only provenance/health 인계. RF-045 목적지 생성 race D2는 C05 `6494328403` 기준 C2 SAFETY_HOLD, 원격 B/긴급 자동 수정·RF-016 C4와 혼합 금지.
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
3. 긴급 코드·테스트에 대해 **원격 파일/commit 존재**, `python -m pytest` normal, `python -O -m pytest`, **Claude의 정확 SOURCE SHA 독립 probe**, 원본 RF C1~C5, `C04` 통합·hosted CI, `C05` DONE/STATUS, **RunLab 실증**을 서로 별도 단계로 판정한다. 로컬 사용자가 전달하지 않았거나 원격 증거가 없으면 `NOT_VERIFIED/NOT_RUN`으로 둔다. 작성된 테스트 개수를 PASS 수로 바꾸거나 commit 시각으로 세션 시간을 추정하지 않는다.
4. 신규 코드 변경이 확인되면 기존 RF Owner/보호 파일 범위·원본 계약과 교차 검증한다. Codex 및 C03 직접 수정 범위는 **긴급 브랜치의 안전한 code/test**, Claude는 별도 격리 checkout의 **독립 read-only peer**다. 같은 작업 트리 동시 수정 금지. RunLab 운영 checkout/컨테이너·실계좌/주문·운영 State·DB·로그·실네트워크·비격리 `--apply`·UEF/Step5C/Guard 및 frozen/CI 정책 변경은 승인 없이는 `SAFETY_HOLD`다.
5. 안전한 통합 후보가 생기면 `EMERGENCY_SHA | BASE_SHA | CHANGED_PATHS | A/B_OVERLAP | NORMAL/-O | CLAUDE_PEER_SOURCE | FIRST_UNMET_C1-C7 | NEXT`를 **신규 사실 발생 시에만 #36**에 남기고 **C04 본인에게 선별 통합·정확 SHA CI**, **C05 본인에게 RF/STATUS/DONE 판정**을 요청한다. C03은 **상시 C04/C05 문서 변경 금지**이며 신규 긴급 후보가 실제 존재하는 경우에만 #36을 해당 후보 인계 증거로 참조하도록 한다. 긴급 코드의 B/A 선행 통합·중복 시에는 통합 보류 또는 소스 동일성 KEEP 근거만 인계한다. 절대 브랜치 전체 자동 병합·임의 DONE 승격 금지.
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

### 3. C01·C02에 쓸 것은 '완결된 구현 명령'뿐
- 지팀장이 다음 실행을 위해 **각 4~6개의 실질적 코드 개발/수정 패키지와 1개 지정 상대 SHA 독립 검증**을 준비한다(안전한 작업이 적으면 임의로 개수를 채우지 않는다). **작성한 모든 패키지는 각각 필수 이행 대상**이고 번호는 식별자일 뿐 선행 순서나 선택권을 뜻하지 않는다. 건수·30분·1시간 실행시간을 성과 목표나 종료 기준으로 만들지 않는다. A/B가 여러 회차에 걸쳐 이어서 구현할 수 있는 넉넉한 작업 목록을 유지한다.
- 각 번호는 다음을 빠짐없이 쓴다: **정확한 기존 경로·함수·확인한 코드 상태/고정 SHA → 변경할 새/기존 경로·함수와 실제 MOVE/수정 방법 → 기존 caller/import/public signature/상태·IO·예외 호환 방법 → 기대 입력·출력 및 음성/실패 사례 → 구체 정상/`python -O` pytest 명령 → 추정이 아닌 실제 LOC 전/후 기록 → 본인 브랜치 커밋·원격 검증 → 부분 실패 시 다음 안전 번호**.
- '분리 검토', '효과를 조사', '전체 계약을 스스로 찾아 처리', '다음 READY RF를 고르라' 같은 **추상 지시 금지**. 새 Owner는 원래 의미 있는 단일 책임으로 만들고 가급적 150~300 LOC, 원칙 350 LOC 이하. facade가 새 Owner를 **실제로 호출**해야 하며 import만 추가하거나 구현을 중복 복제해 LOC 성과를 주장하면 안 된다. 정본의 기존 테스트/동결 오라클을 변경시키지 않는다.
- 상대 독립 검증은 **실제로 존재하는 타인 브랜치 SOURCE SHA**·호출 함수·입력·기대 결과를 명시해 **기존 허용 격리 환경의 임시 복사본**에서 수행하도록 작성한다. 상대 코드 수정/푸시 금지. 개발 중 새 SHA가 등장하면 기존 fixed-SHA peer를 취소하지 않고 새 검증 지시는 다음 C03 회차에 설계한다.
- 원래 RF 번호, 큐 경로, Owner 분류, C1~C7 단계, D00 독해 의무, 지난 회차 요약을 **A/B 명령서에 나열하지 않는다**. 다만 실제 보호·독점·권한 조건과 수정 가능 파일, 실행하지 말아야 할 효과는 해당 명령서 안에 직접 명시한다.


### 3.1 A/B 지시서 품질 게이트 — 로컬 장시간 Codex 방식 상시 적용

- **지팀장이 실행 가능한 작업을 미리 설계한다.** 최소 3개, 통상 4~6개의 *서로 독립인* 안전 개발·회귀 패키지와 1개 고정 SOURCE 독립 peer를 유지한다(실제로 안전한 과제가 적다면 허위로 채우지 않는다). 수량보다 작업별 정확 함수·수정 방법·검증 입력/기대·완료 증거를 우선한다.
- 각 번호를 **실행 단위**로 작성한다: `SOURCE SHA + 파일/함수 + 실패 재현 입력 + 기대 출력 + 허용 코드/테스트 수정 + normal/-O 명령 + 원격 push 증거 + 최초 차단/재개점`. 막연한 '조사/검토/진행'만 있는 항목, 직접 실행할 테스트 경로가 없는 항목, 소유권 불분명한 변경은 다음 실행에 내보내지 않는다.
- C01/C02 상단에는 매회 **연속 실행 루프**를 반드시 유지한다. `모든 번호 상태 확인 → 안전 번호 하나 실제 구현/검증 → 다음 미완료 번호로 이동 → 국소 장애 BLOCKED → 남은 전 번호 계속 → 증거 있는 종료/재개`. 단일 PASS·단일 커밋·일부 peer가 종료 조건이 되어서는 안 된다.
- **중복/환경 처리:** 정확 SOURCE·동일 입력 범위에 대한 기존 PASS는 원격 증거로 재사용하되 새 결함·새 입력은 새 회귀를 요구한다. 로컬 Windows처럼 긴 명령 실행이 가능한 환경에서는 frozen/대규모 테스트를 배정하고, 예약 플랫폼의 입증된 단일 명령 한도는 해당 게이트만 BLOCKED로 관리한다. 로컬 긴급 클론과 예약 A/B의 코드 소유·브랜치 권한을 혼동하지 않는다.
- **회차 후 추적:** #11/#12의 번호별 실제 코드 diff, normal/-O 종료코드, 원격 HEAD, 최초 미충족 계약, NEXT를 확인한다. 여전히 실행 가능한 번호가 남는데 보고만 하고 끝난 경우 다음 회차에 **같은 번호의 정확 재개점**을 유지하고 구체 명령/fixture를 더 명확히 한다. 모두 완료·실증 차단·플랫폼 한도면 조기 종료로 벌주지 않는다. 30분은 경보일 뿐 시간 채우기 지시가 아니다.
- **권한 보존:** A/B는 자기 브랜치 code/test만, 지팀장은 작업서/정본 통합 인계만, 긴급 트랙은 D00 §1.2의 별도 승인 범위만. D00·C04·C05·CI/frozen 원본을 변경하지 않고 C1~C7 판정을 자동 승격하지 않는다.

**이 품질 게이트는 신규 결함 또는 작업 진도 변화가 있을 때 C01/C02 본문을 구체적으로 교체하는 설계 규칙이며, 단순히 동일 문장을 매회 커밋하라는 지시가 아니다.**

### 4. 회차 인계·재개·분량 유지

**실측 작업시간 기반 공급량 조정 — 매회 필수**
- #11(A)·#12(B)의 **직전 3~5회 신규 실행 보고**에서 `START_KST / END_KST / ELAPSED_MIN`, 실제 원격 변경 파일·커밋·테스트, 명령 번호별 `IMPLEMENTED / VERIFIED_ALREADY / BLOCKED / NOT_RUN`를 함께 확인한다. 보고 구간 시간이 서로 일치하는지 계산으로 검산하되 **작업자가 제출한 소요시간을 실제 실행시간으로 추정·보정하거나 서로 다른 세션을 합산하지 않는다**. 자료가 없으면 `TIME_NOT_VERIFIED`로 분리한다. 최근 3회 미만이면 표본 수를 표시한다.
- A/B별 최근 유효 실행의 **중앙 소요시간(분), 30분 미만 비율, 회차당 실제 소스 변경·완료 패키지 수, 시작하지 않은 안전 과제 수**를 계산하고, **2시간 예약 간격**과 구별하여 다음 회차 지시의 크기와 해제할 장애를 조정한다. 예약 간격은 세션의 실제 실행 보장시간이 아니다.
- **실제 ELAPSED_MIN < 30분인데 지시된 안전 과제가 남아 있고 플랫폼 한도·권한·도구·안전 차단 증거가 없다면 `EARLY_STOP / UNDERUTILIZED`로 판정한다.** '이미 PASS', '우선순위 판단', '다음 SHA 대기', '일부 완료', '남은 시간 추측'을 종료 사유로 받아들이지 않는다. C03은 빠진 모든 과제를 다음 C01/C02에 **구체 함수·파일·수정·테스트·재개 지점**까지 재지시하고, 동일한 자의적 조기 종료가 반복되면 #36에 담당자·실측시간·미완료 과제·시정 내용을 명시한다.
- **30분 미만이더라도 실제 작업 전체 완료**, 안전 작업이 모두 실증 차단됨, 도구/권한/실제 플랫폼 실행 한도 등의 근거가 있다면 위반으로 단정하지 않는다. 반대로 30분 이상 실행했어도 코드 diff 없이 테스트·보고만 반복했다면 생산적인 완료로 인정하지 않는다. **30분은 의심 트리거이며 강제 실행시간·최저 근무시간·PASS 기준이 아니다.** 허위 시간 기록·대기·불필요한 반복 작업으로 채우게 하지 않는다.
- **조정 방법:** (가) 수행 가능 과제가 실제로 전부 빨리 끝났으면 최근 완료 속도를 반영해 다음 지시서에 2시간 주기 동안 끊기지 않을 만큼 실제로 검토된 신규 패키지를 보충한다(계획상 약 45~90분의 유효 작업 분량을 참고하되 보장·강제하지 않음). (나) 안전한 미수행 과제가 많이 남은 조기 종료라면 무조건 개수만 늘리지 말고 해당 항목의 모호한 표현·선행 조건·실행 경로를 제거하고 **모든 남은 항목의 필수 이행**을 재강조한다. (다) 환경/도구 장애면 B/A가 수행할 수 있는 다른 실제 코드 패키지를 앞당겨 지정하고 해결 담당을 C03/C05에 인계한다. (라) 작업량이 과도해 중도 실패가 반복되면 독립적인 작은 구현 단위로 분할하되 모든 업무를 지속적으로 남긴다.
- **보고:** 업무량·종료 원인이 바뀌면 #36에 각 담당자의 `SAMPLE_N / MEDIAN_ELAPSED_MIN / LAST_ELAPSED_MIN / IMPLEMENTED_COUNT / SAFE_NOT_RUN_COUNT / EARLY_STOP? / ADJUSTMENT / NEXT`를 간략히 기재한다. 검증 자료가 부족하면 숫자를 만들지 않는다.

- #11/#12 보고와 실제 원격 diff를 보고 **증거로 전부 구현·검증 완료한 과제만 제외**한다. 과제별 `IMPLEMENTED | VERIFIED_ALREADY(원격 SHA) | BLOCKED(증거·재개점) | NOT_RUN`를 구분한다. 진행·차단·미수행 과제는 원격 커밋·마지막 수정 함수·남은 단계·실패/재개 지점을 다음 지시로 그대로 인계한다. **A/B 자신의 판단에 따른 일부 과제 생략·조기 완료 선언은 무효**이며, 미완료 과제를 반드시 다음 회차에 잔존시켜 실제 구현을 요구한다.
- 1~2개가 막혀도 **다른 모든 안전 패키지를 실행 의무로 유지**하고 작업서를 보충한다. 과제는 동시/비순차로 수행 가능하되 **어느 것도 임의 포기 금지**. 이미 정확 SHA와 범위에서 검증된 테스트는 근거를 붙여 재사용할 수 있지만 미수행 작업까지 완료된 것으로 보지 않는다. 한 번의 테스트 PASS·한 번의 커밋·한 개 댓글로 실행 종료 금지. 실제 도구/권한/안전 차단과 플랫폼 한도만 근거 있는 미완료 사유로 구별하고, 실행 한도는 실측 체크포인트로 기록.
- **A/B 실행 중인 지시서를 중간에 깨뜨리지 않는다.** 시작 시 읽은 버전의 작업을 계속하게 하고, 다음 예약이 읽을 내용을 차례로 갱신한다. 새 결과·진도·차단 변화가 없다면 불필요한 문서 수정·커밋·댓글을 만들지 않는다. 주기 1→2→4→24시간 조정은 사용자 판단 시 별도 요청으로 수행하며, 예약 간격은 단일 실행 시간 보장이 아님을 구분한다.

### 5. GitHub 쓰기·보고
- 문서 작성자는 C03: `docs/refactor/work_orders/C01_CODEX_CURRENT.md`, `C02_CLAUDE_CURRENT.md`의 **이전 본문을 완전 교체**한다. 변경한 문서를 `integration/p1.5`에 정상 커밋/푸시하고 **원격 본문과 HEAD/Blob SHA를 재조회**한다. C04/C05 문서·업무·예약은 직접 바꾸지 않고 필요한 재분류·통합은 해당 담당에게 근거를 인계한다.
- 변경된 업무가 있을 때만 Issue **#36**에 적용한 C01/C02 원격 SHA, A/B의 마지막 실제 완료 번호/미완료, 현재 위험·DEFER/REWORK 근거, 다음 명령을 간단히 보고한다.

**보호:** 실계좌·Broker·Supervisor/Executor/Step5C·UEF·RunLab 운영 효과, 실네트워크/운영 DB·상태 파일, frozen test/oracle, Git 이력 재작성/force push, 타인 브랜치 쓰기 금지. 안전한 정적 코드/격리 mock/temp 테스트까지 불필요하게 막지 않는다.
