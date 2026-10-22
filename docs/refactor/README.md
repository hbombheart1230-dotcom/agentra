# Agentra 리팩터링 문서 길잡이

**현재 실행 상황:** [한글 CURRENT.md](work_orders/CURRENT.md) — 20~30줄 정도의 현황/담당·작업 링크. 새 채팅의 첫 진입점.

## 여기서 필요한 링크만 읽기
- [미완료 12개 단계 P1.5.0~11](plan/pending/) / [완료](plan/done/) / [트러블슈팅 진행](plan/troubleshooting/open/) / [해결](plan/troubleshooting/closed/)
- [D00 — 공통 개발·안전 원칙](../ENGINEERING_DELIVERY_POLICY.md) / [D01 — Codex 실행·티키타카](../../AGENTS.md) / [D02 — Claude 실행·티키타카](../../CLAUDE.md)
- [P1.5~P8 전체 로드맵](p1_5_p1_6_master_plan.md) / [P1.5.1~11 책임 정합성](p1_5_1_to_11_responsibility_alignment_v1_1.md)
- [V3 동결 아키텍처](architecture/TREE_V3_FROZEN.md) / [전체 ROOT 현황](architecture/P15_ROOT_TO_LEAF_REALITY_AND_CLEANUP_20261018.md) / [26 libs 책임](architecture/P15_ALL_LIBS_OWNERS_20261018.md)
- [동결 전체 파일 트리](architecture/P15_TREE_ALL_PATHS_PINNED_20261018.txt) / [원본 경로별 소유권 후보](architecture/P15_ALL_FILES_OWNERSHIP_CANDIDATES_20261018.csv)

**사용법:** CURRENT → 담당 작업 파일 → 해당 파일의 **이미 확정된 원본 구현 패킷**. 같은 세션에서 Git blob SHA/파일 내용이 불변이며 이미 이해했다면 중복 전문 재독 금지. 새 세션은 CURRENT와 로드맵 1회 확인. 작업 단계와 근거는 패킷별로 별도 기록.

**완료 정의:** Code SELF_PASS와 PEER_PASS는 통합이 아니다. 지팀장이 정확한 통합 SHA의 필수 CI를 확인하고 단계별 완료 체크를 검수한 뒤 Git에서 `plan/pending/` → `plan/done/`으로 옮긴다. 부분 완료는 pending 유지. 작은 해결은 단계에 기록; 재발·안전·CI·통합 차단만 별도 troubleshooting 등록.

**변경 금지:** 전체 저장소의 P1.5 기존 동결 설계·원본 패킷과 거래 안전 원칙을 벗어나는 새 작업 재설계, 임의 main/실거래 활성화, 옛 BATCH/T00 지시 부활.

**이력:** 이전 장문의 리팩터링 README/CURRENT와 날짜별 증거는 Git의 이전 커밋(예: `1ce79193`) 및 기존 원본 문서에서 보존한다. 새 작업 허가는 아니다.
