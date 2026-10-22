# Trading Agent System — Detailed Patch Notes Timeline

## 2026-10-20 · P1.5 BATCH05 FOLDER SCALE FOUR DELIVERABLES AND LOCAL CI 20261020
**Stage:** BATCH05 개발 범위 승인 (DOCS ONLY) · **Tags:** PROCESS · REFACTOR · TEST · SAFETY

- 지팀장 사용자 승인: Claude/ Codex 각각 **3~4건이 아닌 4개 연결된 실질 개발 묶음**, 이전의 약 2~3배 폴더 단위 분해. Claude는 Reporter 운영 화면·상태·기간·메트릭 약 4,625줄, Codex는 Operator Brief 입력·Monitor/Market·섹션·압축/정제의 4개 묶음(9개 명시 파일)을 서로 충돌 없이 진행. 정확한 경로와 중단 조건은 `docs/refactor/work_orders/P15_BATCH05_FOLDER_SCALE_REPORTING_AND_OPERATOR_BRIEF_20261020.md`.
- **두 개발자 최종 보고 양식 통일:** Claude BATCH04-A 형식의 SHA/변경 경로/4개 산출물/전후 코드 크기/입출력 동등성/normal·-O/적대적 변형/LOCAL_CI·차단/NOT_RUN을 담고 마지막에 반드시 실제 호출별 `티키타카 실행 리스트` 표를 출력. Codex의 간략 보고만으로 핸드오프 종료 금지.
- 지난 Claude `4dbbfa34`: 원본 AST·문자열 및 출력 바이트 증명, normal344/-O344, Codex child exit0 소스 PASS, 검토자 pytest NOT_RUN, Owner 545/524줄 SIZE_DEFERRED, GPT source admission pending. 지난 Codex `57e588d6`: 자체 normal113/-O113, Claude child exit0 소스 PASS/독립79/-O79, 보조 JSON 검사 권한 거부1, 독립 patchnote 리뷰 미완료로 **REVIEW_COMPLETION_BLOCKED** 별도 유지.
- **로컬 CI 문제를 분리하여 진단:** reviewer Python/JSON 명령 차단은 안전하게 승인된 원형 pytest 명령 또는 NOT_RUN/BLOCKED로 기록하고 권한 거부를 우회하지 않음. Hosted Reporting T3 Linux는 SHA `54bebe5` 객체 누락으로 5/6 상태 유지. 이전 거부된 workflow 수정·우회 불허. 읽기 전용 진단은 hosted CI PASS가 아님.
- **docs-only commit:** CURRENT, D00/D01/D02, 새 BATCH05 지시서, forward queue, UI JSON/MD 패치노트 **337/337** 기록. 신규 로컬 CLI·소스 개발·통합 CI는 이 커밋으로 실행되지 않았음. main·실거래 불변.

Sources: `docs/refactor/work_orders/P15_BATCH05_FOLDER_SCALE_REPORTING_AND_OPERATOR_BRIEF_20261020.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/refactor/work_orders/P15_FORWARD_DELIVERY_QUEUE_20261020.md`.

## 2026-10-20 · P1.5 BATCH04 BIG PARALLEL REPORTING AND CONTEXT 20261020
**Stage:** BATCH04 두 파트 대형 개발 승인 (DOCS ONLY) · **Tags:** PROCESS · REFACTOR · TEST · DOCS

- 사용자 승인으로 기존 Claude `ead33ca`와 Codex `8fd49dd` 브랜치의 다음 실질 개발을 동시에 활성화합니다. Claude는 약 1,700줄 Strategist LLM Summary의 품질/읽기 모델과 Markdown 출력을, Codex는 545줄 Commander Decision Context와 323줄 Skill Hydration의 순수 Projection을 함께 담당합니다. 각 파트 2개의 연계 책임 경계, 테스트, 실제 교차검증을 한 묶음으로 수행합니다.
- 파일 소유권과 계약은 `docs/refactor/work_orders/P15_BATCH04_LARGE_PARALLEL_REPORTING_AND_CONTEXT_20261020.md`에 정확히 고정합니다. 외부 API·시간·환경·뉴스/LLM/거래 판단 및 Executor·Supervisor·Broker·UEF/Step5C 안전 책임은 이동/완화하지 않습니다. normal/`-O` 및 BASE 동등성/변형 검출, 기존 CLI에서 직접 상대 검토 CLI 호출, 마지막 `티키타카 실행 리스트` 보고를 의무화합니다.
- Codex 이전 `8fd49dd`는 실제 Claude 23/23 normal/-O, exit0 PASS로 독립 검증 완료했으나 **통합 완료는 아닙니다**. 기존 B 통합 CI 5/6, T3 Git SHA `54bebe5` 객체 누락은 그대로 남고 거부된 workflow 수정을 우회하지 않습니다. main·실거래는 불허합니다.
- 이 커밋은 CURRENT/작업 큐/새 BATCH04 지시서/패치노트 JSON·MD만 작성합니다. 로컬 CLI 세션을 실행하거나 소스·통합 CI를 통과시킨 것이 아닙니다. UI 패치노트 **336/336**.

Sources: `docs/refactor/work_orders/P15_BATCH04_LARGE_PARALLEL_REPORTING_AND_CONTEXT_20261020.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/refactor/work_orders/P15_FORWARD_DELIVERY_QUEUE_20261020.md`.

## 2026-10-20 · P1.5 PEER CLI NO PROMPT ISOLATED REVIEW AND TIKI TAKA LEDGER 20261020
**Stage:** D00/D01/D02 개발 운영 규칙 · **Tags:** PROCESS · DOCS · SAFETY

- 제품 책임자 지시에 따라 개발자가 자기 CLI에서 상대 검토 CLI를 직접 호출할 때, **OS 수준 소스 읽기 전용 격리·자격증명 제거·테스트 임시 경로 분리**가 실제로 확인된 경우에 한해서 승인 프롬프트 생략 플래그를 사용하도록 명시합니다. Claude 검토는 `--dangerously-skip-permissions`, Codex 검토는 `--dangerously-bypass-approvals-and-sandbox`를 사용할 수 있으나 운영 Windows나 writable/source/trading 자격증명이 있는 환경에서 무제한 호출할 수 없습니다. 검토자는 코드 수정/커밋/푸시/중첩 CLI 호출 금지입니다.
- CODEX B `8fd49ddf`는 기존 Claude 하위 검토에서 pytest 명령 파이프라인이 거부되어 **BLOCKED**, 종료 코드 0만으로 PASS가 아닙니다. 이번 명시적 승인 아래 안전 격리 확인 후 1회 새 독립검토만 허용합니다.
- CLAUDE A `41ca719a` quant projection 335줄 및 `ead33ca` Reporter Feedback projection 371줄은 개발자 보고에 따른 로컬 Codex 검토 PASS로 기록하되 통합 CI 및 owner contract 승인과 구분합니다.
- **모든 주 개발자 최종 응답 마지막에는 `티키타카 실행 리스트`**: 실제 CLI 호출 회차/정확한 SHA/옵션/프로세스 exit/명시 판정/독립 테스트/NOT_RUN/실제 REWORK 및 새 SHA. 과거 차단도 표시하고 인위적인 재검증은 금지합니다.
- 앞으로 승인된 개발 묶음은 2–4개의 연결된 실질 구현 산출물로 설계합니다. CI T3 원본 Git object 누락, 워크플로 변경 거부, main/실거래 금지는 그대로 유지됩니다. 현재 커밋은 문서·UI 패치노트만 변경합니다.

Sources: `docs/ENGINEERING_DELIVERY_POLICY.md`, `AGENTS.md`, `CLAUDE.md`, `docs/refactor/work_orders/CURRENT.md`.

## 2026-10-20 · P1.5 BATCH03 A THREE IMPROVEMENT ATTEMPTS AND AUTO CONTINUE 20261020
**Stage:** Claude BATCH03-A 구조 개선 3회 제한과 후속 개발 연결 · **Tags:** PROCESS · DOCS · SAFETY

- Claude 최신 `2e47a887` 소스는 로컬 normal/-O 각 246 PASS, 자체 로컬 `codex exec` PASS 보고. 새 projection Owner 약 443 physical LOC이며 `_promotion_candidate` 내 환경 정책 조회가 순수 계산 책임에 혼입되어 있어 지팀장이 구조 개선을 지시했습니다.
- **최대 3번** 실질적인 구조 개선을 시도합니다. 1차는 `_promotion_candidate`/연관 `_shadow_readiness`를 기존 facade로 복원해 실제 환경변수 조회와 호출 순서를 유지하고, 순수한 9개 계산기만 새 Owner에 남기는 방안입니다. 개선 후 테스트 normal/-O, BASE 바이트/예외/호출/효과 동등성, 적대적 변형 검출 및 개발자 본인 CLI의 `codex exec` 읽기 전용 재검증은 유지합니다.
- 세 번 시도 후 **크기만 미달이면 `SIZE_DEFERRED`**, 안전·동작·계약 자체가 실패하면 `BLOCKED_SAFETY_OR_PARITY`로 정확히 표기하고 미검증 소스는 통합하지 않습니다. 성공하면 세 번을 억지로 채우지 않습니다.
- **그 다음 Claude는 기존 CLI/브랜치에서 독립적인 Reporter feedback pure aggregation 개발로 진행**합니다(사용자 '마킹하고 넘어가' 승인에 따른 조건부 READY, 허용 경로/테스트는 BATCH03 지시서에 고정). Codex B 공동 계약 개발은 계속 병렬입니다. 별도 Codex 검토 인폼 없음.
- 지시서/CURRENT/사전 작업큐/패치노트 JSON·MD만 수정하며 기존 333건 보존 후 **334/334**로 갱신했습니다. 소스·실거래·main·CI 계약 변경 없음.

Sources: `docs/refactor/work_orders/P15_BATCH03_PARALLEL_CONTRACT_AND_QUANT_20261020.md`, `docs/refactor/work_orders/P15_FORWARD_DELIVERY_QUEUE_20261020.md`, `docs/refactor/work_orders/CURRENT.md`.


## 2026-10-20 · P1.5 PROACTIVE TWO LANE FORWARD DELIVERY QUEUE 20261020
**Stage:** 지팀장 선행 준비 큐 (개별 실행 승인 아님) · **Tags:** DOCS · PROCESS

- 지팀장은 매번 개발 결과를 받은 후 계획하지 않고 **현재 ACTIVE → 후속 후보 READY_DESIGNED → 승인 확인 AUTHORIZED_READY → 실제 PEER_PASS/INTEGRATION → 새로운 SHA CI**가 연결되도록 상시 큐를 준비합니다. 현재 BATCH03 양 파트 소스 개발은 유지합니다.
- 기존 B 통합 SHA `2f159b6`의 hosted CI 5/6 성공, 이후 문서 SHA `42314ed`의 4/5 성공과 동일 T3 1개 `fatal: bad object 54bebe5` 병목을 명확히 구분합니다. 보안 정책이 거부한 CI 워크플로 수정을 다른 경로로 우회하지 않습니다.
- **Claude 다음 후보:** `reporter_feedback.py` (619줄) 순수 피드백 집계 / Writer·IO 분리. **Codex 다음 후보:** `build_decision_context.py` (545줄) 캐시 메타데이터·상태 뷰 분리(뉴스/시드/시계/정책 효과 보존). **두 후보는 사전 설계 상태이며 실제 코드 수정은 별도 승인 후에만** 진행합니다.
- Reporter A 계약 수용 → Reporter 소스 선별 통합 → quant shadow 신규 owner 별도 검증 → P1.5.11 전체 회귀/UEF/Docker/UI → 사용자 승인 후 후속 단계라는 의존성을 정리했습니다. 개발자 자신의 로컬 `claude -p`/`codex exec` 검증은 필수이며 메인/실거래 권한은 없음.
- 작업큐·CURRENT·패치노트만 수정, 기존 332건 보존 후 **333/333**.

Sources: `docs/refactor/work_orders/P15_FORWARD_DELIVERY_QUEUE_20261020.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/refactor/p1_5_p1_6_master_plan.md`.


## 2026-10-20 · P1.5 BATCH03 PARALLEL CONTRACT AND QUANT WORK ORDER 20261020
**Stage:** P1.5 BATCH03 개발 지시 (양 개발 파트 병렬) · **Tags:** DOCS · PROCESS · TEST

- `integration/p1.5@2f159b6`의 필수 CI 6개는 **5 PASS / 1 FAIL**입니다. Reporting Regression T3에서 immutable 원본 `54bebe5` Git 객체 부재로 `git diff` 종료 128이 확인되었습니다. 지팀장의 직접 CI 쓰기는 보안 정책으로 거부되어 정상 승인 경로가 확정되기 전까지 수정 완료를 주장하지 않습니다.
- **Codex DEV-B** (기존 `cd5a7f5`)는 Claude A `e92950d`의 최신 Reporter 소스를 정확한 버전으로 수용할 공유 계약과 정상/변형 회귀 테스트를 개발합니다. 기존 역사적 R7 313, Monitor 14/20, S5/B 동결 안전 검증은 유지합니다.
- **Claude DEV-A** (기존 `e92950d`)는 1,426줄 규모 quant shadow candidate Reporter 평가의 결정론적 계산 일부를 한 개의 새 read-only projection owner로 이동하고, 입출력/JSON·Markdown 바이트 및 streaming OOM 경계를 보존하는 회귀 테스트를 구현합니다.
- 각 주 개발자는 자기 로컬 CLI에서 상대 CLI를 직접 실행해 실제 교차 검증하고 REWORK시 새 SHA로 재검토합니다. 공통 파일 동시 쓰기는 금지하며 UI 패치노트는 지팀장이 통합 시 병합합니다. 기존 331건 기록 보존 후 **332/332**.
- 이 문서 변경은 코드 구현/로컬 개발 실행/새 CI PASS가 아닙니다. `main`/실거래/배포 승인 없음.

Sources: `docs/refactor/work_orders/P15_BATCH03_PARALLEL_CONTRACT_AND_QUANT_20261020.md`, `docs/refactor/work_orders/CURRENT.md`, `.github/workflows/p152-r2c-residual-regression.yml`.


## 2026-10-20 · P1.5 B PEER VERIFIED SELECTIVE INTEGRATION CANDIDATE CI PENDING 20261020
**Stage:** P1.5 B source selection, composed-SHA CI pending · **Tags:** REFACTOR · INTEGRATION · TEST

- 지팀장은 Codex `cd5a7f59e1d374617cc668e6e82c32f3284cde43`에서 검증된 **B Operator UI 4개 런타임, 공유 계약과 테스트 9개, 총 13개 코드/테스트 파일**만 실제 Git blob 그대로 `integration/p1.5`에 선별 반영했습니다. Reporter A 소스·main·거래 권한은 제외합니다.
- 개발자 보고 증거는 normal/`-O` 각각 622 PASS, Codex 자체 로컬 `claude -p` 검토 PASS(실제 종료 0, 독립 19건과 기존 음성 8건 PASS, 정보성 지적 3건)이며 통합 CI의 결과와는 구분합니다.
- 기존 통합 UI 기록 327건과 B 고유 기록 3건을 모두 보존해 **331/331**로 갱신했습니다. 기존 S5/R7/Monitor, UEF/Step5C 및 실행 안전 불변 조건을 완화하지 않습니다.
- **실제 새로운 통합 SHA 필수 GitHub CI가 PASS하기 전에는 INTEGRATED라고 판정하지 않습니다.** 전체 pytest, 실데이터, UI 시각 검증, Docker 릴리스는 별도입니다.

Sources: `apps/operator_ui/data_access_core.py`, `apps/operator_ui/data_access_overview_projection.py`, `apps/operator_ui/data_access_trade_index_projection.py`, `apps/operator_ui/data_access_run_detail_projection.py`, `scripts/refactor/shared_strategist_contracts.py`, `scripts/refactor/shared_role_contracts.py`, `tests/test_p15_b_versioned_contract.py`.

## 2026-10-20 · P1.5 CODE BATCH 01 DEV B LIVE OVERVIEW PROJECTION 20261020
**Stage:** P1.5 CODE BATCH 01 developer candidate; integration pending
**Tags:** REFACTOR · TEST

- BASE `4b0c3e0b`의 `load_overview(config)` 실시간 집계·stale daily/reporter/reconciliation 보정을 신규 순수 `data_access_overview_projection.py`로 분리했습니다. 함수는 282→139줄, core는 2754→2612줄입니다. 이미 읽은 입력만 전달하며 IO·경로 우선순위·최종 공개 응답 구성은 기존 facade에 유지합니다.
- strict `allowed is True/False`, NOOP 우선순위, `ts_kst` 우선 날짜 선택, action/key 순서, same-day fallback·reporter snapshot·reconciliation 최대값 우선순위와 helper use-time lookup을 보존합니다. Monitor 동결 Owner·fixture·권한 코드는 변경하지 않습니다.
- Windows Python3.14.2 집중 normal/`-O` 각각98 PASS(기존 UI/read-model81 + 신규17); 분류·날짜·stale 변이4종을 메모리에서 탐지합니다. 고정 BASE와7개 시나리오의 JSON bytes·호출 순서·예외·공개 signature/import를 비교하며 운영 golden을 새로 만들지 않았습니다. 첫 신규 fixture의 operator_summary 부재로 나타난 기존 fallback 분기 실패는 올바른 fixture 문맥으로 수정했고 로그를 보존합니다.
- 커밋 작성 시 새 Claude CLI 독립 읽기 전용 검토는 대기 중입니다. 실제 종료 코드·정확한 candidate SHA·PASS/REWORK/BLOCKED를 별도 인계합니다. 통합 CI·전체 pytest·실데이터24SKIP·운영 HTML/JSON parity·UI build는 NOT_RUN. main·Docker·실거래·운영 배포 승인 없음.

근거: `apps/operator_ui/data_access_core.py`, `apps/operator_ui/data_access_overview_projection.py`, `tests/test_p15_overview_live_projection.py`, `docs/ENGINEERING_DELIVERY_POLICY.md`.

## 2026-10-20 - P1.5 CODE BATCH 02 DEV B TRADE INDEX AND RUN DETAIL PROJECTIONS 20261020
**Stage:** Developer candidate, selective integration pending. **Tags:** REFACTOR / TEST

- BASE `c0c3f808967dc921a956d01a879fe489674cad71`: core 2612 -> 2467 lines; `_trade_report_index` 226 -> 152; `load_run_detail` 272 -> 191. Pure index Owner 225 lines and run-detail Owner 230 lines reuse existing read-model/status helpers through use-time facade lookups.
- Keep discovery, file reads and all path/stat probes in the coordinator, with original priority/ties, linked-record identity, field ordering and exception timing. Reporter lookup, cached brief generation, LLM prompts/call counts and artifact writers stay at their existing boundaries. No change to BATCH01 or Monitor11 owners, safety locks or transaction authority.
- Windows Python 3.14.2 focused normal **116 PASS** (81 existing + 35 new): pinned BASE synthetic JSON/call/exception equality, synthetic HTML bytes, offline real cold/warm generation/cache/file-byte parity and **10 hostile mutations rejected**. Callback addresses, clock/latency and restored fixture mtime were controlled explicitly rather than normalized out of expected outputs. Optimized focused run **118 PASS** includes the paired-note2 checks; normal notes validation is recorded separately.
- Fresh read-only Claude CLI exact-SHA review pending candidate authoring. Hosted integration CI, full pytest, real production frozen snapshots/real-data evidence and UI visual/build **NOT_RUN**. Not final acceptance, deployment or main integration.

Sources: `apps/operator_ui/data_access_core.py`, `apps/operator_ui/data_access_trade_index_projection.py`, `apps/operator_ui/data_access_run_detail_projection.py`, `tests/test_p15_operator_trade_index_projection.py`, `tests/test_p15_operator_run_detail_projection.py`, `docs/ENGINEERING_DELIVERY_POLICY.md`.

## 2026-10-20 - P1.5 B SHARED CONTRACT V2 HISTORICAL AND CURRENT ADMISSION 20261020
**Stage:** Developer contract candidate, peer/GPT selective integration pending. **Tags:** REFACTOR / TEST

- Unchanged reviewed B source and developer base `54bebe5ece0ac34c4f45df55c44889c9ce323e95`; historical pre-B tree `4b0c3e0b5f8f24fa3c10d9082b85fab63f15c4c3`. Existing S5/Reporter/Monitor/Broker/UEF/Step5C source and policies remain unchanged.
- Keep original historical source inventories and five-function/eight-helper proofs; separately admit exactly four runtime and three regression paths from B. Validate actual B contents before historic projection; restore three named UI definitions/import groups to the entire pre-B AST. Current scope rejects unapproved source/test/fixture paths and byte drift, including staged/untracked changes.
- Require actual unmutated current stage/runtime PASS before eight old hostile mutations; assert rejection identifies the injected path. Dedicated19 cases add historical/current mutual rejection, fourteen current hostile probes and three real Owner-read mutations. Windows Python3.14.2 final normal620PASS plus paired-note2PASS; optimized622PASS, zero FAIL/SKIP. Includes UI/API, Reporter/Monitor/S5 regressions; final note-text schema checks recorded separately. No test oracle weakening or vacuous PASS.
- Five missing immutable commits fetched by exact SHA. Fresh local read-only `claude -p` review pending candidate authoring; actual SHA/exit/verdict recorded externally after commit. No direct integration, main, Docker, live LLM, production data or alternate reviewer window.
- Hosted composed-SHA CI, full pytest, Linux, genuine production goldens/real-data evidence and UI build/visual acceptance **NOT_RUN**. Prior321 candidate records preserved, new note322; GPT reconciles newer integration notes serially.

Sources: `scripts/refactor/shared_strategist_contracts.py`, `scripts/refactor/shared_role_contracts.py`, `tests/test_shared_strategist_contracts.py`, `tests/test_p15_integration_completion.py`, `tests/test_shared_role_contracts.py`, `tests/test_p15_b_versioned_contract.py`, `docs/ENGINEERING_DELIVERY_POLICY.md`.


## 2026-10-20 · P1.5 PERMANENT MINIMUM IDLE MAXIMUM SUBSTANTIVE PARALLELISM 20261020
**Stage:** D00/D01/D02 상시 운영 원칙 · **Tags:** DOCS · PROCESS

- 지팀장은 코덱스·클로드 **양쪽 개발 파트의 실제 작업 병렬성 최적화**를 상시 책임집니다. 한쪽이 개발·테스트·교차 검증 중이면 다른 쪽에는 범위와 작성 파일이 겹치지 않는 승인된 READY 개발을 배정합니다. 개발자는 상대 주 개발창이 아니라 자기 로컬 셸에서 `claude -p` / `codex exec`를 직접 호출합니다.
- 인위적 대기·짧은 마이크로 태스크·서류 반복 검증을 줄이고, 실질적인 소스 구현·독립 검증·지팀장의 통합/정확한 SHA CI로 이어가도록 합니다.
- 승인된 독립 작업이 없거나 보안/CI가 차단하면 `NO_MORE_AUTHORIZED_READY_SCOPE` / `BLOCKED`로 명확히 보고합니다. 미승인 코드 수정·파일 충돌·권한 우회·억지 작업 또는 백그라운드 실행 주장은 허용하지 않습니다.
- D00·D01·D02 상시 룰과 UI 패치노트 JSON/MD만 수정, 기존 326건 보존 후 **327/327** 동기화. 소스/트레이딩/메인 변경 없음.

Sources: `docs/ENGINEERING_DELIVERY_POLICY.md`, `AGENTS.md`, `CLAUDE.md`.


## 2026-10-20 · P1.5 CLAUDE REPORTER ACTIVE PARALLEL A-P2 20261020
**Stage:** P1.5 source work-order authorization (docs only) · **Tags:** DOCS · PROCESS

- 클로드 주 개발 파트는 대기가 아닙니다. 기존 A 브랜치에서 Reporter 분석 섹션 조립 부분을 기존 read-model owner로 분리하는 **실제 소스 개발**을 병렬로 진행합니다.
- Claude 허용 범위는 기존 Reporter facade/owner, 기존 테스트 2개, 정확한 기존 SHA256 facade guard, UI JSON/MD입니다. 파일 읽기·LLM·메모리 저장·브리지 기록 순서와 JSON/MD 바이트 동등성, normal/-O, 악의적 변형 탐지를 검증합니다.
- Claude가 직접 로컬 `codex exec`를 호출해 검증받고 진짜 REWORK면 새 SHA로 다시 호출합니다. Codex는 별도 B 공통 계약 작업과 로컬 `claude -p`를 계속합니다.
- 양 개발자가 공통 계약에 동시 쓰지 않습니다. 기존 Reporter 글로벌 계약은 여전히 BLOCKED이며 이번 커밋은 소스가 아닌 지시서/CURRENT/패치노트 **326/326**만 수정합니다.

Sources: `docs/refactor/work_orders/P15_BATCH02_DUAL_SUBSTANTIVE_20261020.md`, `docs/refactor/work_orders/CURRENT.md`.


## 2026-10-20 · P1.5 TIKI TAKA PRIMARY DEVELOPER LOCAL CLI SELF INVOCATION 20261020
**Stage:** P1.5 permanent instruction correction, DOCS ONLY · **Tags:** DOCS · PROCESS

- 코개발에서 개발을 마친 뒤 **코덱스 주 세션이 로컬 셸에서 직접 `claude -p` 실행**→실제 stdout/종료 코드 및 판정 확인→진짜 REWORK이면 코덱스 수정·새 SHA·새 `claude -p` 검토를 수행하는 것이 필수 티키타카 절차입니다. Claude가 개발한 코드는 Claude 주 세션이 직접 `codex exec`를 호출합니다.
- **검토용 별도 Claude 주 개발창 시작 인폼은 금지**합니다. 하위 검토 CLI 프로세스는 호출한 개발자 세션에 결과를 반환하고 종료하며, 검토 중 재귀 CLI를 호출하지 않습니다.
- 팀장은 작업 담당 **개발자 CLI에만** 간단한 복붙용 시작 인폼을 제공합니다. 다른 파트에 독립적인 개발 과제가 실제로 있을 때만 두 번째 시작 인폼을 제공합니다.
- 관련 D00·D01·D02 및 현재 작업 지시서·CURRENT를 정정하고 UI JSON/MD 기록을 기존 324→**325/325**로 보존했습니다. 소스나 거래 안전 계약 수정은 없습니다.

Sources: `docs/ENGINEERING_DELIVERY_POLICY.md`, `AGENTS.md`, `CLAUDE.md`, `docs/refactor/work_orders/P15_BATCH02_DUAL_SUBSTANTIVE_20261020.md`, `docs/refactor/work_orders/CURRENT.md`.


## 2026-10-20 · P1.5 TIKI TAKA STRICT TWO DEV PEER RELAY CORRECTION 20261020
**Stage:** P1.5 operative developer review handoff rule; no source change · **Tags:** DOCS · PROCESS · SAFETY

- 지팀장 기존 지시의 **“Codex 직접 통합 → Claude 단발 검토”** 해석을 폐기하고 D00 §3A의 **티키타카 교차 검증**을 적용합니다.
- **Codex 기존 개발 브랜치**에서 승인된 B 소스 및 버전별 엄격 계약을 구현·테스트→커밋하고, 자기 CLI가 **새 읽기 전용 Claude CLI**를 호출합니다. 실제 지적이 나오면 Codex가 수정·새 SHA로 다시 Claude 검토를 요청합니다. **실제 결함 없는 PASS에는 인위적 재검토를 강요하지 않습니다.**
- 장기 실행 중인 **Claude 주 개발 파트는 단순 대기가 아니라 독립적인 읽기 전용 계약 검토에 참여**하고, Reporter 쓰기는 이전 거부를 우회하지 않습니다. Reporter A의 계약 완성 후에는 반대 `codex exec` 검토와 REWORK 루프를 동일하게 적용합니다.
- **GPT만 최종 통합 판단**, 이후 새 통합 코드 SHA 필수 CI를 확인합니다. 허위 변이 테스트 PASS, 기존 S5/R7/Monitor/Strategist/UEF/Step5C 검증 완화 및 `main`·실거래 변경은 불허합니다.
- 변경은 작업 지시서/CURRENT/패치노트 JSON·MD 문서에만 국한되며, 기존 323건 이력 보존→**324/324**.

Sources: `docs/refactor/work_orders/P15_BATCH02_DUAL_SUBSTANTIVE_20261020.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/ENGINEERING_DELIVERY_POLICY.md`.


## 2026-10-20 · P1.5 BATCH02 DEV-A A2 CLASSIFIER BLOCK OWNERSHIP DECISION 20261020
**Stage:** P1.5 source ownership and safety gate arbitration; no source code changed · **Tags:** DOCS · PROCESS · SAFETY

- DEV-A가 기존 Reporter 계약 수정 중 보안 분류기의 `CI Bypass`·`Security Test Removal` 거부를 보고했습니다. **지팀장 결정은 Option 2**: 권한 우회 없이 Claude는 이미 허용된 facade 가드 초안만 normal/`-O` 검사 후 `BLOCKED` 부분 후보로 보존하고, GPT 통합 담당이 공유 계약과 기존 seed 목록, 비공허(nonvacuous) 변이 가드의 최종 책임을 맡습니다.
- BASE 158 PASS 대 A 후보 3 FAIL은 사용자 제공 개발자 결과이며, 변이 테스트 8건은 기본 검사 자체가 실패해 **허위 PASS(검증 불성립)**였으므로 완료로 인정하지 않습니다.
- 기존 R7 313, Monitor/Strategist 계약, Broker/UEF/Step5C 및 구 historical 불변 oracle은 완화/skip/xfail하지 않습니다. GPT 소유 계약은 **A 코드와 함께** 통합 검증해야 하고 별도 파일만 먼저 main/integration에 넣지 않습니다.
- DEV-B의 Operator UI 개발 지시는 유지됩니다. 새 소스 코드는 이번 문서 커밋에 포함되지 않았으며, UI JSON/MD **323/323** 동기화만 수행합니다.

Sources: `docs/refactor/work_orders/P15_BATCH02_DUAL_SUBSTANTIVE_20261020.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/ENGINEERING_DELIVERY_POLICY.md`.


## 2026-10-20 · P1.5 GPT TEAM LEAD COMPACT START INFO RULE 20261020
**Stage:** P1.5 standing operator/developer handoff governance (docs only) · **Tags:** DOCS · PROCESS

- 운영자 요청에 따라 **팀장 인폼은 간략히, 세부 지시사항은 Git 정식 워크오더 및 Issue #20에 기록**하는 상시 규칙을 D00 §5A에 추가했습니다.
- 앞으로 개발 지시를 내린 뒤에는 짧은 커밋/CI 사실 요약 다음 **Claude DEV-A·Codex DEV-B용 각각 독립적인 복붙용 시작 인폼**만 제공합니다. 단일 파트면 해당 파트만 제공합니다.
- 시작 인폼은 `git fetch`, 정확한 Git 작업 지시 경로, Issue #20, 기존 브랜치 유지, 원격 대화창의 진행/교차 검토 표시, 완료 시 SHA·테스트·판정·차단 사항만 보고할 것을 담습니다.
- Git 지시 등록은 로컬 개발 CLI 실행·재개나 실거래 권한 부여가 아닙니다. 기존 Batch02의 변경 허용 목록, 고정 테스트, Broker/UEF/Step5C, `main` 잠금은 그대로입니다.
- D00/D01/D02와 UI 패치노트만 문서 갱신했고 JSON/MD 322/322 동기화를 유지합니다. 새로운 CI의 실행 결과는 별도 SHA 기준 확인 대상입니다.

Sources: `docs/ENGINEERING_DELIVERY_POLICY.md`, `AGENTS.md`, `CLAUDE.md`, `docs/refactor/work_orders/CURRENT.md`.


## 2026-10-20 · P1.5 CODE BATCH02 DUAL SUBSTANTIVE ASSIGNMENT 20261020
**Stage:** P1.5 authorized active developer work order; NO merged code
**Tags:** DOCS · PROCESS · SAFETY

- 운영자 지시에 따라 **기존 격리 개발 브랜치에서** Claude/CodeX 두 파트의 60~120분급 실질적인 후속 작업을 즉시 병렬 배정했습니다. 새 로컬 감시기·워치·워크트리·브랜치는 만들지 않습니다.
- **CLAUDE_DEV_A** `ad4eed21`: Reporter 기존 가드 2개와 전체 shared 역할 계약을 증거 기반으로 재현하고, 원본 R7/313/불변 body/위험 경로 차단을 유지한 채 정밀 버전별 수용 계약으로 전환합니다. 기존 테스트 우회·skip/xfail/의미 없는 allowlist 확장은 불허합니다.
- **CODEX_DEV_B** `c0c3f808`: Operator UI의 trade-report index·run-detail 읽기/표현 영역을 실제 owner로 모듈화합니다. 중복 인덱스 우선순위·같은 타임스탬프·경로 판단·7역할 표기·JSON 바이트·읽기/쓰기 순서를 검증하고 LLM/캐시 쓰기는 원래 호출자에 보존합니다.
- **CI 전량 완료는 소스 개발 시작 조건이 아닙니다.** CI 실패가 있으면 통합 전 조치하며, **선별 통합 후 새 합성 SHA의 필수 CI**가 통합 완료 판정 조건입니다. 두 개발자 후보 PASS와 통합 PASS를 구별합니다.
- 운영자의 원격 앱 화면에 개발·테스트·상호 CLI 검토 요청·지적·실제 수정 과정을 개발자 본인 CLI 대화창으로 표시합니다. 현재 Git 문서 작업은 소스 실행/로컬 세션 시작·main/실거래·Docker 승인이 아닙니다.

Sources: `docs/refactor/work_orders/P15_BATCH02_DUAL_SUBSTANTIVE_20261020.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/ENGINEERING_DELIVERY_POLICY.md`.


## 2026-10-20 · P1.5 COHERENT 1-2H DEV WORK BLOCK POLICY 20261020
**Stage:** P1.5 developer work-order governance; Batch01 candidates remain outside integration
**Tags:** DOCS · PROCESS · SAFETY

- 운영자 지시에 따라 Claude/Codex 각 개발 파트의 단일 업무를 **60~120분급의 실질 코드 개발 범위(2~4개의 인과적으로 연결된 성과)**로 설계합니다. 시간 채우기나 억지 리뷰가 아니라, 코드의 실제 책임/호출자 검토→구현→원본 동등성/적대적 테스트→서로의 CLI 검토→실제 결함 수정까지 일관된 흐름을 요구합니다.
- 원격 앱에서 직접 보는 기본 개발 CLI 대화창에 단계별 진행과 상대 검토 결과를 표시합니다. 별도 상태 관찰기/PowerShell 프로그램/ZIP은 필요 없고 개발 세션 실행·지속 여부를 허위로 표시하지 않습니다.
- Codex DEV-B `c0c3f808`는 독립 Claude 검토 PASS 보고·통합 대기, Claude DEV-A `ad4eed21`은 1차 REWORK→수정→2차 PASS 보고이나 **기존 Reporter 목록·facade 가드 2개 실패**가 있어 아직 통합 허가되지 않습니다.
- 가드 변경은 첫 개발 배치 허용 범위 밖이므로 별도 계약 변경 승인/증거가 필요합니다. 이전 고정 계약을 무조건 약화하거나 skip/xfail 처리할 수 없습니다. 미래 개발 배치 범위도 별도 승인 없이는 활성화하지 않습니다.
- `DOC_FREEZE_ACCEPTED` 역사와 기존 319개 패치노트를 그대로 보존하며 이번 문서 정책 추가로 JSON/MD **320/320** 동기화합니다. 실거래·도커·main 변경, 새 통합 SHA CI 검증은 수행하지 않았습니다.
- 후속 동기화 수정: UI JSON 필수 필드 `impact`가 신규 항목에서 누락되어 GitHub reporting-compat pytest 591 PASS/1 FAIL을 발생시켰고, 본 후속 커밋에서 **기존 스키마 요구사항 그대로 복구**했습니다. 기존 테스트/워크플로/예전 패치 항목은 변경하지 않았습니다.

Sources: `docs/ENGINEERING_DELIVERY_POLICY.md`, `AGENTS.md`, `CLAUDE.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/refactor/work_orders/P15_SUBSTANTIVE_DEV_LOOP_20261020.md`.


## 2026-10-20 · P1.5 D7 OPERATOR ACCEPTED DOC FREEZE 20261020
**Stage:** P1.5 D7 문서 기준선 동결 · **Tags:** DOCS · PROCESS · SAFETY

- 운영자가 `d89cc136a72efea76fe4da67d1c851f418011312` 기준의 **문서 동결을 명시 승인**했습니다. 해당 SHA의 GitHub 5개 워크플로 5/5 성공 및 사용자가 제공한 Codex DOC-E 독립 검토 6파일 한정 PASS를 근거로 합니다.
- 14개 누락 역사적 로컬 경로의 16회 인용, 339 원본 문서의 미검증 전체 inbound 참조, Windows 상호 CLI smoke 미실행, 패치노트 자동 append 도구 보류를 **예외로 수락했을 뿐 PASS로 바꾸지 않았습니다.**
- 동결된 검토 기준 SHA와 이번 동결 기록 커밋은 구별합니다. 이번 커밋 CI는 별도 확인이 필요합니다. 기존 318개 UI 기록은 그대로 두고 본 항목을 추가해 **319/319**로 동기화했습니다.
- [D7 승인 기록](../refactor/DOC_D7_FREEZE_ACCEPTANCE_20261020.md) · [현재 업무 포인터](../refactor/work_orders/CURRENT.md). **`DOC_FREEZE_ACCEPTED`는 `FINAL_ACCEPTED`나 실거래/배포/메인 병합 승인이 아닙니다.** 개발 세션·브랜치 시작도 별도 범위/운영자 지시가 필요합니다.

Sources: `docs/refactor/DOC_D7_FREEZE_ACCEPTANCE_20261020.md`, `docs/refactor/DOC_D7_RELEASE_READINESS_20261020.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/ENGINEERING_DELIVERY_POLICY.md`.

## 2026-10-20 · P1.5 D6 FULL SOURCE EXCEPTION GUARD AND D7 REVIEW READY 20261020
**Stage:** P1.5 D6 품질 게이트 및 D7 독립 검토 준비 · **Tags:** DOCS · TEST · CI · SAFETY

- 이전 HEAD `974eb9d1`의 패치노트 317개 항목·출처 1,017건 전수를 확인했습니다. 기존 트리 확인 가능 997건, 역사적 누락 로컬 경로 14개에 대한 16회 인용, GitHub 외부 URL 4건이며 신규 미분류 누락은 없습니다.
- 기존 T4·R2C 워크플로의 문서 검증 단계만 보강합니다. 모든 출처를 검사하고 허용되는 과거 14/16 예외 외 신규 누락, 경로 탈출, 허용되지 않은 외부 URL, 버전/제목 중복에 실패하도록 구성했습니다. 기존 UEF·Step5C·브로커·회귀 테스트는 그대로 유지합니다.
- D00/D01/D02의 상호 `claude -p` / `codex exec` 및 비재귀 읽기 전용 리뷰 계약도 확인합니다. 낡은 개발 미착수 문구 자체에 CI를 묶지 않고, Issue #20/DOC_FREEZE의 실제 게이트를 검사합니다.
- [D7 판정표](../refactor/DOC_D7_RELEASE_READINESS_20261020.md)와 현행 진입점을 정리했습니다. **REVIEW_READY ≠ DOC_FREEZE_ACCEPTED**이며 독립 검토, 신규 SHA CI, 운영자 명시 승인이 남아 있습니다. 현재 `main`·실거래·소스 개발은 변동 없습니다.

Sources: `docs/refactor/DOC_D7_RELEASE_READINESS_20261020.md`, `docs/refactor/DOC_PATCHNOTE_SOURCE_PROVENANCE_20261019.md`, `.github/workflows/p15-integration-t4-regression.yml`, `.github/workflows/p152-r2c-residual-regression.yml`, `docs/refactor/README.md`.

## 2026-10-20 · P1.5 D4 HIGH RISK FAMILY AUTHORITY QUARANTINE 20261020
**Stage:** P1.5 DOC D4–D6 risk-based convergence · **Tags:** DOCS · PROCESS · SAFETY

- P1.5 현재 권한·스냅샷 등 주요 리팩터링 문서 35개 및 관련 개발·평가·리포트·실행 문서 17개를 실제로 읽고 혼동 위험이 있는 문서 14개에 **상단 주석만 추가**했습니다. 기존 본문과 과거 명령/평가 증거는 모두 보존했습니다.
- 구 Gemini 검증 체크리스트, 2026-06 Q8/Q9 “current” 기록, `--mode live` 구 명령 예시, Reporter 예전 구현 계획, f555/5cb 고정 아키텍처 스냅샷을 현재 작업지시·실거래 권한으로 사용하지 않도록 분리했습니다. 현재 운영 원칙은 D00/D01/D02, 안전 규칙 및 Issue #20 우선입니다.
- 신규 안내문 14개의 내부 상대링크 32건은 원격 트리에서 대상 경로 모두 확인했습니다. 339개 원본 전체 의미/유입 참조 완료 주장이나 문서 동결 승인은 하지 않습니다.
- 직전 SHA `781aec98`의 관측된 5개 CI 워크플로는 5/5 성공했으나 Target Tree 별도 워크플로는 해당 SHA에서 미실행이며, **이번 신규 커밋 CI는 별도 검증** 대상입니다.
- **D7 DOC_FREEZE HOLD / main HOLD / 실거래 HOLD**. 전체 교차참조·독립 감사·운영자 명시 승인은 여전히 남아 있습니다.

Sources: `docs/refactor/DOC_D4_D6_CONVERGENCE_EVIDENCE_20261020.md`, `docs/dev/gemini_review.md`, `docs/evaluation/current_operating_baseline.md`, `docs/execution_plan/runtime_entrypoint_unification.md`, `docs/report_plan/report_plan.md`, `docs/refactor/architecture/current_overview.md`, `docs/q13_q14_validation/README.md`.

## 2026-10-20 · P1.5 DOC D4 D6 CANONICAL AUTHORITY AND BOUNDED LINK AUDIT 20261020
**Stage:** P1.5 documentation convergence · **Tags:** DOCS · PROCESS · SAFETY

- D4 현재 권한: D00/D01/D02와 Issue #20의 우선순위를 유지하고, 구 `docs/dev/workflow.md`의 Codex→Gemini 작업 절차는 역사적 기록으로만 분류했습니다. `docs/PATCH_NOTES.md`와 Q9-era `docs/evaluation/README.md`도 현재 UI 소스/활성 작업지시로 오인되지 않도록 출처를 명시했습니다.
- D5 보존: 339개 원본 경로 모두 현재 트리에 있으며 292개는 원본 blob과 같고 47개는 이후 변경됐습니다. 339개 전체의 내용·유입 참조 검증은 미완료입니다. 14개/16회 과거 누락된 로컬 출처와 외부 GitHub URL 4개를 분리하고 원문을 보존합니다.
- D6 범위형 점검: 현행 문서 19개에서 일반 Markdown 상대링크 86건을 확인했으며 현재 트리 기준 누락 대상 0건입니다. 모든 링크 형식/앵커/코드 유입 참조 검증이나 새 SHA의 CI PASS를 주장하지 않습니다.
- D7 `DOC_FREEZE`는 아직 HOLD이며 독립 검증·예외 수용·사용자 승인 전에는 새 코드 개발 워크트리, main 병합, 실거래 권한을 열지 않습니다.

Sources: `docs/refactor/DOC_D4_D6_CONVERGENCE_EVIDENCE_20261020.md`, `docs/refactor/README.md`, `docs/00_HOME.md`, `docs/dev/workflow.md`, `docs/PATCH_NOTES.md`, `docs/evaluation/README.md`.

## 2026-10-20 · D00 D01 D02 DIRECT CROSS CLI DEVELOPMENT RELAY RULE 20261020
**Stage:** Documentation governance and developer operating contract · **Tags:** DOCS · PROCESS · SAFETY

- 운영자 지시를 **D00·D01·D02 상시 규칙**으로 격상했습니다. 한 PC에 장기 실행 중인 두 주 개발 세션은 모두 개발자입니다: Claude DEV-A(Reporter/Strategist/Scanner), Codex DEV-B(Monitor/Commander/Operator UI). 작업 영역은 별도 승인된 writer 경계로 구분합니다.
- 개발 배치 완료 시 각 개발자는 반대편 CLI를 **새 비대화형 검증 세션**으로 직접 호출합니다: Codex 개발자 → `claude -p`, Claude 개발자 → `codex exec`. 상대의 상주 개발 세션을 중단하거나 새 runner/daemon/scheduler를 만들어 호출하지 않습니다.
- 검증자는 정확한 BASE/CANDIDATE SHA만 읽기 전용으로 검증하고 `PASS/REWORK/BLOCKED`와 실제 테스트 근거를 원 개발자에게 반환한 뒤 종료합니다. 검증자가 다시 CLI를 중첩 호출하는 재귀는 금지하며 REWORK는 개발자의 신규 SHA 수정/재검증으로 처리합니다.
- D00의 이전 한 방향 개발→감사 순서를 양방향 동시 개발→상대 새 CLI 검증으로 대체했고, D01과 D02에 각각 개발 모드 및 상대 호출로 들어온 검증 전용 모드를 명시했습니다.
- **DOC_FIRST 및 DOC_FREEZE 미승인 상태는 변경 없음**, 승인된 소스 개발 착수/작업공간 생성·삭제/실거래 권한/메인 병합으로 간주하지 않습니다. PC에서 실제 CLI 왕복 호출은 NOT_RUN이며, 새 커밋 CI도 검증 전입니다.

Sources: `docs/ENGINEERING_DELIVERY_POLICY.md`, `AGENTS.md`, `CLAUDE.md`.

## 2026-10-20 · P1.5 T3 PINNED SOURCE HYDRATION AND SCANNER HISTORICAL STAGE FREEZE 20261020
**Stage:** P1.5 integration CI and historical contract repair · **Tags:** CI · TEST · SAFETY · DOCS

- [Shared Candidate #26](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39264502074) 정상 PASS(4개 contracts Job 각 3,307 PASS/24 SKIP, API 2개 PASS) 확인. T4·Reporting 2개의 T3 원본 조회 2건과 Reporting/Web의 Scanner 범위 오류 3건 및 S1 원본 조회 1건이 다른 워크플로에 남아 있었습니다.
- T3 및 S1에서 참조하는 `6849bed4`(Strategist node), `613a945d`(Operator UI 입력 projection)의 원본 Git 트리 blob 존재를 확인하고, 세 관련 CI 워크플로에서 **얕은 fetch 없이** 명시적으로 확보·검사합니다.
- Scanner V2-053·V3-055·V4-056은 원래 이관 종료 커밋 `ca835e9d`, `4df172e1`, `9eec995c`에서 각 BASE 대비 변경 범위 검사를 수행합니다. 기존 금지 경로/원본 byte hash/alias/golden 비교를 유지하며 단계 종료 SHA의 HEAD 조상 관계도 확인합니다.
- 기존 `a50d6e47` 소스 동결 검사를 확장 허용하지 않고, 변경된 Scanner 테스트 3개만 **정확한 Git blob SHA**로 봉인합니다. 나머지 런타임·테스트·Broker/UEF/Step5C 보호, 실거래 차단, 24 real-data SKIP는 그대로 유지합니다.
- 새 SHA의 Linux/Windows 호스팅 CI 및 독립 감사는 아직 완료되지 않았으며 DOC_FREEZE/main은 HOLD입니다.

Sources: `.github/workflows/p15-integration-t4-regression.yml`, `.github/workflows/p152-r2c-residual-regression.yml`, `.github/workflows/p15-integration-crossbranch-compat.yml`, `scripts/refactor/shared_strategist_contracts.py`, `tests/test_p167_v2053_scanner_context_migration.py`, `tests/test_p171_v3055_scanner_projection_migration.py`, `tests/test_p172_v4056_scanner_policy_migration.py`.

## 2026-10-19 · P1.5 SHARED CI NONSHALLOW ANCESTRY AND FAST SMOKE 20261019
**Stage:** CI historical DAG and test quality · **Tags:** CI · TEST · SAFETY · DOCS

- [Shared Candidate #39259157565](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39259157565)에서 Linux/Windows 4개 Job 각각 3,296 PASS / 11 FAIL / 24 SKIP, API 2/2 PASS 확인. SHA 객체 조회 자체는 성공했으나, `git fetch --depth=1`이 runner의 완전한 이력을 shallow로 바꿔 T1/T2/T4 조상 검증을 깨는 원인을 로컬 Git 재현으로 검증했습니다.
- 과거 SHA 7개의 실제 조상 관계는 GitHub 원본에서 확인했습니다. `--depth=1`을 제거하고 비shallow 상태 및 각 SHA 조상 검사를 pytest 이전 fail-closed로 수행합니다.
- 역사가 갈라진 두 SHA에서 `git diff`는 양쪽 트리를 직접 비교하지만 GitHub compare는 merge-base 기준이므로, 과거 병렬 11개를 **전부 존재해야 하는 목록이 아닌 정확히 허용된 상한 목록**으로 교정했습니다. 외부 changed/untracked 경로의 기존 금지는 유지합니다.
- 실패했던 11개 테스트를 빠른 초기 검사로 실행한 뒤에만 기존 전체 suite를 실행합니다. fast gate 실패로 evidence output이 없으면 artifact upload를 건너뛰어 빈 경로 업로드를 방지합니다. 기존 failed full-suite evidence는 유지합니다.
- Broker/UEF/Step5C/golden/pytest 원본 동등성 및 실거래 권한은 변경 없음. Reporter 범위 검사와 24 SKIP는 별도 미해결로 남아 있으며 신규 SHA CI PASS 미검증, DOC_FREEZE/main HOLD.

Sources: `.github/workflows/p15-shared-candidate.yml`, `scripts/refactor/shared_strategist_contracts.py`.

## 2026-10-19 · P1.5 SHARED CI HISTORICAL PARALLEL STAGE PARTITION 20261019
**Stage:** CI contract historical scope proof · **Tags:** CI · TEST · SAFETY · DOCS

- [GitHub Actions 실행 #39254507133](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39254507133)에서 모든 계약 Job은 3,304 PASS / 3 FAIL / 24 SKIP, API Job 2/2 PASS였습니다. 남은 3건 모두 삭제된 역사 브랜치 SHA `1e1e78a9` 기준 `git diff` 실패로 수렴했습니다.
- 정확한 과거 SHA `1e1e78a9061f9a56c3ce1410202ce5193c6af679`, `c5fe8a9a59788cd7cf1eb1d72f9aa8b22a40f7ca`를 명시적으로 fetch하고 커밋/차이 계산 여부를 pytest 이전에 검사합니다.
- 과거 분기 간 diff 47개 중 기존 S5/공유/문서 허용 36개와 별도 Reporter·Monitor·CI 작업 11개를 분리했습니다. **11개는 과거 고정 비교에서만 인정되며 외부 changed/untracked 입력에는 여전히 불허**합니다.
- SHA 고정된 공유 계약 테스트 파일·기존 negative mutation·19-path 승인 source·Broker·Supervisor·Executor·Step5C·UEF·golden·real-trade 안전 및 CI matrix는 수정하지 않았습니다. 24 SKIP, DOC_FREEZE, main HOLD 유지.
- 신규 SHA CI PASS는 **아직 확인되지 않았습니다**.

Sources: `.github/workflows/p15-shared-candidate.yml`, `scripts/refactor/shared_strategist_contracts.py`.

## 2026-10-19 · P1.5 SOURCE SCOPE EXACT TEST PIN CORRECTION 20261019
**Stage:** CI contract exact-scope correction · **Tags:** CI · TEST · SAFETY

- `cfac9b71..05e91ea0`에서 승인된 proof-code 변경 대상은 소스 계약 검사 파일과 검증 단위 테스트 **2개**였는데, 직전 조건이 1개만 허용해 자기참조 충돌이 발생하는 것을 검토 과정에서 확인했습니다.
- 이전 `a50d6e47`의 source 19개 경로 승인 스냅샷을 그대로 보존하고, 해당 두 증명 파일만 이후 수정 대상으로 명시합니다. 추가로 테스트 파일을 정확한 `05e91ea0` SHA에 핀 고정하여 테스트 훼손을 차단합니다. 나머지 전체 `libs/graphs/apps/scripts/tests` 및 tracked 작업공간 drift는 fail-closed입니다.
- 기존 Broker·Supervisor·Executor·Step5C·UEF 안전, negative mutation tests, 24 real-data SKIP, main HOLD 보존. 새 SHA 호스팅 CI는 검증 전이므로 PASS 주장 없음.

Sources: `scripts/refactor/shared_strategist_contracts.py`, `tests/test_shared_strategist_contracts.py`.

## 2026-10-19 · P1.5 SOURCE CONTRACT PROOF PIN SELF-DRIFT CLOSURE 20261019
**Stage:** CI contract verification hardening · **Tags:** CI · TEST · SAFETY

- 직전 커밋 `cfac9b71`의 자체 검토에서 post-a50 소스/테스트 차단 검사가 CI 계약 검증 코드·테스트 2개 파일의 바로 그 수정까지 차단하는 자기 참조 결함을 확인했습니다.
- `a50d6e47`부터 `cfac9b71`까지 실제 변경된 `libs/graphs/apps/scripts/tests` 경로는 정확히 CI 증명 파일 2개입니다. 해당 2개만 명시적으로 기록하고, `cfac9b71` 이후에는 검증기 자체 보정 파일 1개 이외의 모든 runtime/script/test/fixture 변경을 거부합니다. tracked worktree 소스 변경도 거부합니다.
- 기존 source 19-path 고정, NEXT_PATHS 금지 목록, hostile path mutations, 실거래 Broker/UEF/Step5C 금지, untracked 검사는 그대로 유지합니다.
- 호스팅 CI PASS 미검증, 24 real-data SKIP·독립 감사·DOC_FREEZE·main 병합 HOLD.

Sources: `scripts/refactor/shared_strategist_contracts.py`, `tests/test_shared_strategist_contracts.py`.

## 2026-10-19 · P1.5 SHARED SOURCE SCOPE PINNED ADMISSION REANCHOR 20261019
**Stage:** CI contract verification · **Tags:** CI · TEST · SAFETY · DOCS

- GitHub Actions [#39246312258](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39246312258)에서 과거 SHA 확보 step은 Linux/Windows 일반·-O 4개 Job 모두 PASS. 각 계약 Job 3,295 PASS / 4 FAIL / 24 SKIP, API 2/2 PASS로 좁혀졌습니다.
- 옛 NEXT_BASE 개발 변경 범위를 현재 HEAD 전체와 비교해 후속 D00·문서·CI 파일 93개를 소스 단계 변경으로 오판한 문제를 고쳤습니다. 독립 검증된 source integration `a50d6e4780ddccd810fb0708e756e1bf63d8ede0`에 19-path 단계 검증을 고정하고, SHA 조상 관계를 검사합니다.
- **완화가 아니라 추가 안전 검증:** a50 SHA 이후 모든 `libs/`, `graphs/`, `apps/`, `scripts/`, `tests/` (golden/fixture 포함) 변경을 HEAD 및 tracked worktree 기준 fail-closed로 검사합니다. 기존 `NEXT_PATHS`와 Broker·UEF·Step5C 금지, untracked 검사, 실제 매매 권한은 변경하지 않습니다.
- 기존 테스트 통과 수치를 새 SHA의 PASS로 주장하지 않습니다. 신규 CI/독립 리뷰는 대기, real-data 24 SKIP와 DOC_FREEZE/main HOLD 유지.

Sources: `scripts/refactor/shared_strategist_contracts.py`, `tests/test_shared_strategist_contracts.py`, `.github/workflows/p15-shared-candidate.yml`.

## 2026-10-19 · P1.5 SHARED CANDIDATE PINNED HISTORICAL GIT OBJECT HYDRATION 20261019
**Stage:** CI evidence and provenance recovery · **Tags:** CI · TEST · DOCS

- Shared Candidate 실행 [#39219563198](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39219563198)에서 일반 Linux 3,126 PASS / 116 FAIL / 57 ERROR / 24 SKIP, 계약 4개 실패·API 2개 성공을 직접 확인했습니다.
- 삭제된 브랜치의 과거 SHA 5개는 GitHub에 원본 파일과 함께 존재하나, CI checkout에서 `git show` / `git archive`로 접근되지 않았습니다. 따라서 기존 고정 기준을 바꾸지 않고 workflow 안에서 정확한 SHA를 명시적으로 fetch하고 SHA:path의 Git blob 존재 여부를 fail-closed로 확인합니다.
- 테스트 코드·검증 조건·안전 게이트를 수정하거나 skip/xfail하지 않았습니다. 본 변경의 CI PASS는 **아직 확인되지 않았으며**, 별도 DOC/CI 범위 검사 실패도 여전히 OPEN입니다.
- 거래 운영환경·브로커·UEF·Step5C·main 변경 없음. DOC_FREEZE HOLD.

Sources: `.github/workflows/p15-shared-candidate.yml`, `scripts/refactor/shared_candidate_tests.py`, `scripts/refactor/shared_strategist_contracts.py`.

## 2026-10-19 · P1.5 HISTORICAL DIRECT-ENTRY BANNERS 20261019
**Stage:** Documentation governance · **Tags:** DOCS · AUDIT

- DOC-A 독립 감사의 실질적 REWORK 30개 과거 작업지시 + Reporter/Monitor 옛 프로젝트 정의 2개, 총 32개 문서 최상단에 HISTORY/NOT CURRENT AUTHORIZATION 표시를 추가했습니다.
- 기존 ACTIVE/READY/ASSIGNED 문구, 원본 본문, 기록된 SHA/PASS/FAIL/SKIP, 안전 규칙, 레지스트리의 최초 blob SHA는 변경하지 않았습니다. 기존 PASS 4개 파일은 그대로 유지했습니다.
- 현재 CI 트리거 설정은 이전 커밋 10dde6d3에서 복구했지만 실제 GitHub-hosted PASS는 아직 미확인입니다. 전체 339개 본문/내부 참조 검증, 최신 SHA 독립 검수, 사용자 DOC_FREEZE 수용은 남아 있습니다.
- 거래 소스·테스트·CI 정의·실거래·운영 데이터·main은 변경하지 않았습니다.

Sources: `docs/refactor/work_orders/archive/CURRENT_2026-10-15_INTEGRATION.md`, `docs/refactor/work_orders/P15_FAST_TRACK_WAVE_A_013.md`, `docs/refactor/work_projects/MONITOR_PROJECT.md`, `docs/refactor/work_projects/REPORTER_PROJECT.md`.

## 2026-10-19 · P1.5 INTEGRATION CI PUSH TRIGGER RESTORE 20261019
**Stage:** Documentation and CI governance · **Tags:** CI · DOCS · SAFETY

- 삭제된 개발 브랜치를 가리키던 GitHub Actions 7개 워크플로의 push 트리거를 현행 `integration/p1.5`로 변경했습니다. 기존 main/PR/수동 실행 및 paths 필터는 유지했습니다.
- 기존 D00 문서 권한 검사 2곳에 `FINAL_ACCEPTED` 조기 선언 거부 조건을 복구했습니다. pytest·기존 회귀/골든/Step5C/UEF/브로커 안전 게이트는 수정하지 않았습니다.
- 이 변경은 CI 실행 조건 복구이며 새 SHA 호스팅 CI PASS나 독립 감사 PASS를 뜻하지 않습니다. `DOC_FREEZE`와 `main` 병합은 여전히 HOLD입니다.

Sources: `.github/workflows/p15-integration-consumer-inventory.yml`, `.github/workflows/p15-integration-crossbranch-compat.yml`, `.github/workflows/p15-integration-scripts-contract.yml`, `.github/workflows/p15-integration-t4-regression.yml`, `.github/workflows/p152-r2c-residual-regression.yml`, `.github/workflows/p15-shared-candidate.yml`, `.github/workflows/scripts-target-tree-contract.yml`.

## 2026-10-19 · P1.5 LEGACY CI PINNED FETCH CORRECTION 20261019
**Stage:** Documentation governance · **Tags:** CI / DOCS

- 과거 회귀 workflow가 이미 삭제된 `origin refactor/p1.5`를 fetch하던 1개 명령(동일 행의 두 분기)을 현재 존재하는 `origin integration/p1.5`로 변경.
- workflow trigger·stage-pinned 이전 커밋·테스트 및 UEF/golden 안전 검증은 그대로 유지. 현재 브랜치 HEAD에 대한 CI 실행/PASS는 아직 없음.
- 역사 workflow를 P1.5 최신 필수 게이트로 승격하거나 runtime/main을 변경한 것은 아님. DOC_FREEZE HOLD.

Sources: `.github/workflows/p152-r2c-residual-regression.yml`, `docs/refactor/work_orders/CURRENT.md`.

## 2026-10-19 · P1.5 LEGACY CI DOC CONTRACT ALIGNMENT 20261019
**Stage:** Documentation governance · **Tags:** DOCS · CI · SAFETY

- 오래된 Fast Track 실행 역할·단일 활성 Wave·`CURRENT State` 문자열을 강제하던 2개 워크플로의 문서 권한 검사만 D00/#20/DOC_FIRST 조건으로 대체했습니다.
- 원래 파이썬 pytest, Golden, Broker/Step5C/UEF 안전 검사, stage-pinned 근거, CI 트리거는 변경하지 않았습니다.
- 339개 원본 등록부 경로·구 작업 비활성·TREE_V3·패치노트 JSON/MD 일치 및 CI 내 ZIP 금지 조건을 검증합니다.
- GitHub Actions 새 SHA 실행 결과와 독립 검수는 아직 NOT_RUN. DOC_FREEZE와 main 승격은 HOLD.

Sources: `.github/workflows/p15-integration-t4-regression.yml`, `.github/workflows/p152-r2c-residual-regression.yml`, `docs/refactor/work_orders/CURRENT.md`, `docs/ENGINEERING_DELIVERY_POLICY.md`.

## 2026-10-19 · P1.5 ROOT AND LEGACY ROADMAP QUARANTINE 20261019
**Stage:** Documentation governance · **Tags:** DOCS · GOVERNANCE

- 클검 DOC-E 지적 P2-03/P2-04를 반영하여 루트 README의 2026-10-18 snapshot 및 M20~M22 로드맵을 역사적 상태로 표시했습니다.
- `docs/roadmap/` 28개와 `docs/en/12_roadmap.md`, `docs/ko/12_roadmap.md` 2개에 현행 작업지시가 아님을 표시했습니다. 원문 내용과 과거 설계·안전 증거는 유지했습니다.
- 현재 로드맵은 P1.5/P1.6 마스터플랜, 활성 상태는 GitHub #20입니다. DOC_FREEZE는 여전히 PENDING입니다.
- 거래 코드·테스트·CI·브로커·UEF·main 변경 없음. 새로운 릴리스/CI PASS 주장 없음.

Sources: `README.md`, `docs/roadmap/trading_agent_phase_roadmap.md`, `docs/roadmap/unified_roadmap.md`, `docs/en/12_roadmap.md`, `docs/ko/12_roadmap.md`.

## 2026-10-19 · P1.5 HISTORIC SOURCE PROVENANCE DOC-A 20261019
**Stage:** Documentation governance · **Tags:** DOCS · AUDIT

- 과거 UI 패치노트 sources[]를 실제 Git 트리와 대조하여 **고유 14경로/참조 16회**가 저장소 밖의 역사적 소스임을 분류했습니다. 추적 디렉터리 두 개는 누락으로 취급하지 않았습니다.
- 기존 패치노트의 원본 sources[]와 역사적 주장, 출력물/로그/비밀 파일은 일절 복구하거나 덮어쓰지 않았습니다.
- 구 R3 개발 프로토콜과 기존 350 LOC 지침 상단에 역사적 참조 전용 표시를 추가했습니다. CI 워크플로에 남은 과거 요구는 별도 정확 범위 수정·검증 대상으로 기록합니다.
- 거래 소스·테스트·CI·운영 환경·main 변경 없음. DOC_FREEZE 아직 미승인.

Sources: `docs/refactor/DOC_PATCHNOTE_SOURCE_PROVENANCE_20261019.md`, `docs/refactor/P15_EXECUTION_PROTOCOL.md`, `docs/refactor/p1_5_small_owner_policy_and_rollback_decision_v1_2.md`.

## 2026-10-19 · P1.5 DOC REWORK P1 P2 RESOLUTION 20261019
**Stage:** Documentation governance · **Tags:** DOCS · SAFETY · MAINTAINABILITY

- D01/D02에서 종료된 #16–#19을 현재 작업 큐로 읽지 않도록 변경. 신규 업무는 #20의 최신 승인에 한함.
- HYBRID-7 V3의 구조·안전 목표는 그대로 보존하고, V1-052·삭제된 구 브랜치·고정 Claude→Codex 인계는 **역사적 실행 순서**로 명시.
- Constitution §12/§15의 과거 담당자·전체 pytest cadence·브랜치 지시는 D00/#20이 대체하며, §13/§14의 안전 금지 및 과거 테스트 수용 증거는 유지.
- `main`은 **정책상 변경 금지**이나 GitHub에서 물리적 보호가 확인된 상태라고 주장하지 않음. 관리자가 실제 보호 여부를 검증해야 함.
- 이번 작업은 문서만 수정. DOC_FREEZE **PENDING**, 339개 본문/패치노트 출처/독립 재감사 및 사용자 승인 미완. 소스·운영·main 변경 없음.

Sources: `AGENTS.md`, `CLAUDE.md`, `docs/ENGINEERING_DELIVERY_POLICY.md`, `docs/refactor/architecture/TREE_V3_FROZEN.md`, `docs/refactor/p1_5_refactor_constitution.md`.

## 2026-10-19 · P1.5 과거 작업지시 상대링크 12건 수정
**Stage:** Documentation governance
**Tags:** DOCS · MAINTAINABILITY

- 이동된 이전 작업지시 3개 Markdown의 기존 상대링크 12개만 실제 파일 위치로 수정합니다. 기록된 실행 결과·검증 의미 및 과거 작업 격리 상태는 유지합니다.
- 거래 코드, main, 운영 경로 변경 없음. DOC_FREEZE PENDING.

근거: `docs/refactor/work_orders/P15_R3_SEAM_RESTORATION_003.md`, `docs/refactor/work_orders/archive/CURRENT_2026-10-15_INTEGRATION.md`, `docs/refactor/work_orders/archive/CURRENT_R3_CODEX_HANDOFF_THROUGH_923D1E2_2026-10-12.md`.


## 2026-10-19 · P1.5 문서 정합성 및 과거 작업 격리 (DOC FIRST)
**Stage:** Documentation governance
**Tags:** DOCS · GOVERNANCE

- D00 정책, D01 Codex, D02 Claude의 유일한 경로와 #20 실시간 권한을 통일하고, 최초 339개 문서의 SHA·분류 장부를 추가합니다.
- 과거 Reporter/Monitor/R3 문서를 비활성 참고 자료로 격리합니다. 원본은 이동·삭제하지 않습니다. 완료된 a50d6e47 코드·CI와 P1.5 전체 HOLD를 구분합니다.
- 경로별 분류는 본문/외부 링크의 전수 검증이 아닙니다. **DOC_FREEZE PENDING**. 거래 코드, 브로커 권한, main 수정 없음.

근거: `docs/refactor/README.md`, `docs/refactor/work_orders/CURRENT.md`, `docs/refactor/DOC_REGISTRY.csv`, `docs/ENGINEERING_DELIVERY_POLICY.md`.


> UI 노출용 상세 프로젝트 변경 이력. 저장소에 남아 있는 milestone 문서, daily patch, evaluation/research 문서를 시간순으로 재구성했다. Git commit metadata가 ZIP에 포함되지 않은 초기 구간은 정확한 일자를 임의 생성하지 않고 milestone 순서/범위로 표기했다.

총 **45개 릴리즈/변경 구간**을 수록한다. 작은 버그 수정 하나하나를 전부 카드화하기보다, UI에서 의미가 있는 기능·정책·평가 단위로 묶되 각 카드 안에서 실제 세부 변경을 보여주는 방식이다.

## 2026-10-19 · P1.5 SELECTIVE STRATEGIST OPERATOR UI INTEGRATION 20261019
**Stage:** Integration
**Tags:** REFACTOR · TEST · INTEGRATION

- integration `90ec2383` 위에 감사된 Strategist `6849bed4`의 parsing helper 3개·새 Owner·집중 테스트와 Operator UI `613a945d`의 brief 조립 함수 2개·기존 Owner·테스트만 선택 반영합니다. 개발 브랜치 전체와 기존 S5 테스트 파일의 분기 내용은 가져오지 않습니다.
- Strategist 원본은 187줄, UI core는 348줄 줄었습니다. 공개 ABI·facade use-time lookup·응답 순서·예외·읽기 전용 권한·lazy LLM 동작은 보존합니다. 387줄 sections Owner를 숫자만 맞추기 위해 재분리하지 않습니다.
- 과거 S5/T3/T4-D의 import·350줄·AST 검사는 수용된 `c5fe8a9a` 단계 소스에 보존합니다. 실제 현재 파일이 감사된 blob과 정확히 일치해야만 역사적 source view를 얻습니다. 새 단계는 정확한 5개 런타임 파일·함수·import·wrapper/ABI 복원 및 허용 경로를 검사하고, 동적 import·State·추가 LLM·Broker 권한 변이를 거부합니다.
- frozen golden·음성 검사를 삭제하거나 skip/xfail/waiver하지 않습니다. 패치노트 커밋 시 신규 통합 SHA의 필수 CI와 독립 게이트 감사는 아직 대기 상태입니다. 전체 pytest·실운영 JSON/HTML frozen parity·UI build는 NOT_RUN입니다. `main` 및 최종 P1.5 수용은 사용자 승인 사항입니다.

- 로컬 Windows Python3.14.2 집중 소스·동작·단계 게이트: normal은 집중 수정 후 고유421개 PASS, `-O`는 단일 실행421개 PASS. 초기 실패 로그도 보존합니다. 신규 통합 SHA의 Linux3.12/Windows3.13 필수6개 CI는 아직 대기 상태입니다.

- CI 수정1회차: `884318ee` Linux normal/`-O` 각각 3295 PASS / 4 FAIL / 24 SKIP. 3개 inventory 실패는 docs-only `90ec2383`에서 역사적 표식이 사라진 원인으로, `CURRENT.md`에 `P1.5.2 OPEN`·`P1.5.3`을 비활성 provenance로 복원합니다. UI fallback 테스트는 Windows 고정 문자열 대신 격리된 native 경로를 쓰며 동일한 상위 디렉터리·출력 파일명을 요구합니다. 런타임 코드는 변경하지 않았습니다. 수정 집중 검사 normal/`-O` 각각63 PASS; 새 SHA 필수6개 CI는 대기 중입니다.

근거: [Operator UI 감사 #18](https://github.com/hbombheart1230-dotcom/agentra/issues/18), [Strategist 감사 #19](https://github.com/hbombheart1230-dotcom/agentra/issues/19), `tests/test_p15_integration_completion.py`.

## 2026-10-18 · P1.5 작업지시 문서 단일화 (운영 규칙·문서만)
**Stage:** Maintainability
**Tags:** DOCS · GOVERNANCE

- `CURRENT.md`, `COMMON_RULES.md`, `work_orders/README.md`에서 이전 Reporter/Monitor `ACTIVE / WORKERS_NOT_STARTED`, 옛 단일 `refactor/p1.5` 브랜치, 고정 Claude 구현·Codex 감사 지시를 현재 명령에서 제거했습니다.
- **실시간 실행 상태는 Issue #20 하나**, `ENGINEERING_DELIVERY_POLICY.md`는 상시 절차, `AGENTS.md`/`CLAUDE.md`는 각 도구 진입점으로 역할을 구분했습니다. 이전 문서 전문은 Git `c5fe8a9a` 및 기존 기록에 보존했습니다.
- S5+UEF9 통합 코드 `c5fe8a9a`의 필수 CI [39133879389](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39133879389)는 **6/6 성공** 확인. 다음 리팩터링 구현과 P1.5 전체 최종 수용은 별개이며, 코드/테스트/거래 권한은 이번에 변경하지 않았습니다.
- 개발자/감사자 Issue #16~#19의 기존 과제는 종료하고 차기 명시적 SHA 범위가 승인될 때만 다시 할당하도록 안내합니다. `main`, 브랜치와 운영 작업 트리는 변경하지 않았습니다.

근거: `docs/refactor/work_orders/CURRENT.md`, `COMMON_RULES.md`, [Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20).

## 2026-10-18 · Permanent delivery-first engineering rule (설계/운영 규칙만)
**Stage:** Architecture Freeze
**Tags:** ARCHITECTURE · AUDIT · REFACTOR

- 개발자를 위한 규칙과 감사자를 위한 규칙을 분리하고, **작업 SHA 확인 → 변경분 독립 검증 → 지팀장 선택 통합 → 통합 SHA 검사 → 단계 종료**를 상시 순서로 고정했습니다.
- 기존 3천 건 이상 전체 테스트의 무조건적 재실행, 정적 분석기 재감사/반례 공장, 새 브랜치·문서·인벤토리 무한 증식을 금지했습니다. 다만 변경된 위험 경계·안전 회귀는 반드시 검증합니다.
- `IMPLEMENTED/AUDITED/INTEGRATED/RELEASE_ACCEPTED`를 분리해 개발 브랜치 PASS를 통합 완료로 포장하지 않습니다.
- 프로젝트 **루트 전체**의 Owner/중복/호환성 정리가 목표이며, 실제 거래 권한·Step5C/UNKNOWN·UEF oracle·실데이터/고위험 조건은 그대로 보호합니다.
- 공통 정책: `docs/ENGINEERING_DELIVERY_POLICY.md`. 루트 `AGENTS.md`, `CLAUDE.md`, `README.md`, 현재 작업 안내에서 이 규칙을 바로 찾을 수 있게 연결했습니다.

**영향:** 문서/팀 운영 기준만 바뀌었으며 거래 코드·정책·테스트 기대값·CI 구성은 바뀌지 않았습니다. P1.5 최종 PASS를 뜻하지 않습니다.

---

## 2026-10-18 · P1.5 전체 루트 아키텍처 직접 실사 (설계·문서 변경만)
**Stage:** Architecture Freeze
**Tags:** ARCHITECTURE · REFACTOR · AUDIT

- `main` 2,610개와 통합 소스 3,908개 파일을 비교하여 루트 전체(10개 폴더 + 11개 직속 파일), `libs/` 26개 폴더와 모든 추적 경로를 구조·책임 후보로 정리했습니다.
- 원본 거대 파일은 일부 50~85% 감소했지만 1,298개 신규 파일·0개 삭제로 인해 호환 facade, 증거 문서, 스크립트·테스트 증가와 소유권 수렴 미완료를 별도 문제로 구분했습니다.
- Commander의 실제 주문 경로, UEF 단일 발행, Supervisor·Executor·Broker·Step5C 안전 권한은 그대로 보호하며 관련 구조 이전 승인은 내리지 않았습니다.
- 7개 과거 브랜치 가운데 통합 조상 2개는 삭제 **후보**일 뿐 원격 삭제하지 않았고, 고유 커밋이 있는 나머지 5개는 보존합니다.
- 자세한 근거: `docs/refactor/architecture/P15_ROOT_TO_LEAF_REALITY_AND_CLEANUP_20261018.md`, `P15_TECHLEAD_MASTER_20261018.md` 및 3,908개 전체 경로·후보 CSV.

**영향:** 이번 변경은 설계 문서/증거/운영 이력에 한정됩니다. 거래 코드, 배포 실행, 실제 전략·주문 권한, UEF 기대값, CI 테스트 변경은 없습니다. P1.5 최종 수용 아님.

---

## 2026-08-31 · Opening Alpha 및 Q10/Q12 시각 정합성 복구
**Stage:** Controlled Mock Validation
**Tags:** OPENING_ALPHA · Q10 · Q12 · SCHEDULER · KIWOOM_MOCK

### 변경 내용
- Opening Alpha 후보에 Rank가 누락돼도 Scanner 원본 authority가 Rank-1 및 종목 일치를 증명하면 해당 Rank를 사용합니다.
- Q10 선행시장 스냅샷을 09:00 baseline 루프에서 분리하고 기존 08:50 Preopen 예약 작업의 첫 단계에서 불변 파일로 저장합니다.
- Q12 BTC 08:55 스냅샷 전용 스크립트와 평일 08:55 Windows 예약 작업을 추가했습니다.
- Q12 캡처는 짧은 재시도를 지원하고 성공·누락·마감 후 지연을 일별 장부의 시도 이력으로 남깁니다.
- 09:00 이후 Q12 baseline은 동결된 08:55 원본을 재사용하며, 실패한 캡처를 장후 데이터로 소급 복원하지 않습니다.

### 운영 산출물
- `reports/evaluation/baseline_samsung_hynix/YYYY-MM-DD/q10_forward_validation/q10_preopen_signal_snapshot.json`
- `data/logs/q12_btc_0855/YYYY-MM-DD/btc_0855_snapshot.json`
- `data/logs/q12_btc_0855/YYYY-MM-DD/capture_ledger.json`

### 변경의 의미
조건 완화 레인이 후보 객체의 누락 필드나 장중 루프 시작 시각 때문에 무조건 비활성화되는 문제를 제거했습니다. Rank-1 종목 일치, risk-off, 비용, 차트 하드 플로어와 일일 주문 한도는 유지합니다.

---

## 2026-02-07 · v0.1 — 프로젝트 시작 — Traceable Core
**Stage:** Foundation  
**Tags:** CORE · OBSERVABILITY

자동매매 기능보다 먼저 실행 이력을 남길 수 있는 코어와 추적 구조를 만들기 시작한 최초 단계.

### 변경 내용
- 이벤트 로거와 run 단위 추적 개념을 코어 설계에 포함.
- 이후 모든 판단·승인·실행 결과를 run_id 중심으로 재현할 수 있는 방향 설정.
- 단순 주문 스크립트가 아니라 관찰 가능하고 검증 가능한 시스템을 목표로 확정.

### 이 변경의 의미
이후 Reporter, audit, replay, evaluation이 붙을 수 있는 기반이 됨.

### 근거 문서 / 코드
- `libs/event_logger.py`
- `docs/08_observability.md`

---

## 최근 1주일 주요 업데이트 (2026-08-24 ~ 2026-08-28)

기존 패치 이력은 그대로 유지하고, 현재 운영과 연구 방향을 이해하는 데 필요한 주요 변경만 보강합니다.

### 2026-08-24 · Evaluation Integrity + Prospective Board

- 과거 발견 표본과 prospective 표본을 분리했습니다.
- Q 평가와 baseline 산출물의 누락·중복·시간 정합성 검사를 강화했습니다.
- 기존 평가 결과는 Alpha Research Board의 입력 증거로 재사용하며 새 평가 축을 늘리지 않습니다.

### 2026-08-25~26 · Q12 Trend + Opening Snapshot + AI Provenance

- BTC 최근 추세와 신호 가용성을 Q12 증거에 추가했습니다.
- 장초반 국내 지수·야간선물 값, snapshot 시각과 지연을 기록합니다.
- Strategist 단계별 후보·판단·horizon provenance를 연결했습니다.

### 2026-08-27 · Strategist Authority Lineage

- 2차 전략가의 재순위·후보 교체·진입 강화·no-trade 권한을 분리했습니다.
- 3차 전략가의 최초 horizon, 재평가 horizon, 실제 보유시간을 연결했습니다.
- 행동 변경 없이 LLM 기여도를 검증하는 관측 근거를 마련했습니다.

### 2026-08-27 · Web Observability M7

- 메인 런타임, watchdog, health 상태를 읽기 전용 UI에서 확인합니다.
- 호스트 Supervisor와 장전·장후 예약 인텔리전스의 실행 상태를 표시합니다.
- UI 컨테이너는 트레이딩 런타임과 분리되며 데이터 경로는 read-only입니다.

### 2026-08-27~28 · Alpha Board v2 + Q12 Five-Variable Validation

- 장후 판단 기준을 고정된 Alpha Research Board로 통합했습니다.
- Q12는 BTC 08:55 수익률, FIRST_SURGE, BREAKOUT, 우기투 opening gap, 09:03~09:05 수급의 다섯 변수만 검증합니다.
- 09:00·09:03·09:05·09:10·눌림 시점의 forward 성과를 같은 비용 기준으로 비교합니다.
- Q9와 실제 주문·진입·청산 로직은 변경하지 않았습니다.

### 2026-08-28 · Patch Notes Timeline UI

- 누적 패치 이력을 운영 UI에서 검색·stage·type으로 필터할 수 있게 했습니다.
- FastAPI와 React 기능을 독립 모듈로 구성하고 문서 경로만 read-only로 마운트했습니다.
- 앞으로 모든 패치는 JSON과 Markdown 패치 노트를 같은 커밋에서 함께 갱신합니다.

### 2026-08-28 · Q10 Lead-Market Forward Validation

- 기존 삼성전자·SK하이닉스 Q10 기준선은 그대로 유지합니다.
- SOX·Nvidia·Micron·하이닉스 ADR와 08:50 Nasdaq100/S&P500 선물·USD/KRW, US10Y·VIX를 개장 전 불변 스냅샷으로 저장합니다.
- 삼성전자·SK하이닉스·KOSPI·KOSDAQ의 09:00 이후 체크포인트와 gap·MFE·MAE를 기록합니다.
- 고정 예상 상태와 실제 opening gap을 UNDERREACTION·FAIR_REACTION·OVERREACTION·DIVERGENCE로 분류합니다.
- 09:00/09:03/09:05/09:10 및 첫 눌림 진입은 주문 없이 shadow로만 비교합니다.
- `2026-08-31` 이후 데이터만 누적하며 과거 백필·백테스트·threshold 최적화·ML·Executor 연결을 금지합니다.

### 2026-08-28 · Scheduled Intelligence Evidence Detail

- 장전·장후 예약 카드에 접이식 상세 보기를 추가했습니다.
- 전략 프레임·리스크·모델·메모리 적용 방식과 단계별 실행 상태를 표시합니다.
- 브리핑·메모리·Strategist·closeout·통합 인덱스 원본 경로를 확인하고 복사할 수 있습니다.
- 장전 canonical 원본의 날짜 폴더를 UTC가 아닌 KST 거래일 기준으로 바로잡았습니다.
- 읽기 전용 관측 기능이며 예약 실행·전략·메모리·매매 동작은 변경하지 않습니다.

### 2026-08-29~30 · Cloudflare Private Ingress 활성화

- `agentra.win`을 Cloudflare Tunnel의 `web:8080` origin에 연결했습니다.
- Access는 운영자 이메일 allowlist와 One-time PIN으로 보호합니다.
- 인증 없는 요청이 Access 로그인으로 이동하고 API·Trading Runtime은 직접 공개되지 않는 것을 확인했습니다.
- Tunnel token은 Git에서 제외된 로컬 `.env`에만 보관합니다.

### 2026-08-30 · Scheduled Artifact Viewer

- 장전 브리핑·메모리 전달 영수증·전략 메모리·Strategist 원본과 장후 인덱스를 UI에서 직접 엽니다.
- 예약 카드에 실제로 나열된 JSON·Markdown만 읽을 수 있으며 reports 루트 이탈과 미등록 파일은 차단합니다.
- 파일은 포맷된 읽기 전용 모달로 표시하고 변경·실행 기능은 추가하지 않았습니다.
- Trading Runtime과 예약 실행 로직은 변경하지 않았습니다.

### 2026-08-30 · M7.5 Operations Command Center

- 장전·거래·장후 이벤트를 실제 완료 시각과 source를 포함한 운영 타임라인으로 표시합니다.
- 기존 anomaly, 예약 작업 issue와 장중 runtime 불일치를 한곳에서 확인합니다.
- Strategist → Scanner → Monitor → Commander → Execution의 거래 계보를 실제 artifact 기준으로 표시합니다.
- 최신/직전 운영일의 전략 프레임과 closeout 상태, 실제 청산과 post-exit 최선 checkpoint를 비교합니다.
- 모든 API는 GET 전용이며 Trading Runtime과 매매 행동에는 영향을 주지 않습니다.

---

## 2026-02-07 ~ 2026-02-10 · M1–M5 — Kiwoom API Catalog와 요청 파이프라인 골격
**Stage:** Foundation  
**Tags:** CORE · KIWOOM

키움 REST API 원본을 바로 호출하지 않고 Catalog → Discovery → Planner → Request Builder로 정규화.

### 변경 내용
- 공식 API 자료를 data/specs 계층으로 정규화하고 canonical API catalog 구성.
- 자연어/목표에서 필요한 API 후보를 찾는 Discovery와 호출 계획을 만드는 Planner 분리.
- 실제 HTTP 호출 전에 요청 객체를 만드는 Request Builder 계층 구축.
- API raw 응답과 Agent가 소비하는 계약을 분리하기 위한 초기 구조 마련.

### 이 변경의 의미
브로커 API 세부사항이 Agent 로직 전체로 퍼지는 것을 막는 첫 추상화 계층.

### 근거 문서 / 코드
- `docs/plan/archive/m3_api_discovery.md`
- `docs/plan/archive/m4_api_planner.md`
- `docs/plan/archive/m5_prepare_request.md`

---

## 2026-02-09 ~ 2026-02-10 · M6–M7 — Token/HTTP Client, Read-only Account, Dry-run Guard
**Stage:** Execution Skeleton  
**Tags:** KIWOOM · SAFETY · EXECUTION

브로커 연결을 읽기와 실행으로 나누고 주문은 dry-run/guard 뒤에서만 가능하도록 경계를 만들기 시작.

### 변경 내용
- Token client와 공통 HTTP client 도입.
- 계좌 조회를 read-only snapshot 형태로 먼저 구현.
- Supervisor를 거치는 주문 dry-run 경로와 실행 전 guard 도입.
- 실주문보다 모의·검증 경로를 우선하는 mock-first 원칙 고정.

### 이 변경의 의미
'데이터를 읽는 코드'와 '돈을 움직이는 코드'가 분리되기 시작함.

### 근거 문서 / 코드
- `docs/plan/archive/m6_token_client.md`
- `docs/plan/archive/m6_readonly_account.md`
- `docs/plan/archive/m7_order_dry_run.md`
- `docs/plan/archive/m7_supervisor.md`

---

## 2026-02-10 · M8–M10 — Decision Packet → Supervisor → Executor Live Pipeline
**Stage:** Execution Skeleton  
**Tags:** RUNTIME · EXECUTION · SAFETY

판단 결과를 표준 패킷으로 만들고 Supervisor와 Executor를 통해 stateful runtime에 연결.

### 변경 내용
- Decision Packet 계약과 executor wiring 구성.
- 읽기 snapshot과 판단 결과를 실제 실행 계층에 연결하는 live pipeline 골격 구축.
- 실행 전 approval/guard와 실행 후 결과 기록의 책임을 분리.
- 상태를 가진 반복 실행 구조로 확장.

### 이 변경의 의미
단발성 API 호출에서 반복 가능한 trading runtime으로 넘어가는 전환점.

### 근거 문서 / 코드
- `docs/plan/m8_decision_packet.md`
- `docs/plan/m8_wiring.md`
- `docs/plan/m8_executors.md`
- `docs/plan/m10_live_pipeline.md`

---

## 2026-02-11 · M11 — Scanner와 다종목 후보 탐색
**Stage:** Agent Expansion  
**Tags:** SCANNER · AGENT

단일 종목 판단에서 시장 후보를 수집·점수화해 상위 후보를 넘기는 Scanner 계층으로 확장.

### 변경 내용
- Scanner 역할과 후보 수집/랭킹 책임 분리.
- 후보별 데이터와 특징을 정량적으로 비교하는 구조 도입.
- 후속 Strategist가 모든 종목을 직접 탐색하지 않고 압축된 후보군을 받도록 변경.

### 이 변경의 의미
LLM 비용을 줄이고 전략 판단과 데이터 탐색의 책임이 분리됨.

### 근거 문서 / 코드
- `docs/plan/m11_2_scanner.md`
- `docs/plan/m11_4_logging_and_reports.md`

---

## 2026-02-11 ~ 2026-02-12 · M12–M13 — Strategist LLM Provider + Runtime Loop
**Stage:** Agent Expansion  
**Tags:** STRATEGIST · LLM · RUNTIME

LLM Strategist를 provider routing 뒤에 넣고 장중 반복 루프·EOD 보고까지 연결.

### 변경 내용
- rule fallback을 보존한 LLM Strategist HTTP/provider routing 도입.
- OrderIntent schema validation과 AI hook 추가.
- tick → 판단 → 상태 저장 → EOD report로 이어지는 runtime loop 정리.
- LLM 장애 시에도 runtime 전체가 멈추지 않도록 fallback 개념 유지.

### 이 변경의 의미
AI가 포함되지만 AI 자체가 실행 안정성을 소유하지 않는 구조가 만들어짐.

### 근거 문서 / 코드
- `docs/plan/m12_ai_hook.md`
- `docs/plan/m12_1_provider_routing.md`
- `docs/plan/m12_2_llm_strategist_http.md`
- `docs/plan/m13_runtime_loop.md`

---

## 2026-02-12 ~ 2026-02-13 · M14–M16 — 7-Agent Architecture와 Approval Model 확립
**Stage:** Architecture Freeze  
**Tags:** ARCHITECTURE · SAFETY · AGENT

Commander·Strategist·Scanner·Monitor·Supervisor·Executor·Reporter 7개 역할을 공식 구조로 고정.

### 변경 내용
- Agent Layer와 Execution Layer를 구조적으로 분리.
- Monitor는 주문을 직접 실행하지 않고 OrderIntent만 생성하도록 non-negotiable rule 고정.
- SupervisorDecision 이후에만 Executor가 실행할 수 있도록 approval layer 구성.
- intent_id 기반 멱등성과 approve/reject/manual 흐름 도입.
- Guard가 approval보다 항상 우선한다는 실행 우선순위 확립.

### 이 변경의 의미
현재 시스템의 정체성인 'Agents decide, execution is gated'가 완성됨.

### 근거 문서 / 코드
- `README.md`
- `docs/01_overview.md`
- `docs/02_principles.md`
- `docs/05_runtime_flow.md`
- `docs/07_execution_and_guards.md`
- `docs/plan/m16_approval_api.md`

---

## 2026-02-13 ~ 2026-02-14 · M17–M20 — LangGraph Spine, Strategy Signals, News/LLM Reliability
**Stage:** Enterprise Baseline  
**Tags:** LANGGRAPH · LLM · NEWS · OBSERVABILITY

설정·그래프·전략 signal·뉴스·LLM telemetry를 운영 가능한 수준으로 정리.

### 변경 내용
- Settings single-source 방향과 graph spine/risk 구조 정리.
- 시장 후보·Top Picks·Scanner scoring·sentiment/news signal 통합.
- Naver News/OpenRouter provider와 global sentiment 입력 추가.
- LLM smoke/fallback, schema retry telemetry, prompt version, token/cost telemetry 도입.
- circuit breaker safe fallback과 LLM metrics/reporting 기반 구축.

### 이 변경의 의미
LLM을 단순 호출하는 수준에서 실패·비용·버전까지 관리하는 운영 컴포넌트로 승격.

### 근거 문서 / 코드
- `docs/plan/m17_graph_spine_and_risk.md`
- `docs/plan/m18_strategist_signals.md`
- `docs/plan/m19_1_naver_news_provider.md`
- `docs/plan/m19_5_llm_routing_openrouter.md`
- `docs/plan/m20_1_llm_smoke_and_fallback.md`
- `docs/plan/m20_7_token_cost_telemetry.md`

---

## 2026-02-15 ~ 2026-02-21 · M21–M24 — Canonical Runtime, Circuit Breaker, Intent Journal
**Stage:** Production Safety  
**Tags:** RUNTIME · SAFETY · STATE

실행 경로를 하나의 canonical runtime으로 모으고 장애·중복실행·운영자 개입을 상태 기반으로 통제.

### 변경 내용
- Commander bridge와 canonical runtime entry를 표준 경로로 통합.
- runtime mode resolution과 agent-chain mapping/parity test 추가.
- Skill-native scanner/monitor와 hydration node, DTO contract 표준화.
- runtime circuit breaker, safe-degrade, cooldown, operator intervention/resume runbook 추가.
- SQLite intent journal/state machine과 duplicate execution claim guard 도입.
- real execution preflight denial reason과 intent state reconciliation tooling 추가.

### 이 변경의 의미
프로세스 재시작·장애·중복 이벤트가 발생해도 주문 상태를 복구·감사할 수 있는 방향으로 강화.

### 근거 문서 / 코드
- `docs/plan/m21_1_canonical_runtime_entry.md`
- `docs/plan/m22_5_skill_hydration_node.md`
- `docs/plan/m23_2_runtime_circuit_breaker_core.md`
- `docs/plan/m23_6_operator_intervention_resume_runbook.md`
- `docs/plan/m24_1_intent_journal_state_machine_sqlite.md`
- `docs/plan/m24_3_duplicate_execution_claim_guard.md`

---

## 2026-02-18 ~ 2026-02-21 · M25–M30 — Metrics·Alerts·Replay·Portfolio Guard·Deployment·Go-Live Gate
**Stage:** Productionization  
**Tags:** OPS · QUALITY · DEPLOYMENT · PORTFOLIO

실전 운영을 위한 모니터링·알림·재현성·포트폴리오 제한·배포·릴리즈 승인 절차를 묶어 완성.

### 변경 내용
- metric schema freeze와 alert threshold/env profile 정의.
- Slack adapter, retry/noise-control, notification event log 구축.
- fixed dataset/replay runner, scorecard, A/B evaluation, promotion gate 추가.
- multi-strategy allocation, intent conflict resolution, portfolio budget guard 도입.
- runtime lifecycle hook, scheduler/worker wrapper, launch templates, rollback procedure 구성.
- audit completeness, log archive integrity, incident timeline reconstruction, disaster recovery drill 추가.
- quality gate와 release signoff/go-live signoff aggregator 구축.

### 이 변경의 의미
코드가 돌아가는 수준에서 '운영 가능한 시스템'으로 넘어간 구간.

### 근거 문서 / 코드
- `docs/plan/m20_to_m30_master_plan.md`
- `docs/plan/m25_1_metric_schema_freeze_v1.md`
- `docs/plan/m26_2_replay_runner_scaffold.md`
- `docs/plan/m27_3_portfolio_budget_boundary_guard.md`
- `docs/plan/m28_3_rollout_checklist_and_rollback_procedure.md`
- `docs/plan/m29_8_disaster_recovery_drill_restore_replay.md`
- `docs/plan/m30_4_final_golive_signoff_aggregator.md`

---

## 2026-03-06 · M31-1~3 — Post-Go-Live 운영 검증 시작
**Stage:** Operational Readiness  
**Tags:** OPS · SLO · QUALITY

SLO·incident review·mock investor exam·weekly health summary로 실제 장중 운영 상태를 계량화.

### 변경 내용
- M31 SLO baseline과 incident review workflow 구현.
- Mock Investor Exam protocol/check와 agent-chain probe 추가.
- Weekly health summary operator script 추가.
- 3/6 세션 기준 319 runs, 1,376 events를 수집해 execution/LLM 품질을 점검.
- Strategist LLM 성공률 93.5%, 높은 p95 latency와 prompt-version 혼재를 즉시 개선 우선순위로 지정.

### 이 변경의 의미
'기능 구현 완료'가 아니라 실제 세션 데이터로 운영 준비도를 평가하기 시작.

### 근거 문서 / 코드
- `docs/plan/m31_plus_progress_summary_2026-03-06.md`

---

## 2026-03-07 · M31 Safety Patch — Portfolio Snapshot Health Guard + EOD 강제청산
**Stage:** Operational Readiness  
**Tags:** SAFETY · PORTFOLIO · EXECUTION

계좌 snapshot 장애 시 blind BUY를 차단하고 당일 청산 정책을 deterministic rule로 보강.

### 변경 내용
- portfolio_snapshot에 reader_ok/error/source/fallback 등의 health metadata 추가.
- real execution에서 snapshot reader 오류 시 BUY를 portfolio_snapshot_reader_error로 차단.
- USE_EOD_FORCE_LIQUIDATION 기반 pre-close SELL rule 추가.
- 관련 snapshot/execute/decision 테스트 보강.

### 이 변경의 의미
브로커 상태를 모르는 상황에서 신규 포지션을 잡는 위험을 구조적으로 줄임.

### 근거 문서 / 코드
- `docs/plan/m31_plus_runtime_safety_patch_2026-03-07.md`

---

## 2026-03-08 · M31 Audit — Operational Readiness: NOT_READY → READY
**Stage:** Operational Readiness  
**Tags:** AUDIT · SAFETY · STRATEGY

운영 감사에서 설정 문제를 수정한 뒤 M31 readiness gate를 통과.

### 변경 내용
- 초기 audit 결과 NOT_READY 확인.
- APPROVAL_MODE=manual로 수정 후 readiness check 재실행.
- Feature/regime engine, Strategy V1, universe/scanner, data-quality propagation, sizing/exit explainability 활성 상태 확인.
- Operator visibility와 readiness scripts의 실제 연결 검증.
- regime_momentum_v1을 Strategy V1 baseline으로 명시.

### 이 변경의 의미
실전 전환 여부를 사람의 느낌이 아니라 체크 가능한 gate로 판정할 수 있게 됨.

### 근거 문서 / 코드
- `docs/plan/m31_operational_readiness_audit_2026-03-08.md`

---

## 2026-04-14 ~ 2026-04-16 · Reporter v2 — AI Trade Report 안정화와 Reporter Agentification
**Stage:** Explainability  
**Tags:** REPORTER · REPORTING · LLM

거래 후 보고서를 단순 로그 요약이 아닌 evidence 기반 agent output으로 재설계.

### 변경 내용
- Reporter fallback audit 후 recovery/stabilization plan 수행.
- AI Trade Report target example과 improvement plan으로 목표 포맷 고정.
- golden trade matrix와 report runtime regression plan 도입.
- execution snapshot observability와 lifecycle linkage를 report에 연결.
- report surface pruning과 Reporter ownership 정리.

### 이 변경의 의미
거래 결과뿐 아니라 '왜 그 판단이 나왔고 실제로 어떻게 체결됐는지'를 한 보고서에서 추적 가능해짐.

### 근거 문서 / 코드
- `docs/debug/reporter_fallback_audit_2026-04-14.md`
- `docs/trade_report_plan/ai_trade_report_improvement_plan_2026-04-15.md`
- `docs/report_upgrade_plan/reporter_agentification_execution_plan_2026-04-15.md`
- `docs/trade_report_plan/golden_trade_matrix_2026-04-16.md`

---

## 2026-04-19 ~ 2026-04-21 · Memory v1 — Market/Symbol/Position Runtime Memory 구축
**Stage:** Agent Memory  
**Tags:** MEMORY · COMMANDER · STRATEGIST

세션 단발 판단을 넘어 과거 시장·종목·포지션 상태를 다음 판단에 전달하는 memory contract 구축.

### 변경 내용
- market_memory, symbol_memory, memory_flow, reports usage contract 정의.
- position refresh contract와 symbol read-model 정렬.
- memory packet schema와 Strategist memory packet visibility 추가.
- Commander memory authority, Scanner memory bias, Monitor memory bias 역할 분리.
- 불필요한 script/report 중복을 줄이는 reduction policy 도입.

### 이 변경의 의미
각 Agent가 제멋대로 과거를 해석하지 않고 정해진 memory packet을 통해 맥락을 공유하게 됨.

### 근거 문서 / 코드
- `docs/runtime_memory/market_memory_contract_2026-04-19.md`
- `docs/runtime_memory/symbol_memory_contract_2026-04-19.md`
- `docs/runtime_memory/memory_packet_schema_2026-04-21.md`
- `docs/commander_control/commander_memory_authority_2026-04-21.md`

---

## 2026-04-20 ~ 2026-04-28 · Truth Alignment — Kiwoom Truth와 Commander Control 정렬
**Stage:** Runtime Integrity  
**Tags:** KIWOOM · COMMANDER · DATA_QUALITY

broker truth, theme strength, carry/position 관리, 대표 종목 guard를 실제 runtime 판단과 일치시키는 작업.

### 변경 내용
- Kiwoom role inventory/data target map으로 어떤 API가 어떤 판단에 쓰이는지 정리.
- Kiwoom truth current-state/next-step plan으로 raw broker truth와 derived value 경계 강화.
- Commander carry control model과 position management policy 정립.
- theme strength packet과 theme API strategy selection 추가.
- entry participation control 및 market representative guard 도입.

### 이 변경의 의미
리포트 숫자·Agent 판단·브로커 계좌 상태가 서로 다른 truth를 보는 문제를 줄임.

### 근거 문서 / 코드
- `docs/kiwoom_truth/kiwoom_truth_alignment_plan_2026-04-20.md`
- `docs/commander_control/carry_control_model_2026-04-20.md`
- `docs/kiwoom_truth/kiwoom_theme_strength_packet_2026-04-27.md`
- `docs/commander_control/market_representative_guard_2026-04-28.md`

---

## 2026-04-22 · System Status — Trade Report/Kiwoom/Entrypoint 안정화 상태 점검
**Stage:** Runtime Integrity  
**Tags:** REPORTER · MEMORY · RUNTIME

5개 주요 workstream을 통합 점검해 닫힌 영역과 계속 개발할 영역을 분리.

### 변경 내용
- trade_report_plan, kiwoom_truth, runtime_entrypoint는 거의 안정화 상태로 평가.
- runtime_memory와 commander_control은 계속 active development로 유지.
- AI Trade Report에서 broker truth, fee/tax, memory usage, LLM event flow 검증.
- same-day Reporter feedback을 reporter_evaluation으로 재구성하는 경로 확인.

### 이 변경의 의미
개발 우선순위를 기능 추가에서 남은 불확실성 제거로 전환.

### 근거 문서 / 코드
- `docs/system_status_2026-04-22.md`

---

## 2026-04-25 ~ 2026-04-30 · Strategy/Horizon v1 — 보유시간·사후 Shadow·설명 계약 + 보수성 Guard
**Stage:** Strategy Refinement  
**Tags:** STRATEGIST · HORIZON · GUARD

진입 여부만 보던 전략에서 보유시간, post-exit shadow, 설명 가능성, 중복매수 방지까지 확장.

### 변경 내용
- strategy horizon과 post-exit shadow tracking 계약 추가.
- Strategist explanation contract와 LLM summary artifact 정리.
- news query target flow와 operator-summary memory linkage 연결.
- duplicate buy/closeout guard 및 preopen readiness 점검 추가.
- 전략 과보수성 분석 후 runtime guard와 entry gate/reporting memory defaults 보정.

### 이 변경의 의미
'살까 말까'에서 '왜, 얼마나 들고, 언제 실패로 볼 것인가'로 전략 표현 범위가 확장.

### 근거 문서 / 코드
- `docs/strategy_horizon_feedback/strategy_horizon_and_post_exit_shadow_tracking_2026-04-25.md`
- `docs/strategist_output/strategist_explanation_contract_2026-04-25.md`
- `docs/commander_control/duplicate_buy_and_closeout_guard_2026-04-29.md`
- `docs/daily_patch/2026-04-29_strategy-conservatism-runtime-guards.md`
- `docs/daily_patch/2026-04-30_entry-gate-reporting-memory-defaults.md`

---

## 2026-05-04 ~ 2026-05-07 · Live Truth Stabilization — 장중 Cash/가격 Truth와 Report 일치화
**Stage:** Live Stabilization  
**Tags:** LIVE · REPORTING · DATA_QUALITY

실시간 계좌·체결 가격과 보고서에 보이는 값이 어긋나는 문제를 집중 보정.

### 변경 내용
- intraday cash truth와 AI report를 교차 검증.
- truth surface와 summary 문구 정렬.
- today-run gap review로 누락된 런/아티팩트 확인.
- trade price truth refresh로 오래된 가격 참조 제거.
- live open patch verification으로 실제 장 시작 시 경로 재검증.

### 이 변경의 의미
보고서가 계산상 그럴듯한 값이 아니라 당시 broker/runtime truth를 보여주도록 강화.

### 근거 문서 / 코드
- `docs/daily_patch/2026-05-04_intraday-cash-truth-ai-report-check.md`
- `docs/daily_patch/2026-05-05_truth-surface-summary-alignment.md`
- `docs/daily_patch/2026-05-06_trade-price-truth-refresh.md`
- `docs/daily_patch/2026-05-07_live-open-patch-verification.md`

---

## 2026-05-08 · Strategist 4-Stage Draft — 4단계 Strategist LLM + Horizon Slot 설계
**Stage:** Strategy Refinement  
**Tags:** STRATEGIST · LLM · HORIZON

뉴스/시장 → Scanner 후보 → 보유 판단 → Overnight 판단의 다단계 LLM 구조와 horizon slot 운영안을 설계.

### 변경 내용
- Strategist 4-stage LLM flow draft와 chat prompt template 작성.
- LLM reports 4-stage summary layout 정의.
- two-slot runtime과 multi-position minimal patch plan 작성.
- horizon slot one-symbol policy 및 report layout 정의.
- post-scanner refresh latency hotfix로 최신 후보 데이터 연결 지연 감소.

### 이 변경의 의미
현재 전략가의 다단계 역할 구조가 문서화되고 UI/report에서 단계별 판단을 보여줄 기반 마련.

### 근거 문서 / 코드
- `docs/strategy_horizon_feedback/strategist_4stage_llm_flow_draft_2026-05-08.md`
- `docs/strategy_horizon_feedback/strategist_4stage_chat_prompt_templates_2026-05-08.md`
- `docs/strategy_horizon_feedback/two_slot_runtime_patch_plan_2026-05-08.md`
- `docs/daily_patch/2026-05-08_post-scanner-refresh-latency-fix.md`

---

## 2026-05-11 ~ 2026-05-12 · Live Guard Pack A — Scanner↔Monitor 경계와 장중 Guard 대규모 보강
**Stage:** Live Stabilization  
**Tags:** SCANNER · MONITOR · GUARD · LIVE

실전에서 드러난 stale order, chart-fit, VWAP, closeout, repeat-loss 문제를 집중 보강한 대규모 핫픽스.

### 변경 내용
- pending-order stale guard와 pending-exit/recent-fill settle guard 추가.
- Scanner/Monitor chart reading role boundary와 runtime alignment 정리.
- ETF universe·deviation signal, candidate cascade expansion 추가.
- VWAP exit에서 fresh minute source 사용하도록 수정.
- human-chart guard와 chart-fit/horizon alignment 강화.
- full-close trade report gate, closeout preflight fallback 추가.
- defensive Top3/repeat-loss guard와 monitor crash hotfix 적용.

### 이 변경의 의미
Scanner가 후보를 찾고 Monitor가 진입 타이밍을 감시한다는 책임 경계가 실전 규칙에 반영됨.

### 근거 문서 / 코드
- `docs/strategy_horizon_feedback/scanner_monitor_role_boundary_patch_plan_2026-05-11.md`
- `docs/strategy_horizon_feedback/scanner_monitor_chart_reading_runtime_alignment_2026-05-12.md`
- `docs/daily_patch/2026-05-12_candidate-cascade-expansion-hotfix.md`
- `docs/daily_patch/2026-05-12_human-chart-guard-chartfit-horizon-alignment.md`
- `docs/daily_patch/2026-05-12_vwap-exit-fresh-minute-source-hotfix.md`

---

## 2026-05-13 ~ 2026-05-14 · Live Guard Pack B — Entry/Exit Evidence, Peak Protection, VWAP Reclaim
**Stage:** Live Stabilization  
**Tags:** ENTRY · EXIT · REPORTING · LLM

진입·청산 사유와 실행 결과를 분리하고 수익 보호·VWAP reclaim·LLM 비용까지 세밀하게 조정.

### 변경 내용
- exit trigger와 execution status를 분리해 '팔려고 했다'와 '실제로 팔렸다'를 구분.
- entry/exit evidence line과 operator summary pattern performance 추가.
- pending BUY에 human-chart hard guard 적용.
- chart-positive entry와 cooldown scope 재조정.
- peak-profit protection 및 peak-drawdown profit floor 강화.
- VWAP reclaim strategy와 human-chart entry relaxation 실험.
- Strategist input fingerprint cache gate와 token budget 추가.

### 이 변경의 의미
전략 논리, 실행 상태, 보고서 표현이 섞이는 문제를 크게 줄이고 LLM 비용 통제도 시작.

### 근거 문서 / 코드
- `docs/daily_patch/2026-05-13_exit-trigger-execution-status-separation.md`
- `docs/daily_patch/2026-05-13_trade-summary-entry-exit-evidence-lines.md`
- `docs/daily_patch/2026-05-13_peak-profit-protection-report-evidence.md`
- `docs/daily_patch/2026-05-14_vwap-reclaim-strategy-and-human-chart-entry-relaxation.md`
- `docs/daily_patch/2026-05-14_strategist-llm-token-budget.md`

---

## 2026-05-15 ~ 2026-05-18 · Runtime Refactor — Runtime-first 점진 리팩터링과 Execution/Reporting 경계 분리
**Stage:** Maintainability  
**Tags:** REFACTOR · RUNTIME · REPORTING

거대한 runtime/reporting hotspot을 기능 변경 없이 단계적으로 분리하는 리팩터링 시작.

### 변경 내용
- incremental refactor plan과 revised runtime-first plan 수립.
- 대형 reporting hotspot map 작성 후 단계적 extraction 진행.
- live execution reporting boundary를 명시적으로 분리.
- entry cascade hardblock과 summary average 계산 정리.
- 리팩터링이 실전 행동을 바꾸지 않도록 regression 중심으로 진행.

### 이 변경의 의미
기능을 계속 붙이면서도 runtime이 단일 거대 파일로 붕괴하는 것을 방지.

### 근거 문서 / 코드
- `docs/dev/incremental_refactor_plan_2026-05-15.md`
- `docs/dev/revised_runtime_first_refactor_plan_2026-05-15.md`
- `docs/dev/phase_9_3_large_reporting_hotspot_map_2026-05-17.md`
- `docs/daily_patch/2026-05-18_live-execution-reporting-boundary.md`

---

## 2026-05-20 · Q1–Q7 — Quant Tactic Engine 도입
**Stage:** Quant Evaluation  
**Tags:** QUANT · SHADOW · TACTIC

LLM 판단만 평가하지 않고 규칙 기반 전술 후보를 Q1~Q7 독립 실험으로 비교하는 Quant Tactic Engine 구축.

### 변경 내용
- Q1~Q6를 독립 tactic slice로 추가.
- Q7을 3개 slice로 나눠 세부 조건을 분리 검증.
- 각 tactic의 판단과 결과를 메인 전략과 분리해 shadow/evaluation 가능하게 설계.
- 동일한 시장 데이터에서 전술별 evidence를 비교할 수 있는 기반 마련.

### 이 변경의 의미
'전략가가 맞았나'에서 '어떤 규칙이 실제 수익 edge를 만들었나'로 평가 단위가 확장.

### 근거 문서 / 코드
- `docs/daily_patch/2026-05-20_quant-tactic-engine-q1.md`
- `docs/daily_patch/2026-05-20_quant-tactic-engine-q7-slice3.md`

---

## 2026-05-21 ~ 2026-05-26 · Q8 Bootstrap — Quant Entry Enforcement와 Q8 Shadow Dataset
**Stage:** Quant Evaluation  
**Tags:** Q8 · QUANT · DATA_QUALITY

Q1~Q7 결과를 바탕으로 Q8 검증 루프를 열고 후보·체결·리포트 truth를 고정.

### 변경 내용
- quant entry enforcement로 정량 조건이 실제 진입 gate에 반영되는 경로 구축.
- Q7 residual Strategist context를 남겨 규칙과 LLM 상호작용 관찰.
- close review를 통해 Q8 핵심 질문 정의.
- Q8 report integrity와 bundle latency 점검.
- candidate shadow dataset과 broker alignment at report generation 추가.
- Kiwoom account snapshot archive와 truth-first ka10170 경로 검증.
- opening momentum probe shadow 및 guard count fix 적용.

### 이 변경의 의미
메인 runtime을 계속 바꾸지 않고 shadow evidence를 축적하는 실험 방식이 정착.

### 근거 문서 / 코드
- `docs/daily_patch/2026-05-21_quant-entry-enforcement.md`
- `docs/daily_patch/2026-05-22_q8_report_integrity_and_bundle_latency.md`
- `docs/daily_patch/2026-05-24_q8_candidate_shadow_dataset.md`
- `docs/daily_patch/2026-05-26_opening_momentum_probe_shadow.md`

---

## 2026-06-01 ~ 2026-06-20 · Q8 Validation — Q8 장기 검증 — Cost Edge, Lane Decision, 실패 원인 분해
**Stage:** Evidence Validation  
**Tags:** Q8 · EVALUATION · COST

Q8을 단기 실험으로 끝내지 않고 실제 기간 데이터를 누적해 비용 이후 edge와 lane별 성능을 검증.

### 변경 내용
- Q8 active behavior patch와 cost-edge promotion state 정의.
- daily review와 lane decision table을 날짜별로 누적.
- below-VWAP reclaim subtype 및 historical review 수행.
- 실패 원인을 Scanner, entry blocker, timing, cost 관점으로 분리.
- 6/19 handoff와 6/20 final comprehensive review로 Q8 평가를 공식 종료/이관.

### 이 변경의 의미
한두 번의 성공 거래가 아니라 반복 가능한 증거가 있어야 promotion한다는 원칙이 강화됨.

### 근거 문서 / 코드
- `docs/daily_patch/2026-06-01_q8_active_behavior_patch.md`
- `docs/tactics/q8_lane_decision_table_2026-06-16.md`
- `docs/evaluation/q8_handoff_2026-06-19.md`
- `docs/evaluation/q8_final_comprehensive_review_2026-06-20.md`

---

## 2026-06-22 ~ 2026-06-26 · Q9 — Fixed Forward Window와 Horizon Observability
**Stage:** Forward Evaluation  
**Tags:** Q9 · EVALUATION · HORIZON

사후 최적화 편향을 줄이기 위해 고정된 forward window와 horizon 계약을 도입.

### 변경 내용
- horizon alignment, Q9 component, loss decomposition decision 문서화.
- fixed forward-window protocol로 평가 조건을 사전에 고정.
- Day1 opening calculation review로 산식과 artifact를 검증.
- 5m/15m/30m/EOD horizon observability 계약 추가.
- 후속 baseline과 동일한 평가 축을 사용할 수 있도록 준비.

### 이 변경의 의미
좋은 결과가 나온 뒤 조건을 바꾸는 것을 막고 prospective evaluation 성격을 강화.

### 근거 문서 / 코드
- `docs/evaluation/q9_fixed_forward_window_protocol_2026-06-23.md`
- `docs/evaluation/q9_horizon_contract_observability_2026-06-26.md`

---

## 2026-06-23 이후 · Independent Baselines — Samsung/Hynix + BTC→우리기술투자 독립 비교군
**Stage:** Forward Evaluation  
**Tags:** BASELINE · BTC_WOORI · LARGE_CAP

Q9 자체 성능만 보지 않고 단순하고 독립적인 외부 baseline과 비교하는 평가 구조로 확장.

### 변경 내용
- 삼성전자/하이닉스 고정 baseline을 Q9와 같은 horizon에서 비교.
- Top1, trade count, 승률, 평균수익률, PF, MDD 비교 구조 마련.
- BTC 선행 움직임과 우리기술투자 반응을 별도 baseline 연구 track으로 추가.
- Commander Final이 baseline 대비 실제 alpha를 냈는지 구분 가능하도록 설계.

### 이 변경의 의미
복잡한 Agent 시스템이 단순 전략보다 정말 나은지를 검증하는 기준선 확보.

### 근거 문서 / 코드
- `docs/evaluation`
- `reports/evaluation/baseline_samsung_hynix`
- `reports/evaluation/baseline_btc_woori`

---

## 2026-07-06 · Q13 — Entry Timing Attribution — 왜 틀렸는지 수치화
**Stage:** Attribution  
**Tags:** Q13 · EXPLAINABILITY · EVALUATION

손익 결과만 보지 않고 후보선정→판단→실제 진입까지 어느 단계가 성능을 깎았는지 attribution score로 분해.

### 변경 내용
- Q13 entry timing attribution 정의.
- attribution score v0 및 기간 누적 score 생성.
- Scanner/Strategist/entry timing 사이의 지연과 결과를 연결.
- observability patch로 누락 timestamp/evidence 품질 개선.
- 실패 원인을 '전략이 나쁨' 하나로 몰지 않는 진단 구조 구축.

### 이 변경의 의미
개선해야 할 Agent/단계를 데이터로 특정할 수 있게 됨.

### 근거 문서 / 코드
- `docs/q13/q13_entry_timing_attribution_2026-07-06.md`
- `docs/q13/q13_attribution_score_v0_2026-07-06.md`
- `docs/q13/observability_patch_2026-07-06.md`

---

## 2026-07-08 ~ 2026-07-21 · Q14–Q16 — Candidate Filtering과 Cost/Horizon Fit 검증
**Stage:** Policy Validation  
**Tags:** Q14 · Q15 · Q16 · POLICY

Q13 attribution 결과를 실제 개선 후보로 바꾸되 곧바로 live behavior를 수정하지 않고 단계별 검증.

### 변경 내용
- Q15 scanner score component candidate 정의 후 filtering patch 적용.
- 2-day decision tree, close decision, adjustment retest로 단기 과적합 방지.
- Q16 cost-horizon-fit patch로 예상 edge가 거래비용을 넘는지 검증.
- 조정안은 정해진 close/retest 절차를 통과해야 유지하도록 운영.

### 이 변경의 의미
아이디어→패치가 아니라 후보→검증→종료/유지의 연구 절차가 정착.

### 근거 문서 / 코드
- `docs/q13_q14_validation/q15_scanner_score_component_candidate_2026-07-08.md`
- `docs/q13_q14_validation/q15_candidate_filtering_patch_2026-07-10.md`
- `docs/q13_q14_validation/post_q15_adjustment_retest_close_2026-07-21.md`
- `docs/q13_q14_validation/q16_cost_horizon_fit_patch_2026-07-21.md`

---

## 2026-07-22 ~ 2026-07-24 · Measurement Integrity + Q17 — Stale Fill 정합성 수정과 Directional Edge 계약
**Stage:** Evaluation Integrity  
**Tags:** DATA_QUALITY · Q16 · Q17

평가값 자체가 오염될 수 있는 stale fill/measurement 문제를 먼저 고치고 방향성 edge 검증으로 진행.

### 변경 내용
- measurement integrity fix로 평가 산식과 evidence source 경계 보정.
- broker stale fill reconciliation fix로 잘못 연결된 체결 제거.
- Q16 Day1 review 및 close decision 수행.
- Q17 directional edge contract patch 추가.
- horizon operational contract도 runtime 동작과 평가 정의가 일치하도록 수정.

### 이 변경의 의미
잘못된 데이터로 전략을 개선하는 더 큰 오류를 막기 위해 measurement authority를 우선시.

### 근거 문서 / 코드
- `docs/q13_q14_validation/measurement_integrity_fix_2026-07-22.md`
- `docs/q13_q14_validation/broker_stale_fill_reconciliation_fix_2026-07-22.md`
- `docs/q13_q14_validation/q17_directional_edge_contract_patch_2026-07-24.md`
- `docs/strategy_horizon_feedback/horizon_operational_contract_fix_2026-07-24.md`

---

## 2026-07-27 ~ 2026-07-30 · Q8–Q17 Closure — 누적 검증 종료 + Same-Symbol Re-entry Control
**Stage:** Policy Closure  
**Tags:** Q17 · GUARD · EVALUATION

Q8~Q17 누적 결과를 닫고 반복 손실 종목 재진입과 평가 무결성을 별도 통제.

### 변경 내용
- Q8-Q17 cumulative review와 close review 수행.
- same-symbol loss/re-entry control 추가.
- evaluation integrity close로 legacy/수정 후 evidence 경계를 명시.
- canonical final review를 통해 더 이상 이름만 바꿔 같은 실험을 반복하지 않도록 종료 상태 고정.

### 이 변경의 의미
실패한 가설을 계속 재포장해 실험하는 연구 부채를 줄임.

### 근거 문서 / 코드
- `docs/q13_q14_validation/q8_q17_cumulative_review_2026-07-27.md`
- `docs/q13_q14_validation/same_symbol_loss_reentry_control_2026-07-29.md`
- `docs/q13_q14_validation/q8_q17_canonical_final_review_2026-07-30.md`

---

## 2026-07-30 · Structural Alpha v1 — Offline Structural Alpha Search와 Hypothesis Competition
**Stage:** Alpha Research  
**Tags:** ALPHA · OFFLINE · RESEARCH

메인 runtime 변경 없이 기존 evidence에서 구조적 alpha 후보를 찾고 서로 경쟁시키는 offline research layer 구축.

### 변경 내용
- structural alpha batch1/batch2 contract와 result 생성.
- post-reclaim offline research와 executable policy v0 초안 작성.
- alpha hypothesis competition v1으로 여러 설명 가설을 동일한 evidence에서 비교.
- structural alpha search closure로 살아남지 못한 가설을 종료.

### 이 변경의 의미
새 전략을 무작정 코딩하기 전에 기존 데이터에서 조건부 edge가 존재하는지 검증하는 연구 단계 추가.

### 근거 문서 / 코드
- `docs/offline_alpha/structural_alpha_batch1_result_2026-07-30.md`
- `docs/offline_alpha/structural_alpha_batch2_result_2026-07-30.md`
- `docs/offline_alpha/alpha_hypothesis_competition_v1_result_2026-07-30.md`
- `docs/offline_alpha/structural_alpha_search_closure_2026-07-30.md`

---

## 2026-07-31 · Integrated Diagnosis — Opening Rank-1 + Selection/Horizon/Sequence 통합 진단
**Stage:** Alpha Research  
**Tags:** RANK1 · DIAGNOSIS · Q11

Rank-1 후보가 왜 실패/성공하는지 단일 수익률이 아니라 선정·보유시간·동일종목 시퀀스로 통합 분석.

### 변경 내용
- existing evidence mining contract/result 작성.
- opening Rank-1 longitudinal, deep-dive, same-symbol sequence review 수행.
- prospective validation 계약으로 사후 분석과 미래 검증 분리.
- integrated selection-horizon-sequence evaluation 추가.
- Scanner market candidates와 Q11 index sanity도 함께 보강.

### 이 변경의 의미
종목선정 문제와 진입/보유 문제를 한데 섞지 않고 전체 trade lifecycle에서 원인을 찾게 됨.

### 근거 문서 / 코드
- `docs/offline_alpha/opening_rank1_deep_dive_2026-07-31.md`
- `docs/offline_alpha/opening_rank1_same_symbol_sequence_review_2026-07-31.md`
- `docs/quant_trade_diagnosis/integrated_selection_horizon_sequence_evaluation_2026-07-31.md`
- `docs/daily_patch/2026-07-31_scanner_market_candidates_and_q11_index_sanity.md`

---

## 2026-08-05 ~ 2026-08-07 · Canonical Alpha Loop — 조건부 Alpha Findings → Canonical Execution Plan → 5-Session Closure
**Stage:** Alpha Research  
**Tags:** ALPHA · CANONICAL · VALIDATION

흩어진 조건부 발견을 하나의 실행/검증 계획과 active research register로 통합.

### 변경 내용
- position horizon revision contract로 horizon 정의 재정렬.
- conditional alpha diagnosis와 integrated conditional alpha findings 작성.
- canonical execution plan으로 어떤 evidence를 언제 수집할지 고정.
- active research register로 살아있는/종료된 가설을 관리.
- five-session closure에서 broad Rank-1 opening은 intraday에서 음수임을 확인하고 무조건 promotion을 거부.
- 조건부 lane은 shadow-only로 유지.

### 이 변경의 의미
좋아 보이는 발견을 즉시 전략으로 승격하지 않고 prospective evidence를 요구하는 연구 거버넌스가 완성됨.

### 근거 문서 / 코드
- `docs/offline_alpha/conditional_alpha_diagnosis_2026-08-06.md`
- `docs/offline_alpha/canonical_execution_plan_2026-08-06.md`
- `docs/offline_alpha/active_research_register_2026-08-07.md`
- `docs/offline_alpha/five_session_closure_2026-08-07.md`

---

## 2026-08-11 ~ 2026-08-12 · Rank-1 Feature Mart — Canonical Feature Mart + Prospective Shadow + Strategy Choice Observability
**Stage:** Alpha Research  
**Tags:** FEATURE_MART · SHADOW · OBSERVABILITY

Rank-1 후보 연구에 필요한 feature/evidence를 canonical mart로 고정하고 미래 데이터에서 재검증.

### 변경 내용
- canonical Rank-1 feature mart 구축.
- fixed-candidate prospective shadow로 후보 조건을 고정한 채 관찰.
- fresh-change activation shadow로 단순 재등장과 새로운 signal 활성화를 구분.
- strategy-choice observability로 어떤 조건에서 어떤 전략 선택이 일어났는지 기록.

### 이 변경의 의미
연구 데이터셋이 코드마다 달라지는 문제를 줄이고 prospective comparison의 재현성을 높임.

### 근거 문서 / 코드
- `docs/offline_alpha/canonical_rank1_feature_mart_2026-08-11.md`
- `docs/offline_alpha/rank1_fixed_candidate_prospective_shadow_2026-08-11.md`
- `docs/offline_alpha/rank1_fresh_change_activation_shadow_2026-08-12.md`
- `docs/offline_alpha/rank1_strategy_choice_observability_2026-08-12.md`

---

## 2026-08-13 · Memory Integrity Review — Historical Memory 영향 재검증
**Stage:** Agent Memory  
**Tags:** MEMORY · EVALUATION

과거 memory가 실제 의사결정에 도움을 주는지, 잘못된 기억이 누적되지 않는지 별도 integrity review 수행.

### 변경 내용
- memory integrity correction으로 잘못된/오염된 memory 연결 수정.
- historical memory impact review로 memory 사용 전후 판단 영향 평가.
- Memory를 무조건 많이 넣는 것이 아니라 evidence가 있는 정보만 유지하는 방향 강화.

### 이 변경의 의미
Agent memory가 설명용 장식이 아니라 성능/편향을 측정해야 하는 독립 컴포넌트가 됨.

### 근거 문서 / 코드
- `docs/runtime_memory/memory_integrity_correction_2026-08-13.md`
- `docs/runtime_memory/historical_memory_impact_review_2026-08-13.md`

---

## 2026-08-14 · Web Observability M0–M6 — Read-only FastAPI + React/Vite 운영 UI MVP
**Stage:** Productization  
**Tags:** WEB_UI · API · OBSERVABILITY

trading runtime과 완전히 분리된 read-only 웹 관측 계층을 구축해 포트폴리오에서도 시스템 상태를 보여줄 수 있게 됨.

### 변경 내용
- M0 product/data contract와 truth/time/cost/availability 계약 고정.
- M1 isolated FastAPI health/config/path/bounded-read foundation 구축.
- M2 Performance, M3 Trades/Reports, M4 Opportunities/Strategies/Market API 완성.
- M5 React/Vite 기반 9-domain operating console 완성.
- M5.1 OpenRouter role/model/stage/status/latency를 보여주는 LLM Operations 추가.
- M6 public profile과 anomaly surface를 server-side sanitized read model로 구현.
- API 계층은 Trading Core import 0, write call 0, non-GET route 0으로 격리 검증.

### 이 변경의 의미
자동매매 내부 개발 프로젝트에서 외부에 설명 가능한 운영 제품/포트폴리오 형태로 전환.

### 근거 문서 / 코드
- `docs/web_observability/implementation_status_2026-08-14.md`
- `docs/web_observability/m5_web_ui_implementation_2026-08-14.md`
- `docs/web_observability/m6_anomaly_public_profile_implementation_2026-08-14.md`

---

## 2026-08-14 · Opening Probe — Opening Rank-1 Controlled Probe
**Stage:** Alpha Research  
**Tags:** RANK1 · PROSPECTIVE · SHADOW

오프닝 Rank-1 조건을 통제된 probe로 좁혀 live promotion 없이 prospective evidence를 수집.

### 변경 내용
- broad opening rule을 재도입하지 않고 제한된 controlled probe 정의.
- independent episode/day-symbol 단위 표본을 우선하도록 유지.
- 비용 기준을 명시해 gross와 live-net을 분리.
- 조건부 성능이 나와도 자동 promotion하지 않는 shadow-only 원칙 유지.

### 이 변경의 의미
과거 성과가 좋아 보이는 조건을 live rule로 즉시 되살리는 것을 방지.

### 근거 문서 / 코드
- `docs/offline_alpha/opening_rank1_controlled_probe_2026-08-14.md`

---

## 2026-08-18 · Web M7 — Docker Compose 배포 계층
**Stage:** Deployment  
**Tags:** DOCKER · WEB_UI · DEPLOYMENT

private/public Web UI와 API를 컨테이너로 띄우기 위한 M7 배포 코드 완성.

### 변경 내용
- API/UI image와 private/public Compose 구성.
- trading runtime과 web observability의 isolation 유지.
- local Docker engine 검증을 다음 gate로 설정.
- M8 Kubernetes local overlay는 Compose 통과 이후로 순서를 고정.

### 이 변경의 의미
개발 PC 로컬 실행에서 재현 가능한 배포 단위로 확장.

### 근거 문서 / 코드
- `docs/web_observability/m7_docker_compose_implementation_2026-08-18.md`

---

## 2026-08-21 · Measurement Integrity v2 — Q10/Q11/Q13/Q14–Q18 측정 권위 재정립
**Stage:** Evaluation Integrity  
**Tags:** Q10 · Q11 · Q13 · Q18 · DATA_QUALITY

legacy 평가값과 수정 후 prospective cohort가 섞이지 않도록 point-in-time·timestamp·horizon 계약을 재정의.

### 변경 내용
- Q10 point-in-time market snapshot 정합성 보강.
- Q11 shadow-position follow-through와 index sanity 보정.
- Q13 stage timestamp와 decision-to-entry delay를 실제 evidence 기반으로 수정.
- Q14 outcome-conditioned diagnosis와 structural root cause 분리.
- Q16 day-integrity, Q17 intended horizon, Q18 horizon-specific coverage 추가.
- 수정 전 legacy 측정은 corrected prospective cohort와 합산하지 않도록 authority boundary 고정.

### 이 변경의 의미
평가 시스템 자체의 신뢰도를 전략 성능만큼 중요하게 취급하는 단계로 진화.

### 근거 문서 / 코드
- `docs/daily_patch/2026-08-21_q10_q11_q13_measurement_integrity.md`
- `docs/daily_patch/2026-08-21_q14_q18_measurement_integrity.md`

---

## 2026-08-21 · Alpha Research Board — 살아있는 가설/종료 가설을 한 화면에서 관리
**Stage:** Research Governance  
**Tags:** ALPHA · BOARD · RESEARCH

기존 Q와 offline research를 반복하지 않고, 살아있는 discriminator와 폐기된 가설을 하나의 board 계약으로 통합.

### 변경 내용
- OPENING_CONDITIONAL, SCANNER_REACTIVATION_HORIZON, BTC_WOORI, LARGE_CAP_TWO_SYMBOL 4개 fixed research track 정의.
- ACTION_REVIEW, OBSERVE_FIXED, DATA_REPAIR_BOUNDARY, CLOSED_NEGATIVE_PROSPECTIVE, CLOSED bucket 도입.
- 독립 day-symbol/episode를 primary sample count로 고정.
- gross, 0.28% live research net, broker-observed mock net을 분리.
- R1_SCANNER_RISK_HIGH_30M_V1은 contributor dependence로 reject하여 generic HIGH risk discriminator를 폐기.
- Q phase를 새로 만들지 않고 기존 evidence를 board supplier로 재사용.

### 이 변경의 의미
연구가 Q번호만 늘어나는 구조에서 '무엇이 살아 있고 무엇이 폐기됐는가'를 관리하는 포트폴리오형 연구 운영으로 전환.

### 근거 문서 / 코드
- `docs/offline_alpha/alpha_research_board_contract_2026-08-21.md`

---

## 2026-08-21 · Immediate Opening Runtime Validation — 오프닝 Probe의 Runtime Evidence 검증
**Stage:** Research Governance  
**Tags:** OPENING · RUNTIME · VALIDATION

offline에서 정의한 오프닝 조건이 실제 runtime artifact에서 같은 의미로 관찰되는지 검증.

### 변경 내용
- controlled opening probe와 runtime artifact의 필드/시간 정합성 확인.
- missing source는 추정값으로 채우지 않고 missing evidence로 유지.
- promotion이 아니라 measurement path 검증에 초점을 둠.

### 이 변경의 의미
offline research와 실제 runtime 사이의 semantic drift를 줄임.

### 근거 문서 / 코드
- `docs/offline_alpha/immediate_opening_probe_runtime_validation_2026-08-21.md`

---

## 2026-08-27 · Current — 현재 — 7-Agent + Guarded Execution + Evidence Research + Web Observability
**Stage:** Current  
**Tags:** CURRENT · AGENT · ALPHA · WEB_UI

자동주문 스크립트를 넘어 판단·실행·평가·연구·운영 UI가 서로 분리된 포트폴리오급 Agentic Trading System 상태.

### 변경 내용
- Commander/Strategist/Scanner/Monitor/Supervisor/Executor/Reporter 7-Agent 역할 유지.
- 실행은 approval + deterministic guards + idempotency 뒤에서만 허용.
- Q8~Q18, Rank-1, Alpha Research Board를 통해 evidence-driven 개선 루프 운영.
- Samsung/Hynix와 BTC→우리기술투자 같은 독립 baseline/research track 보유.
- Runtime Memory와 Reporter feedback/effectiveness를 통해 장기 개선 영향 분석 가능.
- FastAPI/React Web Observability와 public sanitized profile로 외부 시연 가능.
- 다음 제품화 과제는 patch-note timeline 자체를 UI에 추가하고, 배포 URL/운영 화면을 하나의 showcase로 묶는 것.

### 이 변경의 의미
현재 시스템의 핵심 가치는 'AI가 매매한다'가 아니라 'AI 판단을 안전하게 실행하고, 그 결과를 다시 검증해 다음 정책을 개선하는 폐쇄루프'에 있음.

### 근거 문서 / 코드
- `README.md`
- `docs/01_overview.md`
- `docs/offline_alpha/alpha_research_board_contract_2026-08-21.md`
- `docs/web_observability/implementation_status_2026-08-14.md`

---

## UI 구현 권장 구조

이 상세본은 기본 화면에서 모든 내용을 펼쳐놓기보다 **날짜 + 버전 + 제목 + 1줄 summary**를 먼저 보여주고, 클릭/Expand 시 `변경 내용`, `이 변경의 의미`, `근거 문서`를 펼치는 방식이 적합하다.

권장 필터: `ALL / CORE / AGENT / STRATEGY / LIVE / SAFETY / QUANT / ALPHA / MEMORY / REPORTER / WEB UI / DEPLOYMENT`.

최신 항목에는 `CURRENT` 배지를 표시하고, M/Q/웹 마일스톤은 작은 version chip으로 따로 표시한다. 날짜가 범위인 초기 기록은 범위 그대로 노출하며 임의의 하루로 축약하지 않는다.

### JSON 필드

- `date`: 대표 날짜 또는 날짜 범위
- `version`: M/Q/기능 버전
- `title`: 카드 제목
- `stage`: 프로젝트 단계
- `types`: UI 필터용 태그 배열
- `summary`: 접힌 상태에서 보이는 1줄 요약
- `details`: 펼쳤을 때 보이는 실제 변경 목록
- `impact`: 왜 중요한 변경인지
- `sources`: 저장소 내부 근거 경로
- `status`: historical/current
# 2026-08-28 - Controlled Mock Four-Lane Execution

- Opening Alpha now executes only for `HIGH_COMMON_DIRECTIONAL` or
  `CONFIRMED_RECURRENT_RANK`, using the existing multi-agent selected candidate.
- Q12 BTC-Woori, Q10 Semiconductor and Q10 Index can submit one Kiwoom mock order
  attempt per lane/day through the existing Executor.
- Independent lanes preserve Q9 attribution boundaries and store their own
  strategy/horizon provenance.
- Added lane reservation and opening recurrence artifacts under `data/logs/`.

# 2026-08-28 - Controlled Lane Report Evidence

- Q10/Q12 trade reports show the lane, signal ID, fixed hypothesis evidence,
  score, hold window and mock-only execution scope.
- Closed trades recover the original lane evidence from the position strategy
  frame and daily reservation ledger instead of guessing from the exit cycle.
- Reports show whether R3 horizon revision was allowed for the position.
- Q10/Q12 controlled lanes keep R3 revision disabled so fixed-horizon validation
  remains comparable; normal positions keep the existing R3-to-Monitor path.

# 2026-08-29 - M7.4 Cloudflare Private Ingress

- Added an optional `cloudflared` Compose overlay for `https://agentra.win`.
- The existing Web Nginx is the only origin; API and Trading Runtime ports remain
  private.
- The connector is pinned, non-root, read-only and resource bounded.
- Cloudflare Access must allow only the operator email with OTP before startup.
- Normal local Compose operation does not load or start the Tunnel.

# 2026-08-31 - Q10/Q12 Point-in-Time and Execution Wiring

- Q10 lead-market inputs are frozen at 08:50 before the intraday loop, and Q12
  BTC inputs are captured by a separate 08:55 scheduled task with a daily
  submission ledger.
- Q10/Q12 controlled candidate evaluation now runs before Strategist/Scanner,
  so their early returns cannot suppress an otherwise valid fixed-lane signal.
- Controlled lane evidence is split into evaluation, broker-attempt and
  broker-accepted submission ledgers.
- The daily lane limit is consumed only after broker acceptance or fill. Missing
  input, no candidate and broker rejection remain visible without falsely using
  the daily allowance.
- Added an end-to-end mock integration test from candidate through persisted
  fill state.

# 2026-08-31 - Pre-Claude Refactoring Provenance Baseline

- Fixed the pre-Claude refactoring source baseline at
  `6aa4e398e2e1c33482cab3dbf2518e7b03c18a10`; its recorded verification is
  `2701 passed, 1 skipped`.
- Added an evidence-indexed development history while preserving existing
  historical and patch-note records without reinterpretation or rewriting.
- Marked pre-Git M1-M13 chronology and attribution as inferred, and applied
  `VERIFIED`, `SUPPORTED`, `UNCERTAIN`, and `UNKNOWN` provenance levels.
- Separated Historical Architecture, Target Architecture, and Current AS-IS.
- Described the period from 2026-04-07 as a supported Codex-centered workflow
  without attributing individual commits to Codex when direct evidence is
  absent.
- Recorded current architecture mismatches only as known debt or audit
  findings. No source, runtime, strategy, execution, guard, DTO, test, or
  trading behavior was changed.
- Added the reusable provenance record template and evidence index under
  `docs/development/` for future Claude Code work and Codex cross-review.

# 2026-08-31 - Controlled Lane Observability and Test Integrity

- Confirmed the existing Opening Alpha relaxation and Q10/Q12 point-in-time
  wiring without changing trading policy.
- Added rejected-candidate evidence for Opening Alpha and surfaced Q10, Q12 and
  Opening Alpha status in the operator daily summary.
- Split Q12 intraday shadow evidence from the mandatory 08:55 controlled-lane
  input status so missing snapshots cannot appear generally available.
- Isolated execution tests from the live canonical report tree and identified
  prior `.pytest-work` artifacts for evidence-based cleanup.

# 2026-09-01 - Q12 Capture Rehydration and Trade Report Truth Alignment

- Q12 now rehydrates every baseline payload from the immutable 08:55 capture,
  including processes that were already holding a pre-capture in-memory payload.
- Q12 hypothesis evaluation reads the dedicated captured source instead of a
  newer provider row whose 24-hour momentum is not ready yet.
- Closed-trade summaries derive hold duration from entry/exit execution
  timestamps and keep broker realized PnL authoritative over monitor marks.
- Deterministic, horizon, final conclusion and LLM display sections now use the
  same execution duration and realized result.
- Trading behavior, thresholds, order routing and lane eligibility were not
  changed.

# 2026-09-01 - Opening Alpha Price Integrity

- Open positions are included in every market-quote hydration pass even when
  their symbol falls outside the current Scanner candidate limit.
- Every hydrated quote carries an observation timestamp. A quote older than 90
  seconds is replaced by the current account-position price, or rejected when
  no trustworthy fallback exists.
- Opening Alpha records the first Rank-1 signal price and rejects a delayed
  controlled-probe entry after positive signal-to-entry drift exceeds 2%.
- Immediately before broker submission, Opening Alpha independently compares
  the same initial signal price with the latest available best ask. A drift
  above 2% is recorded as `opening_alpha_execution_price_drift` and exits as
  `NOT_SENT` without calling the broker order API.
- A held-symbol quote older than the expected refresh cadence is cross-checked
  against the account current price when the two sources disagree on whether a
  hard stop has fired. The validated current source wins in either direction;
  a cached quote alone cannot force liquidation.
- Exit artifacts retain quote age, divergence and replacement evidence for
  later report reconstruction.
- Post-exit recap reuses an observed Opening Rank-1 EOD checkpoint when minute
  data cannot reach the regular close, and Alpha Board runtime validation is
  generated directly instead of being lost during canonicalization.
- If the 16:00 Opening Rank-1 closeout refresh cannot reach Kiwoom, it retries
  once in offline/local-artifact mode and records the degraded source instead of
  failing the entire closeout job.
- The 2026-09-01 recap was regenerated with all +5/+15/+30/+60/EOD checkpoints
  observed. No Scanner ranking, Strategist prompt or normal entry/exit threshold
  was changed.

## 2026-09-05 - PRE-Step5C observation and execution truth

- Preserve canonical Scanner rank and explicit broker outcomes.
- Keep unverified index observations out of reaction/return calculations.
- Serialize manifest updates and retain permanent per-attempt claim receipts;
  incomplete acquisition is never automatically replayed.
- Separate actual operation authority, validation evidence and promotion.
- Strategy rules and Step5B mutation safety remain unchanged. See
  `docs/development/pre_step5c_owner_closeout.md` for limits and provenance.

## 2026-09-06 - Step5C durable execution ownership

- Canonical intent_id and atomic SQLite approved-to-executing ownership.
- Concurrent/restarted duplicate calls cannot resubmit the same intent.
- Backend failure submits zero orders; UNKNOWN/crash remains reconciliation-required.
- Existing guards, Supervisor approval and Step5B transport policy are unchanged.
- See `docs/development/step5c_execution_owner.md` for scope and lifecycle semantics.
# 2026-09-07 Q12 vNext

## Q12 V2 corrective update

Weekday 08:45 Q12 preopen task launches the existing day-scoped runner before
the immutable 08:55 capture. The 09:00 stack reuses that runner. Strategy and
order execution conditions are unchanged.

US session comparison now uses BTC at the same two US closes, with weekend BTC
movement separate. V1 records remain immutable. An opening-only input worker
publishes original Q12 features independently of the full report, and runtime
reads the canonical 08:55 BTC source directly. No threshold or broker-path change.
See docs/evaluation/q12_vnext_delivery_time_alignment.md.

Add versioned COIN/MSTR confirmation, opening reaction, A/B candidate comparison,
and immutable forward observations. Existing live Q12, Commander and Executor
are unchanged. Missing data is UNKNOWN, not a new live veto. Definitions and
limitations: docs/evaluation/q12_vnext_crypto_equity_confirmation.md.

# 2026-09-07 - Controlled Lane Cost, VWAP, and Report Integrity

- Connected `CONFIRMED_RECURRENT_RANK` to its approved lane evidence instead of
  requiring an unrelated candidate setup classification. Explicit negative
  cost evidence remains blocking.
- Restricted intraday VWAP exits to current-session minute evidence and rejected
  daily feature-engine VWAP distance as an exit trigger.
- Recovered Q10/Q12 report identity only by exact entry order or run ID, marked
  main Scanner rank as not applicable, and anchored timing to the lane signal.
- Regenerated the 000660 Q10 report with complete post-exit EOD evidence. No Q10
  entry rule, Scanner ranking, cost threshold, or horizon policy was changed.
# 2026-09-08 Opening Alpha Observation Integrity

- Record missing Rank prices from existing fresh quote/minute evidence, without additional API calls.
- Preserve passing executable-price guard results in event logs and canonical Executor artifacts.
- Remove the incorrect fixed one-share cost wording. Unverified Opening Alpha LLM causal claims are not presented as established findings; raw responses remain intact.
- No entry/exit threshold or strategy changes. See `docs/daily_patch/2026-09-08_opening_alpha_observation_integrity.md`.
- Follow-up: align stale max-hold/min-hold assertions with the current safety contract and isolate default metrics output during pytest.
- Final clean-room regression: 3,048 passed, 1 skipped, 0 failed; production-path manifest clean.

# 2026-09-09 - Exit Threshold and Horizon Integrity

- Prevent cached Stage 3/Stage 4 review payloads from being applied unless the
  current run ID and Strategist call kind both match the review stage.
- Synchronize active horizon `max_sec` with both Monitor `max_hold_sec` and
  `time_stop_sec`.
- Preserve raw structural stop, minimum stop floor, stop source and invalidation
  price through final Monitor artifacts.
- Keep Scanner ranking, entry eligibility, stop/take-profit percentages and
  broker execution policy unchanged.
- See `docs/daily_patch/2026-09-09_exit_threshold_and_horizon_integrity.md`.

# 2026-09-09 - Evaluation Observability and Opening Policy Matrix

- A single realized loss is reported as `YELLOW`, not `GREEN`.
- Q12 distinguishes an expected closed opening window from an active-window input delay.
- Q10 displays unverified index captures separately without using them in calculations.
- Q9 exposes forward failure status signatures while retaining the 95% coverage rule.
- Opening Alpha is compared by asset family, risk, setup and horizon in a new
  observation-only day-symbol matrix.
- Controlled Opening Alpha decisions persist a stable relaxation-lane discriminator
  cell ID without changing current eligibility.
- Aligned three stale exit/cooldown tests with the current policy contract:
  cost-aware max-hold reassessment and applied-policy cooldown authority.
- Corrected patch-note metadata from 68 to 69 entries; historical entries were
  not rewritten.
- Clean full regression after stopping the live writer: `3053 passed, 1 skipped`.
- This test alignment changes no runtime trading behavior.
- See `docs/daily_patch/2026-09-09_evaluation_observability_and_opening_matrix.md`.

# 2026-09-10 - Stale Expected Exit Quote Integrity

- Prevent stale or materially conflicting best-bid data from blocking valid
  cost-aware profit exits.
- Preserve expected-exit quote age, divergence and rejection provenance in
  Monitor artifacts.
- Verified live recovery on `024060`: `SELL / take_profit`, 57 shares, broker
  order `0083909`, followed by zero open positions.
- Entry policy, Scanner ranking, cost thresholds and broker semantics are unchanged.
- Focused regression: `68 passed`.
- See `docs/daily_patch/2026-09-10_stale_expected_exit_quote_integrity.md`.

# 2026-09-10 - Evaluation Closeout Integrity

- Keep the broker-authoritative `024060` result and valid selection/entry evidence,
  but exclude its incident-contaminated exit and horizon attribution.
- Rebuild Alpha Research Board companion reports from authoritative builders.
- Persist Q9 closeout minute recovery and reuse it for final day-validity metrics.
- Treat `+120m/+180m` as Samsung/Hynix baseline-only rather than falsely making
  the shared Q9 comparison incomplete.
- Prefer the active Commander horizon in operator summaries and recognize the
  post-exit recap as the inventory artifact.
- Full regression: `3059 passed, 1 skipped`.
- See `docs/daily_patch/2026-09-10_evaluation_closeout_integrity.md`.

# 2026-09-14 - Opening Alpha Initial Signal Price Integrity

- Resolve the already available fresh Rank-1 quote before controlled Opening
  Alpha probe evaluation when the Scanner candidate has no price.
- Preserve that observed price and its source as the initial signal provenance
  used by the pre-submit executable-price drift guard.
- Enrich only the probe evaluation copy. Scanner ranking, selected candidate,
  entry conditions, the two-percent drift threshold and broker semantics are
  unchanged.
- Focused regression: `4 passed`.

# 2026-09-14 - Q10 Signed Executable Price Integrity

- Normalize Kiwoom quote direction prefixes before Q10 order-notional checks.
- A fresh best ask such as `-105820` is now treated as executable price
  `105820`, preserving `market.quote.best_ask.live_refresh` provenance.
- Q10 strategy, eligibility, score, order limits and broker semantics are
  unchanged.
- Regression: signed-price case passed; focused execution-price suite passed
  `12 tests` (the session-level production-write detector separately observed
  concurrent watchdog runtime writes).

# 2026-09-27 - UEF-5.1 Clean Evidence Registry

- Establishes CLEAN/QUARANTINED/FIELD_INVALID/REVIEW_REQUIRED/NO_RULE evidence classification, with a positively-proven clean domain required before anything is treated as CLEAN.
- Independently audited and approved after one correction round; a single non-blocking numeric discrepancy was intentionally left on record rather than silently resolved.
- No Scanner ranking, Strategist behavior, Monitor rules, or broker execution changed.
- Downstream historical recompute (UEF-5.2) now has a proven, auditable admissibility gate instead of an implicit assumption about which evidence is trustworthy.
- See `docs/daily_patch/2026-09-28_uef5_formal_freeze_and_patch_backfill.md`.

# 2026-09-28 - UEF-5.2 Historical Recompute

- Candle admission requires a verified, acquisition-issued data receipt rather than a caller-supplied trust flag.
- A dedicated session policy projects admitted candles onto the canonical trading session before any evaluation runs.
- Independently audited and approved after two correction rounds; one non-blocking debt item was intentionally left on record.
- No legacy comparison and no parity claim -- that boundary belongs to UEF-5.3.
- Historical evaluation numbers are now reproducible from a bound, verifiable input chain instead of ad hoc recomputation.
- See `docs/daily_patch/2026-09-28_uef5_formal_freeze_and_patch_backfill.md`.

# 2026-09-28 - UEF-5.3 Historical Dual Run

- Classifies every material difference through a bounded taxonomy instead of guessing; never treats an undefined legacy metric as a fake zero.
- Gates any numeric comparison on a positively-proven shared population, never on count equality alone.
- Independently audited and approved after five correction rounds; one non-blocking debt item was intentionally left on record.
- Produces no strategy conclusion and no ranking -- comparison classification only.
- The system can now state, with evidence, where legacy and canonical evaluation agree, disagree, or are not comparable -- instead of assuming parity.
- See `docs/daily_patch/2026-09-28_uef5_3_formal_freeze.md`.

# 2026-09-28 - UEF-6 Dedup and Evidence Lineage

- Distinguishes raw rows, physical events, evaluation subjects and evaluation records, reusing the existing identity rules rather than inventing new ones.
- A direct evidence-lineage sidecar proves aggregate membership only when it was actually witnessed at computation time; without that witness, lineage is reported as not available rather than guessed.
- Historical validation against a real target run correctly reported a byte-level input mismatch as non-reproducible instead of silently accepting stale data.
- Independently audited and approved after three correction rounds.
- Aggregate metrics can now be checked for accidental double-counting and, where a direct witness exists, traced to the exact evidence rows they were built from.
- See `docs/daily_patch/2026-09-28_uef6_formal_freeze.md`.

# 2026-09-29 - UEF-7 Alpha Board Normalization

- Preserves every candidate row exactly -- no merging, no reordering, no promotion decision.
- Groups candidates that share the same source evidence, while explicitly stating that shared or different source evidence never proves the candidates share or don't share a population.
- Independently audited and approved after three correction rounds, including a fix closing an adversarial input path that could otherwise smuggle an unrecognized field into the result's identity.
- Downstream comparison tooling can now read one consistent, verified view of the Alpha Board instead of each consumer re-deriving its own interpretation.
- See `docs/daily_patch/2026-09-29_uef7_formal_freeze.md`.

# 2026-09-29 - UEF-8 Fair Comparison Validation

- Every candidate pair is classified as comparable, conditionally comparable, or not comparable, based only on scope, evidence and provenance facts -- never on a metric's own performance value.
- Independently audited and approved after two correction rounds: individually-proven evidence for two candidates does not by itself prove their populations can be compared, and pair identifiers were hardened against a hash-collision edge case.
- Introduces no score, rank, winner or promotion recommendation of any kind.
- The system can now say, with evidence, whether a comparison between two candidates is currently trustworthy -- instead of silently assuming every pair is comparable.
- See `docs/daily_patch/2026-09-29_uef8_formal_freeze.md`.

# 2026-09-29 - UEF-9 Formal Evaluation Authority -- UEF Complete

- Proves that a given comparison result genuinely belongs to a given candidate result, and that no candidate or comparison pair was silently added, dropped, or duplicated.
- Reports one of two outcomes only -- the authority chain is valid, or it is rejected outright -- never a partial or confidence-scored result.
- Records, as an explicit and intentional limitation (not a defect), that the current evaluation schema cannot yet prove two candidates share or differ in their underlying evidence population, so no pair can currently be marked fully comparable.
- Introduces no ranking, promotion, or trading authority -- evaluation validity only.
- The evaluation framework underneath the trading system's research process is now a single, internally-verified authority chain from raw candidate facts through to a final validity verdict.
- See `docs/daily_patch/2026-09-29_uef9_uef_complete.md`.

# 2026-09-29 - UEF P1.1 Real-Run Acceptance

- The chain accepted the real snapshot and returned a valid authority result end to end.
- Replaying the exact same captured snapshot produced identical results, confirming the chain has no hidden randomness or timing dependence.
- Deliberately corrupted copies of the intermediate results were all correctly rejected, confirming the authority checks are not bypassable.
- Verified the evaluation run wrote only to its own report output location and never touched live trading state, logs, or broker data, even while the live trading system kept running and writing concurrently.
- Confirms the frozen evaluation framework is not just theoretically correct but actually works against real, live repository data without interfering with trading operations.
- See `docs/daily_patch/2026-09-29_uef_p1_1_real_run_acceptance.md`.

# 2026-09-29 - Patch Notes Backfill and Canonical Sync

- Traced the Patch Notes UI to its actual data source (a structured JSON file plus its human-readable companion) and confirmed the API and UI code were both working correctly -- only the underlying data file had gone stale.
- Added the missing UEF-5.1 through UEF-9 freeze milestones and the P1.1 real-run acceptance entry, in the order they actually happened, without altering any existing entry.
- Added a regression test that fails if the technical patch-note archive (docs/daily_patch/) ever contains a newer dated entry than the Patch Notes UI's own data file, so a future stall is caught automatically instead of discovered by a user.
- The Patch Notes UI now reflects the true, current state of the project, and a recurrence of the same silent staleness will be caught by an automated check.

# 2026-09-29 - P1.3 Pytest Harness Speedup and Shutdown-Flag Safety Fix

- Split the test-session production-write safety scan into a fast default (a few seconds) and an unweakened full audit mode, cutting the fixed cost every test run paid regardless of which tests actually ran.
- Fixed a concurrent-test-run collision where two test processes running at the same time could fail each other's file cleanup.
- Classified the small number of tests that genuinely spawn a real separate process, so the normal test loop can skip them without losing their coverage.
- Fixed a real bug found while isolating a stalled test: a background trading loop silently ignored a caller's shutdown signal object whenever it wasn't the exact internal class, which could make the loop never stop; it now either accepts a compatible signal object or fails immediately and visibly instead of silently substituting one that never fires.
- Fixed a second bug the same investigation introduced and then closed within this change: an earlier fix to the test-collision issue above briefly broke test path isolation for explicitly-supplied paths, which in turn made a manual crash-reconciliation audit trail appear to go unwritten; both are now confirmed correct.
- Taught the fast safety scan to recognize a small number of files this machine's own live trading process legitimately keeps writing to, so those no longer register as false test failures -- the full audit mode still checks them.
- Corrected a stale executor-exception test fixture that omitted a required BUY price and fresh empty open-order snapshot and therefore never reached its fake executor; it now asserts one executor call and propagation of the deliberate `RuntimeError`, without changing production execution behavior.
- The full P1.3 safety-related test set (20 files) now runs together in 45.58 seconds (220 passed, 0 failed, 9 tests deliberately run separately as a heavy subset) with no false failures, down from a run that previously exceeded 25 minutes. The separate heavy subset also passes cleanly (9 passed, 0 failed).
- Explicit status: implemented = yes, targeted test validation = pass, heavy test validation = pass, Docker operational acceptance = pending, full-session soak = pending, P1.3 overall = not yet closed. This entry covers test-harness correctness and speed only, not the separate P1.3 Docker operational acceptance milestone.
- See `docs/daily_patch/2026-09-29_p1_3_pytest_harness_and_shutdown_safety_fixes.md`.

# 2026-09-29 - Daily Alpha Board / UEF EOD Automation Gap Closed

- Discovered during routine cross-day observation: the daily evaluation summary had not actually updated in several days, even though nothing was reporting an error.
- Traced the cause to a missing automatic daily trigger -- the evaluation chain existed and worked correctly whenever it was run, but nothing was running it on a schedule.
- Built one single, reusable daily evaluation entry point that any current or future scheduler can call, so the evaluation logic itself is never duplicated across scheduling systems.
- Added an explicit safety check that refuses to publish a daily result if the underlying data is not actually dated for that day, even if a top-level label would otherwise have said so -- so a stale result can no longer be mistaken for a fresh one.
- A daily result is only published once the full chain has completed successfully; a failure at any point leaves the previous, still-valid result in place rather than showing a misleading update.
- Attempted today's recovery run: it correctly declined to publish, because some of the underlying daily data genuinely has not updated since the prior trading day -- this is the new safety check working as intended, not a new problem.
- Frozen evaluation semantics were unchanged.
- See `docs/daily_patch/2026-09-29_daily_uef_eod_wiring.md`.

# 2026-09-29 - Daily UEF Publication Boundary Hardened (Fix2)

- An independent review of the same-day daily-evaluation wiring fix found three real gaps before it went live.
- Found and removed a second, independent code path that could publish a daily result on its own, without going through the evaluation chain at all.
- Closed a gap where the data actually evaluated and the data actually published could theoretically differ if something changed in between -- publication now uses the exact same captured data throughout.
- Replaced a one-size-fits-all freshness rule with specific, evidence-based rules per data source.
- Made it structurally impossible for a diagnostic check of old data to publish a real result.
- Hardened the final publish step so an interruption partway through can never leave a half-written or mixed-authority result in place.
- Re-verified against this system's real current data: it still correctly declines to publish today's result, because some source data genuinely has not updated.
- Frozen evaluation semantics were unchanged.
- See `docs/daily_patch/2026-09-29_daily_uef_eod_wiring_fix2.md`.

# 2026-09-29 - Pytest Artifact Hygiene (Permanent Fix)

- An earlier same-day test-speed fix had an unintended side effect: it left a small leftover folder behind in the project after every test run.
- Moved test temporary files to the operating system's own temp folder instead of inside the project.
- A successful test run now deletes its own temporary folder immediately when it finishes; a failed or interrupted run keeps it briefly for troubleshooting but it is swept automatically on the next run, so nothing builds up.
- Removed the leftover folders already found from before this fix, and added a permanent project rule plus an automated check so this cannot quietly return.
- See `docs/daily_patch/2026-09-29_pytest_artifact_hygiene.md`.

# 2026-09-29 - Daily UEF Canonical Publication Authority Closure

- Found and closed a second, older path that could still publish a daily result on its own.
- Every piece of data allowed into a daily result must now be on an explicit, reviewed list; anything unreviewed is refused rather than silently allowed through.
- A daily result is now only considered genuine once a small, tamper-evident completion record formally binds every piece of it together and every piece has been verified to be unaltered.
- A day that already has a valid result is never put at risk by a later attempt that fails partway through.
- The single machine-readable pointer to the current result is the only thing anything should trust as authoritative; the human-readable summary is a convenience copy and its own failure never affects the real result.
- Re-verified against this system's real current data: today's result is still correctly unavailable, because some source data genuinely has not updated.
- Frozen evaluation semantics were unchanged throughout.
- See `docs/daily_patch/2026-09-29_daily_uef_authority_closure.md`.

# 2026-09-30 - Closeout Failure Diagnostics Hardened

- This does not fix the closeout data-freshness gap found on 2026-09-29 -- it makes the two paths that generate this data diagnosable, since both were previously failing without leaving any usable trace. A behavioral fix is expected in a separate follow-up.
- Traced why a live background process that should refresh daily evaluation data had not recorded a successful action in several days: it was catching real failures internally but writing the error to a location that never actually gets saved to disk.
- Traced two separate failures in the scheduled backup path for the same daily refresh: one run hung silently for about ten minutes before failing with no output at all, and a different run the next day was cut off almost immediately by an external interruption -- confirmed not a wider system problem.
- Found that two specific pieces of daily data were not failing due to a bug, but because the source market history they depend on was genuinely missing for that day.
- Added durable, immediately-saved failure logging to both paths, without changing how either path behaves when it succeeds.
- Verified the new logging can never itself cause a failure, and does not touch any trading or order-related code.
- See `docs/daily_patch/2026-09-30_closeout_diagnostic_hardening.md`.

# 2026-09-30 - Closeout Single-Owner Guard

- Closeout execution now enforces single-owner protection across market-status and scheduled fallback triggers. This does not fix the still-unexplained 2026-09-28 hang or 2026-09-29 interruption -- it closes a confirmed, separate gap where both closeout triggers could run at the same time.
- Confirmed the two paths that run end-of-day closeout maintenance -- the live tick-loop and the scheduled backup task -- had no coordination between them, so both could run at the same time and write to the same output files at once.
- Added a single-owner guard so only one of them can actually run closeout at a time; if the other is already running, the second one safely steps aside instead of racing it.
- Reused this system's existing, already-proven single-instance lock mechanism rather than building a new one.
- A run that safely steps aside is not treated as a failure, and does not overwrite anything.
- If a run is interrupted or crashes partway through, the guard does not stay locked forever -- a later attempt can still run normally.
- Every ownership decision is now recorded in the same durable failure log added in the previous closeout diagnostics update.
- Verified with 12 new automated tests covering simultaneous triggers, crash recovery, and later retries, plus the full existing test suite with no new regressions.
- See `docs/daily_patch/2026-09-30_closeout_single_owner_guard.md`.

# 2026-09-30 - Closeout Strict Owner-Identity Lock Fix (CRITICAL)

- A critical correction to the same-day single-owner protection fix: the first version could have let a genuinely still-running closeout lose its own lock to a second trigger just because it took longer than a fixed time limit. This does not fix the still-unexplained 2026-09-28 hang or 2026-09-29 interruption.
- An independent review found that the first version of today's single-owner protection had a real gap: it could treat a closeout that was simply taking a long time the same as one that had actually crashed, and let a second attempt take over while the first was still genuinely running.
- Closeout ownership is now proven by verifying it is the exact same running process, using real operating-system process information, rather than by how much time has passed.
- A running process can no longer lose ownership just because it has been running longer than expected.
- Ownership can still be safely taken over the moment the previous process is confirmed to have actually stopped or been replaced.
- If ownership can't be clearly verified one way or the other, the system now always errs on the side of caution and refuses to proceed, rather than guessing.
- Giving back ownership now requires proving it is the exact same claim that was made originally, so one process can never accidentally cancel another's claim.
- Verified with an expanded set of 25 automated tests covering this exact scenario and related edge cases, plus the full existing test suite with no new regressions.
- This fix has not yet been independently re-verified in a live setting and the real scheduled closeout should not be triggered again until that review is complete.
- See `docs/daily_patch/2026-09-30_closeout_strict_owner_lock_fix.md`.

# 2026-09-30 - Closeout Strict Release-Identity Fail-Closed (Fix2)

- A same-day follow-up to today's strict-ownership lock fix found one remaining unsafe case: if a process could not verify its own identity at the moment it tried to give back ownership, it was allowed to proceed anyway instead of being blocked. This is now blocked. Does not fix the still-unexplained 2026-09-28 hang or 2026-09-29 interruption.
- Found one specific situation where giving back closeout ownership could still succeed without actually proving it was the rightful owner: if the process could not confirm its own identity at that exact moment, the check was written in a way that let it proceed by default instead of stopping it.
- This is now fixed so that giving back ownership always requires positive, confirmed proof on every check -- if any part of that proof cannot be confirmed, ownership is not given back and the safeguard stays in place.
- This only affects the moment ownership is released, not how ownership is claimed or transferred, which were already verified correct.
- Verified with a new targeted automated test for this exact situation, plus the full existing test suite with no new regressions.
- See `docs/daily_patch/2026-09-30_closeout_strict_release_identity_fix2.md`.

# 2026-09-30 - P1.3 Docker Operational Acceptance (In Progress)

- Began formal validation of running this system inside Docker, built from an exact, verified, unmodified snapshot of the code (not today's in-progress work). Initial checks all passed. This does not change which environment is used for real trading, and does not yet close this validation effort -- a full trading-day observation is still pending.
- Confirmed the Docker image was built from an exact, unmodified snapshot of the code, verified file-by-file, so the results below reflect that snapshot and not any of today's in-progress work.
- Confirmed the currently-running live trading process on this machine was left completely untouched throughout -- all Docker testing used a separate, isolated copy of the data, with real order placement turned off.
- The container started up, reported itself healthy within seconds, and correctly took ownership of its own isolated session.
- Confirmed a second container instance correctly refuses to run at the same time as the first, preventing any risk of double execution.
- Confirmed the container's saved data survives being fully recreated, with no data loss.
- Confirmed the system correctly refuses to consider itself ready to trade until its own safety checks are satisfied, rather than assuming it is ready by default.
- Simulated a hard crash and confirmed the container correctly waits out a safety window before taking over again, logging the handover clearly rather than silently overwriting it.
- Confirmed a normal stop signal is handled cleanly and quickly, with ownership properly released every time.
- Measured actual memory cost: the container itself used a small, stable amount of memory. The Docker system as a whole also has its own separate overhead beyond just the container, which was measured and recorded honestly rather than compared only at the container level.
- Two things were deliberately not done yet: testing the real paper-broker connection (skipped for today specifically because the live trading process was actively using the real account connection at the same time) and a full trading-day observation (started today, still running, marked as pending rather than complete).
- No decision has been made about which environment will be used going forward; that decision is intentionally separate and still open.
- See `docs/daily_patch/2026-09-30_p1_3_docker_operational_acceptance.md`.

# 2026-09-30 - P1.3 Docker Post-EOD Final Acceptance Evidence

- Collected the full day's worth of evidence from this morning's Docker validation, all the way through market close and after. Every core mechanic passed cleanly. Two specific items remain before this validation effort can be marked fully complete, and this is reported honestly rather than closed early.
- The isolated Docker container ran continuously from before market open through well after market close today, stayed healthy the entire time, was never restarted, and never ran low on memory.
- Because this container was deliberately isolated from real market data (for safety), it never actually received a real market-close signal, so the end-of-day process never had anything to trigger it during this specific run -- confirmed directly from its own detailed activity log, not assumed from the clock. This is reported plainly as still outstanding, not glossed over.
- Separately ran the actual end-of-day process by itself, using a genuine full-sized copy of today's real activity log (roughly three-quarters of a gigabyte), to specifically measure how much memory that process alone needs under a realistic, full-scale load. It completed in about a minute, using a comfortable amount of memory, well within a safe range -- with the real source data only ever copied, never modified.
- The container was then shut down normally at the end of this check, and it shut down quickly and cleanly, giving back its claim on the isolated session as expected every time this has been tested today.
- Only two things are still outstanding before this validation can be marked fully done: getting a genuine end-of-day trigger to fire (not just simulating it separately), and testing the real paper-account connection specifically through this Docker setup -- the second one is still waiting for a safe window when it will not run alongside the live trading process using the same account connection at the same time.
- No decision has been made about which environment will be used going forward; that decision remains intentionally separate and still open.
- See `docs/daily_patch/2026-09-30_p1_3_docker_post_eod_final_acceptance.md`.

# 2026-09-30 - P1.3 Integrated EOD Cascade Attempt (Still Pending)

- Attempted to prove the end-of-day process using only the system's own existing, already-supported input mechanism (not a new shortcut built for this test). The attempt did not produce confirming evidence, so this is reported honestly as still open rather than closed. The real paper-account connection check also remains open, for the same safety reason as before.
- Before building anything new, first checked whether the system already has a supported way to feed it a realistic market-close signal -- and found one already built in and already used by the real system for this exact purpose.
- Used that existing, unmodified mechanism (not a new one written for this test) to feed in a realistic market-close signal, in an isolated environment with real order placement turned off.
- After feeding in the signal and waiting through several of its normal check cycles, no evidence appeared that the end-of-day sequence actually ran. Confirmed separately that the underlying end-of-day process itself works fine on its own -- the issue is specifically about whether the live signal actually reaches and triggers it under these exact conditions.
- This is reported plainly as unresolved rather than force-fixed or worked around: no new system behavior was written just to make this pass artificially, per the standing rule for this kind of check.
- The container itself stayed completely healthy throughout this attempt -- no crash, no restart, no resource issue. Only the trigger itself could not be confirmed.
- The real paper-account connection check also remains untested today, for the same reason as the prior update: the live trading process was still actively using that same connection throughout, and testing it at the same time was judged unsafe.
- Both of these being open is exactly why this validation effort is still not being marked complete -- reporting it honestly as open is the correct outcome here, not a setback.
- See `docs/daily_patch/2026-09-30_p1_3_eod_cascade_attempt_and_paper_pending.md`.

# 2026-09-30 - P1.2 Daily UEF Automation Integration

- The prepared daily task invokes only the existing canonical UEF entry point after closeout.
- Clock time is not readiness: existing source-freshness contracts still reject stale or incomplete input.
- Each verified COMPLETE generation is indexed once for P1.2 observation; the registry is derived metadata, while COMPLETE manifests and verified pointers remain authoritative.
- The first registered same-day run published a valid 2026-09-30 COMPLETE authority and one observation.
- The required second-run idempotency check failed: it created a different COMPLETE generation and advanced current/latest before the registry rejected the conflicting already-observed-day authority. P1.2 closure is blocked pending a separately scoped idempotency repair.
- No historical backfill, frozen UEF change, trading change, or Docker change was introduced.
- See `docs/daily_patch/2026-09-30_p1_2_daily_automation_integration.md`.

# 2026-09-30 - P1.3 EOD Cascade: Confirmed Reachable (Correction)

- A closer read-only investigation found that the end-of-day trigger mechanism reported as unconfirmed earlier today actually does work correctly -- the earlier check was looking in the wrong place in the saved data, not a real gap in the system. This is now proven directly, including that a duplicate signal correctly does not trigger a second run.
- Traced the exact code path a real market-close signal takes, step by step, from the program's entry point through to the actual end-of-day report generation, confirming every step is reachable and none of it is blocked by time-of-day.
- Re-examined the exact same data produced by the earlier attempt and found the proof was there all along -- it had simply been checked in the wrong location within the saved file.
- Directly confirmed the full chain: a market-close signal is accepted, recorded so it won't be processed twice, the end-of-day process runs, and a complete set of daily report files is produced.
- Separately proved duplicate protection works: sending a second, equivalent close signal was correctly recognized as already handled and did not produce a second run or a second set of reports.
- This required no code changes and no new build -- it is a correction to how the earlier result was read, not a fix to the system itself.
- All previously passed results remain valid and unaffected by this correction.
- See `docs/daily_patch/2026-09-30_p1_3_eod_cascade_confirmed_reachable_correction.md`.

# 2026-09-30 - P1.3 Final Closure Attempt: Paper Connectivity + Resource Benchmark

- Successfully connected the exact accepted Docker build to the real practice-account broker sandbox and confirmed both login and account-balance lookup work correctly. A third check -- looking up open orders -- was blocked, but for a clear, understood reason: an existing safety switch treats that specific lookup the same as placing an order, so it stays off intentionally while that safety switch is off. Because not all three checks passed, this validation effort remains open rather than closed. Separately, a full three-way comparison of running the trading system on this computer directly versus inside Docker is now complete, with real measured numbers.
- Gracefully stopped and later safely restarted the live trading process twice today, as explicitly authorized, to make room for these checks -- confirmed healthy and running normally throughout and at the end.
- Confirmed real login to the broker's own official practice-account sandbox succeeds using the accepted build, with no secrets ever shown or saved anywhere they shouldn't be.
- Confirmed a real account-balance lookup against the practice sandbox succeeds and returns valid data.
- The open-orders lookup was blocked -- traced this precisely: every existing way this system has of checking open orders shares the same safety switch as actually placing an order, and that switch is intentionally left off for this kind of check. This is a specific, understood gap, not an unexplained failure, and is reported openly rather than worked around.
- No order of any kind was placed or even attempted at any point.
- Completed a fair, three-way, real-world comparison: running everything directly on this computer, running the trading process directly with just the monitoring dashboard in Docker, and running the trading process itself inside Docker alongside the dashboard.
- Found that having the monitoring dashboard available at all has a real, roughly fixed cost on this computer regardless of where the trading process itself runs -- and that cost is the same whether the trading process is inside Docker or not.
- Found that the Docker version of the trading process itself is actually lighter than the version running directly on this computer.
- This is a real measurement, not a preference -- and it does not by itself decide which setup should be used going forward; that remains a separate, deliberate decision for later.
- Left the live trading process running normally with the monitoring dashboard available, matching how things were set up before this comparison began, with nothing extra left running afterward.
- See `docs/daily_patch/2026-09-30_p1_3_final_closure_paper_and_resource_benchmark.md`.

# 2026-09-30 - P1.3 CLOSED -- Broker Read/Write Gate Fix

- Found and fixed the exact, narrow reason the one remaining broker check was blocked, verified the fix against the real practice-account sandbox, and re-confirmed that placing a real order is still fully blocked. With that, every required Docker acceptance check now passes and this validation effort is complete.
- Traced the one remaining blocked check to its precise cause: a safety switch meant only for actually placing orders was, by mistake, also blocking simply looking things up.
- Made the smallest possible correction so that looking things up (logging in, checking account balance, checking open orders) works independently from the switch that controls actually placing orders -- reusing an existing, already-trusted way this system already tells the two apart, rather than inventing a new one.
- Re-verified, live, against the real practice-account sandbox with real order placement still turned off: logging in works, checking account balance works, and checking open orders now also works correctly -- with a valid, genuine "nothing pending" result, not a blocked error.
- Immediately re-confirmed, in that same live session, that actually placing a real buy or sell order is still completely blocked, exactly as intended -- proving the fix only affected lookups, not real order-placement safety.
- Because this involved an actual code change, a new officially-accepted build was created and independently re-verified byte-for-byte against its own source, separate from today's unrelated in-progress work elsewhere in the project.
- Re-ran only the specific checks this small change could plausibly affect, rather than repeating everything already proven earlier -- all of them passed, and nothing else needed to be redone.
- No order of any kind was placed at any point. The live trading process itself was left completely untouched throughout this step.
- With this fix, every required check for this Docker validation effort now passes, and it is being marked complete.
- Which environment to actually run going forward remains a separate, deliberate decision for later -- this only confirms Docker works correctly and safely; it does not choose it.
- See `docs/daily_patch/2026-09-30_p1_3_closed_read_write_gate_fix.md`.

# 2026-10-01 - Storage and Temporary-Artifact Hygiene

- Added a permanent project rule requiring temporary worktrees, test scratch, debugging artifacts, and temporary build
  resources to be cleaned after their results are safely preserved.
- Worktrees must be reused where compatible, limited to one temporary worktree per task, and removed after commit
  preservation is verified. Branches may remain for provenance.
- Successful tests leave no repo-local pytest scratch; failed-run evidence is bounded rather than accumulated.
- Docker storage cleanup is evidence-aware: inspect use, remove only proven-unused temporary resources, retain
  operational, rollback, and frozen acceptance artifacts, and never broadly prune without explicit approval.
- Canonical market, broker, runtime, UEF, registry, report, and audit evidence is explicitly protected.
- See `docs/daily_patch/2026-10-01_storage_temp_artifact_hygiene.md`.

# 2026-10-01 - Host Runtime Pivot and Closeout Exactly-Once Completion

- The trading system's production runtime is moving back to running directly on the Host machine, not inside Docker. This is a practical choice about day-to-day reliability, not a sign Docker could not technically do the job -- Docker already passed its earlier acceptance checks, and that validation stands.
- Docker production adoption is being deferred, not adopted and not declared broken -- purely an operational-complexity decision for a single-machine setup.
- A second real Docker restart failure happened today with the exact same cause already found and recorded earlier -- kept on record as further evidence, not treated as a new problem. The underlying Docker restart issue remains openly recorded as backlog and is explicitly not fixed by this change.
- Today's real Docker production-day incident, and the earlier one, are both kept on record as history -- neither is erased or rewritten.
- The end-of-day closeout process now remembers, durably, once it has fully and successfully finished for a given day -- so if it gets triggered again afterward (from either of the two ways it can start), it correctly recognizes the day is already done instead of redoing the entire reporting battery a second time.
- Specifically confirmed: retrying an already-completed day reports it as already done rather than redoing the work; the scheduled fallback reports the same already-done result after a successful run from the other path; and a genuinely interrupted attempt leaves no completion record, so a later retry is still allowed through.
- The daily evaluation script now keeps its own simple start/end record -- who ran it, when, and how it ended -- separate from the Windows Scheduler's own history, so a crash or a hang leaves a trace behind.
- Added a simple read-only status check an operator can run to see, for any given day, whether the daily evaluation was scheduled-and-ran, never started, started-and-failed, or started-and-completed -- rather than only trusting that the schedule itself is turned on.
- The daily evaluation task's battery-power restriction was removed today, applied and verified.
- The daily evaluation task's logon type was changed today so it can run unattended without anyone logged in, applied and verified against the task's own configuration. A live end-to-end unattended trigger was deliberately not performed, to avoid creating a second, duplicate evaluation record for a day that already has a valid, complete one -- the configuration-level confirmation is recorded as today's validation evidence for this change.
- Today's daily evaluation output was checked and confirmed genuine -- the evaluation itself, once it ran at 17:42 KST, completed correctly.
- However, today's run did not meet its scheduled 16:45 KST time -- it started about 57 minutes late. This is recorded plainly as a missed on-time run, not treated as a success just because the evaluation itself eventually completed correctly.
- The exact cause of the late start is not fully proven. The unattended-incapable logon setting is a plausible, consistent contributing factor, but this has not been confirmed as the sole or definitive cause.
- The next real test of today's scheduling correction is the regular 2026-10-02 16:45 KST run -- its outcome is not yet known and is not being assumed in advance.
- Finished cleaning up the temporary work areas left over from the earlier Docker testing, and removed the Docker test images from that testing that are no longer needed, while leaving today's real (if now stopped) production Docker container and its image untouched for review.
- A permanent project rule for cleaning up temporary work areas, test leftovers, and unused Docker build resources was added today, separately from this runtime change.
- Also found and fixed a real gap: the live daily-evaluation schedule was actually running from code that did not yet contain an already-approved fix for safely handling a day that gets re-evaluated more than once (making repeated runs produce the exact same result, and never silently redoing work or creating conflicting records for a day already finished correctly). That approved fix has now been brought into the same branch the live schedule actually runs from, verified with 29 passing tests plus a broader 65-test regression sweep.
- A follow-up check on 2026-10-01's result initially looked like the underlying input data had changed after the fact, which would have been serious. It was traced precisely instead to how the check itself was run (a path-formatting difference, not real data change): the same underlying data, checked the same way the real daily task checks it, produces the exact same result as the original. No actual upstream data drift occurred, repeated runs remain consistent, and 2026-10-01's result stands as valid. The narrow path-formatting detail itself is noted for a later, separate, deliberate fix -- not changed today.
- No change to UEF core logic, Step5C, Step5D, or trading/strategy behavior in any of today's work.
- See `docs/daily_patch/2026-10-01_host_runtime_pivot_final_ops_cleanup.md` and `docs/daily_patch/2026-10-01_p1_2_idempotency_determinism_integration.md`.

# 2026-10-02 - P1.3 R1/R2 Docker Restart Storm Fixes

- Two separate safety checks were each making a restarted Docker trading runtime give up in under a second, which used up its restart allowance and left it stopped. Both were corrected without weakening the rule that a live owner is never displaced.
- The first check identified the previous owner only by a process number. A restarted container always gets the same small number, so it mistook its own dead predecessor for a live owner. It now also compares the exact start time of the process, so a dead or reused number is recognised and a genuinely live owner is still never taken over.
- The second check refused a restart while the previous owner's 30-second claim was still valid, and gave up instantly. It now waits, for no longer than that claim's own remaining time plus a few seconds, and then takes over only once the claim has legitimately expired. If the claim is somehow still valid at the end of the wait it stops safely instead of forcing its way in.
- The shared lock file is now written in one step so a status check can no longer read a half-written file and wrongly report a failure.
- Today's real Host run showed the strict check protecting the system as designed: a scheduled backup closeout that started mid-way through a 55-minute closeout was turned away rather than allowed to take over, and a later duplicate was skipped as already complete.
- Docker is still not the live trading runtime. The Host runtime traded and closed out normally today and was not touched.
- See `docs/daily_patch/2026-10-02_p1_3_r1_r4_docker_restart_safety.md`.

# 2026-10-02 - P1.3 R3 Ownership Heartbeat

- The runtime's claim of ownership expires after 30 seconds but was only renewed between work cycles. Real cycles often took longer, and today's end-of-day closeout took about 55 minutes, so a perfectly healthy owner could look abandoned. A background heartbeat now renews the same claim independently of how long the work takes.
- The heartbeat renews the same existing ownership claim, not a new one, and starts only after ownership is actually obtained.
- It renews roughly every third of the claim's length, derived from the claim's own setting rather than a separate number.
- It can only renew the exact claim this process holds. If another runtime has taken over, the renewal fails, the heartbeat stops for good and the process refuses to start any further work and exits.
- If the claim cannot be renewed for a full claim period (for example the store is unreachable) it also stops work rather than assuming it is still the owner.
- A crash stops the heartbeat with the process, so the claim lapses naturally and the bounded wait and takeover from the previous fix apply unchanged.
- A step already in progress is never interrupted; only the next one is prevented.
- See `docs/daily_patch/2026-10-02_p1_3_r1_r4_docker_restart_safety.md`.

# 2026-10-02 - P1.3 R4 Runtime Mode Switch

- The weekday 09:00 and watchdog Windows tasks start both the live trading process and the data collectors that feed the daily evaluation, so they cannot simply be switched off when trading moves to Docker. A single setting, TRADING_RUNTIME_MODE, now lets those tasks keep running the collectors while declining to start live trading on the host.
- host (the default) behaves exactly as before.
- docker makes the host skip only the live-trading launch, with the logged reason HOST_LIVE_START_SKIPPED_CANONICAL_RUNTIME_DOCKER. The Q10, Q11 and Q12 collectors, the opportunity engine and the macro collectors keep running, and the watchdog neither starts nor tries to recover host live trading.
- Any other value also skips the host launch, so a typo can never accidentally allow a second live runtime.
- Rolling back means setting the mode back to host.
- The setting is configuration only: it does not inspect Docker or process numbers, and it is not an ownership authority. The ownership claim remains the only thing that decides who may trade.
- The setting is not turned on yet, so tomorrow's tasks still behave as today until the cutover.
- See `docs/daily_patch/2026-10-02_p1_3_r1_r4_docker_restart_safety.md`.

# 2026-10-02 - P1.3 R5 Healthcheck, Shutdown and Recovery Evidence

- Docker's health check used to judge a runtime by the lock file's heartbeat, which is only updated between work cycles, so long legitimate cycles made a healthy runtime look unhealthy. It now follows the same ownership claim the heartbeat renews, and lock-file information is only a diagnostic. A stop request during a restart wait is also now handled safely, and a full crash-and-recovery sequence was demonstrated in an isolated Docker environment.
- The health check is strictly read-only: it opens the ownership store in read-only mode and never acquires, renews, releases or changes anything.
- It reports an explicit reason: owner, generation and remaining claim time when healthy; no valid owner, another runtime owning, or an identity mismatch when not.
- A stop signal received while a restarted runtime is waiting for the old claim now makes it exit cleanly without ever taking ownership. Before this, the signal handler was installed too late and the process was simply killed.
- In an isolated Docker run with the real recovery logic and a mock broker: after a hard crash and a quick restart the process stayed alive and waited, took over only when the old claim expired, and showed recovery-required until the mock broker was healthy, then went fresh and green. A second restart repeated this deterministically, and Docker's restart counter stayed at zero.
- No orders were placed, the real production state and the running host process were not touched, and nothing about trading, the daily evaluation, or the order-ownership checks changed.
- Not yet done: the production-state after-hours Docker test against the real paper broker, and the cutover itself. The host remains the live runtime.
- See `docs/daily_patch/2026-10-02_p1_3_r5_healthcheck_shutdown_recovery_matrix.md`.

# 2026-10-02 - P1.3 Production Docker Cutover

- The live trading runtime moved from the Windows host process to a single Docker container after the close. The host runtime was stopped, the container took over the ownership claim, read the paper broker successfully without placing orders, and survived one deliberate crash-and-restart exactly as designed.
- Before the move the account was flat (no positions, no open orders, no pending order claims, no orphans) and the day's closeout was complete.
- The runtime-mode setting was switched to docker: the scheduled tasks stay in place but no longer start the host live loop, while the market-data collectors that feed the daily evaluation are still started by the same code path (proven with a dry run that records launches instead of executing them).
- Exactly one container, trading-agent-live, runs the exact-SHA image; the previous failed container was kept under an incident name. It restarts through Docker's own restart policy, and Docker Desktop's existing logon autostart is the only startup authority.
- Auth, account, open-order and market-data reads against the paper broker passed from inside the container; no order was submitted.
- One controlled restart: the new process was recognised as a new process despite reusing process number 1, waited about 23 seconds for the old claim to expire, took over as generation 3, stayed healthy and never entered a restart loop. A triggered watchdog run did not bring the host runtime back.
- Not yet proven: fresh green execution readiness and clearing of the post-takeover recovery flag, because market hours are hard-coded and every after-hours cycle is skipped. This is the first-session validation item. The boot simulation was static (no reboot or Docker restart).
- Rollback is one setting: runtime mode back to host, stop the container, let the claim expire, start the host.
- See `docs/daily_patch/2026-10-02_p1_3_production_docker_cutover.md`.

# 2026-10-03 - Agentra Root Migration Finalization

- Finalized the one remaining privileged Windows Scheduler migration item after moving the repository root to `C:\Agentra`.
- Re-registered `TradingAgent-DailyUefEvaluation` from an Administrator context while preserving its S4U principal, Limited RunLevel, triggers, schedule, settings, and disabled state.
- All 13 registered TradingAgent tasks now reference `C:\Agentra`; active Scheduler references to `C:\Trading_Agent_System` are zero, and all tasks remain disabled for weekend maintenance.
- Docker configuration remains pinned to the `trading-agent-observability` Compose identity with bind mounts under `C:/Agentra`; Docker and the live trading runtime were not restarted.
- The rebuilt venv passed the dependency drift audit without re-adding historical or optional packages; deterministic, UEF/replay, execution-authority, and production-write-leakage validations remained green.
- The migration was committed and pushed on `codex/observability-20260824`. The temporary compatibility junction `C:\Trading_Agent_System -> C:\Agentra` remains during soak; accumulated data and runtime state were not relocated.
- See `docs/daily_patch/2026-10-03_agentra_root_migration.md`.

# 2026-10-06 - yfinance Dependency Restore and Data-Source Status Integrity

- Root cause of the 2026-10-06 Q12 08:55 `MISSING` (exit 2) and the Q10 08:50 all-`UNAVAILABLE` snapshot: `yfinance` was absent from `requirements.txt` and from the venv recreated on 2026-10-03, and every call site swallowed the import failure.
- `requirements.txt` now declares `yfinance==1.7.0`; installed into `C:\Agentra\venv` via the canonical requirements path (`pip check` clean). A throwaway Python 3.12 dry-run resolves the same dependency set the Docker build would. The running `trading-agent-live` image predates this and lacks `yfinance`; it was not rebuilt or restarted during market hours - rebuild after the close.
- Missing dependency is now explicit: new `DataSourceDependencyError` (`dependency_missing:yfinance`). Q12 capture records `DEPENDENCY_MISSING` (no retries, exit 3); Q10 and the preopen macro snapshot raise and their scripts exit 3 (opening-macro slots record `CAPTURE_FAILED` with the explicit error). Loop-adjacent best-effort paths still degrade but log an explicit error.
- Q10 status integrity: an all-`UNAVAILABLE` lead-market snapshot is persisted unchanged but reported `DATA_UNAVAILABLE` (reason `all_lead_market_observations_unavailable`) instead of `CAPTURED`; partial data stays `CAPTURED`. Scoring/signal semantics are unchanged; consumers that require `CAPTURED` now treat it as not captured.
- Today's expired Q10/Q12 artifacts were not rewritten or replayed (no backfill). Read-only dry loads with the restored environment: Q10 12/13 available, Q12 BTC/USD and BTC/KRW eligible for 08:55, global-sentiment inputs populated; yfinance news returned no items (upstream/unclear).
- Regression tests: `tests/test_yfinance_dependency_integrity.py` (27 tests); related Q10/Q12/macro/sentiment/news/hydration suites remain green.
- See `docs/daily_patch/2026-10-06_yfinance_dependency_restore.md`.

# 2026-10-06 - R6 Immutable Execution Readiness Evidence

- Problem: `execution_readiness.json` is only the latest mutable snapshot, so the readiness value used by the 2026-10-06 09:02 BUY and 09:05 SELL could not be proven afterwards (Codex verdict `INSUFFICIENT_EVIDENCE`).
- New append-only evidence: `libs/execution/readiness_evidence.py` writes one JSON line per BUY/SELL decision to `data/logs/execution_readiness_evidence/<day>.jsonl` (deterministic `record_id`, per-intent `intent_sequence`, `record_hash`, duplicate detection, never rewritten). Fields include intent/run ids, runtime instance id, ownership generation, `recovery_required`, portfolio and open-order reconciliation, readiness verdict/reasons/computed-at, guard verdict, `broker_submission_allowed`, execution mode, symbol/side/quantity and entry/exit reason correlation.
- Order: readiness evaluated -> guard verdict -> evidence persisted -> only then intent admission and broker submission. Readiness-guard blocks are recorded as well.
- Fail-closed: if the evidence cannot be persisted for a real-mode BUY/SELL, nothing is admitted or submitted (`readiness_evidence_write_failed`). A failed record on an already-blocked order leaves the existing block reason unchanged.
- Evidence only: never read back by readiness, execution, ownership, Step5C or Step5D (pinned by tests). Scope: BUY/SELL, real execution mode, `execute_from_packet`. No change to strategy, UEF, Step5C/5D, R1-R5 or broker routing.
- Prospective only: the 2026-10-06 09:02 BUY and 09:05 SELL stay `READINESS_AT_EXECUTION = UNKNOWN` (`HISTORICAL_OBSERVABILITY_GAP`); nothing is fabricated.
- Tests: `tests/test_r6_readiness_evidence.py` (30). The 749-test execution/readiness/Step5/ownership regression set passes; 8 `test_step5b_fix4` tests fail identically on the pre-R6 baseline and were not touched.
- The running Docker image does not contain yfinance or R6 and was not rebuilt during market hours; rebuild and a single controlled restart follow the close. R6 live acceptance is prospective (next real/mock order).
- See `docs/daily_patch/2026-10-06_r6_immutable_readiness_evidence.md`.

# 2026-10-06 - R6.1 Mutation-Path Scope Fix and Atomic Evidence Append

- Codex verdict `R6_SCOPE_FIX_REQUIRED`: three other `execute_owned_order` callers could reach the broker without R6 evidence, and evidence append was scan-then-append without interprocess locking.
- Call graph traced: `execute_from_packet` BUY/SELL (covered), its two CANCEL calls (not exposure), legacy `execute_order` node (now covered by the shared helper + existing readiness guard), `libs/skills/runner.py` (blocked without an evidence reference), and the approval service / ToolFacade / ExecutorAgent flow (covered when a runtime `readiness_state` is supplied, otherwise real-mode BUY/SELL is blocked before admission).
- One shared pre-admission helper records the existing readiness/guard values BEFORE admission/Step5C/broker submit; the order is not moved after admission.
- Final choke point: `execute_owned_order` verifies the evidence reference against durable storage for real-mode BUY/SELL (matching intent/side/symbol/quantity, hash-valid, ALLOW, fresh) and otherwise fails closed (`readiness_evidence_required` / `readiness_evidence_invalid`) before any Step5C claim and with no broker call. No new authority; CANCEL/MODIFY and mock mode excluded.
- Atomic append: per-day interprocess lock (`O_EXCL` lock file, bounded wait) around read/dedup/sequence/append/fsync/read-back; lock timeout fails closed. Same intent + same attempt -> same `record_id` and a deterministic duplicate answer; later attempt -> next `intent_sequence`; torn/partial/tampered lines are never valid evidence.
- Operator note: real-mode BUY/SELL approvals through `approval_cli` now need runtime readiness context or a valid evidence reference. Strategy, readiness, Step5C/5D, UEF and broker routing are unchanged; no 2026-10-06 evidence is fabricated.
- Tests: `tests/test_r61_scope_fix.py` (33). Not deployed; Docker untouched pending independent audit and the after-hours rebuild.
- See `docs/daily_patch/2026-10-06_r6_1_scope_fix.md`.

# 2026-10-06 - R6.2 Evidence Is Proof, Not a Capability Token; Strict Lock Identity

- Codex verdict `R6_1_CORRECTION_REQUIRED`: (1) an R6 evidence reference stayed usable for 600 s and acted like an authorization token; (2) the evidence storage lock was broken on file age alone.
- **R6 evidence is not an authorization token.** The 600-second authorization rule is removed; timestamps are audit data only.
- Evidence is bound to `execution_attempt_id` + runtime instance + ownership generation, and that attempt id flows readiness/guard -> evidence -> admission -> `execute_owned_order` -> broker submit on every mutation path.
- `execute_owned_order` revalidates the CURRENT safety state (canonical owner row with live lease, readiness ready, recovery false, same instance/generation); stale readiness/generation/instance evidence fails closed with no Step5C claim and no broker call. No strategy or readiness recomputation.
- Duplicate concurrent callers for one attempt share one immutable record and Step5C still yields exactly one broker mutation; a later attempt needs new evidence.
- Evidence storage lock: strict live-owner identity (pid + process start identity + owner token + host); live owners are never broken by age, dead or PID-reused owners are reclaimed, unverifiable or malformed locks and foreign-namespace locks fail closed, release is exact-owner only. The mtime-only stale break is removed. Storage serialisation only - not trading ownership.
- AST caller guard now covers direct, imported-alias, module-qualified and simple-alias calls. Documented limitation: with the readiness gate disabled by the operator and no readiness context there is nothing to revalidate.
- No strategy, readiness, Step5C/5D, UEF or broker-routing change; no 2026-10-06 evidence fabricated; not deployed (Docker untouched).
- Tests: `tests/test_r62_attempt_and_lock.py` (30) plus updated R6/R6.1 suites. See `docs/daily_patch/2026-10-06_r6_2_attempt_binding_and_lock_identity.md`.

# 2026-10-06 - Docker Live-Open Observation and Daily UEF Freshness Incident

- The retained daily record confirms one canonical Docker runtime at generation 5. The Host live-launch path recorded `HOST_LIVE_START_SKIPPED_CANONICAL_RUNTIME_DOCKER` while collectors remained active. The report records a BUY and matching SELL for `217590` quantity 41; broker reconciliation matched both local records to the broker by order number.
- The contemporaneous Docker observation recorded `RestartCount=0` and no OOM kill for that generation. This is an observation only, not a new Docker acceptance, rebuild, deployment, or claim that the running image carries post-open changes.
- The earlier Docker restart-storm incident and its R1/R2 corrective work remain historical records in the 2026-10-01/02 notes. No new recurrence or new fix is claimed here.
- `TradingAgent-DailyUefEvaluation` started from `C:\Agentra` at 16:45:02 KST (SHA `a38bf4e9f5f6f76eaee37659c45c7c49705fcef2`) and ended at 16:45:03 KST with exit code 1, no canonical generation, and an explicit registered-freshness failure. It failed closed rather than materializing a canonical board that could mix a fresh through-day label with stale or unreviewed content.
- The individual stale or unknown closeout-written source is not identified by the retained lifecycle event, so source-level RCA remains open. No source artifact, pointer, registry, UEF framework/freeze semantic, or historical evidence was changed. R6/R6.1/R6.2 deployment and live acceptance are not asserted.
- See `docs/daily_patch/2026-10-06_docker_live_open_and_daily_uef_freshness_incident.md`.

# 2026-10-07 - P1.3 Closeout OOM Fix, 2 GiB Limit and After-Hours Production Deployment

- The 10-06 / 10-07 Docker restart storms (RestartCount 23 then 43) were proven to be kernel cgroup OOM kills of PID 1 during the in-process closeout at the 1 GiB limit (the post-restart `OOMKilled=false` read was not evidence).
- Closeout memory use is now bounded (streamed q9 windows, projected shadow payloads, streamed visibility rows, per-symbol rank1 loading, lens folded day by day); outputs were identical to the previous implementation on real 10-01/02/06/07 data. The full 20-day rolling Q9 window was not compared against the old path.
- Closeout-only cross-namespace lock guard: a Host closeout and the Docker closeout no longer reclaim each other's lock by PID; heartbeat decides, and the Host fallback still works when a Docker owner stops refreshing. The m13 trading lock is unchanged.
- 1 GiB was rejected (isolated full closeout OOMed in the Q9 stage); 2 GiB passed (exit 0, 1381 s, one durable SUCCESS, no OOM). Production limit is now 2 GiB (`--memory 2g --memory-swap 3g`).
- After-hours deployment of image `trading-agent-20261007:f4fa335` (application SHA `f4fa33521c1aeed30813a2799824eed5e12a58d6`, includes R6.2 and yfinance): healthy, RestartCount 0, no OOM, Python PID 1, one canonical Docker runtime, Host live runtime 0, today's closeout SUCCESS visible with no second SUCCESS, broker read path PASS. Ownership generation reset to 1 by design (clean lease release); the old container is kept stopped as the rollback.
- Not claimed: FULL P1.3 freeze, P1.2 scheduled-validation PASS, R6 live acceptance, next-day Docker closeout PASS. Status: `PRODUCTION_DEPLOYED_PENDING_LIVE_ACCEPTANCE`; P1.2 `OBSERVING`.
- See `docs/daily_patch/2026-10-07_p1_3_closeout_memory_fix_and_production_deployment.md`.

# 2026-10-08 - P1.2 Closed and P1.3 Full Docker Frozen

- Historical truth kept: scheduled Daily UEF FAILED 2026-10-06 and 2026-10-07; the 2026-10-07 manual recovery PASSED (chain proof only); the 2026-10-08 scheduled run PASSED.
- Production `trading-agent-20261007:f4fa335` (SHA `f4fa33521c1aeed30813a2799824eed5e12a58d6`), 2 GiB: RestartCount 0, no OOM, one canonical Docker runtime, Host live runtimes 0, ownership generation 1 stable, 77/77 watchdog runs `HOST_LIVE_START_SKIPPED_CANONICAL_RUNTIME_DOCKER`.
- Fresh readiness at 09:00:09 and 15:29:53 (ready, recovery false, reconciled, orphans 0). Two real orders (BUY/SELL 155 x 002720) carried hash-verified R6 evidence recorded before the Step5C CAS and broker submit; ended flat with no unresolved or duplicate execution.
- Docker closeout 15:30:08-15:51:50 KST (21 m 42 s), 17/17 steps ok, one durable SUCCESS; the 16:00 Host fallback saw it complete. Process peak RSS 1066-1081 MiB under the 2 GiB limit; oom/oom_kill 0.
- Scheduled 16:45 Daily UEF: exit 0, one COMPLETE `UEF9RUN_559c27f2d0d1f62b`; UEF-7 14/14, UEF-8 91 pairs (0 COMPARABLE / 7 CONDITIONAL / 84 NOT_COMPARABLE), UEF-9 VALID; pointers and registry aligned; replay reproduced the run ids; freeze 11/11 MATCH.
- Status: **P1.2 CLOSED; P1.3 FULL DOCKER FROZEN.** Backlog (non-blocking): Q9 compute-once/share, 20-day old-path equivalence NOT_AVAILABLE, monitor-exit-guard environment contamination. Next: P1.5 prework.
- See `docs/daily_patch/2026-10-08_p1_2_p1_3_final_closure.md`.

# 2026-10-07 - P1.5/P1.6 Refactor Design and Documentation Refactor Start

- Created the design-only `design/p1.5-p1.6-modernization` branch from baseline `b67934a5baa95f4d329ccf345c14ed591a126a0f`.
- Defined P1.5 as behavior-preserving agent-boundary restoration: explicit input/output contracts, standalone-callable agent cores, naming cleanup, test architecture cleanup, and unchanged production topology.
- Defined P1.6 as a post-P1.5 orchestration benchmark of the current custom runtime, LangGraph 1.x, and pydantic-graph. No orchestration framework is adopted during P1.5.
- LLM decision roles remain Strategist + Reporter only. Scanner, Monitor, Supervisor, Executor, and Commander routing remain deterministic unless separately approved in a future feature phase.
- Started documentation refactoring using an inventory-first, link-safe migration policy. Historical milestone and incident records are preserved as audit assets rather than rewritten.
- Clarified patch-note authority: `docs/daily_patch/` is the detailed technical audit history; this folder's `patch_notes.json` and `patch_notes.md` are the UI/API-facing canonical changelog pair.
- No runtime, strategy, broker, execution-authority, or trading-semantic change is included.
- See `docs/refactor/p1_5_p1_6_master_plan.md`, `docs/refactor/p1_5_refactor_constitution.md`, `docs/refactor/p1_5_documentation_refactor_plan.md`, and `docs/refactor/documentation_inventory.md`.

# 2026-10-07 - P1.5 Strategist Deep Design v0.1

- Mapped all 156 top-level functions in `graphs/nodes/strategist_node.py` to proposed P1.5 owners while keeping `strategist_node` as the stable runtime façade.
- Preserved existing semantic owners: `StrategistOutput`, Monitor policy normalization, Scanner bias, horizon policy, explanation and artifact contracts.
- The existing `StrategyInput` remains a per-symbol tactical contract; the new high-level boundary will use `StrategistAgentInput` / `StrategistAgentResult`.
- Recorded direct private imports and node-module monkeypatch targets as compatibility seams.
- Defined S1 as a mechanical LLM extraction only; no prompt, call-count, retry/fallback, strategy, candidate, topology or execution change.
- Defined the explicit Agent-input groups and the current compatibility state-patch surface.
- Runtime implementation remains gated on the frozen P1.2/P1.3 baseline.
- See `docs/refactor/p1_5_strategist_implementation_packet_v0_1.md`.

# 2026-10-07 - P1.5 Strategist Design Complete

- Finalized the P1.5 Strategist modular-refactor design without changing runtime behavior.
- The current 8,878-line Strategist node was mapped into context, LLM, policy, output, observability, service and state-adapter responsibilities.
- New Agent-level contract names are frozen as `StrategistAgentInput` and `StrategistAgentResult`; the existing per-symbol `StrategyInput` is not repurposed.
- Existing `StrategistOutput` remains the canonical normalized compatibility output during P1.5.
- The current 66-key state-write surface will be preserved through a dedicated compatibility state adapter.
- Implementation sequence is frozen as S1 LLM extraction -> S2 deterministic policy/output -> S3 context/IO -> S4 Agent contract/service/state adapter -> S5 tests/wrapper cleanup.
- Implementation remains gated by P1.2/P1.3 freeze and baseline SHA/tag capture.
- Authority: `docs/refactor/p1_5_strategist_implementation_packet_v1_0.md`.

# 2026-10-07 - P1.5 Strategist Design Freeze

- Frozen the Strategist P1.5 implementation design; no runtime code changed.
- Current source inventory: `graphs/nodes/strategist_node.py` 8,879 lines, 156 top-level functions, 69 direct shared-state write keys.
- New Agent-level contract names are `StrategistAgentInput` and `StrategistAgentResult`; the existing tactical `StrategyInput` is not repurposed.
- Existing `StrategistOutput` remains the compatibility authority.
- Implementation order is S1 LLM extraction → S2 deterministic policy/output → S3 context/IO → S4 service/contract/state adapter → S5 tests/wrappers.
- Existing private imports and monkeypatch seams remain during staged migration.
- Runtime implementation remains blocked until the P1.2/P1.3 frozen-baseline gate.
- See `docs/refactor/p1_5_strategist_implementation_packet_v1_0.md`.

# 2026-10-07 - P1.5 Reporting Design Complete

- Completed the P1.5.1/P1.5.2 Reporting structural design.
- Mapped the three giant Reporting modules totaling 18,743 LOC and the responsibility-specific helper modules already extracted from them.
- Proved a roughly 1,100-LOC unreachable legacy tail after `render_trade_summary_markdown_with_evaluation()` delegates and returns.
- Identified the duplicate/shadowed `_playbook_label` definition in `trade_report_markdown_clean.py`.
- Froze a staged implementation sequence: dead-code cleanup first, then AI report façade, Markdown façade, and trade-story façade decomposition.
- Existing report schemas, truth precedence, LLM behavior, artifact paths, provenance, and public/test seams remain unchanged.
- Design authority: `docs/refactor/p1_5_reporting_implementation_packet_v1_0.md`.

# 2026-10-07 - P1.5.3 Operator UI / Operator Brief Design Complete

- Completed the P1.5.3 Operator UI / Operator Brief structural design without changing runtime behavior.
- Mapped the approximately 6,872-line apps/operator_ui/data_access_core.py and identified the remaining mixed responsibilities: canonical Brief truth projection, deterministic sections/fallback, compact LLM input, prompt/repair flow, LLM execution, cache/persistence, health/bundle synchronization, and Markdown rendering.
- Confirmed the repository already contains focused Phase-2 owners for status, run sources, report reads, path linkage, and basic Brief parsing; P1.5.3 continues that existing ownership migration rather than creating a parallel UI framework.
- Froze the Operator Brief required-field contract and artifact version 14, canonical truth precedence, artifact paths, LLM/prompt/retry semantics, Korean sanitation policy, cache invalidation, and UI-visible meaning.
- Mapped direct private compatibility seams in tests/test_operator_ui.py (52 tests) and the existing facade migration contract in tests/test_operator_ui_data_access_phase2.py (28 tests).
- Frozen implementation order: O1 existing-owner completion -> O2 canonical Brief read model/sections -> O3 deterministic fallback/compact/prompt/sanitation -> O4 LLM service/persistence/rendering -> O5 UI page/read orchestration -> O6 operator visibility/period-summary decomposition.
- Runtime implementation remains gated by the P1.5 frozen-baseline policy.
- Design authority: docs/refactor/p1_5_operator_ui_brief_implementation_packet_v1_0.md.

# 2026-10-07 - P1.5.5 Scanner Design Complete

- Completed the P1.5.5 Scanner structural design without changing runtime behavior.
- Mapped the approximately 4,179-line graphs/nodes/scanner_node.py, including 61 top-level functions/classes and a roughly 1,945-line scanner_node orchestration hotspot.
- Confirmed existing focused owners for candidate selection, theme/practical filters, market-representative guard, candidate risk, output snapshots/payloads, feature hydration, runtime Scanner policy, Scanner bias, and memory bias; P1.5.5 reuses these owners rather than creating a parallel Scanner framework.
- Classified libs/agent/scanner.py and the older scan_candidates/select_candidate paths as legacy compatibility surfaces rather than canonical Scanner authority.
- Froze the 21-key compatibility state-write surface and the new ScannerAgentInput / ScannerAgentResult component boundary.
- Preserved the Scanner/Monitor authority split: Scanner chart-fit and Monitor-readiness remain soft ranking context; Monitor remains the hard entry/exit gate.
- Frozen implementation order: SC1 contracts/state adapter -> SC2 existing-owner completion -> SC3 guidance/repeat/prior -> SC4 compatibility/chart fit -> SC5 deterministic scoring -> SC6 evidence/IO -> SC7 scanner_node façade/tests.
- Known Scanner tuning ideas remain deferred; no weights, thresholds, candidate sources, veto semantics, rank ordering, UEF, Step5C/5D, execution or broker behavior changed.
- Design authority: docs/refactor/p1_5_scanner_implementation_packet_v1_0.md.

# 2026-10-07 - P1.5.6 Monitor Design Complete

- Completed the P1.5.6 Monitor structural design without changing runtime behavior.
- Mapped graphs/nodes/monitor_node.py at approximately 3,633 LOC with a roughly 2,635-line monitor_node orchestration hotspot and a roughly 660-line entry-candidate evaluator.
- Identified libs/runtime/intraday_monitor_signals.py (~3,608 LOC) as a separate deterministic signal/policy/chart/scoring hotspot for a later staged decomposition after Monitor orchestration is isolated.
- Confirmed existing focused owners for candidate cascade, entry guards, cost filtering, policy context, quality, sizing, state, memory bias, minute OHLCV, policy/strategy framing, plus the already decomposed monitor_exit package.
- Froze MonitorAgentInput / MonitorAgentResult and the 27-key compatibility state-write surface.
- Preserved the authority chain: Scanner soft ranking -> Monitor hard entry/exit timing and at-most-one intent -> Supervisor approval -> Executor broker side effect.
- Frozen implementation order: MO1 contracts/state adapter -> MO2 existing-owner completion -> MO3 entry orchestration -> MO4 exit orchestration -> MO5 intent arbitration/state adapter -> MO6 evidence/IO -> MO7 intraday signal engine -> MO8 monitor_node façade/tests.
- Monitor scoring/shadow promotion, thresholds, chart logic, candidate cascade, sizing, exit guards, carry, execution, UEF and Step5C/5D semantics remain unchanged.
- Design authority: docs/refactor/p1_5_monitor_implementation_packet_v1_0.md.

# 2026-10-07 - P1.5.7 Commander / Runtime Design Complete

- Completed the P1.5.7 Commander/runtime structural design without changing runtime behavior.
- Mapped graphs/commander_runtime.py at approximately 6,298 LOC with 105 top-level functions and 46 directly assigned compatibility state keys.
- Identified the main remaining hotspots in Commander decision building, behavior/applied-policy composition, open-position override logic, runtime lifecycle and phase routing.
- Confirmed existing focused owners under libs/runtime/commander/ for runtime modes, fast paths, execution bridging, Strategist cache/fingerprint/refresh, session context, shadow runtime and policy surfaces; P1.5.7 completes this existing decomposition rather than building a parallel runtime.
- Froze Commander as deterministic orchestration/policy with zero new LLM decision roles.
- Preserved graph_spine / decision_packet / integrated_chain modes, preopen/session/closeout phases, fast-path semantics, forced closeout SELL, pending BUY cancellation, runtime ownership/CAS, Supervisor/Executor safety and broker mutation ordering.
- Frozen implementation order: C1 contracts/state adapter -> C2 policy composition -> C3 entry control/decision builder -> C4 open-position control -> C5 lifecycle/reporter hooks -> C6 phase routing -> C7 fast-path/execution seams -> C8 evidence/artifacts -> C9 compatibility façade -> C10 test migration.
- No route policy, strategy, execution guard, UEF, Step5C/5D or broker behavior changed.
- Design authority: docs/refactor/p1_5_commander_runtime_implementation_packet_v1_0.md.

# 2026-10-07 - P1.5.8 Milestone / Runtime Naming Design Complete

- Completed the P1.5.8 behavior-preserving naming-cleanup design without changing runtime code.
- Inventory found approximately 468 milestone/phase/step-named file paths, dominated by historical docs (217) and tests (140); these are classified rather than blindly renamed.
- Frozen active runtime canonicalization for the M13 live-loop/tick/EOD path, legacy M10 bridge, M28 deployment/runtime entrypoints and the M31 agent-chain probe.
- Frozen compatibility aliases for milestone state/env names including m13_tick_pipeline, M13_LIVE_LOCK_*, M28_LIFECYCLE_*, M31_MOCK_EXAM_SESSION_HARD_GATE, M25_BATCH_* and M25_NOTIFY_*.
- Historical docs/tests/data, serialized event kinds/schema versions, existing compatibility artifact paths, Step5C/Step5D safety identifiers and UEF/Q program names are explicitly preserved.
- Lock-file path changes are treated as runtime-ownership-sensitive and are not allowed as cosmetic naming changes.
- Frozen N1-N7 migration sequence; legacy-wrapper deletion remains P1.5.10 work after consumer proof.
- No runtime topology, policy, strategy, execution, broker, UEF or Step5C/5D behavior changed.
- Design authority: docs/refactor/p1_5_runtime_naming_implementation_packet_v1_0.md.

# 2026-10-07 - P1.5.9 Executor Low-Risk Extraction Design Complete

- Completed the P1.5.9 low-risk Executor structural design without changing execution behavior.
- Mapped graphs/nodes/execute_from_packet.py at approximately 4,190 LOC with 101 top-level functions and a roughly 1,192-line execute_from_packet authority coordinator.
- Froze the existing execution ordering from readiness/guard evaluation through Supervisor verdict, durable readiness evidence, intent admission, Step5C physical/logical ownership, broker dispatch, BrokerOutcome normalization, UNKNOWN quarantine and post-submit recovery.
- Classified Supervisor context, all execution guards, request/order shaping, readiness evidence, Step5C CAS/idempotency, BrokerOutcome classification, UNKNOWN quarantine, recent-order persistence and cancel/recovery as SAFETY-LOCK.
- Limited P1.5.9 extraction to low-risk observability projection, canonical artifact coordination and optional pure order-view helpers, while preserving private compatibility wrappers.
- Confirmed existing execution owners under libs/execution/ and retained execute_owned_order as the single canonical mutation choke point.
- Frozen EX1-EX6 implementation order; no generic guard engine, new Executor service, broker abstraction, guard reordering, approval change or mutation-path change is permitted.
- No strategy, runtime topology, Supervisor authority, broker semantics, UEF, Step5C or Step5D behavior changed.
- Design authority: docs/refactor/p1_5_executor_low_risk_implementation_packet_v1_0.md.

# 2026-10-07 - P1.5.10 Compatibility-Wrapper Cleanup Design Complete

- Completed the P1.5.10 proof-based compatibility cleanup design without deleting runtime wrappers or changing behavior.
- Classified retained P1.5 seams as REMOVE_NOW, MIGRATE_THEN_REMOVE, KEEP_STABLE_FACADE, HISTORICAL_COMPATIBILITY, SAFETY_LOCK or CONTRACT_ALIAS.
- Confirmed libs/runtime/commander/integrated_chain_support.py is still actively imported by graphs/commander_runtime.py and therefore requires consumer migration before deletion.
- Kept apps/operator_ui/data_access.py and libs/reporting/trade_report_ai.py as intentional stable facades rather than treating wrapper count as a cleanup metric.
- Classified the legacy libs.agent Strategist/Scanner/Monitor/Commander stack and M11 scan/select nodes as historical compatibility surfaces, with coherent-stack retirement required before deletion.
- Identified duplicate AgentExecutor implementations as a strong cleanup candidate while leaving ExecutorAgent and Step5 safety paths intact.
- Frozen a compatibility inventory manifest requirement and CW1-CW7 migration/removal sequence.
- No runtime topology, state semantics, deployment path, Supervisor authority, guard order, CAS/idempotency, broker mutation, UEF or Step5C/5D behavior changed.
- Design authority: docs/refactor/p1_5_compatibility_wrapper_cleanup_implementation_packet_v1_0.md.

# 2026-10-07 - P1.5.11 Full Regression / Docker / UEF Replay / Freeze Design Complete

- Completed the P1.5.11 final acceptance and formal-freeze design without changing runtime behavior.
- Frozen a candidate-SHA-bound acceptance sequence covering targeted subsystem regression, full pytest, artifact hygiene, UEF frozen-manifest verification, deterministic UEF replay, Step5 authority/safety, Docker runtime acceptance, compatibility review, independent audit and human approval.
- Required UEF acceptance now explicitly includes candidate conservation, pair conservation with unique comparison IDs, UEF-9 VALID binding, deterministic replay and Daily UEF publication-safety behavior.
- Preserved the 2026-10-06 Daily UEF freshness incident as an operational upstream-freshness failure; P1.5.11 forbids weakening freshness contracts or fabricating canonical backfill to obtain a green freeze.
- Required Docker revalidation covers clean-image/source parity, startup/health, single runtime ownership, contender rejection, controlled restart/recovery, bounded ownership wait, SIGTERM drain, persistence, resource/EOD smoke and no restart storm/OOM.
- Required safety freeze preserves Supervisor authority, execute_owned_order as mutation choke point, Step5B/C/D semantics, readiness-evidence ordering, CAS/idempotency, UNKNOWN quarantine and broker-mutation ordering.
- Frozen P1.5 final evidence/report schema, independent Claude audit, human approval and freeze-tag policy. P1.6 remains blocked until P1_5_FORMAL_FREEZE=YES.
- Design authority: docs/refactor/p1_5_full_regression_docker_uef_freeze_implementation_packet_v1_0.md.

# 2026-10-07 - P1.5 PREP Closed / Design Frozen

- Formally closed P1.5 preparation and froze the implementation design while keeping runtime implementation gated.
- Quantified the primary giant refactor surface at 57,847 LOC, or approximately 61,455 LOC including the adjacent intraday Monitor signal-engine hotspot.
- Frozen target for the six non-Executor giant façade groups: 53,657 LOC of current giant surface becomes approximately 2,700-5,100 LOC of façade/orchestrator surface, a roughly 90.5-95.0% reduction in giant-file surface. This is responsibility extraction, not a claim of equivalent repository-total LOC deletion.
- Identified approximately 1,100 LOC of definite unreachable Reporting legacy tail as the strongest direct deletion opportunity.
- Frozen the responsibility-first target tree around thin graph adapters, explicit contracts, services, state adapters, evidence/observability owners, stable public facades and a deliberately centralized execution safety chain.
- Preserved two LLM decision roles (Strategist and Reporter), Scanner/Monitor deterministic authority, Commander deterministic routing, Supervisor safety authority and Executor broker side-effect authority.
- Marked P1.5 implementation as NOT STARTED and blocked until the upstream implementation baseline is formally frozen.
- Closure authority: docs/refactor/p1_5_prep_closure_report.md.

---

## 2026-10-08 · P1.5.2 Reporting Responsibility-Minimal Design v1.1
**Stage:** Architecture and Maintainability  
**Tags:** ARCHITECTURE · REFACTOR · TESTING · DOCUMENTATION

- GitHub에 푸시된 R2-A/B/C 실제 구현(3,040 / 3,044 / 949 LOC)을 기준으로 Reporting 상세 설계를 v1.1로 정정했습니다.
- 최초 책임 최소화 목표를 유지하되, 기존 WRAPPER와 실제 구현 책임을 한 함수씩 KEEP/MOVE/WRAPPER/DEAD/SAFETY-LOCK으로 증명하도록 했습니다.
- 중복 Owner를 만들지 않고, API 및 monkeypatch 호환성은 사용처를 이전·검증한 후에만 정리합니다.
- Reporting unit/integration/regression 테스트 분리, 전체 회귀검증과 독립 감사를 최종 P1.5.2 수용 조건으로 명시했습니다.
- 원래 v1.0 설계 및 R2-A/B/C 완료 증거는 보존하며 이번 커밋은 설계 문서만 변경합니다.
- 상세: docs/refactor/p1_5_reporting_implementation_packet_v1_1.md.

---

## 2026-10-08 · P1.5 Reporting Branch Consolidation — Design
**Stage:** Architecture and Maintainability  
**Tags:** ARCHITECTURE · DOCUMENTATION · REFACTOR

- v1.1 Reporting 책임 최소화 설계를 원래 `design/p1.5-p1.6-modernization`에 fast-forward 통합했습니다.
- 설계 v1.0 역사 기록과 v1.1 실행 지침을 모두 보존하며, 향후 설계 변경은 이 브랜치 하나에서만 진행합니다.
- 리팩토링 구현 단일 기준은 `codex/p1.5-reporting`입니다.
- 해당 브랜치의 설계 검증 Actions 트리거를 갱신했습니다. `main` 병합, 운영 설정 및 런타임 코드는 변경하지 않았습니다.
- 상세: docs/daily_patch/2026-10-08_p1_5_reporting_branch_consolidation.md.

---

## 2026-10-08 · P1.5.1–P1.5.11 Responsibility-Minimal Design Review
**Stage:** Architecture and Maintainability  
**Tags:** ARCHITECTURE · REFACTOR · DESIGN_REVIEW · TESTING · SAFETY

- P1.5.1부터 P1.5.11까지 기존 세부 구현 패킷 전체를 최초 책임 최소화 설계 원칙으로 재검토했습니다.
- 모든 v1.0 설계와 단계 순서는 유지하고, 함수별 단일 Owner·호환성 소비자 증거·독립 호출·State Adapter·IO/Authority 경계 인수조건을 추가했습니다.
- P1.5.9 Executor의 안전 체인 중앙집중은 명시적 크기 예외로 보존했습니다.
- P1.5.10 wrapper 소비자 검증과 P1.5.11 최종 Owner/테스트 보존 증거를 연결했습니다.
- 설계 수정만 수행했으며 런타임 코드, UEF, 실거래 및 Docker 배포는 변경하지 않았습니다.
- 정본 추가 문서: docs/refactor/p1_5_1_to_11_responsibility_alignment_v1_1.md.

# 2026-10-07 - P1.5.1 Reporting Definite Dead-Code Cleanup

- Removed 1,131 unreachable lines from `trade_report_ai.py` after the unconditional Markdown delegation return; public API preserved.
- Removed the earlier shadowed `_playbook_label` from `trade_report_markdown_clean.py`; the later complete binding remains.
- Required P1.5.1 suite: **149 passed**.
- Broader affected reporting selection: **280 test assertions passed**; pytest's production-path audit then identified test-only writes to `reports/metrics` and `reports/runtime`, and those tests were redirected to session `tmp_path` storage.
- No trading/report schema, truth precedence, LLM, Supervisor/Executor, UEF, or broker semantics changed.
- See `docs/daily_patch/2026-10-07_p1_5_1_reporting_dead_code_cleanup.md`.

# 2026-10-07 - P1.5.2 R2-A Reporting Service Extraction

- Extracted AI trade-report and trade-summary LLM orchestration into `libs/reporting/trade_report/service.py`.
- Existing `trade_report_ai.py` public functions remain compatibility façades; current helper and router seams are passed through at call time.
- Façade size moved from 7,223 to 6,770 LOC versus the P1.5.1 baseline.
- Python 3.12 focused regression: **151 passed**.
- No schema, truth precedence, LLM call-role/count, retry/repair, artifact-path, trading-authority, UEF, or broker semantic change.
- See `docs/daily_patch/2026-10-07_p1_5_2_r2a_reporting_service_extraction.md`.

## P1.5.2 R2-A Residual Update — Normalization / Operator Text / Shared Section Seed

- Added `normalization.py`, `operator_text.py`, and `sections.py` under `libs/reporting/trade_report/`.
- `trade_report_ai.py` now keeps compatibility wrappers while the moved implementations live in responsibility-specific owners.
- Façade size: **7,223 -> 5,156 LOC** relative to the P1.5.1 baseline (net -2,067 LOC).
- Python 3.12 focused Reporting suite passed **151/151** after normalization, after operator-text extraction, and again after shared-section extraction.
- No schema, truth precedence, LLM decision role/count, retry/repair, artifact path, trading authority, UEF or broker behavior changed.

## P1.5.2 R2-A Compact / Deterministic Fallback Update

- Extracted `_compact_story_input_for_llm()` into `trade_report_ai_compact_input.py`.
- Extracted deterministic `_fallback_report()` into `trade_report_ai_deterministic.py`.
- Compatibility wrappers and helper injection preserve the existing public/private call seams.
- `trade_report_ai.py`: **7,223 -> 4,376 LOC** versus the P1.5.1 baseline (net -2,847 LOC).
- Python 3.12 focused Reporting suite: **151/151 PASS**.
- No report contract, truth precedence, fallback meaning, LLM role/count, trading authority, UEF or broker semantics changed.

## P1.5.2 R2-A Completion — Section / Context Builders

- Extracted market/scanner and lifecycle section builders into `trade_report/sections.py`.
- Added `trade_report/context.py` for entry execution visibility and strategist compact-context assembly.
- `trade_report_ai.py`: **7,223 -> 3,040 LOC** from the P1.5.1 baseline (**-57.9%**).
- Intermediate dependency-boundary regressions were detected by tests and fixed without weakening assertions.
- Final focused gate: **151 passed**. Final broader Reporting regression: **297 passed, 1 warning**.
- R2-A is **COMPLETE**. R2-B Markdown façade decomposition is next.

## P1.5.2 R2-B — Markdown Summary / Signal Extraction

- Added `trade_report/markdown_summary.py` for trade-summary Markdown rendering and summary-input assembly.
- Added `trade_report/markdown_signals.py` for entry-watch, entry-signal and exit-trigger presentation logic.
- Existing public/private names in `trade_report_markdown_clean.py` remain compatibility façades/wrappers.
- Markdown façade size: **5,852 -> 4,187 LOC** (**-28.5%**).
- Focused regression: **168 passed**. Broader Reporting/API/runtime regression: **297 passed, 1 warning**.
- No Markdown contract, truth precedence, symbol metadata, signal interpretation, LLM, trading authority, UEF or broker semantic change.
- R2-B is **ACTIVE**; carryover/memory/translation residual extraction is next.
- See `docs/daily_patch/2026-10-07_p1_5_2_r2b_markdown_decomposition.md`.

## P1.5.2 R2-B — Carryover / Memory / Translation Update

- Extended `trade_report_markdown_strategy_memory.py` with carryover, prompt-proven memory and memory-application ownership.
- Added `trade_report/markdown_translation.py` for operator-facing translation rules.
- `trade_report_markdown_clean.py`: **5,852 -> 3,713 LOC** from the R2-B baseline (**-36.6%**).
- Incremental gates caught and fixed missing `timedelta` and `html/re` imports without semantic changes.
- Focused regression: **168 passed**. Broader Reporting/API/runtime regression: **297 passed, 1 warning**.
- No Markdown contract, memory meaning, translation output contract, truth precedence, LLM, trading authority, UEF or broker semantic change.
- R2-B remains **ACTIVE**; diagnostics/market/strategist residuals are next.

## P1.5.2 R2-B Completion — Diagnostics / Market / Strategist / Truth

- Added `trade_report/markdown_diagnostics.py` and `trade_report/markdown_strategy.py`.
- Moved final entry-visibility logic into `markdown_signals.py` and truth-surface rendering into `trade_report_markdown_truth.py`.
- `trade_report_markdown_clean.py`: **5,852 -> 3,044 LOC** (**-2,808 LOC / -48.0%**).
- No remaining function in the Markdown façade is 70 LOC or larger.
- Focused regression: **168 passed**. Final broader Reporting/API/runtime regression: **297 passed, 1 warning**.
- No Markdown contract, truth precedence, strategist/market meaning, LLM behavior, trading authority, UEF or broker semantic change.
- R2-B is **COMPLETE**. R2-C trade-story façade decomposition is next.

## P1.5.2 R2-C — Trade-story Human / Evidence / Assembly Extraction

- Moved market/scanner/monitor human payload builders into `trade_story_pipeline_human_payloads.py`.
- Moved scanner/filter evidence enrichment into `trade_story_pipeline_evidence_hydration.py`.
- Moved lifecycle bundle, report section seeds and final trade-story assembly into `trade_story_pipeline_story_assembly.py`.
- `trade_story_pipeline.py`: **4,527 -> 1,873 LOC** (**-58.6%**).
- Focused trade-story tests: **40 passed**. Broader Reporting + trade-story regression: **337 passed, 1 warning**.
- No story schema, lifecycle meaning, provenance, truth precedence, LLM, trading authority, UEF or broker semantic change.
- R2-C is **ACTIVE**; residual scanner/news/provenance helpers are next.
- See `docs/daily_patch/2026-10-07_p1_5_2_r2c_trade_story_decomposition.md`.

## P1.5.2 R2-C — Residual News / Scanner / Provenance Owners (2026-10-08)

- Extracted 15 news, 8 scanner and 13 provenance helpers into three dedicated `trade_story_pipeline_*.py` owners.
- Reduced `trade_story_pipeline.py` from **1,873 to 1,200 LOC** (**-673 LOC**, cumulative R2-C reduction **73.5%** from 4,527 LOC).
- Retained existing façade imports and introduced call-time lookup for helper seams across owner boundaries.
- Broader Reporting/trade-story suite passed **337 tests** with one existing Starlette warning; isolated helper-seam and UI Patch Notes consistency checks were added to the validation workflow.
- No report data schema, canonical evidence priority, LLM count/routing, Supervisor/Executor permission, UEF or broker execution change.
- R2-C remains **ACTIVE** for final seam and residual-function review; no deployment or live-mode enablement occurred.
- Technical evidence: `docs/daily_patch/2026-10-08_p1_5_2_r2c_residual_owners.md`.

## P1.5.2 R2-C Closure — Final Scanner/News Long Functions (2026-10-08)

- Extracted news/scanner contribution attachment, chart-fit evidence lookups, and normalized feature coverage from the trade-story façade.
- Final `trade_story_pipeline.py`: **4,527 → 949 LOC** (**-3,578 LOC / ~79.0%** cumulative R2-C reduction); **45 functions**, longest **70 LOC**.
- Compatibility façade keeps exact callable names, and extracted owner functions resolve patchable helpers at call time.
- Python 3.12: **337 passed, 1 existing warning** (broader trade-story / Reporting), plus **12 passed, 1 existing warning** (helper seam / UI Patch Notes API and sync).
- ZIP artifact consists only of changed files; no repo-persistent test artifacts, production deployment, real trade orders, broker changes or authority changes.
- **R2-C structural extraction COMPLETE on feature branch only**; main integration/deployment requires a separate review.
- Technical audit: `docs/daily_patch/2026-10-08_p1_5_2_r2c_residual_owners.md`.

---

## 2026-10-08 · P1.5 Reporting Branch Consolidation — Implementation
**Stage:** Architecture and Maintainability  
**Tags:** ARCHITECTURE · REFACTOR · DOCUMENTATION · TESTING

- P1.5.1, R2-A, R2-B, R2-C 및 2026-10-08 잔여 추출의 직선형 Git 이력을 `codex/p1.5-reporting` 하나의 구현 기준으로 통합했습니다.
- 설계 단일 기준은 `design/p1.5-p1.6-modernization`이며, v1.0 원본 설계와 v1.1 책임 최소화 수정 설계를 모두 보존합니다.
- 기존 Report CI를 통합 브랜치로 옮기고, ZIP 산출물은 해당 커밋의 실제 변경 파일만 포함하도록 수정했습니다.
- 과거 배치별 브랜치는 개발 중단 및 삭제 검토 대상으로만 유지합니다. `main` 병합이나 실거래/도커 설정은 변경하지 않았습니다.
- 상세: docs/daily_patch/2026-10-08_p1_5_reporting_branch_consolidation.md.

---

## 2026-10-09 · P1.5 Small-Owner and Executor v1.2
**Stage:** Architecture and Maintainability  
**Tags:** ARCHITECTURE · REFACTOR · EXECUTOR · REPORTING · SAFETY · TESTING

- P1.5.1/R2-A/B/C 기존 코드를 **전체 롤백하지 않고 현재 refactor/p1.5에서 계속 구현**합니다. C:\Agentra 로컬 환경의 HEAD와 실데이터 BEFORE 동등성을 먼저 확인합니다.
- 새로 추출·확장한 단일 책임 구현 Owner는 **150~300줄 권장, 350 physical LOC 초과 금지**로 설계를 강화했습니다. 현재 2,233/1,356/1,337/1,275줄 등 대형 Reporting Owner는 책임별로 추가 분리합니다.
- Executor `execute_from_packet.py`는 안전한 EX1~EX6 이후 추가 EX7~EX10을 선택적으로 허용합니다. 현 4,189 LOC → 중간 2,600~3,200 → 동등성 입증 시 최종 1,200~1,800 LOC를 목표로 하되, 단일 주문 변경 권한·Guard 순서·R6.2·Step5C/D·UNKNOWN 처리는 보존합니다.
- P1.2 CLOSED, P1.3 FULL_DOCKER_FROZEN, Docker 2 GiB, 7개 Agent 및 Q12 dirty worktree 보존. 설계 문서와 검증 Workflow만 변경하고 런타임 Python은 수정하지 않았습니다.
- 문서: `docs/refactor/p1_5_small_owner_policy_and_rollback_decision_v1_2.md`, `p1_5_reporting_implementation_packet_v1_2.md`, `p1_5_executor_safe_decomposition_packet_v1_1.md`.

---

## 2026-10-09 · P1.5 Git-Driven Claude/Codex Work Orders v1.0
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · ARCHITECTURE · DOCUMENTATION · TESTING · WORKFLOW

- 긴 채팅 프롬프트 대신 **GitHub 문서를 단일 작업 지시의 정본**으로 지정했습니다. 루트의 `CLAUDE.md`, `AGENTS.md`에서 각 역할의 운영 지침과 `docs/refactor/work_orders/CURRENT.md`를 읽도록 구성했습니다.
- `docs/refactor/P15_EXECUTION_PROTOCOL.md`에 GPT 범위/수용 판정 → 로컬 Claude 구현 → 로컬 Codex 독립 검증 → GPT PASS/FIX 단계 전환을 정의했습니다.
- 첫 지시서 `P15-R2-R0R1-001`은 Reporting 현재 로컬 상태/BEFORE 동등성/함수·사용처·Owner 목록 확인만 수행하는 감사 전용 작업입니다. Python 수정 없이 증거를 먼저 확보합니다.
- 작업별 증거는 Claude와 Codex가 서로 다른 파일에 기록하고, 정확한 코드 SHA를 기준으로 검증합니다. `refactor/p1.5` 한 브랜치, Q12 dirty worktree 보존, 새 Owner 350 LOC 상한, UI 패치노트·변경 파일 ZIP 규칙을 유지합니다.
- 이번 커밋은 문서와 검증 워크플로만 변경했습니다. 운영·매매·Docker·UEF 코드는 변경하지 않았습니다.

---

## 2026-10-09 · P1.5.2 Reporting Sections Owner Split 01
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · REPORTING · TESTING

- `trade_report/sections.py`의 독립 섹션 빌더 16개를 **책임별 8개 단일 Owner**로 분리했습니다. 추출된 새 파일은 전부 **350 physical LOC 이하**입니다.
- 기존 16개 API명과 함수 본문, `deps` 호출 바인딩을 변경하지 않고 `sections.py`에서 명시적으로 재공개합니다.
- 약 700줄인 `build_shared_summary_seed()`는 동작·truth precedence를 보존한 채 남겨 **별도 작업으로 검증 후 분리**합니다.
- 변경 사항은 GitHub CI와 로컬 실데이터/Codex 검증을 거쳐 최종 인수합니다. 실거래 권한·UEF·Docker 설정은 변경하지 않았습니다.

---

## 2026-10-09 · P1.5.2 Reporting Seed Owner Split 02
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · REPORTING · TESTING

- `build_shared_summary_seed()`의 Commander, Scanner, Monitor, Strategist 시드 구성 책임을 4개 소형 Owner에 분리했습니다. 각 파일은 350 LOC 이하입니다.
- 사실 우선순위와 최종 결과 조립 로직, 호출 순서, 기존 16개 섹션 API를 유지합니다. 새 로직이나 외부 의존성은 추가하지 않았습니다.
- CI 회귀 테스트를 거쳐 사용하며, 로컬 실데이터 동등성 검증은 별도 인수 조건으로 남깁니다.

---

## 2026-10-09 · P1.5.2 Trade Story Assembly Owner Split 03
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · REPORTING · TESTING

- Trade Story의 타임라인·라이프사이클 정규화·라이프사이클 번들·섹션 시드 책임 6개 함수를 **4개 단일 Owner**로 이동했습니다. 구현 본문과 API를 변경하지 않았습니다.
- 새 파일은 모두 350 LOC 이하입니다. 남은 809줄 Story 조립 함수는 별도 동등성 검증 후 분리합니다.

---

## 2026-10-09 · P1.5.2 Seed Owner Import Binding Repair
**Stage:** Architecture and Maintainability  
**Tags:** BUGFIX · REPORTING · TESTING

- Shared Seed 분리 커밋의 CI가 누락된 `build_seed_commander_route` import로 실패했습니다. 이력과 실패 근거를 보존하고 소형 Owner 4개에 대한 명시적 import를 복원했습니다.
- 기존 함수의 본문과 출력 의미는 변경하지 않았고, 전체 회귀검증 결과로 다시 인수합니다.

---

## 2026-10-09 · P1.5.2 Human Market and Scanner Owner Split 04
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · REPORTING · TESTING

- Trade Story의 Market Context / Scanner Reason 사람용 프로젝션을 각 350 LOC 이하의 단일 Owner 파일로 이동했습니다. 원본 함수 본문과 공개 API 이름을 보존했습니다.
- 남은 Monitor Reason 대형 함수는 별도 안전 동등성 작업으로 유지합니다.

---

## 2026-10-09 · P1.5.2 Markdown Signals Owner Split 05
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · REPORTING · TESTING

- Markdown의 Entry Watch, Entry Metrics, Exit 판단 설명 7개 함수를 3개 Owner로 분리했습니다. 각 모듈은 350 LOC 이하입니다.
- 원래 모듈 경로와 함수 본문을 그대로 유지해 기존 import 사용자와 출력 계약을 보존합니다.

---

## 2026-10-09 · P1.5.2 Story Evidence Owner Split 06
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · REPORTING · TESTING

- Trade Story의 정본 증거 hydration, Scanner enrichment, Filters enrichment 5개 구현을 각각 350 LOC 이하인 Owner 3개로 이동했습니다.
- 기존 import 경로·함수 본문·증거 우선순위는 유지했습니다.

---

## 2026-10-09 · P1.5.2 Reporting Service Owner Split 07
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · REPORTING · TESTING

- Reporting 서비스의 AI 생성 및 deterministic summary 두 함수를 각각 독립적인 350 LOC 이하 Owner로 옮겼습니다.
- 기존 `trade_report/service.py`는 공개 import 호환성만 유지하며, 서비스 본문과 LLM 동작은 변경하지 않았습니다.

---

## 2026-10-09 · P1.5.2 Original Source AST Parity Gate
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · QUALITY

- 분리된 Reporting 함수 38개의 AST를 시작 커밋 `2fb4b8f`의 원본 구현과 대조하고, 기존 import 재공개 동일성과 새 Owner의 350 LOC 제한을 검사하는 CI를 추가했습니다.
- 실제 로컬 리포트 데이터/LLM/UEF 검증을 대신할 수는 없으며 별도 Codex 독립검증이 필요합니다.

---

## 2026-10-09 · P1.5.2 Owner Parity Gate Invocation Fix
**Stage:** Architecture and Maintainability  
**Tags:** BUGFIX · TESTING

- AST 동등성 검증 실행 시 저장소 루트가 Python import 경로에서 빠져 CI가 실패했습니다. 모듈 방식(`python -m`)으로 실행하도록 교정했습니다. 검사 내용과 런타임 코드는 변경하지 않았습니다.

---

## 2026-10-09 · P1.5.2 AI Owner Physical LOC Cap Repair
**Stage:** Architecture and Maintainability  
**Tags:** BUGFIX · REFACTOR · TESTING

- 물리적 LOC 상한 검사에서 AI 서비스 파일의 마지막 공백 줄 때문에 351 LOC가 검출됐습니다. 함수 AST는 그대로 보존하고 뒤쪽 공백만 삭제했습니다(351 → 347). 검사 기준을 완화하지 않았습니다.

---

## 2026-10-09 · P1.5.2 GPT Split Evidence and Local Verification Work Order
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · DOCUMENTATION · TESTING · QUALITY

- P1.5.2 GPT 구현 분할 작업을 코드 SHA `4f291e9`로 동결해 검증 지시서를 만들었습니다. **26개 소형 Owner**, 38개 원본 함수 AST 동등성, GitHub Reporting 테스트 337+12 PASS가 확인됐습니다.
- 다만 주요 façade와 800/700/400줄대 혼합 책임 함수, 로컬 실데이터/전체 회귀 테스트는 **미완료**이므로 P1.5.2의 최종 완료는 선언하지 않았습니다.
- `work_orders/CURRENT.md`는 Claude/Codex가 코드 수정 없이 각각 로컬 실데이터·호출/계약/모듈 검증만 수행하도록 갱신했습니다. P1.5.3 자동 착수는 금지했습니다.
- 검증 GitHub CI에서 P1.5.2 시작 커밋 대비 **실제로 수정된 파일만 ZIP**에 수록하게 했습니다.

---

## 2026-10-09 · P1.5.2 ZIP Upload Path Repair
**Stage:** Architecture and Maintainability  
**Tags:** BUGFIX · TESTING · DOCUMENTATION

- 최종 CI의 코드 검증(38 AST, 26 소형 Owner, 337+12 회귀)은 통과했고 ZIP 업로드 경로만 이전 파일명을 참조했습니다. 변경 파일 ZIP의 업로드 경로를 일치시켰으며 런타임 코드는 수정하지 않았습니다.

---

## 2026-10-09 · P1.5.2 GPT Remote Source Audit
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · DOCUMENTATION · TESTING · QUALITY

- `refactor/p1.5` 원격 HEAD `8a9ba219`과 최신 GitHub Actions run `37877818709`를 다시 감사했습니다. 38개 원본 AST/export parity, 26개 소형 Owner 350 LOC 상한, Reporting 337 + seam/UI 12 회귀 및 변경 파일 ZIP 업로드가 모두 성공했습니다.
- 성공 artifact를 격리 경로에서 AST/import 분석한 결과, 변경 모듈의 의존 방향은 façade/wrapper → Owner이며 변경 모듈 사이 순환 import는 발견되지 않았습니다.
- 다만 3,039/3,043/948 LOC 공개 façade와 802/464/428/807/703 LOC의 잔여 대형 구현은 여전히 OPEN입니다.
- `C:\Agentra` 실데이터·worktree·full pytest 및 별도 Claude/Codex 증거가 아직 없으므로 **P1.5.2는 CLOSED가 아니며 P1.5.3은 시작하지 않습니다.**
- 런타임 Python, 실거래, Broker, UEF, Docker, Step5C/D, R6.2, 전략 및 production 데이터 경로는 변경하지 않았습니다.
- 근거: `docs/refactor/work_orders/evidence/P15-R2-GPT-VERIFY-002-GPT-REMOTE.md`.

---

## 2026-10-09 · P1.5.2 GPT Lifecycle Human Owner 08
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- trade-story 생명주기 human fallback/truth 우선순위를 별도 작은 Owner (116 LOC)로 분리해 기존 835 LOC 구현 파일을 762 LOC로 축소했습니다.
- 기존 call-time `deps` 호환성 유지, 직접/생명주기 경로의 사전/사후 비교 및 보완 회귀 테스트 추가.
- 출력·LLM·전략·실거래·UEF·Docker·Step5C/D/R6.2 기능 변경 없음. **P1.5.2는 계속 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_lifecycle_human_small_owner_08.md`.

---

## 2026-10-09 · P1.5.2 GPT Shared Story Provenance Owner 09
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- lifecycle v2와 일반 v1의 동일한 reasoning provenance 블록(각 67줄)을 85 LOC 단일 Owner로 통합했습니다.
- story assembly 762 → 644 LOC. canonical 증거 우선순위·call-time monkeypatch 호환 유지, 별도 단위 테스트 추가.
- 직전 CI `37879379703`은 Python 테스트 이전에 CURRENT 문구 검사에서 FAIL, `a010f53`에서 문구 수정. **P1.5.2는 여전히 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_story_provenance_owner_09.md`.

---

## 2026-10-09 · P1.5.2 GPT Direct Story Owner 10
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 일반(v1) trade-story 조립 경로를 단일 246 LOC Owner로 추출, 기존 story assembly 644 → 445 LOC 축소.
- 기존 v1/v2 사전·사후 결과 일치, 350 LOC 상한 검증 추가. UI·실거래·UEF·Docker·LLM 기능은 변경하지 않았습니다.
- **P1.5.2 OPEN**, 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_direct_story_owner_10.md`.

---

## 2026-10-09 · P1.5.2 GPT Lifecycle Evidence Owner 11
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- canonical Strategist/Scanner/Monitor 근거·선택·출구정책 해석을 169 LOC 작은 Owner로 분리해 story assembly 부모 파일 **445 → 331 LOC**로 줄였습니다 (시작 835 LOC).
- v1/v2 before/after smoke 일치, 350 LOC 상한 및 의존 방향 단위 테스트 추가. Trading/UEF/Docker/LLM 수정 없음.
- 남은 Markdown/Human/Operator/public façade 책임 및 로컬 검증으로 **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_lifecycle_evidence_owner_11.md`.

---

## 2026-10-09 · P1.5.2 GPT Facade Symbol Inventory 12
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · DOCUMENTATION · TESTING

- Reporting 공개 façade 3개의 top-level 정의 **436개**를 파일·줄 범위·호환성·소유 책임별로 인벤토리화하고 CI 누락 검사를 추가했습니다.
- 실제 사용자 환경의 monkeypatch/호출 소비자는 검증 전이므로 무근거 DEAD 삭제 없음. 원본 public/import 경로 유지, P1.5.2 OPEN.
- 근거: `docs/refactor/p1_5_2_facade_symbol_audit_2026-10-09.md`.

---

## 2026-10-09 · P1.5.2 GPT Monitor Diagnostics Owner 13
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Monitor 진단 문구의 watch axes 및 entry threshold gaps를 75 LOC 전용 Owner로 분리, 기존 human payload 파일 861 → 812 LOC.
- 위험/매매 의사결정이 아닌 읽기 전용 문구 로직만 이동. 원래 호출 주입·회귀 테스트 유지. P1.5.2는 OPEN.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_diagnostics_owner_13.md`.

---

## 2026-10-09 · P1.5.2 GPT Operator Phrase Owners 14
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 긴 operator 문구 처리 함수에서 exact phrase / 시장·종목선정 / 거래 생명주기·실행 문구를 **3개 별도 <=350 LOC Owner**로 분리했습니다. 원래 매칭 순서·공개 함수·호출 시 의존성 주입은 유지했습니다.
- 신규 회귀 테스트와 기존 Reporting CI를 함께 실행하고, 실제 로컬 데이터 검증 전에는 **P1.5.2 OPEN**을 유지합니다.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_operator_phrase_owners_14.md`.

---

## 2026-10-09 · P1.5.2 GPT Operator Language Owner 15
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 언어 정규화 구현을 별도 <=350 LOC Owner로 옮기고 공개 import 경로, call-time clip/sanitize 테스트 주입은 유지했습니다.
- `operator_text.py` 443 → 318 LOC. P1.5.2 승인 전까지 실제 보고서/전수 회귀 검증 필요.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_operator_language_owner_15.md`.

---

## 2026-10-09 · P1.5.2 GPT Summary Findings Owner 16
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- deterministic positives/problems/causes/validation 질문 구성을 별도 Owner로 분리했습니다. 원래 평가 순서 및 call-time dependencies 유지, 안전 회귀 검사 추가.
- 전략/승인/주문/UEF/Step5/Docker 동작을 변경하지 않았습니다. **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_summary_findings_owner_16.md`.

---

## 2026-10-09 · P1.5.2 GPT Monitor Policy Bullets Owner 17
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 모니터 정책 중 손절/익절/추적손절의 **보고서 표시 문구만** 별도 Owner(89 LOC)로 분리했습니다. 원래 출력 순서와 보조함수 주입 유지.
- 매매 전략·주문·가드·UEF·Docker 권한 변경 없음. **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_policy_bullets_17.md`.

---

## 2026-10-09 · P1.5.2 GPT Monitor Entry Review Owner 18
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 진입/차트 피처 및 정책 근거를 설명하는 read-only Monitor 문구를 전용 Owner 146 LOC로 분리했습니다. 원래 항목 순서, 21개 호출 시점 입력·함수 의존성 유지.
- 매매/주문 권한·UEF·Docker 불변, **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_entry_review_owner_18.md`.

---

## 2026-10-09 · P1.5.2 GPT Remote Continuation 08–18 CI Closeout
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION · QUALITY

- 작은 Reporting Owner 12개 추가, 공개 façade 436개 심볼 인벤토리 및 원본 호환성 경계를 유지했습니다. `trade_story_pipeline_story_assembly.py` 331 LOC, `operator_text.py` 320 LOC.
- 최신 CI `37881544761` **PASS** — 원본 AST 38개, Reporting 337건, helper/UI/owner 43건, 변경 파일 ZIP 업로드. 실패 `37881458077`의 들여쓰기 오류도 이력에 남기고 `8f3c1465` 수정 후 재검증했습니다.
- Markdown summary 1,226 LOC, Monitor human 636 LOC, 공개 façade 3,039/3,043/948 LOC 및 실데이터·전체 pytest·독립검증은 아직 OPEN. **P1.5.2 미종료, P1.5.3 미승인.**
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_gpt_continuation_08_to_18_ci_accepted.md`.

---

## 2026-10-09 · P1.5.2 Monitor Context Owner 19
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Monitor 스냅샷/정책 근거·진입 관측 컨텍스트 224줄을 258 LOC 전용 Owner로 분리하여 human payload **636 → 431 LOC**로 축소했습니다.
- AST 동일성 84개 문장 및 65개 명시적 반환값 검증, 6개 사전/사후 독립 실행 fixture PASS. 실제 Windows 거래 리포트 비교는 미실행.
- 전략·실거래·UEF·R6.2·Step5/Docker 불변. **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_monitor_context_split_19.md`.

---

## 2026-10-09 · P1.5.2 Render Diagnostics Owner 20
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Markdown 요약의 강점/문제점/원인/권고 문구 109줄을 150 LOC Owner로 분리했습니다. `markdown_summary.py` 1226 → 1145 LOC, 원본 AST 37구문 동일.
- 이월청산/부분청산/비용/차순위/청산 패턴의 64개 조합에서 사전·사후 출력 일치. 실제 거래 보고서 골든 테스트는 미실행.
- 거래 권한·UEF·R6.2·Step5/Docker 불변. **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_render_diagnostics_owner_20.md`.

---

## 2026-10-09 · P1.5.2 Monitor Trace Wrapper Owner 21
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Monitor 정책 근거/진입 차단 관측 및 Strategist 적응형 청산 추적 3개 함수의 본문을 107 LOC Owner로 이동. 공개 래퍼와 monkeypatch 의존성 그대로 유지.
- Human payload 부모 파일 **431 → 350 LOC**로 350 LOC 상한 충족. 3개 함수 AST 동일, 32×3 전/후 결과 일치.
- Markdown·공개 façade 및 C:\\Agentra 실데이터 검증은 여전히 OPEN. 매매 실행 경계 불변, **P1.5.2 미종료**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_monitor_trace_wrapper_owner_21.md`.

---

## 2026-10-09 · P1.5.2 New Owner Dependency DAG Gate
**Stage:** Architecture and Maintainability  
**Tags:** TESTING · QUALITY · DOCUMENTATION

- 새 Reporting Owner 15개 각각 350 LOC 이하, 공개 façade·실거래 코드 역방향 import 금지, Owner 순환 의존 금지를 검사하는 pytest를 CI에 추가했습니다.
- 직전 Owner 19/20/21 원격 CI PASS. 이 추가 게이트는 이번 커밋의 CI에서 별도 확인합니다.
- Markdown/Public façade·실데이터/전체 테스트·독립 검증은 **OPEN**이며 거래 권한·Docker·UEF·R6.2 불변.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_owner_19_21_dependency_gate.md`.

---

## 2026-10-09 · P1.5.2 GPT Markdown Render Section Owners 22
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 보고서 개요·시장/뉴스·매매 결정·최종 판단을 4개 Markdown Owner로 분리해 `markdown_summary.py` **1,145 → 827 LOC**로 감소했습니다.
- 6개 원본 출력 SHA-256 골든을 CI에 고정하고 새 Owner 19개 크기/의존성 검사를 추가했습니다. 실거래 보고서 검증 전에는 **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_markdown_render_section_owners_22.md`.

---

## 2026-10-09 · P1.5.2 GPT Summary Input Contract Owners 23
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Broker alignment/Market & Strategy/Decision Flow 3개 출력 딕셔너리를 전용 Owner로 분리하여 `markdown_summary.py` 827 → 740 LOC.
- 원본 계약 AST와 6개 JSON SHA-256 골든 동일성 검증 추가, 22개 Owner DAG·크기 체크. 로컬 원천 데이터 검증 전이므로 **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_summary_input_contract_owners_23.md`.

---

## 2026-10-09 · P1.5.2 GPT Summary Input Main Builder Owner 24
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- `build_trade_summary_input`의 구현을 328 LOC Owner로 옮기고 공개 함수는 호출시점 의존성 주입 래퍼로 유지. `markdown_summary.py` 740 → 432 LOC.
- 입력 JSON 골든 6건과 monkeypatch 호환 검증, 23개 신규 Owner 크기/DAG 검사 추가. 실제 거래 보고서 검증 전 **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_input_main_builder_owner_24.md`.

---

## 2026-10-09 · P1.5.2 GPT Markdown Renderer and Helpers Owner 25
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Markdown 내부 헬퍼 11개 및 렌더러 본문을 소형 Owner 2개 (130/326 LOC)로 분리했습니다. 기존 `markdown_summary.py` 432 → 60 LOC 호환 공개 래퍼만 유지.
- 원본 보고서 바이트 골든 6개, 호출시점 monkeypatch 및 25개 Owner 의존성 검증 추가. 실데이터 검증 전 **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_markdown_facade_main_renderer_25.md`.

---

## 2026-10-09 · P1.5.2 GPT Owner25 Remote CI Evidence Closeout
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION · QUALITY

- Markdown 공개 래퍼 60 LOC / 신규 구현 Owner 최대 350 LOC로 분리 완료. 원격 CI `37885565737` **337 Reporting + 72 Helper/UI/Owner PASS**, 기존 38개 함수 AST 검증 PASS.
- 12개 합성 Golden 출력, 25개 신규 Owner 순환/역방향 의존 검사 포함. 로컬 진짜 보고서/LLM/전체 pytest·독립검증은 미실행. 3개 대형 공개 façade도 소비자 증거 확보 전까지 유지.
- **P1.5.2 OPEN**, P1.5.3 미시작. 매매 실행·Docker·UEF·R6.2·Step5C/D 불변.
- 근거: `docs/refactor/work_orders/evidence/P15-R2-GPT-P152-OWNER25-REMOTE-CI.md`.

---

## 2026-10-09 · P1.5.2 Static Façade Consumer Evidence 26
**Stage:** Architecture and Maintainability  
**Tags:** TESTING · QUALITY · DOCUMENTATION

- 3개 Reporting 공개 façade의 436개 심볼에 대해 저장소 전체의 정적 import·모듈 별칭·monkeypatch·getattr·문자열 patch/동적 참조를 구분하는 CI 근거 산출기를 추가했습니다.
- 정적으로 참조되지 않은 함수도 **DEAD 판정 금지**, 런타임 소비자·로컬 검증 OPEN. P1.5.3 미시작.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_facade_static_consumer_evidence_26.md`.

---

## 2026-10-09 · P1.5.2 Story Façade Compatible Owner 27
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 기존 Story 함수 4개 본문을 Strategist 근거/Scanner 필터 전용 Owner 2개 (103/73 LOC)로 분리. 공개 이름·호출시점 monkeypatch 유지; façade 948 → 826 LOC.
- 436개 공개 함수 장부 위치를 동기화하고 원본 AST/출력 등가·monkeypatch CI 검사를 추가했어. 매매 권한·UEF·Docker 불변, **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_story_facade_compatible_owners_27.md`.

---

## 2026-10-09 · P1.5.2 Story Façade Human Judgments Owner 28
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Supervisor·Reporter·Operator의 기존 설명 함수 3개 본문을 110 LOC 전용 Owner로 분리하고 public 함수명·시그니처·호출 시점 의존성을 유지했습니다. Story façade 826 → 753 LOC.
- 원본 AST·출력 비교·monkeypatch 검사, 공개 심볼 436개 장부 동기화. 실거래 경계 불변이며 **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_story_facade_human_judgments_28.md`.

---

## 2026-10-09 · P1.5.2 Story Report Contract Owner 29
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Story 식별자·커버리지·실행모드 *표시* 함수 8개를 162 LOC Owner로 이동, Story façade 753 → 636 LOC. 공개 함수 45개와 monkeypatch 유지.
- 원본 AST/대표 출력 및 29개 Owner DAG CI 고정. Broker 실제 모드·주문 경로는 변경하지 않았고 **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_story_contract_owner_29.md`.

---

## 2026-10-09 · P1.5.2 Markdown Clean Summary Language Owner 30
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- Markdown Clean 순수 출력 문구 함수 8개를 140 LOC Owner로 분리하고 부모 3043 → 2948 LOC. 공개 함수 209개와 monkeypatch 경로 보존.
- 원본 AST/문자열 출력 CI, 30개 신규 Owner DAG 검사. 실데이터/실거래 권한 불변. **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_markdown_clean_summary_language_30.md`.

---

## 2026-10-09 · P1.5.2 AI Reporter Text Helpers Owner 31
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- AI Reporter의 출력용 helper 6개 구현을 47 LOC 전용 Owner로 분리. 공개 API 182개 유지, 부모 3039 → 3027 LOC.
- 원본 AST·출력/monkeypatch 및 31개 Owner DAG CI. LLM/매매 경계 불변, **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_ai_facade_text_helpers_31.md`.

---

## 2026-10-09 · P1.5.2 Owners26–31 Remote CI Evidence
**Stage:** Architecture and Maintainability  
**Tags:** TESTING · QUALITY · DOCUMENTATION

- 최신 CI `37887432333` **337 Reporting + 144 Helper/Owner/UI PASS**, 31개 Owner 의존성 검사 완료. 세 공개 façade 3027/2948/636 LOC, 436 함수 보존.
- 소비자 맵 1,763개 Python 파일 중 공개 심볼 82개 정적 참조, 동적 불확실 4건; 나머지 DEAD 금지. 로컬 실데이터 및 독립 검증은 **OPEN**.
- 근거: `docs/refactor/work_orders/evidence/P15-R2-GPT-P152-OWNER26-31-REMOTE-CI.md`, `docs/refactor/work_orders/P15_R2_OWNER31_READONLY_LOCAL_ACCEPTANCE_CHECKLIST.md`.

---

## 2026-10-09 · P1.5.2 Markdown Clean Display Owners 32–33
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 리포트 표시 문자열/Strategist 설명 함수 21개를 Owner 두 개(227/79 LOC)로 분리. 기존 `trade_report_markdown_clean.py` **2948→2717 LOC**. 공개 함수 209개 및 monkeypatch 유지.
- 원본 AST/출력 21개, 33-Owner CI 크기/DAG 검사. 실제 보고서·LLM/독립 검증 전 **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_markdown_clean_label_owner_32_33.md`.

---

## 2026-10-09 · P1.5.2 Façade ABI and Authority Scope Guard 34
**Stage:** Architecture and Maintainability  
**Tags:** TESTING · QUALITY · DOCUMENTATION

- Reporter/Story 공개 함수 436개 ABI(인수/반환형/데코레이터)와 실제 import 가능 여부를 기존 소스 기준으로 CI 고정했습니다.
- 기준 SHA 이후 Trading·Broker·Executor·Supervisor·Docker·UEF 소스 파일이 변경되면 테스트가 실패하도록 범위를 제한했습니다.
- 로컬 거래 리포트·LLM/전체 독립 검증은 별도 OPEN, **P1.5.2 미종료**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_facade_abi_authority_guard_34.md`.

---

## 2026-10-09 · P1.5.2 AI Reporter Market and Scanner Labels Owners 35–36
**Stage:** Architecture and Maintainability  
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- AI Reporter 시장·테마·스캐너·진입 결과 표시 21개 함수를 117/166 LOC Owner로 분리. 공개 부모 **3027→2820 LOC**로 감소했고 182개 함수·monkeypatch는 그대로 유지.
- 본문 원본 AST/출력 21개 검증, 35-Owner DAG 및 공개 API·매매 영역 보호 CI 포함. **P1.5.2 OPEN**.
- 근거: `docs/daily_patch/2026-10-09_p1_5_2_ai_facade_labels_35_36.md`.

---

## 2026-10-09 · P1.5.2 Owners32–36 Remote CI Evidence
**Stage:** Architecture and Maintainability  
**Tags:** TESTING · QUALITY · DOCUMENTATION

- 원격 코드 `46e4e7439d146ffdc6135b5b483c04dc78ce0cfa` CI `37888641327`: Reporting **337 PASS**, Helper/UI/Owner **234 PASS**, 35 Owner 크기/DAG 및 436 public ABI/변경 경로 검사 PASS.
- Markdown Clean 2,717 LOC, AI Reporter 2,820 LOC, Story 636 LOC. 총 436 공개 심볼 유지, 미참조 340개는 DEAD가 아니라 UNKNOWN.
- 독립 Claude/Codex 읽기 전용 로컬 검증 지시서와 원격 근거 최신화. 실보고서·전체 테스트 미실행이므로 **P1.5.2 OPEN, P1.5.3 미시작**.
- 근거: `docs/refactor/work_orders/evidence/P15-R2-GPT-P152-OWNER32-36-REMOTE-CI.md`.

---

## 2026-10-10 · P1.5.2 AI Reporter Duration/Grammar Owner37
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 보유시간 문자열 변환·한국어 서술격 및 ‘으로/로’ 처리를 별도 소형 Owner로 분리하고 기존 호출 경로 및 monkeypatch 호환성을 유지했습니다.
- 원본 AST/결과·의존성 패치 회귀 테스트와 36개 Owner DAG/350 LOC 검사, 신규 커밋 변경 파일만 담는 ZIP CI 아티팩트를 추가했습니다.
- 실제 C:\\Agentra 거래 리포트·전체 pytest·독립 Claude/Codex 검증 미완료로 **P1.5.2 OPEN**, P1.5.3 미착수입니다. 실거래/UEF/R6.2/Docker/Step5C/D 변경 없음.
- 근거: `docs/daily_patch/2026-10-10_p1_5_2_ai_duration_language_owner_37.md`.
- GitHub Actions [`38023989098`](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38023989098) **SUCCESS**: Reporting 337, Owner/UI 255 PASS; 원본 함수 AST/입력·출력/monkeypatch와 436 공개 함수 보존. 실데이터·전체 pytest·독립 검증 미완료.
- 원격 증거: `docs/refactor/work_orders/evidence/P15-R2-GPT-P152-OWNER37-REMOTE-CI.md`.

---

## 2026-10-10 · P1.5.2 Markdown Clean News Headlines Owner38
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCUMENTATION

- 뉴스 제목 정제·샘플링·종목코드 매칭·타 종목 기사 배제·문구 8개를 전용 Owner로 추출하고 기존 Markdown Clean 공개 API를 유지했습니다.
- AST/21건 합성 결과/호출시점 monkeypatch, 37 Owner DAG/크기, 436개 façade 공개 함수 불변 검증을 CI에 추가했습니다.
- 실데이터·LLM 프롬프트·전체 pytest·Claude/Codex 독립 검증 전까지 **P1.5.2 OPEN**, P1.5.3 미착수. 주문/UEF/R6.2/Step5C/D/Docker 변경 없음.
- 근거: `docs/daily_patch/2026-10-10_p1_5_2_markdown_news_headlines_owner_38.md`.
- 최종 원격 검증 [38025461656](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38025461656) **SUCCESS**: Reporting 337 + Helper/UI/Owner 286 = 623 PASS. 최초 실패는 테스트의 monkeypatch 해제 누락이었으며 테스트에서만 수정했습니다.
- 증거: `docs/refactor/work_orders/evidence/P15-R2-GPT-P152-OWNER38-REMOTE-CI.md`; 로컬 독립 검증 지시서: `docs/refactor/work_orders/P15_R2_OWNER38_READONLY_LOCAL_ACCEPTANCE_CHECKLIST.md`.

---

## 2026-10-10 · P1.5.2 통합 검증·종료 게이트 003
**Stage:** Architecture and Maintainability
**Tags:** TESTING · DOCUMENTATION · SAFETY

- Owner 38에서 추가 소형 분리를 중단하고 실제 결과 동등성·검증 부채 해소를 우선합니다. 변경된 Reporting 실행 코드 없이 37개 Owner 크기와 436개 공개 ABI를 확인하는 정적 통합 스냅샷을 도입했습니다.
- 기존 원격 Reporting 회귀 외에 Reporter/Node/일별 LLM(mock)/운영 리포트 테스트를 별도 CI에서 검증하도록 확장했습니다. 정확한 결과는 CI 로그로 확정하며 로컬 실데이터 성공으로 표기하지 않습니다.
- GitHub-only 성공만으로는 P1.5.2를 종료할 수 없으며 `C:\\Agentra` 실데이터 JSON/Markdown 바이트 비교·LLM 프롬프트·전체 pytest·Claude와 Codex 독립 검증은 **NOT RUN**입니다.
- P1.5.2 OPEN, P1.5.3 미착수. 원본 동결 Q12/UEF/R6.2/Step5C/D/실거래 및 Docker 변경 없음.
- 근거: `docs/daily_patch/2026-10-10_p152_integration_closeout_003.md`, `scripts/refactor/p152_integration_acceptance.py`.
- 통합 CI [38031366650](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38031366650) **SUCCESS**: 337+286+83+3=**709 PASS** (선택된 오프라인 회귀 테스트 한정).
- 아직 façade 2,761/2,658/636 LOC이며 크기 목표 미달을 OPEN으로 유지. 실데이터/LLM/전체 테스트/독립 검증은 NOT RUN.
- 검증 근거: `docs/refactor/work_orders/evidence/P15-R2-GPT-CLOSEOUT-003-REMOTE-CI.md`; Claude/Codex 복붙 지시서: `docs/refactor/work_orders/P15_R2_CLOSEOUT_003_LOCAL_VERIFICATION_HANDOFF.md`.

---

## 2026-10-10 · P1.5.2 사전 로컬 검증을 위한 원격 검증 강화 004
**Stage:** Architecture and Maintainability
**Tags:** TESTING · DOCUMENTATION · SAFETY

- 로컬 검증은 GPT 원격 점검 후로 연기했습니다. 436개 Reporter 공개 함수의 정적 참조, 래퍼/호환성 유지 판단, 누락된 정적 참조와 동적 접근 위험을 별도 장부로 생성합니다.
- 전체 테스트 대상 중 표시된 heavy/Docker/benchmark를 제외한 오프라인 mock/DRY_RUN CI를 별도 잡으로 추가하고 JUnit 결과를 보존합니다. 원격 데이터 검증은 `C:\\Agentra` 실데이터 검증을 대체하지 않습니다.
- P1.5.2 OPEN / P1.5.3 차단. 기존 실거래·UEF·R6.2·Step5C/D·Q12 Docker 운영 코드 변경 없음.
- 근거: `docs/daily_patch/2026-10-10_p152_prelocal_remote_exhaustive_004.md`.
- 넓은 테스트 첫 실행 [38035524693](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38035524693): **2,114 PASS / 12 FAIL / 9 deselected**, 즉 전체 PASS 아님. CI의 전역 DRY_RUN 영향·이전 커밋 미확보·Linux/Windows 환경 차이·API route 검증 실패를 분리 조사 중.
- 원격 증거: `docs/refactor/work_orders/evidence/P15-R2-GPT-PRELOCAL-004-BROAD-SWEEP-INITIAL.md`. 생산 실행 코드는 건드리지 않고 CI 설정만 교정.
- 두 번째 원격 광범위 테스트 [38035913347](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38035913347): **4,607 PASS / 25 FAIL / 25 SKIP / 9 DESELECTED**, 25 실패 시 중단. 모의 LLM/과거 AST 누락은 해결됐지만 Scanner·보호된 Step5B·로컬 UEF fixture·Windows 경로 등 실패를 보존합니다.
- 전체 결과 관측을 위해 조기 종료 `--maxfail`만 해제합니다. 근거 `docs/refactor/work_orders/evidence/P15-R2-GPT-PRELOCAL-004-BROAD-SWEEP-SECOND.md`.
- 조기 중단 없는 원격 Linux 회귀 [38036400641](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38036400641): **4,919 PASS / 41 FAIL / 2 ERROR / 25 SKIP / 9 DESELECTED**. 원격 전체 PASS로 오인하지 않으며 결과를 보존합니다.
- Windows 호스팅 테스트를 추가해 경로·락·API·Scanner 문제를 OS별로 독립 확인합니다. 실거래 실행과 사용자의 실제 로컬 데이터는 사용하지 않습니다.
- 이번 사용자 요청 시작 시점 SHA `4db23efbc69c176d0901bf8f4a7dbc9f6d234bf8` 이후 변경된 파일만 ZIP으로 묶도록 범위를 교정했습니다. 원격 분석 증거 `docs/refactor/work_orders/evidence/P15-R2-GPT-PRELOCAL-004-BROAD-SWEEP-EXHAUSTIVE.md`.
- GitHub 호스팅 Windows 테스트 [38036845579](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38036845579): 락·경로·UI·subprocess **123 PASS**, API/Scanner 그룹 **11 PASS / 2 FAIL**. 후자 두 건은 Linux/Windows 모두 재현, 리팩토링 범위 밖의 미해결 검증 항목으로 보존합니다.
- 광범위 Linux/Windows 테스트는 원격 진단용 수동 실행으로 전환합니다. 자동 Reporting 핵심 회귀 PASS와 광범위 진단 FAIL을 혼동하지 않습니다.
- Windows 증거: `docs/refactor/work_orders/evidence/P15-R2-GPT-PRELOCAL-004-WINDOWS-HOSTED.md`; 로컬 실데이터·전체 native 검증과 별도 사용자 최종승인은 NOT RUN.

---

## 2026-10-10 · P1.5.2 빠른 로컬 동등성 검증 도구 005
**Stage:** Architecture and Maintainability
**Tags:** TESTING · DOCUMENTATION · SAFETY

- 이미 안전하게 복사해 둔 보고서 디렉터리 두 개의 Markdown/JSON/JSONL 해시·바이트를 비교하고, JSON 포맷만 다르더라도 바이트 차이를 FAIL로 기록하는 로컬 검증 도구를 추가했습니다.
- 선택된 JSON/JSONL LLM 캡처의 누락 및 불일치 확인, 잘못된 동일 경로/빈 폴더/심볼릭 링크 거부, 민감한 원문 대신 해시만 출력하도록 설계했습니다.
- 실제 거래 실행·LLM 호출 또는 로컬 증거 자동 수집은 하지 않습니다. Codex 일괄 검증 → Claude 독립 감사를 위한 빠른 인계 문서가 함께 제공됩니다.
- 근거: `docs/daily_patch/2026-10-10_p152_fast_parity_kit_005.md`, `docs/refactor/work_orders/P15_R2_FAST_LOCAL_PARITY_KIT.md`. P1.5.2 OPEN, P1.5.3 미착수.
## 2026-10-12 · P1.5.2 Codex Local Acceptance
**Stage:** Architecture and Maintainability
**Tags:** TESTING · DOCUMENTATION · SAFETY

- Windows Owner parity source decoding now uses explicit UTF-8; 38 AST-preserved functions across 26 bounded Owners passed.
- P1.5.2 selected tests: **295 passed / 1 skipped**, but the production-path write audit fired. Full pytest is **NOT PASS** because FastAPI is unavailable during collection; real report/LLM snapshot parity is **NOT RUN** because no independent frozen copies were available.
- Facade sizes remain **2,761 / 2,658 / 636 LOC** and OPEN. No trade execution, live LLM, Docker, Q12, API/Scanner/UEF/Step5B, or runtime source changes.
- Evidence: `docs/refactor/work_orders/evidence/P15-R2-CODEX-LOCAL-ACCEPTANCE-2026-10-12.md`.
## 2026-10-12 · P1.5.2 Isolated Clone Acceptance
**Stage:** Architecture and Maintainability
**Tags:** TESTING · DOCUMENTATION · SAFETY

- History-preserving clone with project venv Python 3.14.2, pytest 9.1.1 and FastAPI 0.142.2: P1.5.2 selection **295 passed / 1 skipped**, with zero clone write-audit markers.
- Full pytest no longer has the prior FastAPI collection error, but the first failure is the out-of-scope API isolation test; an unrestricted run terminated at 50% without a complete summary, so it is not accepted as PASS.
- No actual frozen report/LLM captures exist under `C:\\AgentraEvidence`; parity remains **BLOCKED / NOT RUN**. Façades remain **KEEP/DEFER** at 2,761 / 2,658 / 636 LOC.
- Evidence: `docs/refactor/work_orders/evidence/P15-R2-CODEX-CLONE-ACCEPTANCE-2026-10-12.md`.

---

## 2026-10-12 · P1.5.2 R3 Git-first / Agentra Claude 구현·Codex 감사
**Stage:** Architecture and Maintainability
**Tags:** DOCUMENTATION · WORKFLOW · SAFETY

- Agentra의 공식 역할은 **Claude 구현 → Codex 독립 감사 → GPT/사용자 승인**입니다. Agentco만 구현/감사가 반대 순서입니다.
- 기존 CURRENT 전문은 archive에 안전하게 보존하고, 짧은 CURRENT/공용 규칙/단일 R3 지시서를 통해 대형 façade 3개(636 / 2,658 / 2,761줄)를 순서대로 분리할 작업을 정의했습니다.
- R3에서만 격리된 feature worktree 1개를 허용하며, 독립 검증 전 원본 C:\\Agentra, refactor/p1.5, main은 건드리지 않습니다. 436 ABI, monkeypatch, LLM/보고서 동등성 필수.
- UI 패치노트 JSON/MD 연동과 실제 푸시 diff 기준 변경 파일 ZIP 생성을 유지합니다. 전체 pytest는 여전히 미완료, 실데이터·LLM parity는 NOT RUN, P1.5.2 OPEN / P1.5.3 미착수입니다.
- 근거: `docs/daily_patch/2026-10-12_p152_r3_claude_codex_git_first.md`, `docs/refactor/work_orders/P15_R3_FACADE_DECOMPOSITION_001.md`.

- Git 작업지시 CI 게이트의 구식 R2 감사 전용 검사를 R3의 Claude 구현·Codex 감사 지시서/보존 아카이브 검사로 교체했습니다.

- P1.5.2 Reporting authority test preserves its path guard but explicitly permits only the two agent instruction files `AGENTS.md` and `CLAUDE.md` as root documentation edits.
- CI emits an additional task-baseline ZIP for precisely the paths changed since `341cedc`, alongside the existing push-only ZIP.

- 원격 acceptance inventory 역시 루트 문서 `AGENTS.md`, `CLAUDE.md` 두 개만 허용하는 정확한 allowlist를 사용합니다. 다른 루트 실행/거래 파일 변경은 계속 차단합니다.

## 2026-10-12 · P1.5.2 R3 호환성 우선 façade 분해
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · SAFETY

- Story/Markdown/AI façade의 구현 본문 57개(3/25/29)를 `libs/reporting/**/…_r3_parts/bodies_*.py` 11개 Owner(최대 275줄)로 이동했습니다. façade LOC는 636/2,658/2,761 → 562/1,891/1,958입니다.
- 436개 public `def`, 시그니처, 데코레이터는 그대로이며, 이동한 본문은 AST가 동일하고 기존 façade 전역은 주입된 `facade` 모듈에서 호출 시점에 이름으로 읽어 monkeypatch 의미를 보존합니다. `__getattr__`/exec/일괄 re-export는 사용하지 않았습니다.
- AI provider/router/prompt/retry/timeout/fallback/merge 경로는 이동하지 않았습니다. façade ≤350줄 목표는 SIZE_DEFERRED입니다.
- 집중 오프라인 Reporting 테스트 810 passed / 1 skipped, 운영 경로 쓰기 감사 0. 실제 snapshot·LLM parity는 NOT RUN, 전체 pytest 미완료, P1.5.2 OPEN, P1.5.3 미착수, Codex 독립 감사 대기.
- 근거: `docs/refactor/work_orders/evidence/P15-R3-CLAUDE-IMPLEMENTATION-001.md`, `docs/daily_patch/2026-10-12_p1_5_2_r3_compat_first_decomposition.md`.

## 2026-10-12 · P1.5.2 R3 Codex 독립 감사 작업지시
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · SAFETY

- `CURRENT.md`의 활성 작업을 Codex 독립 감사로 전환했습니다. 감사 SHA `e41d42d` / 런타임 `321eabb`; 구현 변경과 병합은 없습니다.
- ABI 436개, façade 전역 바인딩 시점, numbered Owner 구조, Story Owner LOC 불일치, 격리 합성 입력 차분과 쓰기 감사를 확인합니다.
- 실제 자료·LLM parity와 전체 pytest는 여전히 미완료. P1.5.2 OPEN / P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/P15_R3_CODEX_INDEPENDENT_AUDIT_001.md`, `docs/daily_patch/2026-10-12_p152_r3_codex_audit_handoff.md`.

## 2026-10-12 · P1.5.2 R3 Codex PASS_WITH_FINDINGS 및 증거 보완
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · SAFETY

- 사용자가 전달한 Codex 독립 감사: **PASS_WITH_FINDINGS**, 197 PASS / 1 SKIP, 격리 clone 쓰기 0. 원시 감사 로그는 Git에 아직 없음.
- façade SIZE_DEFERRED(562/1,891/1,958); 실제 Markdown/JSON/LLM 동등성 BLOCKED·NOT RUN, 전체 pytest NOT RUN. P1.5.2 OPEN, 병합·P1.5.3 미승인.
- 합성 before/after 차분, façade 전역 바인딩, Story LOC 및 Owner 책임성 검토를 [증거 보완 작업](docs/refactor/work_orders/P15_R3_ACCEPTANCE_EVIDENCE_002.md)으로 전환. 코드 변경 없음.
- 근거: `docs/refactor/work_orders/evidence/P15-R3-CODEX-INDEPENDENT-001.md`, `docs/daily_patch/2026-10-12_p152_r3_codex_pass_with_findings.md`.

## 2026-10-12 · 리팩터링 브랜치 단일화 규칙
**Stage:** Architecture and Operations
**Tags:** REFACTOR · SAFETY · DOCUMENTATION

- 사용자 지시: 개발 브랜치는 `refactor/p1.5` **하나만** 유지합니다. feature/task/ZIP 추가 브랜치 금지.
- R3 기존 feature 작업 이력을 `refactor/p1.5`로 안전하게 fast-forward(`ba6618d` → `05dbb5f`)했습니다. 이는 WIP 보존이지 P1.5.2 완료 승인·main 병합·라이브 반영이 아닙니다.
- 구 feature 원격 ref는 이력 포함 및 로컬 워크트리 정합성 확인 후 삭제하도록 활성 작업에 명시했습니다. 보존해야 할 로컬 변경은 강제 정리하지 않습니다.
- P1.5.2 OPEN, P1.5.3 미승인.
- 근거: `docs/daily_patch/2026-10-12_p152_single_refactor_branch_policy.md`, `docs/refactor/work_orders/CURRENT.md`.

## 2026-10-12 · P1.5.2 R3 수용 증거 002
**Stage:** Architecture and Maintainability
**Tags:** TESTING · REPORTING · SAFETY

- 동일 fixture 625개 테스트에서 이동한 57개 함수의 호출 47,092건을 baseline과 비교해 47,091건이 동일했고, 1건은 wall-clock latency만 달랐습니다(두 함수는 직접 357 케이스로 비교).
- Seam 점검: 호출 전 패치는 57/57 동일, 호출 도중 콜백 패치는 36개에서 달랐습니다(호출 진입 시 façade 전역 바인딩). 결정 대기.
- 전체 pytest 1회 완료: 35 failed / 5115 passed / 2 errors, 실패 노드는 모두 baseline과 동일한 범위 밖(UEF/Step5B/Scanner/API) 항목이며 `data/logs/controlled_mock_lanes` 쓰기 격리 이슈 1건을 기록했습니다.
- Story Owner 줄 수를 102로 정정, 실제 snapshot·LLM parity는 계속 BLOCKED/NOT RUN. P1.5.2 OPEN, P1.5.3 미착수.
- 근거: `docs/refactor/work_orders/evidence/P15-R3-CLAUDE-ACCEPTANCE-EVIDENCE-002.md`.

## 2026-10-12 · P1.5.2 R3 호출 시점 호환성 복구 결정
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · SAFETY

- Claude 독립 합성 차분은 47,091/47,092건 일치(1건 타이밍 필드) 및 직접 케이스 357건. 호출 이전 패치 57/57 동일하지만 호출 중 전역 패치 36/57 차이가 발생해 **엄격한 호환성 FAIL**로 판정했습니다.
- 호출 진입 시점 고정 바인딩을 수용하지 않고 기존 **실제 사용 시점 전역 조회**를 보존하는 제한적 수정을 승인했습니다. `refactor/p1.5` 단일 브랜치만 사용하며 Codex 독립 감사를 거칩니다.
- 이전 전체 pytest 5,115 PASS / 35 FAIL / 2 ERROR / 27 SKIP / 9 deselected (baseline 동일 실패 37건). `controlled_mock_lanes` 테스트 쓰기 이슈와 numbered Owner 책임 구분은 별도 OPEN.
- 실보고서/LLM parity BLOCKED, façade 크기 SIZE_DEFERRED, P1.5.2 OPEN, P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/P15_R3_SEAM_RESTORATION_003.md`, `docs/daily_patch/2026-10-12_p152_r3_seam_restoration_decision.md`.

## 2026-10-12 · P1.5.2 R3 사용 시점(use-time) seam 복원
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · SAFETY

- 이동한 57개 본문이 호출 진입 시 façade 전역을 캡처하던 방식을 제거하고, 각 전역을 원래 사용 위치에서 `facade.NAME`으로 조회하도록 복원했습니다(507개 지점).
- 호출 도중 monkeypatch seam이 baseline과 57/57 동일해졌고(이전 36개 불일치), 호출 전 패치 57/57, 직접 357 케이스, 기록된 호출 47,091/47,092가 동일합니다(1건은 wall-clock latency).
- 집중 오프라인 Reporting 테스트 925 passed / 1 skipped, 운영 경로 쓰기 0. 436 ABI·import DAG·Owner ≤350 불변.
- 폐기 대상 feature 브랜치 `feature/p152-facades-r3`는 조상/클린 검증 후 정리했습니다. 실제 snapshot·LLM parity BLOCKED, façade 크기 SIZE_DEFERRED, `controlled_mock_lanes` 쓰기 격리 이슈 OPEN, P1.5.2 OPEN / P1.5.3 미착수.

## 2026-10-12 · P1.5.2 R3 Codex 독립 감사 인계
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · TESTING

- `refactor/p1.5`의 `6512201`을 Codex 감사 대상으로 고정했습니다. feature 브랜치는 삭제됐고 `main` 변경은 없습니다.
- Claude 검증 보고: 호출 전·중 seam 57/57 동등, 925 PASS / 1 SKIP, 집중 테스트 쓰기 0. 독립 감사 전으로 최종 PASS는 아닙니다.
- 기존 전체 테스트의 쓰기 격리 이슈, 실자료·LLM parity BLOCKED, façade SIZE_DEFERRED, Owner 응집도 부채는 그대로 OPEN입니다.
- 근거: `docs/refactor/work_orders/P15_R3_CODEX_SEAM_AUDIT_004.md`, `docs/daily_patch/2026-10-12_p152_r3_codex_seam_audit_handoff.md`.

## 2026-10-12 · P1.5.2 R3 Codex seam 감사 결과
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · TESTING · SAFETY

- Codex 독립 감사 결과 PASS_WITH_FINDINGS: 298 PASS, seam 검증 357건 / 함수 57개. 감사 대상 코드 SHA `6512201`.
- 실행 경로 오류가 있던 비교 결과는 무효 처리했으며, 감사 중 관찰된 쓰기 이벤트의 귀속은 확인되지 않았습니다.
- 실보고서/LLM parity는 NOT RUN, 기존 전체 테스트 격리 결함 OPEN. P1.5.2 OPEN / P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/evidence/P15-R3-CODEX-SEAM-AUDIT-004.md`, `docs/daily_patch/2026-10-12_p152_r3_audit_closeout.md`.

## 2026-10-12 · P1.5.2 R3 감사 종결 005 — live-root 실수 실행 로그 분석
**Stage:** Architecture and Maintainability
**Tags:** DOCUMENTATION · SAFETY

- 수리 전 비교 테스트가 live `C:\Agentra`에서 실행됐으나 대상 테스트 파일이 없어 **수집된 테스트 0개**였고, 테스트 코드로 인한 쓰기 가능성은 배제됩니다(conftest 훅만 실행).
- `events.jsonl`, `reports/canonical|llm` 변경의 쓰기 주체는 PID 정보가 없어 **UNKNOWN**이며 live 루프와 일치하나 입증되지는 않았습니다. live 프로브/재실행은 하지 않았습니다.
- 확인된 영향은 읽기 전용 스캔(약 10GB ledger SHA-256 읽기 포함)뿐이며 비교 증거에서는 제외합니다. 원인은 작업 디렉터리 의존 도구이고, `--root` 가드는 별도 승인 과제로 권고합니다.
- 실데이터/LLM parity BLOCKED, 전체 pytest 0-write와 `controlled_mock_lanes` 격리 OPEN, façade SIZE_DEFERRED, P1.5.2 OPEN / P1.5.3 미착수.

## 2026-10-12 · P1.5.2 R3 감사 도구 실행경로 보호 작업 시작
**Stage:** Safety and Test Infrastructure
**Tags:** SAFETY · TESTING · REFACTOR

- 실수 실행은 live 루트에서 테스트 0건 수집; 관측된 기록 파일 변경의 쓰기 주체는 UNKNOWN으로 유지합니다.
- R3 오프라인 감사 스크립트 2개에만 `--root`/환경변수 명시, live 실행 차단, 결과 경로 격리 및 bytecode 비활성화를 추가하도록 작업지시했습니다.
- 독립 clone에서 집중 테스트 후 Codex 감사. 런타임 변경·전체 pytest·main 병합·신규 브랜치 금지. P1.5.2 OPEN / P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/P15_R3_AUDIT_HARNESS_GUARDS_006.md`, `docs/daily_patch/2026-10-12_p152_r3_harness_guard_task_activation.md`.

## 2026-10-12 · P1.5.2 R3 감사 하네스 Guard 006
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY

- seam-challenge 스크립트와 call-recorder 플러그인이 명시적 절대 경로의 격리 Git clone root, cwd 일치, `PYTHONDONTWRITEBYTECODE=1`을 만족하지 않으면 Reporting import·pytest 수집·출력 열기 전에 거부합니다.
- 라이브 `C:\Agentra`와 그 하위/상위 경로는 항상 거부하며(대소문자·슬래시·긴 경로 접두사·`..`·8.3 별칭·심볼릭 링크/junction 포함) 라이브 경로는 문자열 검사만 하고 stat/실행하지 않습니다. 출력은 새 파일만 허용하고 입력 덮어쓰기·clone 내부 출력은 거부합니다.
- 가드 테스트 61개 통과, 안전 smoke 결과는 baseline seam 결과와 동일(357 케이스/57 함수), 회귀 656 passed / 1 skipped, 운영 경로 쓰기 0. 런타임 코드 변경 없음.
- 미해결: `controlled_mock_lanes` 쓰기 격리, 실제 snapshot·LLM parity BLOCKED, façade SIZE_DEFERRED. P1.5.2 OPEN, P1.5.3 미착수.

## 2026-10-12 · P1.5.2 R3 Guard 독립 감사 및 Façade 추가 축소 계획
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · TESTING

- Guard 006 `f6cc71b` 제출 검증 완료. Claude 보고 가드 61 PASS, 회귀 656 PASS / 1 SKIP, 격리 seam 357건/57 함수. Codex 독립 감사 007 대기.
- 현재 Reporting façade 물리 LOC: AI 1,958 / Markdown 1,891 / Story 562 = 4,411줄(최초 18,743줄). 기존 선언 436개 유지.
- `SIZE_DEFERRED`는 계속 줄일 대상이며 영구 면제 아님. 감사 후 LOC 008에서 함수별 책임/실제 소비자/전역 패치 호환성을 검증하고 **안전하게 줄일 수 있는 부분을 최대한 추출**할 계획.
- 실보고서·LLM parity BLOCKED, 테스트 격리 부채 OPEN. P1.5.2 OPEN, P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/P15_R3_CODEX_GUARD_AUDIT_007.md`, `docs/refactor/work_orders/P15_R3_FACADE_LOC_MAX_REDUCTION_008.md`.

## 2026-10-12 · P1.5.2 Guard 007 수용 및 LOC 008 활성화
**Stage:** Architecture and Maintainability
**Tags:** SAFETY · TESTING · REPORTING · REFACTOR

- Codex Guard 007 독립 감사 **PASS_WITH_FINDINGS**: 61 PASS / 0 SKIP, 오프라인 seam 357건 / 57함수, 격리 clone 쓰기 0. `cache_dir` 설정 경고 1건은 비차단이며 필수 수정 없음.
- `refactor/p1.5` 단일 개발 브랜치 유지, `main` 및 라이브 영향 없음. 사용자 방향에 맞춰 Reporting façade **안전하게 줄일 수 있는 부분 최대 축소**를 위한 LOC 008 구현 작업 활성화.
- 현재 façade AI 1,958 / Markdown 1,891 / Story 562, 총 4,411 LOC. 436 ABI 및 호출 중 façade 전역 패치 호환성을 유지하면서 함수별 책임·호출자 분석 후 하나의 응집된 구현 영역을 추출하고 Codex 감사를 받을 예정.
- 실데이터/LLM parity BLOCKED, `controlled_mock_lanes` 쓰기 격리 OPEN, P1.5.2 OPEN / P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/evidence/P15-R3-CODEX-GUARD-AUDIT-007.md`, `docs/refactor/work_orders/P15_R3_FACADE_LOC_MAX_REDUCTION_008.md`, `docs/daily_patch/2026-10-12_p152_guard007_pass_loc008_activation.md`.

## 2026-10-12 · P1.5.2 R3 façade LOC 축소 008
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR

- 남은 façade 함수를 전수 측정한 결과 계약이 없는 가장 큰 덩어리는 Markdown-clean 의존성 맵 factory 9개(242줄)였고, 이를 `markdown_clean_dependency_maps.py`(268줄)로 이동했습니다. Markdown façade는 1,891 → 1,678줄(-213)입니다.
- 436개 def 이름/시그니처는 그대로이며 각 맵은 주입된 façade 모듈의 `facade.NAME`을 호출 시점에 조회해 원래 dict literal과 동일하게 현재 전역을 반영합니다.
- baseline 대비 기록 호출 96,565건 중 96,564건 동일(1건은 wall-clock latency), 맵 9개 모두 실행, 집중 회귀 1,041 passed / 1 skipped, 운영 경로 쓰기 0.
- façade 합계 4,198줄(원본 18,743). 실제 snapshot·LLM parity BLOCKED, 크기 SIZE_DEFERRED 유지, P1.5.2 OPEN / P1.5.3 미착수, Codex 감사 대기.

## 2026-10-12 · P1.5.2 LOC 008 제출 및 Codex 독립 감사 인계
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · TESTING

- Claude 구현 `3d85085`: Markdown 의존성 맵 factory 9개를 268-LOC 책임형 Owner로 이동. façade **1,891→1,678 LOC(-213)**, 3개 합계 **4,411→4,198 LOC**. 기존 436 함수 계약 유지.
- 66개 moved-body(57+9) 게이트 확장; Claude 보고 집중 **1,041 PASS/1 SKIP**, 합성 호출 **96,564/96,565 동일**(차이 1건은 latency), 운영 쓰기 0. Codex 재검증 전 최종 PASS 아님.
- 남은 LOC 후보: Markdown 서술/번역(-93 추정), AI·Story deps(각 -75 추정), memory/policy(-65), 숫자 포맷(-55). LOC 010은 현재 *대기*이며 감사 후 활성화 판단.
- 실보고서·LLM parity BLOCKED, test-write 격리 OPEN, façade SIZE_DEFERRED와 Owner 응집도 OPEN, P1.5.2 OPEN/P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/P15_R3_CODEX_LOC_008_AUDIT_009.md`, `docs/refactor/work_orders/P15_R3_FACADE_LOC_NEXT_CANDIDATES_010.md`, `docs/daily_patch/2026-10-12_p152_loc008_codex_handoff.md`.

## 2026-10-12 · P1.5.2 LOC 008 Codex 감사 수용 및 LOC 010 활성화
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · TESTING

- 독립 Codex 감사 결과 **PASS_WITH_FINDINGS** (`3d85085`): 맵 호출시점 55 PASS, 66 moved-body·ABI·패치노트 핵심 359 PASS, p152 선택군 711 PASS/1 SKIP, 운영 쓰기 0. `cache_dir` 경고 1건은 비차단. 독립 검증 범위와 Claude의 1,041건 회귀군은 다름.
- Markdown façade 1,891→1,678 LOC **-213** 확인, 새 책임형 Owner 268 LOC, 436 API 계약/66 symbol 보호 유지. 현재 3개 façade 합계 4,198 LOC.
- 다음 **LOC 010**에 책임형 코드 한 묶음의 실질적 추가 축소를 승인. 사용자 원칙대로 SIZE_DEFERRED는 영구 면제가 아니며, 함수별 소비자/패치 시점 호환성을 증명하면서 안전한 범위를 최대한 추출.
- 실보고서/LLM parity BLOCKED, `controlled_mock_lanes` 쓰기 격리·Owner 응집도·나머지 façade 크기 OPEN. P1.5.2 OPEN/P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/evidence/P15-R3-CODEX-LOC-008-AUDIT-009.md`, `docs/refactor/work_orders/P15_R3_FACADE_LOC_NEXT_CANDIDATES_010.md`, `docs/daily_patch/2026-10-12_p152_loc008_audit_accepted_loc010_activated.md`.

## 2026-10-12 · P1.5.2 R3 façade LOC 축소 010
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR

- 후보를 재측정해 가장 큰 안전 순감을 낸 Markdown-clean 운영자 서술 builder 20개(문장·번역 helper, entry/guard/timeline bullet)를 `markdown_clean_operator_narrative.py`(264줄)로 이동했습니다. Markdown façade는 1,678 → 1,527줄(-151)입니다.
- 436개 def 이름/시그니처는 유지되고 이동한 본문은 `facade.NAME`을 사용 위치에서 조회하므로 호출 중 monkeypatch도 원래와 동일하게 반영됩니다.
- baseline 대비 기록 호출 99,690건 중 99,689건 동일(1건은 wall-clock latency), 20개 모두 실행, 집중 회귀 1,142 passed / 1 skipped, 운영 경로 쓰기 0.
- façade 합계 4,047줄(원본 18,743). 실제 snapshot·LLM parity BLOCKED, 크기 SIZE_DEFERRED 유지, P1.5.2 OPEN / P1.5.3 미착수, Codex 감사 대기.

## 2026-10-12 · P1.5.2 LOC 010 제출 및 Codex 독립 감사 011
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · REFACTOR · TESTING

- Claude `b0cfc2b`: Markdown 운영자 서술·번역·entry/guard/timeline 표시용 함수 20개를 책임형 Owner(264 LOC)로 이동. façade **1,678→1,527 LOC(−151)**, 3개 façade 합계 **4,198→4,047**. 저장소 전체 코드 151줄 삭제와는 다름.
- 436개 함수 계약/86개 이동 심볼 호환성 유지 주장. Claude 집중 테스트 1,142 PASS/1 SKIP, 합성 호출 99,689/99,690 동일(1건 실행시간), 운영 쓰기 0 — **Codex 독립 감사 전**.
- Codex 감사 011을 활성화하고 다음 AI/Story dependency map 등 LOC 012는 대기로 유지. `SIZE_DEFERRED`는 미완료 부채.
- 실제 frozen report/LLM parity BLOCKED, `controlled_mock_lanes` 쓰기 격리 OPEN, Owner 응집도 OPEN. P1.5.2 OPEN / P1.5.3 미승인.
- 근거: `docs/refactor/work_orders/P15_R3_CODEX_LOC_010_AUDIT_011.md`, `docs/refactor/work_orders/P15_R3_FACADE_LOC_NEXT_CANDIDATES_012.md`, `docs/daily_patch/2026-10-12_p152_loc010_codex_handoff.md`.

## 2026-10-12 · P1.5 전체 1차 분해 Fast Track 승인
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · TESTING · WORKFLOW

- 사용자 결정: P1.5.2~1.5.11 **전체 1차 구조 분해를 우선 빠르게 수행**, 남은 대형 파일과 호환 래퍼 부채는 이후 2차 집중 정리. 100~200줄마다 별도 감사하던 절차를 단계별 집중 테스트 + Wave 경계 Codex 독립 감사로 개편.
- Wave A Reporting+Operator UI, B Strategist+Scanner+Monitor, C Commander+Naming+Executor 안전한 관측 분리+Wrapper, D 전체 pytest/Docker/UEF/최종 Freeze. P1.6 런타임 평가는 P1.5 Freeze 이후.
- Codex LOC010 PASS_WITH_FINDINGS 수용(812 PASS/1 SKIP, 핵심 460 PASS, 436 ABI/86 이동 심볼, 쓰기 0). 실보고서/LLM parity BLOCKED, `controlled_mock_lanes` 격리 OPEN; `FIRST_PASS_WITH_DEBT`는 최종 PASS가 아님.
- `main` 및 live 변경·실거래·추가 브랜치 없음. 패치노트 이전 011 소스 링크 오류도 바로잡음.
- 근거: `docs/refactor/P15_FAST_TRACK_FIRST_PASS_2026_10_12.md`, `docs/refactor/work_orders/P15_FAST_TRACK_WAVE_A_013.md`, `docs/daily_patch/2026-10-12_p15_fast_track_first_pass_approved.md`.
- 작업지시서·공통규칙의 Fast Track 정책 링크는 실제 상대 경로 `../P15_FAST_TRACK_FIRST_PASS_2026_10_12.md`로 정정했습니다.

## 2026-10-12 · P1.5 Fast Track Wave A (Reporting 잔여 + P1.5.3 Operator UI/Brief 1차 분해)
**Stage:** Architecture and Maintainability
**Tags:** REPORTING · OPERATOR_UI · REFACTOR · WORKFLOW

- A1 Reporting: 의존성 맵과 결정적 도메인 helper 55개를 책임명 Owner 10개로 이동했고 façade 합계는 4,047 → 3,479줄입니다(AI 1,656 / Markdown 1,325 / Story 498). 436 ABI 유지.
- A2 P1.5.3: Operator UI/Brief의 IO 없는 본문 136개를 Owner 22개로 이동했습니다. `data_access_core.py` 6,871 → 4,594, `operator_period_summary.py` 3,210 → 1,195, `operator_visibility.py` 1,879 → 1,520(-4,651줄). 공개 def/시그니처와 use-time monkeypatch seam은 그대로입니다.
- 영속화·IO·LLM 호출 함수와 350줄 초과 단일 함수는 이동하지 않고 2차 부채로 기록했습니다.
- 검증: 이동 본문 AST 동일성·use-time oracle·ABI, baseline 대비 호출 비교(Reporting 150,692/150,693 동일, Operator UI 결과 동일·`prompt_hash`만 비결정적), 통합 집중 회귀 2,374 passed / 1 skipped / 기존 API 실패 1건, 운영 경로 쓰기 0.
- 운영 규칙: 책임 단위 일괄 추출, 하위 시스템별 게이트, ZIP·다운로드 산출물 금지(Git만 산출물)를 Git 문서에 반영했습니다. 실제 snapshot·LLM parity BLOCKED, 전체 pytest·`controlled_mock_lanes` OPEN, P1.5.2 최종 OPEN, Codex Wave A 감사 대기.

## 2026-10-12 · P1.5 Fast Track Wave A 종료
**Stage:** Architecture and Maintainability
**Tags:** TESTING · WORKFLOW · SAFETY

- Codex Wave A 판정 PASS_WITH_FINDINGS를 기록했습니다(집중 1,455 PASS / 정책 FAIL 1, A2 706 PASS, 운영 쓰기 0).
- R2 시대 범위 가드를 Wave A 종료 커밋에 고정하고 `apps/operator_ui/`를 명시 허용했으며 apps/api·graphs·conftest.py·실행 권한 경로는 계속 금지합니다.
- GitHub Actions는 Fast Track 활성 작업 계약 검사로 교체하고 모든 ZIP 생성·업로드 단계를 삭제했습니다(JSON inventory·JUnit·ABI·Owner·patch-note·오프라인 회귀 유지).
- 실제 frozen 보고서/LLM parity BLOCKED, `controlled_mock_lanes`·전체 pytest OPEN. Wave A는 FIRST_PASS_WITH_DEBT이며 FINAL_ACCEPTED가 아닙니다.

## 2026-10-12 · P1.5 Fast Track Wave B (Strategist · Scanner · Monitor 1차 분해)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · SAFETY · WORKFLOW

- Wave A 종료: 범위 가드·P1.5.2 inventory를 Wave A 종료 커밋에 고정하고 CI를 Fast Track 활성 계약 검사로 교체했으며 ZIP 단계를 모두 삭제했습니다(CI 성공 2504d70, Codex Wave A PASS_WITH_FINDINGS 기록).
- B1 Strategist: `strategist_node.py` 8,878 → 5,144줄, 본문 104개를 `libs/runtime/strategist/{context,policy,llm,output}` Owner 22개로 이동. LLM 호출·prompt·repair·token budget·call-kind 경로는 노드에 그대로 유지했습니다.
- B2 Scanner: `scanner_node.py` 4,178 → 2,652줄, 본문 40개를 `libs/runtime/scanner` Owner 11개로 이동(순위·tie-break·soft guidance 의미 불변).
- B3 Monitor: helper 2개만 이동하고 `monitor_node`(2,634줄)·`_evaluate_monitor_entry_candidate`(658줄)는 2차 부채로 남겼습니다(intent-only 역할 불변).
- 검증: 이동 본문 AST 동일성·use-time oracle, 범위/권한 경계 테스트, consumer 620개 baseline=feature 동일, 동시 실행 호출 비교에서 baseline 안정 레코드 16,792건 중 차이 0(라이브 시장 데이터 기반 672건은 비결정적), 운영 쓰기 0. 실제 snapshot·LLM parity BLOCKED, 전체 pytest·Docker·UEF는 Wave D, Codex Wave B 감사 대기.

## 2026-10-12 · P1.5 Fast Track Wave C (Commander · 런타임 명칭 · Executor read model · wrapper 분류)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · SAFETY · WORKFLOW

- C1 Commander: `graphs/commander_runtime.py` 6,297 → 4,709줄, 순수 정책·projection 본문 48개를 `libs/runtime/commander` Owner 8개로 이동(그래프 순서·fast path·state key·runtime 소유 함수는 유지, 새 LLM 역할 없음).
- C2 명칭: 기존 이름은 그대로 두고 canonical 모듈/CLI(`live_cycle`, `runtime_tick`, `eod_report`, `entrypoints.live_loop`, `run_live_loop.py`)와 `LIVE_LOOP_LOCK_*` → `M13_LIVE_LOCK_*` 우선순위 resolver를 추가했습니다(lock 경로·state key 불변).
- C3 Executor: 관측/read-model 함수 3개만 `libs/execution/executor_observability.py`로 이동. guard·readiness·admission·CAS·UNKNOWN·broker 경로는 baseline과 AST 동일, 나머지는 실제 fixture 부재로 SAFETY_BLOCKED.
- C4 wrapper: 분류만 수행(DEFINITE_DEAD 0, Reporting ABI 330 UNKNOWN, 중복 본문 114그룹, 삭제·통합 없음).
- 검증: 범위/권한 경계·AST 동일성·alias 테스트·consumer 회귀, 동시 실행 호출 비교에서 baseline 안정 레코드 차이 0, 운영 쓰기 0. Codex Wave B PASS_WITH_FINDINGS 기록, 실제 snapshot·LLM parity BLOCKED, 전체 pytest·Docker·UEF는 Wave D, Codex Wave C 감사 대기.

## 2026-10-13 · P1.5 Seven-Agent 목표 트리 및 Reporter 실제 구조 기준 고정
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · DOCUMENTATION · REPORTING

- GPT가 `docs/refactor/P15_CANONICAL_TARGET_TREE_AND_REPORTER_ASIS_2026_10_13.md`에 7-Agent + Reporter + Operator UI 최종 목표 트리와 현재 Git의 실제 경로를 `[E]`/`[P]`/`[L]`로 구분해 기록했습니다. GPT 2차 마스터 설계에도 연결했습니다.
- Reporter는 `reporter_node.py → intraday_trade_reports.generate_intraday_trade_artifacts` 연결이 확인됐고, 실제 bundle/queue/process/IO 핵심 구현은 약 1,850줄로 남아 있습니다. Reporter는 `FIRST_PASS_WITH_DEBT`로 분류합니다.
- `libs/reporting/` 아래에는 Reporter 거래 리포트뿐 아니라 Q10/Q12 연구, Alpha Board, UEF 평가도 함께 있습니다. 466개 Python 파일을 모두 Reporter 에이전트 코드로 분류하지 않습니다.
- Wave A의 Reporting 55개 함수→10 Owner 이동은 실제 반영됐지만, 공개 façade 436개 ABI 중 330개는 소비자 증거가 UNKNOWN이고, 실제 frozen report/LLM parity는 BLOCKED/NOT RUN입니다.
- 이번 변경은 아키텍처 문서·UI 패치노트만 포함합니다. Reporter 코드, Broker, Supervisor/Executor, main, live runtime과 배포는 변경하지 않았습니다.

---

## 2026-10-13 · P1.5 Wave D 이전 Reporter 포함 전체 구조 정리
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · WORKFLOW

- 2차 대량 모듈화(S1~S6)와 Codex 중간 통합감사 이후 실제 코드 전체를 다시 검사합니다.
- Reporter도 포함해 남은 거대 함수, 중복 Owner, 번호형 Owner, 공개 Facade 및 최소권한 부채를 GPT가 설계하고 Claude가 추가 대량 모듈화를 반복합니다.
- Reporter `intraday_trade_reports.py`와 AI·Markdown·Story 경로는 실제 소비자 및 부작용 근거를 확인한 범위에서만 분해합니다.
- 전체 구조감사 완료 이후 Wave D에서 실데이터 Reporter/LLM, Executor, UEF, Docker, 전체 pytest를 최종 검증합니다.
- 이 변경은 작업 순서의 문서 기록이며 실거래·코드·권한 변경이 아닙니다.

## 2026-10-13 · P1.5 Second Pass (Monitor · Scanner · Commander · Operator Brief · Strategist 함수 내부 일괄 분해)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · SAFETY · TESTING

- 거대 비-Reporter 함수 13개를 dataflow로 증명된 extract-method로 분해: 본문 120개(6,533줄)를 최소권한 Owner 45개(모두 350줄 이하)로 이동했습니다. 상태 쓰기·이벤트·artifact·provider/LLM 호출·trigger 우선순위·정규 scanner 순위 구간은 원래 함수에 그대로 남았습니다.
- Monitor: monitor_node 2,634→1,107, evaluate_intraday_entry_signal 1,229→458, evaluate_exit_policy 1,234→673. Commander: _build_commander_decision 857→195. Operator Brief: sections/input/markdown 846/426/652→341/314/351(_load_operator_brief LLM 조정자 불변). Strategist: LLM 경계 밖 1,705→1,216(SAFETY_LOCK 함수 불변). Supervisor/Executor는 SAFETY_LOCK 유지.
- Owner는 import·환경·시계 읽기가 없고 caller의 fresh 지역 컨테이너만 변경하며 모듈 전역은 use-time facade로 해석합니다(TEMPORARY_COMPATIBILITY, monkeypatch seam 보존).
- 검증: Owner 호출을 baseline 함수 AST로 되돌려 비교하는 ledger 게이트, consumer 2,950개 baseline과 결과 동일(기존 실패 2개), post-call State 해시 포함 호출 비교 불일치 0(결정적 레코드), 운영 쓰기 0. 실제 frozen 보고서/LLM·Brief byte parity는 BLOCKED, 전체 pytest·Docker·UEF는 Wave D, Codex 독립 감사 대기이며 FINAL_ACCEPTED가 아닙니다.

## 2026-10-13 · P1.5 Parity Evidence Closure (Second Pass 증거 보강)
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY

- 과거 1,131건 raw 로그(약 366MB x4)를 찾아 SHA-256을 기록했고, 필드 단위 엄격 규칙으로 재분류해 PASS가 아님을 명시했습니다(baseline 두 실행이 한 clone 공유, 실시간 시세 읽기).
- 세션별 clone/TEMP/로그를 쓰는 격리 differential harness와 결정성 플러그인을 추가했습니다. 격리 4세션: 동일 1,020 / 정당화 86 / 실제 불일치 0 / 미해결 25(임시 경로의 PID 한 가지 원인).
- 기존 불일치 6개 테스트(17/17)와 미해결 24개 테스트(28/28)는 목표 재실행에서 byte-identical. 운영 코드 변경 없음, 운영 쓰기 0.
- 실제 frozen 보고서/LLM·Brief byte parity는 BLOCKED, 전체 pytest·Docker·UEF는 Wave D, controlled_mock_lanes 운영 경로 격리 OPEN, Codex 재감사 대기.

## 2026-10-13 · P1.5 Parity Comparator P1 Fix (비교기 R-ID 결함 · Targeted A 쓰기 감사)
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY

- 비교기: `strategy`를 R-ID 허용 키에서 제거했고, memory packet id는 `memory_<20 hex>` 형식이 양쪽에서 맞고 명시적 packet-id 컨테이너 아래일 때만 조건부 허용합니다. 전략 선택·순위·가격·수량·승인 필드는 ID라는 이유로 허용하지 않으며 음성 테스트를 추가했습니다. 과거 86건 재분류 결과는 86건 그대로(전부 실제 memory id/mtime 서명)입니다.
- data/logs 원인: controlled_mock_lanes ledger의 기본 루트가 cwd 상대 경로이며 baseline에서도 재현됩니다. harness가 세션별 `CONTROLLED_MOCK_LANE_LOG_ROOT`로 우회하고, 프로젝트 쓰기 감사는 약화하지 않았습니다(운영 코드 OPEN 항목은 그대로).
- containment 검사는 빈/무시된 디렉터리·프로젝트 감사 배너·종료 코드까지 FAIL로 판정합니다. Targeted A: baseline×2/feature×2 순차 exit_code 0×4, 17/17 byte-identical, 금지된 쓰기 0.

## 2026-10-13 · P1.5 Third Pass Reporter 포함 전체 모듈화 설계
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · WORKFLOW · REPORTING

- 사용자 전달 Codex P1 수정 재감사 `PASS_WITH_FINDINGS`를 토대로 3차 설계를 시작하되 GPT가 테스트를 재실행한 것처럼 주장하지 않습니다.
- Reporter 실제 번들 실행기 `main` 약 1,529줄, memory surface 675줄, trade read model 601줄 등 주요 잔여 대형 함수를 소스에서 검증하고 작업 순서를 문서에 고정했습니다.
- Reporter T0 동작·ABI 증거 확보 → T1 순수 Read Model·Fallback 분리 → T2 증거가 충분한 번들 실행기 분리 → T3 Owner facade·tuple 계약 정리 → T4 기타 에이전트 거대 함수 분리 → Codex 독립 감사 → 마지막 Wave D 순서입니다.
- Reporter 공개 Facade 물리 이동·rename 금지; 실 LLM/보고서/락/큐/저장 동작 미검증 영역은 SAFETY_LOCK. 작업 계획 문서만 수정했습니다.

## 2026-10-13 · P1.5 현재 폴더트리 / 거대 함수 / 삭제 후보 검증
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · REFACTOR · SAFETY

- HEAD `4cb92916` 실제 트리(전체 Python 1,941, reporting 466)와 목표 트리의 `[E]/[P]` 상태를 대조했습니다. 2차에 생성된 Owner 상당수가 과거 설계에는 `[P]`로 남아 있어 상태 보정 안내를 연결했습니다.
- 운영 소스 20KB 이상 파일 118개의 함수 경계를 검사해 빠진 `libs/contracts/agent_outputs.py` 공통 계약 생성자(809/530/466/358줄)와 `decide_trade`, Monitor 추가 함수, Reporter 메트릭 실행기 등을 3차 후속 점검 대상에 포함했습니다.
- Reporter와 Q10/Q12/UEF를 구분하고 레거시 어댑터 및 안전 실행 경로 삭제 금지를 확인했습니다. `strategist_llm_summary.py`의 중복 이름 함수는 사용처 검증을 요구하는 **후보**일 뿐 삭제 승인이 아닙니다.
- Reporter T0+T1 작업 순서는 그대로이며 코드 삭제·이동·실거래 경로 변경·Wave D 실행은 없습니다.

## 2026-10-13 · P1.5 Third Pass T0+T1 (Reporter 소비자 지도 · 순수 read-model/fallback/compact-input 분해)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · SAFETY · TESTING

- T0: Reporter 소비자·monkeypatch·fixture 지도를 기록했습니다(집중 테스트 40개, facade 3개). 실제 frozen 운영 보고서가 없어 REAL_REPORT_PARITY_BLOCKED로 분리했습니다.
- T1: build_trade_report_memory_surface 671→50, build_trade_read_model 563→80, fallback_report 534→187, compact_story_input_for_llm 408→51. 본문 16개를 trade_memory_projection_parts/·trade_read_model_parts/·trade_report/ai_facade_parts/ Owner 12개로 이동했고 facade·prompt·저장·queue/lock 경로는 건드리지 않았습니다.
- 의존 callable은 명시적 인자로 전달하고(deps 바인딩은 원 함수에 유지), Owner는 import·파일·LLM·State 접근이 없습니다.
- 격리 baseline×2/feature×2 결정성 비교: 기록 호출 2,912건(Markdown str·JSON dict 포함) 전부 byte-identical, 운영 쓰기 0. 실제 frozen 보고서/LLM parity·T2~T5·Wave D 미실행, Codex 감사 대기.

## 2026-10-13 · P1.5 Third Pass T1 Evidence Closure (T1 증거 재고정)
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY · WORKFLOW

- 정확히 T1 완료 SHA(67e0dc0e)와 BASE(4cb92916)로 격리 세션 BASE×2/FEATURE×2 비교를 새로 실행했습니다. 결정성 모드 2,912건 전부 byte-identical, 자연 모드 테스트 672개 전부 통과·2,911건 동일.
- 자연 모드의 UNRESOLVED 1건은 hard-timeout 테스트의 wall-clock `latency_ms`(109 vs 106ms)로, 같은 측 반복 간에도 달라지는 본질적 비결정성입니다. 허용오차는 추가하지 않았고 결정성 모드에서 동일함을 근거로 남겼습니다. 결정성 모드의 알려진 타임아웃 실패는 양쪽에서 동일 원인(sleep 대체)으로 재현됩니다.
- T1 scope gate를 BASE..T1_END_SHA 고정 범위(조상 검증 포함)로 교체하고, CI에 독립 단계 'Gate P1.5 Third Pass T1 — pinned extraction parity'(JUnit 포함)를 분리했습니다. CURRENT.md 상태 정정: T2–T5·Wave D 미시작, REAL_REPORT_PARITY_BLOCKED OPEN, Codex 재감사 필요.

## 2026-10-13 · P1.5 Third Pass T2 (Reporter bundle runner 순수 구간 분해 · CI 얕은 이력 보강)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · SAFETY · TESTING · WORKFLOW

- T2-0: CI에 조상(ancestry) 확보 단계를 추가해 `fetch-depth: 2`에서도 T1/T2 단계 고정 SHA가 HEAD의 조상임을 보장하고, CURRENT.md의 낡은 T0/T1/설계 대기 지시를 정리했습니다.
- T2: `live_execution_bundle_runner.main` 1527 → 1343줄. 호출 closure에 파일 I/O·환경·시계·로깅·락이 없음을 정적으로 증명한 순수 구간 8개(192줄)를 `reporter_bundle_runtime_parts` Owner 5개로 이동했고, 락·큐·LLM·저장·이벤트 효과는 main()에 남겼습니다. 집계 목록을 변경하던 구간은 제외했습니다.
- 검증: 고정 결정성 모드에서 `main()` 호출 29건과 순서가 있는 파일 효과 스트림(경로·내용 SHA-256)을 포함해 69/69 byte-identical, 자연 모드는 전체 테스트 통과(효과 스트림은 시간/pid 노이즈로 미해결), 운영 쓰기 0.
- 무실행일·zero-fill fixture는 BLOCKED, REAL_REPORT_PARITY_BLOCKED OPEN, T3~T5·Wave D 미시작, Codex T2 감사 대기.

## 2026-10-13 · P1.5 Third Pass T3 (아키텍처·Owner 계약 정리)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · SAFETY · TESTING · WORKFLOW

- T3-0: 정적 순수성 검사기를 이식 가능한 3상태(PURE/IMPURE/UNKNOWN, 자문용)로 재작성했습니다. 해석 불가·동적 dispatch·깊이 초과는 UNKNOWN이며 PURE로 바뀌지 않습니다. 과거 추출 gate는 단계 종료 SHA의 불변 스냅샷을 비교하고, 현재 HEAD는 별도 gate(import·권한·record 계약·시그니처·facade 폭)로 검증합니다. 두 gate가 정리 후에도 함께 통과합니다.
- T3-A: 207개 모듈의 책임·소비자·계약·부수효과·호환 상태 매트릭스(JSON+MD)와 canonical 목표 트리의 [E]/[P]/[L] 현황 overlay를 추가했습니다. `ranking_core.py`는 두 번째 순위 권한이 되므로 만들지 않았고 마커만을 위한 파일도 만들지 않았습니다.
- T3-B: T2 정책 모듈을 `closed_sell_reconciliation.py`/`report_generation_policy.py`로 분리하고, 기계적 `if True:`를 제거했으며, Owner 함수 12개가 의미 있는 이름의 불변 NamedTuple record를 반환합니다(위치 호환, 호출부 불변).
- 검증: 순서 있는 파일 효과 포함 69/69, Reporter 2,912/2,912, 2차 소비자 1,020 동일 + 정당화 91 + 불일치 0(미해결 20은 재실행 20/20). 남은 위치 반환·facade 폭·REAL_REPORT_PARITY_BLOCKED·T3.5~T5·Wave D는 미완이며 Codex 감사 대기입니다.

## 2026-10-13 · P1.5 Third Pass T3-0.1 (감사 종결·구조 증거 보강)
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY · WORKFLOW

- 분석기 P1: `Path(src).replace(dst)`가 PURE로 오판되던 문제를 수정했습니다. `replace`는 수신자 타입이 증명된 경우에만 판정합니다(Path → IMPURE, str → PURE, 그 외 UNKNOWN). 입력을 변경하는 메서드는 신선한 지역 컨테이너가 아니면 UNKNOWN이며 "순수"는 I/O 없음이지 입력 불변성이 아닙니다(문서화). 테스트 13 → 24, 검사기는 계속 ADVISORY입니다.
- 소유권 매트릭스는 도달 가능한 커밋 `a5cffb9`의 Git 객체에서 재현 가능하게 생성됩니다(207행 재검증, `--verify`). CONTRACT_CANDIDATE와 RENAME_CANDIDATE는 독립 플래그이며 결함 주장이 아닙니다. 마커만을 위한 파일·이동·삭제는 없습니다.
- 변환된 NamedTuple 12개에 dict/list payload 기반 테스트(순서·참조 동일성·공유 변경·copy/deepcopy·JSON 뷰)와 불변 T2 스냅샷 대비 실제 함수 비교를 추가했습니다(NamedTuple은 얕은 불변만 보장).
- `%SystemDrive%` 미해결 placeholder가 clone 안에 캐시 디버리스를 만드는 문제를 재현하고, 세션별 해결된 `PYTHONPYCACHEPREFIX`와 placeholder fail-closed 검사를 harness에 추가했습니다. 운영 코드 변경 없음, T3.1/T3.5/Wave D 미시작, Codex delta 감사 대기.

## 2026-10-13 · P1.5 Third Pass T3-0.2 (Windows harness 격리 P1 종결 작업)
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY · WORKFLOW

- 원인 확정: `SYSTEMDRIVE`가 없는 scrubbed 환경으로 Microsoft Store CPython을 시작하면 시작 시점에 cwd(세션 clone) 안에 리터럴 `%SystemDrive%\ProgramData\Microsoft\Windows\Caches` 트리가 생깁니다. `PYTHONPYCACHEPREFIX`·`sitecustomize.py`와 무관하며 python.org CPython에서는 재현되지 않습니다. 기존 테스트의 최소 환경과 실제 `session_env()` 모두 `SYSTEMDRIVE`가 없었습니다.
- 수정(harness 한정): `session_env`에 해결된 `SYSTEMDRIVE`를 항상 포함하고, 세션 시작 전 인터프리터 preflight가 cwd에 무엇이든 생기면 fail-closed로 중단합니다. 격리 테스트는 손으로 만든 최소 환경 대신 실제 `session_env()`로 사용 가능한 모든 인터프리터·바이트코드 on/off를 검증합니다(17 → 22).
- CI: Linux는 Windows 전용 테스트를 SKIPPED로 따로 집계(Windows PASS로 계산하지 않음)하고, 새 필수 `windows-latest` smoke job은 Windows 전용 테스트가 실제 실행되어 통과하지 않으면 실패합니다. `sitecustomize.py`·운영 코드 변경 없음, 독립 Codex 재감사 전까지 PENDING_CLOSURE.

## 2026-10-14 · P1.5 Third Pass T3-0.3 (세션 write-containment P1 종결 작업)
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY · WORKFLOW

- 확인된 격리 공백: 기존 harness는 경로 이름만 스냅샷하여 *새 파일*만 검출했고, 기존 파일의 내용 변경·삭제·같은 크기 변경(mtime 복원 포함)은 PASS로 처리되었습니다. 8개 변경 케이스를 먼저 재현했습니다(6건 false PASS).
- 수정(harness 한정): 구조화된 manifest(type/size/mtime_ns/SHA-256/symlink target)로 CREATED·DELETED·TYPE_CHANGED·CONTENT_CHANGED·METADATA_CHANGED·SCAN_ERROR를 모두 증거에 기록하고, 읽기 실패·불안정 스캔·지원하지 않는 타입은 fail-closed로 FAIL 처리합니다. strict(SHA-256)와 fast(내용 동등성 미증명, 명시 라벨)를 구분하고, 보장 수준은 `PRE_POST_END_STATE_MANIFEST_EQUIVALENCE`(실행 중 일시적 write-and-restore 및 OS 전체 write 차단은 증명하지 않음)로 명명했습니다.
- 실패 세션 증거는 cleanup 전에 기록하며(경계·민감정보 제외·보존 개수/기간/용량 제한, task-owned 디렉터리만 삭제) 통제 실험: 동일 SHA 4세션 PASS(59/59 동일), 단일 세션 의도적 오염은 병렬·`--same-path` 모두 exit 2.
- NTFS 디렉터리 mtime 문제는 P2 UNRESOLVED로 유지(로컬 재현 불가, 호스티드 진단 추가, 허용치 없음). 운영 코드·`sitecustomize.py`·`conftest.py` 변경 없음, 독립 Codex 감사 전까지 PENDING_CLOSURE.

## 2026-10-14 · P1.5 Third Pass T3.1 (Owner 구조 정리)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · SAFETY

- 변경: 위치 기반 반환값이 22~30개인 Owner 함수 8개(Reporter memory feedback, Operator Brief market/monitor 섹션 3개, Monitor volume/pullback/breakout gate, Scanner candidate score components, Commander decision policy/applied policy command)를 의미 있는 이름과 positional-compatible `NamedTuple` 결과로 정리했습니다. 함수 본문·시그니처·facade 심볼·호출부 unpacking은 그대로이며 파일 생성/삭제/이름변경은 없습니다.
- 구조: 24개 필드 record로 `signal_features.py`가 350 LOC를 넘어, 해당 함수를 같은 책임의 기존 `signal_features_breakout_volume_gate.py`로 이동했습니다.
- 검증: BASE×2/FEATURE×2 differential(strict SHA-256 containment 4/4 PASS, 세션당 1253 tests 통과, 기록 호출 474건 중 469 byte-identical·5 justified(session 경로 의존 memory packet id)·REAL_MISMATCH 0·UNRESOLVED 0). AST 본문 동일성, 과거/현재 Owner gate 모두 통과.
- 후보: CONTRACT 30→27, RENAME 54→52. ranking/결정 순서/위험 경로 모듈은 SAFETY_LOCK로 유지. 실패 증거 기밀성 P2는 열려 있으며 T3.5 이전 metadata-only 보존이 필수 후속입니다. 독립 Codex 감사 전까지 PENDING.

## 2026-10-14 · P1.5 Third Pass T3.2 (실패 증거 보안 P2 종결 작업)
**Stage:** Architecture and Maintainability
**Tags:** SAFETY · TESTING · WORKFLOW

- 확인: 실패 세션 증거가 변경 파일의 본문을 파일명 필터만으로 복사하여, 평범한 이름의 파일에 담긴 비밀이 그대로 복사될 수 있었습니다(합성 마커로 재현).
- 수정: 본문 복사 경로를 제거했습니다. 실패 세션은 분류·개수·경로/크기/mtime/SHA-256 manifest만 로컬에 보존하고, `summary.json`에는 개수와 경로 digest만 남깁니다. 본문 복사를 다시 켜는 스위치는 없습니다. strict containment 검증(파일 본문 읽기·해시)은 그대로입니다.
- 검증: 보안 테스트 7건이 BASE에서 실패하고 현재 통과(harness 47 → 56), 4세션 strict containment 통과, 의도적 오염 세션은 exit 2 + metadata-only + 마커 미검출.
- 잔여: pytest 출력/recorder 로그·경로명·저엔트로피 파일 digest는 로컬 전용·비정제 상태로 명시. NTFS P2 미해결, T3.5 미시작, 독립 보안 delta 감사 대기.

## 2026-10-14 · P1.5 Third Pass T3.2.1 (export-safe summary 종결 작업)
**Stage:** Architecture and Maintainability
**Tags:** SAFETY · TESTING

- 확인: `summary.json`이 내부 evidence 전체를 기록하여 테스트 경로·이름, pytest 출력 꼬리, 실패 테스트 이름, 기록 함수명, reproduce 명령이 그대로 내보내질 수 있었습니다(합성 마커로 재현).
- 수정: `summary.json`은 고정 allowlist(검증된 enum·SHA·상한 있는 정수·경로 digest)에서 새로 만든 객체이며, 전체 내부 evidence는 LOCAL ONLY `local_evidence.json`으로 분리했습니다. strict containment·exit code 2·실패 메타데이터 보존은 그대로입니다.
- 검증: 직렬화된 `summary.json` 전체에서 합성 마커 0건(단위 + 실제 4세션 2회), 보안 테스트 BASE 실패→통과(harness 56 → 63), Windows smoke는 export 테스트 실행을 요구합니다.
- 상태: 파일 본문 복사 하위 문제 FIXED, export-safe summary는 독립 Codex 재감사 대기, 로컬 로그/manifest는 민감 가능·LOCAL ONLY, NTFS P2 미해결, T3.5는 보안 승인까지 BLOCKED.

## 2026-10-14 · P1.5 Third Pass T3.2.2 (export validator 종결 작업)
**Stage:** Architecture and Maintainability
**Tags:** SAFETY · TESTING

- 확인: export 요약의 SHA/경로 digest 검증이 `$` + `match`라 끝의 개행을 허용했고, `execution_order`는 유효 ID만 걸러 내거나 중복을 그대로 보존했습니다.
- 수정: `fullmatch`로 정확히 40/16 소문자 hex만 허용(무효 SHA는 null, 무효 digest 항목은 제외), `execution_order`는 b1·b2·f1·f2가 각각 정확히 한 번 있는 리스트만 허용하고 그 외는 null입니다. 순서는 입력 그대로 유지합니다(parallel/same-path 모두 유효).
- 검증: 신규 음성 테스트 31건이 이전 harness에서 실패하고 현재 통과(63 → 108), 직렬화된 export 전체에서 마커 0건, 4세션 clean/contaminated smoke 불변.
- 상태: file-body retention CLOSED, validator 수정은 독립 Codex 재감사 대기, T3.5 BLOCKED, NTFS P2 미해결.

## 2026-10-14 · P1.5 Third Pass T3.5 (cross-agent output contract 리팩터)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · SAFETY

- 변경: `libs/contracts/agent_outputs.py`의 대형 builder 4개(monitor 807 / strategist 528 / scanner 464 / commander 356 LOC)를 `libs/contracts/` 안의 응집된 projection stage 모듈로 분해했습니다. 공개 함수명·시그니처·출력 필드·key 순서·validation은 그대로이고, facade가 계약의 단일 권위입니다(현재 71 / 20 / 75 / 52 LOC).
- 검증: 구현 전에 BASE에서 고정한 fixture(입력 148건 + 결정적 변형 18,497건)가 바이트 단위로 0 mismatch, 모든 stage를 인라인하면 BASE builder AST와 정확히 일치합니다. BASE×2/FEATURE×2 strict containment differential은 647 호출 중 641 byte-identical·6 justified(세션 경로 의존 memory packet id)·REAL_MISMATCH 0·UNRESOLVED 0입니다.
- 유예: monitor decision-rule stage(201 LOC)와 scanner bias stage(155 LOC)는 평가 순서 변경 위험으로 SAFETY_LOCK 유지. Supervisor/Executor/Step5C 및 실제 Reporter parity(BLOCKED)는 변경 없음. 독립 Codex 검토 대기.
- Linux CI 진단: 고정 fixture replay가 Linux에서 실패했으나 원본 BASE 트리도 Linux에서 동일하게 실패(`source_refs.evidence_log_path`의 `str(Path(...))` 경로 구분자 차이)하여 리팩터 회귀가 아닌 fixture 이식성 문제로 확인했습니다. 커밋된 golden은 수정하지 않았고, 비 Windows 환경에서는 고정 BASE 트리를 같은 플랫폼에서 실행한 증거와 비교합니다.

## 2026-10-14 · P1.5 T3.5.1 (portable oracle · Windows native gate 종결 작업)
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY · WORKFLOW

- 확인(Codex): portable replay가 80개 non-bound 레코드를 경로 구분자를 정규화한 golden과 비교하여 구분자만 바꾼 FEATURE 회귀를 통과시키는 false negative, 그리고 필수 Windows job이 T3.5 계약 테스트를 실행하지 않는 gap.
- 수정: portable 모드에서 148개 전체 레코드를 고정 BASE 트리를 같은 호스트에서 실행한 결과와 canonical SHA-256 정확 일치로 비교(정규화 금지, BASE 증거 누락·형식 오류는 fail-closed)하고, golden 무결성은 별도 집계(80/68)합니다. 필수 Windows job에 native 계약 replay(16개 필수 테스트 JUnit 집계, skip/deselect/누락 금지)를 추가했습니다.
- 검증: 기존 false negative 재현 및 현재 거부, committed golden 불변, 구조 AST gate 유지. 독립 Codex 재감사 대기, T3.5 구조 parity PASS 유지, REAL_REPORT_PARITY_BLOCKED·NTFS P2 유지, T4/T5/Wave D 미시작.

## 2026-10-14 · P1.5 T4-A (Scanner 구조 종결 작업)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · SAFETY

- 변경: 1,261줄이던 `scanner_node`를 474줄로 줄였습니다. 후보별 점수 row, ranking policy overlay, selection evidence projection, 이벤트/trace payload builder를 `libs/runtime/scanner/`의 응집된 Owner 4개로 옮겼습니다(원문 그대로, use-time facade, 두 번째 ranking 구현 없음). State 쓰기·이벤트 발행·영속화·정식 rank 정렬은 노드의 원래 경계에 남겼습니다.
- 검증: 구현 전에 BASE에서 고정한 계약(State 73건 + 변형/후보풀 시나리오 1,575건: 동점, rank-1 뒤집기, 순서/중복/빈 풀, 순서가 있는 effect 증거)이 0 mismatch이고, 모든 stage를 인라인하면 BASE AST와 정확히 일치합니다.
- 발견: BASE의 Scanner ranking은 문자열 hash 순서에 의존하여 freeze는 `PYTHONHASHSEED=0`을 고정합니다(동작은 변경하지 않음). Windows native 재생과 같은 호스트 BASE oracle이 필수 CI gate입니다.
- 상태: 독립 Codex 감사 대기, T4-B/T5/Wave D 미시작, REAL_REPORT_PARITY_BLOCKED·NTFS P2 유지.

## 2026-10-15 · P1.5 T4-A.1 (golden variant conservation 종결 작업)
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY

- 확인(Codex): Scanner 계약 비교기가 기대된 variant가 사라져도(누락) native/portable 모두 불일치를 보고하지 않는 false negative.
- 수정: 전체 variant ID inventory를 결정적으로 재도출하고, 기존 `_sampled()`로 기대 샘플 ID를 계산하여 기대 샘플 == pinned BASE == FEATURE ID 집합을 정확히 요구합니다. 누락·추가·중복·형식 오류·manifest 합계 불일치는 fail-closed입니다. golden은 수정·재생성하지 않았습니다.
- 검증: 기존 false negative 재현 및 두 비교기 모두 거부, 73 records / 1,575 variants 전체 replay 0 mismatch, T3.5 계약 gate 유지. P2: hash seed 간 rank-1/선택 변화는 재현되지 않았고 두 State의 제외 심볼 목록 순서 차이는 기존 BASE 동작(변경 없음).
- 상태: 독립 Codex 감사 대기, T4-B는 ACCEPT까지 BLOCKED, REAL_REPORT_PARITY_BLOCKED·NTFS P2 유지.

## 2026-10-15 · P1.5 Architecture Visualization Gate — 사용자 확정
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · DOCUMENTATION · WORKFLOW

- T4 전체 분해와 독립 검증을 먼저 완료하고, 그다음 실제 Git SHA 기반 7개 Agent/Owner Mermaid 현재 구조, import 의존성 SVG, 수정 가능한 draw.io 목표 구조, 경로별 consumer·권한 gap matrix를 필수로 생성하도록 문서 규칙을 고정했습니다.
- GPT와 사용자가 실제 트리/목표를 눈으로 검토·승인해야 파일 이동·병합·이름 변경, P1.5.10 정리, Wave D 또는 P1.6로 넘어갈 수 있습니다. Codex 소비자/동적 의존성/SAFETY_LOCK 감사와 별도 동등성 검증 필수. 증거 부재 시 `ARCH_CONVERGENCE_BLOCKED`.
- 규칙 연결: `AGENTS.md`, `CLAUDE.md`, `COMMON_RULES.md`, `CURRENT.md`, pre-Wave-D 순서. 현재 T4-A.1 Codex 감사 대기·T4-B BLOCKED 그대로. 이번 변경은 문서만, 다이어그램 생성·코드 재배치 미실시.
- 근거: `docs/refactor/P15_POST_T4_ARCHITECTURE_VISUALIZATION_GATE_2026_10_15.md`, `docs/daily_patch/2026-10-15_p1_5_architecture_visualization_gate.md`.

## 2026-10-15 · P1.5 T4-A.1 Codex ACCEPT / UI 노트 스키마 복구
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY · WORKFLOW

- Codex 독립 검증으로 variant conservation P1 CLOSED, T4-A 최종 ACCEPT. 샘플 ID 개수는 mod=4: 396, mod=1: 1,575. Codex의 full-corpus PASS는 accounting이며 새 실 Scanner full replay 수행 증거는 아닙니다.
- 최근 아키텍처 문서 커밋의 UI 노트 status=`planned` 오류를 기존 허용값 `current`로 수정했습니다. 규칙은 현재 유효하지만 시각화 산출물은 아직 시작하지 않았습니다.
- T4-B Monitor는 최신 HEAD Linux/Windows 필수 CI SUCCESS 확인 이후에만 착수. 새 PYTHONPATH CLI P2 및 기존 telemetry/NTFS/Reporter parity 미해결은 별도 유지.
- 증거: `docs/refactor/work_orders/evidence/P15-T4-A-1-CODEX-039.md`, `docs/daily_patch/2026-10-15_p1_5_t4_a_1_codex_accept.md`.

## 2026-10-15 · P1.5 T4-B (Monitor 구조 분해)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · SAFETY

- 변경: `monitor_node`(1,107→498 LOC), entry candidate 평가(449→250), `evaluate_exit_policy`(673→354), 계좌 PnL 교차검증(186→71)을 기존 `libs/runtime/monitor`, `libs/runtime/monitor_exit` 패키지의 15개 Owner로 분해했습니다. 이동은 verbatim이며 모듈 전역은 use-time(`facade.NAME`)으로 해석되어 monkeypatch seam이 유지됩니다.
- 검증: 구현 전에 BASE 계약(149 입력, 2,879 variant, 순서 있는 effect)을 먼저 동결했고, 전체 corpus replay 0 mismatch, AST inline-reconstruction gate가 BASE 함수 AST와 정확히 일치합니다. 기존 Monitor 테스트 961건·역대 P1.5 gate 3,092건 통과.
- 경계: State 변경·이벤트 발행·영속화·probe의 환경변수 읽기는 node 경계에 유지, Broker/LLM/Supervisor/Executor/Step5C 변경 없음.
- 상태: 독립 Codex 감사 대기, T4-C/T5/Wave D 미착수, REAL_REPORT_PARITY_BLOCKED·NTFS P2 유지.

## 2026-10-15 · P1.5 T4-B Codex ACCEPT / T4-C Strategist GO
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · WORKFLOW

- T4-B 독립 감사 **ACCEPT**: AST 42 segment·15 Owner 복원, 구조 gate 13 PASS, Monitor 집중 회귀 139 PASS, pinned BASE/FEATURE 149개씩 full portable 2,879 variant 0 mismatch, golden 무결성 133 non-bound / 16 bound PASS.
- FINAL `4e242e5` CI `38664980307` Linux/Windows 네이티브 replay 및 JUnit accounting 모두 SUCCESS; CI 제한 20→35분 확대는 21m18s 실제 실행시간으로 정당화됨.
- 신규 P0/P1 없음. BASE×2/FEATURE×2 별도 세션 differential은 **NOT RUN / P2** 유지. Reporter 실증 parity, NTFS mtime, cross-seed telemetry, Scanner 도구 PYTHONPATH P2 미해결.
- 다음 한 건의 활성 명세는 `docs/refactor/work_orders/P15-T4-C-STRATEGIST-041.md`. T4-C는 기존 `strategist_node` 결정적/pure 부분만 분리, LLM prompt/provider/재시도/timeout 및 호출 수, State/Event·Broker 경계는 변경 금지. T4-D/T5/Wave D 아직 불허, 사용자 승인 전 구조 트리 변경 금지.
- 근거: `docs/refactor/work_orders/evidence/P15-T4-B-CODEX-040.md`, `docs/daily_patch/2026-10-15_p1_5_t4_b_codex_accept_t4_c_go.md`.

## 2026-10-15 · P1.5 T4-C (Strategist 구조 분해)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · SAFETY

- 변경: `strategist_node`(1,216→545 LOC)를 기존 `libs/runtime/strategist/{context,policy,output}`의 13개 Owner로 분해했습니다. 이동은 verbatim이며 모듈 전역은 use-time(`facade.NAME`)으로 해석되어 monkeypatch seam이 유지됩니다.
- 검증: 구현 전에 BASE 계약(50 입력, 1,141 variant, mock LLM ok/error/timeout/raises/strict, news/global 예외, 순서 있는 effect)을 먼저 동결했고 전체 corpus replay 0 mismatch, AST inline-reconstruction gate가 BASE 함수와 정확히 일치합니다. 동결 중 offline replay가 curl 경로로 실제 네트워크에 닿을 수 있음을 발견해 차단하고 결정적 offline provider를 사용합니다.
- 경계: Frame LLM 호출·프롬프트·모델/타임아웃/재시도/fallback, State 변경, 이벤트 발행, 영속화, 환경변수 읽기는 node에 유지, Broker/Supervisor/Executor/Step5C 변경 없음.
- 상태: 독립 Codex 감사 대기, T4-D/T5/Wave D 미착수, REAL_LLM_PARITY_NOT_RUN, REAL_REPORT_PARITY_BLOCKED·NTFS P2 유지.

## 2026-10-15 · P1.5 T4-C Codex ACCEPT / T4-D GO
**Stage:** Architecture and Maintainability
**Tags:** TESTING · REFACTOR · SAFETY

- T4-C Strategist 독립 감사 최종 **ACCEPT**: 22 ledger/13 Owners AST 복원, 구조 11 PASS, 계약 5 PASS, archived BASE 50 + FEATURE 50 records 전체 1,141 variants/0 mismatch, mock LLM 5모드 호출/상태 동등. FINAL CI `38679851004` SUCCESS.
- **P2**: golden v1→v2는 단순 6개 누락이 아니라 **Reporter 피드백 Fallback 29-variant 레코드**와 **max-token Fallback 23-variant 레코드**가 교체된 것. 상태 효과 21→24. 원래 시나리오 커버리지가 사라졌으므로 P1.5 최종 승인 전 별도 immutable BASE fixture로 복원·Codex 독립 감사 필수. v3 동등성 자체는 PASS.
- `REAL_LLM_PARITY_NOT_RUN`, `REAL_REPORT_PARITY_BLOCKED`, NTFS/cross-seed/PYTHONPATH 및 BASE×2/FEATURE×2 P2 유지. T4-D는 Commander pure 정책 우선순위/Operator UI 정확 Markdown 렌더만 분리, 기존 LLM·권한·State/Event·영속화 동작은 보존.
- 근거: `docs/refactor/work_orders/evidence/P15-T4-C-CODEX-043.md`, `docs/refactor/work_orders/evidence/P15-T4-C-GOLDEN-SCENARIO-GAP-044.md`, `docs/refactor/work_orders/P15-T4-D-COMMANDER-UI-044.md`.

## 2026-10-15 · P1.5 T4-D preflight CI 문서 계약 복구
**Stage:** Architecture and Maintainability
**Tags:** TESTING · DOCUMENTATION · SAFETY

- 최신 CI `38689842640`의 기존 Fast Track 계약 단계에서 `CURRENT.md`의 `**State:**` 선언 누락으로 실패한 것을 확인하고, `MAIN_FROZEN` 및 `No ZIP` 상태를 활성 T4-D 문서에 복구했습니다.
- 기존 `P15_FAST_TRACK_WAVE_S_020.md`는 CI 호환을 위한 *과거 링크*로만 유지합니다. **현행 활성 작업은 T4-D 하나**이며 T5/Wave D/main merge 권한은 부여하지 않습니다.
- 새 HEAD의 Linux/Windows CI가 모두 SUCCESS일 때만 Claude의 T4-D 순수 구조 분리를 시작합니다. T4-C Reporter-feedback fallback coverage P2는 별도 복원·독립 검증 전까지 OPEN입니다.
- 문서 전용 수정이며 주문/승인/LLM/State 동작 변경은 없습니다.

## 2026-10-15 · P1.5 T4-D (Commander 정책 · Operator UI 구조 분해)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · SAFETY

- 변경: Commander `_resolve_commander_behavior_policy`(528→135), `_attach_commander_applied_policy`(297→175), `_assess_open_position_commander_override`(155→129)와 Operator UI `_render_operator_brief_markdown`(351→22), `_build_operator_brief_sections`(341→249), `_build_operator_brief_input`(314→105)를 11개 Owner로 분해했습니다. 이동은 verbatim이며 모듈 전역은 use-time(`facade.NAME`)으로 해석됩니다.
- 검증: 구현 전에 BASE 계약(189 입력, 6,456 variant, Markdown 정확 문자열)을 먼저 동결했고 전체 replay 0 mismatch, AST 재구성 gate가 6개 BASE 함수와 정확히 일치합니다.
- 경계: 환경변수 읽기, State 변경, LLM 연동 `_load_operator_brief`, 아티팩트 저장은 변경하지 않았고 LLM/Broker/Supervisor/Executor 권한 변경 없음. REAL_BRIEF_PARITY_NOT_RUN(합성 offline 입력만 검증).
- 상태: 독립 Codex 감사 대기, T5/Wave D/main 병합 미착수. T4-C Reporter fallback 커버리지 P2는 별도 유지.


# 2026-10-15 - Reporting Target-Tree Relocation Batch 1

- Relocated **12 Reporter helper modules** without changing their implementation bytes: `trade_report` (6), `trade_report_markdown` (2), `trade_story` (4).
- Kept all previous import locations as identical module-object aliases for compatibility; existing runtime call sites and major reporting entrypoints remain untouched.
- No T4 runtime files, order execution logic, guard, CAS or broker paths changed.
- Added focused import-identity tests. Full pytest and UI build still needed before merge.
- Details: `docs/daily_patch/2026-10-15_reporting_relocation_batch1.md`.

# 2026-10-15 - Reporting Target-Tree Relocation Batch 2

- Move five implementation bodies byte-for-byte, retaining legacy module-object aliases.
- `trade_report_ai_merge_policy` -> `trade_report/merge_policy`
- `trade_report_ai_prompting` -> `trade_report/prompting`
- `trade_report_ai_shared_facts` -> `trade_report/shared_facts`
- `trade_report_markdown_monitor` -> `trade_report_markdown/monitor`
- `trade_report_markdown_scanner` -> `trade_report_markdown/scanner`
- Existing call sites, top-level Reporting owners and all agent/runtime/execution paths remain untouched.
- Batch 1 prerequisite: 14 import checks and 185 related tests passed.
- Validation results are recorded in the Batch 2 refactor document.

- Batch 2 validation: **272 pytest passed**, **16 web tests passed**, production build passed; five implementation byte comparisons and canonical-first import checks passed. Full repository suite/live trading not run.

# 2026-10-15 - T4 / PR #5 Reporting Integration Hold

- Deleted only retired `refactor/gpt-p0-strategist-contract-20261015` after user-confirmed PR #4 CLOSED/unmerged; verified full-history bundle retained locally.
- Compared 11 overlapping paths by full Git blob SHA and content. Preserve T4 ownership, especially normalization/operator_text and expanded or separated flat helpers.
- Nine byte-identical relocation pairs are selective integration candidates; no Reporting code moved or changed. Batch 3 remains paused; merge remains on hold.
- PR #5 Draft workflow is retained; GitHub API Forbidden prevents independent isDraft verification. No Ready/merge/auto-merge operation performed.
- Full report: `docs/refactor/2026-10-15_t4_pr5_reporting_conflict_report.md`.

## 2026-10-15 - T4 conflict snapshot recheck

- T4 advanced to `4e242e5`; only five documentation files changed. Eleven overlapping paths, nine independent relocation candidates and code preservation strategy remain valid. Latest shared changelog blob SHAs are recorded in the conflict report. No code moved; Batch 3 and merge remain on hold.

# 2026-10-15 - Scripts / Config Inventory and Safe Example Relocation

- Scripts 212 -> 216 files: classify all files and record import/subprocess/CI/Docker/Windows scheduler/docs references.
- Move demo_m22_skill_flow, demo_m22_graph_with_hydration and demo_m7_dry_run_pipeline implementations into scripts/examples; legacy module/CLI paths remain wrappers.
- Business logic unchanged: bootstrap +7/-2 lines, 45 wrapper lines, one package marker. Original implementation bytes recovered by reversing only bootstrap edits.
- Related pytest 20 passed; original offline CLI 34/34, relocated CLI 68/68 equivalent after clock-only normalization; direct bootstrap 6/6 passed.
- Config 8 KEEP; no deletes, order submissions or strategy/config value changes. Reporting Batch 3 remains paused; T4 code conflict 0. Only the two shared changelog files use the approved append-only exception. Future integration must preserve both histories and check duplicate entries.
- Evidence: docs/refactor/2026-10-15_scripts_config_migration.md and docs/refactor/2026-10-15_scripts_config_inventory.json.
- Final combined targeted pytest: **26 passed**; one dependency deprecation warning. Existing JSON entries/order and Markdown prefix preservation verified.

# 2026-10-15 - Scripts Bulk Target-Tree Migration

- Processed 157 candidates; relocated **138** implementations: Research 53, Diagnostics 73, Maintenance 12. Held 19 with per-file evidence.
- Kept legacy CLI/import paths with 138 thin wrappers (1,932 lines). Root Python: 42 local implementations, 8 existing forwarders, 141 total compatibility wrappers and one package marker.
- Bootstrap-only changes; inverse edits recover byte-identical originals. No business logic, operational/trading policy, Config 8 or protected Reporting/runtime changes.
- Validation: **276 import/signature/root checks**, **828 CLI parity checks**, **300 existing pytest tests passed**. Guarded temp-only validation; no orders or external collection.
- Preserved Operations/T4 scripts; T4 code overlap zero. These two shared changelogs use the approved append-only exception; future integration preserves both histories and checks duplicate entries.
- Reporting Batch 3 paused; PR #5 Draft workflow unchanged, no merge or auto-merge.
- Report: docs/refactor/2026-10-15_scripts_bulk_migration.md; ledger: docs/refactor/2026-10-15_scripts_bulk_manifest.json.
- Final UI patch-note checks: **5 passed**; append-only history integrity verified and successful temporary test/runtime artifacts cleaned.

# 2026-10-15 — T4 / PR #5 Reporting Conflict Cleanup

- Restore eight T4-overlapping flat helpers to their exact main source blobs, remove eight corresponding stale PR5 canonical copies.
- Match `trade_report/__init__.py` with T4, retain only nine independent Reporting relocation pairs.
- All 138 Scripts canonical relocations and 141 public CLI wrappers preserved.
- No T4 files or live trading policy changed. PR #5 Draft remains unmerged.
- Regression on the combined T4 + PR5 checkout required before approval.
- Detail: `docs/refactor/2026-10-15_t4_pr5_reporting_cleanup.md`.

# 2026-10-15 — Scripts Target-Tree Compatibility Audit

- Add static AST-based read-only preflight for all 138 relocated Scripts and 141 root compatibility wrappers.
- Validate legacy/canonical path presence, Python syntax, CLI/import dispatch target literals and manifest conservation. No target script is invoked.
- Four synthetic fixture tests PASS in GPT isolated environment. Full checkout and T4/PR5 combined tests not run.
- Existing public CLI wrappers, T4 source, Config and trading authority untouched; PR #5 remains Draft.
- Docs: `docs/refactor/2026-10-15_scripts_wrapper_contract_audit.md`.

# 2026-10-15 — Scripts contract CI / Codex handoff

- Add read-only wrapper auditing CI for Python 3.12 Linux and Windows; 141 path checks and four isolated fixture tests.
- Independently re-ran isolated fixture tests: **4 PASS**. CI and full-checkout wrapper audit remain **PENDING**.
- Register `docs/refactor/work_orders/PR5-CODEX-SCRIPTS-ACCEPTANCE-20261015.md` for Codex. Claude T4 remains independent; no wrapper retirement or T4/PR5 merge.

# 2026-10-15 — Scripts CI Windows fixture isolation correction

- First run: Linux 141 wrapper checks + four fixture pytest PASS; Windows 141 wrapper checks + four fixture pytest assertions PASS but repository conftest returned exit 1 on NTFS directory mtime change under data/originals and data/specs.
- Keep the actual-checkout static audit; stage only synthetic source/unit fixtures in GitHub runner temporary workspace, outside the checkout. Production-write protections in repository unchanged.
- New Linux/Windows CI evidence required; no changes to T4 or public CLI paths.

# 2026-10-15 - Scripts continuation / Issue #8

- Status **SCRIPTS_CONTINUATION_IN_PROGRESS**. Prior Issue #6 accepted the 138 migrated implementations only.
- Classified remaining 42 implementations, 8 delegates, 20 Windows/shell launchers, 19 holds and 141 wrappers. Holds: KEEP 15 / TEST_BLOCKED 3 / relocation after gate 1. Wrappers: 112 PRESERVE / 29 review after gate, all retained.
- Fixed source auditor false accepts: disconnected ABI alias, incorrect CLI run_name, commented example dispatch. All 141 wrappers pass unchanged.
- Added source-only Windows invocation/CWD/policy/task graph and native Windows Parser.ParseFile checks for six PowerShell files in Scripts CI. Local isolated tests: **12 PASS**; native Windows evidence is recorded by the new CI job after push. No live launcher invoked.
- Existing registration/unregistration leaves two Q12 task suffixes unmatched; operational-owner review only, no task-policy edit. No T4/Reporting/runtime/strategy/Config/deployment changes or physical moves/removals.
- Future physical cleanup requires architecture approval and usage/retirement proof. Issue #9 UI work remains next, not executed here.
- Details: docs/refactor/2026-10-15_scripts_continuation_issue8.md; evidence: docs/refactor/2026-10-15_scripts_remaining_dispositions.json.

# 2026-10-15 — Scripts continuation / Issue #8 iteration 2

- Fix empty research outlier analysis; validate held entrypoints without production execution.
- Empty research top1 return is null instead of IndexError; nonempty values preserved.
- Seven new held-entrypoint tests plus five research tests and one missing-authority test PASS.
- Windows venv command contract mocked; empty historical no-write CLI is COMPLETE with zero units, not proof of historical authority.
- Order-demo duplicate helpers, Q12 scheduler asymmetry, physical moves and wrapper retirement remain gated; all wrappers retained. Issue #9 not started.
- Offline research handles empty input; trading, scheduler, Reporting and T4 code unchanged.
- Status: SCRIPTS_CONTINUATION_IN_PROGRESS. Details: docs/daily_patch/2026-10-15_scripts_issue8_followup.md

# 2026-10-15 — Scripts continuation / Issue #8 iteration 3

- Resolve literal per-file task prefixes without shell expansion; parse cleanup CLI before deletion.
- Keep raw task fields; add resolved mismatches, unresolved evidence and optional strict six-create/four-delete baseline gate.
- Report two Q12 unmatched tasks for owner review; scheduler policy and launchers unchanged.
- Cleanup --help exits0 and unknown flags exit2 before glob/deletion; zero-argument behavior unchanged.
- 23 isolated fixture tests PASS; source audits141 wrappers and20 launchers PASS. Ubuntu/Windows gates retained; exact commit results in Actions.
- Historical snapshot unchanged; held delta17 KEEP /1 TEST_BLOCKED /1 relocation after architecture gate. All141 wrappers retained.
- Source-only contract hardening; no T4, Reporting, trading, Config or scheduler policy changes.
- Status: SCRIPTS_CONTINUATION_IN_PROGRESS. Details: docs/daily_patch/2026-10-15_scripts_issue8_iteration3.md

# 2026-10-15 — GPT Source Work Order01

- Replace four duplicate JSONL loops with the existing reader; fix intent attribution and exact-zero broker observations.
- Preserve _load_jsonl/_iter_rows, CLI entrypoints, JSON keys, output formatting, ordering and M25 UTC-day semantics. Shared reader unchanged.
- Prefer execution.allowed including false/null; fallback verdict and verdict_reason require a matching explicit intent ID. Suppress ambiguous multi-order context.
- Finite Decimal equality accepts exact numeric zero only; fractional, NaN, Infinity and tiny nonzero codes cannot count as success.
- 77 targeted pytest PASS;80 fake-file CLI invocations across four entrypoint forms and8 baseline JSON/text comparisons PASS. No native Windows diagnostic-suite claim.
- All141 wrappers retained; no T4, order/approval/broker runtime, UEF authority, scheduler, Config or UI code changed.
- More accurate read-only trade diagnostics; trading authority and execution behavior unchanged.
- Status: SCRIPTS_CONTINUATION_IN_PROGRESS. Details: docs/daily_patch/2026-10-15_source_work_order01.md

# 2026-10-15 — GPT Source Work Order02

- Q10/Q12 share baseline_candle_reader and baseline_artifact_io while retaining legacy facades.
- Move three candle functions to a shared owner; Q12 no longer depends directly on the Q10 provider. Q10 public signatures and local normalization/number monkeypatch seams retained.
- Replace four local JSON I/O bodies with two shared implementations, removing two redundant copies. Keep UTF-8 formatting, newline, error behavior and all artifact paths/schemas.
- 81 focused pytest PASS;13 baseline differential scenarios PASS. Q10 six/Q12 nine artifact files, including10 JSON, byte-identical with the existing Q12 generated_at clock fixed equally in test only.
- No external collection/order calls, T4 code, strategy, returns/cost, decision cadence, authority, scheduler/Config or vnext publication changes. All141 wrappers retained.
- Common data responsibility no longer belongs to a strategy-specific provider; reporting behavior preserved.
- Status: SCRIPTS_CONTINUATION_IN_PROGRESS. Details: docs/daily_patch/2026-10-15_source_work_order02.md

# 2026-10-15 — GPT Source Work Order03

- Share pure diagnostic owners and remove12 redundant copies; correct Ops broker-code truncation.
- 18 local helper bodies delegate to shared owners or the existing JSONL reader. Broker implementations converge after the Ops exact-zero correction.
- Preserve legacy function names, eager/lazy JSONL, percentile rounding, argv, stdout/stderr, JSON types, exit/exception behavior, 1MiB hashing and tolerant UTF-8 line counting.
- 119 distinct targeted pytest PASS;63 baseline helper comparisons and22 CLI help/error comparisons PASS (110 subprocesses).
- Closeout/Drill child bodies never executed; milestone seams tested only with stubs. No native Windows or full-workflow acceptance claim.
- All141 wrappers retained; no T4/runtime/order/authority/Config/UI/scheduler changes. Existing date fallback functions and shared event reader unchanged.
- Read-only diagnostics share one implementation per responsibility; trading and operational execution contracts unchanged.
- Status: SCRIPTS_CONTINUATION_IN_PROGRESS. Details: docs/daily_patch/2026-10-15_source_work_order03.md

## 2026-10-15 · P1.5 T4 + PR #5 Integration Begin
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · SAFETY

- Isolated two-parent merge `496d495` on `integration/p15-t4-pr5-convergence-20261015` preserves 264 previously unique JSON history entries and both Markdown change histories.
- T4-D independent Codex evidence and required final Linux/Windows CI SUCCESS recorded (Windows T4-D 5/5), without claiming a new Codex verdict or integrated CI PASS.
- New combined-branch Linux/Windows and Reporter/Web checks configured. Safety: no real orders/LLM, no production writes, no main merge or architecture relocation.
- Remaining P2 and real-report parity limitations remain open. See `docs/daily_patch/2026-10-15_p15_t4_pr5_integration_start.md`.

## 2026-10-15 · P1.5 Integration CI Initial-Run Correction
**Stage:** Architecture and Maintainability
**Tags:** TESTING · DOCUMENTATION · SAFETY

- Combined Reporting checks initially: 346 PASS / 2 FAIL. One invalid status was introduced by the integration patch entry; fixed `in_progress` to `current` without rewriting historical entries.
- A preexisting Windows-literal path test fails on Linux; match the existing T4 CI exact test-specific deselection in the additional Linux job. **NOT a Linux PASS; native Windows contracts remain mandatory.**
- Evidence: `docs/daily_patch/2026-10-15_p15_integration_ci_preexisting_scope.md`. No application code changes.

## 2026-10-15 · P1.5 Integrated Architecture Draft V1
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · DOCUMENTATION · REFACTOR

- Source-pinned seven-agent actual modules and proposed target tree; no code/file relocation.
- Added 12-entrypoint static import matrix SVG, structured sample, reproducibility script, and risk-classified architecture gap matrix.
- Dynamic/import consumer proof and trading authority remain SAFETY_LOCK / UNPROVEN; requires user/Codex approval.

## 2026-10-15 · P1.5 T4+PR5 Consumer Inventory and Codex Audit Gate
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCUMENTATION · SAFETY

- Tracked Python 2,226, AST static edges 4,486, literal dynamic edges 162, unresolved dynamic sites 58; full consumer audit GitHub run `38715884053` SUCCESS.
- Reporter evaluation 133 referenced modules and 327 cross-boundary static dependencies. Legacy Reporter/Monitor and operational script wrappers remain consumed; no blind folder delete.
- Root b.jsonl and _health.json have textual references, so no automatic deletion. See `docs/refactor/architecture/consumer_inventory_findings_20261015.md` and independent Codex task `docs/refactor/work_orders/P15-INTEGRATION-CODEX-CONSUMER-AUDIT-047.md`.
- Approval: architecture migration remains blocked pending scoped owner/consumer safety review and `ARCH_CONVERGENCE_APPROVED`.

## 2026-10-15 · P1.5 Integration Codex REWORK P1 / P2 Fix
**Stage:** Architecture and Maintainability
**Tags:** SAFETY · TESTING · BUGFIX · DOCUMENTATION

- Codex independent audit returned REWORK on integration `e207b612`. Deleted prohibited CI changed-files ZIP workflow; user-facing updated-files-only ZIP remains external to repo CI.
- Normalized Q10/Q12 baseline JSON writer on native Windows to explicit LF bytes matching `test_baseline_shared_owners.py` contract. Added native-Windows two-parameter pytest job; SUCCESS remains to be verified on new HEAD.
- Historical audit findings (106 PASS / 2 Windows FAIL, current T4 required CI pending at audit time) are preserved and not mislabeled ACCEPT.
- See `docs/refactor/work_orders/evidence/P15-INTEGRATION-CODEX-REWORK-048.md` and `docs/daily_patch/2026-10-15_p15_codex_rework_p1_p2_fix.md`.

## 2026-10-15 · P1.5 Integration P2 Writer-Line Correction
**Stage:** Architecture and Maintainability
**Tags:** BUGFIX · TESTING · DOCUMENTATION

- First P2 patch accidentally commented out `path.write_text()` by writing a literal backslash-n in a comment, resulting in FileNotFoundError on Linux and Windows. Explicitly acknowledged as a new regression.
- Restored the active write statement on its own Python source line while preserving required LF bytes; new CI is mandatory before acceptance. See `docs/refactor/work_orders/evidence/P15-INTEGRATION-CODEX-REWORK-048.md`.

## 2026-10-15 · P1.5 Single Active Branch T4 Scope and Windows Full Audit
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY · DOCUMENTATION

- T4-D original BASE→T4 FINAL scope remains pinned; integration HEAD rechecks Commander/UI immutable source and forbidden order authority without mislabeling PR5 libraries as T4-D modifications.
- Native Windows Q10/Q12 prior 2/2 PASS did not establish job PASS (data/originals and data/specs directory mtime fast-tier failure). Isolated native job now requires full file audit; unresolved directory-only metadata finding remains recorded.
- Single active development branch; no main merge/branch deletion before verification. Evidence: `docs/refactor/work_orders/evidence/P15-INTEGRATION-SCOPE-WINDOWS-FULL-AUDIT-049.md`.

## 2026-10-15 · P1.5 Single-Branch Design Source Preservation
**Stage:** Architecture and Maintainability
**Tags:** DOCUMENTATION · ARCHITECTURE · SAFETY

- Preserved 9 unique documents from `design/p1.6-orchestration` and 14 from `design/p2plus-architecture` (23 Markdown blobs; 138,450 bytes) in integration by original Git blob SHA.
- No application code or CI from these legacy branches was imported. All historic proposals remain unapproved. Branch deletion and main merge remain blocked until fresh integrated Linux/Windows CI + Codex audit.
- Original SHA map: `docs/refactor/branch_convergence/2026-10-15_preserved_design_branch_materials.md`.

## 2026-10-15 · P1.5 CI Main Transition
**Stage:** Architecture and Maintainability
**Tags:** CI · SAFETY · DOCS

- 변경: 통합 워크플로 4종과 PR #5 scripts contract가 `main` push 및 `main` 대상 PR에서도 실행되도록 트리거를 추가했습니다(통합 브랜치 트리거는 최종 승인까지 유지). 브랜치 삭제 후에도 T4 frozen-contract 회귀, Reporting/Web 호환, 141 wrapper, consumer inventory 검증이 유지됩니다.
- 분류: 브랜치 이력 전용 검사는 삭제하지 않고 분리했습니다 — CURRENT.md 단일 브랜치/MAIN_FROZEN 문장은 통합 브랜치에서 그대로 단언하고 main에서는 분류만 출력, CI-ZIP 금지는 모든 워크플로 대상으로 강화, ancestry fetch에서 `refactor/p1.5` 참조 제거.
- 제약: 고정된 stage SHA ancestry 검사는 엄격하게 유지되므로 main에는 merge commit으로 반영해야 합니다. hosted `pull_request -> main` 실행은 아직 관측되지 않아 BLOCKED로 기록했습니다.
- 안전: Guard/Approval/Step5C CAS/Broker 권한 및 런타임 코드 변경 없음, 레거시 p152 워크플로 파일 변경 없음.



## 2026-10-16 · P1.5 HYBRID-7 V3 Frozen and V1 Implementation Kickoff
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · DOCS · SAFETY

- 사용자 결정: HYBRID-7 V3 폴더 목표를 고정하고 설계 재반복 없이 실제 구현을 시작합니다. `libs/agents/` 7개 역할 표면을 최종 목표로 지정하되 빈 장식 폴더나 중복 실행 권한은 만들지 않습니다.
- 시작 작업지시서: `docs/refactor/work_orders/P15-TREE-MIGRATION-V1-052.md`. Scanner의 순수 `candidate_risk.py` 단일 모듈 이동을 소비자/ABI/monkeypatch 증명과 정확한 동작 동일성 조건으로 승인했습니다.
- 현재 커밋은 지시·정책·문서만 갱신합니다. 실제 파일 이동, Codex 독립 승인, P1.5 최종 완료를 의미하지 않습니다.
- 활성 개발 브랜치는 `integration/p15-t4-pr5-convergence-20261015`; `main`과 실거래·Broker·CAS·UEF 권한은 그대로 보존합니다.

## 2026-10-16 · P1.5 Tree Migration V1-052 (첫 물리 이동)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING

- 변경: Scanner `libs/runtime/scanner/candidate_risk.py`를 `libs/agents/scanner/candidate_risk.py`로 byte-identical 이동했습니다. 기존 경로는 `sys.modules` module-object identity shim이어서 두 import 경로는 같은 모듈 객체이며 구현은 하나입니다.
- 검증: BASE 본문에서 실행한 115개 frozen 입력의 결과가 key 순서까지 동일, 유일한 소비자 `scanner_node.py`는 수정하지 않았고 T4-A frozen Scanner 계약과 stage gate 통과, old/new-first import identity 및 monkeypatch 공유 확인.
- 경계: rank owner·Broker·LLM·Supervisor/Executor·State·운영 쓰기 변경 없음, 다른 Scanner 경로는 이동하지 않음. 독립 Codex 감사 후 V2.


## 2026-10-16 · V1-052 ACCEPTED / V2-053 작업지시서 GitHub 등록
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · DOCS · WORKFLOW

- V1-052: GPT 수용 `PASS_WITH_FINDINGS`; Blob 일치, old/new module identity, 115/115 BASE 사례, 13/13 집중 테스트, 필수 CI 3/3 SUCCESS. Codex 지적 P2 문서 표현 두 건은 V2 첫 작업에서 수정.
- V2-053 작업지시서와 V1 승인 근거를 GitHub 통합 브랜치의 정식 문서 경로로 등록. `CURRENT.md`와 Claude/Codex 시작 지침은 활성 작업 V2-053 한 건만 지정.
- 본 커밋은 문서와 UI 변경 이력만 반영하며 V2의 다섯 모듈은 아직 이동하지 않음. 운영 주문·Broker·LLM·Step5C·UEF·Q10/Q12 변경 없음.

## 2026-10-16 · P1.5 Tree Migration V2-053 (Scanner context 5개 이동)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCS

- 변경: `feature_coverage`, `sentiment_inputs`, `scoring_inputs`, `macro_focus`, `macro_chart_fit`를 `libs/runtime/scanner`에서 `libs/agents/scanner/context`로 byte-identical 이동했습니다. 기존 경로는 module-identity shim이며 구현은 하나입니다. V1-052 Gap Matrix 문구(P2)도 먼저 정정했습니다.
- 검증: BASE 트리에서 공개 Scanner wrapper로 생성한 136개 frozen case를 예외·key 순서까지 정확히 재현, T4-A Scanner frozen 계약과 stage gate 통과.
- 경계: `scanner_node.py`, 랭킹/선택, Broker, LLM, Supervisor/Executor, 운영 쓰기 변경 없음. V3 전 독립 Codex 감사 대기.


## 2026-10-16 · V2-053 Codex FAIL / 재작업 054 활성화
**Stage:** Architecture and Maintainability
**Tags:** SAFETY · TESTING · DOCS

- Codex 판정: **FAIL**. 실제 이동된 Scanner 5개 본문 Blob과 136개 BASE/FINAL 사례 및 필수 CI는 성공했지만, Wave B `_owner_file()` 검증기가 추가 실행문과 잘못된 import 대상이 포함된 Shim을 허용하는 P1 결함 발견.
- 기존 전체 회귀의 37개 FAIL/ERROR가 BASE에서도 같다는 주장은 테스트 ID·명령·로그 비교 자료 부족으로 **BLOCKED**. 기저 결함으로 확정하지 않음.
- `docs/refactor/work_orders/P15-V2-053-REWORK-054.md` 작업 하나만 활성화. 수정은 AST fail-closed 게이트 + 음성 테스트 + 동일 환경 BASE/FINAL 실패 매니페스트 + CURRENT 문서 정정 범위로 제한.
- 이 커밋은 코드 실행 경로 변경 없이 지시서·사용자 UI 노트만 업데이트. V2 최종 승인, V3 구현, main 병합 모두 보류.

## 2026-10-16 · P1.5 V2-053 Rework 054
**Stage:** Architecture and Maintainability
**Tags:** TESTING · SAFETY · DOCS

- 변경: Wave B moved-body gate가 허용목록의 V2 identity shim 5개만 따라가며, shim 소스 AST를 import 없이 정확히 검증합니다. 추가 실행문·잘못된 import 대상·순서 변경은 모두 실패합니다.
- 검증: Codex 반례 3개를 포함한 22개 변이 전부 거부(기존 헬퍼는 12개 통과), Wave B 768/768 유지. V2 이전/재작업 트리를 같은 명령으로 광역 실행한 결과 FINAL 전용 실패 0, 원인 상이 0, 동일 서명 37, BASE 전용 1(초 경계 flake).
- 상태: Scanner 구현·shim·랭킹·거래 권한 변경 없음. V2 승인과 V3는 Codex 델타 감사 대기.


## 2026-10-16 ? P1.5 Rework 054 Optimized Verifier and Observed Failure Evidence
**Stage:** Architecture and Maintainability
**Tags:** TESTING ? SAFETY ? DOCS

- Explicit raises keep shim validation active under Python -O. Original 31 tests retained; optimized-child regression rejects all 21 source mutations including the three Codex counterexamples.
- Preserved JUnit provides exception/location for BASE 38 and FINAL 37 records, with 37 equal observed signatures. No broad reruns. Raw hashes identify retained evidence; complete semantic causes and original SHA/environment provenance are not established and remain BLOCKED.
- Codex implementation supplement under user instruction; a separate independent 054 delta audit is required. Scanner implementation/shims and protected runtime paths unchanged. V3 BLOCKED.


## 2026-10-16 · V2 구조 한정 승인 / V3-055 구현 시작
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · DOCS · WORKFLOW

- V2-053/054: 코드 이동과 모듈 동일성, BASE 기반 136개 사례, 엄격 AST/-O 검증, 필수 CI가 통과해 **구조 변경만 조건부 수용**. 광역 테스트 37건의 실패는 미해결이고 원본 실행 SHA/환경 출처는 BLOCKED. 이전 커밋 작성 참여로 인해 감사 독립성에 한계가 있다는 점도 명시.
- V3-055: 기존 동결 목표 트리 아래 Scanner read-only Projection 모듈 후보 5개를 안전 입증된 경우에만 물리적으로 이동하도록 GitHub 작업지시 등록.
- 이 커밋에는 V3 코드 이동이 없으며 실거래, Rank-1, Broker/LLM/Step5C/UEF, main 병합 모두 금지 유지.

## 2026-10-16 · P1.5 Tree Migration V3-055 (Scanner projection 5개 이동)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCS

- 변경: `candidate_context_projection`, `control_eligibility`, `output_payloads`, `output_snapshots`, `selection_evidence_projection`을 `libs/runtime/scanner`에서 `libs/agents/scanner/projections`로 byte-identical 이동했습니다. 기존 경로는 module-identity shim(엄격 AST 검증 통과)이며 구현은 하나입니다.
- 검증: BASE 트리에서 기록한 218개 케이스(실제 호출 입력 + 엣지)를 JSON key 순서까지 정확히 재현, T4-A Scanner 계약·second-pass·Wave B 768/768 통과, 엄격 검증 음성 테스트는 `python -O`에서도 통과.
- 경계: `scanner_node.py`, 랭킹/선택, Broker, LLM, Supervisor/Executor, 운영 쓰기 변경 없음. SAFETY_BLOCKED 없음. V4 전 독립 Codex 감사 대기.


## 2026-10-16 · V3-055 구조 범위 한정 승인 / V4-056 구현 지시 등록
**Stage:** Architecture and Maintainability
**Tags:** ARCHITECTURE · DOCS · WORKFLOW

- V3-055: Codex PASS_WITH_FINDINGS를 수용하여 Scanner Projection 구현 5개 이동을 구조 범위 내 승인. BASE 구현 Blob 5/5 동일, 218개 BASE Frozen 결과, T3·Wave B·T4-A 검증, 필수 CI 성공. 실제 Git diff는 22개 경로.
- P2 부채: 로컬 SKIP 1건 이유 미검증, BASE caller 캡처의 모듈 라벨 82건 보정 근거/원본 hash 보강 필요, 6.2 MiB fixture 중복 입력 1건/축소 후보. 기존 광역 오류 37건 미해결, 과거 실행 SHA·환경 출처 BLOCKED.
- V4-056: 동결된 HYBRID-7 V3 트리를 바꾸지 않고 Scanner policy R3 helper 5개만 개별 안전 검증 후 이동하도록 GitHub 작업 지시. 이번 커밋에는 실제 V4 소스 이동 없고 Broker/LLM/Step5C/UEF·main 변화 없음.

## 2026-10-16 · P1.5 Tree Migration V4-056 (Scanner 정책 helper 5개 이동)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCS

- 변경: `symbol_prior`, `blocker_family_overlay`, `repeat_guard`, `guidance`, `compatibility`를 `libs/runtime/scanner`에서 `libs/agents/scanner/policy`로 byte-identical 이동했습니다. 기존 경로는 3문장 module-identity shim이며, Wave B fail-closed 허용목록은 정확히 이 5쌍만 확장했고 엄격 AST 검증과 `python -O` 음성 테스트를 유지합니다.
- 검증: 공개 Scanner wrapper로 BASE 트리에서 생성한 318개 케이스(시계 고정, SCANNER_* 환경 통제, 예외·입력 변경 기록)를 key 순서까지 정확히 재현, T4-A Scanner 계약·Wave B 768·T3 gate 통과.
- 경계: `scanner_node.py`, 랭킹/선택, Broker, LLM, Supervisor/Executor, 운영 쓰기 변경 없음. SAFETY_BLOCKED 없음. 독립 Codex 감사 대기.

## 2026-10-16 · P1.5 P15-058 Scanner V4 + Strategist S1 통합
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · SAFETY · DOCS

- Gate A: repeat_guard가 실제로 읽는 `persisted_state.recent_monitor_blocks`와 중첩 `scanner_repeat_guard` 정책으로 repeat_count > 0 케이스를 BASE에서 먼저 생성한 별도 fixture(286)로 추가하고 FINAL과 완전 일치함을 확인했습니다. V3 디렉터리 검사는 버전 allowlist 기반 정확 일치로 복원, 쓰기 감사 mtime은 재현되지 않아 UNRESOLVED(메타데이터 한정)로 기록했습니다.
- Gate B: Strategist S1 승인 경로 16개만 선택 통합(브랜치 병합·공통 문서 복사 없음), Wave B 엄격 AST allowlist를 Scanner 10 + Strategist 5 = 15쌍으로 확장하고 exact-set·잘못된 shim 거부·`python -O` 음성 테스트를 유지했습니다.
- 경계: 주문·LLM·Step5C·UEF 변경 없음, Reporter/Monitor 미착수, main 병합 없음. 독립 감사 대기.
## 2026-10-16 - P1.5 Test Harness Performance First Slice
**Stage:** Test Infrastructure
**Tags:** TESTING / SAFETY / PERFORMANCE / DOCS

- Identical Wave B 768 + T3 14: 782 PASS, 0 FAIL/ERROR/SKIP. 157.67s -> 49.07s with fresh bytecode prefix, 68.88% reduction. Not whole-suite timing.
- Cache immutable pinned Git text/metadata only; no current Owner/shim, mutable AST or verdict cache. Existing assertions unchanged.
- Windows TEMP cleanup queries status without os.kill(pid, 0). No runtime/golden/expected-value/skip/CI changes.
- Reporter R1-059 and Monitor M1-060 deferred. PERF-1 publication authorized on perf/p15-harness-perf1-20261016 only; integration/main unchanged. PERF-2 analysis follows, with CI implementation in a separate commit after equivalent-coverage proof. Linux and hosted post-change validation pending.
- Evidence: docs/daily_patch/2026-10-16_p15_test_harness_performance.md.
## 2026-10-17 - P1.5 PERF-2A Variant ID Inventory
**Stage:** Test Infrastructure
**Tags:** TESTING / PERFORMANCE / SAFETY / DOCS

- Canonical IDs/order retained without payload deepcopy; default replay payloads, sampling, existing negatives and frozen fixtures unchanged. No execution-result cache.
- BASE parity: 411 records / 10,910 variants, sample_mod=1/4; new equivalence 15 PASS. Existing paired negatives 3 PASS before/after, 111.78s -> 7.00s locally (93.74%); optimized Python 3 PASS. Not whole-CI timing.
- Only perf/p15-perf2a-20261017 is published. PERF-1/common runtime/workflows unchanged. Claude audit and combined integration review pending; no main merge or next project.
- Evidence: docs/daily_patch/2026-10-17_p15_perf2a.md.


## 2026-10-17 · Agentra Work Reporter Monitor Whole-Role Activation 2026-10-17
**Stage:** Architecture and Maintainability
**Tags:** DOCS

- 사용자 착수 승인에 따라 Reporter(Claude)/Monitor(Codex) 역할 전체 프로젝트와 교차 감사를 활성화했습니다. Runtime BASE d773709, 18개 seed blob 재사용.
- 공통 파일은 Work 단일 담당, 역할 내부 순수 범위는 원장 기록 후 연속 진행. 기존 6시간 보고 유지, Auto-review 권한 심사와 코드 감사를 구분합니다.
- 로컬 작업자는 아직 NOT_STARTED입니다. 코드·테스트·workflow·기존 통합/main 변경 없음. 근거: `docs/refactor/work_projects/ACTIVATION.md`.

## 2026-10-18 · P1.5 isolated shared candidate
Monitor retained-boundary checkpoint: 359 retained definitions excluded from additional moves. Static evidence only; shared gates, hosted CI and independent review pending. No deployment or whole-role acceptance.

Shared candidate: strict Reporter 313-body facade restoration, Monitor 14-module/20-body mappings, F1 historical provenance and F2 router discovery implemented. Shared contracts 45 PASS normal/-O; FastAPI 0.143 API 9 PASS. Whole selected matrix: 2865 PASS / 1 FAIL / 24 SKIP; UEF9 failure under investigation, CI and independent review pending. No final acceptance.

Expanded direct negative gates: 75 PASS under -O. UEF9 failure reproduced unchanged on BASE; no waiver. Final test scratch constrained to ignored candidate .agentra-worktmp under sandbox policy 15.

Exact code SHA 95c11cacb9c73ae3d97d89e2061372762efff12b: Windows normal and -O each 2895 PASS / 1 FAIL / 24 SKIP (2920 tests, zero setup ERROR). FastAPI 0.143 normal/-O each 9 PASS. No full PASS; baseline-reproduced UEF9 failure and missing real-artifact skips retained. Hosted CI and independent Claude audit NOT_RUN.

## 2026-10-18 · P1.5 Codex P2 CI portability candidate

Reporter 예외 비교는 같은 too-many 방향과 expected 값에서 선택적인 got 상세만 허용합니다. Monitor 기록 해시는 Python 버전 간 동일한 증거 직렬화 형식으로 검증하며 원본 fixture와 런타임은 보존합니다. Codex 브랜치의 필수 CI와 자식 인터프리터 최적화 검증을 연결했습니다.

기존 호스팅 CI는 실제 FAIL이었습니다. Linux에는 증거 직렬화 2건과 UEF9 1건, Windows에는 UEF9 1건이 남았습니다. 새 SHA의 CI 및 Claude 독립 감사는 별도 확인해야 하며 전체 통합 PASS를 선언하지 않습니다. 실데이터 검증과 Web build·desktop/mobile visual smoke는 NOT_RUN입니다.

근거: `docs/daily_patch/2026-10-18_codex_p15_p2_ci_portability.md`, `docs/dev-team/integration/CODEX_P2_CI_CHECKPOINT_20261018.md`.


## 2026-10-18 · P1.5 S5 shared gate preparation

Strategist 보조 함수 8개와 Owner 2개의 정확한 본문·ABI·import 복원 계약, p164/p172/Monitor 공유 게이트, 통합 기준 SHA의 닫힌 범위 검사를 준비했습니다. 이 준비 시점에는 독립 감사 전이라 S5 소스·테스트를 미적용하고 admission 잠금을 유지했습니다. 이후 동일 후보의 아래 S5 적용 항목에서 승인된 소스를 반영했습니다. 임의 import, 미이동 본문, Broker/Executor/Supervisor 변경을 거부하는 부정 검사를 유지합니다.

현재 변경은 게이트 준비이며 S5 런타임 동등성이나 통합 승인을 뜻하지 않습니다. UEF9 전체 FAIL과 실데이터 SKIP을 유지합니다. 새 CI·전체 저장소·실데이터·UI build는 실제 결과를 별도 기록합니다.

근거: `docs/daily_patch/2026-10-18_s5_shared_gate_preparation.md`, `docs/dev-team/integration/CODEX_S5_GATE_PREPARATION_20261018.md`.


## 2026-10-18 · P1.5 audited S5 shared candidate

독립 Codex 감사의 c4960c53 S5 구현 PASS 후, S5-A를 포함한 정확한 4개 소스·테스트 커밋만 Codex 개발 후보에 반영했습니다. 수치·텍스트 helper 8개를 Owner 2개로 옮긴 원본과 ABI·사용 시점 facade 조회를 보존하며, 정책·LLM 요청·거래 권한은 변경하지 않습니다. 정확한 공유 계약과 브랜치 범위 검사, S5 런타임·T4-C 고정 CI를 연결했습니다.

이 후보는 Claude 공동 감사와 별도 통합 승인 대기 상태입니다. 통합·main 반영은 없으며 UEF9 실패는 면제하지 않습니다. 실행 결과와 NOT_RUN 항목은 S5 공유 체크포인트와 Issue #14에 기록합니다.

근거: `docs/daily_patch/2026-10-18_s5_shared_gate_preparation.md`, `docs/dev-team/integration/CODEX_S5_GATE_PREPARATION_20261018.md`.

전체 CI에서 API 파일 재진입 시 발생한 fixture 설정 오류는 API 파일의 원래 연속 배치를 복원하고 실제 CLI 회귀 검사로 검증했습니다. endpoint 검사·fixture·기대값을 축소하지 않았습니다.


## 2026-10-18 · P1.5 UEF9 synthetic input isolation

UEF9 필수 계약은 고정된 비민감 합성 원천 JSON 4개를 명시적 reports_root로 전달합니다. 기존 생산 로직과 7 CONDITIONAL / 84 NOT_COMPARABLE 기대값을 유지하며, 운영 보고서·실거래 자료는 복사하지 않았습니다. 누락·변조·추가 파일, 읽기 거부·경로 탈출, 시계·hash seed 차이를 검증합니다.

실행한 normal/-O·CI 결과는 Issue16/18과 체크포인트에 기록합니다. 합성 계약 검증은 실데이터 동등성이나 P1.5 최종 수용을 뜻하지 않으며 integration/main은 변경하지 않습니다.

근거: `docs/daily_patch/2026-10-18_uef9_synthetic_fixture.md`, `docs/dev-team/integration/CODEX_UEF9_FIXTURE_CHECKPOINT_20261018.md`.

합성 fixture 해시는 LF Git blob 바이트를 기준으로 고정해 Windows checkout과 CI의 줄바꿈 차이를 제거했습니다.


## 2026-10-18 · P1.5 S5 및 UEF9 선택 통합 (지팀장)
**Stage:** Maintainability · Evaluation
**Tags:** REFACTOR · AUDIT · EVALUATION

- `f8232e10` 독립 감사 PASS 변경을 통합 브랜치에 선택 적용합니다. Git 경로 34개 중 충돌하지 않는 32개는 기존 blob을 재사용, UI 패치노트 JSON/MD 2개는 루트 아키텍처 및 영구 운영 원칙 이력과 병합합니다.
- S5 여덟 helper의 기존 ABI·호출 시점 facade 보존, UEF9 기존 생산 로직의 합성 원천 입력 0/7/84 검증을 유지합니다.
- 코개발 필수 CI는 Linux/Windows normal/-O 각각 3144 PASS/0 FAIL/24 SKIP, API 2×9 PASS. 클검 Windows normal/-O 3168 수집·0 FAIL·0 ERROR·24 SKIP.
- 지팀장 루트 설계 문서 13개 경로는 S5 스코프의 별도 명시적 예외로 처리하되 거래 실행/정책 허용 경로는 확장하지 않습니다.
- **새 통합 SHA의 CI 결과는 아직 없음.** 실데이터 24 SKIP, 전체 저장소, UI 시각 검증 및 P1.5 최종 수용은 미완료. `main` 미변경.

근거: `docs/daily_patch/2026-10-18_uef9_synthetic_fixture.md`, `docs/refactor/architecture/P15_ROOT_TO_LEAF_REALITY_AND_CLEANUP_20261018.md`, GitHub Actions 39123404564.


## 2026-10-20 - P1.5 T3 IMMUTABLE GIT OBJECT HYDRATION HOTFIX 20261020
**Stage:** Dedicated CI hotfix PR candidate; independent review and integrated-SHA hosted checks pending. **Tags:** FIX / CI

- Integration BASE9b83ac6d4549eb8f5e0c0f9273ea011e4bf0709a. Dedicated hotfix branch contains only two workflow and paired UI note changes. Developer B source d9e77a3f remains on its original branch, not selected or merged.
- Both existing git fetch --no-tags origin commands additionally fetch 54bebe5ece0ac34c4f45df55c44889c9ce323e95. Immediately after the two original source-blob checks, git cat-file -e verifies the exact commit object. Existing set -euo pipefail, shallow-history check, original T3 pytest, pins and security guards remain unchanged.
- Original hosted run39396207960 had42PASS/1FAIL at T3: git diff of the pinned B source exited128 because the immutable object was absent from the runner. Remote/local object availability alone was not hosted success.
- Latest operator HOTFIX authorization clarifies normal Codex CLI editing and Git PR route are separately supported from the previous ordinary ChatGPT connector write limitation. No dangerous permission flags, policy changes or alternate path after an actual Codex denial.
- Actual local validation and exact-SHA fresh read-only Claude receipt are recorded in PR/Issue20 after commit. Required hosted checks on the resulting integration SHA remain pending GPT review/merge. No automatic integration/main merge, source/test/oracle modification, live trading or deployment.

Sources: `.github/workflows/p152-r2c-residual-regression.yml`, `.github/workflows/p15-integration-t4-regression.yml`, `tests/test_p159_current_owner_contract_gates.py`, `scripts/refactor/shared_strategist_contracts.py`.

## 2026-10-21 - P1.5 COMMANDER MONITOR PURE OWNERS 20261021
**Stage:** B1/B2 developer candidate; B3/B4 STAGE_CONTRACT_BLOCKED; peer/integration pending.

- Commander context/cache readiness pure bodies move to two canonical Owners, preserving runtime calls, environment/clock/memory IO, original threshold lookup, aliases and callbacks.
- Monitor B3/B4 attempts were rejected by the existing byte-identical protected-runtime gate (entry_cascade_projection.py was the first failure). All six approved Monitor sources remain exact BASE; attempted unused Owners removed. No safety/oracle/CI/gate edit.
- BASE normal193PASS/-O193PASS; exact candidate parity/negative/peer receipts in Issue20. Complete Commander runtime, Monitor migrations, real-data golden, full suite, CI and release are not claimed.
- Final normal455PASS/1FAIL and -O455PASS/1FAIL: historical shared_strategist_contracts.verify_b_scope rejects new Commander/test paths. Same retained-runtime test on exact BASE passes1/exit0. B1/B2 are source checkpoints only; B1-B4 STAGE_CONTRACT_BLOCKED, no gate/allowlist update or integration approval.
- Canonical Owner source whitespace normalized; no literal, logic or historical source/gate changes.

## 2026-10-21 - P15_COMMANDER_PURE_V1
**Stage:** Exact versioned contract candidate; peer and integration pending.

- Add isolated P15_COMMANDER_PURE_V1 exact-source admission for unchanged e4a59788 Commander B1/B2. Historical S5/B pins, source inventories, Reporter313/23 and Monitor14/20 proofs remain intact; both shared scope and runtime boundaries require the new version before admitting its nine runtime paths.
- All11 Commander source/test blobs pinned unchanged; exact closed source/proof inventory, checker hashes and paired notes preserve old339 records. Missing/extra files, byte/ABI drift, historical role mutations and new trading/LLM/write capability reject before admission.
- Monitor B3/B4 remain blocked. No historical allowlist/pin change, skip/waiver, new runtime behavior, CI/main/integration or PR modification. Actual normal/-O and independent results in Issue20.

## 2026-10-22 - P15_OPERATOR_BRIEF_PURE_READOUT_20261022
**Stage:** Structural source candidate; historical admission pending Tech Lead integration.

- Move four Operator Brief source-truth helpers and seven evidence/section readouts into two pure Owners. Existing module names re-export the same callables; builders keep facade use-time lookup, signatures, output order and fallback semantics.
- Input assembly248->123LOC; section assembly387->270LOC. New Owners139/134LOC; core, R3 compaction, routes/templates, historical gates and trading boundaries unchanged.
- Existing340 records preserved; BASE differential normal/-O tests and source-only Claude review are reported with exact SHA/exit in Issue20. Historical UI_PIN/current standalone scope rejection remains STAGE_ADMISSION_PENDING_GPT, not waived. No integration/main/CI or runtime-data claim.

## 2026-10-22 - P15_B_COMPOSED_INTEGRATION_20261022
**Stage:** B-only local integration candidate; exact source/test/peer/CI outcomes in Issue20.

- Select only approved d7ab8294..fedef7f7 B23paths; A and Q8 excluded. Issue20 6331537986 adds only the existing integration and p159 current-head test paths (25 total).
- Current p159 resolves two literal Commander and four literal Brief input identity reexports by symbol (Issue20 6331537986/6331883747), verifies exact import AST/canonical facade ABI/runtime identity, the unchanged delegated wrapper and accepted pure Owners. Current reexport modules and Owners match fedef source; unknown symbol/target/module/alias, duplicate import, rebinding, dynamic import and wrapper mutations fail closed. Original p159 executes unchanged on pinned BASE; historical ledgers and source proofs remain intact.
- Original historical predicates/pins/manifest remain unchanged and execute on actual pinned archive source fixtures. Exact current Commander/Brief sources are validated before historical projections; no wildcard, hash-chain framework, skip or authority change.
- Preserve341 records and paired Markdown history, append one integration record342. Core/R3, Broker/UEF/Step5C/Monitor policies, workflow and main remain unchanged. Do not infer hosted CI/integration PASS from this entry.

## 2026-10-22 - P15_B_CI_ADMISSION_REPAIR_20261022
**Stage:** B-only candidate; source review/Tech Lead integration and exact-SHA CI remain separate.

- Preserve historical Scanner pilot START and genuine17d3a4ac endpoint; exact current Commander package has four pinned files and one projections directory. Unknown roles/modules, altered source and authority paths still fail.
- Distinguish only18 literal untracked JUnit outputs proven in both unchanged CI workflows, with exact workflow/checkout provenance and real regular UTF-8 JUnit XML content. NUL/UTF-16, DOCTYPE/entities and hostile unknown/lookalike/content/provenance cases reject; no tracked/source/wildcard exemption. Later non-JUnit diagnostic TXT outputs remain outside the explicit exception and need separate integration handling, not a whole-workflow CI PASS claim.
- Retain original B25 source/proof scope plus two explicitly approved CI proof files; preserve all342 old records and append343. No production, historic pin, workflow, trading, A, integration or main modification. Results and peer verdict in Issue20.

## 2026-10-22 - P15_B_CI_DIAGNOSTIC_TEMP_20261022
**Stage:** B candidate; Tech Lead admission and integrated hosted CI pending.

- Move only the two bounded BASE/current T3.5 diagnostic TXT outputs and their notice consumer to RUNNER_TEMP/agentra-t35-diag in both existing workflows. Preserve original diagnostic calls, pinned BASE, arguments, continue-on-error, notice bounds/escaping and all other workflow text.
- Exact two-path admission compares complete workflows against frozen1bcf6290 with only three literal path substitutions. Unknown workflow/source changes and untracked diagnostic TXT still fail; no broad output exemption.
- Preserve343 historical entries, original historical predicates and accepted B sources; append344. No production, authority, A, integration or main change. Actual test/reviewer results are separate from hosted CI.

## 2026-10-22 - P15_B_OPERATOR_STRUCTURE_B1_20261022
**Stage:** Developer source candidate; GPT admission pending.

- Core2467->2309LOC: pure brief response/finalization inputs and run event/evidence shaping have coherent brief_parts/response.py and read_models/run_inputs.py Owners. Legacy facade signatures and use-time lookup remain; no IO/clock/LLM/retry/cache/persistence moves.
- Exact new-stage AST reconstruction protects all copied bodies, unmoved code, arguments and imports from green51bb7130. Historical pins and B29 proof remain separate; preserve344 old note records and append345. Top-level Python count35 remains35; implementation bodies move into packages rather than new root files.
