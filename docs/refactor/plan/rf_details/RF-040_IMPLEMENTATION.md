# RF-040 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-040.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 19개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/agent/reporter.py` blob `00a8d240af99c14b493b50b2e989cc2e605e9968` (721 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/agent/reporter.py::run_reporter_agent` L643-721 | MOVE_BODY | `libs/agent/reporter_run_reporter_agent.py::run_reporter_agent` | 79행 · 순수 후보 |
| `libs/agent/reporter.py::run` L191-217 | KEEP_CLASS_OR_EXTRACT | `libs/agent/reporter.py::run` | 27행 · 순수 후보 |

### run_reporter_agent — 원본 79행
- **확인된 책임:** `libs/agent/reporter.py` L643–721; 직접 호출 helper `_normalize_trade_reporter_policy`, `_validate_trade_read_model`. 감지된 효과: 없음.
- **목표:** `libs/agent/reporter_run_reporter_agent.py::run_reporter_agent` (Owner Claude A, RF-040). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### run — 원본 27행
- **확인된 책임:** `libs/agent/reporter.py` L191–217; 직접 호출 helper `_result`. 감지된 효과: 없음.
- **목표:** `libs/agent/reporter.py::run` (Owner Claude A, RF-040). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/agent/__init__.py` | `libs/agent/__init__.py` | `f27b7be40d02` / 364B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/commander.py` | `libs/agent/commander.py` | `029586f70c71` / 6046B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/executor.py` | `libs/agent/executor.py` | `6f5c8ac831e5` / 2288B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/executor/__init__.py` | `libs/agent/executor/__init__.py` | `e390f3aa4198` / 130B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/executor/agent_executor.py` | `libs/agent/executor/agent_executor.py` | `3135159a0cf3` / 2182B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/executor/executor_agent.py` | `libs/agent/executor/executor_agent.py` | `e015d72a570b` / 11115B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/intent_parser.py` | `libs/agent/intent_parser.py` | `7e717177580c` / 2714B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/monitor.py` | `libs/agent/monitor.py` | `240836e15abc` / 589B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/reporter.py` | `libs/agent/reporter.py` | `00a8d240af99` / 29462B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/agent/reporter_inputs.py` | `libs/agent/reporter_inputs.py` | `d0de9efd007f` / 1559B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/reporter_outputs.py` | `libs/agent/reporter_outputs.py` | `e545c883b801` / 2661B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/router.py` | `libs/agent/router.py` | `ae763cafeb48` / 1336B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/scanner.py` | `libs/agent/scanner.py` | `95a1135f08f6` / 6046B | 짧은 단일 책임이면 KEEP_OK |
| `libs/agent/strategist.py` | `libs/agent/strategist.py` | `104f6b73a884` / 3235B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf040_058_054_residual_gaps_contract.py` | `tests/test_rf040_058_054_residual_gaps_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf040_libs_agent_reporter_agent.py` | `tests/test_rf040_libs_agent_reporter_agent.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf040_libs_agent_reporter_dtos.py` | `tests/test_rf040_libs_agent_reporter_dtos.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf040_libs_agent_reporter_hooks.py` | `tests/test_rf040_libs_agent_reporter_hooks.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf040_libs_agent_reporter_result.py` | `tests/test_rf040_libs_agent_reporter_result.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-040|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
