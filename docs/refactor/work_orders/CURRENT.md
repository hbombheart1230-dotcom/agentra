# Agentra CURRENT — P1.5 전체 리팩터링

> **유일한 활성 배정판:** 매 실행 원격 `integration/p1.5` CURRENT부터 확인. [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D01 Codex](../../../AGENTS.md) · [D02 Claude](../../../CLAUDE.md). 불변 문서는 재독하지 않는다.

## 2026-10-24 07:23 KST — CI_RED 후보 안전 판정 및 정확한 CI 확인 (우선 적용)

- **직접 원격 확인:** integration `af0caf776833efbc738bca9b88655980c78a45d7`; A `94a12b71f4f34821dd5b621bac4fc3cbf8e1331e` / `sched-21` (소스 불변), B `1e8faa4848ef1f1950ba8af9572ab73a062b9642` / `B-20261023T185820Z` (코드 후보 `8bde643d` 불변). 새로운 독립 최종 PASS나 소스 통합 없음.
- **hosted exact-SHA CI 직접 확인:** integration `af0caf776833efbc738bca9b88655980c78a45d7`의 5개 push Actions는 모두 완료, **Scripts 1 SUCCESS / Shared·Reporting/Web·Design Guard·T4 4 FAILURE**. Shared/Reporting은 `verify_b_composed()`가 현재 운영 문서 **9경로**(D00, STATUS, verification 양쪽 .gitkeep, RF-001/013/018/020/026)를 역사적 B-stage 목록 밖으로 판정; Design Guard/T4는 `read-only peer-review gate missing` 및 폐지된 opposite-CLI 문자열을 요구. 이는 CI_RED이며 정상/optimized 전체 PASS 아님. GitHub Actions runs `40021830240/243/287/233/387`.
- **지팀장 신규 직접 판정 — CI_RED `a0493b6035b390a1691371364b1e4ba3ec50aea9` = REJECTED_AS_SUBMITTED / BLOCKED:** GitHub exact commit diff는 `scripts/refactor/shared_strategist_contracts.py` **1파일**에 historical B-stage 허용 문서 **4경로**를 추가한다. 이는 **CI 오라클 자체 변경**이며 현재 사용자/D00 승인 범위 밖이다. 후보는 현 integration 실패 9경로 전체를 해소하지도 못한다. 별도 peer와 exact candidate hosted CI도 **NOT_RUN(각 Actions 0건)**. **이 SHA를 통합하거나 allowlist를 더 확장하지 말 것.** B는 이 후보를 반복 테스트하지 않고 RF-001/020 소유 소스·계약 작업을 계속한다. 역사 오라클의 의미 보존된 수리는 사용자 명시 승인 전 **SAFETY_HOLD**.
- **RF 게이트 유지:** RF-001 sanitation 2경로 `PASS_SCOPED`·33/33 owner-map 정적 검증은 인정하되 core side-effect 및 full RF 독립 PASS·exact integration normal/-O·hosted GREEN 부족으로 선별 통합 **BLOCKED**. RF-013 stage `7e06e979`는 RF-074 frozen inventory 1 FAIL로 **BLOCKED**, 9 owner와 RF-030/035 소비자 원소유 분리 유지. RF-020 KEEP 범위 한정, RF-021 안전 HOLD. 이번 지팀장 runtime test `NOT_RUN`, source merge `NOT_RUN`, **DONE 0/93**. 다음 A/B 회차는 이미 통과한 테스트를 반복하지 말고 RF-001 19 divergent owner의 공개 IO/부작용 경계와 새 독립 검증 가능한 소스 증거를 제출한다.

## 2026-10-24 08:58 KST — 공식 검증 큐 4건 접수 / 개발 병렬 재배정 (우선 적용)

- **원격 원본:** integration `500b358ea0d85001487e2c2c4299fdcc2fd6d387`, A HEAD `fa3f144f19c5aa5ae4c3cdc043fe0f76cdff0831` / RUN `2026-10-23T2317Z-claude-a-sched-23`, B HEAD `b0616a75a8effe1043ccee39d65aead47543dd27` / RUN `B-20261023T190650Z`. 신규 소스 없음.
- **지팀장 실행:** 기존 RF 파일을 원본 내용·증거 보존하여 **pending→verification/claude: RF-013, RF-018**(Codex peer), **pending→verification/codex: RF-001, RF-020**(Claude peer) 원자적 단일 Git tree/commit + nonforce CAS로 이동. **큐 접수는 PASS/통합/DONE 아님**; 각 RF에 코드 SHA·normal/-O·peer 범위·BLOCKED 사유·새 증거 시 재검증 조건을 기록.
- **차단 소유권:** RF-013=RF-074 9-new-file frozen inventory 및 RF-030/035 4-wrapper cross-owner(지팀장 소유권 판정/A 제안/B peer); RF-018=역사 inventory/collection 분리(A 분석/B peer); RF-001=core side effects·19 divergent files(B 수정/A peer); RF-020=외부 dynamic effects/RF-026 별도 안전 HOLD(B 분석/A peer). CI_RED `a0493b60` oracle 변경 거부 유지.
- **독립 개발 즉시 재배정:** Claude A → **RF-014** (Scanner agent, 20 owner paths), Codex B → **RF-002** (Operator UI UI/assets, 9 owner paths). 각자 기존 브랜치에서만 소유 파일을 개발하고 기존 큐 검증·수정은 별도 트랙. 교차 소유·안전·오라클 변경 금지.
- **이번 회차 runtime normal/-O NOT_RUN, 신규 peer NOT_RUN, source integration 0, hosted exact source GREEN 없음.** integration 기존 `500b358e` Actions **1 SUCCESS/4 FAILURE**, 신규 큐 상태 커밋 exact CI는 완료 전 **UNKNOWN**. **DONE 0/93**.

## 현재 배정 (CURRENT가 유일한 배정 권한)

