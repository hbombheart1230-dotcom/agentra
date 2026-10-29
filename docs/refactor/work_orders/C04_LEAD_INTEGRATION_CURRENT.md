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

## 현재 할 일 — 2026-10-30 03:35 KST / A14 RF-034 TARGET_GAP 6 MOVE 선별 통합

- **새 A 코드 SOURCE:** [`3f7cea82b8ad2eb7298240c874f1abbbe5fe1224`](https://github.com/hbombheart1230-dotcom/agentra/commit/3f7cea82b8ad2eb7298240c874f1abbbe5fe1224), #11 댓글 `6504869860`, C02 명령 blob `19e29dc75b623abfe2d75562f9a3d20113e3ab15`. 직전 A `0d8dd2ad`→새 A diff는 **14 code/test paths**만: 원본 facade 2 + 신규 Owner 6 + 신규 테스트 6. C03 인라인 Owner/target 지정과 RF-034 상세의 builder `_large_cap_candidate` MOVE 확인. 신규 target 모두 integration 사전 미존재, 원본 facade 사전 blob A 이전과 동일 (`builder.py=812d5363`, `canonical.py=708e2552`).
- **실제 통합:** [`ae413b0ee1eeb86d203b465176aa4e1080f67cf3`](https://github.com/hbombheart1230-dotcom/agentra/commit/ae413b0ee1eeb86d203b465176aa4e1080f67cf3), parent `821a6e31c0c306cea0f1573d626d9a3c160623d9`, non-force expected-head fast-forward. 14/14 remote source/test Git blobs 정확 A와 일치; 기타 코드/테스트/RF/STATUS/workflow 미변경. Builder facade `47616817`, canonical facade `9daa794a`.
- **RF-034 이미 DONE, 구조 TARGET_GAP만 전진:** `builder.py::_prospective_concentrations` → `builder_prospective_concentrations.py::prospective_concentrations`, `_large_cap_candidate` → `builder_large_cap_candidate.py::large_cap_candidate`; `canonical.py::_latest_stage2_source/_stage2_candidate/_negative_control_candidate/_question_summaries` → `canonical_{stage2_source,stage2_candidate,negative_control,question_summaries}.py` 단일 Owner. 원래 이름/서명 얇은 facade wrapper 유지, 본문 중복 제거. `canonicalize_board` 및 effectful build/write·운영 상태·주문 코드는 변경 0. **신규 MOVE 6, RF DONE +0**. 기존 RF-034 05_DONE 재승격/재마이그레이션 금지.
- **G3_REUSE 범위:** A #11 `6504869860`의 `python -m pytest -q -p no:cacheprovider <A14 신규 6개 테스트>` **normal 45 PASS exit0** (A 작업자 보고), 관련 기존 11파일 **277 PASS, 24 SKIP**(실제 artifact 미존재). 통합 facade/Owner/test 14/14 exact A blob, 나머지 `alpha_research_board` subtree 16개 기존 blob 동일, `pytest.ini`/`requirements.txt` 및 직접 `contracts/loaders/large_cap_review/short_alpha` deps 동일. **C04 직접 pytest/-O/full suite NOT_RUN**, 신규 RF 전용 CI NOT_RUN. 신규 테스트는 fake/tmp_path 기반, 실계좌·실주문·운영 런 아님.
- **Actions:** 새 코드 SHA에서 push-trigger 자동 [run #40932608025](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/40932608025) 최초 조회 `in_progress`, 최종 성공 아직 주장 금지. Workflow는 offline safety 전용으로 신규 A14 targeted 테스트를 포함하지 않음. **수동 dispatch 0**; 문서 변경으로 CI 반복 금지. C05 G3 수용은 A exact-source normal targeted exit0 범위만 재사용, 자동 Actions는 독립 안전 증거로만 취급.
- **C05 NEXT:** RF-034 기존 DONE 보존하고 `_large_cap_candidate` 등 이번 6개 TARGET_GAP_CLOSED 실제 함수 이동과 SHA를 RF 원본/STATUS에 필요 시 반영(C05 단독). 다른 RF G1/G2 신규 READY가 있으면 다음 선별 통합. B #12 최신 `6503399021` `cf71eac7`은 기존 RF-044 wrapper 복구, 신규 B1-B6 MOVE/normal delivery 없음; 중복 통합 금지. RF-041 nonfinite price, RF-045 D2 TOCTOU SAFETY_HOLD 유지. RF-016/028/029 및 기타 DONE 동일 SHA 재검증·재통합 금지. 실계좌/실주문/배포/unsafe `--apply` 0.
