# RF-005 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 40개. 원본 RF `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-005.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**실제 함수 분석 대상 없음:** Python 원본이 없거나 원격 본문 조회가 안 됨. 추측 함수명을 새 코드로 구현하지 않는다. 모든 소유 파일의 위치/책임·공개 소비자가 적절하면 KEEP_OK. 구조 부채 확인 시 실제 Git blob 함수명을 지정하고 그 함수만 분리.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `apps/api/__init__.py` | `apps/api/__init__.py` | 123B `222a8eceaa9b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/__init__.py` | `apps/api/adapters/__init__.py` | 81B `c20632b6a35f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/llm_artifacts.py` | `apps/api/adapters/llm_artifacts.py` | 4303B `62a7fed5e46d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/llm_event_tail.py` | `apps/api/adapters/llm_event_tail.py` | 3123B `4ef7d1c40dee` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/market_snapshot.py` | `apps/api/adapters/market_snapshot.py` | 623B `82945743b8eb` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/operator_summary.py` | `apps/api/adapters/operator_summary.py` | 1861B `aaec22e97d7a` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/opportunity_artifacts.py` | `apps/api/adapters/opportunity_artifacts.py` | 1947B `fccbfc4bffa6` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/patch_notes.py` | `apps/api/adapters/patch_notes.py` | 925B `28c95f4e40a8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/performance_summary.py` | `apps/api/adapters/performance_summary.py` | 2152B `ebb10eefa05d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/runtime_status_artifacts.py` | `apps/api/adapters/runtime_status_artifacts.py` | 4450B `34a97896a2b1` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `apps/api/adapters/safe_reports.py` | `apps/api/adapters/safe_reports.py` | 2778B `682ab0126905` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/source_freshness.py` | `apps/api/adapters/source_freshness.py` | 802B `fbb7b59f652b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/adapters/trade_bundle.py` | `apps/api/adapters/trade_bundle.py` | 2485B `0a673c31eb18` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/config.py` | `apps/api/config.py` | 3290B `3f61a1ba0a31` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/__init__.py` | `apps/api/infrastructure/__init__.py` | 651B `03870250d3dd` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/bounded_reader.py` | `apps/api/infrastructure/bounded_reader.py` | 961B `213235d7a29e` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/dates.py` | `apps/api/infrastructure/dates.py` | 818B `466873879a10` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/jsonl_tail.py` | `apps/api/infrastructure/jsonl_tail.py` | 1243B `0ecba6343d20` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/paths.py` | `apps/api/infrastructure/paths.py` | 973B `6e6718dcf7c0` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/public_middleware.py` | `apps/api/infrastructure/public_middleware.py` | 1455B `5c1661775fd2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/public_sanitization.py` | `apps/api/infrastructure/public_sanitization.py` | 1342B `5f87608f2ef1` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/source_roots.py` | `apps/api/infrastructure/source_roots.py` | 735B `824211ae42a8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/infrastructure/trade_index.py` | `apps/api/infrastructure/trade_index.py` | 3102B `579667f81ab5` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/main.py` | `apps/api/main.py` | 1991B `19650cb9f2cf` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/requirements.txt` | `apps/api/requirements.txt` | 49B `efd6330dbb44` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/api/routers/__init__.py` | `apps/api/routers/__init__.py` | 42B `fd597acf13cf` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/anomalies.py` | `apps/api/routers/anomalies.py` | 552B `c7e1bd9f65f5` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/health.py` | `apps/api/routers/health.py` | 572B `1f8cd64a17d2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/llm_operations.py` | `apps/api/routers/llm_operations.py` | 593B `888758d91656` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/market.py` | `apps/api/routers/market.py` | 1242B `81878cac5e07` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/operations.py` | `apps/api/routers/operations.py` | 470B `18a4ef7a9709` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/opportunities.py` | `apps/api/routers/opportunities.py` | 1333B `2d96c990e894` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/overview.py` | `apps/api/routers/overview.py` | 709B `0b0360caa576` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/patch_notes.py` | `apps/api/routers/patch_notes.py` | 421B `8255a782e583` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/performance.py` | `apps/api/routers/performance.py` | 1416B `0d994af2599b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/portfolio.py` | `apps/api/routers/portfolio.py` | 687B `3a16e4315a39` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/profile.py` | `apps/api/routers/profile.py` | 425B `2e0ad0133be4` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/runtime_status.py` | `apps/api/routers/runtime_status.py` | 2010B `edd135e7c17d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/strategies.py` | `apps/api/routers/strategies.py` | 869B `6accc2774950` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/api/routers/trades.py` | `apps/api/routers/trades.py` | 2487B `f0fd4879c24e` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-005|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
