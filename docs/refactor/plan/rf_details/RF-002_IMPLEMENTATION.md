# RF-002 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 9개. 원본 RF `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-002.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**읽은 실제 파일:** `apps/operator_ui/main.py` blob `87483c5b25bdb84360d67e1759435652528201a1`, **125 LOC**. 파이썬 함수 정의와 들여쓰기를 읽어 분리 후보를 잡았다. 아래 target은 코드 작성 전 현재 Owner·소비자 중복을 1회 확인하여 필요 시 기존 Owner를 재사용한다.

| 원본 함수/줄 | 분리판정 | 목표 소스::함수 | 본문 행수·주의 |
|---|---|---|---|
| `apps/operator_ui/main.py::create_app` L22–123 | **MOVE_BODY** | `apps/operator_ui/main_create_app.py::create_app` | 102행, 부작용 정적 탐지 없음 |

### create_app (L22–123)
- **기능 경계:** `apps/operator_ui/main.py::create_app` (102행), 내부 호출 탐지 없음. 감지된 경계: 없음.
- **정확한 목표:** `apps/operator_ui/main_create_app.py::create_app`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `apps/operator_ui/__init__.py` | `apps/operator_ui/__init__.py` | 186B `9cb3ebe54d44` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `apps/operator_ui/main.py` | `apps/operator_ui/main.py` | 4375B `87483c5b25bd` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `apps/operator_ui/static/operator.css` | `apps/operator_ui/static/operator.css` | 11388B `4a2a59e0571e` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/operator_ui/templates/base.html` | `apps/operator_ui/templates/base.html` | 880B `0cc9fb138da8` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/operator_ui/templates/operator_brief_detail.html` | `apps/operator_ui/templates/operator_brief_detail.html` | 7511B `e003ec4a2ae9` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/operator_ui/templates/overview.html` | `apps/operator_ui/templates/overview.html` | 18872B `d9027b2ed2bc` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/operator_ui/templates/run_detail.html` | `apps/operator_ui/templates/run_detail.html` | 17628B `0a7a86fb9779` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/operator_ui/templates/runs.html` | `apps/operator_ui/templates/runs.html` | 5192B `a5e34bf36160` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/operator_ui/templates/trade_report_detail.html` | `apps/operator_ui/templates/trade_report_detail.html` | 8519B `5624c136dfbc` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-002|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
