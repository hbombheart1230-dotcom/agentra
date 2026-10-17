## 2026-10-17 · Reporter Role R-7
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCS

- R3 facade 주입 패턴으로 Reporter 모듈 21개의 순수 함수 본문 264개를 `libs/agents/reporter` owner로 이동(기존 함수 서명·wrapper 유지, 호출 시점 조회).
- 함수별 BASE 본문 동일성, monkeypatch 호출 순서, ABI 검증. LLM 라우팅·실행, 파일 I/O, truth precedence, broker, feedback 코드는 이동하지 않음.
- 공유 T3 검사 변경안(패치 v4)은 Work 통합 단계에서 적용.
