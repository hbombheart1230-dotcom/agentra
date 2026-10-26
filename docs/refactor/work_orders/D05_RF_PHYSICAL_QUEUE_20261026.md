# D05 — P1.5 RF 물리 큐 및 담당팀 분리 (2026-10-26 KST)

> D00 안전·권한 및 D03 검증·통합 게이트에 종속. D05는 상태·이동의 단일 정본이다. 93개 RF 전체에 적용한다.

## 표준 디렉터리
```text
docs/refactor/plan/queue/
  01_PENDING/
    CLAUDE_A/
    CODEX_B/
    UNASSIGNED/
  02_DEVELOPING/
    CLAUDE_A/
    CODEX_B/
  03_PEER_REVIEW/
    CLAUDE_A/    # Claude A가 Codex B의 후보를 검증
    CODEX_B/     # Codex B가 Claude A의 후보를 검증
  04_LEAD_ACCEPTANCE/
    CLAUDE_A/    # 원개발 Claude A, 처리 권한은 지팀장
    CODEX_B/     # 원개발 Codex B, 처리 권한은 지팀장
  05_DONE/
    CLAUDE_A/
    CODEX_B/
  06_REWORK/
    CLAUDE_A/
    CODEX_B/
```

## 불변 조건
1. RF-001~RF-093은 각각 정확히 하나의 활성 단계·파일에만 존재한다. 단계 간 이동은 Git rename에 준하는 내용 보존·원본 삭제·신규 경로 확인을 하나의 원자적 커밋으로 처리한다.
2. PENDING/DEVELOPING/REWORK/DONE/LEAD_ACCEPTANCE 하위 팀은 **원개발팀**이다. PEER_REVIEW 하위 팀은 **실제 독립 검증팀**이다. 교차 팀이 개발 권한을 갖는다는 뜻이 아니다.
3. 원개발자가 source SHA와 정상/-O 및 구체 인수 증거를 제출하면 DEVELOPING→PEER_REVIEW/상대팀. peer 완료 시 PEER_REVIEW→LEAD_ACCEPTANCE/원개발팀. 실제 결함만 REWORK/원개발팀. D03 인수·통합 exact SHA 완료 시 DONE/원개발팀.
4. REWORK 해결 뒤 새 SHA만 재-peer한다. 동일 source SHA·동일 테스트 경계 반복 금지. KEEP_NOOP는 원본 owner/test blob 동일성과 기존 독립 증거를 근거로 지팀장이 직접 종결할 수 있다.
5. 위험 안전 HOLD·환경 차단은 정확한 해제 조건을 기록한다. 추상적 부분 PASS라는 이유로 개발팀에 재배정하지 않는다.
6. 지팀장만 큐 이동, STATUS/CURRENT 정합성 및 최종 DONE을 승인한다. PC 런검증팀은 이동 권한이 없다.
7. 이전 `pending/`, `verification/`, `rework/`, `done/`은 **마이그레이션 중에는 정본**이다. 93개 실제 파일 이동과 링크·카운트 검증이 끝나기 전 새 큐를 활성화했다고 주장하지 않는다. 혼합 큐 상태를 ACTIVE로 선언하지 않는다.

## 마이그레이션 게이트
- 기존 실제 경로 93개를 HEAD에서 조회하고 ID 001~093 중복/누락 0, 내용 blob 보존, 새 파일 93개·기존 활성 파일 0을 검사한다.
- 모든 STATUS/CURRENT/RF 상호 링크를 새 경로로 갱신하고 시작/종료 SHA 및 실제 이동 개수를 기록한다.
- 원자적 전환 전 예약 작업의 구 큐 해석을 유지한다. 사용자 승인 없는 예약 수정 금지.
