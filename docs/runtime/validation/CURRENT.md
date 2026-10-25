# Agentra PC 실런 검증팀 — CURRENT (전용 작업 포인터)

> 이 문서는 **개인 PC Codex·Claude 런검증 전용**이다. 최초·변경 시 [D04](D04_RUNTIME_VALIDATION_RULES.md)만 읽는다. 개발팀 D00/D01/D02/D03·RF·HANDOFF를 작업 시작 조건으로 삼지 않는다.

- **대상:** `origin/integration/p1.5` 최신 exact SHA를 매 실행 확인. `main` 또는 A/B 브랜치 실행·변경 금지.
- **PC:** `C:\AgentraRunLab` 전용. `C:\Agentco`와 기존 개발·운영 데이터 보존.
- **이번 과제:** 실제 Agentra 운영 PC와 같은 진입점·설정으로 **키움 모의투자 + 실데이터 + LLM + 전체 장중 루프**를 구동·검증. 단순 probe/fixture PASS로 대체하지 않음.
- **Codex:** 환경 구성·실제 실행·증거 수집. **Claude:** 같은 SHA에서 실행 증거 독립 확인·실패 원인 검증.
- **결과:** 로컬 `C:\AgentraRunLab\reports` / `logs` / `state`에 실행 SHA·모드·명령·exit·주문/체결·장애·다음 행동 기록. 보고는 PASS/FAIL/BLOCKED/NOT_RUN 구분.
- **예약:** Codex/Claude 자체 예약 기능 대상. 사용자 지시 없이 예약 생성·주기/활성 변경하지 않음.
- **권한:** PC 검증 전용. 원격 push·개발 소스 수정·RF 이동·CI 오라클·안전 가드·실계좌·`main` 변경 금지.

> 실런 환경은 구축 중이며, 이전 5362874e SHA의 probe exit 0만 확인됐다. 외부 데이터·LLM·Paper 전체 런 성공은 **아직 NOT_RUN/미입증**. 새 회차 증거는 이 포인터에 누적하지 않는다.