- 전체 ROOT→LEAF 3985파일/298폴더, RF 93개. [STATUS](../plan/STATUS.md) · [단독 파일 소유권](../plan/FILE_COVERAGE_63182ab2.csv) · [기존 P1.5.0~11 최종 12개 합격 기준](../plan/criteria/).
- **Claude A:** 검증 큐 [RF-013](../plan/verification/claude/RF-013.md)·[RF-018](../plan/verification/claude/RF-018.md)는 Codex B peer 대기/BLOCKED. **신규 개발 RF-014 Scanner agent** ([pending](../plan/pending/RF-014.md), 20 owner files): 기존 소유 경계 내 read-only 전수·KEEP/MOVE/WRAPPER→실제 안전한 source change 또는 KEEP evidence·normal/-O·patchnotes·SHA 제출. RF-013 rework는 소유권 분리 제안으로 병행. 기존 브랜치 `work/p15-a-reporter-pure-20261021`.
- **Codex B:** 검증 큐 [RF-001](../plan/verification/codex/RF-001.md)·[RF-020](../plan/verification/codex/RF-020.md)는 Claude A peer 대기/BLOCKED. **신규 개발 RF-002 Operator UI 화면·자산** ([pending](../plan/pending/RF-002.md), 9 owner files): RF-001 33개 소유 파일과 교차 쓰기 금지, 정적 자산·UI 계약 read-only 분석→독립 소스 개선 또는 KEEP evidence·normal/-O·patchnotes·SHA 제출. RF-001 core rework는 별도 병행. [구 브랜치 정리](../plan/troubleshooting/open/P15_BRANCH_CLEANUP.md). 기존 브랜치 `work/p15-b-operator-structure-20261022`.
- **정규 RF 검증 큐:** Claude 작성 → [verification/claude](../plan/verification/claude/)에서 Codex 검증 (**RF-013/018 2건**); Codex 작성 → [verification/codex](../plan/verification/codex/)에서 Claude 검증 (**RF-001/020 2건**). **대기/BLOCKED 총 4건, DONE 0건**. 차단 중에도 A=RF-014, B=RF-002 독립 개발 병행.
- **별도 CI_RED 검증 대기(Codex B):** [CI 호환성 트러블슈팅](../plan/troubleshooting/open/P15_DOC_CI_COMPAT_20261023.md), 임시 `claude/agentra-p15-cloud-setup-v5ue0u` @ `59e34204abb66562780773b649576fa142976041` (코드 `a0493b60`, 인수인계 `d629bc31`). **SELF_PASS / PEER_PENDING**. 일반 RF가 아니며 새 RF 생성 금지. GPT가 CI 오라클 검증 후 수용·통합 결정.
- **GPT 지팀장:** 위 CI_RED 예외·[4-HEAD 합성 후보 d73be191](../plan/troubleshooting/open/P15_SOURCE_ADMISSION.md) source admission, RF 배정·최종 DONE. 합성 후보는 아직 SOURCE_ADMISSION_PENDING.

## 동일 실행 절차 — Claude/Codex, 로컬/클라우드 공통

1. **조회:** 최신 CURRENT, 본인 배정 pending RF **전부**, 반대쪽 검증 큐, 일회성 작업을 순회한다. 한 건 BLOCKED여도 다른 작업은 계속한다. 미배정 RF·다른 RF 소유 파일 수정 금지.
2. **개발:** 기존 소스 재사용 → 계약·입출력·부작용 동등성 → normal/`python -O`·경계 회귀 → UI patchnotes JSON/MD → 정확한 SHA 원격 push → **작성자 기준** `pending → verification/<author>` 인수인계. 공용 큐 상태 이동은 GPT/승인 publisher가 반영한다. SELF_PASS는 독립 PASS가 아니다.
3. **독립 검증:** 반대쪽 **별도 세션**이 exact SHA를 읽기 전용 검증한다. **로컬·클라우드 모두 상대 CLI 직접 호출·티키타카 의무 폐지.** 리뷰 세션 수정/커밋/푸시/다른 CLI 실행 금지. 실제 테스트 exit·PASS/REWORK/BLOCKED·NOT_RUN 기록.
4. **통합:** 정상 RF는 독립 PASS 후 별도 통합 단계에서 검증자가 승인 경로만 단일 writer/CAS·비강제 통합해 그 SHA의 normal/`-O`·필수 hosted CI 확인. CI 미통과·충돌·잠금 불명은 BLOCKED. **CI 오라클, PR31/4-HEAD, 안전·공유 계약은 GPT 별도 승인**. 최종 `verification → done`은 GPT만 결정.
5. **브랜치·안전:** 상시 `main`/`integration/p1.5`/A/B 4개. **integration과 A/B 개발 브랜치의 분기는 정상이며 개발 BLOCKED 사유가 아니다.** RF·D00/D01/D02는 integration에서 읽고 코드 작업은 해당 A/B 브랜치에서 수행한다(기존 A/B 브랜치에 RF 문서가 없어도 integration RF를 참고). 로컬 개발 커밋이 **원격 같은 A/B 브랜치 HEAD**의 자손이면 정상 fast-forward push할 수 있다. 동일 브랜치의 원격 HEAD가 변경돼 fast-forward 불가하거나 소유권/계약이 충돌할 때만 BLOCKED로 보고한다. 실행 전 checkout/BASE/원격 HEAD/권한 확인. 강제 push, 무단 merge/rebase, 자동 신규 브랜치 금지. 위 `claude/...`는 기존 승인된 단일 임시 예외이며 검증·보존·소비자 확인 후 정리. `main`, 실거래, Supervisor/Executor/Step5C/UEF, CI 오라클 무승인 수정 금지.
6. **예약:** A/B 모두 기존 개발 브랜치의 고정 `docs/refactor/work_orders/HANDOFF_A.md` / `HANDOFF_B.md`에 실제 예약 실행 결과 push 확인. 예약은 배정권·독립 PASS가 아니며 매 회차 원격 SHA/실행 증거를 검증한다. GitHub 이벤트 자동 트리거는 NOT_ENABLED.

## 2026-10-23 12:11 UTC 지팀장 최신 수거 판정

