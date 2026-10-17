## 2026-10-17 · Reporter Role R-9
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCS

- R3 facade 주입 패턴으로 Reporter 순수 함수 본문 313개(23개 facade 경로, owner 파일 41개)를 `libs/agents/reporter`로 이동(R-4~R-9). 기존 함수 서명·wrapper 유지.
- controlled_mock_lane_report는 Work 결정에 따라 현재 경로에 Reporter 표시/읽기 어댑터로 유지.
- 이전 T3 v4 제안은 Work의 guard(P15-WORK-001)로 대체. 공식 UI 반영은 Work 소관.
