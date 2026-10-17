## 2026-10-17 · Reporter Role R-10 (proposal, NOT_PUBLISHED)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCS

- R3 facade 주입 패턴으로 Reporter 순수 함수 본문 313개(23개 facade 경로, owner 파일 41개) 이동(R-4~R-9).
- R-10: 이동하지 않은 I/O 함수 47개 전부에 대해 BASE와 현재 코드의 오프라인 계약(읽기·쓰기·시계·모듈 정체성·재정의) 검증, 리포트 생성→파일→API 읽기 패리티, 고정 시계 바이트 비교, LLM·Broker·truth 함수 22개 읽기 전용 권한 지도 추가. I/O·권한 함수 이동 없음.
- UI 소스: `apps/api/adapters/patch_notes.py` → `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` (Work 소관). 이 항목은 미게시 제안.
