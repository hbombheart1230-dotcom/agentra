# RF-064 — 코드 구조/함수 재배치 설계 (T08)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-064.md` blob `e04799af7f8f8bb25a9c36647785f07a67d344af`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 58개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `scripts/refactor/shared_strategist_contracts.py` | 63920 | `8b0d6988695cfa599aacd16aa024b5c0a38989c7` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/refactor/shared_strategist_contracts_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `scripts/refactor/p156_parity_differential.py` | 46469 | `8cd1d477af507b861ce0725b0b052af29ef930dd` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/refactor/p156_parity_differential_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `scripts/refactor/p164_strategist_freeze_tool.py` | 32699 | `ac9b2a7a3edd81856b0fe512185088b7b27532e3` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/refactor/p164_strategist_freeze_tool_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `scripts/refactor/p165_commander_ui_freeze_tool.py` | 31351 | `9f7a094281832eb66f6e286bb245de709daed013` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/refactor/p165_commander_ui_freeze_tool_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `scripts/refactor/p158_static_purity_closure.py` | 28404 | `fdc4d89672ae58d45da86f71de7ed19a131ac31a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/refactor/p158_static_purity_closure_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `scripts/refactor/p162_scanner_node_freeze_tool.py` | 26826 | `9c700142cd498d16caa0164d9a57e70f5b288bf2` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/refactor/p162_scanner_node_freeze_tool_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `scripts/refactor/p163_monitor_freeze_tool.py` | 26809 | `054b5f437b01eed57881cd60f7a354e9e7577e89` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/refactor/p163_monitor_freeze_tool_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `scripts/refactor/p159_ownership_matrix.py` | 20070 | `d09ec878c421584790aef09688105b0e8f0d00cc` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/refactor/p159_ownership_matrix_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `scripts/refactor/inventory_p15_consumers.py` → `scripts/refactor/inventory_p15_consumers.py` | 6172 | `1ea82c616abc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/monitor_evidence_ast.py` → `scripts/refactor/monitor_evidence_ast.py` | 3644 | `185539a85e1e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p152_facade_consumer_scan.py` → `scripts/refactor/p152_facade_consumer_scan.py` | 9808 | `0877984afc40` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p152_integration_acceptance.py` → `scripts/refactor/p152_integration_acceptance.py` | 6370 | `1969986dd0c6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p152_owner_parity.py` → `scripts/refactor/p152_owner_parity.py` | 7945 | `5f6ebcb30d37` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p152_prelocal_consumer_debt.py` → `scripts/refactor/p152_prelocal_consumer_debt.py` | 4742 | `e2ee1efa1eaa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p152_r3_call_recorder.py` → `scripts/refactor/p152_r3_call_recorder.py` | 17728 | `e9ccb2146bfc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p152_r3_seam_challenge.py` → `scripts/refactor/p152_r3_seam_challenge.py` | 14095 | `7e84a1cc6a6d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p152_snapshot_parity.py` → `scripts/refactor/p152_snapshot_parity.py` | 7623 | `162ee86f29db` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p156_determinism_plugin.py` → `scripts/refactor/p156_determinism_plugin.py` | 6471 | `061a3c8fa655` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p156_parity_differential.py` → `scripts/refactor/p156_parity_differential.py` | 46469 | `8cd1d477af50` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p158_static_purity_closure.py` → `scripts/refactor/p158_static_purity_closure.py` | 28404 | `fdc4d89672ae` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p159_ownership_matrix.py` → `scripts/refactor/p159_ownership_matrix.py` | 20070 | `d09ec878c421` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p15_strategist_s5_runner.py` → `scripts/refactor/p15_strategist_s5_runner.py` | 1866 | `8c40208248c6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p160_ntfs_dir_mtime_diagnostics.py` → `scripts/refactor/p160_ntfs_dir_mtime_diagnostics.py` | 4626 | `435ddd2e7181` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p161_agent_output_capture_plugin.py` → `scripts/refactor/p161_agent_output_capture_plugin.py` | 2535 | `522241aa4d7b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p161_agent_output_diagnose.py` → `scripts/refactor/p161_agent_output_diagnose.py` | 5875 | `39290d8815b5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p161_agent_output_freeze.py` → `scripts/refactor/p161_agent_output_freeze.py` | 3480 | `4dd9af368a09` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p161_agent_output_freeze_tool.py` → `scripts/refactor/p161_agent_output_freeze_tool.py` | 16669 | `0af3b182bbd9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p161_agent_output_variants.py` → `scripts/refactor/p161_agent_output_variants.py` | 3142 | `1c201232e2dd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p162_scanner_capture_plugin.py` → `scripts/refactor/p162_scanner_capture_plugin.py` | 2654 | `8c288dfeba0a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p162_scanner_node_freeze_tool.py` → `scripts/refactor/p162_scanner_node_freeze_tool.py` | 26826 | `9c700142cd49` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p163_monitor_capture_plugin.py` → `scripts/refactor/p163_monitor_capture_plugin.py` | 2069 | `e83c483075e8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p163_monitor_freeze_tool.py` → `scripts/refactor/p163_monitor_freeze_tool.py` | 26809 | `054b5f437b01` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p164_strategist_capture_plugin.py` → `scripts/refactor/p164_strategist_capture_plugin.py` | 1788 | `59f05a36ebab` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p164_strategist_freeze_tool.py` → `scripts/refactor/p164_strategist_freeze_tool.py` | 32699 | `ac9b2a7a3edd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p165_commander_ui_capture_plugin.py` → `scripts/refactor/p165_commander_ui_capture_plugin.py` | 2439 | `f6e342322591` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p165_commander_ui_freeze_tool.py` → `scripts/refactor/p165_commander_ui_freeze_tool.py` | 31351 | `9f7a09428183` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p167_v2053_scanner_context_cases.py` → `scripts/refactor/p167_v2053_scanner_context_cases.py` | 6630 | `7183a622a9c9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p169_broad_failure_evidence.py` → `scripts/refactor/p169_broad_failure_evidence.py` | 5038 | `f031ed40cd6b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p170_v3055_projection_capture_plugin.py` → `scripts/refactor/p170_v3055_projection_capture_plugin.py` | 1977 | `857c74c26feb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p172_strategist_s1_057_capture.py` → `scripts/refactor/p172_strategist_s1_057_capture.py` | 15363 | `7ffe320492a8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p172_v4056_scanner_policy_cases.py` → `scripts/refactor/p172_v4056_scanner_policy_cases.py` | 8403 | `7c3d10f8d698` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/p173_v4056_repeat_guard_cases.py` → `scripts/refactor/p173_v4056_repeat_guard_cases.py` | 7116 | `3792717eb892` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/render_p15_import_matrix.py` → `scripts/refactor/render_p15_import_matrix.py` | 2620 | `e01e71781917` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/reporter_facade_guard.py` → `scripts/refactor/reporter_facade_guard.py` | 6528 | `a0d8caf7e491` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/shared_candidate_tests.py` → `scripts/refactor/shared_candidate_tests.py` | 6029 | `ac21b4cd6c3f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/shared_role_contracts.py` → `scripts/refactor/shared_role_contracts.py` | 5783 | `3ddeefe0ff27` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/shared_strategist_contracts.py` → `scripts/refactor/shared_strategist_contracts.py` | 63920 | `8b0d6988695c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/shared_uef_baseline.py` → `scripts/refactor/shared_uef_baseline.py` | 2168 | `8f23ffd8f8de` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_annotation_replay.py` → `scripts/refactor/work_monitor_annotation_replay.py` | 4479 | `33a4fcab7ff8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_body_replay.py` → `scripts/refactor/work_monitor_body_replay.py` | 4594 | `6cb46b039862` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_continuous_replay.py` → `scripts/refactor/work_monitor_continuous_replay.py` | 7935 | `e85c1e261a80` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_contracts.py` → `scripts/refactor/work_monitor_contracts.py` | 10864 | `d625a5743db0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_current_tree.py` → `scripts/refactor/work_monitor_current_tree.py` | 10715 | `b771b06912ac` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_observation_replay.py` → `scripts/refactor/work_monitor_observation_replay.py` | 4845 | `7cbbc1b13c66` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_policy_trace_replay.py` → `scripts/refactor/work_monitor_policy_trace_replay.py` | 6628 | `faad17697b6b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_retained_boundary.py` → `scripts/refactor/work_monitor_retained_boundary.py` | 3392 | `6b9cf9c540c5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_monitor_scope_accounting.py` → `scripts/refactor/work_monitor_scope_accounting.py` | 10173 | `6732cbd8eea6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_capture.py` → `scripts/refactor/work_reporter_capture.py` | 6489 | `de2718b82a1a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_contract_runner.py` → `scripts/refactor/work_reporter_contract_runner.py` | 4349 | `2e47d56f45f7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_facade_ledger_v2.py` → `scripts/refactor/work_reporter_facade_ledger_v2.py` | 1852 | `f87afac145d2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_flow_map.py` → `scripts/refactor/work_reporter_flow_map.py` | 3411 | `428270e5d952` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_hygiene_check.py` → `scripts/refactor/work_reporter_hygiene_check.py` | 4471 | `dfe322e24ab0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_inventory.py` → `scripts/refactor/work_reporter_inventory.py` | 3898 | `f7de9d4a9ca1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_r4_extract.py` → `scripts/refactor/work_reporter_r4_extract.py` | 12918 | `d75d7865f0e6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_split.py` → `scripts/refactor/work_reporter_split.py` | 4842 | `8a2cdf48c8ab` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/refactor/work_reporter_triage.py` → `scripts/refactor/work_reporter_triage.py` | 4860 | `b5cf839b053c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
