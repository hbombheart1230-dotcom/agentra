# C02 — Claude A | 신규 실측 SOURCE→Owner MOVE 6개 (단일 실행 문서)

## 실행·권한·재개
- Owner branch: work/p15-a-reporter-pure-20261021. 이 문서에 명시한 A 전용 code/test만 수정·커밋·정상 push. 다른 설계·상태·큐 문서, 타인 브랜치/코드, 운영 보고·DB/State·실주문/브로커/Guard/UEF·frozen/CI 정책은 읽거나 변경하지 않는다. 네트워크/실프로세스 호출 금지; 모든 실행 fixture는 fake/temp.
- Preflight: 원격 integration/p1.5 CANONICAL_HEAD, 이 문서의 ORDER_FILE_BLOB_SHA, A OWNER_REMOTE_SHA를 시작 시 고정. 번호별 ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1..A6. 실행 중 지시서가 갱신되어도 이미 시작한 버전은 유효하며 소급 실패 아님. A 원격 기준 5da432ff405067a277547597305a21d8cbc26242. 이미 해당 SHA에서 완료된 builder opening/broad/latent/fresh/attention, model slot 6개는 절대 반복하지 않는다.
- MOVE 정의: 원본 def의 실제 본문 제거, 신규 단일 Owner def로 이동, 원명/원서명 얇은 facade wrapper 유지. facade 모듈은 sys.modules[__name__]를 명시적으로 facade=에 전달하고 target은 facade를 역import하지 않는다. 기존 helper/argparse/os/JSON 의존을 use-time facade 조회하여 monkeypatch/예외/순서/문자열/alias 동작 보존. 동일 본문 이중 유지 금지. 원본 before golden을 변경 전 확보하고 새 wrapper와 owner에 2~4개 fixture로 비교한다.
- 실행 전 각 SOURCE 파일을 git show/checkout의 **실제 파일 bytes**에서 확인하고 원본 py_compile/AST parse 후 수정. 표시용 tool 출력이 생략·truncated 되었으면 절대 그 텍스트를 소스에 붙여넣지 않는다. 원격 target 존재/Owner blob 변화 시 덮어쓰지 말고 해당 item만 CONFLICT_BLOCKED 후 다른 항목 계속. 정상 targeted pytest exit0 한 번(없으면 stdlib unittest smoke exit0); -O/full peer/전체 CI 필수 아님. 인증 실패는 PUSH_BLOCKED이지 G1 아님. 한 item 종료·차단 뒤 나머지 독립 item 전부 진행.
- **A1~A3** 공통 SOURCE libs/reporting/live_execution_bundle_runner.py (A blob df06f64556dd0468a067303a9555ce473228f4bc, 실제 2788 LOC). **A4~A6** 공통 SOURCE libs/reporting/alpha_research_board/builder.py (A blob 753f0e9b2806b80fa7a6ecd11e4d81943efed19c, 실제 592 LOC). 6개 신규 target은 위 A SHA에서 모두 미존재. 각 파일 변경은 서로 다른 원함수에 대한 독립 patch이며 같은 facade 변경은 순차 누적한다.

## A1 — PID active probe 함수 몸체 이동
- SOURCE libs/reporting/live_execution_bundle_runner.py::_pid_active(pid) L386–413 (28행) → TARGET libs/reporting/live_execution_bundle_runner_pid_active.py::_pid_active(pid, *, facade). 0/음수 pid False, Windows ctypes OpenProcess/CloseHandle, POSIX os.kill(pid,0), PermissionError True, OSError False, 기타 기존 예외 처리 전부 target로 MOVE. 원본에는 _pid_active(pid) thin wrapper. target에서 facade.os.name/facade.os.kill을 호출시점 조회, Windows ctypes import/exception 경계 그대로 보존. **실제 os.kill/프로세스 종료·운영 PID 접촉 금지**.
- tests/test_p15_live_bundle_pid_active_owner.py: (1) 0/-1/None→False, (2) fake POSIX os.kill 성공→True, (3) fake PermissionError→True/OSError→False, (4) fake Windows OpenProcess 0/유효 handle/CloseHandle 및 예외; 모든 경로 외부 호출 0, wrapper==owner==before golden, 원본 부작용 0. normal: python -m pytest -q -p no:cacheprovider tests/test_p15_live_bundle_pid_active_owner.py (또는 동등 stdlib unittest) exit0.

