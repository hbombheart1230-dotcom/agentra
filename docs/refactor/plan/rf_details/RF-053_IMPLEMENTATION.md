# RF-053 — 실제 소스 함수→목표 Owner 설계

**기준:** `integration/p1.5@ef0fa5531222d7ad34737712ac56b09c0da80e4b`; 원본 RF `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-053.md`; 담당 **Claude A 단독**, 상대는 read-only. 12 경로.

## 1. 실제 def 분석 / 새 파일명·함수명

Git blob `851700ffadd4509b8970fbdfd579b38c4badecfe`, SOURCE `libs/news/news_pipeline.py`, 531줄 확인.

| 현재 SOURCE::함수 | 줄수/행 | TARGET::함수 | 동작 |
|---|---:|---|---|
| `libs/news/news_pipeline.py::_fetch_yfinance_news_items` | L60–111 / 52 | `libs/news/news_pipeline_fetch_yfinance_news_items.py::_fetch_yfinance_news_items` | MOVE_BODY; pure 후보 |
| `libs/news/news_pipeline.py::_to_news_item` | L118–163 / 46 | `libs/news/news_pipeline_to_news_item.py::_to_news_item` | MOVE_BODY; pure 후보 |
| `libs/news/news_pipeline.py::_news_symbol_decay_meta` | L343–386 / 44 | `libs/news/news_pipeline_news_symbol_decay_meta.py::_news_symbol_decay_meta` | MOVE_BODY; pure 후보 |
| `libs/news/news_pipeline.py::_parse_news_timestamp` | L310–331 / 22 | `libs/news/news_pipeline_parse_news_timestamp.py::_parse_news_timestamp` | MOVE_BODY; pure 후보 |

- **_fetch_yfinance_news_items:** 원본 52행 → `libs/news/news_pipeline_fetch_yfinance_news_items.py::_fetch_yfinance_news_items`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_to_news_item:** 원본 46행 → `libs/news/news_pipeline_to_news_item.py::_to_news_item`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_news_symbol_decay_meta:** 원본 44행 → `libs/news/news_pipeline_news_symbol_decay_meta.py::_news_symbol_decay_meta`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_parse_news_timestamp:** 원본 22행 → `libs/news/news_pipeline_parse_news_timestamp.py::_parse_news_timestamp`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.

## 2. 소유 전체 파일별 SOURCE → TARGET / 사유

| 파일(기존/기본 목표) | bytes / blob | 처리 |
|---|---|---|
| `libs/news/model.py` → `libs/news/model.py` | 468 / `0f8832b9a4f1` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/models.py` → `libs/news/models.py` | 469 / `05bce4b41d9a` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/news_analyzer.py` → `libs/news/news_analyzer.py` | 2968 / `5954198398f8` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/news_pipeline.py` → `libs/news/news_pipeline.py` | 18228 / `851700ffadd4` | 상기 함수 이동·경계 유지 |
| `libs/news/providers/base.py` → `libs/news/providers/base.py` | 893 / `54c957add846` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/providers/google_news.py` → `libs/news/providers/google_news.py` | 697 / `c36d5869be39` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/providers/naver.py` → `libs/news/providers/naver.py` | 3575 / `3ea82d4f2b88` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/providers/registry.py` → `libs/news/providers/registry.py` | 1591 / `1a709626bd94` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/scorers/base.py` → `libs/news/scorers/base.py` | 374 / `ca6b87f8cb3b` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/scorers/llm.py` → `libs/news/scorers/llm.py` | 1127 / `638b6a76a7bc` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/scorers/registry.py` → `libs/news/scorers/registry.py` | 365 / `164692b14526` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/news/scorers/simple.py` → `libs/news/scorers/simple.py` | 2612 / `0603f76fbf09` | KEEP_IF: 역할·위치·길이 정당하면 통과 |

## 3. C03 전달·개발자 구현·수용

- **C03만** 위 설계 문서/소스를 읽고 목적지 충돌을 확인한 후 정확한 SOURCE·TARGET·fixture를 C01/C02 **본문에 직접 기재**. A/B는 이 RF 문서를 추가로 읽지 않는다.
- 적절한 KEEP는 한 줄 이유+blob으로 즉시 PASS, 반복 테스트/peer 0. 이동은 계산 몸체 원본에서 실제 제거하고 새로운 Owner에 구현, public wrapper 유지; 소비자·부작용 유지.
- 변경 함수만 normal fake before/after test 1회, git body diff 및 target blob/원본 LOC 보고. 개발자는 자기 브랜치 code/test만 push, C04 묶음 통합/C05 기존 DONE 보존·TARGET_GAP 분리.
