# RF-014 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Claude A 구현, Codex B 읽기 전용 독립 검증. 파일 20개. 원본 RF `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**읽은 실제 파일:** `libs/agents/scanner/projections/selection_evidence_projection.py` blob `bf20e9af5ec4988e7fef831b0cbb3e44644f6914`, **252 LOC**. 파이썬 함수 정의와 들여쓰기를 읽어 분리 후보를 잡았다. 아래 target은 코드 작성 전 현재 Owner·소비자 중복을 1회 확인하여 필요 시 기존 Owner를 재사용한다.

| 원본 함수/줄 | 분리판정 | 목표 소스::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/agents/scanner/projections/selection_evidence_projection.py::scan_select_commander_memory_application_trace_selec` L205–230 | **MOVE_BODY** | `libs/agents/scanner/projections/selection_evidence_projection_scan_select_commander_memory_applicati.py::scan_select_commander_memory_application_trace_selec` | 26행, 부작용 정적 탐지 없음 |
| `libs/agents/scanner/projections/selection_evidence_projection.py::scan_select_reasons_row_conf` L231–252 | **MOVE_BODY** | `libs/agents/scanner/projections/selection_evidence_projection_scan_select_reasons_row_conf.py::scan_select_reasons_row_conf` | 22행, 부작용 정적 탐지 없음 |

### scan_select_commander_memory_application_trace_selec (L205–230)
- **기능 경계:** `libs/agents/scanner/projections/selection_evidence_projection.py::scan_select_commander_memory_application_trace_selec` (26행), 내부 호출 `_to_float`. 감지된 경계: 없음.
- **정확한 목표:** `libs/agents/scanner/projections/selection_evidence_projection_scan_select_commander_memory_applicati.py::scan_select_commander_memory_application_trace_selec`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### scan_select_reasons_row_conf (L231–252)
- **기능 경계:** `libs/agents/scanner/projections/selection_evidence_projection.py::scan_select_reasons_row_conf` (22행), 내부 호출 `_to_float`. 감지된 경계: 없음.
- **정확한 목표:** `libs/agents/scanner/projections/selection_evidence_projection_scan_select_reasons_row_conf.py::scan_select_reasons_row_conf`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `libs/agents/scanner/__init__.py` | `libs/agents/scanner/__init__.py` | 43B `d0176c7a20e6` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/candidate_risk.py` | `libs/agents/scanner/candidate_risk.py` | 3803B `8dea30aebd81` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/context/__init__.py` | `libs/agents/scanner/context/__init__.py` | 119B `bfd3a052024c` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/context/feature_coverage.py` | `libs/agents/scanner/context/feature_coverage.py` | 3108B `32ad1370df7e` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/context/macro_chart_fit.py` | `libs/agents/scanner/context/macro_chart_fit.py` | 7853B `7a5828c8b93b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/context/macro_focus.py` | `libs/agents/scanner/context/macro_focus.py` | 2641B `24170e434adb` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/context/scoring_inputs.py` | `libs/agents/scanner/context/scoring_inputs.py` | 7390B `b436430ea437` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/context/sentiment_inputs.py` | `libs/agents/scanner/context/sentiment_inputs.py` | 4821B `f514156e8eac` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/policy/__init__.py` | `libs/agents/scanner/policy/__init__.py` | 98B `ef4a8b56c14f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/policy/blocker_family_overlay.py` | `libs/agents/scanner/policy/blocker_family_overlay.py` | 4444B `81d59515d0ba` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/policy/compatibility.py` | `libs/agents/scanner/policy/compatibility.py` | 13412B `323d5a54f5e2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/policy/guidance.py` | `libs/agents/scanner/policy/guidance.py` | 13223B `3318a80a01b8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/policy/repeat_guard.py` | `libs/agents/scanner/policy/repeat_guard.py` | 10402B `5f794e544dd0` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/policy/symbol_prior.py` | `libs/agents/scanner/policy/symbol_prior.py` | 4660B `9bbc39ae6c00` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/projections/__init__.py` | `libs/agents/scanner/projections/__init__.py` | 95B `cd9db42ceffa` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/projections/candidate_context_projection.py` | `libs/agents/scanner/projections/candidate_context_projection.py` | 4373B `15fd6fc26a51` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/projections/control_eligibility.py` | `libs/agents/scanner/projections/control_eligibility.py` | 2357B `d47013045a37` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/projections/output_payloads.py` | `libs/agents/scanner/projections/output_payloads.py` | 13822B `fe5e34d58aec` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/projections/output_snapshots.py` | `libs/agents/scanner/projections/output_snapshots.py` | 13408B `02ef48a40833` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `libs/agents/scanner/projections/selection_evidence_projection.py` | `libs/agents/scanner/projections/selection_evidence_projection.py` | 19820B `bf20e9af5ec4` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |

## 3. 개발자 독점 순서와 최소 검증

1. Claude A만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 A 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-014|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
