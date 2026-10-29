# RF-009 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 3개. 원본 RF `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-009.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**읽은 실제 파일:** `graphs/nodes/scanner_node.py` blob `ffa8825e83edfa1bc3883a1a1aec2566b0961216`, **1223 LOC**. 파이썬 함수 정의와 들여쓰기를 읽어 분리 후보를 잡았다. 아래 target은 코드 작성 전 현재 Owner·소비자 중복을 1회 확인하여 필요 시 기존 Owner를 재사용한다.

| 원본 함수/줄 | 분리판정 | 목표 소스::함수 | 본문 행수·주의 |
|---|---|---|---|
| `graphs/nodes/scanner_node.py::scanner_node` L749–1223 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/nodes/scanner_node.py::scanner_node` | 475행, BROKER, STATE, CLOCK/ENV |
| `graphs/nodes/scanner_node.py::_maybe_hydrate_scanner_skill_results` L401–444 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/nodes/scanner_node.py::_maybe_hydrate_scanner_skill_results` | 44행, BROKER, STATE |

### scanner_node (L749–1223)
- **기능 경계:** `graphs/nodes/scanner_node.py::scanner_node` (475행), 내부 호출 `_enforce_live_equity_symbols`, `_filter_live_equity_candidates`, `_norm_symbol`, `_to_float`, `_apply_scanner_guidance_weights`, `_maybe_hydrate_scanner_skill_results`, `_extract_skill_quotes`, `_extract_account_open_order_counts`, `_summarize_quote_metric_coverage`, `_should_refresh_scanner_features`. 감지된 경계: BROKER, STATE, CLOCK/ENV.
- **정확한 목표:** `graphs/nodes/scanner_node.py::scanner_node`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _maybe_hydrate_scanner_skill_results (L401–444)
- **기능 경계:** `graphs/nodes/scanner_node.py::_maybe_hydrate_scanner_skill_results` (44행), 내부 호출 `_extract_skill_quotes`, `_extract_account_open_order_counts`, `_should_auto_hydrate_scanner_skills`, `_is_trueish`. 감지된 경계: BROKER, STATE.
- **정확한 목표:** `graphs/nodes/scanner_node.py::_maybe_hydrate_scanner_skill_results`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `graphs/nodes/scan_candidates.py` | `graphs/nodes/scan_candidates.py` | 8397B `b590b50dedc5` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/scanner_node.py` | `graphs/nodes/scanner_node.py` | 64858B `ffa8825e83ed` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `graphs/nodes/select_candidate.py` | `graphs/nodes/select_candidate.py` | 1457B `6d21a3cf854b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-009|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
