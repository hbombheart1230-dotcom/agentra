# RF-022 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-022.md` blob `a9424c6a023ba2213d2746be3ca41e14817d34d5`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 40개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/runtime/commander/applied_policy.py` → `libs/runtime/commander/applied_policy.py` | 12005 | `908957ac8094` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/applied_policy_attach_projection.py` → `libs/runtime/commander/applied_policy_attach_projection.py` | 7492 | `80f7678451f8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/applied_policy_context_projection.py` → `libs/runtime/commander/applied_policy_context_projection.py` | 9846 | `055a7b7af192` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/behavior_policy_applied_summary.py` → `libs/runtime/commander/behavior_policy_applied_summary.py` | 12539 | `2277d5b43654` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/behavior_policy_carry_overrides.py` → `libs/runtime/commander/behavior_policy_carry_overrides.py` | 4020 | `0c38eca90de6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/behavior_policy_llm_profiles.py` → `libs/runtime/commander/behavior_policy_llm_profiles.py` | 9171 | `44143c870c3e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/behavior_policy_monitor_scanner.py` → `libs/runtime/commander/behavior_policy_monitor_scanner.py` | 6044 | `1b95fefb2f01` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/candidate_watch_policy.py` → `libs/runtime/commander/candidate_watch_policy.py` | 5423 | `34e8967f6b91` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/carry_review_policy.py` → `libs/runtime/commander/carry_review_policy.py` | 9890 | `72d7540ad62b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/decision_context_projection.py` → `libs/runtime/commander/decision_context_projection.py` | 10511 | `79a4a45775f9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/decision_context_projection_applied_policy_command.py` → `libs/runtime/commander/decision_context_projection_applied_policy_command.py` | 8973 | `b7c4c12e1236` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/decision_overlay_projection.py` → `libs/runtime/commander/decision_overlay_projection.py` | 9228 | `c17422c01f99` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/decision_rules_projection.py` → `libs/runtime/commander/decision_rules_projection.py` | 6920 | `36791a50e0b0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/entry_control_policy.py` → `libs/runtime/commander/entry_control_policy.py` | 13202 | `5ed88e6ad6ae` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/env_overrides.py` → `libs/runtime/commander/env_overrides.py` | 4573 | `452b3ff500f2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/event_projection.py` → `libs/runtime/commander/event_projection.py` | 13971 | `50ffc743d380` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/execution.py` → `libs/runtime/commander/execution.py` | 6355 | `c4a272296ab7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/fast_path_policy.py` → `libs/runtime/commander/fast_path_policy.py` | 14420 | `09eb0f651982` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/fast_paths.py` → `libs/runtime/commander/fast_paths.py` | 16832 | `58991ea62a10` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/integrated_chain_support.py` → `libs/runtime/commander/integrated_chain_support.py` | 1511 | `c2ea63ad1c6a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/nodes.py` → `libs/runtime/commander/nodes.py` | 1804 | `da3a5db87ecc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/open_position_assessment_projection.py` → `libs/runtime/commander/open_position_assessment_projection.py` | 10453 | `10a649efe338` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/open_position_inputs_projection.py` → `libs/runtime/commander/open_position_inputs_projection.py` | 9253 | `c2048332ea0a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/open_position_override_result.py` → `libs/runtime/commander/open_position_override_result.py` | 2761 | `cda0f14d41cd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/output_frames.py` → `libs/runtime/commander/output_frames.py` | 2700 | `ad38fd75603c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/policy_inputs_projection.py` → `libs/runtime/commander/policy_inputs_projection.py` | 8685 | `d616a1eacbc9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/policy_normalizers_projection.py` → `libs/runtime/commander/policy_normalizers_projection.py` | 6900 | `4b7d295669cf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/policy_readers.py` → `libs/runtime/commander/policy_readers.py` | 2350 | `906570589cf0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/policy_surface.py` → `libs/runtime/commander/policy_surface.py` | 5919 | `528fe1cc89f6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/position_projection.py` → `libs/runtime/commander/position_projection.py` | 14451 | `728eb4167691` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/route_surface.py` → `libs/runtime/commander/route_surface.py` | 3171 | `9f3c75fe38bb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/runtime_modes.py` → `libs/runtime/commander/runtime_modes.py` | 3017 | `a5100ecd51c5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/session_assessments.py` → `libs/runtime/commander/session_assessments.py` | 10777 | `aaaeb536f394` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/session_context.py` → `libs/runtime/commander/session_context.py` | 3191 | `7735184cc15f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/shadow_runtime.py` → `libs/runtime/commander/shadow_runtime.py` | 3190 | `76e77cc8fdc5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/strategist_cache_decision.py` → `libs/runtime/commander/strategist_cache_decision.py` | 14611 | `defb0bb1a15d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/strategist_cache_store.py` → `libs/runtime/commander/strategist_cache_store.py` | 4186 | `c6b7fe6aff60` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/strategist_cycle.py` → `libs/runtime/commander/strategist_cycle.py` | 10045 | `b424c6f43e4f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/strategist_fingerprint.py` → `libs/runtime/commander/strategist_fingerprint.py` | 13912 | `b49869b25f14` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/commander/strategist_refresh_decision.py` → `libs/runtime/commander/strategist_refresh_decision.py` | 16156 | `e955fa954b75` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