- **원격 확인:** integration `8239db1d`, Claude A `27a400d6` (RUN `2026-10-23T1211Z-claude-a-sched-5`), Codex B `1fbfb78e` (RUN `B-20261023T111042Z`). GitHub compare: A 코드 후보 `a21401db`→A HEAD 변경 경로는 `HANDOFF_A.md` 1개뿐, B 코드 후보 `a3d60e37`→B HEAD도 `HANDOFF_B.md` 1개뿐. **신규 소스·테스트 파일 변경 없음**; 두 HANDOFF 원격 저장 확인.
- **A RF-013/018 — BLOCKED / KEEP_VERIFIED_NOT_ACCEPTED:** 새 A 자체 테스트(후보 `a21401db` detached, 소유 범위 48 test files) normal 및 `python -O` **각각 667 passed / 1 failed**. 남은 실패는 역사적 S5 `test_diff_against_pinned_source_touches_only_the_closed_path_set` 범위 게이트. `test_m12_strategist_hook.py`의 RF-026 순환 import 수집 오류는 **667/1 합계에서 제외**됐으므로 전체 PASS가 아니다. 이전 2290 passed / 1 failed / 58 errors도 미해결. **PEER NOT_RUN**, 통합 NOT_RUN. A는 RF-013/018 전용 계약 증거와 S5 역사 게이트를 분리해 독립 검증 요청 근거를 준비하고 오라클은 수정하지 않는다.
- **B RF-001/020:** RF-001 `VERIFY_PENDING` (소유권/구조 계약), RF-020 `NO_WORK / VERIFY_PENDING` (전수 MOVE/KEEP/WRAPPER 및 테스트 미증명). 이번 회차 normal/`-O` `NOT_RUN`, 독립 PASS 없음. 브랜치 정리 `VERIFY_PENDING` (클라우드 외 worktree/process UNKNOWN).
- **CI_RED 예외 — REWORK_REQUIRED / NOT_ADMITTED:** 후보 `a0493b60`, handoff `59e34204`. B 이전 read-only normal/`-O` **모두 exit 1**, pinned `613a945d` UI 파일 로컬 `git show` 실패. 지팀장 GitHub 원격에서 해당 pinned blob 존재 확인했으므로 B는 clone/fetch 범위·git stderr·로컬 객체 접근을 진단한 후 동일 후보 normal/`-O` 재검증. 독립 PASS·통합 없음.
- **CI/안전:** 마지막 직접 확인 `138bdaed` hosted CI **1 PASS / 4 FAIL**. 현재 integration `8239db1d`의 exact-SHA hosted CI는 **UNKNOWN** (PR 전용 조회에서 결과 없음은 성공/미실행 증거가 아님). RF-026 `PENDING / SAFETY_HOLD` (exit_policy↔monitor_exit 순환; 교차 소유권 승인 전 소스 수정 금지). 정규 검증 큐 0건, **RF DONE 0/93**, 신규 코드 통합 0건. GPT는 S5 적용 범위·RF-026 소유권 판정을 유지하며 오라클/main/실거래/무승인 브랜치는 변경하지 않는다.

## 2026-10-23 지팀장 실행 지시 — 첫 RF 검증 전진 (우선 적용)

- **우선순위 1 / Claude A / RF-013:** 기존 후보 `a21401db`의 `libs/agents/reporter/` 독점 67파일에 대해 MOVE/KEEP/WRAPPER/SAFETY_HOLD 전수 증거를 정리하고, Reporter에 한정된 normal 및 `python -O` 회귀를 새로 실행한다. S5 historical cross-scope 1 FAIL과 RF-026 순환 import는 별도 차단으로 구분하되 삭제·skip·오라클 완화 금지. 독립 검증 가능한 정확한 코드 SHA, 테스트 명령/exit, 남은 결함을 `HANDOFF_A.md`에 남긴다. **RF-018은 병렬 독립 증거만 준비**하고 RF-013 검증 요청을 늦추지 않는다. 검증 준비가 되면 B의 다음 read-only 검증 대상으로 RF-013을 명시한다.
- **우선순위 1 / Codex B / CI_RED:** 원격에 존재하는 `613a945d:apps/operator_ui/data_access_core.py`가 로컬에서 조회되지 않는 원인을 `git cat-file -t`, `git show` stderr, shallow/partial clone/fetch 상태로 진단한다. 허가된 읽기 전용 이력 fetch로 해결 가능하면 기존 후보 `a0493b60` normal 및 `python -O`를 **정확한 SHA**에서 재실행하고 실제 exit와 verdict를 `HANDOFF_B.md`에 기록한다. 후보·오라클 수정 및 integration 병합 금지. 객체가 여전히 불가하면 정확한 명령·stderr와 최소 재현으로 BLOCKED 판정한다.
- **우선순위 2 / Codex B / RF-013 peer:** A가 검증 가능한 RF-013 후보 SHA와 테스트 증거를 HANDOFF에 올리면, **별도 읽기 전용 검증 세션**에서 RF-013만 정상/`-O` 독립 재현하고 PASS/REWORK/BLOCKED를 명시한다. 독립 검증에서 소스·테스트·오라클 변경 금지. B의 RF-001/RF-020은 기존 소유권/계약 미확정 범위를 임의 수정하지 말고 안전한 독립 파일 검증을 계속한다.
- **GPT 지팀장:** RF-026 순환 import는 해당 소유 RF의 안전·교차 소유권 승인 전 코드 변경 금지. CI_RED가 독립 PASS 및 exact-SHA CI를 얻기 전 통합 금지. A/B의 다음 HANDOFF가 실제 소스 또는 검증 증거를 전진시켰는지 확인하고, 미진전 시 원인별 REWORK 판정한다. RF 최종 DONE은 정상/`-O`, 독립 PASS, 선별 통합, exact-SHA CI를 모두 만족할 때만.
- **금지:** 새로운 RF·트러블슈팅·예약 로그 문서 생성, 불필요한 추가 브랜치, main/실거래/안전 가드/CI 오라클 수정, 무단 merge/rebase/force push.

## 2026-10-23 13:00 UTC 지팀장 신규 증거·판정

- **원격:** integration 이전 `6bdac585`; A HEAD `97a620f3` / RUN `2026-10-23T1300Z-claude-a-sched-6`; B HEAD `1fbfb78e` / RUN `B-20261023T111042Z` (새 회차 없음). A 후보 `a21401db`→A HEAD GitHub compare는 HANDOFF_A 1파일만 변경, BASE `63182ab2`→A 후보는 **58경로 변경**. B 코드 후보 `a3d60e37` 유지.
- **RF-013:** A 자체 Reporter 19파일 normal/`-O` 각각 **624 PASS / exit 0**; 추가 직접 참조 6파일 각각 **202 PASS / 10 FAIL**, 공유 계약 각각 **77 PASS / 11 FAIL**. A 보고 67/67 기존 소유 파일 KEEP, 신규 Reporter 9파일, 다른 RF 소유/CSV 미등재 경로 존재. **범위 제한 SELF 증거만 준비됨; PEER NOT_RUN, 소유권·공유 계약 BLOCKED, 통합 NOT_RUN.** [RF-013](../plan/verification/claude/RF-013.md)에 상세 증거 반영. 624 PASS를 RF 전체 PASS로 취급하지 않는다.
- **B 다음 행동:** A 후보 `a21401dbf8161b549848ac682b8bd11cac439ab5`에 대해 Reporter 19파일 정상/`-O` 독립 read-only 재현, 58경로의 RF 소유권·CSV 미등재 파일을 구분하고 PASS/REWORK/BLOCKED 명시. 기존 CI_RED pinned 역사 객체 fetch 문제 해결도 병행. B의 이전 CI_RED normal/`-O`는 exit 1; RF-001/020 이번 신규 테스트 NOT_RUN.
- **GPT 판정:** 교차 RF 소유 파일을 RF-013로 일괄 편입하거나 오라클을 완화하지 않는다. 안전·계약 소유권 해소 전 선별 통합 보류. integration `6bdac585` exact-SHA hosted CI는 조회 가능한 결합 status가 비어 있어 **UNKNOWN** (PASS 아님). RF DONE **0/93**, 독립 PASS **0**, 신규 통합 **0**.

