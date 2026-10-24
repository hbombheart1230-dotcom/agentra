# T00 — Agentra P1.5 전체 ROOT→LEAF 목표 폴더트리

> **목적:** 저장소 전체의 디렉터리 목표, 책임, 기존 경로 처리 기준을 한 곳에서 찾도록 하는 아키텍처 진입점. libs/agents 전용 설계가 아니다.
> **상태:** TARGET_STRUCTURE_PROPOSED / NOT_A_MOVE_AUTHORIZATION. 2026-10-24 작성. 세부 파일별 최종 경로는 RF 소비자 검증과 지팀장 판정 후 확정한다.
> **실물 기준:** integration/p1.5 @ 7e3190e064420e03b5eb2124122a33ee07b7c9aa, Git 추적 파일 4,079개. 아래 기존 폴더는 해당 Git tree에서 확인했다.
> **RF 전수 기준:** 63182ab27ecf889768003f637a40577ba1277f86, 3,985개 파일/298개 디렉터리/93개 RF. 기준선과 실물의 경로 차이는 별도 reconciliation 대상으로 남긴다.
> **정본 우선순위:** D00 안전·변경 규칙과 사용자 승인 > 동결 [TREE_V3_FROZEN](TREE_V3_FROZEN.md) 7개 역할·안전 경계 > 본 T00의 전체 폴더 목표 > [STATUS](../plan/STATUS.md) 및 [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv)의 작업·소유권 현황. CURRENT는 이번 작업 배정 포인터이며 목표 구조를 대체하지 않는다.

## 1. 무엇을 완료해야 하는가

P1.5는 다음 **10개 루트 디렉터리(.github, apps, config, data, deploy, docs, graphs, libs, scripts, tests)와 루트 개별 파일**을 ROOT→LEAF로 정리한다. libs/는 **26개 1차 패키지 전부**, libs/agents는 그중 하나이다.

- **목표:** 각 파일·함수의 단일 실제 Owner, 예측 가능한 패키지 이름·깊이, 응집된 작은 모듈, 최소 책임 공개 파사드, 검증된 정리/이동/유지/호환/안전 HOLD.
- **기존 동작 유지:** import/DTO/State/상태전이/예외/로그/출력 순서·바이트/LLM 호출/주문/스크립트·스케줄러 실행 경로를 변경하지 않는다. 승인 없는 main·실거래·안전 경계·CI 오라클 변경 금지.
- **동결 HYBRID-7 V3:** libs/agents/{commander,strategist,scanner,monitor,reporter,supervisor,executor}/ 가 최종 공개 역할 7개. 실제 엔진을 중복 생성하거나 비어 있는 장식용 폴더를 만들라는 뜻이 아니다.
- **포함:** 전체 93개 RF의 소유권, 신규/삭제/이동 파일 재조정, 기존 12개 P1.5.0~11 합격 기준, 독립 검증, 통합 SHA normal/-O 및 hosted Linux/Windows CI, Docker·UEF·replay·거래 안전 최종 동결.
- **비목표:** 새 전략, 새 LLM 판단 주체, LangGraph 엔진 교체(P1.6), 운영 토폴로지 변경, 대규모 이력 삭제.

## 2. 읽는 방법: 목표 트리와 현재 실물을 분리

아래 모든 기존 디렉터리는 **실제 Git에서 확인**했다. 트리는 실물 누락을 피하기 위한 전체 하위 디렉터리 인덱스이자 목표 경계의 출발점이다. 트리에 있다는 이유만으로 그 경로가 영구 최종 Owner이거나 이동 승인이라는 뜻은 아니다.

- **KEEP:** 공개/운영 계약 또는 단일 Owner로 계속 유지할 목표 경계.
- **CONSOLIDATE_AFTER_PROOF:** 현행 디렉터리는 유지하면서 실제 중복·소비자·외부 진입점을 확인한 뒤 정리한다. 입증 전 삭제·일괄 이동 금지.
- **SAFETY_LOCK:** 물리적 effect/승인/주문/UEF 출처 경계 유지. 사용자 별도 승인 없이는 변경 금지.
- **TARGET_ADD:** 현재 Git에 존재하지 않는 목표 공개 역할 폴더. 빈 스텁을 만드는 행위는 금지.
- **INVENTORY_HISTORICAL:** 과거 증거·레거시 파일. 링크·소비자 확인 후 보존/아카이브를 결정한다.

