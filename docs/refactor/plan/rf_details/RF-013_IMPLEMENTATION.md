# RF-013 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Claude A 구현, Codex B 읽기 전용 독립 검증. 파일 67개. 원본 RF `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-013.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**읽은 실제 파일:** `libs/agents/reporter/read_models/read_model_bodies_01.py` blob `26790aff9de6afdd6e3fd5aeb3807600b80316b7`, **318 LOC**. 파이썬 함수 정의와 들여쓰기를 읽어 분리 후보를 잡았다. 아래 target은 코드 작성 전 현재 Owner·소비자 중복을 1회 확인하여 필요 시 기존 Owner를 재사용한다.

| 원본 함수/줄 | 분리판정 | 목표 소스::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/agents/reporter/read_models/read_model_bodies_01.py::normalize_canonical_monitor_snapshot_r4_impl` L243–291 | **MOVE_BODY** | `libs/agents/reporter/read_models/read_model_bodies_01_normalize_canonical_monitor_snapshot_r.py::normalize_canonical_monitor_snapshot_r4_impl` | 49행, 부작용 정적 탐지 없음 |
| `libs/agents/reporter/read_models/read_model_bodies_01.py::load_time_bucketed_trade_report_recent_feedback_pack_r4_impl` L108–155 | **MOVE_BODY** | `libs/agents/reporter/read_models/read_model_bodies_01_load_time_bucketed_trade_report_recent.py::load_time_bucketed_trade_report_recent_feedback_pack_r4_impl` | 48행, 부작용 정적 탐지 없음 |
| `libs/agents/reporter/read_models/read_model_bodies_01.py::collect_strategist_feedback_inputs_r4_impl` L70–94 | **MOVE_BODY** | `libs/agents/reporter/read_models/read_model_bodies_01_collect_strategist_feedback_inputs_r4_.py::collect_strategist_feedback_inputs_r4_impl` | 25행, 부작용 정적 탐지 없음 |

### normalize_canonical_monitor_snapshot_r4_impl (L243–291)
- **기능 경계:** `libs/agents/reporter/read_models/read_model_bodies_01.py::normalize_canonical_monitor_snapshot_r4_impl` (49행), 내부 호출 `_fmt_optional_price`, `_fmt_optional_pct`. 감지된 경계: 없음.
- **정확한 목표:** `libs/agents/reporter/read_models/read_model_bodies_01_normalize_canonical_monitor_snapshot_r.py::normalize_canonical_monitor_snapshot_r4_impl`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### load_time_bucketed_trade_report_recent_feedback_pack_r4_impl (L108–155)
- **기능 경계:** `libs/agents/reporter/read_models/read_model_bodies_01.py::load_time_bucketed_trade_report_recent_feedback_pack_r4_impl` (48행), 내부 호출 `_resolve_items`, `_resolve_window_size`, `_bucket`. 감지된 경계: 없음.
- **정확한 목표:** `libs/agents/reporter/read_models/read_model_bodies_01_load_time_bucketed_trade_report_recent.py::load_time_bucketed_trade_report_recent_feedback_pack_r4_impl`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### collect_strategist_feedback_inputs_r4_impl (L70–94)
- **기능 경계:** `libs/agents/reporter/read_models/read_model_bodies_01.py::collect_strategist_feedback_inputs_r4_impl` (25행), 내부 호출 탐지 없음. 감지된 경계: 없음.
- **정확한 목표:** `libs/agents/reporter/read_models/read_model_bodies_01_collect_strategist_feedback_inputs_r4_.py::collect_strategist_feedback_inputs_r4_impl`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `libs/agents/reporter/__init__.py` | `libs/agents/reporter/__init__.py` | 128B `f5038c2c285d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/__init__.py` | `libs/agents/reporter/narrative/__init__.py` | 60B `bceaed968a38` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/agent_pipeline_trace_r8_bodies_01.py` | `libs/agents/reporter/narrative/agent_pipeline_trace_r8_bodies_01.py` | 11811B `2b128dd0fc9f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/markdown_clean_bodies_01.py` | `libs/agents/reporter/narrative/markdown_clean_bodies_01.py` | 2938B `f605f44e4d82` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/narrative_axes.py` | `libs/agents/reporter/narrative/narrative_axes.py` | 7239B `8eee2c502ed8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/news_headlines.py` | `libs/agents/reporter/narrative/news_headlines.py` | 5612B `fb82d8ed57cc` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/news_scanner_contribution.py` | `libs/agents/reporter/narrative/news_scanner_contribution.py` | 9923B `ffe90b982fd1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/news_text.py` | `libs/agents/reporter/narrative/news_text.py` | 4870B `2ba553edf253` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/pipeline_trace_bodies_01.py` | `libs/agents/reporter/narrative/pipeline_trace_bodies_01.py` | 13393B `cc6aec344577` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/post_exit_recap_bodies_01.py` | `libs/agents/reporter/narrative/post_exit_recap_bodies_01.py` | 14398B `5279037b0a15` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/post_exit_recap_bodies_02.py` | `libs/agents/reporter/narrative/post_exit_recap_bodies_02.py` | 1989B `8e2c3083df64` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/post_exit_shadow_recap_r8_bodies_01.py` | `libs/agents/reporter/narrative/post_exit_shadow_recap_r8_bodies_01.py` | 6226B `6a56ba3c0f6d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/reasoning_trace.py` | `libs/agents/reporter/narrative/reasoning_trace.py` | 8758B `0807b9f3a942` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/report_ai_bodies_01.py` | `libs/agents/reporter/narrative/report_ai_bodies_01.py` | 3631B `b064bed7ac1f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/scanner_basis.py` | `libs/agents/reporter/narrative/scanner_basis.py` | 5422B `3edf7ab210d6` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/scanner_evidence_fit.py` | `libs/agents/reporter/narrative/scanner_evidence_fit.py` | 7671B `9b5f01292460` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/scanner_selection_trace.py` | `libs/agents/reporter/narrative/scanner_selection_trace.py` | 6434B `91866d5bbe2a` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/single_trade_report_bodies_01.py` | `libs/agents/reporter/narrative/single_trade_report_bodies_01.py` | 4123B `143d923cfb90` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/single_trade_report_r8_bodies_01.py` | `libs/agents/reporter/narrative/single_trade_report_r8_bodies_01.py` | 18035B `f290c10cb0c8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/story_provenance_bodies_01.py` | `libs/agents/reporter/narrative/story_provenance_bodies_01.py` | 9017B `aade3e9233ef` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/strategist_quant_context_report.py` | `libs/agents/reporter/narrative/strategist_quant_context_report.py` | 5330B `7068f16019b1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/strategy_memory_md_bodies_01.py` | `libs/agents/reporter/narrative/strategy_memory_md_bodies_01.py` | 25209B `c135893fff2c` | 큰 Python 함수 추가 실사: 서로 다른 실제 책임 확인 후 이름 붙여 분리 |
| `libs/agents/reporter/narrative/strategy_memory_md_bodies_02.py` | `libs/agents/reporter/narrative/strategy_memory_md_bodies_02.py` | 8370B `a35bbbfc1ac9` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/symbol_trade_report_bodies_01.py` | `libs/agents/reporter/narrative/symbol_trade_report_bodies_01.py` | 13349B `41e1c4644e3f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/symbol_trade_report_bodies_02.py` | `libs/agents/reporter/narrative/symbol_trade_report_bodies_02.py` | 6581B `639bbb0fe717` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/symbol_trade_report_r8_bodies_01.py` | `libs/agents/reporter/narrative/symbol_trade_report_r8_bodies_01.py` | 11664B `e744fc3b6746` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/trade_execution_outcome_text.py` | `libs/agents/reporter/narrative/trade_execution_outcome_text.py` | 7995B `ca7ff430a44c` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/trade_explain_bodies_01.py` | `libs/agents/reporter/narrative/trade_explain_bodies_01.py` | 18502B `a2639503770b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/trade_explain_r8_bodies_01.py` | `libs/agents/reporter/narrative/trade_explain_r8_bodies_01.py` | 9222B `d20adbc3d2d4` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/trade_fallback_text.py` | `libs/agents/reporter/narrative/trade_fallback_text.py` | 1441B `de225b4556c9` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/trade_report_common_r9_bodies_01.py` | `libs/agents/reporter/narrative/trade_report_common_r9_bodies_01.py` | 3887B `51748f685579` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/trade_report_post_exit_shadow.py` | `libs/agents/reporter/narrative/trade_report_post_exit_shadow.py` | 7701B `040c582f9965` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/trade_reporter_status_text.py` | `libs/agents/reporter/narrative/trade_reporter_status_text.py` | 3695B `ce3578e8d2e6` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/narrative/truth_source_labels.py` | `libs/agents/reporter/narrative/truth_source_labels.py` | 2890B `5a30f3df03c1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/__init__.py` | `libs/agents/reporter/read_models/__init__.py` | 61B `fb47c915bbe8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/bundle_assembly_bodies_01.py` | `libs/agents/reporter/read_models/bundle_assembly_bodies_01.py` | 20919B `ca23065756d3` | 큰 Python 함수 추가 실사: 서로 다른 실제 책임 확인 후 이름 붙여 분리 |
| `libs/agents/reporter/read_models/bundle_state_bodies_01.py` | `libs/agents/reporter/read_models/bundle_state_bodies_01.py` | 12969B `a55554b728dc` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/chart_structure_decision_hint_summary.py` | `libs/agents/reporter/read_models/chart_structure_decision_hint_summary.py` | 9316B `16a5d887bc3a` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/compact_input_bodies_01.py` | `libs/agents/reporter/read_models/compact_input_bodies_01.py` | 19587B `ac78436e7fbd` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/entry_blocker_bodies_01.py` | `libs/agents/reporter/read_models/entry_blocker_bodies_01.py` | 26866B `a9cab49f5c37` | 큰 Python 함수 추가 실사: 서로 다른 실제 책임 확인 후 이름 붙여 분리 |
| `libs/agents/reporter/read_models/entry_blocker_bodies_02.py` | `libs/agents/reporter/read_models/entry_blocker_bodies_02.py` | 6612B `801d7e625608` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/intraday_trade_reports_r9_bodies_01.py` | `libs/agents/reporter/read_models/intraday_trade_reports_r9_bodies_01.py` | 14029B `a6c8e6266e04` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/lifecycle_builder_bodies_01.py` | `libs/agents/reporter/read_models/lifecycle_builder_bodies_01.py` | 9171B `e8a07e1405a6` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/memory_application_bodies_01.py` | `libs/agents/reporter/read_models/memory_application_bodies_01.py` | 13459B `8c64095a61dd` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/memory_surface_bodies_01.py` | `libs/agents/reporter/read_models/memory_surface_bodies_01.py` | 9247B `b38a1f8589a7` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/policy_surface_summary.py` | `libs/agents/reporter/read_models/policy_surface_summary.py` | 8805B `4a3aa078fefa` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/read_model_bodies_01.py` | `libs/agents/reporter/read_models/read_model_bodies_01.py` | 31408B `26790aff9de6` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `libs/agents/reporter/read_models/read_model_bodies_02.py` | `libs/agents/reporter/read_models/read_model_bodies_02.py` | 1774B `a255b3ceb4d3` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/report_deterministic_bodies_01.py` | `libs/agents/reporter/read_models/report_deterministic_bodies_01.py` | 19495B `b6847fa948c1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/report_metadata.py` | `libs/agents/reporter/read_models/report_metadata.py` | 3238B `d0fffd0097d5` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_01.py` | `libs/agents/reporter/read_models/reporter_analysis_bodies_01.py` | 14573B `c8649f2555cb` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_02.py` | `libs/agents/reporter/read_models/reporter_analysis_bodies_02.py` | 27038B `49f549d2924e` | 큰 Python 함수 추가 실사: 서로 다른 실제 책임 확인 후 이름 붙여 분리 |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_03.py` | `libs/agents/reporter/read_models/reporter_analysis_bodies_03.py` | 12937B `c3ac247838be` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/reporter_analysis_bodies_04.py` | `libs/agents/reporter/read_models/reporter_analysis_bodies_04.py` | 14607B `ac0d85a21c9a` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/reporter_analysis_r8_bodies_01.py` | `libs/agents/reporter/read_models/reporter_analysis_r8_bodies_01.py` | 753B `62b2d7f22011` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/strategy_read_model_bodies_01.py` | `libs/agents/reporter/read_models/strategy_read_model_bodies_01.py` | 12553B `3fdc01fcc56d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/strategy_read_model_bodies_02.py` | `libs/agents/reporter/read_models/strategy_read_model_bodies_02.py` | 19586B `d78564e7b661` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/symbol_metadata_fallbacks.py` | `libs/agents/reporter/read_models/symbol_metadata_fallbacks.py` | 1496B `19de879997a6` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/symbol_metadata_name_inference.py` | `libs/agents/reporter/read_models/symbol_metadata_name_inference.py` | 3933B `590597677ced` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/symbol_metadata_resolution.py` | `libs/agents/reporter/read_models/symbol_metadata_resolution.py` | 3708B `d45fb8f63d87` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/symbol_metadata_sources.py` | `libs/agents/reporter/read_models/symbol_metadata_sources.py` | 3216B `19b9586df678` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/symbol_metadata_text.py` | `libs/agents/reporter/read_models/symbol_metadata_text.py` | 2233B `0a7c4346b405` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/symbol_read_model_r9_bodies_01.py` | `libs/agents/reporter/read_models/symbol_read_model_r9_bodies_01.py` | 5729B `5be341088339` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/trade_bundle_assembly_r8_bodies_01.py` | `libs/agents/reporter/read_models/trade_bundle_assembly_r8_bodies_01.py` | 10860B `65f3b533e4b1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/trade_lifecycle_builder_r8_bodies_01.py` | `libs/agents/reporter/read_models/trade_lifecycle_builder_r8_bodies_01.py` | 982B `3aff3fe4eb4d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/trade_pnl_estimate.py` | `libs/agents/reporter/read_models/trade_pnl_estimate.py` | 2081B `614f79242d78` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/reporter/read_models/trade_read_model_r8_bodies_01.py` | `libs/agents/reporter/read_models/trade_read_model_r8_bodies_01.py` | 12439B `da01f1df9e92` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |

## 3. 개발자 독점 순서와 최소 검증

1. Claude A만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 A 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-013|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