## A2 — 기존 trade linked run ID 수집 이동
- SOURCE libs/reporting/live_execution_bundle_runner.py::_existing_trade_run_ids(trade_dir) L1225–1248 (24행) → TARGET libs/reporting/live_execution_bundle_runner_existing_trade_run_ids.py::_existing_trade_run_ids(trade_dir, *, facade). lifecycle_bundle.json 존재 확인, facade._read_json_if_exists use-time, linked_run_ids 선행, entry/exit/holding 순서, 공백 정리·중복 처리의 원래 본문을 이동. 기존 wrapper 이름/서명 보존. 실운영 trade dir 접근 금지.
- tests/test_p15_live_bundle_existing_trade_ids_owner.py: (1) tmp_path 파일 없음→[], (2) linked [r2,r1] + entry r1 + exit r3 + holding [r3,r4]→[r2,r1,r3,r4], (3) 불량/누락 nested payload·공백·숫자 id 원래 출력/예외, (4) patched facade._read_json_if_exists spy와 원본 파일 해시 불변; wrapper==owner==before. normal pytest 위 파일 exit0.

## A3 — CLI parser 구성만 이동 (main KEEP)
- SOURCE libs/reporting/live_execution_bundle_runner.py::_build_parser() L1401–1424 (24행) → TARGET libs/reporting/live_execution_bundle_runner_build_parser.py::_build_parser(*, facade). argparse.ArgumentParser 생성·모든 옵션·상호배타 trade-report-ai 두 flag·set_defaults 본문만 이동. 원본 _build_parser() wrapper; target은 facade.argparse를 호출시점 조회. main(argv), 실제 report 생성, background job/lock, process spawn은 원위치 KEEP 및 **실행 금지**.
- tests/test_p15_live_bundle_parser_owner.py: (1) parse_args([]) defaults 전체 vars 순서·값 동일, (2) --max-runs 3/--json/--target-symbol 값, (3) --trade-report-ai와 --no-trade-report-ai 단독/동시 SystemExit 코드 동일, (4) --max-runs invalid int의 SystemExit/usage 및 patched argparse spy parity. 오직 parser.parse_args만 호출, main 금지. normal pytest 위 파일 exit0.

## A4 — Q12 hypothesis metric 선택 순수 함수 이동
- SOURCE libs/reporting/alpha_research_board/builder.py::_q12_hypothesis_metric(payload, *, phase, path_value="FAST_BUY_ALL_PASS", entry_method="09:05", horizon="+30m") L74–92 (19행) → TARGET libs/reporting/alpha_research_board/builder_q12_hypothesis_metric.py::_q12_hypothesis_metric(payload, *, phase, path_value="FAST_BUY_ALL_PASS", entry_method="09:05", horizon="+30m", facade). rows 첫 matching evidence_phase/axis/value/entry_method/horizon만 facade.mapping → facade.metric_snapshot, 미일치 metric_snapshot({}) 원문 그대로 이동. wrapper 원서명/기본값 유지.
- tests/test_p15_alpha_q12_metric_owner.py: (1) rows 없음/빈 list, (2) 동일 phase 두 row 중 첫 매칭 선택, (3) phase/path_value/entry_method/horizon 각 mismatch와 지정 override, (4) facade.metric_snapshot spy·원본 입력 불변/원래 예외. before==wrapper==owner, normal pytest 위 파일 exit0.

