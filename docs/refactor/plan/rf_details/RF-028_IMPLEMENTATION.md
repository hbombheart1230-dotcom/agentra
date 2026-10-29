# RF-028 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-028.md` blob `396471c1dd682ca74210e435ab230bc064f9d080`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 85개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/reporting/trade_report/ai_facade_parts/compact_input_payload.py` | 20713 | `991b8940e1e9579ecad54d56e263cd0db90e5d85` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_report/ai_facade_parts/compact_input_payload_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_report/shared_facts.py` | 20532 | `888a666ad6167f0fb39a3b2a089f786e075cd35a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_report/shared_facts_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/trade_report/markdown_strategy.py` | 20114 | `b50e92e7a0a3a64653ee56fe92ccda4154d2ffc1` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/trade_report/markdown_strategy_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/reporting/trade_report/__init__.py` → `libs/reporting/trade_report/__init__.py` | 82 | `e51a1b91dabe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/compact_input_facts.py` → `libs/reporting/trade_report/ai_facade_parts/compact_input_facts.py` | 7820 | `4ca9806bccce` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/compact_input_payload.py` → `libs/reporting/trade_report/ai_facade_parts/compact_input_payload.py` | 20713 | `991b8940e1e9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/dependency_maps.py` → `libs/reporting/trade_report/ai_facade_parts/dependency_maps.py` | 5303 | `cdc4c2afea54` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/duration_language.py` → `libs/reporting/trade_report/ai_facade_parts/duration_language.py` | 3045 | `1bfebbeb83b9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/entry_gate_snapshots.py` → `libs/reporting/trade_report/ai_facade_parts/entry_gate_snapshots.py` | 3289 | `daae97e1a37f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/fallback_sections_schema.py` → `libs/reporting/trade_report/ai_facade_parts/fallback_sections_schema.py` | 16426 | `acfaffd0e7c7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/fallback_seed_context.py` → `libs/reporting/trade_report/ai_facade_parts/fallback_seed_context.py` | 6358 | `40934907a57a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/fallback_summary_status.py` → `libs/reporting/trade_report/ai_facade_parts/fallback_summary_status.py` | 5699 | `c6de735cd59f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/holding_memory_compaction.py` → `libs/reporting/trade_report/ai_facade_parts/holding_memory_compaction.py` | 4528 | `79be27f4e0ea` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/lifecycle_status_labels.py` → `libs/reporting/trade_report/ai_facade_parts/lifecycle_status_labels.py` | 3238 | `efd54b900bb2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/market_context_text.py` → `libs/reporting/trade_report/ai_facade_parts/market_context_text.py` | 3135 | `c0264b2532fc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/market_labels.py` → `libs/reporting/trade_report/ai_facade_parts/market_labels.py` | 4993 | `163dee1ab38e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/scanner_labels.py` → `libs/reporting/trade_report/ai_facade_parts/scanner_labels.py` | 6827 | `50ecaf672098` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/scanner_selection.py` → `libs/reporting/trade_report/ai_facade_parts/scanner_selection.py` | 4426 | `ba494df955fd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_parts/text_helpers.py` → `libs/reporting/trade_report/ai_facade_parts/text_helpers.py` | 1272 | `ae1cec1c23a0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_01.py` → `libs/reporting/trade_report/ai_facade_r3_parts/bodies_01.py` | 10802 | `6a6b9f2412d0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_02.py` → `libs/reporting/trade_report/ai_facade_r3_parts/bodies_02.py` | 13172 | `b4ff54bc0959` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_03.py` → `libs/reporting/trade_report/ai_facade_r3_parts/bodies_03.py` | 12646 | `77904ba2f8d6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_04.py` → `libs/reporting/trade_report/ai_facade_r3_parts/bodies_04.py` | 11505 | `921774608d49` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_05.py` → `libs/reporting/trade_report/ai_facade_r3_parts/bodies_05.py` | 4074 | `4e552e0ccd2c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/compact_helpers.py` → `libs/reporting/trade_report/compact_helpers.py` | 9388 | `10f710874c9e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/context.py` → `libs/reporting/trade_report/context.py` | 12124 | `5e159043e91b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/llm.py` → `libs/reporting/trade_report/llm.py` | 10952 | `ce4a1bf60fc7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_dependency_maps.py` → `libs/reporting/trade_report/markdown_clean_dependency_maps.py` | 14112 | `07ed1b3b8a3b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_operator_narrative.py` → `libs/reporting/trade_report/markdown_clean_operator_narrative.py` | 11646 | `abc4a5a8302e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_parts/memory_policy_phases.py` → `libs/reporting/trade_report/markdown_clean_parts/memory_policy_phases.py` | 7221 | `73b07b5d8895` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_parts/monitor_artifact_resolution.py` → `libs/reporting/trade_report/markdown_clean_parts/monitor_artifact_resolution.py` | 3625 | `d190c45a379d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_parts/news_headlines.py` → `libs/reporting/trade_report/markdown_clean_parts/news_headlines.py` | 3631 | `7fb7bd713a61` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_parts/operator_labels.py` → `libs/reporting/trade_report/markdown_clean_parts/operator_labels.py` | 9477 | `a243f2c8cd00` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_parts/report_paths_and_time.py` → `libs/reporting/trade_report/markdown_clean_parts/report_paths_and_time.py` | 3729 | `60b45b986452` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_parts/strategist_language.py` → `libs/reporting/trade_report/markdown_clean_parts/strategist_language.py` | 3918 | `941f240f69ff` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_parts/summary_language.py` → `libs/reporting/trade_report/markdown_clean_parts/summary_language.py` | 6199 | `01860f233429` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_01.py` → `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_01.py` | 11304 | `74404d2f1ae7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_02.py` → `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_02.py` | 11184 | `1e606792d067` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_03.py` → `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_03.py` | 12822 | `a9f870faf8e3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_04.py` → `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_04.py` | 11269 | `df49808a79f6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_05.py` → `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_05.py` | 3041 | `88aff9090b80` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_diagnostics.py` → `libs/reporting/trade_report/markdown_diagnostics.py` | 14646 | `81fb0842e0da` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_signal_parts/entry_metrics.py` → `libs/reporting/trade_report/markdown_signal_parts/entry_metrics.py` | 10985 | `ffc9547aec35` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_signal_parts/entry_watch.py` → `libs/reporting/trade_report/markdown_signal_parts/entry_watch.py` | 15725 | `579886ea30ee` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_signal_parts/exit.py` → `libs/reporting/trade_report/markdown_signal_parts/exit.py` | 15599 | `bfe5df83da03` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_signals.py` → `libs/reporting/trade_report/markdown_signals.py` | 494 | `b2b26673b483` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_strategy.py` → `libs/reporting/trade_report/markdown_strategy.py` | 20114 | `b50e92e7a0a3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_summary.py` → `libs/reporting/trade_report/markdown_summary.py` | 2883 | `0ecafb94b11c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/markdown_translation.py` → `libs/reporting/trade_report/markdown_translation.py` | 12538 | `3b1e3d1ba4fb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/merge_policy.py` → `libs/reporting/trade_report/merge_policy.py` | 15127 | `06d613b31775` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/normalization.py` → `libs/reporting/trade_report/normalization.py` | 16659 | `decdeadcf913` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/operator_parts/__init__.py` → `libs/reporting/trade_report/operator_parts/__init__.py` | 77 | `60ecc0e9ea75` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/operator_parts/context_patterns.py` → `libs/reporting/trade_report/operator_parts/context_patterns.py` | 8556 | `685dd62bfe98` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/operator_parts/exact_phrases.py` → `libs/reporting/trade_report/operator_parts/exact_phrases.py` | 8195 | `791418df2854` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/operator_parts/language.py` → `libs/reporting/trade_report/operator_parts/language.py` | 6572 | `e758f53d7951` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/operator_parts/lifecycle_patterns.py` → `libs/reporting/trade_report/operator_parts/lifecycle_patterns.py` | 10638 | `1a1edec8d57f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/operator_text.py` → `libs/reporting/trade_report/operator_text.py` | 13231 | `335d5e14fb88` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/prompting.py` → `libs/reporting/trade_report/prompting.py` | 14283 | `a4aaaaaf0ee3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_parts/entry_bullets.py` → `libs/reporting/trade_report/section_parts/entry_bullets.py` | 7885 | `711f177126bb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_parts/entry_decision.py` → `libs/reporting/trade_report/section_parts/entry_decision.py` | 11289 | `ecc9ddf37dcb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_parts/execution_quality.py` → `libs/reporting/trade_report/section_parts/execution_quality.py` | 4824 | `8f1369690512` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_parts/lifecycle_bullets.py` → `libs/reporting/trade_report/section_parts/lifecycle_bullets.py` | 9562 | `1bca7e942e70` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_parts/market_context.py` → `libs/reporting/trade_report/section_parts/market_context.py` | 9968 | `40cf49db28ed` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_parts/reporter_evaluation.py` → `libs/reporting/trade_report/section_parts/reporter_evaluation.py` | 12943 | `e3b37b5caded` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_parts/scanner_selection.py` → `libs/reporting/trade_report/section_parts/scanner_selection.py` | 16096 | `ed05fab405ca` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_parts/strategist.py` → `libs/reporting/trade_report/section_parts/strategist.py` | 12513 | `d679c6d882b3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_seed_parts/commander.py` → `libs/reporting/trade_report/section_seed_parts/commander.py` | 4898 | `c239be9371e0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_seed_parts/monitor.py` → `libs/reporting/trade_report/section_seed_parts/monitor.py` | 10284 | `5cd03cd15d49` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_seed_parts/scanner.py` → `libs/reporting/trade_report/section_seed_parts/scanner.py` | 5838 | `2da1dc23eccd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/section_seed_parts/strategist.py` → `libs/reporting/trade_report/section_seed_parts/strategist.py` | 7431 | `175034187a1f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/sections.py` → `libs/reporting/trade_report/sections.py` | 14765 | `4fb16c44cb01` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/service.py` → `libs/reporting/trade_report/service.py` | 169 | `5aaec67ba24c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/services/ai_report.py` → `libs/reporting/trade_report/services/ai_report.py` | 15515 | `e48639d22eab` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/services/trade_summary.py` → `libs/reporting/trade_report/services/trade_summary.py` | 9739 | `c67a2fcb138a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/shared_facts.py` → `libs/reporting/trade_report/shared_facts.py` | 20532 | `888a666ad616` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_adapter.py` → `libs/reporting/trade_report/summary_adapter.py` | 7222 | `3cc0f1475581` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_input_parts/broker_alignment.py` → `libs/reporting/trade_report/summary_input_parts/broker_alignment.py` | 1517 | `c2f5c0ce8cbe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_input_parts/decision_flow.py` → `libs/reporting/trade_report/summary_input_parts/decision_flow.py` | 5041 | `d4af4002b023` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_input_parts/main_builder.py` → `libs/reporting/trade_report/summary_input_parts/main_builder.py` | 18546 | `bb9de1ce5b5c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_input_parts/market_and_strategy.py` → `libs/reporting/trade_report/summary_input_parts/market_and_strategy.py` | 2069 | `7d2738423a21` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_parts/findings.py` → `libs/reporting/trade_report/summary_parts/findings.py` | 4967 | `fd57b980cbec` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_parts/render_diagnostics.py` → `libs/reporting/trade_report/summary_parts/render_diagnostics.py` | 8034 | `3273cb90474b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_render_parts/closing.py` → `libs/reporting/trade_report/summary_render_parts/closing.py` | 3602 | `dc3544026f7f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_render_parts/decision_lifecycle.py` → `libs/reporting/trade_report/summary_render_parts/decision_lifecycle.py` | 7806 | `664a1475aedf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_render_parts/main_renderer.py` → `libs/reporting/trade_report/summary_render_parts/main_renderer.py` | 19707 | `ec1a686f6546` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_render_parts/market_news.py` → `libs/reporting/trade_report/summary_render_parts/market_news.py` | 4604 | `cf0df600c436` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_render_parts/overview.py` → `libs/reporting/trade_report/summary_render_parts/overview.py` | 4565 | `8fa82f9242f9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/trade_report/summary_render_parts/render_helpers.py` → `libs/reporting/trade_report/summary_render_parts/render_helpers.py` | 5439 | `037d338abd07` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