## 2026-10-23 13:13 UTC 지팀장 최신 검증·다음 행동

- **원격:** integration 이전 `f2bd4beb`; A HEAD `428b81ca` / 최하단 재확인 RUN `2026-10-23T1500Z-claude-a-sched-7` (상단 RUN_ID는 이전 `...1300Z...-6`로 남아 있음), B HEAD `c3d41076` / RUN `B-20261023T131355Z` (**신규 독립 검증**). A는 HANDOFF 1경로만 추가, 코드 `a21401db` 그대로; Reporter normal/`-O` 624 PASS 자체 재실행(독립 아님). B 코드 `a3d60e37` 유지; B 후보→HEAD GitHub compare는 HANDOFF_B 1경로만 변경. A는 다음 회차에 상단 RUN_ID와 PEER_VERDICT를 최신 원격 사실로 통일한다.
- **RF-013:** B 별도 read-only 검증 normal/`python -O` **각각 624 PASS / exit 0** (19파일, A 코드 `a21401db`). **PEER_VERDICT BLOCKED/REWORK**, 소유권·공유 계약 미해소로 전체 PASS 아님. B 보고 106경로와 GitHub BASE→후보 compare 58경로는 집계 기준 불일치; 경로별 소유권 분리 필요. A는 RF-013 독점 범위만 선별할 수 있는 후보/계약 증거를 준비하고 B는 경로 집계 기준·교차 소유권을 명시한다.
- **CI_RED:** B의 pinned `613a945d` history fetch·UI blob 읽기 **성공**; 기존 `a0493b60` normal/`-O`는 각각 **exit 1**, 원인이 B-stage UI structure 6경로 unexpected/missing으로 구체화. **REWORK_REQUIRED / NOT_ADMITTED**. B는 6경로의 기대/실제·소유권 증거 제출, GPT는 역사 오라클 보존 하에 admission 경계 판정. RF-001/020 신규 테스트 **NOT_RUN**.
- **통합/CI:** 신규 통합 **0**, RF DONE **0/93**, 독립 최종 PASS **0**. integration `f2bd4beb` exact-SHA hosted CI **UNKNOWN** (PR 필터 조회 결과 없음). RF-026 안전 HOLD 유지; main/실거래/오라클/무승인 브랜치 변경 없음.

## 2026-10-23 14:20 UTC 지팀장 최신 수거·판정

- **원격:** integration 기존 `99de4fb3`, A HEAD `5493ec81` / RUN `2026-10-23T1420Z-claude-a-sched-8`, B HEAD `baf066f1` / RUN `B-20261023T141441Z`. 코드 후보 A `a21401db`, B `a3d60e37` 불변; 이번 A/B 소스 변경 없음. A는 상단 RUN_ID 불일치 정리 완료, 이번 회차 테스트 NOT_RUN.
- **RF-013:** B 독립 read-only Reporter 19파일 normal/`-O` 각각 **624 PASS**는 유지하나 PEER **BLOCKED/REWORK**. A가 106경로(BASE 양방향 차이)와 58경로(A merge-base 기준 실제 변경)를 분리했고, 신규 Reporter owner 9파일만 선별하면 활성 소비자 없는 휴면 코드임을 확인. RF-030/035 wrapper와 CSV 미등재 43파일, 공유 계약 51경로 충돌은 **GPT 소유권/계약 판정 전 BLOCKED**. A는 타 RF 소유 파일 무단 수정하지 말고 경계별 선별 후보를 준비한다.
- **CI_RED:** B가 exact detached 후보 `a0493b60`에서 normal/`python -O` **각 exit 0** 재현. 이전 UI 6경로 exit 1은 잘못된 작업 트리 결과로 철회. [기존 CI_RED troubleshooting](../plan/troubleshooting/open/P15_DOC_CI_COMPAT_20261023.md)에 정정 기록. **별도 peer receipt NOT_RUN, exact-SHA hosted CI UNKNOWN, NOT_ADMITTED/통합 NOT_RUN**. B는 검증 근거를 보존하고 독립 peer 증거 확보; GPT는 오라클 변경 없이 source admission·CI 확인.
- **상태:** RF-001/020 신규 테스트 NOT_RUN, RF-026 SAFETY_HOLD. RF DONE **0/93**, 최종 독립 PASS **0**, 신규 통합 **0**. integration `99de4fb3` hosted CI는 A 보고 1 PASS/4 FAIL이나 지팀장 PR 전용 조회 결과 없음; **직접 확정 UNKNOWN**. main/실거래/오라클 변경 없음.

## 지팀장 확정 결정 — 소유권 분리 및 실행 우선순위 (2026-10-23)

