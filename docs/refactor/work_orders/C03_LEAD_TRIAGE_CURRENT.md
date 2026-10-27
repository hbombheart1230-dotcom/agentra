# C03 — 지팀장 수용·배정 라우터

**역할:** A/B Owner·독립 peer의 **원래 C1~C5 증거 판정과 다음 작업 배정만** 담당한다. [D00](D00_ENGINEERING_DELIVERY_POLICY.md) 준수. RF 실물 체크·단계/STATUS 이동은 **C05**, 정확 통합 SHA/CI는 **C04** 담당. 이 파일은 실행 지시이지 이력 저장소가 아니다. 이력은 [RF 원본/STATUS](../plan/STATUS.md) 및 A/B 브랜치 `HANDOFF_A.md`·`HANDOFF_B.md`에서 확인한다.

## 우선 배정 (원본 RF·HANDOFF가 최신 정본)
1. **B 독립 peer:** [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md)(원래 19 Owner C2/C3/C4) → [RF-031](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md)(원래 writer/State/실패 C2/C4). 기존 scoped 결과를 전체 PASS로 승격하지 않는다. 첫 미검증 계약만 특정하고 다음 RF로 이동.
2. **A Owner:** [RF-040](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-040.md)·[RF-061](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-061.md) 활성 CLAIM 2건. 기존 5 FAIL 출처 재분석 금지, 안전 C2/C3 마무리 → **B** full peer. Step5C 보호 HOLD 유지.
3. **B Owner:** [RF-065](../plan/queue/02_DEVELOPING/CODEX_B/RF-065.md)·[RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md) 전체 C1 ACTION/첫 미충족 C2/C3; **A**는 새로운 범위만 독립 peer.
4. **기존 PEER/DEV 계속:** A RF-014/016/028/029/032/033/034/050/051/054/058, B RF-066/070/071. 자기 [C01](C01_CODEX_CURRENT.md)/[C02](C02_CLAUDE_CURRENT.md)의 직접 RF 목록에서 안전한 미완료 계약을 수행. 보호 UEF/closeout·실거래·운영 쓰기 금지.
5. **신규 작업 공급:** B 미CLAIM RF-044→045→024→010→011→059, A는 슬롯이 비면 RF-036→037→039→038. A/B 각 동시 CLAIM 최대 2건, C05가 실제 PENDING→DEV 이동.
6. **RF-067:** 이미 LEAD, A peer 재실행 금지. C04의 정확 integration SHA offline safety CI → C05 C6/C7/DONE. **RunLab #32:** [OPEN 대장](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md)·[Issue](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 참조, 안전 HOLD/런 적용 판정 분리.

## 변경·정지 규칙
- **A/B SHA나 신규 증거가 없더라도 위 READY/미완료 원래 계약이 남아 있으면 작업 공급은 존재한다.** C03이 새 코드를 기다리며 A/B의 `할 일 없음`을 인정하지 않는다. 실제 환경/승인 차단과 대체 RF 소진을 근거로 구분한다.
- **배정·Owner·원래 차단 조건이 실제 바뀐 경우에만** C03 및 C01/C02의 해당 항목을 **교체**한다. 검증 표·이전 run/SHA·테스트 수치·STATUS 집계는 복제하거나 덧붙이지 않는다. 신규 변화가 없으면 **GitHub 쓰기 0**, 단 한 줄 보고.
- A/B가 막힌 RF 한 건만 보고 종료하지 않도록 **다음 READY RF 링크**를 명시한다. `NO_DELTA`, `BLOCKED`, 실제 `EXECUTION_LIMIT`는 D00 근거대로 구분한다.

**보고:** `변경된 배정만 | 실제 첫 차단 C | 담당 | 다음 READY RF`. C03은 코드·원본 RF 체크·큐 이동·통합·CI·DONE을 수행하지 않는다.
