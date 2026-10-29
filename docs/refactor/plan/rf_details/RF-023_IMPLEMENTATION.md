# RF-023 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-023.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 21개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/entrypoints/live_session_watch.py` blob `5b229dec3eadb5c17c6e15fc777ea9f6aaed074f` (358 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/entrypoints/live_session_watch.py::_run_once` L225-305 | KEEP_EFFECT_SPLIT_PURE | `libs/runtime/entrypoints/live_session_watch.py::_run_once` | 81행 · IO, Clock/Env |
| `libs/runtime/entrypoints/live_session_watch.py::_build_markdown` L120-171 | MOVE_BODY | `libs/runtime/entrypoints/live_session_watch_build_markdown.py::_build_markdown` | 52행 · 순수 후보 |
| `libs/runtime/entrypoints/live_session_watch.py::main` L325-355 | KEEP_CLASS_OR_EXTRACT | `libs/runtime/entrypoints/live_session_watch.py::main` | 31행 · 순수 후보 |
| `libs/runtime/entrypoints/live_session_watch.py::_parse_args` L205-224 | KEEP_EFFECT_SPLIT_PURE | `libs/runtime/entrypoints/live_session_watch.py::_parse_args` | 20행 · Clock/Env |
| `libs/runtime/entrypoints/live_session_watch.py::_build_console_line` L306-324 | MOVE_BODY | `libs/runtime/entrypoints/live_session_watch_build_console_line.py::_build_console_line` | 19행 · 순수 후보 |

### _run_once — 원본 81행
- **확인된 책임:** `libs/runtime/entrypoints/live_session_watch.py` L225–305; 직접 호출 helper `_run_live_summary`, `_build_markdown`. 감지된 효과: IO, Clock/Env.
- **목표:** `libs/runtime/entrypoints/live_session_watch.py::_run_once` (Owner Claude A, RF-023). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _build_markdown — 원본 52행
- **확인된 책임:** `libs/runtime/entrypoints/live_session_watch.py` L120–171; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/entrypoints/live_session_watch_build_markdown.py::_build_markdown` (Owner Claude A, RF-023). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### main — 원본 31행
- **확인된 책임:** `libs/runtime/entrypoints/live_session_watch.py` L325–355; 직접 호출 helper `_parse_args`, `_run_once`, `_build_console_line`. 감지된 효과: 없음.
- **목표:** `libs/runtime/entrypoints/live_session_watch.py::main` (Owner Claude A, RF-023). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _parse_args — 원본 20행
- **확인된 책임:** `libs/runtime/entrypoints/live_session_watch.py` L205–224; 직접 호출 helper 없음. 감지된 효과: Clock/Env.
- **목표:** `libs/runtime/entrypoints/live_session_watch.py::_parse_args` (Owner Claude A, RF-023). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _build_console_line — 원본 19행
- **확인된 책임:** `libs/runtime/entrypoints/live_session_watch.py` L306–324; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/entrypoints/live_session_watch_build_console_line.py::_build_console_line` (Owner Claude A, RF-023). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/entrypoints/check_runtime_profile.py` | `libs/runtime/entrypoints/check_runtime_profile.py` | `b98e2fd4178a` / 2853B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/commander_runtime_once.py` | `libs/runtime/entrypoints/commander_runtime_once.py` | `aedeffcb0059` / 3740B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/launch_with_preflight.py` | `libs/runtime/entrypoints/launch_with_preflight.py` | `0b90b987f6eb` / 5038B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/live_loop.py` | `libs/runtime/entrypoints/live_loop.py` | `645a54f3ab5e` / 548B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/live_session_summary.py` | `libs/runtime/entrypoints/live_session_summary.py` | `5ea00f7cbb7d` / 11002B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/live_session_watch.py` | `libs/runtime/entrypoints/live_session_watch.py` | `5b229dec3ead` / 14286B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/entrypoints/m13_live_loop.py` | `libs/runtime/entrypoints/m13_live_loop.py` | `a44050abde31` / 3485B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_closeout_check.py` | `libs/runtime/entrypoints/m28_closeout_check.py` | `6e20cf3985d5` / 11920B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_deploy_launch_template_check.py` | `libs/runtime/entrypoints/m28_deploy_launch_template_check.py` | `ac6b6d51a5f3` / 7576B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_launch_hook_integration_check.py` | `libs/runtime/entrypoints/m28_launch_hook_integration_check.py` | `563315928954` / 8294B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_launch_templates.py` | `libs/runtime/entrypoints/m28_launch_templates.py` | `8901110b0946` / 6218B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_registration_helper_check.py` | `libs/runtime/entrypoints/m28_registration_helper_check.py` | `dea62d3dfcba` / 8007B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_registration_helpers.py` | `libs/runtime/entrypoints/m28_registration_helpers.py` | `d88ce607f864` / 5324B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_rollout_rollback_check.py` | `libs/runtime/entrypoints/m28_rollout_rollback_check.py` | `b6784dcfd9a0` / 8907B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_runtime_lifecycle_hooks_check.py` | `libs/runtime/entrypoints/m28_runtime_lifecycle_hooks_check.py` | `bf809b4d190e` / 3896B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_runtime_profile_scaffold_check.py` | `libs/runtime/entrypoints/m28_runtime_profile_scaffold_check.py` | `90e58df44de4` / 5413B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_scheduler_worker_launch_wrapper_check.py` | `libs/runtime/entrypoints/m28_scheduler_worker_launch_wrapper_check.py` | `a6143bd46ff8` / 7585B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m28_startup_preflight_check.py` | `libs/runtime/entrypoints/m28_startup_preflight_check.py` | `d7f78e81deac` / 9406B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/m31_agent_chain_probe.py` | `libs/runtime/entrypoints/m31_agent_chain_probe.py` | `6bbbca28681a` / 7022B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/mock_exam_day.py` | `libs/runtime/entrypoints/mock_exam_day.py` | `618c16e04495` / 12779B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/entrypoints/offhours_validation_loop.py` | `libs/runtime/entrypoints/offhours_validation_loop.py` | `a9b001b45c1e` / 3724B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-023|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