- **결정 RF-013:** A 후보 `a21401db`의 실제 변경 58경로는 **RF-013 일괄 편입 불허**. 신규 `libs/agents/reporter/read_models/` 9파일은 RF-013 소유로 유지하고, 기존 67파일은 KEEP_VERIFIED 후보(최종 검증 전). RF-030의 `operator_visibility.py`·`operator_period_summary.py`, RF-035의 `metrics_report_generator.py`·`phase_runtime_health.py` 등 소비자 wrapper는 **각 원소유 RF에서만 변경**. A는 9파일+필수 소비자 변경을 **파일별 별도 후보/패치 집합**으로 구분하여 제출하고, 단독 9파일은 비활성 코드이므로 DONE/통합 신청하지 않는다. 타 RF 수정 15경로 및 CSV 미등재 신규 34경로는 원 소유 RF·테스트 소유자 판정 전 RF-013 통합 범위에서 제외한다. 원래 브랜치 전체 merge 금지.
- **A 즉시 행동:** 반복 624 PASS 재실행보다 실제 소비자 의존성/기존 인터페이스 parity를 증명하고, RF-013 9파일과 RF-030/035의 최소 활성화 wrapper 경로를 분리한 검증 가능한 코드 후보를 기존 A 브랜치에 생성. RF-030/035의 소유권은 변경하지 않으며, 필요한 교차 파일은 **읽기 전용 patch proposal**로만 제출(원소유 RF의 코드 변경·push 금지). 나머지 Q8·Alpha·AI Review 변경은 각각 별도 소유 RF로 분류하고 RF-013 완료 근거에서 제외. 코드 변경 시 UI patchnotes JSON/MD 동기화. 독립 normal/-O·소비자 회귀를 증명할 때까지 BLOCKED.
- **B 즉시 행동:** CI_RED `a0493b60`은 exact detached normal/-O exit 0 **재현까지만 인정**, hosted CI·별도 peer receipt 이전 source admission 보류. 이미 해소된 역사 객체/잘못된 작업트리 오류를 다시 진단하지 않는다. RF-013에 대한 동일 624 PASS 반복 검증 중단. 우선 **RF-001 소유 파일에서 실제 최소 코드 개선 + normal/-O**, 이어 RF-020 전수 MOVE/KEEP/WRAPPER 검증에 착수; 교차 소유 파일은 읽기 전용 제안. 각 회차 HANDOFF에는 새 코드 SHA 또는 재현 가능한 구체 장애를 남긴다.
- **지팀장 통합 게이트:** ① 원소유 RF별 파일 집합과 테스트 분리 ② RF별 독립 peer PASS ③ 선별 integration SHA normal/-O ④ 동일 SHA hosted CI 필수 PASS 순서. 기존 역사 S5/B-stage oracle을 현 후보 51경로에 무조건 적용하거나 allowlist 확장하지 않는다. CI_RED는 별도 호환성 트랙으로 독립 검증하고 RF 완료 수치에 합산하지 않는다. RF-026 SAFETY_HOLD, main/실거래/안전권한 변경 금지.
- **상태:** 소유권 분리 결정만 완료. **신규 소스 커밋/테스트/통합 NOT_RUN**, RF DONE 0/93. 다음 예약 실행은 보고서 갱신만으로 진전 처리하지 않는다.

## 2026-10-23 15:02 UTC — 지팀장 exact-SHA hosted CI 실패 직접 진단·처리

- **원격 대조:** integration `fa233811`; A HEAD `5493ec81` / RUN `2026-10-23T1420Z-claude-a-sched-8` / 코드 `a21401db`; B HEAD `baf066f1` / RUN `B-20261023T141441Z` / 코드 `a3d60e37`. **A/B 신규 회차·소스 변경 없음**. 소유권 결정은 직전 절로 이미 확정, 반복 승인 불필요.
- **직접 확인 CI:** `fa233811`의 5 Actions 중 Scripts **SUCCESS**, Shared **FAIL**, Reporting/Web **FAIL**, Design Guard/T4 **IN_PROGRESS** (각 Linux regression step FAIL, Windows step 진행 중; 전체 결론 미확정). [기존 CI troubleshooting](../plan/troubleshooting/open/P15_DOC_CI_COMPAT_20261023.md)에 정확한 job/log 근거와 수락 조건 반영. **CI_RED 유지, RF DONE 0/93, source 통합 0**.
- **확인된 두 원인:** Shared/Reporting의 pinned B-stage inventory는 **현재 허가된 문서 6경로**를 역사적 변경 목록과 혼동하여 FAIL; Design Guard/T4 Linux 단계는 폐지된 direct opposite-CLI 역사 문자열을 현행 D01/D02에 요구(`REVIEW_ONLY_NO_NESTED_CLI` 첫 실패). **역사 오라클 수정·토큰만 채워 거짓 통과 처리 금지**. GPT가 historical/current scope 분리 설계·계약 소유 판정 담당. A는 RF-013 9 owner/원소유 소비자 patch 제안, B는 RF-001/020 코드·normal/-O에 집중. CI 수리는 별도 검증 가능한 후보·정확한 SHA·hosted CI 이후만 ACCEPT.

## 2026-10-24 지팀장 소스 후보 분리 승인 — 단일 임시 브랜치

