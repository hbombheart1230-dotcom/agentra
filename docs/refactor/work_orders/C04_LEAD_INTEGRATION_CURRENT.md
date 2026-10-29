# C04 — 지팀장 · 선별 통합/CI

## FAST-3 G3 재실행 중복 방지 — C04 실제 판단 절차
- **1단계 대상 검증:** RF의 G1 원격 OWNER SOURCE SHA와 integration의 실제 파일별 Git blob을 대조하고, G2의 정확 SOURCE SHA·영향 테스트/실제 exit0 증거를 확인한다. 단순 문서 HEAD 변경으로 `SOURCE_CHANGED`를 판단하지 않는다.
- **2단계 증거 재사용:** 같은 대상 source+consumer 경계, 동일 테스트·의존성·CI 워크플로 상태에 대해 이미 성공한 정상 smoke/targeted pytest 또는 exact relevant CI 증거가 있으면 `G3_REUSE`로 수용한다. SOURCE 또는 테스트/의존성/보호 경계가 바뀌었으면 관련 범위만 재검증한다. 이전 기록의 PASS가 현재 코드에 해당하는지 불명확하면 재사용 불가, 하지만 full suite로 확대하지 않는다.
- **3단계 명시적 분기:** `KEEP_BLOB_IDENTICAL + VALID_RELEVANT_EVIDENCE` ⇒ **새 CI/pytest 실행 요청 0**, C05에 G3 증거 전달. `SOURCE_CHANGED` 또는 `TEST/DEPENDENCY/WORKFLOW_CHANGED` ⇒ 대상 변경분을 최소 통합하고 **관련 smoke/pytest 1회 또는 유효한 CI 1개** 확인. `DOCS_STATUS_ONLY` ⇒ **신규 CI dispatch 0 / smoke 반복 0**. `NO_MATCHING_EVIDENCE` ⇒ targeted smoke 1회만 실행(실행 환경 부재 시 G3 BLOCKED, 성공으로 간주 금지).
- **4단계 중복 dispatch 락:** 실제 GitHub Actions 수동 dispatch 이전 **기존 run의 head SHA, workflow/테스트 범위, conclusion을 조회**하고, 동등하게 성공한 run이나 같은 범위의 진행 중 run이 있으면 또 요청하지 않는다. 한 번 실행한 후 해당 `RF | owner blobs | integration/source SHA | relevant test list | PASS/FAIL | run_id 또는 local command | reuse/new/blocked` 근거를 #36 한 번만 보고한다. `python -O`/full hosted CI는 FAST-3 강제요건 아님.
- GitHub Actions `push` 트리거/branch protection·workflows·frozen oracle는 변경하지 않는다. 현재 `.github/workflows/p15-shared-candidate.yml`은 코드/테스트 변경 Push에서 자동 실행될 수 있으므로 이것을 삭제/비활성화한다고 주장하지 않는다. **중복 수동 실행 요청만 차단**하고 정상적인 자동 안전 CI는 유지한다.

## FAST-3 간소 통합 우선 (2026-10-29 승인)
- D00 §2 FAST-3가 아래 구 C1~C7/full independent C4/매 RF 전체 hosted normal/-O CI 요구보다 우선한다. **G1/G2 MET인 RF를 G3로 처리**한다. C05의 과거 7개 전수 수용을 기다리지 말고 실제 새로운 G1/G2 상태를 원격에서 확인한다.
- KEEP이면 해당 코드의 integration blob 동일성 확인 후 기존 정상 smoke/CI evidence 1개로 G3 제출 가능. 변경 있으면 최소 파일 선택 통합 후 **변경 경계 관련 smoke/pytest 1회** 또는 해당 integration SHA의 기존 관련 CI 성공으로 G3 제출한다. 전체 suite, -O 반복, 반대 전체 peer, 새 hosted CI 매번 강제하지 않는다.
- RF-016은 DONE이므로 재검증 금지. 신규 최우선 RF-029, 다음 RF-028 (C05 G1/G2 MET·실물 LEAD 선행 확인). 통합 결과 없으면 새 G3를 꾸며내지 않고 BLOCKED(scope/명령/NEXT). #36에 필요한 새 증거만 제출.
- mock/paper 실행은 모의 모드·계정이 확인된 환경에서만, 실제 런검증은 별도 단계. 실계좌 real mode는 무승인 실행 금지.

