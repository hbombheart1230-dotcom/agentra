# RF-086 — 코드 구조/함수 재배치 설계 (T06)

## T06 developer-policy KEEP reason
D00 is the one active delivery policy. Past dev-team and development notes retain history and version, not competing execution authority. Keep documented links and source filename when correct. One-line KEEP_OK with blob; no new code/test and no forced relocation.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-086.md` blob `e4b81627ed9cb902b61e8bb7bf75364b6dc1dab4`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 96개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `docs/00_HOME.md` → `docs/00_HOME.md` | 6572 | `f2179ff72d01` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ENGINEERING_DELIVERY_POLICY.md` → `docs/ENGINEERING_DELIVERY_POLICY.md` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/KNOWLEDGE_POLICY.md` → `docs/KNOWLEDGE_POLICY.md` | 2282 | `0010a0b89623` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/PATCH_NOTES.md` → `docs/PATCH_NOTES.md` | 16417 | `6287723d707b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/agents.md` → `docs/agents.md` | 14424 | `6bc7eb36923b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/canonical_artifact_flow.md` → `docs/canonical_artifact_flow.md` | 2093 | `fcce57c2aa09` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/canonical_event_schema.md` → `docs/canonical_event_schema.md` | 1890 | `650bda83d83a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/composite_skills.md` → `docs/composite_skills.md` | 1992 | `7f23a1fdf72b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/debug/peak_drawdown_entry_diagnosis_2026-04-16.md` → `docs/debug/peak_drawdown_entry_diagnosis_2026-04-16.md` | 4801 | `7504cf020761` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/debug/reporter_fallback_audit_2026-04-14.md` → `docs/debug/reporter_fallback_audit_2026-04-14.md` | 21817 | `406097a9d4f9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/dtos.md` → `docs/dtos.md` | 10442 | `c3abac08d243` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/00_index.md` → `docs/en/00_index.md` | 7105 | `cea2a2dc2cef` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/01_overview.md` → `docs/en/01_overview.md` | 2632 | `16f3b27a36aa` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/02_principles.md` → `docs/en/02_principles.md` | 969 | `41cdd02d0894` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/03_context_and_scope.md` → `docs/en/03_context_and_scope.md` | 623 | `b9aff1e8a66a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/04_logical_architecture.md` → `docs/en/04_logical_architecture.md` | 1084 | `edfc90f2c78f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/05_runtime_flow.md` → `docs/en/05_runtime_flow.md` | 3350 | `9b473e1b39f4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/06_contracts.md` → `docs/en/06_contracts.md` | 697 | `3b0f92b147bd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/07_execution_and_guards.md` → `docs/en/07_execution_and_guards.md` | 990 | `edddb3880627` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/08_observability.md` → `docs/en/08_observability.md` | 1050 | `1665a93ccbd1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/09_security_and_compliance.md` → `docs/en/09_security_and_compliance.md` | 507 | `d628508a9daf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/10_deployment_and_ops.md` → `docs/en/10_deployment_and_ops.md` | 1237 | `6d36e4a92981` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/11_testing_and_quality.md` → `docs/en/11_testing_and_quality.md` | 569 | `db2340c4b1c5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/12_roadmap.md` → `docs/en/12_roadmap.md` | 20592 | `5487d5ca86fa` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/13_project_tree.md` → `docs/en/13_project_tree.md` | 10521 | `c5dcfdacc0b5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/en/99_glossary.md` → `docs/en/99_glossary.md` | 326 | `19492ad092cb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/ops_checklist.md` → `docs/env_plan/ops_checklist.md` | 1274 | `fd21a4b955e7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase1_close.md` → `docs/env_plan/phase1_close.md` | 367 | `b425d33e3656` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase2_close.md` → `docs/env_plan/phase2_close.md` | 377 | `1c2896714d0e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase3_close.md` → `docs/env_plan/phase3_close.md` | 490 | `1872c477b1c8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase4_close.md` → `docs/env_plan/phase4_close.md` | 1090 | `63dabf208080` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase4_plan.md` → `docs/env_plan/phase4_plan.md` | 343 | `84d6456f35df` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase5_catalog_review.md` → `docs/env_plan/phase5_catalog_review.md` | 2403 | `a1afdb2d0905` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase5_close.md` → `docs/env_plan/phase5_close.md` | 1710 | `dab471a38ae2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase5_plan.md` → `docs/env_plan/phase5_plan.md` | 435 | `3a0380ac7588` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase5_sync_ops_note.md` → `docs/env_plan/phase5_sync_ops_note.md` | 1348 | `6ce88cccfbe5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase6_design_note.md` → `docs/env_plan/phase6_design_note.md` | 2978 | `423d34b52224` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase6_plan.md` → `docs/env_plan/phase6_plan.md` | 402 | `87ce420420ec` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/phase7_plan.md` → `docs/env_plan/phase7_plan.md` | 295 | `de02a3490583` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/runtime_bridge_note_2026_04_10.md` → `docs/env_plan/runtime_bridge_note_2026_04_10.md` | 2590 | `a7b2f1bbf850` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_plan/status_snapshot_2026_04_10.md` → `docs/env_plan/status_snapshot_2026_04_10.md` | 1584 | `839597b54c9d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/env_rules.md` → `docs/env_rules.md` | 403 | `cfa3926b9886` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/io_contracts.md` → `docs/io_contracts.md` | 11882 | `ff340b21b9f4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/00_index.md` → `docs/ko/00_index.md` | 1124 | `d1f7fae5d187` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/01_overview.md` → `docs/ko/01_overview.md` | 2761 | `d264e8df23b0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/02_principles.md` → `docs/ko/02_principles.md` | 1098 | `2d0f21491a7c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/03_context_and_scope.md` → `docs/ko/03_context_and_scope.md` | 686 | `e3abae3d6867` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/04_logical_architecture.md` → `docs/ko/04_logical_architecture.md` | 1139 | `85a920aa94f1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/05_runtime_flow.md` → `docs/ko/05_runtime_flow.md` | 1347 | `82d46f80e66c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/06_contracts.md` → `docs/ko/06_contracts.md` | 679 | `0272deaf5be7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/07_execution_and_guards.md` → `docs/ko/07_execution_and_guards.md` | 1060 | `0f2ab613be06` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/08_observability.md` → `docs/ko/08_observability.md` | 1118 | `936abc0d4ef3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/09_security_and_compliance.md` → `docs/ko/09_security_and_compliance.md` | 508 | `9587a54004bb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/10_deployment_and_ops.md` → `docs/ko/10_deployment_and_ops.md` | 880 | `80100c9a8bfe` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/11_testing_and_quality.md` → `docs/ko/11_testing_and_quality.md` | 580 | `53a889e20a9b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/12_roadmap.md` → `docs/ko/12_roadmap.md` | 3242 | `c07bf75cdc97` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/13_project_tree.md` → `docs/ko/13_project_tree.md` | 1119 | `403548fe108f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/ko/99_glossary.md` → `docs/ko/99_glossary.md` | 375 | `5fa0b64da372` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/llm_architecture.md` → `docs/llm_architecture.md` | 4927 | `a59da9254de8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/milestones/Evidence_Memory.md` → `docs/milestones/Evidence_Memory.md` | 538 | `10e7c2ae00f5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/milestones/Reporter_Q100.md` → `docs/milestones/Reporter_Q100.md` | 2817 | `714bd0dfba12` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/milestones/Safety.md` → `docs/milestones/Safety.md` | 2550 | `879fb3be5800` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/milestones/Strategy_Program_Integration.md` → `docs/milestones/Strategy_Program_Integration.md` | 1514 | `46f9aaf65787` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/milestones/System_V2.md` → `docs/milestones/System_V2.md` | 360 | `3df9f4c9e250` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/milestones/UEF.md` → `docs/milestones/UEF.md` | 36427 | `bfddd490f082` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/registry.md` → `docs/registry.md` | 1332 | `b0689c2c95d8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/skill_map.md` → `docs/skill_map.md` | 2250 | `64bd20740638` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/system_status_2026-04-22.md` → `docs/system_status_2026-04-22.md` | 8146 | `5333da3d4e6d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/README.md` → `docs/tactics/README.md` | 7856 | `9cfac4517e2b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/artifact_integrity_audit.md` → `docs/tactics/artifact_integrity_audit.md` | 4752 | `d3080cae016d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/evaluation_layer_gap_analysis.md` → `docs/tactics/evaluation_layer_gap_analysis.md` | 4043 | `7d0505772255` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/evaluation_layer_schemas.md` → `docs/tactics/evaluation_layer_schemas.md` | 5486 | `6df3bf815d1f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/feedback_effectiveness_review.md` → `docs/tactics/feedback_effectiveness_review.md` | 5659 | `d80d4913e7c1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/intraday_validation_checklist.md` → `docs/tactics/intraday_validation_checklist.md` | 3491 | `988805067683` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/market_regime_rail_plan.md` → `docs/tactics/market_regime_rail_plan.md` | 7569 | `1278f5d8c315` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/news_event_intelligence_plan.md` → `docs/tactics/news_event_intelligence_plan.md` | 6489 | `03121f05f455` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/promotion_framework.md` → `docs/tactics/promotion_framework.md` | 12544 | `bd3beff11ff3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_below_vwap_reclaim_subtype_review_2026-05-18_to_2026-06-08.md` → `docs/tactics/q8_below_vwap_reclaim_subtype_review_2026-05-18_to_2026-06-08.md` | 3898 | `4cf336da273e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_daily_review_2026-06-02.md` → `docs/tactics/q8_daily_review_2026-06-02.md` | 7833 | `001245cbd7de` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_daily_review_2026-06-04.md` → `docs/tactics/q8_daily_review_2026-06-04.md` | 10477 | `b227c0bc0b25` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_daily_review_2026-06-10.md` → `docs/tactics/q8_daily_review_2026-06-10.md` | 9326 | `1a5d0e5a19b8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_entry_lane_observation_plan.md` → `docs/tactics/q8_entry_lane_observation_plan.md` | 3006 | `c4b141620328` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_evaluation_contract.md` → `docs/tactics/q8_evaluation_contract.md` | 3204 | `c6fbfc4c1d5c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_historical_review_2026-05-18_to_2026-06-08.md` → `docs/tactics/q8_historical_review_2026-05-18_to_2026-06-08.md` | 9229 | `4333e37714d6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_historical_review_2026-06-01_to_2026-06-16.md` → `docs/tactics/q8_historical_review_2026-06-01_to_2026-06-16.md` | 9495 | `ca020ca852f5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_historical_review_2026-06-01_to_2026-07-27.md` → `docs/tactics/q8_historical_review_2026-06-01_to_2026-07-27.md` | 13358 | `77552330c5f7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_historical_review_2026-06-01_to_2026-08-21.md` → `docs/tactics/q8_historical_review_2026-06-01_to_2026-08-21.md` | 16026 | `d351b62a0929` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_lane_decision_table_2026-06-09.md` → `docs/tactics/q8_lane_decision_table_2026-06-09.md` | 2952 | `9595abc3ef36` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_lane_decision_table_2026-06-10.md` → `docs/tactics/q8_lane_decision_table_2026-06-10.md` | 1383 | `950130d9786f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_lane_decision_table_2026-06-16.md` → `docs/tactics/q8_lane_decision_table_2026-06-16.md` | 3440 | `1979c2be75db` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/q8_shadow_evaluation_operating_plan.md` → `docs/tactics/q8_shadow_evaluation_operating_plan.md` | 9410 | `9a506a0ca4fc` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/quant_tactic_engine_phase_plan.md` → `docs/tactics/quant_tactic_engine_phase_plan.md` | 21715 | `6a938bdbdbf3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/quant_tactic_engine_plan.md` → `docs/tactics/quant_tactic_engine_plan.md` | 9773 | `637a919452e4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/strategist_effectiveness_review.md` → `docs/tactics/strategist_effectiveness_review.md` | 7568 | `d107552f8888` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/tactics/tactical_operating_baseline.md` → `docs/tactics/tactical_operating_baseline.md` | 18532 | `7de7f52e6706` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/unified_runtime_spec.md` → `docs/unified_runtime_spec.md` | 2066 | `5a66cd1be05c` | KEEP_IF: 문서 참조·경로·내용 정본 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
