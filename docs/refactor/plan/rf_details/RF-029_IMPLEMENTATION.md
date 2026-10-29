# RF-029 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-029.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 38개 경로.

## 1. 실측 함수 단위 분석 / 배치

이 RF의 Python 함수 본문 실측 없음(원본 Python 부재 또는 읽을 large 함수 없음). 유효한 target 위치의 문서/스크립트/설정/작은 단일 책임 코드는 정당한 KEEP. 새 함수명을 추측하여 개발자가 구현하도록 만들지 않는다.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/reporting/trade_read_model_parts/__init__.py` | `libs/reporting/trade_read_model_parts/__init__.py` | `dcb91cd7d5f1` / 93B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_read_model_parts/read_artifact_selection.py` | `libs/reporting/trade_read_model_parts/read_artifact_selection.py` | `693b150a6842` / 5501B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_read_model_parts/read_display_context.py` | `libs/reporting/trade_read_model_parts/read_display_context.py` | `17f91f315f81` / 10166B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_read_model_parts/read_truth_projection.py` | `libs/reporting/trade_read_model_parts/read_truth_projection.py` | `62bda630841b` / 10928B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story/__init__.py` | `libs/reporting/trade_story/__init__.py` | `98ec21a238b6` / 82B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story/evidence.py` | `libs/reporting/trade_story/evidence.py` | `57097d7d7ee3` / 3195B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_assembly_parts/direct_story.py` | `libs/reporting/trade_story_assembly_parts/direct_story.py` | `182aa196d9fd` / 14196B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_assembly_parts/lifecycle_bundle.py` | `libs/reporting/trade_story_assembly_parts/lifecycle_bundle.py` | `9bcac004ce95` / 11986B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_assembly_parts/lifecycle_evidence.py` | `libs/reporting/trade_story_assembly_parts/lifecycle_evidence.py` | `c72d65981f5b` / 8222B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_assembly_parts/lifecycle_human.py` | `libs/reporting/trade_story_assembly_parts/lifecycle_human.py` | `9c324a8bfaad` / 6320B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_assembly_parts/lifecycle_normalization.py` | `libs/reporting/trade_story_assembly_parts/lifecycle_normalization.py` | `3fcf05c3c35d` / 4244B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_assembly_parts/reasoning_provenance.py` | `libs/reporting/trade_story_assembly_parts/reasoning_provenance.py` | `5842127a5f07` / 4810B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_assembly_parts/report_seeds.py` | `libs/reporting/trade_story_assembly_parts/report_seeds.py` | `010d6bdc593c` / 4487B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_assembly_parts/timeline.py` | `libs/reporting/trade_story_assembly_parts/timeline.py` | `bd019673ac4d` / 3768B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_evidence.py` | `libs/reporting/trade_story_evidence.py` | `5af38a6a2c9d` / 318B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_evidence_parts/canonical.py` | `libs/reporting/trade_story_evidence_parts/canonical.py` | `e2e864b990fe` / 3349B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_evidence_parts/filters.py` | `libs/reporting/trade_story_evidence_parts/filters.py` | `4409adf623e4` / 12640B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_evidence_parts/scanner.py` | `libs/reporting/trade_story_evidence_parts/scanner.py` | `4a799ee64cf1` / 14971B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_facade_parts/dependency_maps.py` | `libs/reporting/trade_story_facade_parts/dependency_maps.py` | `eb8a351b24a7` / 5796B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_facade_parts/filter_checklist.py` | `libs/reporting/trade_story_facade_parts/filter_checklist.py` | `5712a0c9153e` / 4569B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_facade_parts/human_judgments.py` | `libs/reporting/trade_story_facade_parts/human_judgments.py` | `88adc7ef974d` / 5485B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_facade_parts/story_contracts.py` | `libs/reporting/trade_story_facade_parts/story_contracts.py` | `49c6fc520a33` / 6911B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_facade_parts/strategist_evidence.py` | `libs/reporting/trade_story_facade_parts/strategist_evidence.py` | `30218763a8d9` / 4547B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_facade_r3_parts/bodies_01.py` | `libs/reporting/trade_story_facade_r3_parts/bodies_01.py` | `9d64b37ebc96` / 4421B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_human_parts/market_context.py` | `libs/reporting/trade_story_human_parts/market_context.py` | `568a05c3314f` / 11123B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_human_parts/monitor_context.py` | `libs/reporting/trade_story_human_parts/monitor_context.py` | `f960784e5567` / 13830B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_human_parts/monitor_diagnostics.py` | `libs/reporting/trade_story_human_parts/monitor_diagnostics.py` | `07d401459472` / 5197B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_human_parts/monitor_entry_review.py` | `libs/reporting/trade_story_human_parts/monitor_entry_review.py` | `26204f7eb20e` / 8902B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_human_parts/monitor_policy_bullets.py` | `libs/reporting/trade_story_human_parts/monitor_policy_bullets.py` | `4cb442d64dd4` / 5325B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_human_parts/monitor_traces.py` | `libs/reporting/trade_story_human_parts/monitor_traces.py` | `31d40c34d29a` / 7141B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_human_parts/scanner_reason.py` | `libs/reporting/trade_story_human_parts/scanner_reason.py` | `dbde7e037442` / 15223B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_pipeline.py` | `libs/reporting/trade_story_pipeline.py` | `2d64151e46b9` / 18481B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_pipeline_evidence_hydration.py` | `libs/reporting/trade_story_pipeline_evidence_hydration.py` | `13df91d9b960` / 560B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_pipeline_human_payloads.py` | `libs/reporting/trade_story_pipeline_human_payloads.py` | `9b98755db5b2` / 18562B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_pipeline_news.py` | `libs/reporting/trade_story_pipeline_news.py` | `070e226c7812` / 1242B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_pipeline_provenance.py` | `libs/reporting/trade_story_pipeline_provenance.py` | `aaebda6196fb` / 3692B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_pipeline_scanner.py` | `libs/reporting/trade_story_pipeline_scanner.py` | `5370aa9bc3e6` / 1085B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/trade_story_pipeline_story_assembly.py` | `libs/reporting/trade_story_pipeline_story_assembly.py` | `ab34a6dee2ac` / 20868B | 위 실측 함수 이동·효과 경계 먼저 |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-029|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
