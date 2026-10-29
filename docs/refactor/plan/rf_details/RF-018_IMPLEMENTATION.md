# RF-018 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/03_PEER_REVIEW/CODEX_B/RF-018.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 47개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/strategist/llm/adjustment_directives.py` blob `148a531f206bb9cec6fdde90bea1b7a1fea4a361` (312 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/strategist/llm/adjustment_directives.py::_infer_policy_adjustment_direction_r3_impl` L11-46 | MOVE_BODY | `libs/runtime/strategist/llm/adjustment_directives_infer_policy_adjustment_direction_r3.py::_infer_policy_adjustment_direction_r3_impl` | 36행 · 순수 후보 |
| `libs/runtime/strategist/llm/adjustment_directives.py::_normalize_rejected_strategy_reasons_r3_impl` L271-302 | MOVE_BODY | `libs/runtime/strategist/llm/adjustment_directives_normalize_rejected_strategy_reasons_.py::_normalize_rejected_strategy_reasons_r3_impl` | 32행 · 순수 후보 |

### _infer_policy_adjustment_direction_r3_impl — 원본 36행
- **확인된 책임:** `libs/runtime/strategist/llm/adjustment_directives.py` L11–46; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/runtime/strategist/llm/adjustment_directives_infer_policy_adjustment_direction_r3.py::_infer_policy_adjustment_direction_r3_impl` (Owner Codex B, RF-018). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _normalize_rejected_strategy_reasons_r3_impl — 원본 32행
- **확인된 책임:** `libs/runtime/strategist/llm/adjustment_directives.py` L271–302; 직접 호출 helper `_clean_directive_reason`, `_unit_score`. 감지된 효과: 없음.
- **목표:** `libs/runtime/strategist/llm/adjustment_directives_normalize_rejected_strategy_reasons_.py::_normalize_rejected_strategy_reasons_r3_impl` (Owner Codex B, RF-018). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/strategist/__init__.py` | `libs/runtime/strategist/__init__.py` | `e69de29bb2d1` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/__init__.py` | `libs/runtime/strategist/context/__init__.py` | `e69de29bb2d1` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/candidate_rerank.py` | `libs/runtime/strategist/context/candidate_rerank.py` | `07b4077a694a` / 2078B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/commander_refresh_context.py` | `libs/runtime/strategist/context/commander_refresh_context.py` | `325a4267c2cf` / 12167B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/common_values.py` | `libs/runtime/strategist/context/common_values.py` | `dcec3ec8b564` / 2485B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/llm_input_payload.py` | `libs/runtime/strategist/context/llm_input_payload.py` | `a62a0128ba6a` / 6870B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/market_inputs.py` | `libs/runtime/strategist/context/market_inputs.py` | `9ea446d39258` / 12825B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/market_key_events.py` | `libs/runtime/strategist/context/market_key_events.py` | `19e21da95f3c` / 203B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/memory.py` | `libs/runtime/strategist/context/memory.py` | `33be9482ad9c` / 16081B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/news_compaction.py` | `libs/runtime/strategist/context/news_compaction.py` | `50ffe432449a` / 201B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/news_context.py` | `libs/runtime/strategist/context/news_context.py` | `35d446121467` / 12112B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/news_signal_fallbacks.py` | `libs/runtime/strategist/context/news_signal_fallbacks.py` | `9fbd55eaa33d` / 3423B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/node_context_projection.py` | `libs/runtime/strategist/context/node_context_projection.py` | `b7fd69044ecb` / 6176B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/regime_scoring.py` | `libs/runtime/strategist/context/regime_scoring.py` | `f3476b6a84fd` / 1611B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/symbol_read_models.py` | `libs/runtime/strategist/context/symbol_read_models.py` | `583583f87481` / 204B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/theme_candidate_projection.py` | `libs/runtime/strategist/context/theme_candidate_projection.py` | `d24f835e3db0` / 1860B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/theme_compaction.py` | `libs/runtime/strategist/context/theme_compaction.py` | `b7d4bc396d87` / 8924B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/theme_packet.py` | `libs/runtime/strategist/context/theme_packet.py` | `3f23060a9fd2` / 12423B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/theme_strength.py` | `libs/runtime/strategist/context/theme_strength.py` | `3b4986442fa4` / 200B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/context/value_helpers.py` | `libs/runtime/strategist/context/value_helpers.py` | `6e65e1c94431` / 1268B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/llm/__init__.py` | `libs/runtime/strategist/llm/__init__.py` | `e69de29bb2d1` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/llm/adjustment_directives.py` | `libs/runtime/strategist/llm/adjustment_directives.py` | `148a531f206b` / 16083B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/strategist/llm/candidate_watch_overrides.py` | `libs/runtime/strategist/llm/candidate_watch_overrides.py` | `dd2467cf694b` / 4352B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/llm/override_normalization.py` | `libs/runtime/strategist/llm/override_normalization.py` | `1448908993e2` / 13816B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/llm/response_contract_parsing.py` | `libs/runtime/strategist/llm/response_contract_parsing.py` | `b7daa246fc15` / 8711B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/llm/stage_reviews.py` | `libs/runtime/strategist/llm/stage_reviews.py` | `220d4c89a407` / 10545B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/llm/text_fragment_helpers.py` | `libs/runtime/strategist/llm/text_fragment_helpers.py` | `0c3f96b5d44d` / 1589B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/__init__.py` | `libs/runtime/strategist/output/__init__.py` | `e69de29bb2d1` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/commander_context_and_plan.py` | `libs/runtime/strategist/output/commander_context_and_plan.py` | `8cf270c07651` / 13258B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/node_event_payloads.py` | `libs/runtime/strategist/output/node_event_payloads.py` | `1ec79f4e34ad` / 13768B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/node_output_projection.py` | `libs/runtime/strategist/output/node_output_projection.py` | `896da85c2baa` / 6356B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/node_trace_projection.py` | `libs/runtime/strategist/output/node_trace_projection.py` | `18b0c5e7dd23` / 6997B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/strategic_answers.py` | `libs/runtime/strategist/output/strategic_answers.py` | `26c68a838ce3` / 202B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/strategist_output_core_fields.py` | `libs/runtime/strategist/output/strategist_output_core_fields.py` | `cf5478bee855` / 9153B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/strategist_output_explanations.py` | `libs/runtime/strategist/output/strategist_output_explanations.py` | `73b362a7a357` / 1357B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/strategist_output_policy_commander_fields.py` | `libs/runtime/strategist/output/strategist_output_policy_commander_fields.py` | `eede76d0f9ad` / 7195B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/strategist_output_stage_reviews.py` | `libs/runtime/strategist/output/strategist_output_stage_reviews.py` | `7cbf8c16e84f` / 2909B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/output/strategy_scores_and_summary.py` | `libs/runtime/strategist/output/strategy_scores_and_summary.py` | `6f41de2eca4e` / 9399B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/__init__.py` | `libs/runtime/strategist/policy/__init__.py` | `e69de29bb2d1` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/exit_and_defaults.py` | `libs/runtime/strategist/policy/exit_and_defaults.py` | `0eb9a9b5c1b1` / 10760B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/global_risk_adjustment.py` | `libs/runtime/strategist/policy/global_risk_adjustment.py` | `fbab9b722bfe` / 1294B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/llm_override_application.py` | `libs/runtime/strategist/policy/llm_override_application.py` | `57c2c0d44e2f` / 4197B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/monitor_entry_policy.py` | `libs/runtime/strategist/policy/monitor_entry_policy.py` | `091388ed8992` / 14619B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/monitor_entry_policy_seed.py` | `libs/runtime/strategist/policy/monitor_entry_policy_seed.py` | `6784c635c7aa` / 2814B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/node_policy_projection.py` | `libs/runtime/strategist/policy/node_policy_projection.py` | `b1319b9e6e6c` / 12881B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/scanner_policy.py` | `libs/runtime/strategist/policy/scanner_policy.py` | `8eeb6808e84c` / 9196B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/strategist/policy/strategy_policy_annotation.py` | `libs/runtime/strategist/policy/strategy_policy_annotation.py` | `8a0c0a9d0d14` / 5041B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-018|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
