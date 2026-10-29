# RF-026 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-026.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 15개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/intraday_monitor_signals.py` blob `bca3ee95d1c68edc443d4b4318f34c2d6d98b2cd` (2726 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/intraday_monitor_signals.py::_status_item` L1405-1445 | KEEP_CLASS_OR_EXTRACT | `libs/runtime/intraday_monitor_signals.py::_status_item` | 41행 · 순수 후보 |
| `libs/runtime/intraday_monitor_signals.py::_session_gap_context` L2010-2049 | MOVE_BODY | `libs/runtime/intraday_monitor_signals_session_gap_context.py::_session_gap_context` | 40행 · 순수 후보 |
| `libs/runtime/intraday_monitor_signals.py::_empty_human_chart_entry_setup` L336-367 | MOVE_BODY | `libs/runtime/intraday_monitor_signals_empty_human_chart_entry_setup.py::_empty_human_chart_entry_setup` | 32행 · 순수 후보 |
| `libs/runtime/intraday_monitor_signals.py::_build_monitor_signal_evidence` L193-222 | MOVE_BODY | `libs/runtime/intraday_monitor_signals_build_monitor_signal_evidence.py::_build_monitor_signal_evidence` | 30행 · 순수 후보 |
| `libs/runtime/intraday_monitor_signals.py::_merge_candle_group` L1899-1928 | MOVE_BODY | `libs/runtime/intraday_monitor_signals_merge_candle_group.py::_merge_candle_group` | 30행 · 순수 후보 |
| `libs/runtime/intraday_monitor_signals.py::_candles_from_rows` L1873-1898 | MOVE_BODY | `libs/runtime/intraday_monitor_signals_candles_from_rows.py::_candles_from_rows` | 26행 · 순수 후보 |
| `libs/runtime/intraday_monitor_signals.py::_session_vwap` L1987-2009 | MOVE_BODY | `libs/runtime/intraday_monitor_signals_session_vwap.py::_session_vwap` | 23행 · 순수 후보 |

### _status_item — 원본 41행
- **확인된 책임:** `libs/runtime/intraday_monitor_signals.py` L1405–1445; 직접 호출 helper `_parse_policy_signal_spec`, `_chart_feature_status_item`. 감지된 효과: 없음.
- **목표:** `libs/runtime/intraday_monitor_signals.py::_status_item` (Owner Codex B, RF-026). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _session_gap_context — 원본 40행
- **확인된 책임:** `libs/runtime/intraday_monitor_signals.py` L2010–2049; 직접 호출 helper `_current_kst_session_anchor`, `_to_float`, `_to_int`. 감지된 효과: 없음.
- **목표:** `libs/runtime/intraday_monitor_signals_session_gap_context.py::_session_gap_context` (Owner Codex B, RF-026). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _empty_human_chart_entry_setup — 원본 32행
- **확인된 책임:** `libs/runtime/intraday_monitor_signals.py` L336–367; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/intraday_monitor_signals_empty_human_chart_entry_setup.py::_empty_human_chart_entry_setup` (Owner Codex B, RF-026). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _build_monitor_signal_evidence — 원본 30행
- **확인된 책임:** `libs/runtime/intraday_monitor_signals.py` L193–222; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/intraday_monitor_signals_build_monitor_signal_evidence.py::_build_monitor_signal_evidence` (Owner Codex B, RF-026). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _merge_candle_group — 원본 30행
- **확인된 책임:** `libs/runtime/intraday_monitor_signals.py` L1899–1928; 직접 호출 helper `_to_float`. 감지된 효과: 없음.
- **목표:** `libs/runtime/intraday_monitor_signals_merge_candle_group.py::_merge_candle_group` (Owner Codex B, RF-026). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _candles_from_rows — 원본 26행
- **확인된 책임:** `libs/runtime/intraday_monitor_signals.py` L1873–1898; 직접 호출 helper `_to_float`. 감지된 효과: 없음.
- **목표:** `libs/runtime/intraday_monitor_signals_candles_from_rows.py::_candles_from_rows` (Owner Codex B, RF-026). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/asset_universe_policy.py` | `libs/runtime/asset_universe_policy.py` | `b2db143fe602` / 20223B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/chart_structure_features.py` | `libs/runtime/chart_structure_features.py` | `bdc372f6f1f1` / 18299B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander_memory_policy.py` | `libs/runtime/commander_memory_policy.py` | `57253e58764c` / 12831B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/decision_observability.py` | `libs/runtime/decision_observability.py` | `c68340540c46` / 38281B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/decision_trace.py` | `libs/runtime/decision_trace.py` | `48be20e76a9c` / 2828B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/exit_policy.py` | `libs/runtime/exit_policy.py` | `f58d750c9393` / 33354B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/feature_engine.py` | `libs/runtime/feature_engine.py` | `2c42ab55d718` / 13998B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/intent_conflict_resolver.py` | `libs/runtime/intent_conflict_resolver.py` | `39f5f7233d3e` / 9973B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/intraday_monitor_signals.py` | `libs/runtime/intraday_monitor_signals.py` | `bca3ee95d1c6` / 135937B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/monitor_entry_policy_context.py` | `libs/runtime/monitor_entry_policy_context.py` | `a89055b8304e` / 7749B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor_policy.py` | `libs/runtime/monitor_policy.py` | `f98d0b9516a6` / 36903B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/policy_bundle.py` | `libs/runtime/policy_bundle.py` | `f0c0c6726a06` / 1129B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/q9_decision_snapshots.py` | `libs/runtime/q9_decision_snapshots.py` | `425700a26e0b` / 25161B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/scanner_feature_hydration.py` | `libs/runtime/scanner_feature_hydration.py` | `c4bdf792ee30` / 15792B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner_policy.py` | `libs/runtime/scanner_policy.py` | `a10a75a10a8c` / 4910B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-026|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
