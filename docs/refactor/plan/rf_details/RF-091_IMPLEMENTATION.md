# RF-091 — 코드 구조/함수 재배치 설계 (T04)

## T04 exact targets
Preserve pinned data/specs JSONL, default rules, eval manifest and dataset paths. Historical originals and archived state remain restricted. No file content read, move or deletion. Correct stable path and source authority is KEEP_OK; no Python functions to split.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-091.md` blob `d6fa61fb4e33c986a2ddff43ea6c60e5d8113a96`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 25개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `data/eval/m26_fixed_dataset_v1/execution/fills.jsonl` → `data/eval/m26_fixed_dataset_v1/execution/fills.jsonl` | 102 | `c1dd4b5d3f0d` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/execution/intents.jsonl` → `data/eval/m26_fixed_dataset_v1/execution/intents.jsonl` | 113 | `f416307c28e1` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/execution/order_status.jsonl` → `data/eval/m26_fixed_dataset_v1/execution/order_status.jsonl` | 86 | `6a66bd1454c9` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/features/scanner_monitor_features.jsonl` → `data/eval/m26_fixed_dataset_v1/features/scanner_monitor_features.jsonl` | 103 | `9baf7123ed1b` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/manifest.json` → `data/eval/m26_fixed_dataset_v1/manifest.json` | 707 | `814b9a0b5b23` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/market/corporate_actions.csv` → `data/eval/m26_fixed_dataset_v1/market/corporate_actions.csv` | 63 | `66e99a553ed8` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/market/ohlcv_1d.csv` → `data/eval/m26_fixed_dataset_v1/market/ohlcv_1d.csv` | 101 | `2e08e4e711ec` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/market/ohlcv_1m.csv` → `data/eval/m26_fixed_dataset_v1/market/ohlcv_1m.csv` | 101 | `2e08e4e711ec` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/market/ohlcv_5m.csv` → `data/eval/m26_fixed_dataset_v1/market/ohlcv_5m.csv` | 101 | `2e08e4e711ec` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/microstructure/top_of_book.jsonl` → `data/eval/m26_fixed_dataset_v1/microstructure/top_of_book.jsonl` | 84 | `e9345595d596` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/news/headlines.jsonl` → `data/eval/m26_fixed_dataset_v1/news/headlines.jsonl` | 82 | `f39cd0d52985` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/news/sentiment_by_symbol.jsonl` → `data/eval/m26_fixed_dataset_v1/news/sentiment_by_symbol.jsonl` | 75 | `f23770b17c00` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/eval/m26_fixed_dataset_v1/news/sentiment_daily.jsonl` → `data/eval/m26_fixed_dataset_v1/news/sentiment_daily.jsonl` | 62 | `896402425769` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/m15_demo_events.jsonl` → `data/m15_demo_events.jsonl` | 1839 | `89bc6d6ad1c7` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/m15_demo_intents.jsonl` → `data/m15_demo_intents.jsonl` | 897 | `cab1b0179db7` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/originals/- 복사본.env` → `data/originals/- 복사본.env` | 1177 | `2fa060457bc8` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/originals/키움 REST API 문서.xlsx` → `data/originals/키움 REST API 문서.xlsx` | 707635 | `4872fbdaad98` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/specs/api_catalog.jsonl` → `data/specs/api_catalog.jsonl` | 313018 | `49e956168690` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/specs/default_rules.json` → `data/specs/default_rules.json` | 635 | `fc75d5e86df0` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/specs/kiwoom_api_list_tagged.jsonl` → `data/specs/kiwoom_api_list_tagged.jsonl` | 38997 | `89559a4555c4` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/specs/kiwoom_apis.jsonl` → `data/specs/kiwoom_apis.jsonl` | 1101988 | `289fe322007f` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/state.json.bak_20260317_1023` → `data/state.json.bak_20260317_1023` | 3162 | `f3694660d309` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/state.json.bak_reset_20260317_103653` → `data/state.json.bak_reset_20260317_103653` | 3289 | `22b020988de6` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/state.pre_force_sell_20260331_134241.json` → `data/state.pre_force_sell_20260331_134241.json` | 62628 | `57e7b1cc1317` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `data/state.pre_restart_20260331_1.json` → `data/state.pre_restart_20260331_1.json` | 54729 | `b6bdcf0f0b4b` | KEEP_IF: 리소스·데이터 소비자 경로 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
