# RF-020 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-020.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 30개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/monitor/entry_cascade_projection.py` blob `8dfaa5184be988a50e433d1b1a89d8812f865add` (278 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/monitor/entry_cascade_projection.py::entry_cascade_entry_cooldown_map_runner_entry` L102-185 | MOVE_BODY | `libs/runtime/monitor/entry_cascade_projection_entry_cascade_entry_cooldown_map_run.py::entry_cascade_entry_cooldown_map_runner_entry` | 84행 · 순수 후보 |
| `libs/runtime/monitor/entry_cascade_projection.py::entry_cascade_intent` L215-278 | MOVE_BODY | `libs/runtime/monitor/entry_cascade_projection_entry_cascade_intent.py::entry_cascade_intent` | 64행 · 순수 후보 |
| `libs/runtime/monitor/entry_cascade_projection.py::entry_cascade_buy_blocked_closeout_window_buy_blocked` L52-101 | MOVE_BODY | `libs/runtime/monitor/entry_cascade_projection_entry_cascade_buy_blocked_closeout_w.py::entry_cascade_buy_blocked_closeout_window_buy_blocked` | 50행 · 순수 후보 |
| `libs/runtime/monitor/entry_cascade_projection.py::entry_cascade_entry_candidate_cascade_entry_cascade_co` L12-51 | MOVE_BODY | `libs/runtime/monitor/entry_cascade_projection_entry_cascade_entry_candidate_cascad.py::entry_cascade_entry_candidate_cascade_entry_cascade_co` | 40행 · 순수 후보 |
| `libs/runtime/monitor/entry_cascade_projection.py::entry_cascade_buy_blocked_closeout_window_buy_blocked_2` L186-214 | MOVE_BODY | `libs/runtime/monitor/entry_cascade_projection_entry_cascade_buy_blocked_closeout_w.py::entry_cascade_buy_blocked_closeout_window_buy_blocked_2` | 29행 · 순수 후보 |

