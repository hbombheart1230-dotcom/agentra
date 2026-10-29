# RF-025 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-025.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 13개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/controlled_mock_lanes/coordinator.py` blob `19d95a08c39dda4a9136a1ff1d4608169eb6e53e` (613 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/controlled_mock_lanes/coordinator.py::_resolve_broker_outcome` L478-534 | MOVE_BODY | `libs/runtime/controlled_mock_lanes/coordinator_resolve_broker_outcome.py::_resolve_broker_outcome` | 57행 · 순수 후보 |
| `libs/runtime/controlled_mock_lanes/coordinator.py::_pending_buy_symbols` L96-124 | MOVE_BODY | `libs/runtime/controlled_mock_lanes/coordinator_pending_buy_symbols.py::_pending_buy_symbols` | 29행 · 순수 후보 |
| `libs/runtime/controlled_mock_lanes/coordinator.py::_intent` L253-280 | MOVE_BODY | `libs/runtime/controlled_mock_lanes/coordinator_intent.py::_intent` | 28행 · 순수 후보 |

### _resolve_broker_outcome — 원본 57행
- **확인된 책임:** `libs/runtime/controlled_mock_lanes/coordinator.py` L478–534; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/controlled_mock_lanes/coordinator_resolve_broker_outcome.py::_resolve_broker_outcome` (Owner Claude A, RF-025). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _pending_buy_symbols — 원본 29행
- **확인된 책임:** `libs/runtime/controlled_mock_lanes/coordinator.py` L96–124; 직접 호출 helper `_mapping`, `_text`, `_int`. 감지된 효과: 없음.
- **목표:** `libs/runtime/controlled_mock_lanes/coordinator_pending_buy_symbols.py::_pending_buy_symbols` (Owner Claude A, RF-025). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _intent — 원본 28행
- **확인된 책임:** `libs/runtime/controlled_mock_lanes/coordinator.py` L253–280; 직접 호출 helper `_text`, `_strategy_snapshot`. 감지된 효과: 없음.
- **목표:** `libs/runtime/controlled_mock_lanes/coordinator_intent.py::_intent` (Owner Claude A, RF-025). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/controlled_mock_lanes/__init__.py` | `libs/runtime/controlled_mock_lanes/__init__.py` | `5faf82e3646e` / 220B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/controlled_mock_lanes/artifacts.py` | `libs/runtime/controlled_mock_lanes/artifacts.py` | `18b78d26ad56` / 1099B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/controlled_mock_lanes/contracts.py` | `libs/runtime/controlled_mock_lanes/contracts.py` | `520e816de621` / 994B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/controlled_mock_lanes/coordinator.py` | `libs/runtime/controlled_mock_lanes/coordinator.py` | `19d95a08c39d` / 24847B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/controlled_mock_lanes/ledger.py` | `libs/runtime/controlled_mock_lanes/ledger.py` | `9abd79be7a83` / 13539B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/controlled_mock_lanes/signals.py` | `libs/runtime/controlled_mock_lanes/signals.py` | `6030a983caa9` / 9536B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/mock_exam_day/__init__.py` | `libs/runtime/mock_exam_day/__init__.py` | `784eca15cbdf` / 45B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/mock_exam_day/closeout_liquidation.py` | `libs/runtime/mock_exam_day/closeout_liquidation.py` | `1f7b94f1439a` / 16278B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/mock_exam_day/closeout_phase.py` | `libs/runtime/mock_exam_day/closeout_phase.py` | `ebe56a62d24c` / 10758B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/mock_exam_day/common.py` | `libs/runtime/mock_exam_day/common.py` | `01c861d6ef1e` / 2837B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/mock_exam_day/preopen_phase.py` | `libs/runtime/mock_exam_day/preopen_phase.py` | `d1ed57c1256f` / 6907B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/mock_exam_day/processes.py` | `libs/runtime/mock_exam_day/processes.py` | `c8a2171e06a3` / 9923B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/mock_exam_day/session_phase.py` | `libs/runtime/mock_exam_day/session_phase.py` | `7568f0be634a` / 5993B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-025|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