### 2.1 루트 9개(= libs 제외) 디렉터리 — 전체 확인된 하위 트리

표현되지 않은 개별 파일들은 기존 경로에 남아 있으며 FILE_COVERAGE/RF로 검증한다. 기존 공용 CLI, 진입점, 운영 스케줄러 파일은 하위 폴더가 있어도 무조건 이동시키지 않는다.

~~~text
agentra/
├── .github/
│   └── workflows/
├── apps/
│   ├── api/
│   │   ├── adapters/
│   │   ├── domain/
│   │   │   └── anomalies/
│   │   ├── infrastructure/
│   │   ├── models/
│   │   ├── routers/
│   │   └── services/
│   ├── operator_ui/
│   │   ├── static/
│   │   └── templates/
│   └── web/
│       ├── e2e/
│       └── src/
│           ├── app/
│           ├── features/
│           │   ├── alerts/
│           │   ├── data-quality/
│           │   ├── llm-operations/
│           │   ├── market/
│           │   ├── operations/
│           │   ├── opportunities/
│           │   ├── overview/
│           │   ├── patch-notes/
│           │   ├── performance/
│           │   ├── reports/
│           │   ├── runtime-status/
│           │   ├── strategies/
│           │   └── trades/
│           ├── shared/
│           │   ├── api/
│           │   ├── components/
│           │   ├── formatters/
│           │   ├── layout/
│           │   └── tables/
│           └── styles/
├── config/
│   └── skills/
├── data/
│   ├── eval/
│   │   └── m26_fixed_dataset_v1/
│   │       ├── execution/
│   │       ├── features/
│   │       ├── market/
│   │       ├── microstructure/
│   │       └── news/
│   ├── originals/
│   └── specs/
├── deploy/
│   ├── compose/
│   ├── docker/
│   ├── m28_launch_templates/
│   │   ├── linux/
│   │   └── windows/
│   ├── m28_registration_helpers/
│   │   ├── linux/
│   │   └── windows/
│   ├── m31_registration_helpers/
│   │   └── windows/
│   └── trading/
├── docs/
│   ├── alignment/
│   ├── architecture/
│   │   └── p2_plus/
│   ├── commander_control/
│   ├── daily_patch/
│   ├── debug/
│   ├── decisions/
│   ├── dev-team/
│   │   ├── checkpoints/
│   │   │   └── monitor/
│   │   └── integration/
│   ├── dev/
│   ├── development/
│   ├── en/
│   ├── env_plan/
│   ├── evaluation/
│   ├── execution_plan/
│   ├── ground_rules/
│   ├── kiwoom_truth/
│   ├── ko/
│   ├── milestones/
│   ├── observability/
│   ├── offline_alpha/
│   ├── operations/
│   ├── plan/
│   │   └── archive/
│   ├── profitability_recovery/
│   ├── q13/
│   ├── q13_q14_validation/
│   ├── q14/
│   ├── quant_trade_diagnosis/
│   ├── refactor/
│   │   ├── architecture/
│   │   ├── branch_convergence/
│   │   ├── evidence/
│   │   │   ├── p156_parity/
│   │   │   ├── p157_third_pass/
│   │   │   ├── p158_third_pass_t2/
│   │   │   └── p159_third_pass_t3/
│   │   │       ├── t302/
│   │   │       ├── t303/
│   │   │       ├── t31/
│   │   │       ├── t32/
│   │   │       ├── t321/
│   │   │       ├── t322/
│   │   │       ├── t35/
│   │   │       ├── t351/
│   │   │       └── t4a/
│   │   ├── p1_6/
│   │   ├── plan/
│   │   │   ├── criteria/
│   │   │   ├── done/
│   │   │   ├── pending/
│   │   │   ├── troubleshooting/
│   │   │   │   ├── closed/
│   │   │   │   └── open/
│   │   │   └── verification/
│   │   │       ├── claude/
│   │   │       └── codex/
│   │   ├── work_orders/
│   │   │   ├── archive/
│   │   │   └── evidence/
│   │   └── work_projects/
│   │       └── evidence/
│   │           ├── monitor/
│   │           │   └── continuous/
│   │           └── reporter/
│   ├── report_plan/
│   ├── report_upgrade_plan/
│   ├── research/
│   │   ├── evidence/
│   │   │   └── p1_1_real_run_acceptance_2026-09-29/
│   │   └── source_material/
│   ├── roadmap/
│   ├── runtime/
│   ├── runtime_entrypoint/
│   ├── runtime_memory/
│   ├── strategist_output/
│   ├── strategy_horizon_feedback/
│   ├── tactics/
│   ├── trade_report_plan/
│   ├── trading_agent_patch_notes_detailed_update/
│   └── web_observability/
├── graphs/
│   ├── nodes/
│   └── pipelines/
├── scripts/
│   ├── diagnostics/
│   ├── examples/
│   ├── maintenance/
│   ├── refactor/
│   └── research/
└── tests/
    ├── apps/
    │   └── api/
    ├── deploy/
    └── fixtures/
        ├── p1_5_p058_repeat_guard/
        ├── p1_5_strategist_s1_057/
        ├── p1_5_t35_agent_outputs/
        ├── p1_5_t4a_scanner_node/
        ├── p1_5_t4b_monitor/
        ├── p1_5_t4c_strategist/
        ├── p1_5_t4d_commander_ui/
        ├── p1_5_v1052_candidate_risk/
        ├── p1_5_v2053_scanner_context/
        ├── p1_5_v3055_scanner_projections/
        ├── p1_5_v4056_scanner_policy/
        ├── uef9_synthetic/
        ├── work_monitor/
        └── work_reporter/
