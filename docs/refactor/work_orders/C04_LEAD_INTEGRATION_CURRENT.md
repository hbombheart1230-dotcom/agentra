# C04 — 지팀장 · 선별 통합/CI

## 최신 우선 계약 — 구현 변경 묶음만 통합

C01/C02에서 나온 **실제 함수 이동 source+target blob**과 해당 normal targeted exit를 대조해 여러 준비 RF를 한 회차에 통합. 관련 경계 기존 PASS 증거 재사용, 변경 없는 정당한 KEEP은 새 테스트/CI dispatch 0. T00~T09 및 `rf_details/INDEX.md`의 SOURCE/TARGET Owner와 교차 RF 신규 경로 충돌 점검. 아래 이미 DONE인 RF-016/028/029 등 고정 반복 통합 지시는 신규 delta 없으면 적용 금지. 실거래/운영 효과 보호.


## FAST-3 G3 재실행 중복 방지 — C04 실제 판단 절차
- **1단계 대상 검증:** RF의 G1 원격 OWNER SOURCE SHA와 integration의 실제 파일별 Git blob을 대조하고, G2의 정확 SOURCE SHA·영향 테스트/실제 exit0 증거를 확인한다. 단순 문서 HEAD 변경으로 `SOURCE_CHANGED`를 판단하지 않는다.
- **2단계 증거 재사용:** 같은 대상 source+consumer 경계, 동일 테스트·의존성·CI 워크플로 상태에 대해 이미 성공한 정상 smoke/targeted pytest 또는 exact relevant CI 증거가 있으면 `G3_REUSE`로 수용한다. SOURCE 또는 테스트/의존성/보호 경계가 바뀌었으면 관련 범위만 재검증한다. 이전 기록의 PASS가 현재 코드에 해당하는지 불명확하면 재사용 불가, 하지만 full suite로 확대하지 않는다.
- **3단계 명시적 분기:** `KEEP_BLOB_IDENTICAL + VALID_RELEVANT_EVIDENCE` ⇒ **새 CI/pytest 실행 요청 0**, C05에 G3 증거 전달. `SOURCE_CHANGED` 또는 `TEST/DEPENDENCY/WORKFLOW_CHANGED` ⇒ 대상 변경분을 최소 통합하고 **관련 smoke/pytest 1회 또는 유효한 CI 1개** 확인. `DOCS_STATUS_ONLY` ⇒ **신규 CI dispatch 0 / smoke 반복 0**. `NO_MATCHING_EVIDENCE` ⇒ targeted smoke 1회만 실행(실행 환경 부재 시 G3 BLOCKED, 성공으로 간주 금지).
- **4단계 중복 dispatch 락:** 실제 GitHub Actions 수동 dispatch 이전 **기존 run의 head SHA, workflow/테스트 범위, conclusion을 조회**하고, 동등하게 성공한 run이나 같은 범위의 진행 중 run이 있으면 또 요청하지 않는다. 한 번 실행한 후 해당 `RF | owner blobs | integration/source SHA | relevant test list | PASS/FAIL | run_id 또는 local command | reuse/new/blocked` 근거를 #36 한 번만 보고한다. `python -O`/full hosted CI는 FAST-3 강제요건 아님.
- GitHub Actions `push` 트리거/branch protection·workflows·frozen oracle는 변경하지 않는다. 현재 `.github/workflows/p15-shared-candidate.yml`은 코드/테스트 변경 Push에서 자동 실행될 수 있으므로 이것을 삭제/비활성화한다고 주장하지 않는다. **중복 수동 실행 요청만 차단**하고 정상적인 자동 안전 CI는 유지한다.

## FAST-3 간소 통합 우선 (2026-10-29 승인)
- D00 §2 FAST-3가 아래 구 C1~C7/full independent C4/매 RF 전체 hosted normal/-O CI 요구보다 우선한다. **G1/G2 MET인 RF를 G3로 처리**한다. C05의 과거 7개 전수 수용을 기다리지 말고 실제 새로운 G1/G2 상태를 원격에서 확인한다.
- KEEP이면 해당 코드의 integration blob 동일성 확인 후 기존 정상 smoke/CI evidence 1개로 G3 제출 가능. 변경 있으면 최소 파일 선택 통합 후 **변경 경계 관련 smoke/pytest 1회** 또는 해당 integration SHA의 기존 관련 CI 성공으로 G3 제출한다. 전체 suite, -O 반복, 반대 전체 peer, 새 hosted CI 매번 강제하지 않는다.
- RF-016/028/029 및 RF-051/054/058은 DONE이므로 동일 SHA 재검증·재통합 금지. 새 C01/C02 G1/G2 실제 SOURCE와 RF Owner를 우선하고, 통합 결과 없으면 G3를 꾸며내지 않고 BLOCKED(scope/명령/NEXT). #36에는 신규 근거만 제출.
- mock/paper 실행은 모의 모드·계정이 확인된 환경에서만, 실제 런검증은 별도 단계. 실계좌 real mode는 무승인 실행 금지.

