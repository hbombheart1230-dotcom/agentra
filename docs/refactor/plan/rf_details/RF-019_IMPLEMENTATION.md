# RF-019 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-019.md` blob `131e0ab3ff29132dee067a69ae1b6678054c16fe`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 29개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/runtime/scanner/candidate_row_projection.py` | 26885 | `d10fc459c72000eb8caa0ea5120b8ecbd25764ea` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/scanner/candidate_row_projection_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/runtime/scanner/candidate_selection.py` | 21416 | `d2e4525cfcd3ad2c895faf5800b880dab143c78b` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/runtime/scanner/candidate_selection_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/runtime/scanner/__init__.py` → `libs/runtime/scanner/__init__.py` | 1 | `8b137891791f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/blocker_family_overlay.py` → `libs/runtime/scanner/blocker_family_overlay.py` | 490 | `2c7584214053` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/candidate_context_projection.py` → `libs/runtime/scanner/candidate_context_projection.py` | 512 | `2b8310374b3e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/candidate_risk.py` → `libs/runtime/scanner/candidate_risk.py` | 514 | `97bed59dbe02` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/candidate_row_projection.py` → `libs/runtime/scanner/candidate_row_projection.py` | 26885 | `d10fc459c720` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/candidate_selection.py` → `libs/runtime/scanner/candidate_selection.py` | 21416 | `d2e4525cfcd3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/compatibility.py` → `libs/runtime/scanner/compatibility.py` | 472 | `22c523abd247` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/control_eligibility.py` → `libs/runtime/scanner/control_eligibility.py` | 494 | `9f734f09cf46` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/evidence.py` → `libs/runtime/scanner/evidence.py` | 12106 | `fe1a48aa4563` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/feature_coverage.py` → `libs/runtime/scanner/feature_coverage.py` | 480 | `047760874541` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/guidance.py` → `libs/runtime/scanner/guidance.py` | 462 | `0b709dc3d225` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/macro_chart_fit.py` → `libs/runtime/scanner/macro_chart_fit.py` | 478 | `8ab5ab11b8d8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/macro_focus.py` → `libs/runtime/scanner/macro_focus.py` | 470 | `f76e495459c5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/market_representative_guard.py` → `libs/runtime/scanner/market_representative_guard.py` | 12350 | `a4338360c19d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/output_payloads.py` → `libs/runtime/scanner/output_payloads.py` | 486 | `54fea44f4237` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/output_snapshots.py` → `libs/runtime/scanner/output_snapshots.py` | 488 | `4d88ab0569b1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/practical_filters.py` → `libs/runtime/scanner/practical_filters.py` | 10006 | `661959dbd029` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/ranking_policy_overlay.py` → `libs/runtime/scanner/ranking_policy_overlay.py` | 9718 | `04626f975012` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/repeat_guard.py` → `libs/runtime/scanner/repeat_guard.py` | 470 | `5c1000d90d44` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/scanner_event_payloads.py` → `libs/runtime/scanner/scanner_event_payloads.py` | 15227 | `fdce844762c2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/score_feature_projection.py` → `libs/runtime/scanner/score_feature_projection.py` | 13809 | `4e501786611d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/score_policy_projection.py` → `libs/runtime/scanner/score_policy_projection.py` | 8860 | `8784d750856c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/scoring_inputs.py` → `libs/runtime/scanner/scoring_inputs.py` | 476 | `f5bfcba9553e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/selection_evidence_projection.py` → `libs/runtime/scanner/selection_evidence_projection.py` | 514 | `1f70854eb855` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/selection_evidence_projection_value_te_scanner.py` → `libs/runtime/scanner/selection_evidence_projection_value_te_scanner.py` | 11688 | `8c3f2b0506f6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/selection_output_projection.py` → `libs/runtime/scanner/selection_output_projection.py` | 14611 | `9733495639cc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/sentiment_inputs.py` → `libs/runtime/scanner/sentiment_inputs.py` | 480 | `d418b40364f8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/symbol_prior.py` → `libs/runtime/scanner/symbol_prior.py` | 470 | `9c26484ffaea` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/runtime/scanner/theme_filter.py` → `libs/runtime/scanner/theme_filter.py` | 9760 | `800be79309a4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
