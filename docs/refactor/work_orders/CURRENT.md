# Agentra P1.5 — CURRENT

**정본:** `integration/p1.5`의 이 파일. 상시 정책 [D00](D00_ENGINEERING_DELIVERY_POLICY.md)은 **읽기 전용**, 상세 증거·차단은 [STATUS](../plan/STATUS.md)와 기존 RF/HANDOFF. 현재 상태만 전체 교체하며 과거 회차 절 누적 금지.

## 현재 물리 상태·인수

- **큐:** PENDING 61 / DEVELOPING 3 / PEER 1 / **LEAD 14** / DONE 14 / REWORK 0 = **93 unique**, 중복 0. LEAD = 014,015,016,028,029,031,032,033,034,050,063,065,067,069. 신규 LEAD 0 / 신규 DONE 0 / 운영 source 통합 0.
- integration 기준 `ec1e302f`. **A `61e6aadc`:** 운영 source 0, RF-063/065/067 실제 CLI를 독립 temp-only subprocess normal/`-O` 추가 검증(보존 peer 스크립트 7개). 전체 RF PASS 아님. **B `b2399dfb`:** 운영 source 0·HANDOFF-only; RF-031 caller ledger/memory + 강제 partial Markdown OSError normal/`-O` exit 0 **보고**, 하네스 미보존. 기타 A 원개발 RF 9건의 scoped 결과도 전체 peer PASS 아님. 기존 동일 SHA/경계 PASS·BASE FAIL 재실행 금지.
- **지팀장 최종:** 위 scoped 경계만 인수, 모든 14 LEAD **HOLD/NOT_DONE**(069 SAFETY_HOLD). BASE 동등 pre-existing 오류는 신규 CODE REWORK 아님. 04→05 이동 0 / 코드 선택 통합 0 / CI 신규 실행 NOT_RUN. 원격 HEAD·A/B source SHA·93개 단일 경로 재확인 후 변경 판단.

## Claude A — B 원개발 peer

기존 브랜치 `work/p15-a-reporter-pure-20261021`만 사용. 완료된 RF-063 diagnostics 46+4 CLI, RF-065 research 46 및 필수 인자 19, RF-067 안전 target 재검증 **금지**.

1. **RF-063 / 065 / 067:** A의 안전한 Linux 격리 실행 경계는 현재 소진. 보호 UEF/실 인증/Windows Scheduler·PowerShell은 **NOT_RUN/승인 대기**. 추가 fake 전수검증·HANDOFF-only 커밋 금지. A가 확인한 `run_m23_closeout_check` 텍스트 출력 unbound `day`는 BASE 기존 버그: 소스 수정은 지팀장·사용자 별도 승인 후 원 Owner에 배정.
2. **RF-015 조건부:** B가 기존 11 FAIL node별 BASE 대비 근거 및 B-only `libs/agents/monitor` 2파일의 **새 실제 소비자**를 제시한 경우, 그 미검증 범위만 독립 read-only normal/`-O` 실행. 없다면 A 신규 검증 중지.

## Codex B — A 원개발 peer

기존 브랜치 `work/p15-b-operator-structure-20261022`만 사용. 기존 자기 RF-063/065/067를 자기 peer라고 주장하지 않는다.

1. **P0 RF-031:** 새로 보고한 caller ledger/memory·부분 OSError는 범위 한정 재사용. **최초 부족: 부분 산출을 받은 downstream 호출자의 상태·복구/재시도 처리**를 temp-only fake LLM, 실제 원본 caller·실효과 격리 normal/`python -O` 독립 검증. 정확 source blob·재현 가능 명령·하네스·exit·outside-write0을 1회 제출. `pytest` 미설치(기존 exit 1/1)는 **ENV** — 기존 테스트 반복 없이 안전한 직접 Python 실행 우선; 필요할 때만 환경 담당자에 의존성 요청.
2. **이후 순서 (첫 게이트만):** RF-050 model catalog cache artifact/부분실패 → 016 nested State 예외 projection → 029 외부 truth-root 읽기/실패 → 033 provider/storage 실패 → 014 dynamic Top1→NOOP → 028 정식 rich schema writer → 034 casebook→Scanner → 015 역사 11 FAIL·B-only 소비자 → 032 validation_id/Stage2 부분실패. 기존 marker 재실행 금지, source 변경 필요 시 사용자 승인 전 진행 금지.

## 지팀장 다음 행동·안전

- A/B 새 **source/peer**, RF 큐, CI/RunLab #32 **신규** 변화만 비교. 미처리 DONE 조건이 없다면 동일 LEAD 전건 재심사 금지. 조건 충족 즉시 해당 04→05 단일 경로 물리 이동/구 경로 삭제·93 unique/정확 blob/tree/commit 확인.
- RF-069 UEF5 historical snapshot **path/SHA/use-scope 승인 전 SAFETY_HOLD**. RF-032/034 보호 closeout·UEF 승인 필요. RunLab #32 mock SELL `0045749` fill-truth 불명, 전일 SELL `0020349` provenance 불명, OCI SOURCE_SHA UNKNOWN: 주문·운영 데이터·가드·배포 무승인 변경 금지.
- D00·main·실거래·Broker/Supervisor/Executor/Step5C/UEF·동결 테스트/CI·스케줄·신규 브랜치/tag/PR/worktree 변경 금지. 충돌 시 기존 integration HEAD 재조회 후 비강제 재시도, 불가하면 `GIT_BLOCKED`. **순서:** 신규 peer→지팀장 판정·가능한 코드/RF 이동→새 배정→STATUS 전체 교체→CURRENT **마지막 전체 교체**. 진척·현재상태 변화 없으면 Git 쓰기 0.
