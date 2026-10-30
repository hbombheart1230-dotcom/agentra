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

## 현재 상태 — 2026-10-30 18:35 KST / RF-035 A8 선별 통합, B 신규 원격 없음

- **코드 통합 SHA:** `d0475b492695b1e833c9c0c60aec52e42eb43396` (parent `d6eda9198d22e77fc2a9c7a52f127d086ed5548e`). expected-HEAD 비강제 fast-forward push 성공. GitHub compare 1 commit/11 code+test paths, 원격 11/11 blob exact 확인. 새 실제 BODY MOVE 8개, RF_DONE_DELTA=0.
- **A / RF-035 A1–A8:** #11 [6519315242](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6519315242), A SOURCE `dc2bc153a522f9a296f4ae81b354d0afe7885941`, C02 order blob `5667dbcbe5c3e9f75d6edb828cb93b709ea75228`. `libs/reporting/llm_artifacts.py` integration before `9721ccd6d3b61ed78109faa670481ea5134914a1` == A actor before; after `27aea755e3ab9a3143affbd28294e4c8c775b8ca` exact actor. 실제 8 함수 `iter_trade_dirs`, `find_trade_dir`, `_looks_like_trade_day_dir`, `misplaced_trade_day_root`, `resolve_trade_day_root`, `iter_trade_day_roots`, `list_misplaced_trade_day_roots` → 신규 단일 Owner `llm_artifacts_trade_lookup.py`, `llm_artifact_paths` → `llm_artifacts_run_paths.py`. 원시그니처 얇은 wrapper, 의존 helper call-time facade, read-only/path lookup. A 정상 targeted `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_trade_lookup_*_owner.py tests/test_p15_rf035_llm_run_paths_owner.py` **24 PASS exit0**. 현재 통합 11/11 동일 blob에 한정하여 **G3_REUSE**. C04 직접 pytest 0, full suite 0, 수동 CI dispatch 0.
- **B / RF-065 B1–B8:** #12 [6519207511](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6519207511), C01 blob `939ad923b91e1cae77317c4ba66840f3c9a9f6e3`. `scripts/research/run_phase5_validation_bundle.py` wrapper 생성에서 `SyntaxError` → 로컬 작업 트리 폐기, **원격 신규 코드·테스트 SHA 0 / G1·G2 NOT_MET / NOT_INTEGRATED**. B remote `f3a907bde784bfa5056100161c8b461c94562589` 그대로. NEXT B exact signatures로 B1–B8 재구현·정상 targeted·원격 push. 기존 RF-063 B9의 `globals().update`/stale facade seam G3_BLOCKED는 수정된 신규 SHA가 없어 그대로 보류.
- **CI:** 자동 push safety run [#41034168109](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/41034168109) 최초 조회 IN_PROGRESS, conclusion NOT_VERIFIED. 신규 targeted 24 PASS와 별개. RF-044 전체 체크아웃 facade-call smoke도 NOT_VERIFIED, 별도 성공으로 대체 금지.
- **C05 인계:** #36에 정확 통합 SHA·11/11 blob·G3_REUSE 및 B 차단을 1회 보고. RF-035 기존 DONE의 TARGET_GAP_CLOSED +8, **RF_DONE_DELTA=0**; 마지막 독립 확인 DONE 32/93. RF-016/028/029·051/054/058 동일 SHA 재통합 0. RunLab safety HOLD 보존, 실주문/real mode/Guard/Broker/Step5C/UEF/운영 재시작·배포 금지.