**입력:** [Issue #11 Claude A](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [Issue #12 Codex B](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [Issue #32 RunLab](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 **새 댓글 delta만** → C05가 실제 `04_LEAD_ACCEPTANCE`로 이동한 RF. [D00](D00_ENGINEERING_DELIVERY_POLICY.md) 준수. [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)은 결과 출력 전용. 오래된 A/B HANDOFF 재독·갱신 금지.

## 현재 할 일 — RF-051/054/058 선별 소스·테스트 통합, C05 G3/DONE 인계 (2026-10-29 22:35 KST)
- **원격 LEAD 확인:** C05 [#36 6497069816](https://github.com/hbombheart1230-dotcom/agentra/issues/36#issuecomment-6497069816), RF-051/054/058 `04_LEAD_ACCEPTANCE/CLAUDE_A` G1/G2 MET, G3 PENDING. RF-016/028/029/067 기존 DONE은 중복 KEEP/통합/CI 금지.
- **실제 G1 SOURCE:** Claude A `bed173058613ad97f830001771d0bd7b3c191f30`. 변경 전 integration `867f174c48405cf1a8172265bfdda5a2c368a2fa`와 3개 owner 소스 blob이 달랐고 3개 신규 테스트는 없었음. 최소 6경로만 GitHub Contents API로 반영. **코드+테스트 최종 원격 integration `87d3777513856b9f89575115c285f20e1a3560fc`** 에서 6/6 A SOURCE blob 동일 재조회:
  - RF-051 `libs/market/korea_index_sanity.py` `5e4d3c0f`, `tests/test_p15_korea_index_sanity_finite.py` `896b16d1`.
  - RF-054 `libs/performance/playbook_stats.py` `01d36ab6`, `tests/test_p15_playbook_stats_finite_contract.py` `1cfaedf1`.
  - RF-058 `libs/storage/proposal_store.py` `775fbf2e`, `tests/test_p15_proposal_store_append_serialization.py` `9f25286e`.
- **G2 기수용:** A [#11 6495308964](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6495308964) normal pytest RF-051 10 PASS, RF-054 13 PASS, RF-058 5 PASS(exit0), SOURCE `bed17305`. 이 결과를 새 integration pytest 수행으로 오인하지 않음.
- **C04 G3 관련 정상 smoke 실제 exit0:** 별도 격리 Python 3.13 환경에 위 integration의 **세 source 파일 Git blob을 정확 재구성·git hash-object 3/3 일치**시킨 후 `cd /mnt/data/c04_smoke && python smoke.py` 정상 **exit0**. RF-051 NaN/Inf, KOSPI/KOSDAQ warning·JSON finite·입력 불변; RF-054 finite returns, invalid recent_window, 계산·JSON finite·입력 불변; RF-058 temp JSONL append, UTF-8, serialization failure no write. RF-054의 무관한 `performance_aggregator` import만 fake stub 사용, 실운영 IO/network/실계좌 0. **이것은 격리된 변경 경계 smoke이며 저장소 전체 pytest 또는 exact test 파일 pytest 실행은 NOT_RUN**. `python -O`/hosted CI NOT_RUN; 결론을 확대하지 않음. 동일 소스+관련 정상 smoke로 FAST-3 G3 evidence READY, C05가 RF 원본/STATUS 단독 G3 MET/DONE 수용.
- **CI 확인:** 통합 SHA `87d37775` GitHub combined commit statuses `[]`, commit workflow runs `[]` (후자는 PR-trigger first page 제한). Actions 전체 실행 없음이라고 단정하지 않으며 수동 dispatch 0. 새 full CI 필수 아님.
- **기타 안전 후보:** RF-008 긴급 구조 `069dadd5`의 3개 source/test blob은 integration에 이미 동일하지만 신규 targeted 정상 exit0 아직 확인되지 않음. 기존 DONE을 중복 이동하지 말고 C03/긴급 테스트 담당이 `python -m unittest discover -s tests -p test_rf008_strategist_reporter_feedback_split.py -v` 격리 exit0 확보 후 C05에 별도 구조 개선 근거로 전달. RF-031 A 신규 module/normal/push는 아직 G1 BLOCKED(C02/Claude A). B push/pytest 인증 환경 차단은 C03/C01 담당.
- **재개:** C05가 RF-051/054/058 G3 수용해 DONE 이동하면 중복 통합·시험 없이 신규 LEAD만 조사. C04 변경/실제 G3 증거는 #36에 한 번 인계; RF 원본/STATUS/LEAD_CURRENT는 C05 전용. 문서 전용 추가 커밋에 CI 재실행 금지. 운영 실계좌/주문/배포 금지.