~~~

### 2.2 libs/ 26개 패키지 — 전체 확인된 하위 트리 및 동결 추가 목표

~~~text
libs/
├── agent/                         # KEEP: legacy compatibility
│   └── executor/
├── agents/                        # HYBRID-7 public role surfaces
│   ├── commander/
│   │   └── projections/
│   ├── strategist/
│   │   ├── context/
│   │   └── output/
│   ├── scanner/
│   │   ├── context/
│   │   ├── policy/
│   │   └── projections/
│   ├── monitor/
│   │   ├── events/
│   │   └── projections/
│   ├── reporter/
│   │   ├── narrative/
│   │   └── read_models/
│   ├── supervisor/                # TARGET_ADD: public role contract only
│   └── executor/                  # TARGET_ADD: public role contract only
├── ai/
│   └── providers/
├── approval/                      # SAFETY_LOCK
├── catalog/
├── contracts/
├── core/
├── data_quality/
├── diagnostics/
├── execution/                     # SAFETY_LOCK
│   ├── executors/
│   └── guards/
├── kiwoom/                        # SAFETY_LOCK
├── llm/
├── market/
├── market_data/
├── news/
│   ├── providers/
│   └── scorers/
├── performance/
├── read/
├── reporting/
│   ├── alpha_research_board/
│   ├── baseline_btc_woori_tech/
│   │   └── vnext/
│   ├── baseline_samsung_hynix/
│   │   └── forward_validation/
│   ├── daily_report_runtime/
│   ├── evaluation/                # UEF canonical publisher SAFETY_LOCK
│   │   ├── canonical/
│   │   │   ├── adapters/
│   │   │   ├── forward/
│   │   │   └── metrics/
│   │   ├── memory_review/
│   │   ├── monitor_noop_attribution/
│   │   ├── same_symbol_sequences/
│   │   ├── stage2_authority/
│   │   ├── uef5/
│   │   ├── uef5_3/
│   │   ├── uef6/
│   │   ├── uef7/
│   │   ├── uef8/
│   │   └── uef9/
│   ├── metrics_report/
│   ├── opening_rank1_shadow/
│   ├── operator_period_summary_parts/
│   ├── operator_visibility_parts/
│   ├── quant_trade_diagnosis/
│   ├── reporter_bundle_runtime_parts/
│   ├── scheduled_intelligence/
│   ├── short_alpha_discriminator/
│   ├── trade_memory_projection_parts/
│   ├── trade_read_model_parts/
│   ├── trade_report/
│   │   ├── ai_facade_parts/
│   │   ├── ai_facade_r3_parts/
│   │   ├── markdown_clean_parts/
│   │   ├── markdown_clean_r3_parts/
│   │   ├── markdown_signal_parts/
│   │   ├── operator_parts/
│   │   ├── section_parts/
│   │   ├── section_seed_parts/
│   │   ├── services/
│   │   ├── summary_input_parts/
│   │   ├── summary_parts/
│   │   └── summary_render_parts/
│   ├── trade_report_markdown/
│   ├── trade_story/
│   ├── trade_story_assembly_parts/
│   ├── trade_story_evidence_parts/
│   ├── trade_story_facade_parts/
│   ├── trade_story_facade_r3_parts/
│   └── trade_story_human_parts/
├── research/
│   ├── alpha_competition/
│   ├── conditional_alpha_diagnosis/
│   ├── existing_evidence_mining/
│   ├── horizon_revision_backtest/
│   ├── integrated_trade_diagnosis/
│   ├── opening_rank1_deep_dive/
│   ├── opening_rank1_longitudinal/
│   ├── opportunity_engine/
│   ├── post_reclaim_alpha/
│   ├── rank1_feature_mart/
│   ├── structural_alpha/
│   └── structural_alpha_batch2/
├── risk/                          # SAFETY_LOCK
├── runtime/
│   ├── commander/
│   ├── controlled_mock_lanes/
│   ├── entrypoints/
│   ├── mock_exam_day/
│   ├── monitor/
│   ├── monitor_exit/
│   │   └── adapters/
│   ├── quant/
│   ├── scanner/
│   └── strategist/
│       ├── context/
│       ├── llm/
│       ├── output/
│       └── policy/
├── skills/
├── storage/
├── strategies/
│   ├── candidates/
│   └── v1/
├── supervisor/                    # SAFETY_LOCK
└── tools/
~~~

