# Agentra P1.5 — CURRENT

**정본:** `integration/p1.5`의 이 파일. 상시 규칙은 [D00](D00_ENGINEERING_DELIVERY_POLICY.md), 상세 차단은 [STATUS](../plan/STATUS.md)와 각 RF. **D00 수정 금지.** 회차별 절 추가 금지, 현재 상태로 전체 교체.

## 실물 상태·새 배정

- 큐: PENDING 61 / DEVELOPING 3 / PEER 1 / **LEAD 14** / DONE 14 / REWORK 0 = 93 unique. **물리 큐 및 원개발 Owner 유지.** LEAD = 014,015,016,028,029,031,032,033,034,050,063,065,067,069.
- A `1fe4efe3`: B 소유 RF-063 DR Windows temp, RF-065 scorecard→Stage2 실제 writer, RF-067 reports/trades delegated target 독립 scoped peer; source0. B `2b1cd7da`: A 소유 RF-031 writer·3번째 write OSError 독립 scoped peer 보고; source0·하네스 미보존. 전체 DONE 아님. 재실행 금지.
- **최우선 목표:** 신규 PENDING 개발·반복 synthetic 테스트 대신 LEAD 미충족 게이트 해소. A는 B 원개발 RF의 독립 peer, B는 A 원개발 RF의 독립 peer. 검증만 통과했다고 DONE으로 판단하지 않으며, 최종 결정과 04→05 물리 이동은 지팀장 전담.
- A/B는 기존 자기 브랜치에서만 수행. 각 신규 최초 경계는 SOURCE SHA, 실제 normal/-O 명령·exit, State·IO·예외·outside-write 및 잔여 1개 게이트만 HANDOFF 1회 제출. 차단되면 다음 배정 RF 계속. 동일 SHA/경계 재검증·HANDOFF-only 커밋 금지.

## Claude A — B 원개발 LEAD 독립 검증

브랜치: `work/p15-a-reporter-pure-20261021`. **기존 A 자기 원개발 반복 검증은 후순위.**

1. **P0 RF-063:** diagnostics CLI의 미검증 쓰기·cp949 locale·출력/exit·Windows/스케줄러 소비자를 안전한 temp-only fake로 독립 검증. 기존 76 import/metrics/alert/audit peer 반복 금지.
2. **P1 RF-065:** research CLI의 scorecard→Stage2 실제 temp 연속 쓰기·부분 OSError·State, no-fetch·argv/exit·외부 IO 독립 검증. 기존 CLI fake·A smoke·54 import 반복 금지.
3. **P2 RF-067:** 공개 wrapper 14개는 검증 완료. delegated diagnostics target의 새 소비자·stdout/stderr·exit·PATH·fail-closed 독립 peer만 수행.
4. **조건부 RF-015:** B가 Monitor 역사 11 FAIL·B-only 2파일 소비자 근거를 제출하면 그 **새 B 범위만** A가 독립 peer. RF-069 UEF5는 승인된 historical snapshot 전 실행 금지.

## Codex B — A 원개발 LEAD 독립 검증

브랜치: `work/p15-b-operator-structure-20261022`. **아래 순서대로 처리, 첫 미충족 경계 해제 후 다음 RF.**

1. **P0 RF-031:** 기존 writer/부분 OSError peer 반복 금지. **최초 부족: Reporter caller State→day-cache/ledger/memory 및 예외 후 부분 산출 소비자·복구**를 temp-only fake LLM normal/-O로 독립 검증. 재현 명령·하네스·exit 제출.
2. **P1 RF-050:** Operator `data_access_core` primary→repair→line LLM fake 오류/timeout·fallback·cache 효과.
3. **P2 RF-016:** news-query→`strategic_answers` 실제 facade/dynamic 소비자·중첩 State/예외.
4. **P3 RF-029:** story bundle v1/v2→assembly·external truth-root read·State alias/예외.
5. **P4 RF-033:** `InputWorker.tick→publish_input` provider→storage·실제 temp IO/State·실패 독립 peer. A Windows storage 15×2는 재사용만.
6. **P5 RF-014:** Scanner→Graph/Runtime Top1/ranking/NOOP dynamic 소비자 및 역사 3 BASE FAIL 분리.
7. **P6 RF-028:** trade-report rich schema→summary/full renderer·실제 외부 writer 소비자.
8. **P7 RF-034:** casebook→scanner와 latent producer→temp cache/output·부분실패.
9. **P8 RF-015:** Monitor 11 역사 FAIL BASE 대조, State/event 소비자 및 B-only 2파일 실사용 확인 후 A peer 인계.
10. **P9 RF-032:** validation_id 입력 신뢰/Exit Horizon와 scorecard→Stage2 temp 부분실패, 기존 135 owner 증거 재사용. UEF/frozen 의미 변경은 승인 대기.

B가 직접 소유하는 RF-063/065/067은 A peer가 요청하는 **신규** 소비자·효과 자료만 보완하며, 자기 검증을 독립 peer로 보고하지 않는다.

## 지팀장 인수·안전

- 새 A/B 증거가 도착한 **영향 RF만** 최종 인수하고, 조건 충족 시 LEAD→DONE 즉시 실물 이동/구 경로 삭제/93 unique·commit SHA 확인. 새 증거 없으면 `NO_DELTA`, Git 쓰기0.
- RF-069은 UEF5 historical snapshot **path/SHA/use-scope 사용자/증거 소유자 승인 전 SAFETY_HOLD**. RF-032/034 보호 closeout·UEF 승인 대기. RunLab #32 신규 mock SELL `0045749` 체결 미확정·전일 SELL 출처 불명·OCI SOURCE_SHA 미입증: 안전 수정·재배포 금지.
- D00·main·거래 안전 계약·동결 테스트/CI·운영 데이터·예약 변경 및 신규 브랜치/PR/worktree 생성 금지. 실제 소스 변경은 사전 사용자 승인. 작업 순서: A/B 새 근거→지팀장 판단·가능한 DONE→다음 배정→STATUS 현재 상태 교체→**CURRENT 마지막 전체 교체**.
