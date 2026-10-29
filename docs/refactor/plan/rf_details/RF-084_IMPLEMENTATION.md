# RF-084 — 코드 구조/함수 재배치 설계 (T06)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-084.md` blob `7b9fc8c834142f34f2e0da31bb6f69dba3ca1087`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 41개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `docs/alignment/01_glossary_and_core_terms.md` → `docs/alignment/01_glossary_and_core_terms.md` | 6669 | `e3ce0dd1b35a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/alignment/02_current_system_definition_as_is.md` → `docs/alignment/02_current_system_definition_as_is.md` | 7736 | `26a707f637c0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/alignment/03_agent_roles_inputs_outputs_and_handoffs.md` → `docs/alignment/03_agent_roles_inputs_outputs_and_handoffs.md` | 8900 | `896b5a8ae821` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/alignment/04_contracts_source_of_truth_and_schema_surfaces.md` → `docs/alignment/04_contracts_source_of_truth_and_schema_surfaces.md` | 6478 | `ee4c45962d4f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/alignment/05_gap_analysis_and_plan_5_4_to_6.md` → `docs/alignment/05_gap_analysis_and_plan_5_4_to_6.md` | 5723 | `5c8fb933c41d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/alignment/README.md` → `docs/alignment/README.md` | 1893 | `81c76a83105f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/decisions/ADR-0002_Q_Namespace_Freeze_and_Seven_Node_Lifecycle_Authority.md` → `docs/decisions/ADR-0002_Q_Namespace_Freeze_and_Seven_Node_Lifecycle_Authority.md` | 1128 | `9c7714feed53` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/decisions/ADR-0003_UEF5_2_Market_Data_Authority_and_Recompute_Identity.md` → `docs/decisions/ADR-0003_UEF5_2_Market_Data_Authority_and_Recompute_Identity.md` | 16759 | `b53a292bf2c1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/ACTIVE_P15_THREE_BRANCHES_AND_AUDITOR_RELAY_20261018.md` → `docs/dev-team/ACTIVE_P15_THREE_BRANCHES_AND_AUDITOR_RELAY_20261018.md` | 10722 | `fc9a58b4b60b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-000-rebaseline-and-ready-queue.md` → `docs/dev-team/checkpoints/monitor/CP-000-rebaseline-and-ready-queue.md` | 1507 | `757ba4c5a132` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-001-entry-exit-order-dtos.md` → `docs/dev-team/checkpoints/monitor/CP-001-entry-exit-order-dtos.md` | 2508 | `4ec53e476536` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-002-feature-state-views.md` → `docs/dev-team/checkpoints/monitor/CP-002-feature-state-views.md` | 2587 | `028f9eb80094` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-003-empty-observation-dtos.md` → `docs/dev-team/checkpoints/monitor/CP-003-empty-observation-dtos.md` | 2738 | `d39b227088bf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-004-exit-label-views.md` → `docs/dev-team/checkpoints/monitor/CP-004-exit-label-views.md` | 1773 | `5079d710046c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-005-policy-observation-views.md` → `docs/dev-team/checkpoints/monitor/CP-005-policy-observation-views.md` | 2792 | `d668c98fc1dc` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-006-observation-annotations.md` → `docs/dev-team/checkpoints/monitor/CP-006-observation-annotations.md` | 2968 | `f23d63a2d58f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-007-role-freeze-and-work-review.md` → `docs/dev-team/checkpoints/monitor/CP-007-role-freeze-and-work-review.md` | 7142 | `16eed0dc4b2a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/checkpoints/monitor/CP-008-m9-offline-proof-not-parking.md` → `docs/dev-team/checkpoints/monitor/CP-008-m9-offline-proof-not-parking.md` | 3237 | `9fcb0daabcde` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/integration/CODEX_P2_CI_CHECKPOINT_20261018.md` → `docs/dev-team/integration/CODEX_P2_CI_CHECKPOINT_20261018.md` | 4352 | `adceb12add12` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/integration/CODEX_P2_LOCAL_EXECUTION_20261018.json` → `docs/dev-team/integration/CODEX_P2_LOCAL_EXECUTION_20261018.json` | 5342 | `45e5c3f27713` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `docs/dev-team/integration/CODEX_S5_GATE_PREPARATION_20261018.md` → `docs/dev-team/integration/CODEX_S5_GATE_PREPARATION_20261018.md` | 11702 | `26779c0b20a8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/integration/CODEX_SHARED_CANDIDATE_20261018.md` → `docs/dev-team/integration/CODEX_SHARED_CANDIDATE_20261018.md` | 7594 | `ddd2e458629f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/integration/CODEX_SHARED_EXECUTION_20261018.json` → `docs/dev-team/integration/CODEX_SHARED_EXECUTION_20261018.json` | 39888 | `e2240afb9b71` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `docs/dev-team/integration/CODEX_UEF9_FIXTURE_CHECKPOINT_20261018.md` → `docs/dev-team/integration/CODEX_UEF9_FIXTURE_CHECKPOINT_20261018.md` | 3894 | `9387b6adcf57` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev-team/integration/S5_SCOPE_POST_AUDIT_20261018.patch` → `docs/dev-team/integration/S5_SCOPE_POST_AUDIT_20261018.patch` | 680 | `c84cf6eaf433` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `docs/dev/code_structure_policy_2026-04-20.md` → `docs/dev/code_structure_policy_2026-04-20.md` | 1854 | `8635cde7d054` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev/codex_rules.md` → `docs/dev/codex_rules.md` | 264 | `cc5705ef6684` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev/gemini_review.md` → `docs/dev/gemini_review.md` | 767 | `069e4a931544` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev/incremental_refactor_plan_2026-05-15.md` → `docs/dev/incremental_refactor_plan_2026-05-15.md` | 15523 | `ccc123a14a35` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev/phase_9_3_large_reporting_hotspot_map_2026-05-17.md` → `docs/dev/phase_9_3_large_reporting_hotspot_map_2026-05-17.md` | 14063 | `7d358ea94b70` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev/revised_runtime_first_refactor_plan_2026-05-15.md` → `docs/dev/revised_runtime_first_refactor_plan_2026-05-15.md` | 9309 | `ca4ed973fddd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dev/workflow.md` → `docs/dev/workflow.md` | 798 | `866d478f31dd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/development/ai_provenance.md` → `docs/development/ai_provenance.md` | 6282 | `dee05c3d310d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/development/change_provenance_template.yaml` → `docs/development/change_provenance_template.yaml` | 2212 | `7666060cec4e` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `docs/development/development_history.md` → `docs/development/development_history.md` | 20314 | `012297cc5962` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/development/evidence_index.md` → `docs/development/evidence_index.md` | 7541 | `7accfca44be7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/development/pre_claude_refactoring_baseline_2026-08-31.md` → `docs/development/pre_claude_refactoring_baseline_2026-08-31.md` | 9615 | `857abec122a6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/development/pre_step5c_owner_closeout.md` → `docs/development/pre_step5c_owner_closeout.md` | 2583 | `c28f9d3688d0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/development/step5c_execution_owner.md` → `docs/development/step5c_execution_owner.md` | 49028 | `6ebd76d2da03` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ground_rules/AGENT_RULES.md` → `docs/ground_rules/AGENT_RULES.md` | 8077 | `b6ddc3c0a154` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ground_rules/QUALITY_GATES.md` → `docs/ground_rules/QUALITY_GATES.md` | 1943 | `d2a4d4d8b5e5` | KEEP_IF: 문서 참조·경로·내용 정본 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
