# RF-055 — 코드 구조/함수 재배치 설계 (T00/V3)

## SOURCE 본문 검토 확정 — RF-055 (2026-10-29)

**대표 source:** `libs/read/kiwoom_theme_reader.py` 580 LOC. 테마 API의 HTTP client와 pure normalization이 같은 파일에 혼재한다. 담당 **Codex B 단독**, Claude A는 읽기 검증. 원본 소스 원격 HEAD blob 재확인 후 진행.

| SOURCE::확인된 함수 | 원본 구간 | TARGET::확정 함수 | 코드 처리 |
|---|---|---|---|
| `libs/read/kiwoom_theme_reader.py::normalize_theme_group` | L136–176 (41 LOC) | `libs/read/kiwoom_theme_normalization.py::normalize_theme_group` | MOVE BODY |
| `libs/read/kiwoom_theme_reader.py::normalize_theme_component` | L177–195 (19 LOC) | 같은 `kiwoom_theme_normalization.py::normalize_theme_component` | MOVE BODY, 같은 책임 묶기 |
| `libs/read/kiwoom_theme_reader.py::_symbols_from_any` | L98–122 (25 LOC) | 같은 `kiwoom_theme_normalization.py::_symbols_from_any` | 그룹/구성종목 정규화 의존성 함께 MOVE |
| `libs/read/kiwoom_theme_reader.py::_split_text_items` | L77–97 (21 LOC) | 같은 `kiwoom_theme_normalization.py::_split_text_items` | 문자열 파싱 의존성 함께 MOVE |
| `libs/read/kiwoom_theme_reader.py::_live_fetch_enabled` | L274–303 (30 LOC) | **원위치 KEEP** | `PYTEST_ALLOW_LIVE_KIWOOM_FETCH`·환경 차단 경계 |
| `KiwoomThemeReader._post` | L368–388 | **원위치 KEEP** | 실 HTTP 요청 및 헤더/재시도 경계 |

**정확한 이동 방법:** 동일 책임 4개 함수를 **한 개 normalization Owner**로 이동한다. `_norm_symbol/_first/_to_int/_round4/_to_float/_clean_text` 등 사용시점 호출 globals를 facade 또는 명시 의존성으로 제공하여 기존 monkeypatch 가능성 보존. `normalize_theme_group`와 `normalize_theme_component` 공개 명칭은 기존 위치에서 얇은 wrapper 보존. HTTP 요청·환경 live guard는 건드리지 않는다. raw dict/None/중복 종목·순서/주가 자리수의 고정 원본 결과 비교, 정상 offline targeted test 1회. 그 외 `libs/read/` 하위 파일은 단일 책임이 맞으면 KEEP_OK.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-055.md` blob `85213b9f511336df8aacdd5bbf8b2a567a42ffc8`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 17개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/read/kiwoom_theme_reader.py` | 22020 | `ac88bc3a802b7a5133dffa63c86335e028c0dae4` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/read/kiwoom_theme_reader_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/read/__init__.py` → `libs/read/__init__.py` | 0 | `e69de29bb2d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_account_snapshot_collector.py` → `libs/read/kiwoom_account_snapshot_collector.py` | 11285 | `c50e2c507cda` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_broker_truth_common.py` → `libs/read/kiwoom_broker_truth_common.py` | 2845 | `030cfbfc6db1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_condition_reader.py` → `libs/read/kiwoom_condition_reader.py` | 3575 | `98c77c4354bb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_day_pnl_reader.py` → `libs/read/kiwoom_day_pnl_reader.py` | 8109 | `7a2922cd299d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_market_index_reader.py` → `libs/read/kiwoom_market_index_reader.py` | 9713 | `ec4cf187c06d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_order_fill_reader.py` → `libs/read/kiwoom_order_fill_reader.py` | 13288 | `d85f2fdcb68d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_orderable_cash_reader.py` → `libs/read/kiwoom_orderable_cash_reader.py` | 2957 | `567cb78ba454` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_portfolio_reader.py` → `libs/read/kiwoom_portfolio_reader.py` | 6552 | `bcff82faadc6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_price_reader.py` → `libs/read/kiwoom_price_reader.py` | 4011 | `bac5692a2a40` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_program_trading_reader.py` → `libs/read/kiwoom_program_trading_reader.py` | 6091 | `ee4adeea5ba3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_rank_reader.py` → `libs/read/kiwoom_rank_reader.py` | 5623 | `ce4d182335a4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/kiwoom_theme_reader.py` → `libs/read/kiwoom_theme_reader.py` | 22020 | `ac88bc3a802b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/krx_night_futures_reader.py` → `libs/read/krx_night_futures_reader.py` | 7982 | `950775f5d303` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/portfolio_reader.py` → `libs/read/portfolio_reader.py` | 1424 | `a3a841223628` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/price_reader.py` → `libs/read/price_reader.py` | 713 | `82fcbe1ce387` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/read/snapshot_models.py` → `libs/read/snapshot_models.py` | 981 | `3fa97cd4c13d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
