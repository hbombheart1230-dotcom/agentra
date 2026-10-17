## 2026-10-17 · Reporter Role R-11 (proposal, NOT_PUBLISHED)
**Stage:** Architecture and Maintainability
**Tags:** REFACTOR · TESTING · DOCS

- R3 facade 주입 패턴으로 Reporter 함수 본문 313개(23개 facade 경로, owner 파일 41개)를 이동했습니다(R-4~R-9). 모두 순수 함수는 아닙니다. R-8에는 facade가 넘겨준 콜백으로 I/O를 수행하는 READ_VIA_CALLBACK 읽기 함수가 포함되며, 읽기 계약 테스트와 콜백 패리티 테스트로 검증했습니다.
- R-10: 이동하지 않은 I/O 함수 47개 전부에 BASE 대비 현재 코드의 오프라인 계약 검증을 추가했습니다(읽기·쓰기·시계·모듈 정체성·재정의). 리포트 생성→파일→API 읽기 패리티, 고정 시계 바이트 비교, LLM·Broker·truth 함수 22개의 읽기 전용 권한 지도도 추가했습니다. I/O·권한 함수는 이동하지 않았습니다.
- `controlled_mock_lane_report`: Reporter 표시·읽기 어댑터로 기존 경로에 의도적으로 유지합니다(Work 결정). Q10/Q12는 변경하지 않았습니다.
- R-11: 저장소 산출물 위생 검사를 추가했습니다(커밋별 OS 캐시·미확장 환경 변수 경로 거부). c5d004b의 Windows 캐시 파일 4개는 트리에서 제거됐지만 이력에는 남아 있습니다. 이력 재작성은 소유자 승인이 필요합니다.
- UI 소스: `apps/api/adapters/patch_notes.py` → `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` (Work 소관). 이 항목은 미게시 제안입니다.
