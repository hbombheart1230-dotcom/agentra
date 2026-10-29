# C02 — Claude A | 6개 실측 독립 BODY MOVE (단일 실행 지시)

## 실행·격리·preflight
- **이 파일 하나만** 실행 지시로 읽는다. 본인 `work/p15-a-reporter-pure-20261021` 브랜치의 아래 code/test만 수정하고 정상 commit/push한다. 타인 브랜치·다른 문서·운영 State/DB/로그·실계좌·주문·네트워크·보호 정책·CI/frozen oracle·배포 변경 금지. 운영 reports 경로를 열지 않는다. fixture는 dict/fake/tmp_path만 사용.
- 시작 시 `CANONICAL_HEAD=git ls-remote origin refs/heads/integration/p1.5`, `ORDER_FILE_BLOB_SHA=git rev-parse <CANONICAL_HEAD>:docs/refactor/work_orders/C02_CLAUDE_CURRENT.md`, `OWNER_REMOTE_SHA=git ls-remote origin refs/heads/work/p15-a-reporter-pure-20261021`를 실제 기록. `ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1..A6`. 도중 새 지시서가 발행돼도 시작 당시 blob을 완료하고 다음 회차에 새 지시 적용.
- **C03 확인 원격 SOURCE**: A `0d8dd2ad0f93b9b11cbdd65de101919b5c48f42b`; `libs/reporting/alpha_research_board/builder.py` blob `812d53634f184f2da808d890a5b1559530de4b56`, 503 lines; `libs/reporting/alpha_research_board/canonical.py` blob `708e2552200581b1d7a9bba3723a697a5525c2fe`, 555 lines. 아래 원함수 6개 body 존재, 지정 target 6개 모두 원격 A에서 미존재 확인. SOURCE가 전진했으면 해당 함수와 target blob을 재확인하고 이미 실제 MOVE면 ALREADY_MOVED, 다른 안전 item 계속.
- 각 항목은 **원래 def body를 제거**하고 새 Owner에 단일 body로 이동한다. 기존 원함수 이름·서명은 1~3줄 thin wrapper로 유지. source에 `import sys`(없는 경우) 및 `from . import <target module> as _..._owner` 추가. wrapper에서 `facade=sys.modules[__name__]`를 전달, target은 source를 역import하지 않고 use-time `facade.<helper>`로 호출. 현재 결과의 dict key order, 문자열/한글, 원본 shallow alias, 예외, 순회/IO 순서, caller monkeypatch 유지. **MOVE 이전** 현재 source에서 fixture golden/exception 기록. truncated 출력으로 파일 재구성 금지, 실제 함수 hunk 단위 patch만.
- 항목별 `python -m pytest -q -p no:cacheprovider tests/<아래 파일>` **정상 exit0 한 번**. pytest가 없다면 동등한 `python -m unittest discover -s tests -p '<아래 파일>' -v`로 stdlib smoke exit0. 전체 suite/-O/full peer/매 RF CI 불필요. 테스트 차단과 push 차단을 분리하고 나머지 안전 item 계속. 단순 KEEP은 구조 MOVE 실적으로 세지 않는다.

## A1 — 날짜별 prospective concentration 실제 분리
- SOURCE `libs/reporting/alpha_research_board/builder.py::_prospective_concentrations(*,reports_root,first_day,through_day)` L96–151 (56줄) → TARGET `libs/reporting/alpha_research_board/builder_prospective_concentrations.py::prospective_concentrations(*,reports_root,first_day,through_day,facade)`.
- `evaluation/feature_mart/opening_rank1/prospective/20??-??-??/rank1_candidate_shadow_daily.json` glob, 기간 필터, `load_json` 오류 skip, matched 관측의 (day,symbol) set, Counter/동률 key 오름차순, 4자리 share 반올림과 전체 result 본문 MOVE. 내부 `_largest_key`도 새 owner 내부에 유지. `facade.load_json/facade.mapping/facade.Counter` use-time, facade wrapper 원서명 유지. 파일 생성/삭제 없음.
- `tests/test_p15_alpha_prospective_concentration_owner.py`: (1) tmp root 없음→{}, (2) 2일/2symbol 중복 관측 dedup·share/day count, (3) 동일 빈도 tie의 largest_day/largest_symbol 사전순 고정, (4) malformed source error skip·범위 외 제외·load_json spy·입력 tmp 파일 sha256 불변. before==owner==wrapper.

## A2 — large-cap 후보 projection 실제 분리
- SOURCE `libs/reporting/alpha_research_board/builder.py::_large_cap_candidate(reports_root,through_day)` L172–199 (28줄) → TARGET `libs/reporting/alpha_research_board/builder_large_cap_candidate.py::large_cap_candidate(reports_root,through_day,*,facade)`.
- `build_large_cap_daily_review` 호출 결과의 `base`→metric_snapshot/window_count, 고정 SAMSUNG_HYNIX 후보/한국어 evidence_note/next_action, source_count·invalid_sources metadata tuple 전체 MOVE. `facade.build_large_cap_daily_review/metric_snapshot/mapping/_candidate` use-time; 실제 review 함수 호출 대신 fake 주입.
- `tests/test_p15_alpha_large_cap_candidate_owner.py`: (1) source_count=0→available False, (2) source_count>0/invalid_sources→INVALID_DAILY_ARTIFACT, (3) base window_count 문자열·누락·metric_snapshot 결과, (4) _candidate spy와 원본 tuple/key order·한국어 bytes·입력 불변.

