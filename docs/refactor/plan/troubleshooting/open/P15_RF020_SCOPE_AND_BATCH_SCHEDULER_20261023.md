# P1.5 — RF-020/001 범위 및 예약 조기 종료 검증

- **상태:** `OPEN / VERIFY_PENDING` · 지팀장 GPT 소유권·배정 검토, Codex B 실행 결과 보완
- **관계:** [RF-020 Monitor](../../pending/RF-020.md) · [RF-001 Operator UI](../../pending/RF-001.md) · [RF-010 graph](../../pending/RF-010.md) · [RF-026 runtime signals](../../pending/RF-026.md) · [RF-075 tests](../../pending/RF-075.md) · [원격 브랜치 정리](P15_BRANCH_CLEANUP.md)
- **기준 SHA:** `integration/p1.5@95d04a40`, B `work/p15-b-operator-structure-20261022@a3d60e37` (실행 시 재확인)

## 접수된 B 보고 (실행 로그/리뷰 증거는 별도 확인 전)
- RF-020: `libs/runtime/monitor/` 30파일은 B/integration 차이 없고 기존 Owner 분리 완료라고 보고. 실제 남은 `intraday_monitor_signals.py`는 RF-026, `monitor_node.py`는 RF-010, 역할 관련 테스트는 RF-075 귀속.
- RF-001: 현재 B/integration의 UI data_access 범위 차이 없음으로 보고. `NO_MORE_AUTHORIZED_READY_SCOPE`로 종료.
- **이번 실행의 새 구현 커밋 없음, normal/`python -O` = NOT_RUN, Claude 검증 = NOT_RUN.** 기존 구현 재수용/KEEP_VERIFIED/DONE 판정 근거가 아직 없음.
- CURRENT의 Codex 배정은 **RF-001 + RF-020 + 구 UI 브랜치 정리 3건**. 보고에는 세 번째 건의 실행·차단 근거 없음.
- 예약 프롬프트의 '가장 큰 RF 1건 우선' 표현으로 배정 전체 순회가 빠졌을 가능성. 운영 규칙을 CURRENT와 D01/D02에서 바로잡아 예약 프롬프트는 한 줄로 유지.

## 지팀장 추가 확인 / 종료 조건
- [ ] RF-020·RF-001의 실제 BASE 대비 소비자 호출·중복 책임/잔여 구조 감사. 'diff 없음'만으로 KEEP_VERIFIED/DONE 선언 금지.
- [ ] RF-010/026/075가 실제 Monitor 작업을 막는지 확인, 필요하면 지팀장이 **정확한 독점 파일 소유권**을 재배정하거나 RF를 별도 병렬 실행. 임의 cross-RF 코드 수정 금지.
- [ ] Codex B가 현재 배정 모든 RF와 브랜치 정리 각각에 대해 `PASS/VERIFY_PENDING/BLOCKED/NO_WORK` 상태, SHA, 근거를 보고.
- [ ] 신규 코드가 있다면 normal/`python -O` 및 새 독립 Claude CLI PASS, 통합 SHA hosted CI 증거 확인. 없더라도 KEEP_VERIFIED는 명시적 근거/독립 검토 필요.
- [ ] 충돌·브랜치 삭제와 실거래 안전 영향 없음 확인 후 지팀장이 CLOSED 여부 판정.

**금지:** 본 문서만으로 RFC 소유권 변경·코드 병합·브랜치 삭제·실거래/안전 수정 또는 DONE 이동 불가.