- **실제 실행 완료:** 지팀장이 `stage/p15-rf013-activation-20261024@7e06e979f854b323eb70eaf63e6d252e27be6965`를 생성·원격 검증했다. 부모는 integration `e39052edbae7627a027920b4ff18523da45e2f3f`, **변경 경로 정확히 17개 = RF 소스·테스트 15 + UI patchnotes JSON/MD 2**. 원본 A `a21401db`의 다른 43경로는 제외. patch_notes JSON entry_count **356/356**. `7e06e979` hosted Actions 조회 **0건(미실행, PASS 아님)**. 실제 GitHub 소스 커밋이므로 단순 문서 계획이 아니다.
- **B 독립 peer 다음 회차 최우선:** 기존 B 브랜치 소스 변경 없이 별도 detached read-only worktree에서 **stage `7e06e979` exact SHA**를 checkout하고 `tests/test_p15_a_reporter_pure_boundaries.py` + `tests/test_p15_a_reporter_pure_parity.py` normal/-O 및 A가 지정한 16 consumer 테스트 normal/-O를 실행. `test_work_reporter_seed_migration.py::test_target_tree_discipline_and_no_forbidden_surface`의 **실패 로그·frozen inventory 실제 값**을 분리하고 원본 오라클 수정 없이 PASS/REWORK/BLOCKED를 판정. 15경로 외 타 RF·안전 변경·새 브랜치/merge 금지. 증거는 기존 HANDOFF_B에 exact SHA·명령·exit로 기록. A는 이 stage에서 새 소스 개발 금지(원 A 브랜치의 RF-018·후속 RF-013 독립 작업은 가능).
- **실행 승인(예외):** D00의 단일 임시 브랜치 규정에 따라 지팀장이 `stage/p15-rf013-activation-20261024`를 integration 최신 SHA에서 1회 생성한다. **소유자 GPT**, 목적은 A 후보 `a21401db`의 58경로 중 **정확히 15개 소스·테스트 경로만 분리한 검증용 staging**. 여기에 UI patchnotes JSON/MD만 추가 가능. **integration/source admission, 독립 PASS, CI GREEN 또는 RF DONE 승인이 아니다.** 신규 상시 브랜치 불가. 소비자 B peer·CI·PR 및 SHA 보존 상태 확인 후 최종 통합 또는 명시적 폐기 시 정리; 임의 삭제 금지.
- **교차 RF 제한 승인:** RF-013 신규 read_models 9개는 A 소유. 4개 wrapper `libs/reporting/{metrics_report_generator,operator_period_summary,operator_visibility,phase_runtime_health}.py`는 각각 **RF-035 2개, RF-030 2개** 원소유 유지. 이 4경로에 한해서만 **GPT가 stage에서 원소유 RF의 통합 준비 역할을 수행**하며, A에게 다른 RF 전체 소유권을 넘기지 않는다. `tests/test_p15_a_reporter_pure_{boundaries,parity}.py` 2개는 후보 증거용. Q8/Alpha/AI Review, RF-074 기존 oracle, 안전권한 파일은 stage에서 제외.
- **새 A 증거:** sched-9/10에서 위 15경로를 integration `29637622`에 격리 오버레이하여 pure normal/-O 각각 **41 PASS**, 16 consumer 파일 normal/-O 각각 **985 PASS/1 FAIL**. 유일한 실패는 RF-074 `test_work_reporter_seed_migration.py::test_target_tree_discipline_and_no_forbidden_surface`의 frozen folder inventory가 신규 read_models 9개를 거부. **oracle 변경 승인 없음, CI/peer PASS 아님**. B는 stage exact SHA에서 **별도 읽기 전용 세션**으로 41·986 consumer 및 계약·소유권을 재검증하고, 실패가 역사 inventory인지 실제 계약 위반인지 독립 판정. 지팀장은 oracle 수리 없이 안전한 추가 source 분리 가능성을 계속 평가한다.
- **B RF-001 개발 차단 해제 판정:** `0254a5aa`의 변경은 RF-001 소유 `apps/operator_ui/data_access_brief.py`, `data_access_brief_sanitation.py` **정확히 2경로**이며, 지팀장이 diff에서 기존 `clean_brief_text/list`를 sanitation owner로 옮기고 facade의 `clean_brief_text` 호출을 유지하는 설계를 직접 확인했다. **기존 B-stage frozen inventory FAIL은 RF-001 새 개발 자체의 금지 사유가 아니라 역사적 stage 적용 범위 문제**로 분리한다. B는 **기존 B 브랜치에서만** 이 2경로 후보를 다시 적용하거나 동등한 개선을 구현하고, normal/-O 순수·facade monkeypatch·예외/빈값 parity와 원본 historical gate 실패를 구분해 기록하라. 재적용을 PASS·통합으로 주장하지 말고, RF-001 독립 peer와 hosted CI는 계속 요구한다. 오라클·안전·타 RF 변경 금지.
- **새 B 증거:** B RF-001 sanitation 후보 `0254a5aa`는 frozen B-stage inventory 차단으로 `6b0681df`에서 **revert**. RF-020 CSV 30/30 KEEP, focused normal/-O 각 122 PASS/1 FAIL(외부 UI inventory 6경로). 두 RF **독립 PASS 없음**. B는 같은 CI/역사 allowlist 재진단을 중단하고 원소유 코드 경계에서 계약을 유지하는 새 최소 구현 또는 30파일 외부 소비자 parity를 계속한다.
- **hosted CI 직접 재조회:** integration `29637622` Actions **Scripts 1 SUCCESS / Shared·Reporting/Web·Design Guard·T4 4 FAILURE** (5개 모두 completed). 정확한 SHA `29637622`의 CI RED이며 다른 SHA에 대한 판정으로 재사용 금지.

## 2026-10-24 02:19 KST 지팀장 실측·차단 해소 판정

- **실측 원격:** integration `d11ab08f` (본 점검의 RF 증거 반영 후), A `bcd3c8d6` / sched-12 (신규 소스 없음), B `744c6e8c` / RUN `B-20261023T171720Z` (stage 독립 peer 수행, 신규 B 소스 없음).
- **RF-013 stage `7e06e979` 독립 peer:** B detached read-only pure normal/-O **41/41 PASS**, direct consumer 9파일 + RF-074 inventory normal/-O **153 PASS/1 FAIL**. 이 증거는 A의 16 consumer 파일 985/1 전수 범위를 대체하지 않는다. 1 FAIL은 `test_work_reporter_seed_migration.py::test_target_tree_discipline_and_no_forbidden_surface`의 **read_models 기존 33파일 고정 목록 대비 신규 9파일** 충돌(지팀장 GitHub 양쪽 디렉터리 실측: 33→42). **RF-074 오라클 수정·allowlist 확장 승인하지 않음**. 9개 신규 파일이 역사 고정 구조에 부합하도록 소스 배치 대안 및 기존 33개 owner 재사용 가능성을 A가 분석·제안한다(코드/테스트 오라클 임의 변경 금지). 새 후보가 없으면 B는 동일 41·153/1 반복하지 않는다. stage/source admission **BLOCKED**, RF-013 DONE 아님.
- **RF-018 / RF-020 지팀장 독립 정적 검증 완료:** GitHub Contents API 재귀로 BASE↔integration↔A/B 해당 브랜치 경로·blob SHA 대조. RF-018 Strategist **47/47 동일**, RF-020 Monitor **30/30 동일**, 경로 추가/삭제 0. 각 RF 원본에 증거 반영. **KEEP_VERIFIED 후보로 진전**했으나 normal/-O 및 반대편 독립 peer가 아직 없어 DONE 아님. A는 RF-018 소유·소비자 회귀 normal/-O를 제출하고 B는 RF-020 회귀 명령·exit 및 소비자 경계를 제출; A가 RF-020을, B가 RF-018을 각각 별도 read-only peer 검증.
- **B RF-001:** GPT가 승인한 sanitation 2경로 개선을 **기존 B 브랜치에서 신규 코드 SHA로 재적용**하고 monkeypatch/예외/빈값 parity normal/-O·patchnotes를 먼저 확보. 역사 frozen B-stage inventory는 별도 트랙으로 분리하고 오라클 수정 금지. 단순 HANDOFF만 갱신하는 회차를 진전으로 취급하지 않는다.
- **hosted CI 직접 확인:** integration `2170066e` 5개 Actions 완료, Scripts **1 SUCCESS**, Shared·Reporting/Web·Design Guard·T4 **4 FAILURE**. stage `7e06e979` hosted Actions **0건**. 본 문서/증거 업데이트 exact SHA CI **UNKNOWN**. CI_RED `a0493b60` 별도 peer/exact CI 미충족, 통합 금지. RF DONE **0/93**; main·실거래·안전 가드·CI 오라클 불변.

