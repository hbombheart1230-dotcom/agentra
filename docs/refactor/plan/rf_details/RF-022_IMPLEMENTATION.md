# RF-022 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-022.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 40개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/commander/fast_paths.py` blob `58991ea62a10e47821c38b4b8a472baee444c2f7` (378 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/commander/fast_paths.py::run_closeout_guard_fast_path` L180-206 | MOVE_BODY | `libs/runtime/commander/fast_paths_run_closeout_guard_fast_path.py::run_closeout_guard_fast_path` | 27행 · 순수 후보 |
| `libs/runtime/commander/fast_paths.py::_open_position_row` L21-41 | MOVE_BODY | `libs/runtime/commander/fast_paths_open_position_row.py::_open_position_row` | 21행 · 순수 후보 |
| `libs/runtime/commander/fast_paths.py::run_monitor_only_fast_path` L103-122 | MOVE_BODY | `libs/runtime/commander/fast_paths_run_monitor_only_fast_path.py::run_monitor_only_fast_path` | 20행 · 순수 후보 |

### run_closeout_guard_fast_path — 원본 27행
- **확인된 책임:** `libs/runtime/commander/fast_paths.py` L180–206; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/commander/fast_paths_run_closeout_guard_fast_path.py::run_closeout_guard_fast_path` (Owner Codex B, RF-022). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _open_position_row — 원본 21행
- **확인된 책임:** `libs/runtime/commander/fast_paths.py` L21–41; 직접 호출 helper `_coerce_int`. 감지된 효과: 없음.
- **목표:** `libs/runtime/commander/fast_paths_open_position_row.py::_open_position_row` (Owner Codex B, RF-022). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### run_monitor_only_fast_path — 원본 20행
- **확인된 책임:** `libs/runtime/commander/fast_paths.py` L103–122; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/commander/fast_paths_run_monitor_only_fast_path.py::run_monitor_only_fast_path` (Owner Codex B, RF-022). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/commander/applied_policy.py` | `libs/runtime/commander/applied_policy.py` | `908957ac8094` / 12005B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/applied_policy_attach_projection.py` | `libs/runtime/commander/applied_policy_attach_projection.py` | `80f7678451f8` / 7492B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/applied_policy_context_projection.py` | `libs/runtime/commander/applied_policy_context_projection.py` | `055a7b7af192` / 9846B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/behavior_policy_applied_summary.py` | `libs/runtime/commander/behavior_policy_applied_summary.py` | `2277d5b43654` / 12539B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/behavior_policy_carry_overrides.py` | `libs/runtime/commander/behavior_policy_carry_overrides.py` | `0c38eca90de6` / 4020B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/behavior_policy_llm_profiles.py` | `libs/runtime/commander/behavior_policy_llm_profiles.py` | `44143c870c3e` / 9171B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/behavior_policy_monitor_scanner.py` | `libs/runtime/commander/behavior_policy_monitor_scanner.py` | `1b95fefb2f01` / 6044B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/candidate_watch_policy.py` | `libs/runtime/commander/candidate_watch_policy.py` | `34e8967f6b91` / 5423B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/carry_review_policy.py` | `libs/runtime/commander/carry_review_policy.py` | `72d7540ad62b` / 9890B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/decision_context_projection.py` | `libs/runtime/commander/decision_context_projection.py` | `79a4a45775f9` / 10511B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/decision_context_projection_applied_policy_command.py` | `libs/runtime/commander/decision_context_projection_applied_policy_command.py` | `b7c4c12e1236` / 8973B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/decision_overlay_projection.py` | `libs/runtime/commander/decision_overlay_projection.py` | `c17422c01f99` / 9228B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/decision_rules_projection.py` | `libs/runtime/commander/decision_rules_projection.py` | `36791a50e0b0` / 6920B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/entry_control_policy.py` | `libs/runtime/commander/entry_control_policy.py` | `5ed88e6ad6ae` / 13202B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/env_overrides.py` | `libs/runtime/commander/env_overrides.py` | `452b3ff500f2` / 4573B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/event_projection.py` | `libs/runtime/commander/event_projection.py` | `50ffc743d380` / 13971B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/execution.py` | `libs/runtime/commander/execution.py` | `c4a272296ab7` / 6355B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/fast_path_policy.py` | `libs/runtime/commander/fast_path_policy.py` | `09eb0f651982` / 14420B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/fast_paths.py` | `libs/runtime/commander/fast_paths.py` | `58991ea62a10` / 16832B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/commander/integrated_chain_support.py` | `libs/runtime/commander/integrated_chain_support.py` | `c2ea63ad1c6a` / 1511B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/nodes.py` | `libs/runtime/commander/nodes.py` | `da3a5db87ecc` / 1804B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/open_position_assessment_projection.py` | `libs/runtime/commander/open_position_assessment_projection.py` | `10a649efe338` / 10453B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/open_position_inputs_projection.py` | `libs/runtime/commander/open_position_inputs_projection.py` | `c2048332ea0a` / 9253B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/open_position_override_result.py` | `libs/runtime/commander/open_position_override_result.py` | `cda0f14d41cd` / 2761B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/output_frames.py` | `libs/runtime/commander/output_frames.py` | `ad38fd75603c` / 2700B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/policy_inputs_projection.py` | `libs/runtime/commander/policy_inputs_projection.py` | `d616a1eacbc9` / 8685B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/policy_normalizers_projection.py` | `libs/runtime/commander/policy_normalizers_projection.py` | `4b7d295669cf` / 6900B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/policy_readers.py` | `libs/runtime/commander/policy_readers.py` | `906570589cf0` / 2350B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/policy_surface.py` | `libs/runtime/commander/policy_surface.py` | `528fe1cc89f6` / 5919B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/position_projection.py` | `libs/runtime/commander/position_projection.py` | `728eb4167691` / 14451B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/route_surface.py` | `libs/runtime/commander/route_surface.py` | `9f3c75fe38bb` / 3171B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/runtime_modes.py` | `libs/runtime/commander/runtime_modes.py` | `a5100ecd51c5` / 3017B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/session_assessments.py` | `libs/runtime/commander/session_assessments.py` | `aaaeb536f394` / 10777B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/session_context.py` | `libs/runtime/commander/session_context.py` | `7735184cc15f` / 3191B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/shadow_runtime.py` | `libs/runtime/commander/shadow_runtime.py` | `76e77cc8fdc5` / 3190B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/strategist_cache_decision.py` | `libs/runtime/commander/strategist_cache_decision.py` | `defb0bb1a15d` / 14611B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/strategist_cache_store.py` | `libs/runtime/commander/strategist_cache_store.py` | `c6b7fe6aff60` / 4186B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/strategist_cycle.py` | `libs/runtime/commander/strategist_cycle.py` | `b424c6f43e4f` / 10045B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/strategist_fingerprint.py` | `libs/runtime/commander/strategist_fingerprint.py` | `b49869b25f14` / 13912B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/commander/strategist_refresh_decision.py` | `libs/runtime/commander/strategist_refresh_decision.py` | `e955fa954b75` / 16156B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-022|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
