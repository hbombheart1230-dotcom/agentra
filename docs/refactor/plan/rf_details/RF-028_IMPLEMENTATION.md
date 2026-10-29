# RF-028 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-028.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 85개 경로.

## 1. 실측 함수 단위 분석 / 배치

이 RF의 Python 함수 본문 실측 없음(원본 Python 부재 또는 읽을 large 함수 없음). 유효한 target 위치의 문서/스크립트/설정/작은 단일 책임 코드는 정당한 KEEP. 새 함수명을 추측하여 개발자가 구현하도록 만들지 않는다.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/reporting/trade_report/__init__.py` | `libs/reporting/trade_report/__init__.py` | `e51a1b91dabe` / 82B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/compact_input_facts.py` | `libs/reporting/trade_report/ai_facade_parts/compact_input_facts.py` | `4ca9806bccce` / 7820B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/compact_input_payload.py` | `libs/reporting/trade_report/ai_facade_parts/compact_input_payload.py` | `991b8940e1e9` / 20713B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/reporting/trade_report/ai_facade_parts/dependency_maps.py` | `libs/reporting/trade_report/ai_facade_parts/dependency_maps.py` | `cdc4c2afea54` / 5303B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/duration_language.py` | `libs/reporting/trade_report/ai_facade_parts/duration_language.py` | `1bfebbeb83b9` / 3045B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/entry_gate_snapshots.py` | `libs/reporting/trade_report/ai_facade_parts/entry_gate_snapshots.py` | `daae97e1a37f` / 3289B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/fallback_sections_schema.py` | `libs/reporting/trade_report/ai_facade_parts/fallback_sections_schema.py` | `acfaffd0e7c7` / 16426B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/fallback_seed_context.py` | `libs/reporting/trade_report/ai_facade_parts/fallback_seed_context.py` | `40934907a57a` / 6358B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/fallback_summary_status.py` | `libs/reporting/trade_report/ai_facade_parts/fallback_summary_status.py` | `c6de735cd59f` / 5699B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/holding_memory_compaction.py` | `libs/reporting/trade_report/ai_facade_parts/holding_memory_compaction.py` | `79be27f4e0ea` / 4528B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/lifecycle_status_labels.py` | `libs/reporting/trade_report/ai_facade_parts/lifecycle_status_labels.py` | `efd54b900bb2` / 3238B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/market_context_text.py` | `libs/reporting/trade_report/ai_facade_parts/market_context_text.py` | `c0264b2532fc` / 3135B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/market_labels.py` | `libs/reporting/trade_report/ai_facade_parts/market_labels.py` | `163dee1ab38e` / 4993B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/scanner_labels.py` | `libs/reporting/trade_report/ai_facade_parts/scanner_labels.py` | `50ecaf672098` / 6827B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/scanner_selection.py` | `libs/reporting/trade_report/ai_facade_parts/scanner_selection.py` | `ba494df955fd` / 4426B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_parts/text_helpers.py` | `libs/reporting/trade_report/ai_facade_parts/text_helpers.py` | `ae1cec1c23a0` / 1272B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_01.py` | `libs/reporting/trade_report/ai_facade_r3_parts/bodies_01.py` | `6a6b9f2412d0` / 10802B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_02.py` | `libs/reporting/trade_report/ai_facade_r3_parts/bodies_02.py` | `b4ff54bc0959` / 13172B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_03.py` | `libs/reporting/trade_report/ai_facade_r3_parts/bodies_03.py` | `77904ba2f8d6` / 12646B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_04.py` | `libs/reporting/trade_report/ai_facade_r3_parts/bodies_04.py` | `921774608d49` / 11505B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/ai_facade_r3_parts/bodies_05.py` | `libs/reporting/trade_report/ai_facade_r3_parts/bodies_05.py` | `4e552e0ccd2c` / 4074B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/compact_helpers.py` | `libs/reporting/trade_report/compact_helpers.py` | `10f710874c9e` / 9388B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/context.py` | `libs/reporting/trade_report/context.py` | `5e159043e91b` / 12124B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/llm.py` | `libs/reporting/trade_report/llm.py` | `ce4a1bf60fc7` / 10952B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_dependency_maps.py` | `libs/reporting/trade_report/markdown_clean_dependency_maps.py` | `07ed1b3b8a3b` / 14112B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_operator_narrative.py` | `libs/reporting/trade_report/markdown_clean_operator_narrative.py` | `abc4a5a8302e` / 11646B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_parts/memory_policy_phases.py` | `libs/reporting/trade_report/markdown_clean_parts/memory_policy_phases.py` | `73b07b5d8895` / 7221B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_parts/monitor_artifact_resolution.py` | `libs/reporting/trade_report/markdown_clean_parts/monitor_artifact_resolution.py` | `d190c45a379d` / 3625B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_parts/news_headlines.py` | `libs/reporting/trade_report/markdown_clean_parts/news_headlines.py` | `7fb7bd713a61` / 3631B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_parts/operator_labels.py` | `libs/reporting/trade_report/markdown_clean_parts/operator_labels.py` | `a243f2c8cd00` / 9477B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_parts/report_paths_and_time.py` | `libs/reporting/trade_report/markdown_clean_parts/report_paths_and_time.py` | `60b45b986452` / 3729B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_parts/strategist_language.py` | `libs/reporting/trade_report/markdown_clean_parts/strategist_language.py` | `941f240f69ff` / 3918B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_parts/summary_language.py` | `libs/reporting/trade_report/markdown_clean_parts/summary_language.py` | `01860f233429` / 6199B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_01.py` | `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_01.py` | `74404d2f1ae7` / 11304B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_02.py` | `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_02.py` | `1e606792d067` / 11184B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_03.py` | `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_03.py` | `a9f870faf8e3` / 12822B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_04.py` | `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_04.py` | `df49808a79f6` / 11269B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_05.py` | `libs/reporting/trade_report/markdown_clean_r3_parts/bodies_05.py` | `88aff9090b80` / 3041B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_diagnostics.py` | `libs/reporting/trade_report/markdown_diagnostics.py` | `81fb0842e0da` / 14646B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_signal_parts/entry_metrics.py` | `libs/reporting/trade_report/markdown_signal_parts/entry_metrics.py` | `ffc9547aec35` / 10985B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_signal_parts/entry_watch.py` | `libs/reporting/trade_report/markdown_signal_parts/entry_watch.py` | `579886ea30ee` / 15725B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_signal_parts/exit.py` | `libs/reporting/trade_report/markdown_signal_parts/exit.py` | `bfe5df83da03` / 15599B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_signals.py` | `libs/reporting/trade_report/markdown_signals.py` | `b2b26673b483` / 494B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_strategy.py` | `libs/reporting/trade_report/markdown_strategy.py` | `b50e92e7a0a3` / 20114B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_report/markdown_summary.py` | `libs/reporting/trade_report/markdown_summary.py` | `0ecafb94b11c` / 2883B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/markdown_translation.py` | `libs/reporting/trade_report/markdown_translation.py` | `3b1e3d1ba4fb` / 12538B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/merge_policy.py` | `libs/reporting/trade_report/merge_policy.py` | `06d613b31775` / 15127B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/normalization.py` | `libs/reporting/trade_report/normalization.py` | `decdeadcf913` / 16659B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/operator_parts/__init__.py` | `libs/reporting/trade_report/operator_parts/__init__.py` | `60ecc0e9ea75` / 77B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/operator_parts/context_patterns.py` | `libs/reporting/trade_report/operator_parts/context_patterns.py` | `685dd62bfe98` / 8556B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/operator_parts/exact_phrases.py` | `libs/reporting/trade_report/operator_parts/exact_phrases.py` | `791418df2854` / 8195B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/operator_parts/language.py` | `libs/reporting/trade_report/operator_parts/language.py` | `e758f53d7951` / 6572B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/operator_parts/lifecycle_patterns.py` | `libs/reporting/trade_report/operator_parts/lifecycle_patterns.py` | `1a1edec8d57f` / 10638B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/operator_text.py` | `libs/reporting/trade_report/operator_text.py` | `335d5e14fb88` / 13231B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/prompting.py` | `libs/reporting/trade_report/prompting.py` | `a4aaaaaf0ee3` / 14283B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_parts/entry_bullets.py` | `libs/reporting/trade_report/section_parts/entry_bullets.py` | `711f177126bb` / 7885B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_parts/entry_decision.py` | `libs/reporting/trade_report/section_parts/entry_decision.py` | `ecc9ddf37dcb` / 11289B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_parts/execution_quality.py` | `libs/reporting/trade_report/section_parts/execution_quality.py` | `8f1369690512` / 4824B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_parts/lifecycle_bullets.py` | `libs/reporting/trade_report/section_parts/lifecycle_bullets.py` | `1bca7e942e70` / 9562B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_parts/market_context.py` | `libs/reporting/trade_report/section_parts/market_context.py` | `40cf49db28ed` / 9968B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_parts/reporter_evaluation.py` | `libs/reporting/trade_report/section_parts/reporter_evaluation.py` | `e3b37b5caded` / 12943B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_parts/scanner_selection.py` | `libs/reporting/trade_report/section_parts/scanner_selection.py` | `ed05fab405ca` / 16096B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_parts/strategist.py` | `libs/reporting/trade_report/section_parts/strategist.py` | `d679c6d882b3` / 12513B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_seed_parts/commander.py` | `libs/reporting/trade_report/section_seed_parts/commander.py` | `c239be9371e0` / 4898B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_seed_parts/monitor.py` | `libs/reporting/trade_report/section_seed_parts/monitor.py` | `5cd03cd15d49` / 10284B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_seed_parts/scanner.py` | `libs/reporting/trade_report/section_seed_parts/scanner.py` | `2da1dc23eccd` / 5838B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/section_seed_parts/strategist.py` | `libs/reporting/trade_report/section_seed_parts/strategist.py` | `175034187a1f` / 7431B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/sections.py` | `libs/reporting/trade_report/sections.py` | `4fb16c44cb01` / 14765B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/service.py` | `libs/reporting/trade_report/service.py` | `5aaec67ba24c` / 169B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/services/ai_report.py` | `libs/reporting/trade_report/services/ai_report.py` | `e48639d22eab` / 15515B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/services/trade_summary.py` | `libs/reporting/trade_report/services/trade_summary.py` | `c67a2fcb138a` / 9739B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/shared_facts.py` | `libs/reporting/trade_report/shared_facts.py` | `888a666ad616` / 20532B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/trade_report/summary_adapter.py` | `libs/reporting/trade_report/summary_adapter.py` | `3cc0f1475581` / 7222B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_input_parts/broker_alignment.py` | `libs/reporting/trade_report/summary_input_parts/broker_alignment.py` | `c2f5c0ce8cbe` / 1517B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_input_parts/decision_flow.py` | `libs/reporting/trade_report/summary_input_parts/decision_flow.py` | `d4af4002b023` / 5041B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_input_parts/main_builder.py` | `libs/reporting/trade_report/summary_input_parts/main_builder.py` | `bb9de1ce5b5c` / 18546B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_input_parts/market_and_strategy.py` | `libs/reporting/trade_report/summary_input_parts/market_and_strategy.py` | `7d2738423a21` / 2069B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_parts/findings.py` | `libs/reporting/trade_report/summary_parts/findings.py` | `fd57b980cbec` / 4967B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_parts/render_diagnostics.py` | `libs/reporting/trade_report/summary_parts/render_diagnostics.py` | `3273cb90474b` / 8034B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_render_parts/closing.py` | `libs/reporting/trade_report/summary_render_parts/closing.py` | `dc3544026f7f` / 3602B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_render_parts/decision_lifecycle.py` | `libs/reporting/trade_report/summary_render_parts/decision_lifecycle.py` | `664a1475aedf` / 7806B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_render_parts/main_renderer.py` | `libs/reporting/trade_report/summary_render_parts/main_renderer.py` | `ec1a686f6546` / 19707B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_render_parts/market_news.py` | `libs/reporting/trade_report/summary_render_parts/market_news.py` | `cf0df600c436` / 4604B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_render_parts/overview.py` | `libs/reporting/trade_report/summary_render_parts/overview.py` | `8fa82f9242f9` / 4565B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_report/summary_render_parts/render_helpers.py` | `libs/reporting/trade_report/summary_render_parts/render_helpers.py` | `037d338abd07` / 5439B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-028|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
