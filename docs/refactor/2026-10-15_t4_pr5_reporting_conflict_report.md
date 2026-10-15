# T4 / PR #5 Reporting 충돌 보고서 — 2026-10-15

## 기준과 작업 범위

- 공통 기준: `2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb`
- T4 `refactor/p1.5`: `5c8001c35fb623b8f1a19cfa1b3a1bd9d2e5dca0`
- PR #5 분석 기준 `refactor/agentra-target-tree`: `e353ae631f24308084ab0582cdd72ff0c4ed86fb`
- 산식: `git diff --name-only BASE PR5` ∩ `git diff --name-only BASE T4`. 정확히 11경로(코드 9, 공용 패치노트 2). 내용 차이는 `git diff PR5 T4 -- PATH`; 아래 +/-는 PR5에서 T4 방향이다.
- PR #4 CLOSED·미병합은 사용자가 GitHub에서 확인한 사실을 근거로 사용. 이 실행의 GitHub API는 Forbidden이며 별도 재확인했다고 주장하지 않는다.
- Batch 3 중단. T4 checkout/코드, PR5 Reporting 코드, import 테스트는 이번 작업에서 변경하지 않음. merge/rebase/cherry-pick/auto-merge 실행 없음. 신규 브랜치 생성 없음.
- PR #5 Draft 유지 및 병합 보류. API 접근 제한으로 isDraft 재확인/변경은 불가; Ready 전환 명령을 실행하지 않음. Git push를 통해 보고서만 누적.

## 삭제한 브랜치

- 삭제: `refactor/gpt-p0-strategist-contract-20261015`만. 삭제 시 예상 tip `ddb014a529968789580dcaf408715ebba570957b`를 force-with-lease로 고정해 동시 갱신 시 삭제가 실패하도록 함.
- 삭제 전 전체 이력을 `/workspace/agentra-setup/retired-gpt-p0-strategist-contract-20261015.bundle`에 저장하고 `git bundle verify` 성공. 신규 branch/ref를 만들지 않음.
- 삭제 후 `git ls-remote origin refs/heads/refactor/gpt-p0-strategist-contract-20261015` 결과 없음. 다른 원격 브랜치는 삭제하지 않음.

## 11개 중복 파일: blob SHA 및 내용 차이

아래 SHA는 commit SHA가 아닌 전체 Git blob SHA이다. `—`는 BASE에 경로가 없어 양쪽 add/add임을 뜻한다.

| 경로 | BASE blob | PR5 blob | T4 blob | PR5 → T4 (+/-) |
| --- | --- | --- | --- | --- |
| `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` | `182c687f4780c520121eb40bf0c17d0559a16a32` | `6763b565a09f429c31e95100d70350d9767ff333` | `30f42aac907d6be0d45ffd7ab5998141aa963ecf` | +3445/-34 |
| `docs/trading_agent_patch_notes_detailed_update/patch_notes.md` | `38836b2934bbd97308718175d36f733e08e218e9` | `381d770e7029d3058d2fffea6dd36ab59635f60a` | `93dd924268af878817575395ca5bfe1ae2c6923e` | +1355/-21 |
| `libs/reporting/trade_report/__init__.py` | `—` | `b24aba91d1abbd3042dd55b2ff05666b56ccfd8f` | `e51a1b91dabe697ec05c0ebfe334dee8be47fad2` | +1/-1 |
| `libs/reporting/trade_report/normalization.py` | `—` | `4c6b2a6979d27bf4d0d5421653d3c07e873b1272` | `decdeadcf913c92093ccead60e82ab0720c73abd` | +271/-170 |
| `libs/reporting/trade_report/operator_text.py` | `—` | `ce3578e8d2e6e7036a9f1f48085516a73905fca3` | `335d5e14fb886d14cbe85a11217a35d9ef6cdf2b` | +309/-66 |
| `libs/reporting/trade_report_ai_compact_input.py` | `bb7a05bafefc5224e8a86a842fb63bbb0fdc36d6` | `5fd3fee0b56e5698032ec18359e71d4a7cdafc8c` | `8355b5dd2808282b2fdd9258091b2d4762cb871a` | +415/-6 |
| `libs/reporting/trade_report_markdown_strategy_memory.py` | `d5f5b9339ba8efc36444109097b0e37b6fb1d416` | `2f5bddc4c1828665b6a2466598d77a0d9c7bfd83` | `c2d646e4304cf18473317e62fe7f8057c5eab490` | +728/-6 |
| `libs/reporting/trade_report_markdown_truth.py` | `463870269b21055b669ce648249db847705101c7` | `aeaa9b100c7190fcc9a700432aa0019197814751` | `ba367a62a5ef64a0cbb0cab48f4198f76ab15a9e` | +394/-6 |
| `libs/reporting/trade_story_pipeline_evidence_hydration.py` | `b5110bc8e9e5a685ef06089d27de95602cf5b7d6` | `5fe2506f4880ea760bf74d035f583cda28ddc9fa` | `13df91d9b9604cc9c17d095aca017d255c1169de` | +20/-6 |
| `libs/reporting/trade_story_pipeline_human_payloads.py` | `38e21bf0819a662dc6c5c048695fe63acf9b3d8b` | `a82fae4b0d74eedb30e460a8bdeb482430eb2f9e` | `9b98755db5b26c46dfee6c67ba348c81392d543f` | +347/-6 |
| `libs/reporting/trade_story_pipeline_story_assembly.py` | `52ef963774d455ce608e625227361238097d9c81` | `1f15002bb163f1d837c5676136f16f8c8f62e7bc` | `ab34a6dee2ac91a0f9c5abd1f07939f5b2561dd3` | +328/-6 |