**입력:** [Issue #11 Claude A](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [Issue #12 Codex B](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [Issue #32 RunLab](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 **새 댓글 delta만** → C05가 실제 `04_LEAD_ACCEPTANCE`로 이동한 RF. [D00](D00_ENGINEERING_DELIVERY_POLICY.md) 준수. [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)은 결과 출력 전용. 오래된 A/B HANDOFF 재독·갱신 금지.

## 현재 상태 — 2026-10-31 05:35 KST / RF-035 A-05 8함수 통합, B G2 보류

- **정확 통합 코드 SHA:** `3f55688ccd045aa583d0b37b827aad5ccb579786` (parent `c081914190a8e97764b54f1718a7960e69d429cd`, tree `977ea418eff6d2a1943d1c6ef94199985d880e54`). Expected-head non-force fast-forward 성공. A remote `6df60c7d8ca1d954a66bb5c207d386a6671f8104`, #11 `6532635190`, C02 order blob `f031d0dfb45bfff445c04379150ec40e216bf64f`. Integration pre-SOURCE blobs `28f8a159` / `84718376` / `01e6ea1c` / `cd659475` all matched order; Owner 8 paths absent before integration. A 전체 브랜치 병합 없이 SOURCE4 + Owner8 + targeted tests8 = **20/20 exact Git blobs** 선별 통합/원격 확인.
- **RF-035 실제 BODY MOVE 8:** `symbol_trade_report.py`의 `_extract_trade_artifact_snapshot, _build_history_index, collect_symbols_for_day` → 각각 `symbol_trade_artifact_projection, symbol_trade_history_projection, symbol_trade_symbol_projection` (3); `report_source_helpers.py`의 `build_policy_surface_quality_snapshot, build_commander_route_summary` → `report_source_policy_projection, report_source_route_summary_projection` (2); `strategist_llm_summary.py`의 `build_strategist_llm_summary_payload, generate_strategist_llm_summary` → `strategist_llm_summary_payload_projection, strategist_llm_summary_writer_projection` (2); `market_regime_rail_review.py::classify_market_regime_rail` → `market_regime_rail_classification_projection` (1). SOURCE thin wrapper, Owner 실제 본문 단일화 및 call-time facade; A8 쓰기는 tmp_path fake 테스트 한정. 실주문·운영 효과 없음.
- **G2/G3:** A worker `python3 -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_*_owner.py` **normal 25 PASS exit0** (#11 `6532635190`), golden/fake/negative/facade parity; **G3_REUSE** scoped. C04 직접 pytest 0, 수동 CI dispatch 0. A wide regression 894 PASS/1 FAIL은 baseline에서도 동일 실패라는 A 보고이며 전체 PASS 주장 금지. 정확 코드 SHA의 GitHub status API statuses=[] 및 PR-filtered workflow-runs=[]: 자동 push CI의 성공 여부 **NOT_VERIFIED**, CI SUCCESS 주장 금지. C05는 G2 scoped 증거와 정확 integration blob을 재판정.
- **B RF-063:** B remote HEAD `88a1a763d1053d0227afbe1f9920405dfa58ebc6`에서 `_build_bundle_repair_command` 신규 Owner BODY MOVE 1건 확인(기존 `_read_json, _resolve_trade_context` 포함 부분 3건). 이번 신규 commit은 SOURCE+Owner 2개 파일, 신규 targeted test/normal exit0 증거 없음, #12 최신 `6524800387` 이후 신규 댓글 없음. **G1 PARTIAL / G2 NOT_VERIFIED / G3 NOT_INTEGRATED**. C01 B3–B9 잔여 + 테스트 증거 확보 후 선별 검토.
- **B RF-065:** `run_phase5_validation_bundle.py`의 `phase5_markdown` 미import runtime NameError 결함, 정상 테스트 수정 원격 미확인. **G3 BLOCKED**. B0 import + fake parity normal exit0 요구.
- **성과/보호:** REFACTOR_CHANGED=8 / TARGET_GAP_CLOSED=8 / RF_DONE_DELTA=0 (RF-035 기존 DONE 32/93). C05만 STATUS/단계 변경. RF-016/028/029 및 RF-051/054/058 동일 SHA 재통합 0. RF-044 facade smoke NOT_VERIFIED. RunLab Exited(255)/RUN_SOURCE_SHA UNKNOWN 별도 SAFETY_HOLD. 실계좌/실주문/운영 재시작·배포/보호 Broker·Guard·Step5C·UEF 변경 0.
- **NEXT:** B RF-065 import/normal targeted와 RF-063 신규 원격 code+test SHA·exit0 확보 시 최소 G3 통합. A 동일 20 blob 반복 통합/pytest/수동 CI 금지. #36에 정확 SHA·20/20 blob·25 PASS 재사용·B 차단 인계. 문서 전용 변경 CI/pytest 0.