## A3 — 최신 stage2 source read-only 선택 분리
- SOURCE `libs/reporting/alpha_research_board/canonical.py::_latest_stage2_source(reports_root,through_day)` L267–279 (13줄) → TARGET `libs/reporting/alpha_research_board/canonical_stage2_source.py::latest_stage2_source(reports_root,through_day,*,facade)`.
- `evaluation/agent_effectiveness/cumulative_*/strategist_stage2_effectiveness_deep_dive.json`의 suffix cutoff와 max end_day 선택, 후보 없으면 `through_day` daily fallback, `load_json` 반환 tuple/예외 그대로 MOVE. `facade.load_json` use-time, temp root 읽기만. 원서명 wrapper 유지.
- `tests/test_p15_alpha_stage2_source_owner.py`: (1) cumulative 없음→daily path, (2) 여러 cumulative에서 가장 최신 cutoff 이하 선택, (3) cutoff 이후 후보만 있으면 daily fallback, (4) patched load_json spy·오류 전파/순서·파일 hash 불변. before==owner==wrapper.

## A4 — stage2 후보/attribution projection 분리
- SOURCE `libs/reporting/alpha_research_board/canonical.py::_stage2_candidate(reports_root,through_day)` L280–329 (50줄) → TARGET `libs/reporting/alpha_research_board/canonical_stage2_candidate.py::stage2_candidate(reports_root,through_day,*,facade)`.
- `changed_symbol_by_horizon['+30m']` metric, coverage, historical/agent_attribution/concentration, fixed source_status=OBSERVATION_ONLY 및 한국어 note, source tuple 반환 본문 MOVE. `facade._latest_stage2_source`(A3 미완료여도 기존 원함수 사용), `facade.mapping` use-time. 외부 네트워크/실효과 없음.
- `tests/test_p15_alpha_stage2_candidate_owner.py`: (1) empty payload→0 sample/None metrics, (2) +30m metric과 coverage populated→필드/키 순서, (3) role_definition important_boundary/한글 evidence 보존, (4) patched facade source/mapping spy·source object identity·입력 불변·예외 parity.

## A5 — negative-control candidate projection 분리
- SOURCE `libs/reporting/alpha_research_board/canonical.py::_negative_control_candidate(short_alpha)` L330–359 (30줄) → TARGET `libs/reporting/alpha_research_board/canonical_negative_control.py::negative_control_candidate(short_alpha,*,facade)`.
- `cohort_review.cohorts`에서 `TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1` 첫 매칭 선택, +5m metric_snapshot, concentration, 고정 OBSERVE_FIXED/NEGATIVE_CONTROL/한국어 설명·source_keys 본문 MOVE. `facade.mapping/metric_snapshot` use-time.
- `tests/test_p15_alpha_negative_control_owner.py`: (1) cohorts 없음→기본 metric, (2) 첫 매칭/후속 중복 우선순위, (3) malformed cohort/비mapping 처리 원본과 동일, (4) metric_snapshot spy·한글/키 순서/원본 입력 불변. before==owner==wrapper.

## A6 — 질문별 status 집계 projection 분리
- SOURCE `libs/reporting/alpha_research_board/canonical.py::_question_summaries(rows)` L385–411 (27줄) → TARGET `libs/reporting/alpha_research_board/canonical_question_summaries.py::question_summaries(rows,*,facade)`.
- `QUESTIONS` 순서, `ALLOWED_STATUSES`별 counts, 활성 DISCOVERY/PROSPECTIVE/REVIEW_READY vs CLOSED ID 목록과 question dict 확장 순서 전체 MOVE. `facade.QUESTIONS/facade.ALLOWED_STATUSES` 호출시점 조회; 기존 `canonicalize_board` caller 변경 금지.
- `tests/test_p15_alpha_question_summaries_owner.py`: (1) 빈 rows→질문별 0 count, (2) mixed statuses·중복 candidate·질문 순서, (3) fake QUESTIONS/ALLOWED_STATUSES monkeypatch 도달·key order, (4) row 필수 key 누락시 기존 KeyError parity·입력 불변. before==owner==wrapper.

## KEEP·소유권·종료
- `canonical.py::_operation_status/_fixed_validation_status/_production_promotion_status`는 실효과/승격·안전 정책 판정 경계이므로 **KEEP, 변경 금지**. `canonicalize_board` 공개 orchestration/contract·`builder.py::build_alpha_research_board/write_alpha_research_board`은 집계·파일쓰기 경계로 KEEP. 이미 분리된 builder의 `_opening_rows/_broad_opening/_latent/_fresh_change/_attention_order/_q12_hypothesis_metric/_feature_candidates/_btc_woori` 및 이전 runner 6개 재이동 금지. KEEP은 신규 MOVE 0. B의 Commander/Strategist/Operator UI source/target과 A1~A6 경로 교집합 0.
- 모든 A1~A6는 각각 필수·독립. `ORDER_ID | ITEM_STATUS=IMPLEMENTED/ALREADY_MOVED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOB | MOVED_FUNCTION | NORMAL_CMD/EXIT | FIRST_BLOCKER/NEXT`를 #11 댓글 **1회** 보고. 본인 브랜치 정상 push 후 `git ls-remote` 및 원격 source/target/test blob 확인. C04만 최소 통합, C05만 상태/DONE 판정. 인증/pytest 실패는 해당 단계만 BLOCKED로 기록하고 다른 안전 item 계속.