모든 비-에이전트 패키지를 다른 곳으로 일괄 합치지 않는다. 현재 경로를 기본 KEEP으로 보고, 오직 실제 중복 Owner와 소비자 검증을 마친 파일만 RF 단위로 재배치한다. 원래 경로가 public/CLI/monkeypatch/pickle/패키지 identity 경계이면 검증된 호환 shim 또는 KEEP_VERIFIED가 목표이다.

## 3. 10개 루트 영역별 목표 책임과 처리 기준

| 루트 | 정착시킬 목표 경계 | 실제 해야 하는 정리 및 유지 조건 | RF |
|---|---|---|---|
| .github/ | workflows = **최소·충분한 필수 CI** | 원래 7개 기준선 대비 현재 2개; 제거·통합·필수 검증 누락 여부를 대조. CI 오라클 임의 변경 금지 | RF-092 |
| apps/ | api/{routers,services,domain,models,adapters,infrastructure}, operator_ui/{static,templates,read model 역할}, web/{src/app,features,shared,styles;e2e} | Operator Brief 대형 core 분리, UI truth writer 금지, 라우트/자산/빌드·응답 바이트와 E2E 유지. 새 하위 폴더 생성은 검증된 Owner가 있을 때만 | RF-001~007 |
| config/ | skills + canonical config/defaults | 중복 env 조회·시크릿 노출 방지, 안전 기본값 변경 금지 | RF-090 |
| data/ | originals, specs, eval | 원본·버전·고정 fixture 구분. 운영 DB 및 비밀정보 이동 금지 | RF-091 |
| deploy/ | compose, docker, trading, OS별 templates/registration helpers | 실제 Windows/Linux 런처·예약 작업 참조로만 재배치·제거. 무승인 배포/재시작 금지 | RF-087~089 |
| docs/ | refactor/{architecture,plan,work_orders,evidence} 단일 운영 인덱스, daily_patch, UI patchnotes; 나머지 역사/도메인 문서 | 현재 여러 plan/development/dev-team/architecture 경로의 역할·링크 중복을 분류, 역사 증거 보존. CURRENT는 포인터, D00은 규칙, T00은 목표트리, STATUS는 상태로 분리 | RF-079~086 |
| graphs/ | commander_runtime.py = 운영 entry(KEEP), trading_graph.py = M17 테스트 spine(KEEP), nodes = State/호환 어댑터, pipelines = 실행 흐름 | 노드 대형 순수 함수의 Owner 분리; 실제 execute_from_packet 안전효과와 executor_node stub 혼동 금지 | RF-008~012 |
| libs/ | 아래 26개 도메인·역할 패키지와 공개 API | 7-role facade, Owner 증명, 계약 의존 역전, 레거시 shim 유지, 안전 권한 단일성 | RF-013~062 |
| scripts/ | diagnostics, examples, maintenance, refactor, research + root CLI/scheduler 호환 진입점 | 실행 wrapper/외부 job 참조 입증 전 대량 이동·삭제 금지; 진짜 단일 CLI Owner 확립 | RF-063~071 |
| tests/ | apps/api, deploy, fixtures + 기존 루트 contract/regression/safety tests | 관련 코드와 검증 Owner 연결, 중복 검사, normal/-O, fixture·임시 산출물 격리/보존, golden/오라클 불변 | RF-072~078 |
| 루트 11파일 | README·AGENTS·CLAUDE / conftest·pytest·sitecustomize / requirements·ignore 등 | 외부 진입/테스트·개발 규칙을 단일 정본으로 안내, 의심 산출물은 provenance 확인 후 결정 | RF-093 |