### 1. `docs/trading_agent_patch_notes_detailed_update/patch_notes.json`

공용 이력. PR5는 Batch1/2 항목, T4는 확장된 작업 이력을 포함. T4 전체 이력을 보존하고 PR5 신규 항목만 version/date로 중복 확인 후 추가; entry_count 재계산.
행 수: PR5 3113, T4 6524.

### 2. `docs/trading_agent_patch_notes_detailed_update/patch_notes.md`

공용 이력. T4 기존 내용을 보존하고 PR5 Batch1/2 설명 및 이 보고서 항목만 중복 없이 추가. 파일 전체 대체 금지.
행 수: PR5 1858, T4 3192.

### 3. `libs/reporting/trade_report/__init__.py`

양쪽이 신규 추가한 패키지이며 docstring만 다름. T4 package 소유권 유지; PR5 init 이관은 중복.
행 수: PR5 1, T4 1.

### 4. `libs/reporting/trade_report/normalization.py`

동명·다른 책임. PR5는 common의 safe_int/safe_float/report_clip 등 17개 유틸리티 복사. T4는 deps 주입형 normalize_trade_report_output 구현. T4 이름과 구현 보존; PR5 common -> normalization alias는 통합에서 제외하고 T4의 기존 trade_report_common 유지.
행 수: PR5 174, T4 275.

### 5. `libs/reporting/trade_report/operator_text.py`

동명·다른 책임. PR5는 reporter 상태 문구 함수 2개. T4는 operator_parts와 연계한 exit_reason_label/operatorize_report_section 등 11개 함수. T4 유지; PR5 reporter_status_text -> operator_text alias 제외, 기존 reporter_status_text 유지.
행 수: PR5 77, T4 320.

### 6. `libs/reporting/trade_report_ai_compact_input.py`

PR5는 9행 alias -> trade_report/compact_input(이전 355행). T4는 418행 façade, compact_story_input_for_llm 추가 및 ai_facade_parts/compact_input_facts,payload로 소유권 분리. PR5 이관은 중복·구현 퇴행이므로 제외.
행 수: PR5 9, T4 418.

### 7. `libs/reporting/trade_report_markdown_strategy_memory.py`

PR5는 alias -> trade_report_markdown/memory(이전 319행). T4는 731행이며 carryover_context/build_prompt_proven_memory/build_memory_application 추가. 확장 소유권이 이미 T4에 있으므로 PR5 구버전 이관 제외.
행 수: PR5 9, T4 731.

### 8. `libs/reporting/trade_report_markdown_truth.py`

PR5는 alias -> trade_report_markdown/truth(이전 309행). T4는 397행이며 deps 기반 build_truth_surface 및 report_truth_surface 연계 추가. PR5 구버전 이관 제외.
행 수: PR5 9, T4 397.

### 9. `libs/reporting/trade_story_pipeline_evidence_hydration.py`

PR5는 alias -> trade_story/evidence_hydration(이전 82행). T4는 23행 façade, trade_story_evidence_parts/{canonical,scanner,filters}에서 재수출. T4 분리 완료: 중복 이관, PR5 alias/구버전 복사 제외.
행 수: PR5 9, T4 23.

### 10. `libs/reporting/trade_story_pipeline_human_payloads.py`

PR5는 alias -> trade_story/human_payloads(이전 149행). T4는 350행, build_monitor_reason_human 추가 및 trade_story_human_parts 7개 owner에 위임. T4 분리 완료: PR5 이관 제외.
행 수: PR5 9, T4 350.

### 11. `libs/reporting/trade_story_pipeline_story_assembly.py`

PR5는 alias -> trade_story/assembly(이전 186행). T4는 331행 build_trade_story_input와 trade_story_assembly_parts 8개 owner 조합. T4 분리 완료: PR5 이관 제외.
행 수: PR5 9, T4 331.

## 통합 전략과 파일 분류

### A. T4 우선 보존 / 중복 이관 제외

- 위 코드 9경로는 T4를 기준으로 유지. 특히 normalization/operator_text/init은 T4가 이미 소유하는 목적지이므로 PR5 버전으로 덮어쓰지 않는다.
- compact_input, strategy_memory, truth, evidence_hydration, human_payloads, story_assembly 6개는 T4 확장/분리 소유권이 선행한다. PR5의 각 flat alias와 대응 구버전 canonical 복사 파일은 향후 통합에서 제외한다. 이 보고서 작업에서 삭제/복원하지 않는다.
- trade_report_common과 trade_reporter_status_text는 텍스트상 11경로 교집합에 없지만 alias 도착지가 충돌하는 간접 충돌이다. T4 flat 구현을 유지해야 한다.
- normalization/operator_text에 대한 PR5 기존 import identity 기대는 T4 기준으로 그대로 적용할 수 없다. 안전한 9쌍의 identity 테스트와 T4 API 계약 검사를 분리하는 통합 설계가 필요하다.