## 2026-10-24 03:02 KST 지팀장 신규 증거·실행 판정

- **원격 수거:** integration 이전 `7d0167bf`, A `51065012` / sched-13 (RF-018 **신규 자체 테스트 증거**, 소스 불변), B `744c6e8c` / RUN `B-20261023T171720Z` (이전과 동일, RF-001 신규 소스 없음). A/B 원격 HANDOFF를 직접 재조회했다. A 코드 후보 `a21401db`, B 신규 유효 코드 후보 **NONE**; RF-013 stage `7e06e979` 유지.
- **RF-018 새 근거 수용:** A는 integration `2170066e` detached에서 Strategist 관련 13파일 normal/-O 각각 **1152 PASS / 2 FAIL / 57 collection ERROR**, 공유 계약 1파일 제외 12파일 각각 **1152 PASS / 2 FAIL** 보고. 실패·수집 오류는 역사 `verify_b_composed` B-stage inventory와 연관됐다는 **A 분석이며 지팀장 독립 실행 NOT_RUN**. 47/47 blob KEEP 정적 확인과 기능 PASS를 인정하되 **RF 전체 PASS 아님**. [RF-018](../plan/verification/claude/RF-018.md)에 신규 실행 증거 반영. **B 별도 read-only peer 우선 배정**, 실패 2건과 collection 57건은 CI_RED 계약 트랙과 분리 추적. A는 RF-013 역사 inventory 해결을 위한 기존 33 owner 재사용/구조 대안만 제안하고 기존 oracle 무단 수정 금지.
- **RF-013:** stage `7e06e979`의 B 41 PASS, 소비자 153 PASS/1 FAIL은 이미 판정됨. 직접 import 소비자 9파일만 검사했으므로 A의 16파일 985 PASS/1 FAIL을 대체하지 않는다. RF-074 `test_target_tree_discipline_and_no_forbidden_surface`가 `read_models` 폴더의 **실제 파일 목록과 닫힌 기대 목록을 비교**한다는 점을 원본 코드에서 직접 재확인했다. **오라클 변경 승인 없음**, stage BLOCKED. 동일 테스트 반복 금지.
- **B 즉시 개발:** 기존 RF-001 2경로 sanitation 후보 `0254a5aa`의 안전한 재적용/동등 구현, facade monkeypatch·빈값·예외 parity normal/-O와 UI patchnotes를 **새 소스 SHA**로 제출. RF-020은 30/30 KEEP 기능·소비자 계약 증거를 제출하고 A peer 요청. CI_RED는 별도 peer·hosted exact CI 전 통합 금지. 기존 B-stage 실패만으로 B의 RF-001 개발을 되돌리지 말 것.
- **exact-SHA hosted CI 직접 확인:** `dc475680` 2026-10-23 17:21 UTC push Actions 5개 **completed: Scripts SUCCESS 1, Reporting/Web·Design Guard·Shared·T4 FAILURE 4**. 이는 새 CI 수리 성공이 아니다. 이번 RF-018 문서 커밋의 exact CI **UNKNOWN**. RF DONE **0/93**, 신규 소스 통합 **0**. `main`/실거래/안전 가드/CI 오라클 변경 없음.

## 2026-10-24 04:05 KST — 지팀장 실행: RF-001 코드 접수·RF-020 독립 peer 판정

- **원격 HEAD 실측:** 점검 시작 integration `19c0b1135f5cf8353ba11a1056e21ad56cb32132`, A `d5967afddea79c2da8df0b9e1b2d383b68f429c0` / `sched-15`, B `362ad570caf16a365c6199b27028d84039067c18` / `B-20261023T182320Z`. GitHub 비교 B `744c6e8c..362ad570`: **RF-001 소스 2경로 + UI patchnotes 2경로 + HANDOFF 1경로**. A 신규 소스 없음; A `29339105..d5967afd`는 HANDOFF 1경로.
- **직접 처리 RF-001:** B 소스 후보 `8bde643dffe0312e4be2301e5f93298149a7f99e`의 2파일 diff·원문을 지팀장이 독립 정적 검토. 기존 public facade signature와 dynamic monkeypatch 호출 유지, sanitation helper 분리 확인. B SELF parity script normal/-O 각 exit 0, patchnotes `16ed53e4` 확인. **RF-001 원본에 코드 SHA·수락 테스트·Claude A peer 배정 기록 완료**. A는 정확한 B 후보(소스 `8bde643d`, patchnotes 포함 `16ed53e4`)를 read-only 검증하고 소비자·public import·예외·경계 normal/-O pytest 증거를 제출. `re` facade 전역 제거의 외부 의존성도 확인. **PEER_PENDING / NOT_ADMITTED**; historical B-stage UI inventory FAIL로 소스 개발을 되돌리지 않는다.
- **직접 처리 RF-020:** A `sched-15` 별도 read-only peer에서 B `16ed53e4`의 Monitor 참조 19파일 normal/-O 각각 **528 PASS / exit 0**, Monitor 30/30 blob KEEP 확인. 역사 inventory 파일 포함 시 528 PASS/64 FAIL, integration 기준에서도 같은 역사 테스트 55 FAIL. 지팀장이 **RF-020 원본에 범위 한정 peer 증거 수용**. 전체 RF/CI PASS는 아님; 같은 19파일 반복 금지, B는 파일별 KEEP 근거·외부 계약 보강.
- **RF-018:** B read-only Strategist 소비자 normal/-O 각 **391 PASS/2 FAIL**(historical B-stage inventory); A self 1152 PASS/2 FAIL/57 ERROR와 분리 기록. 47/47 KEEP 정적 증거 유지, 전체 peer PASS/CI PASS는 아님. 동일 실패 반복 대신 CI_RED 별도 해결 대상으로 분류.
- **RF-013 구조 결정:** stage `7e06e979` 신규 9 owner와 RF-074 frozen 33-file inventory는 실제로 충돌. A의 5가지 구조 대안 중 oracle 불변·원소유 RF 보존·유의미한 분할을 동시에 만족하는 후보는 없음. **이번 회차 RF-074 oracle 수정/허용 목록 확대 승인하지 않음.** 9파일 stage는 BLOCKED로 보존하고 RF-001/020/018 검증을 우선; A/B 동일 41·153/1 재실행 금지. 필요시 추후 별도 명시 승인으로만 RF-074 역사 계약 범위 재설계.
- **hosted CI 직접 재조회:** integration `19c0b113` 2026-10-23 18:04 UTC 5 runs 모두 completed: Scripts **1 SUCCESS**, Shared/Reporting-Web/Design Guard/T4 **4 FAILURE**. 새로운 문서 커밋 exact-SHA CI는 아직 UNKNOWN. CI_RED `a0493b60` peer·exact CI 부재, 통합 금지. **RF DONE 0/93, 신규 소스 통합 0**. main·실거래·안전 가드·CI oracle 불변.