### entry_cascade_entry_cooldown_map_runner_entry — 원본 84행
- **확인된 책임:** `libs/runtime/monitor/entry_cascade_projection.py` L102–185; 직접 호출 helper `_monitor_selected_snapshot_for_symbol`, `_evaluate_monitor_entry_candidate`. 감지된 효과: 없음.
- **목표:** `libs/runtime/monitor/entry_cascade_projection_entry_cascade_entry_cooldown_map_run.py::entry_cascade_entry_cooldown_map_runner_entry` (Owner Codex B, RF-020). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### entry_cascade_intent — 원본 64행
- **확인된 책임:** `libs/runtime/monitor/entry_cascade_projection.py` L215–278; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/monitor/entry_cascade_projection_entry_cascade_intent.py::entry_cascade_intent` (Owner Codex B, RF-020). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### entry_cascade_buy_blocked_closeout_window_buy_blocked — 원본 50행
- **확인된 책임:** `libs/runtime/monitor/entry_cascade_projection.py` L52–101; 직접 호출 helper `_evaluate_monitor_entry_candidate`. 감지된 효과: 없음.
- **목표:** `libs/runtime/monitor/entry_cascade_projection_entry_cascade_buy_blocked_closeout_w.py::entry_cascade_buy_blocked_closeout_window_buy_blocked` (Owner Codex B, RF-020). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### entry_cascade_entry_candidate_cascade_entry_cascade_co — 원본 40행
- **확인된 책임:** `libs/runtime/monitor/entry_cascade_projection.py` L12–51; 직접 호출 helper `_resolve_entry_candidate_cascade_config`. 감지된 효과: 없음.
- **목표:** `libs/runtime/monitor/entry_cascade_projection_entry_cascade_entry_candidate_cascad.py::entry_cascade_entry_candidate_cascade_entry_cascade_co` (Owner Codex B, RF-020). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### entry_cascade_buy_blocked_closeout_window_buy_blocked_2 — 원본 29행
- **확인된 책임:** `libs/runtime/monitor/entry_cascade_projection.py` L186–214; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/monitor/entry_cascade_projection_entry_cascade_buy_blocked_closeout_w.py::entry_cascade_buy_blocked_closeout_window_buy_blocked_2` (Owner Codex B, RF-020). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/monitor/__init__.py` | `libs/runtime/monitor/__init__.py` | `e69de29bb2d1` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/cycle_detail_projection.py` | `libs/runtime/monitor/cycle_detail_projection.py` | `891fc0f2685e` / 249B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/cycle_detail_projection_exit_decision_detail.py` | `libs/runtime/monitor/cycle_detail_projection_exit_decision_detail.py` | `337def9d3829` / 291B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/cycle_event_payloads.py` | `libs/runtime/monitor/cycle_event_payloads.py` | `92353886934b` / 233B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/cycle_log_trace_payloads.py` | `libs/runtime/monitor/cycle_log_trace_payloads.py` | `ea09d2208d54` / 241B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/cycle_output_projection.py` | `libs/runtime/monitor/cycle_output_projection.py` | `15efec65b9f7` / 249B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/cycle_output_projection_value_state_monitor.py` | `libs/runtime/monitor/cycle_output_projection_value_state_monitor.py` | `8d71d5444db6` / 289B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/cycle_posture_projection.py` | `libs/runtime/monitor/cycle_posture_projection.py` | `bb5bc64aef88` / 251B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_candidate_annotation.py` | `libs/runtime/monitor/entry_candidate_annotation.py` | `4e8261c75470` / 1509B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_candidate_guards.py` | `libs/runtime/monitor/entry_candidate_guards.py` | `260ec04e8474` / 4904B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_candidate_policy.py` | `libs/runtime/monitor/entry_candidate_policy.py` | `efd4fc99b66d` / 3988B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_candidate_probe.py` | `libs/runtime/monitor/entry_candidate_probe.py` | `d258a5a200c4` / 2596B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_carry_guard.py` | `libs/runtime/monitor/entry_carry_guard.py` | `0b38d174ee3b` / 2900B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_cascade_projection.py` | `libs/runtime/monitor/entry_cascade_projection.py` | `8dfaa5184be9` / 19770B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/monitor/entry_cascade_selection.py` | `libs/runtime/monitor/entry_cascade_selection.py` | `db8b243f694d` / 4155B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_context.py` | `libs/runtime/monitor/entry_context.py` | `b75523ccbf59` / 3639B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_cycle_context.py` | `libs/runtime/monitor/entry_cycle_context.py` | `295d06ced47b` / 7386B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_evidence.py` | `libs/runtime/monitor/entry_evidence.py` | `16c01ec85b3f` / 221B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_focus_output_projection.py` | `libs/runtime/monitor/entry_focus_output_projection.py` | `a03222361945` / 261B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_guard_evidence.py` | `libs/runtime/monitor/entry_guard_evidence.py` | `e202b6e6858d` / 4816B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/entry_quality_projection.py` | `libs/runtime/monitor/entry_quality_projection.py` | `a89377fa3220` / 3713B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/exit_decision_projection.py` | `libs/runtime/monitor/exit_decision_projection.py` | `8d6b25a64db1` / 11821B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/exit_frame_projection.py` | `libs/runtime/monitor/exit_frame_projection.py` | `94364273e750` / 6887B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/policy_output_projection.py` | `libs/runtime/monitor/policy_output_projection.py` | `6d1170c9863b` / 251B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/scanner_monitor_handoff_projection.py` | `libs/runtime/monitor/scanner_monitor_handoff_projection.py` | `b497c1376f9e` / 271B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/signal_explanation.py` | `libs/runtime/monitor/signal_explanation.py` | `89b372fc2a81` / 239B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/signal_features.py` | `libs/runtime/monitor/signal_features.py` | `6d58c717290f` / 15750B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/signal_features_breakout_volume_gate.py` | `libs/runtime/monitor/signal_features_breakout_volume_gate.py` | `9b1ad3d2fc31` / 10873B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/signal_score_projection.py` | `libs/runtime/monitor/signal_score_projection.py` | `a1a293581795` / 17772B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/monitor/signal_score_projection_chart_structure_decision.py` | `libs/runtime/monitor/signal_score_projection_chart_structure_decision.py` | `1464297872b4` / 4319B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-020|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
