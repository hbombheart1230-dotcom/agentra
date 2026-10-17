## 2026-10-17 · Reporter Role R-3
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCS

- 순수 Reporter 모듈 12개 이동 + 350 LOC 초과 3개(trade_report_symbol_metadata, trade_story_pipeline_news, trade_story_pipeline_scanner)를 11개 owner로 분해(본문 AST 동일, 기존 경로는 re-export facade).
- BASE 기준 2565 사례 동일, 리포트 20종 결정 자료(변경 없음).
- 공유 ledger로 고정된 facade·T1 대상과 I/O 혼합 모듈은 BLOCKED/KEEP로 기록.
