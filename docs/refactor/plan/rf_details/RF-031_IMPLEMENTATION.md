# RF-031 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md` blob `af4451c4d6a6c8b482b9f0dd093fefad0e824c9e`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 38개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**실제 함수 확인:** 아래 함수명·규모는 정본 원본에서 확인한 설계 입력이다. 작업시 최신 원격 SHA에서 원함수 및 이미 이동된 몸체를 먼저 확인한다.

| SOURCE_PATH::함수 | 본문 규모 | TARGET_PATH::함수 | 코드 변경 |
|---|---:|---|---|
| `libs/reporting/reporter_ai_review.py::_build_compact_input` | 약 110행 | `libs/reporting/reporter_ai_review_input.py::build_compact_input` (RF-031) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `libs/reporting/reporter_ai_review.py::_build_messages` | 약 44행 | `libs/reporting/reporter_ai_review_input.py::build_messages` (RF-031) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `libs/reporting/reporter_ai_review.py::_normalize_result` | 약 25행 | `libs/reporting/reporter_ai_review_result.py::normalize_result` (RF-031) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `libs/reporting/reporter_ai_review.py::_normalize_evidence_link_items` | 약 21행 | `libs/reporting/reporter_ai_review_result.py::normalize_evidence_link_items` (RF-031) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |

**구현 계약:** 입력/출력 dict 키·순서·문자열 bytes, 예외, fallback, monkeypatch는 기존과 동등. IO/LLM/상태/주문 발생 순서를 바꾸지 않으며 실제 effect boundary는 원래 위치에 남긴다. 새 Owner→facade 역import 금지. 기존 동일 target 함수가 있으면 재활용하고 중복 구현하지 않는다.
**순서:** 입력/메시지 생성 2함수 먼저 이동 후 결과 정규화 2함수. `_clip_str`, `_list_str`, `json.dumps`는 facade 호출시점 주입; LLM 호출·writer 본문 이동 금지.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/reporting/trade_report_ai.py` | 64646 | `d0b90c5b792757ad4f0b8fc2f9d8baa97c4adbf0` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_report_ai_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_report_markdown_clean.py` | 48689 | `f2abd5c1249cf8eb2b8e790387efaa751e589076` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_report_markdown_clean_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_report_ai_deterministic.py` | 28650 | `d810c0f97dded584ce9408e51ab82de409e1a8f9` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_report_ai_deterministic_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/reporter_analysis.py` | 28062 | `9b7963ffa5930d4cbbbc27dca1f48cc58402677f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/reporter_analysis_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/reporter_feedback.py` | 27567 | `90a6f54e0cd33d89b7530f7ba6d5c33f4e1edd91` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/reporter_feedback_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/reporter_ai_review.py` | 23229 | `a8c2507f70d2293b0a106830d9366b64b498236c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/reporter_ai_review_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/reporting/reporter_ai_review.py` → `libs/reporting/reporter_ai_review.py` | 23229 | `a8c2507f70d2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_analysis.py` → `libs/reporting/reporter_analysis.py` | 28062 | `9b7963ffa593` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/reporter_feedback.py` → `libs/reporting/reporter_feedback.py` | 27567 | `90a6f54e0cd3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai.py` → `libs/reporting/trade_report_ai.py` | 64646 | `d0b90c5b7927` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai_compact_helpers.py` → `libs/reporting/trade_report_ai_compact_helpers.py` | 334 | `7a591b68bd2f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai_compact_input.py` → `libs/reporting/trade_report_ai_compact_input.py` | 9026 | `685597aa7fb9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai_deterministic.py` → `libs/reporting/trade_report_ai_deterministic.py` | 28650 | `d810c0f97dde` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai_llm.py` → `libs/reporting/trade_report_ai_llm.py` | 310 | `f5a3b40c94ad` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai_merge_policy.py` → `libs/reporting/trade_report_ai_merge_policy.py` | 328 | `b5a4d16fe6ef` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai_prompting.py` → `libs/reporting/trade_report_ai_prompting.py` | 322 | `3f987ab5a1cb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai_shared_facts.py` → `libs/reporting/trade_report_ai_shared_facts.py` | 328 | `339576c0f917` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_ai_summary_adapter.py` → `libs/reporting/trade_report_ai_summary_adapter.py` | 334 | `8c3190e10da3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_common.py` → `libs/reporting/trade_report_common.py` | 3174 | `de80a055059e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_markdown_clean.py` → `libs/reporting/trade_report_markdown_clean.py` | 48689 | `f2abd5c1249c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_markdown_monitor.py` → `libs/reporting/trade_report_markdown_monitor.py` | 336 | `4f7e7d110ec6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_markdown_scanner.py` → `libs/reporting/trade_report_markdown_scanner.py` | 336 | `6155383e49ca` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_markdown_strategy_memory.py` → `libs/reporting/trade_report_markdown_strategy_memory.py` | 4539 | `29fe568654df` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_markdown_truth.py` → `libs/reporting/trade_report_markdown_truth.py` | 16961 | `ba367a62a5ef` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_post_exit_shadow.py` → `libs/reporting/trade_report_post_exit_shadow.py` | 525 | `c5aaf2f0b5b3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_runtime_generation.py` → `libs/reporting/trade_report_runtime_generation.py` | 15796 | `59bd7bb713d8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_runtime_policy.py` → `libs/reporting/trade_report_runtime_policy.py` | 9391 | `82f5fb331b09` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report_symbol_metadata.py` → `libs/reporting/trade_report_symbol_metadata.py` | 1234 | `1dbe154fe3bc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `tests/test_rf031_reporter_ai_review_caller_contract.py` → `tests/test_rf031_reporter_ai_review_caller_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_reporter_ai_review_contract.py` → `tests/test_rf031_reporter_ai_review_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_reporter_analysis_callers.py` → `tests/test_rf031_reporter_analysis_callers.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_reporter_analysis_helpers_contract.py` → `tests/test_rf031_reporter_analysis_helpers_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_reporter_analysis_optional_writers_contract.py` → `tests/test_rf031_reporter_analysis_optional_writers_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_reporter_analysis_writers.py` → `tests/test_rf031_reporter_analysis_writers.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_reporter_feedback_helpers_contract.py` → `tests/test_rf031_reporter_feedback_helpers_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_report_ai_helpers_contract.py` → `tests/test_rf031_trade_report_ai_helpers_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_report_alias_modules_contract.py` → `tests/test_rf031_trade_report_alias_modules_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_report_compact_input_contract.py` → `tests/test_rf031_trade_report_compact_input_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_report_deterministic_seed_contract.py` → `tests/test_rf031_trade_report_deterministic_seed_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_report_markdown_clean_wrappers_contract.py` → `tests/test_rf031_trade_report_markdown_clean_wrappers_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_report_runtime_generation_plan.py` → `tests/test_rf031_trade_report_runtime_generation_plan.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_report_runtime_policy_contract.py` → `tests/test_rf031_trade_report_runtime_policy_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_report_strategy_memory_labels_contract.py` → `tests/test_rf031_trade_report_strategy_memory_labels_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf031_trade_story_human_payloads_contract.py` → `tests/test_rf031_trade_story_human_payloads_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