## 4. libs/ 26개 패키지별 최종 Owner 경계

| 1차 패키지 | 목표 책임 / 처리 | RF |
|---|---|---|
| agent | 레거시 M15 API 및 검증된 호환 진입점 KEEP | 040 |
| agents | Commander, Strategist, Scanner, Monitor, Reporter, Supervisor, Executor의 7개 공개 역할. 독립 호출·구현 Owner 증거 필요 | 013~017 |
| ai | AI 정책·provider 인터페이스 | 041 |
| approval | 승인 서비스, SAFETY_LOCK | 042 |
| catalog | API catalog/계획/요청 구축 | 043 |
| contracts | DTO/schema/serialization 공개 계약; runtime 역방향 의존은 parity 입증 후 해소 | 044 |
| core | 환경·설정·경로·기초 공용 로직 | 045 |
| data_quality | 신호·데이터 가용성 품질 | 046 |
| diagnostics | 읽기 전용 진단·상태 관측 | 047 |
| execution | guarded order execution/Step5C, SAFETY_LOCK | 048 |
| kiwoom | Kiwoom API·broker edge, SAFETY_LOCK | 049 |
| llm | 모델/라우터·프롬프트 효과 경계 | 050 |
| market | 시장 지표·외부 시장 상태 | 051 |
| market_data | 데이터 receipt·provenance | 052 |
| news | provider/scorer 뉴스 도메인 | 053 |
| performance | 성과·전략 메모리 입력 | 054 |
| read | readonly 데이터 어댑터 | 055 |
| reporting | 리포트 출력·artifact/read model·UEF publisher 유지; pure Reporter와 Research 경계 소비자 검증 | 028~035 |
| research | Q10/Q12·알파·사후 연구; 실행/선정 권한 금지 | 036~039 |
| risk | 단일 Supervisor 위험 판단 SAFETY_LOCK | 056 |
| runtime | 실제 공용 스케줄·State·시간·환경 primitive, legacy role owner 중 이전 입증된 순수 부분만 agents로 이동 | 018~027 |
| skills | IO skill/catalog adapter | 057 |
| storage | 영속화/저장 책임, 운영 write 안전 경계 | 058 |
| strategies | 후보 생성·전략 정책; Scanner 최종 랭킹과 중복 금지 | 059 |
| supervisor | intent state/승인·CAS 등 SAFETY_LOCK | 060 |
| tools | 경계가 분명한 저위험 공용 유틸 | 061 |

libs/__init__.py 등 libs 루트 단독 파일은 RF-062 대상. agents에 Supervisor/Executor public surface를 만들 때 기존 libs/supervisor, libs/risk, libs/approval, libs/execution, libs/kiwoom의 실제 권한·effect Owner는 이동하지 않는다.

### 대형/중복/역사적 분해 폴더의 판정 정책