## 2026-10-24 04:40 KST — RF-001 peer 수용·통합 입력 분리 (지팀장 확정)

- **원격:** integration 직전 `50a93793`, A `46d90a5a` / sched-16, B `19e958a4` / RUN `B-20261023T183030Z`. A가 B source `8bde643d`를 detached 독립 검증: normal/-O parity `PARITY_OK`, 40 consumer tests에서 후보·parent 동일 **806 PASS / 102 FAIL / 116 ERROR**(실패/오류 node 차이 0). **RF-001 `PASS_SCOPED` 수용**, 전체 PASS 아님. RF-001 원본에 증거 반영.
- **지팀장 직접 확인:** integration과 B parent `744c6e8c`의 RF-001 2개 source blob 동일 → **향후 2파일만 선별 가능**. B HEAD와 integration의 RF-001 33파일 중 **19파일이 다르므로 브랜치 전체 merge 금지**. B patchnotes는 기존 integration 355 entries를 유지하고 신규 sanitation entry **1개만 추가**해야 함(후보 349개 JSON으로 덮어쓰기 금지).
- **다음 B:** RF-001 33/33 KEEP/MOVE/WRAPPER 전수 근거와 저장소에서 재현 가능한 focused normal/-O PASS 시험 제출(임시 parity 스크립트만으로 완료 불가). RF-020은 이미 확인한 19 consumer×528 PASS 반복 금지; 미확인 side-effect·RF-026 경계만 검증. **다음 A:** 새 B 증거가 생기면 그 범위만 독립 read-only peer. RF-013 stage `7e06e979`는 RF-074 inventory BLOCKED 유지. CI_RED `a0493b60` 별도 peer/exact CI 미충족. `50a93793` hosted **1 PASS / 4 FAIL**, 새 문서 SHA CI UNKNOWN. **RF DONE 0/93, 신규 source 통합 0**.

## 2026-10-24 05:44 KST — 지팀장 독립 소유구조 검증·교차 안전 소유권 결정

- **원격:** 시작 integration `05367a23`; A `8d785acf` / `sched-18`(HANDOFF 갱신, A 코드 `a21401db` 불변); B `0d011a7e` / `B-20261023T184120Z`(코드 `8bde643d`, patchnotes `16ed53e4` 불변). A는 B의 focused 60/60 normal/-O를 별도 read-only 재현했다고 보고, B의 33/33 분류는 새 근거. 새 A/B 소스 커밋 없음.
- **지팀장 직접 수행 RF-001:** GitHub B HEAD에서 CSV RF-001 **33/33 소스 원문/blob 독립 열람**, 정확히 **4행 alias 16 + 호환 facade 3 + owner 14** 정적 분류를 확인하고 [RF-001](../plan/verification/codex/RF-001.md)에 기록. `data_access_core.py`는 2,308행으로 owner 책임·side effect 동등성 검증이 여전히 필요. **OWNER_MAP_STATIC_VERIFIED**, 그러나 2-source PASS_SCOPED를 RF 전체 PASS로 승격하지 않음. B는 core/19개 divergent 파일의 소비자 계약과 2-file 선별 admission 근거를 집중 보강, A는 새 증거만 peer 검증. **전체 브랜치 병합 금지**.
- **지팀장 직접 수행 RF-026/RF-021:** 순환 import 3파일의 BASE↔integration Git blob **3/3 동일**을 확인해 **기준선 기존 결함**으로 분리. `exit_policy.py`는 RF-026, `monitor_exit/__init__.py` 및 `policy_map_builder.py`는 **RF-021** 소유로 확정. [RF-026](../plan/pending/RF-026.md)에 정확한 import 체인·소유권·read-only 검증 게이트를 기록. **RF-021 패키지 export 변경 후보는 명시적 안전 승인 전 소스 수정 금지**, RF-020 작업에 섞지 않음.
- **게이트:** 이번 회차 실제 신규 runtime 테스트 `NOT_RUN`, 새 source integration `NOT_RUN`, 새 SHA hosted Actions PR-only/combined-status 조회는 빈 결과여서 **UNKNOWN(PASS 아님)**. 기존 CI_RED 1/4 및 RF-013/RF-074 BLOCKED, CI_RED `a0493b60` peer/exact CI 미완 유지. **RF DONE 0/93**, main/실거래/안전가드/CI 오라클 불변. 위 두 소유권·정적 검증은 새 증거이나 런타임/통합 완료가 아니다.

## 현재 검증 상태와 역사

- 마지막 직접 확인 `c4ae36f5`의 5개 hosted Actions **1 PASS / 4 FAIL** (job 완료 재조회); 이번 문서 갱신 SHA의 CI는 **NOT_RUN/UNKNOWN**. 과거 `b768b2b3`의 필수 6/6 PASS는 다른 SHA의 이전 증거이며 현재 GREEN이 아니다. CI 수리 후보는 아직 integration 미반영.
- 합성 `d73be191`과 PR31은 normal/`python -O`·독립검증·exact-SHA hosted CI 이전에 통합 금지.
- 역사적 `DOC-A` · `DOC_FREEZE` · `P1.5.2 OPEN` · `P1.5.3`, Issue #20과 Issues #16–#19 CLOSED는 provenance. 구 BATCH/T00 재활성 및 불필요 Issue 댓글 금지.

## 두 클라우드 예약의 공통 한 줄 프롬프트

`Agentra P1.5 {Claude A|Codex B}: GitHub integration/p1.5의 CURRENT와 D00/D01/D02를 따른다. 매 실행 배정 RF 전부 개발·normal/-O·patchnotes·SHA push 후 작성자 verification 큐에 인수인계하고, 상대 검증 큐는 별도 독립 읽기 전용 세션으로 검증한다. 독립 PASS한 정상 RF만 분리 통합·exact-SHA CI 확인, 예외는 GPT 승인 대기. 상대 CLI 호출·무승인 브랜치·force·main·실거래 금지. 각 RF SHA·테스트·검증·CI·BLOCKED만 보고한다.`
