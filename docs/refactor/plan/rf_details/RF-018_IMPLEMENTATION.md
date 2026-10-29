# RF-018 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/03_PEER_REVIEW/CODEX_B/RF-018.md` blob `005d5c44ac76657a2363f43e7897ff3a42e74627`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 47개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/runtime/strategist/__init__.py` → `libs/runtime/strategist/__init__.py` | 0 | `e69de29bb2d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/__init__.py` → `libs/runtime/strategist/context/__init__.py` | 0 | `e69de29bb2d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/candidate_rerank.py` → `libs/runtime/strategist/context/candidate_rerank.py` | 2078 | `07b4077a694a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/commander_refresh_context.py` → `libs/runtime/strategist/context/commander_refresh_context.py` | 12167 | `325a4267c2cf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/common_values.py` → `libs/runtime/strategist/context/common_values.py` | 2485 | `dcec3ec8b564` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/llm_input_payload.py` → `libs/runtime/strategist/context/llm_input_payload.py` | 6870 | `a62a0128ba6a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/market_inputs.py` → `libs/runtime/strategist/context/market_inputs.py` | 12825 | `9ea446d39258` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/market_key_events.py` → `libs/runtime/strategist/context/market_key_events.py` | 203 | `19e21da95f3c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/memory.py` → `libs/runtime/strategist/context/memory.py` | 16081 | `33be9482ad9c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/news_compaction.py` → `libs/runtime/strategist/context/news_compaction.py` | 201 | `50ffe432449a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/news_context.py` → `libs/runtime/strategist/context/news_context.py` | 12112 | `35d446121467` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/news_signal_fallbacks.py` → `libs/runtime/strategist/context/news_signal_fallbacks.py` | 3423 | `9fbd55eaa33d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/node_context_projection.py` → `libs/runtime/strategist/context/node_context_projection.py` | 6176 | `b7fd69044ecb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/regime_scoring.py` → `libs/runtime/strategist/context/regime_scoring.py` | 1611 | `f3476b6a84fd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/symbol_read_models.py` → `libs/runtime/strategist/context/symbol_read_models.py` | 204 | `583583f87481` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/theme_candidate_projection.py` → `libs/runtime/strategist/context/theme_candidate_projection.py` | 1860 | `d24f835e3db0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/theme_compaction.py` → `libs/runtime/strategist/context/theme_compaction.py` | 8924 | `b7d4bc396d87` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/theme_packet.py` → `libs/runtime/strategist/context/theme_packet.py` | 12423 | `3f23060a9fd2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/theme_strength.py` → `libs/runtime/strategist/context/theme_strength.py` | 200 | `3b4986442fa4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/context/value_helpers.py` → `libs/runtime/strategist/context/value_helpers.py` | 1268 | `6e65e1c94431` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/llm/__init__.py` → `libs/runtime/strategist/llm/__init__.py` | 0 | `e69de29bb2d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/llm/adjustment_directives.py` → `libs/runtime/strategist/llm/adjustment_directives.py` | 16083 | `148a531f206b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/llm/candidate_watch_overrides.py` → `libs/runtime/strategist/llm/candidate_watch_overrides.py` | 4352 | `dd2467cf694b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/llm/override_normalization.py` → `libs/runtime/strategist/llm/override_normalization.py` | 13816 | `1448908993e2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/llm/response_contract_parsing.py` → `libs/runtime/strategist/llm/response_contract_parsing.py` | 8711 | `b7daa246fc15` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/llm/stage_reviews.py` → `libs/runtime/strategist/llm/stage_reviews.py` | 10545 | `220d4c89a407` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/llm/text_fragment_helpers.py` → `libs/runtime/strategist/llm/text_fragment_helpers.py` | 1589 | `0c3f96b5d44d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/__init__.py` → `libs/runtime/strategist/output/__init__.py` | 0 | `e69de29bb2d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/commander_context_and_plan.py` → `libs/runtime/strategist/output/commander_context_and_plan.py` | 13258 | `8cf270c07651` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/node_event_payloads.py` → `libs/runtime/strategist/output/node_event_payloads.py` | 13768 | `1ec79f4e34ad` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/node_output_projection.py` → `libs/runtime/strategist/output/node_output_projection.py` | 6356 | `896da85c2baa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/node_trace_projection.py` → `libs/runtime/strategist/output/node_trace_projection.py` | 6997 | `18b0c5e7dd23` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/strategic_answers.py` → `libs/runtime/strategist/output/strategic_answers.py` | 202 | `26c68a838ce3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/strategist_output_core_fields.py` → `libs/runtime/strategist/output/strategist_output_core_fields.py` | 9153 | `cf5478bee855` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/strategist_output_explanations.py` → `libs/runtime/strategist/output/strategist_output_explanations.py` | 1357 | `73b362a7a357` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/strategist_output_policy_commander_fields.py` → `libs/runtime/strategist/output/strategist_output_policy_commander_fields.py` | 7195 | `eede76d0f9ad` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/strategist_output_stage_reviews.py` → `libs/runtime/strategist/output/strategist_output_stage_reviews.py` | 2909 | `7cbf8c16e84f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/output/strategy_scores_and_summary.py` → `libs/runtime/strategist/output/strategy_scores_and_summary.py` | 9399 | `6f41de2eca4e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/__init__.py` → `libs/runtime/strategist/policy/__init__.py` | 0 | `e69de29bb2d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/exit_and_defaults.py` → `libs/runtime/strategist/policy/exit_and_defaults.py` | 10760 | `0eb9a9b5c1b1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/global_risk_adjustment.py` → `libs/runtime/strategist/policy/global_risk_adjustment.py` | 1294 | `fbab9b722bfe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/llm_override_application.py` → `libs/runtime/strategist/policy/llm_override_application.py` | 4197 | `57c2c0d44e2f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/monitor_entry_policy.py` → `libs/runtime/strategist/policy/monitor_entry_policy.py` | 14619 | `091388ed8992` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/monitor_entry_policy_seed.py` → `libs/runtime/strategist/policy/monitor_entry_policy_seed.py` | 2814 | `6784c635c7aa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/node_policy_projection.py` → `libs/runtime/strategist/policy/node_policy_projection.py` | 12881 | `b1319b9e6e6c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/scanner_policy.py` → `libs/runtime/strategist/policy/scanner_policy.py` | 9196 | `8eeb6808e84c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/strategist/policy/strategy_policy_annotation.py` → `libs/runtime/strategist/policy/strategy_policy_annotation.py` | 5041 | `8a0c0a9d0d14` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
