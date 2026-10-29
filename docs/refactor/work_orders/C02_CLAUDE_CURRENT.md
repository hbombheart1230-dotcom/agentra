# C02 — Claude A | 실측 Owner 함수 MOVE 6개 (단일 실행 문서)

## 실행·권한 (이 문서만 읽는다)
- Owner branch: `work/p15-a-reporter-pure-20261021`. **이 문서에 지정된 code/test 파일만** 수정·커밋·정상 push. 다른 문서·설계·상태·원본 큐를 찾거나 수정하지 않는다. 다른 작업자 브랜치, CI/보호 정책, 운영 데이터·State·DB·로그, 실제 네트워크/주문/브로커/Guard/UEF는 절대 쓰지 않는다.
- 시작할 때 `git ls-remote`로 **CANONICAL_HEAD**(`integration/p1.5`), **OWNER_REMOTE_SHA**(A 브랜치), `git rev-parse <CANONICAL_HEAD>:docs/refactor/work_orders/C02_CLAUDE_CURRENT.md`로 **ORDER_FILE_BLOB_SHA**를 고정. 번호별 **ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1..A6**. 실행 도중 지시서가 바뀌어도 시작 당시 blob의 과제는 유효하며 소급 실패 아님. 기존 local-only와 원격 push/테스트 exit는 분리.
- 각 과제는 **원본 함수 몸체 제거 → 새 Owner 단일 구현 → 원래 이름/서명의 얇은 wrapper**. 호출시점 monkeypatch를 보존하려면 facade 모듈 `sys.modules[__name__]`를 target 함수에 **명시적 키워드 `facade=`로 전달**하고 target에서는 `facade.mapping`, `facade._candidate` 등 원래 참조를 use-time에 조회한다. **target에서 facade 역import 금지.** 결과 dict/list 순서·한국어 bytes·예외·입력 불변을 유지. 이전 구현을 새 파일에 복제하고 원본에도 남겨 두는 이중 구현 금지.
- 각 Item의 2~4개 fake fixture를 기존 source BEFORE golden(변경 전 BLOB/함수 실행값)과 새 owner+wrapper에서 비교한다. **정상** `python -m pytest -q -p no:cacheprovider <해당 새 test 파일>` 또는 `python -m unittest discover -s tests -p '<파일명>' -v` **exit0 한 번**; pytest 없으면 stdlib. `-O`/full suite/전수 peer/hosted CI 필수 아님. 한 item이 막히면 정확 `ITEM_STATUS=TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED`·원인·재개점만 기록하고 **나머지 독립 item 계속**. 중복 완료한 함수는 원격 body/target blob이 같을 때만 `ALREADY_MOVED`로 제외하고 동일 테스트 재실행 금지.
- 이번 6개 target은 A 원격 `048c6d3faeba24a90116e818ae98104293addd9c`에서 **모두 미존재**이고 아래 source 함수 본문은 실제 확인됨. 동일 source 파일의 함수끼리도 **서로 독립 ITEM**이며 같은 파일의 패치를 순차 누적한다. 새 owner가 기존 경로에 출현했으면 overwrite하지 말고 C03에 충돌 보고 후 다른 item 계속. **정당 KEEP은 기존 위치/책임/효과 경계에 맞는 경우 한 줄+blob으로만**, 이 6개 미이동 본문을 KEEP으로 대체하지 않는다.

## A1 — opening lane 3행 투영
- **SOURCE** `libs/reporting/alpha_research_board/builder.py::_opening_rows` (A source blob `0302499b8616c8f2daef55f0d1a7711b88069900`, L244–282, 39행) → **TARGET** `libs/reporting/alpha_research_board/builder_opening_rows.py::_opening_rows(payload, *, facade)`. `summary.conditional_lane_summaries`에서 `IMMEDIATE_OPENING_PROBE/+5m`, `CONFIRMED_RECURRENT_RANK/+30m`, `DISLOCATION_REBOUND/+60m` 순서의 3개 `_candidate`를 생성하는 **for-loop 몸체 전체**를 MOVE. 원래 `_opening_rows(payload)`는 facade wrapper만; target의 `mapping`, `metric_snapshot`, `_candidate`는 facade에서 조회.
- **test** `tests/test_p15_alpha_board_opening_rows_owner.py`: (1) 빈 summary → 3개 순서/기본 값, (2) 각 lane live_net 서로 다른 값 → horizon별 prospective 구분, (3) `facade._candidate` spy가 호출순서·인자 기록, (4) 입력 deep copy 불변/한국어 note 정확 일치. 네 fixture old/new/owner 결과 동일.

