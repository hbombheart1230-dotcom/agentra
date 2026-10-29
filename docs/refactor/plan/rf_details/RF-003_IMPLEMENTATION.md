# RF-003 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 25개. 원본 RF `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-003.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**읽은 실제 파일:** `apps/api/services/performance.py` blob `01589521f7d8990f0357d141f594953fb9873e63`, **255 LOC**. 파이썬 함수 정의와 들여쓰기를 읽어 분리 후보를 잡았다. 아래 target은 코드 작성 전 현재 Owner·소비자 중복을 1회 확인하여 필요 시 기존 Owner를 재사용한다.

| 원본 함수/줄 | 분리판정 | 목표 소스::함수 | 본문 행수·주의 |
|---|---|---|---|
| `apps/api/services/performance.py::_points` L193–213 | **MOVE_BODY** | `apps/api/services/performance_points.py::_points` | 21행, 부작용 정적 탐지 없음 |

### _points (L193–213)
- **기능 경계:** `apps/api/services/performance.py::_points` (21행), 내부 호출 `_point`. 감지된 경계: 없음.
- **정확한 목표:** `apps/api/services/performance_points.py::_points`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `apps/api/services/__init__.py` | `apps/api/services/__init__.py` | 59B `74c0a48acdc7` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/anomalies.py` | `apps/api/services/anomalies.py` | 3043B `e62a7d00a0a1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/health.py` | `apps/api/services/health.py` | 1333B `3e724a8046d1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/llm_operations.py` | `apps/api/services/llm_operations.py` | 3066B `ec5a6cba470f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/market.py` | `apps/api/services/market.py` | 5903B `0f417d35cc4d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/metric_factory.py` | `apps/api/services/metric_factory.py` | 822B `0a62174d0764` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/operations.py` | `apps/api/services/operations.py` | 9191B `01f0f270ec83` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/opportunities.py` | `apps/api/services/opportunities.py` | 4631B `6168db524c20` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/opportunity_projection.py` | `apps/api/services/opportunity_projection.py` | 4998B `0dce193a4204` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/overview.py` | `apps/api/services/overview.py` | 1610B `57f83b2258fc` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/patch_notes.py` | `apps/api/services/patch_notes.py` | 1812B `0a13a9e6eeaa` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/performance.py` | `apps/api/services/performance.py` | 11164B `01589521f7d8` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `apps/api/services/portfolio.py` | `apps/api/services/portfolio.py` | 6488B `cefe54813de2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/profile.py` | `apps/api/services/profile.py` | 750B `c3f214f19070` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/reports.py` | `apps/api/services/reports.py` | 4123B `6a8d666d7d5c` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/runtime_status.py` | `apps/api/services/runtime_status.py` | 1523B `874a4ae448e9` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/scheduled_artifacts.py` | `apps/api/services/scheduled_artifacts.py` | 2156B `40f498770413` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/strategy_performance.py` | `apps/api/services/strategy_performance.py` | 4006B `cd39142d1c6d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/trade_fallback_projection.py` | `apps/api/services/trade_fallback_projection.py` | 1624B `95734ce79a32` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/trade_fallbacks.py` | `apps/api/services/trade_fallbacks.py` | 3328B `f68a95adf0fa` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/trade_integrity_projection.py` | `apps/api/services/trade_integrity_projection.py` | 1664B `2cac10a85ddf` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/trade_summary_projection.py` | `apps/api/services/trade_summary_projection.py` | 3727B `f323f16324e2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/trade_timeline_projection.py` | `apps/api/services/trade_timeline_projection.py` | 3284B `5b6b2831b030` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/trade_values.py` | `apps/api/services/trade_values.py` | 1598B `d237b7ca32e9` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/services/trades.py` | `apps/api/services/trades.py` | 4176B `f48e1c211fd2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-003|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