## A5 — feature candidate projection 이동
- SOURCE libs/reporting/alpha_research_board/builder.py::_feature_candidates(feature_payload, prospective_payload, concentrations) L95–169 (약 77행) → TARGET libs/reporting/alpha_research_board/builder_feature_candidates.py::_feature_candidates(feature_payload, prospective_payload, concentrations, *, facade). 두 고정 후보 R1_SCANNER_RISK_HIGH_30M_V1 및 R1_ENTRY_DAILY_MA5_20_EXTENDED_15M_V1의 specs, find_by_id, historical match, ACTION_REVIEW/OBSERVE_FIXED, 한국어 evidence/next_action, candidate order 전체 이동. facade.find_by_id/mapping/metric_snapshot/_candidate 호출시점 사용, source에는 얇은 wrapper.
- tests/test_p15_alpha_feature_candidates_owner.py: (1) 빈 feature/prospective→두 후보와 순서/기본 status, (2) 첫 후보 eligible vs 둘째 rejected의 bucket/owner/notes 정확 값, (3) historical train/validation/prospective + concentration 연동, (4) facade._candidate spy·입력 불변·한국어 UTF-8/키 순서 golden. normal pytest 위 파일 exit0.

## A6 — BTC Woori fixed-horizon candidate 이동
- SOURCE libs/reporting/alpha_research_board/builder.py::_btc_woori(payload) L244–259 (약 17행) → TARGET libs/reporting/alpha_research_board/builder_btc_woori.py::_btc_woori(payload, *, facade). find_horizon episode_horizons "+30m", fixed candidate ID/track/OBSERVE_FIXED, historical real_net, 고정 한국어 note/next_action, source_keys 한 원문 본문 MOVE. facade.find_horizon/_candidate/metric_snapshot use-time, wrapper 원서명.
- tests/test_p15_alpha_btc_woori_owner.py: (1) 빈 payload default status, (2) +5m/+30m/+60m 중 +30m real_net만 선택, (3) conclusion="REJECTED"와 비매핑 horizon 기존 예외/출력, (4) patched facade.find_horizon/_candidate spy·입력 불변/한국어 bytes golden. normal pytest 위 파일 exit0.

## 정당 KEEP · 충돌 회피
- live_execution_bundle_runner.py::main, _active_background_process, _touch_background_job_lock은 운영 IO/Clock/process/lock 효과 경계라 원위치 KEEP; _terminate_process_tree는 실제 SIGTERM/taskkill 효과이므로 별도 안전 승인 전 **MOVE/호출 금지**.
- builder.py::_candidate는 이미 이동된 5개 owner가 facade._candidate 호출시점 patch seam으로 공유하는 스키마 생성기라 지금은 KEEP; _prospective_concentrations는 reports_root의 glob/read 효과를 가지므로 별도 temp read 계약 전 KEEP; _large_cap_candidate는 보고서 IO 소비자 결합이라 KEEP. KEEP은 신규 MOVE 성과 0이며 이번 6개를 대체하지 않는다.
- A 전용 파일만 작업하고 B Commander/Strategist/Operator UI target 및 긴급 브랜치 수정 금지. 같은 원본을 다른 작업자가 변경하면 원격 blob 확인 후 해당 item CONFLICT_BLOCKED로 분리.

## 종료·인계
- A1~A6 전부 필수 독립 실코드 MOVE. 각 item ORDER_ID, SOURCE_BEFORE/AFTER_LOC·BLOB, TARGET_PATH/BLOB, 실제 MOVED_FUNCTIONS, TEST_CMD/NORMAL_EXIT, ITEM_STATUS=IMPLEMENTED|ALREADY_MOVED|TEST_BLOCKED|PUSH_BLOCKED|SAFETY_BLOCKED|NOT_RUN, FIRST_BLOCKER/NEXT를 #11 댓글 한 번에 기록. 자기 branch만 정상 commit/push, git ls-remote 및 원격 source/target/test blob 검증. 이미 이동된 동일 blob은 ALREADY_MOVED로만 기록하고 다시 테스트/이동하지 않는다. C04는 최소 통합·targeted normal smoke, C05는 G1/G2/G3·DONE 독점.