## A2 — broad opening 투영
- **SOURCE** 같은 `builder.py::_broad_opening` (L285–311, 27행) → **TARGET** `libs/reporting/alpha_research_board/builder_broad_opening.py::_broad_opening(payload, *, facade)`. `promotion_decision.values`에서 `sample_count/window_count/win_rate/coverage`, `concentration`을 구성하는 전체 `_candidate` 본문 MOVE. 원명 wrapper, `facade.mapping`/`facade._candidate` use-time.
- **test** `tests/test_p15_alpha_board_broad_opening_owner.py`: (1) 빈 decision → 기본 status/0 counts, (2) observed_count=7·win_rate=.5·largest_day_share=.6 → 지정 필드/키순서, (3) patched candidate spy와 원본 예외 parity, (4) 입력 불변.

## A3 — latent reactivation 투영
- **SOURCE** 같은 `builder.py::_latent` (L314–334, 21행) → **TARGET** `libs/reporting/alpha_research_board/builder_latent.py::_latent(payload, *, facade)`. `summary.horizons["+30m"].live_net`·concentration 3키를 구성하는 원본 몸체 MOVE; wrapper·`facade.mapping/metric_snapshot/_candidate` 전달.
- **test** `tests/test_p15_alpha_board_latent_owner.py`: (1) 빈 summary, (2) +30m live_net와 largest_* 값, (3) spy candidate의 한국어 evidence_note 및 key order, (4) 원본 입력 불변.

## A4 — fresh change 투영
- **SOURCE** 같은 `builder.py::_fresh_change` (L222–241, 20행) → **TARGET** `libs/reporting/alpha_research_board/builder_fresh_change.py::_fresh_change(payload, *, facade)`. `historical_reference.branch.horizons["+30m"]`와 `branch.horizons["+30m"]`의 historical/prospective 매핑과 고정 기각 사유 전체 MOVE; 원명 wrapper·facade use-time.
- **test** `tests/test_p15_alpha_board_fresh_change_owner.py`: (1) 누락 historical → 기본, (2) historical positive/prospective negative 값 구분, (3) decision.status와 patched `metric_snapshot` 호출, (4) 원본 불변/한국어 bytes parity.

## A5 — attention 정렬 순수 함수
- **SOURCE** 같은 `builder.py::_attention_order` (L382–399, 18행) → **TARGET** `libs/reporting/alpha_research_board/builder_attention_order.py::_attention_order(candidates)`. 8개 bucket priority와 `candidate_id` tie-break 정렬 몸체 MOVE; 기존 `_attention_order` thin wrapper. target은 facade 필요 없음(단독 pure Owner).
- **test** `tests/test_p15_alpha_board_attention_order_owner.py`: (1) 빈 list → [], (2) CLOSED vs RUNTIME_VALIDATION_NEXT 순서, (3) 동일 bucket id 오름차순·unknown bucket 마지막, (4) 잘못된 row/누락 id의 **기존 예외와 입력 불변**. 새 결과와 변경 전 golden 동일.

## A6 — model slot 우선순위 해석
- **SOURCE** `libs/llm/model_catalog.py::resolve_policy_llm_slot` (blob `3d3ab4dae19e96f60b5a8019f8213e414db90f45`, L273–306, 34행) → **TARGET** `libs/llm/model_catalog_resolve_policy_llm_slot.py::resolve_policy_llm_slot(policy, *path, default_profile, facade)`. `applied_policy.llm → commander.applied_policy.llm → reporter_output.applied_policy.llm → llm → reporter_policy.llm → default` 순서, primary/fallback/cards/profile_source를 계산하는 **전체 함수 몸체** MOVE. 원명 `resolve_policy_llm_slot(policy,*path,default_profile=...)` wrapper 유지; `_nested_get/resolve_model_profile/normalize_openrouter_model_name/get_model_card/_dedupe_models`를 **facade 호출시점** 조회. `resolve_policy_llm_execution_slot` 호출자 수정·이동 금지.
- **test** `tests/test_p15_model_catalog_slot_owner.py`: (1) None policy 기본 profile, (2) 우선순위 충돌(상위 applied_policy 승리), (3) primary=fallback 중복 제거·모델 카드 순서, (4) facade normalize spy·비매핑 입력/기존 예외/원본 불변.

## 종료·인계
- **각 A1~A6는 필수**이며 순서가 종료/선택 권한이 아니다. 한 번에 안전한 code/test 커밋을 묶을 수 있으나 A 본인 브랜치만 정상 push하고 **remote branch SHA 및 source/target/test blob**을 다시 조회한다. 원본 함수 전후 LOC, 실제 MOVED_FUNCTIONS, `NORMAL_TEST_CMD/EXIT`, `ITEM_STATUS`, `ORDER_ID`, `FIRST_BLOCKER/NEXT`를 #11 댓글 **1회** 보고. C04는 최소 diff 통합·targeted smoke, C05는 G1/G2/G3 수용·DONE; A는 상태 문서를 쓰지 않는다.
