# RF-013 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-013.md` blob `860fbc8855100e56266b9ec930286b9b21e8b4f6`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 67개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/agents/reporter/read_models/read_model_bodies_01.py` | 31408 | `26790aff9de6afdd6e3fd5aeb3807600b80316b7` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/agents/reporter/read_models/read_model_bodies_01_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_02.py` | 27038 | `49f549d2924ec01f720e454efe90d256765cf160` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/agents/reporter/read_models/reporter_analysis_bodies_02_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/agents/reporter/read_models/entry_blocker_bodies_01.py` | 26866 | `a9cab49f5c37f5a430a91e09d1c59ed0194cb8f8` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/agents/reporter/read_models/entry_blocker_bodies_01_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/agents/reporter/narrative/strategy_memory_md_bodies_01.py` | 25209 | `c135893fff2c353eeab16cb23ebfed966ff27f68` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/agents/reporter/narrative/strategy_memory_md_bodies_01_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/agents/reporter/read_models/bundle_assembly_bodies_01.py` | 20919 | `ca23065756d3a46dc3d81051615c7652e0cb7cc6` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/agents/reporter/read_models/bundle_assembly_bodies_01_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/agents/reporter/__init__.py` → `libs/agents/reporter/__init__.py` | 128 | `f5038c2c285d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/__init__.py` → `libs/agents/reporter/narrative/__init__.py` | 60 | `bceaed968a38` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/agent_pipeline_trace_r8_bodies_01.py` → `libs/agents/reporter/narrative/agent_pipeline_trace_r8_bodies_01.py` | 11811 | `2b128dd0fc9f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/markdown_clean_bodies_01.py` → `libs/agents/reporter/narrative/markdown_clean_bodies_01.py` | 2938 | `f605f44e4d82` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/narrative_axes.py` → `libs/agents/reporter/narrative/narrative_axes.py` | 7239 | `8eee2c502ed8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/news_headlines.py` → `libs/agents/reporter/narrative/news_headlines.py` | 5612 | `fb82d8ed57cc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/news_scanner_contribution.py` → `libs/agents/reporter/narrative/news_scanner_contribution.py` | 9923 | `ffe90b982fd1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/news_text.py` → `libs/agents/reporter/narrative/news_text.py` | 4870 | `2ba553edf253` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/pipeline_trace_bodies_01.py` → `libs/agents/reporter/narrative/pipeline_trace_bodies_01.py` | 13393 | `cc6aec344577` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/post_exit_recap_bodies_01.py` → `libs/agents/reporter/narrative/post_exit_recap_bodies_01.py` | 14398 | `5279037b0a15` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/post_exit_recap_bodies_02.py` → `libs/agents/reporter/narrative/post_exit_recap_bodies_02.py` | 1989 | `8e2c3083df64` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/post_exit_shadow_recap_r8_bodies_01.py` → `libs/agents/reporter/narrative/post_exit_shadow_recap_r8_bodies_01.py` | 6226 | `6a56ba3c0f6d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/reasoning_trace.py` → `libs/agents/reporter/narrative/reasoning_trace.py` | 8758 | `0807b9f3a942` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/report_ai_bodies_01.py` → `libs/agents/reporter/narrative/report_ai_bodies_01.py` | 3631 | `b064bed7ac1f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/scanner_basis.py` → `libs/agents/reporter/narrative/scanner_basis.py` | 5422 | `3edf7ab210d6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/scanner_evidence_fit.py` → `libs/agents/reporter/narrative/scanner_evidence_fit.py` | 7671 | `9b5f01292460` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/scanner_selection_trace.py` → `libs/agents/reporter/narrative/scanner_selection_trace.py` | 6434 | `91866d5bbe2a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/single_trade_report_bodies_01.py` → `libs/agents/reporter/narrative/single_trade_report_bodies_01.py` | 4123 | `143d923cfb90` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/single_trade_report_r8_bodies_01.py` → `libs/agents/reporter/narrative/single_trade_report_r8_bodies_01.py` | 18035 | `f290c10cb0c8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/story_provenance_bodies_01.py` → `libs/agents/reporter/narrative/story_provenance_bodies_01.py` | 9017 | `aade3e9233ef` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/strategist_quant_context_report.py` → `libs/agents/reporter/narrative/strategist_quant_context_report.py` | 5330 | `7068f16019b1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/strategy_memory_md_bodies_01.py` → `libs/agents/reporter/narrative/strategy_memory_md_bodies_01.py` | 25209 | `c135893fff2c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/strategy_memory_md_bodies_02.py` → `libs/agents/reporter/narrative/strategy_memory_md_bodies_02.py` | 8370 | `a35bbbfc1ac9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/symbol_trade_report_bodies_01.py` → `libs/agents/reporter/narrative/symbol_trade_report_bodies_01.py` | 13349 | `41e1c4644e3f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/symbol_trade_report_bodies_02.py` → `libs/agents/reporter/narrative/symbol_trade_report_bodies_02.py` | 6581 | `639bbb0fe717` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/symbol_trade_report_r8_bodies_01.py` → `libs/agents/reporter/narrative/symbol_trade_report_r8_bodies_01.py` | 11664 | `e744fc3b6746` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/trade_execution_outcome_text.py` → `libs/agents/reporter/narrative/trade_execution_outcome_text.py` | 7995 | `ca7ff430a44c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/trade_explain_bodies_01.py` → `libs/agents/reporter/narrative/trade_explain_bodies_01.py` | 18502 | `a2639503770b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/trade_explain_r8_bodies_01.py` → `libs/agents/reporter/narrative/trade_explain_r8_bodies_01.py` | 9222 | `d20adbc3d2d4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/trade_fallback_text.py` → `libs/agents/reporter/narrative/trade_fallback_text.py` | 1441 | `de225b4556c9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/trade_report_common_r9_bodies_01.py` → `libs/agents/reporter/narrative/trade_report_common_r9_bodies_01.py` | 3887 | `51748f685579` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/trade_report_post_exit_shadow.py` → `libs/agents/reporter/narrative/trade_report_post_exit_shadow.py` | 7701 | `040c582f9965` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/trade_reporter_status_text.py` → `libs/agents/reporter/narrative/trade_reporter_status_text.py` | 3695 | `ce3578e8d2e6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/narrative/truth_source_labels.py` → `libs/agents/reporter/narrative/truth_source_labels.py` | 2890 | `5a30f3df03c1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/__init__.py` → `libs/agents/reporter/read_models/__init__.py` | 61 | `fb47c915bbe8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/bundle_assembly_bodies_01.py` → `libs/agents/reporter/read_models/bundle_assembly_bodies_01.py` | 20919 | `ca23065756d3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/bundle_state_bodies_01.py` → `libs/agents/reporter/read_models/bundle_state_bodies_01.py` | 12969 | `a55554b728dc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/chart_structure_decision_hint_summary.py` → `libs/agents/reporter/read_models/chart_structure_decision_hint_summary.py` | 9316 | `16a5d887bc3a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/compact_input_bodies_01.py` → `libs/agents/reporter/read_models/compact_input_bodies_01.py` | 19587 | `ac78436e7fbd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/entry_blocker_bodies_01.py` → `libs/agents/reporter/read_models/entry_blocker_bodies_01.py` | 26866 | `a9cab49f5c37` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/entry_blocker_bodies_02.py` → `libs/agents/reporter/read_models/entry_blocker_bodies_02.py` | 6612 | `801d7e625608` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/intraday_trade_reports_r9_bodies_01.py` → `libs/agents/reporter/read_models/intraday_trade_reports_r9_bodies_01.py` | 14029 | `a6c8e6266e04` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/lifecycle_builder_bodies_01.py` → `libs/agents/reporter/read_models/lifecycle_builder_bodies_01.py` | 9171 | `e8a07e1405a6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/memory_application_bodies_01.py` → `libs/agents/reporter/read_models/memory_application_bodies_01.py` | 13459 | `8c64095a61dd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/memory_surface_bodies_01.py` → `libs/agents/reporter/read_models/memory_surface_bodies_01.py` | 9247 | `b38a1f8589a7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/policy_surface_summary.py` → `libs/agents/reporter/read_models/policy_surface_summary.py` | 8805 | `4a3aa078fefa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/read_model_bodies_01.py` → `libs/agents/reporter/read_models/read_model_bodies_01.py` | 31408 | `26790aff9de6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/read_model_bodies_02.py` → `libs/agents/reporter/read_models/read_model_bodies_02.py` | 1774 | `a255b3ceb4d3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/report_deterministic_bodies_01.py` → `libs/agents/reporter/read_models/report_deterministic_bodies_01.py` | 19495 | `b6847fa948c1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/report_metadata.py` → `libs/agents/reporter/read_models/report_metadata.py` | 3238 | `d0fffd0097d5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_01.py` → `libs/agents/reporter/read_models/reporter_analysis_bodies_01.py` | 14573 | `c8649f2555cb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_02.py` → `libs/agents/reporter/read_models/reporter_analysis_bodies_02.py` | 27038 | `49f549d2924e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_03.py` → `libs/agents/reporter/read_models/reporter_analysis_bodies_03.py` | 12937 | `c3ac247838be` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_04.py` → `libs/agents/reporter/read_models/reporter_analysis_bodies_04.py` | 14607 | `ac0d85a21c9a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/reporter_analysis_r8_bodies_01.py` → `libs/agents/reporter/read_models/reporter_analysis_r8_bodies_01.py` | 753 | `62b2d7f22011` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/strategy_read_model_bodies_01.py` → `libs/agents/reporter/read_models/strategy_read_model_bodies_01.py` | 12553 | `3fdc01fcc56d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/strategy_read_model_bodies_02.py` → `libs/agents/reporter/read_models/strategy_read_model_bodies_02.py` | 19586 | `d78564e7b661` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/symbol_metadata_fallbacks.py` → `libs/agents/reporter/read_models/symbol_metadata_fallbacks.py` | 1496 | `19de879997a6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/symbol_metadata_name_inference.py` → `libs/agents/reporter/read_models/symbol_metadata_name_inference.py` | 3933 | `590597677ced` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/symbol_metadata_resolution.py` → `libs/agents/reporter/read_models/symbol_metadata_resolution.py` | 3708 | `d45fb8f63d87` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/symbol_metadata_sources.py` → `libs/agents/reporter/read_models/symbol_metadata_sources.py` | 3216 | `19b9586df678` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/symbol_metadata_text.py` → `libs/agents/reporter/read_models/symbol_metadata_text.py` | 2233 | `0a7c4346b405` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/symbol_read_model_r9_bodies_01.py` → `libs/agents/reporter/read_models/symbol_read_model_r9_bodies_01.py` | 5729 | `5be341088339` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/trade_bundle_assembly_r8_bodies_01.py` → `libs/agents/reporter/read_models/trade_bundle_assembly_r8_bodies_01.py` | 10860 | `65f3b533e4b1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/trade_lifecycle_builder_r8_bodies_01.py` → `libs/agents/reporter/read_models/trade_lifecycle_builder_r8_bodies_01.py` | 982 | `3aff3fe4eb4d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/trade_pnl_estimate.py` → `libs/agents/reporter/read_models/trade_pnl_estimate.py` | 2081 | `614f79242d78` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/agents/reporter/read_models/trade_read_model_r8_bodies_01.py` → `libs/agents/reporter/read_models/trade_read_model_r8_bodies_01.py` | 12439 | `da01f1df9e92` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