### B. PR5에서 독립적으로 가져갈 수 있는 변경 후보

아래 9쌍은 PR5 canonical blob == T4 flat blob이며 T4에 목적지 파일이 없다. 전체 커밋 cherry-pick 대신 승인된 통합 작업에서 쌍별 적용할 후보이며, 통합 런타임 PASS를 뜻하지 않는다.

| PR5 canonical | T4 flat/legacy | 구현 blob SHA |
| --- | --- | --- |
| `libs/reporting/trade_report/merge_policy.py` | `libs/reporting/trade_report_ai_merge_policy.py` | `06d613b31775f652a8b82b954a5efc0626554dff` |
| `libs/reporting/trade_report/prompting.py` | `libs/reporting/trade_report_ai_prompting.py` | `a4aaaaaf0ee3c78058980606135af5d2914bd6e1` |
| `libs/reporting/trade_report/shared_facts.py` | `libs/reporting/trade_report_ai_shared_facts.py` | `888a666ad6167f0fb39a3b2a089f786e075cd35a` |
| `libs/reporting/trade_report_markdown/monitor.py` | `libs/reporting/trade_report_markdown_monitor.py` | `4bce9673aba19b53443689f6eda0f94a8bb05ce1` |
| `libs/reporting/trade_report_markdown/scanner.py` | `libs/reporting/trade_report_markdown_scanner.py` | `4a46472d89045202b4cfb91359c7ebb45f4aae91` |
| `libs/reporting/trade_report/summary_adapter.py` | `libs/reporting/trade_report_ai_summary_adapter.py` | `3cc0f147558181621923ff5783887b06c77c3ed8` |
| `libs/reporting/trade_report/compact_helpers.py` | `libs/reporting/trade_report_ai_compact_helpers.py` | `10f710874c9e08715165c7449f1c62bfcebffe7e` |
| `libs/reporting/trade_report/llm.py` | `libs/reporting/trade_report_ai_llm.py` | `ce4a1bf60fc7636d85fc924fac2ef80023b624e6` |
| `libs/reporting/trade_story/evidence.py` | `libs/reporting/trade_story_evidence.py` | `57097d7d7ee3b01265d866134699bf544776044f` |

### C. 통합 검증 필요

- 공용 patch_notes JSON/Markdown 2경로: T4 이력 전부 보존, PR5 항목 append-only로 통합.
- T4 façade deps 주입, 상대 import, 공개/private 재수출, monkeypatch 위치, compact_story_input/build_truth_surface/build_trade_story_input의 추가 export를 보존하는지 확인해야 한다.
- 통합 시에만 T4 관련 계약 테스트와 Reporting/import/patch-note의 표적 회귀 검증을 실행한다. 현재 PR5 단독 테스트 PASS를 T4 통합 PASS로 해석하지 않는다.
- 선행 조건: T4 기준 소유권/목적지 확정 → 9쌍 후보 선별 적용 → 겹치는 구버전 이관 제외 → 테스트 계약 조정 → 표적 검증 → 수동 리뷰. 자동 병합 금지.

## 다음 안전한 이동 후보 (지금은 실행하지 않음)

| 현재 파일 | 제안 목적지 | 근거 |
| --- | --- | --- |
| `libs/reporting/trade_report_post_exit_shadow.py` | `libs/reporting/trade_report/post_exit_shadow.py` | PR5/T4 동일 blob `040c582f99654778312216fe7ffbc1e6ccd3ea9c`; 목적지 양쪽 없음; stdlib만 import; `__file__` 의존 없음 |
| `libs/reporting/trade_report_symbol_metadata.py` | `libs/reporting/trade_report/symbol_metadata.py` | PR5/T4 동일 blob `e44bef233e29fb7b249e3f3412cc2007eec759bc`; 목적지 양쪽 없음; stdlib만 import; `__file__` 의존 없음 |

T4/PR5 목적지 충돌을 먼저 해소하고 최신 T4 SHA를 다시 비교한 뒤 후보 이동 여부를 결정한다. Batch 3은 계속 중단한다.

## 이번 검증

- 11경로 교집합, 전체 blob SHA, diff +/- 및 AST 함수/import 목록 대조.
- 독립 후보 9쌍의 blob 동일성과 T4 목적지 부재 확인. 다음 후보 2개의 동일성/목적지 부재 확인.
- 변경은 이 보고서와 UI 패치노트뿐. 전체 pytest 및 전체 빌드 반복 없음. 패치노트 JSON/append-only/필수 필드 및 표적 패치노트 검증만 수행.

- 実行結果 / Result: patch-note targeted pytest **5 passed**; existing JSON entries preserved byte-semantically and new entry appended; `git diff --check` passed.
