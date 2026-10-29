# RF-001 — 코드 구조/함수 재배치 설계 (T02)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-001.md` blob `2e1a3bf30a48815935e66ec237503934e69e4392`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 33개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**실제 함수 확인:** 아래 함수명·규모는 정본 원본에서 확인한 설계 입력이다. 작업시 최신 원격 SHA에서 원함수 및 이미 이동된 몸체를 먼저 확인한다.

| SOURCE_PATH::함수 | 본문 규모 | TARGET_PATH::함수 | 코드 변경 |
|---|---:|---|---|
| `apps/operator_ui/data_access_core.py::_load_operator_brief` | 약 444행 | `apps/operator_ui/data_access_brief_loader.py::load_operator_brief` (RF-001) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `apps/operator_ui/data_access_core.py::_trade_report_index` | 약 154행 | `apps/operator_ui/data_access_report_index.py::trade_report_index` (RF-001) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `apps/operator_ui/data_access_core.py::load_run_detail` | 약 193행 | `apps/operator_ui/data_access_run_detail.py::load_run_detail` (RF-001) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |

**구현 계약:** 입력/출력 dict 키·순서·문자열 bytes, 예외, fallback, monkeypatch는 기존과 동등. IO/LLM/상태/주문 발생 순서를 바꾸지 않으며 실제 effect boundary는 원래 위치에 남긴다. 새 Owner→facade 역import 금지. 기존 동일 target 함수가 있으면 재활용하고 중복 구현하지 않는다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `apps/operator_ui/data_access_core.py` | 112756 | `0666538f5f6ddd74e3ca8a3fa290c95f044fbdb6` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `apps/operator_ui/data_access_core_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `apps/operator_ui/data_access_brief_sections_projection.py` | 23839 | `abf8602e2eea46c875dbab1c31f257e04e585260` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `apps/operator_ui/data_access_brief_sections_projection_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `apps/operator_ui/data_access_brief_compaction.py` | 23528 | `708c0cbc99b8f126cdce6d5309e50b467a5ed7fe` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `apps/operator_ui/data_access_brief_compaction_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `apps/operator_ui/data_access.py` → `apps/operator_ui/data_access.py` | 422 | `23747be56ff8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief.py` → `apps/operator_ui/data_access_brief.py` | 2017 | `a993e258e528` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_canonical_input.py` → `apps/operator_ui/data_access_brief_canonical_input.py` | 18481 | `f3cd04a9668c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_compaction.py` → `apps/operator_ui/data_access_brief_compaction.py` | 23528 | `708c0cbc99b8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_evidence_readout_p15.py` → `apps/operator_ui/data_access_brief_evidence_readout_p15.py` | 9083 | `554a9d1fa86b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_facts.py` → `apps/operator_ui/data_access_brief_facts.py` | 7457 | `3ddfe185a08f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_fallback.py` → `apps/operator_ui/data_access_brief_fallback.py` | 15684 | `d7e3a94ca3c0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_input_projection.py` → `apps/operator_ui/data_access_brief_input_projection.py` | 10711 | `c0bdd87f87b6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_input_sections.py` → `apps/operator_ui/data_access_brief_input_sections.py` | 16998 | `f6f39476d973` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_market_sections.py` → `apps/operator_ui/data_access_brief_market_sections.py` | 13992 | `3105419f352b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_monitor_notes.py` → `apps/operator_ui/data_access_brief_monitor_notes.py` | 11173 | `4f73570f9b14` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_monitor_sections.py` → `apps/operator_ui/data_access_brief_monitor_sections.py` | 18272 | `7cac6e42c32d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_prompts.py` → `apps/operator_ui/data_access_brief_prompts.py` | 11785 | `3cedb7eaa291` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_render_fallback.py` → `apps/operator_ui/data_access_brief_render_fallback.py` | 11372 | `fc4195904672` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_render_helpers.py` → `apps/operator_ui/data_access_brief_render_helpers.py` | 13466 | `2ef7ff64dad9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_render_narrative_helpers.py` → `apps/operator_ui/data_access_brief_render_narrative_helpers.py` | 1670 | `84cb48bf7465` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_render_sections.py` → `apps/operator_ui/data_access_brief_render_sections.py` | 10488 | `ffe4e4bfc091` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_render_summary_derivation.py` → `apps/operator_ui/data_access_brief_render_summary_derivation.py` | 10245 | `3759794e152a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_sanitation.py` → `apps/operator_ui/data_access_brief_sanitation.py` | 14119 | `7b8c960ce590` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_sections_projection.py` → `apps/operator_ui/data_access_brief_sections_projection.py` | 23839 | `abf8602e2eea` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_brief_source_truth_p15.py` → `apps/operator_ui/data_access_brief_source_truth_p15.py` | 7405 | `45a8816ffc03` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_core.py` → `apps/operator_ui/data_access_core.py` | 112756 | `0666538f5f6d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_linkage.py` → `apps/operator_ui/data_access_linkage.py` | 4962 | `1dfe639982ef` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_overview_projection.py` → `apps/operator_ui/data_access_overview_projection.py` | 9336 | `530778971a44` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_reports.py` → `apps/operator_ui/data_access_reports.py` | 312 | `d8fe355e23eb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_run_detail_projection.py` → `apps/operator_ui/data_access_run_detail_projection.py` | 9494 | `b0e22024c5ea` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_run_read_models.py` → `apps/operator_ui/data_access_run_read_models.py` | 16584 | `c2d3cc08f6f4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_runs.py` → `apps/operator_ui/data_access_runs.py` | 1713 | `bde2090e3326` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_status.py` → `apps/operator_ui/data_access_status.py` | 13569 | `68c852e4afcd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_symbol_run_chain.py` → `apps/operator_ui/data_access_symbol_run_chain.py` | 4960 | `69efe0e7f79c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_trade_index_projection.py` → `apps/operator_ui/data_access_trade_index_projection.py` | 9536 | `263c12de487c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_trade_read_models.py` → `apps/operator_ui/data_access_trade_read_models.py` | 12887 | `edbea32ffefa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/operator_ui/data_access_value_formatting.py` → `apps/operator_ui/data_access_value_formatting.py` | 9523 | `f4f543bd7b74` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
