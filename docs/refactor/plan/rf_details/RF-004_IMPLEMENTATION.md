# RF-004 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 35개. 원본 RF `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-004.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**읽은 실제 파일:** `apps/api/domain/runtime_status_projection.py` blob `8a685f25e4088e64284c50c3ff888c323f88d20f`, **287 LOC**. 파이썬 함수 정의와 들여쓰기를 읽어 분리 후보를 잡았다. 아래 target은 코드 작성 전 현재 Owner·소비자 중복을 1회 확인하여 필요 시 기존 Owner를 재사용한다.

| 원본 함수/줄 | 분리판정 | 목표 소스::함수 | 본문 행수·주의 |
|---|---|---|---|
| `apps/api/domain/runtime_status_projection.py::_supervisor_status` L152–177 | **MOVE_BODY** | `apps/api/domain/runtime_status_projection_supervisor_status.py::_supervisor_status` | 26행, 부작용 정적 탐지 없음 |
| `apps/api/domain/runtime_status_projection.py::_market_status` L208–232 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `apps/api/domain/runtime_status_projection.py::_market_status` | 25행, BROKER |

### _supervisor_status (L152–177)
- **기능 경계:** `apps/api/domain/runtime_status_projection.py::_supervisor_status` (26행), 내부 호출 `_mapping`, `_non_negative_int`, `_parse_datetime`. 감지된 경계: 없음.
- **정확한 목표:** `apps/api/domain/runtime_status_projection_supervisor_status.py::_supervisor_status`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _market_status (L208–232)
- **기능 경계:** `apps/api/domain/runtime_status_projection.py::_market_status` (25행), 내부 호출 `_mapping`, `_parse_datetime`. 감지된 경계: BROKER.
- **정확한 목표:** `apps/api/domain/runtime_status_projection.py::_market_status`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `apps/api/domain/__init__.py` | `apps/api/domain/__init__.py` | 62B `b2710a7510da` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/__init__.py` | `apps/api/domain/anomalies/__init__.py` | 510B `c0ac41296223` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/factory.py` | `apps/api/domain/anomalies/factory.py` | 1036B `ce07557a24d1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/freshness_rules.py` | `apps/api/domain/anomalies/freshness_rules.py` | 2398B `56a5bf1d41fe` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/integrity_rules.py` | `apps/api/domain/anomalies/integrity_rules.py` | 1055B `6c75969aba9b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/opportunity_rules.py` | `apps/api/domain/anomalies/opportunity_rules.py` | 2232B `3e3be09910e9` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/policy.py` | `apps/api/domain/anomalies/policy.py` | 485B `2597303bf7ad` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/trade_cost_rule.py` | `apps/api/domain/anomalies/trade_cost_rule.py` | 1668B `c228533ff4b2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/trade_exit_rule.py` | `apps/api/domain/anomalies/trade_exit_rule.py` | 1700B `057a3af369c1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/trade_rules.py` | `apps/api/domain/anomalies/trade_rules.py` | 699B `eecfeed9bea4` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomalies/trade_sequence_rule.py` | `apps/api/domain/anomalies/trade_sequence_rule.py` | 1932B `34bce956ddf0` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/anomaly_rules.py` | `apps/api/domain/anomaly_rules.py` | 487B `8c71098c4cf5` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/llm_operations_projection.py` | `apps/api/domain/llm_operations_projection.py` | 6273B `a4ee2720750a` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/llm_role_catalog.py` | `apps/api/domain/llm_role_catalog.py` | 1491B `9429746c0397` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/performance_math.py` | `apps/api/domain/performance_math.py` | 2420B `0541d5652139` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/runtime_status_projection.py` | `apps/api/domain/runtime_status_projection.py` | 10278B `8a685f25e408` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `apps/api/domain/scheduled_intelligence_projection.py` | `apps/api/domain/scheduled_intelligence_projection.py` | 6048B `a9ac9b151f9d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/domain/watchdog_history_projection.py` | `apps/api/domain/watchdog_history_projection.py` | 3882B `467c5052c159` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/__init__.py` | `apps/api/models/__init__.py` | 991B `6a4303fb770c` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/anomalies.py` | `apps/api/models/anomalies.py` | 1762B `fc4f8c7c6ee8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/common.py` | `apps/api/models/common.py` | 1078B `ee7cf13bf2fd` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/health.py` | `apps/api/models/health.py` | 646B `ca070dfcfb6c` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/llm_operations.py` | `apps/api/models/llm_operations.py` | 2837B `f423b30f7bd0` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/market.py` | `apps/api/models/market.py` | 1710B `40b6ac25b821` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/operations.py` | `apps/api/models/operations.py` | 1325B `009237a56572` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/opportunities.py` | `apps/api/models/opportunities.py` | 3028B `092ca066739e` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/overview.py` | `apps/api/models/overview.py` | 545B `1b77ee4cded8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/patch_notes.py` | `apps/api/models/patch_notes.py` | 1148B `c16aca2fe040` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/performance.py` | `apps/api/models/performance.py` | 1782B `516c31df33c0` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/portfolio.py` | `apps/api/models/portfolio.py` | 1021B `14157c104a0a` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/profile.py` | `apps/api/models/profile.py` | 484B `fc9ed38da990` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/reports.py` | `apps/api/models/reports.py` | 962B `73ffdcb46ace` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/runtime_status.py` | `apps/api/models/runtime_status.py` | 4645B `e630d0fda79b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/strategies.py` | `apps/api/models/strategies.py` | 1301B `6dc7c6bdb61e` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/models/trades.py` | `apps/api/models/trades.py` | 2914B `5337e0a3ddfc` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-004|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