- apps/operator_ui/data_access_core.py, graphs/nodes/{strategist_node,scanner_node,monitor_node}.py, graphs/commander_runtime.py, libs/contracts/agent_outputs.py, libs/runtime/intraday_monitor_signals.py, libs/reporting/의 거대 facade는 **줄 수 감소가 아니라 한 함수/책임의 실제 단일 Owner**를 기준으로 분해한다.
- libs/reporting/trade_report/*_parts 및 *_r3_parts, trade_story_*_parts 등은 디렉터리 이름만으로 최종 승인하지 않는다. 기존 호환성이 확인되면 KEEP, 중복 분해가 증명되면 실제 Owner로 통합, 소비자 없는 과거 파일만 안전 삭제 대상으로 제안한다.
- docs의 중복해 보이는 하위 폴더도 과거 감사 증거·링크를 지우지 않고 정본 탐색 경로를 정리한다.
- graph broker admission/approval/Step5C CAS, UNKNOWN quarantine, Q10/Q12 운영 lane, UEF canonical publisher, production DB, persistent effect/LLM semantics는 무승인 변경 불가.
- 새 folder 이름을 보기 좋게 만들기 위한 빈 패키지, misc/common2/owner_XXX 등 모호한 새 canonical Owner 금지.

## 5. RF-93과 T00 목표의 접점

RF-001~093은 전체 파일을 분담한 **작업·독립 검증 단위**이지 T00을 자동 충족했다는 의미가 아니다. 모든 RF의 최종 결과에 아래 항목을 경로별로 연결한다.

| 반드시 기록할 필드 | 의미 |
|---|---|
| SOURCE_PATH / TARGET_PATH | 원래 파일 → 최종 canonical Owner·공개 import 경로 |
| DISPOSITION | MOVE / KEEP_VERIFIED / WRAPPER_COMPAT / SAFETY_HOLD / REMOVE_PROVEN |
| OWNER / RF | 단일 책임자 + 독점 수정 RF |
| CONSUMERS | 직접 import, 동적 호출, scheduler/CLI, 테스트, UI/API, monkeypatch/pickle 확인 |
| EVIDENCE | BASE blob, candidate SHA, offline parity, independent peer, integration SHA, Linux/Windows normal/-O/CI |
| OPEN_DEBT | 아직 증명되지 않은 계약·파일·안전 예외; PASS와 섞지 않음 |

**차이 해소:** 3,985개 baseline CSV를 4,079개 실제 스냅샷에 무비판적으로 재사용하지 않는다. 최신 HEAD의 전체 경로 집합과 비교하여 신규/삭제/이동/무소유/다중 RF를 구별하고, 지팀장 승인으로 기존 RF의 소유권을 보완한다. 파일 94개 순증감은 새 파일 94개라는 뜻이 아니다.

**P1.5 DONE:** 최종 목표 폴더·Owner 충족 + 93개 RF 근거 기반 완료 + P1.5.0~11 합격 기준 + 전체 코드·구성·문서 경로 정합성 + exact integration SHA CI·독립검증 + 안전 HOLD 처리 및 사용자 Freeze 승인을 **모두** 만족해야 한다. T00의 존재나 폴더 생성 자체는 DONE 근거가 아니다.

## 6. 문서 탐색 원칙

- **작업 시작:** [CURRENT](../work_orders/CURRENT.md) → [D00](../../ENGINEERING_DELIVERY_POLICY.md) → **T00** (이 문서) → 해당 [RF](../plan/) 및 [STATUS](../plan/STATUS.md). 같은 SHA의 불변 문서를 반복해서 읽지 않는다.
- **설계 상세:** [HYBRID-7 V3 freeze](TREE_V3_FROZEN.md), [전체 10루트 현실·정리](P15_ROOT_TO_LEAF_REALITY_AND_CLEANUP_20261018.md), [26 packages owner snapshot](P15_ALL_LIBS_OWNERS_20261018.md). 이들은 역사/근거이며 T00 및 현재 RF 상태를 덮어쓰지 않는다.
- **상태·진행률:** STATUS만 업데이트. **배정:** CURRENT만. **안전·변경 권한:** D00만. **목표트리:** T00만.
- 최초 문서 작성은 architecture-only이며 **runtime/source/test/CI oracle, main, 거래·배포 설정 변경 없음**. 실제 디렉터리 이동은 해당 RF에 사전 기록하고 승인·검증 후 진행한다.
