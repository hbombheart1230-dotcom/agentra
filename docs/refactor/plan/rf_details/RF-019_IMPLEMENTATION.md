# RF-019 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-019.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 29개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/scanner/candidate_row_projection.py` blob `d10fc459c72000eb8caa0ea5120b8ecbd25764ea` (320 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/scanner/candidate_row_projection.py::score_scanner_candidate_row` L11-320 | MOVE_BODY | `libs/runtime/scanner/candidate_row_projection_score_scanner_candidate_row.py::score_scanner_candidate_row` | 310행 · 순수 후보 |

### score_scanner_candidate_row — 원본 310행
- **확인된 책임:** `libs/runtime/scanner/candidate_row_projection.py` L11–320; 직접 호출 helper `_stable_unit_hash`, `_to_float`, `_norm_symbol`, `_compute_entry_compatibility_signal`, `_clamp`. 감지된 효과: 없음.
- **목표:** `libs/runtime/scanner/candidate_row_projection_score_scanner_candidate_row.py::score_scanner_candidate_row` (Owner Claude A, RF-019). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/scanner/__init__.py` | `libs/runtime/scanner/__init__.py` | `8b137891791f` / 1B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/blocker_family_overlay.py` | `libs/runtime/scanner/blocker_family_overlay.py` | `2c7584214053` / 490B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/candidate_context_projection.py` | `libs/runtime/scanner/candidate_context_projection.py` | `2b8310374b3e` / 512B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/candidate_risk.py` | `libs/runtime/scanner/candidate_risk.py` | `97bed59dbe02` / 514B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/candidate_row_projection.py` | `libs/runtime/scanner/candidate_row_projection.py` | `d10fc459c720` / 26885B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/scanner/candidate_selection.py` | `libs/runtime/scanner/candidate_selection.py` | `d2e4525cfcd3` / 21416B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/runtime/scanner/compatibility.py` | `libs/runtime/scanner/compatibility.py` | `22c523abd247` / 472B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/control_eligibility.py` | `libs/runtime/scanner/control_eligibility.py` | `9f734f09cf46` / 494B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/evidence.py` | `libs/runtime/scanner/evidence.py` | `fe1a48aa4563` / 12106B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/feature_coverage.py` | `libs/runtime/scanner/feature_coverage.py` | `047760874541` / 480B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/guidance.py` | `libs/runtime/scanner/guidance.py` | `0b709dc3d225` / 462B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/macro_chart_fit.py` | `libs/runtime/scanner/macro_chart_fit.py` | `8ab5ab11b8d8` / 478B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/macro_focus.py` | `libs/runtime/scanner/macro_focus.py` | `f76e495459c5` / 470B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/market_representative_guard.py` | `libs/runtime/scanner/market_representative_guard.py` | `a4338360c19d` / 12350B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/output_payloads.py` | `libs/runtime/scanner/output_payloads.py` | `54fea44f4237` / 486B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/output_snapshots.py` | `libs/runtime/scanner/output_snapshots.py` | `4d88ab0569b1` / 488B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/practical_filters.py` | `libs/runtime/scanner/practical_filters.py` | `661959dbd029` / 10006B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/ranking_policy_overlay.py` | `libs/runtime/scanner/ranking_policy_overlay.py` | `04626f975012` / 9718B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/repeat_guard.py` | `libs/runtime/scanner/repeat_guard.py` | `5c1000d90d44` / 470B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/scanner_event_payloads.py` | `libs/runtime/scanner/scanner_event_payloads.py` | `fdce844762c2` / 15227B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/score_feature_projection.py` | `libs/runtime/scanner/score_feature_projection.py` | `4e501786611d` / 13809B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/score_policy_projection.py` | `libs/runtime/scanner/score_policy_projection.py` | `8784d750856c` / 8860B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/scoring_inputs.py` | `libs/runtime/scanner/scoring_inputs.py` | `f5bfcba9553e` / 476B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/selection_evidence_projection.py` | `libs/runtime/scanner/selection_evidence_projection.py` | `1f70854eb855` / 514B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/selection_evidence_projection_value_te_scanner.py` | `libs/runtime/scanner/selection_evidence_projection_value_te_scanner.py` | `8c3f2b0506f6` / 11688B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/selection_output_projection.py` | `libs/runtime/scanner/selection_output_projection.py` | `9733495639cc` / 14611B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/sentiment_inputs.py` | `libs/runtime/scanner/sentiment_inputs.py` | `d418b40364f8` / 480B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/symbol_prior.py` | `libs/runtime/scanner/symbol_prior.py` | `9c26484ffaea` / 470B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/scanner/theme_filter.py` | `libs/runtime/scanner/theme_filter.py` | `800be79309a4` / 9760B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-019|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
