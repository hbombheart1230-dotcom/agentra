# C03 — 지팀장① | 현재 수용·배정 라우터

> **진입점 C03 + [D00](D00_ENGINEERING_DELIVERY_POLICY.md).** 구 `CURRENT.md`(C00) 사용 금지. RF 원본의 `## DONE 체크`가 판정 정본이다. C03은 **C1~C5 근거 권고·A/B 배정만** 수행하며 RF 체크·실물 이동·STATUS·통합·CI·DONE은 각각 C05/C04 소유다. 같은 SOURCE/범위의 성공 검증 재실행 금지.

## 🔴 현재 첫 미충족 조건·다음 담당 (2026-10-27 23시, A run161~162 + B RF-028/029/066/070/071 신규 근거)

| 우선 | RF 원본 | 첫 원래 부족 조건 / 신규 증거 판정 | 담당·NEXT |
|---:|---|---|---|
| 1 | [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md) | C1/C2 A run149 19-owner ACTION·State/event **Owner 증거 도착**, C3 BASE 11 FAIL은 기존 docs inventory, B-only Commander frozen 실패는 별도. 원본 C1~C4는 여전히 미체크; **C4 full peer 없음** | **B**: 19 owner 원래 C2/C3/C4 범위와 기존 scoped peer를 1회 매칭해 최초 실제 누락만 독립 확인; frozen oracle 변경 금지. A는 기존 run112/145/149 반복 금지 |
| 2 | [RF-031](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md) | **C2** 원래 writer/State/실패 계약 전체 인수 대기. A run150 22-owner ACTION·partial OSError, B 최신 real caller cache/memory + partial regeneration **SCOPED_PASS**, full C4 아님 | **B**: frozen 13개 보호 범위와 나머지 원래 C2/C4를 대조, 미충족 **한 소비자 계약만** 제출; 동일 OSError·cache peer 재실행 금지 |
| 3 | [RF-067](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-067.md) | **C4**. 원래 14 root wrapper. A 독립 root→target scoped 증거는 기존 2(root reports_trades_health/reporter_upgrade) + run151 4 + run138e 4(file-effect temp 격리) + run138d 2(q9_q12/트레이드 리포트 제한 모드) = **서로 다른 12/14 root**. 기존 “6개 검증·나머지 8개”는 run138d/e 누락으로 과소집계. A run162 이후 **보호 2 root도 fake-wrapper 기계적 경계만 검증됨**(실 target NOT_RUN). 남은 **2 root는 daily_uef_run_status/real_execution_preflight** 보호 target. 전체 RF C4 PASS 아님 | **B→A**: 12개 경로별 정확 SHA/실행 모드/보호 제외 매트릭스 확정 → **A run162**가 보호 2 root 공개 import/argv/예외/exit fake-module **20/20 SCOPED_PASS** 제출(정확 wrapper blobs `7a531b73`/`27ac1cf1`). **14/14 root의 wrapper 기계적 경계에는 증거가 있으나**, 보호 2개 실제 delegated target은 NOT_RUN/SAFETY_HOLD. **A**: 기존 12개 scoped target/root + run162 보호 2개 fake-wrapper 근거를 정확 SHA로 한 표에 합쳐 **원래 14 wrapper 범위 전체 C4 PASS 가능 여부** 또는 부족한 원래 조건 1개를 서면 판정(재실행 금지). **C03→C05**: 원래 RF-067 C4가 root-wrapper 계약만 요구하는지, target 동작까지 요구하는지 원본으로 최종 대조; 보호 target 실실행을 새 게이트로 만들지 말 것. UEF/real preflight 실제 target·Windows 운영 호출 금지 |
| 4 | [RF-014](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md) | **C2** 원래 Scanner consumer/ranking/reject/NOOP 계약의 남은 범위. A run148 C1 20-owner ACTION, B static 20/20·shim→RF-009 dynamic scoped peer 도착; 전체 C1~C4 MET 아님 | **A**: C2/C3 원래 범위와 기존 증거 매칭, 부족한 한 경계만 제시 → **B** 반대 full peer 판정 |
| 5 | [RF-016](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md) | **C2/C4**. A run155 C1 8-owner 최종 KEEP ACTION; 기존 run115/116 및 B nested-projection scoped peer. 원래 외부 facade 전체 PASS 미확인 | **B**: A exact blobs의 원래 Strategist facade→owner 소비자 범위 중 미검증 한 경계만 peer; A는 기존 C1 반복 금지 |
| 6 | [RF-050](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md) | **C1** 8-owner 최종 ACTION의 C05 판정 근거 아직 부족(원개발 run146은 source/caller/cache 지도). B fake caller 10/10 scoped 재사용 | **A**: 8-owner KEEP/COMPAT/효과 ACTION 최종 한 표 → **B** 원래 UI caller/cache 실패 C4 잔여만 |
| 7 | [RF-065](../plan/queue/02_DEVELOPING/CODEX_B/RF-065.md) | **C1** 54-owner ACTION map 후보·원본 미체크. 이전 C2 출력 루트 이탈 8건의 원인(`run_integrated_trade_diagnosis`에 `output_root` 미전달)을 B가 **소스 blob `6aaabc3e`→`4119747f`**로 수정(B commit `1641cfef`). B의 fake downstream normal/`-O` 2모드 `SCOPED_PASS`는 격리 출력 경계만 증명. **A run161 독립 공개 CLI fake 14/14 SCOPED_PASS**(정확 B `1641cfef`, blob `4119747f`; real downstream writer NOT_RUN), 전체 54-owner C1 및 원래 C2/C3/C4 미충족, integration 미통합 | **A**: run161 성공 범위 재실행 금지; 다른 원래 C4 필수 경계가 특정될 때만 추가 peer. **B**: 54-owner C1 ACTION 최종 근거·원래 C2/C3 최초 누락 계약만 제출하고 RF-015/031 full peer 우선. 실제 writer/네트워크/운영 보고서 실행 금지 |
| 8 | [RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md) | **C1** 76-owner 중 13 wrapper 매핑 완료, 잔여 63 ACTION. TEXT NameError 1행은 통합·A 4/4 peer·CI 성공, 전체 RF는 미완료 | **B**: 잔여 원래 ACTION/소비자 근거만 제출 → A 새 범위 peer; 기존 TEXT/JSON 검증 반복 금지 |
| 9 | [RF-029](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md) | **C4**. A run158 **38/38 최종 KEEP_VERIFIED ACTION**(정적 Owner C1) 도착, run153 facade→bundle은 A 자체 scoped 증거. **B 신규 facade→bundle 35/35 normal/`-O` 소비자 peer SCOPED_PASS**. 원본 C1 체크는 C05 전용이며 B full peer 아님 | **B**: 35/35 facade→bundle 성공 범위 재실행 금지; 38-owner 전체 소비자 중 최초 미검증 경계만 확인. A C1 재작업 금지 |
| 10 | [RF-028](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md) | **C4**. A run158 **85/85 최종 KEEP_VERIFIED ACTION**(정적 Owner C1), 무효과 토큰·소스 parity 주장; **B 신규 132/132 normal/`-O` rich-schema facade/AI fake 소비자 peer SCOPED_PASS**. C1 원본 체크·85-owner 전체 peer PASS 별도 | **B**: 기존 132/132 소비자 검증 재실행 금지; 원래 85-owner 범위 중 빠진 첫 소비자/효과 경계를 정확 SOURCE로 특정해 독립 peer; A C1 반복 금지 |
| 11 | [RF-033](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md) · [RF-034](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md) | **C4**. A run157 **45/45·40/40 최종 KEEP_VERIFIED ACTION**(정적 Owner C1) 도착; run156 parity에서 진전. 효과 토큰은 기존 fake/temp 근거와 구별, UEF/closeout 실실행 미확인 | **B**: RF-033 Q10/Q12 input_worker→publish_input, RF-034 casebook→Scanner의 원래 필수 미검증 소비자 1개씩 독립 peer; 보호 실행 금지 |
| 12 | [RF-032](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md) | **C1/C4**. A run159 135파일 정적 ACTION: **107 KEEP_VERIFIED + 28 SAFETY_HOLD(KEEP)**, 보호 UEF writer 실실행 없음. 정적 Owner 분류는 C1 최종 체크나 반대 B peer PASS가 아님 | **B**: 기존 temp/fake writer·validation-id 증거와 원래 C2~C4를 대조해 안전한 최초 누락만 peer; UEF/closeout 보호 실행은 별도 승인 전 NOT_RUN |
| 13 | [RF-069](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-069.md) | **SAFETY_BLOCKED** historical UEF5 snapshot 경로/SHA/use-scope 및 사용자·증거 소유자 승인 없음 | **B/A**: NOT_RUN 유지, 다른 안전 RF로 회전 |

**다음 안전 READY:** [RF-051](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-051.md) · [RF-054](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-054.md) · [RF-058](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-058.md). RF-028/029/032/033/034는 A의 최신 정적 ACTION을 B 독립 peer에 배정한다. A run154의 RF-051/054/058 C1 ACTION도 원래 C2~C4·반대 peer 전체 PASS는 별도다.

## ▶ 신규 안전 READY/부분 근거 (B HANDOFF `fea02def`, A HANDOFF `6cdb53b1`)

- **RF-066 (B Owner):** synthetic skill/timeout 11개 normal PASS, `python -O` 11개 수집·exit0은 pytest assert 제거 경고로 **최적화 모드 실행/예외 parity**만 인정. 직접 demo는 yfinance 호출 시도로 `SCOPED_FAIL/SAFETY_HOLD`; **B**는 네트워크 시도 0을 보장하는 fake scanner fallback 경계만 추가하고 나머지 16-owner C1/C2/C3를 정리. **A**는 안전한 새 SOURCE·원래 전체 범위가 제출될 때만 독립 peer.
- **RF-070 (B Owner):** operator/reporter 두 launcher parser normal/`-O` scoped, reporter temp synthetic writer 8/8 normal/`-O` scoped. **B**는 남은 20 OTHER launcher 원래 C1/효과 분류, 32 위험 launcher 실실행 HOLD. 기존 parser·8개 테스트 반복 금지.
- **RF-071 (B Owner):** 42-owner 중 3개 entrypoint 정적 C1만 분류(2 COMPAT wrapper, `approval_cli.py`는 Step5C 승인 경계 SAFETY_HOLD_KEEP). **B**는 나머지 39개 Owner ACTION/소비자 경계를 읽기 전용·temp/fake로 진행; 승인 CLI 실제 호출 금지.
- **A HANDOFF 구 C00 정본 참조:** 문서 맨 위 `CURRENT.md` 지시는 폐기된 참조다. D00과 C02가 정본이며 A 작업자가 후속 자기 HANDOFF 편집 시 정합화할 사항이다(C03은 A HANDOFF를 수정하지 않음).

## ▶ 인계·물리 단계

- [C01 B 작업판](C01_CODEX_CURRENT.md) / [C02 A 작업판](C02_CLAUDE_CURRENT.md): 위 **최초 부족 C번호 + 담당 + 다음 링크**를 우선한다. 새 테스트 명세를 여기서 만들거나 누적 델타를 덧붙이지 않는다.
- [A HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md) `6cdb53b1` run149~162 / [B HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md) `fea02def` (RF-065 출력 seam `1641cfef` 이후 RF-028/029 scoped peer·RF-066/070/071 owner evidence, full peer 아님): 정확 SOURCE·Owner vs peer·PASS vs SCOPED_PASS/NOT_RUN을 구분한다. A의 정적 C1 ACTION은 C05의 원본 체크가 아니다.
- [C05 종결판](C05_LEAD_CLOSEOUT_CURRENT.md) / [C04 통합판](C04_LEAD_INTEGRATION_CURRENT.md): **현재 신규 LEAD_READY 0건**. C1~C5 전체 MET/적법 N/A 및 반대 full peer PASS 확인 때만 C05에 추천; C05 실제 LEAD 이동 후 C04 C6.
- [RF-046](../plan/queue/05_DONE/CLAUDE_A/RF-046.md) · [RF-047](../plan/queue/05_DONE/CLAUDE_A/RF-047.md) · [RF-052](../plan/queue/05_DONE/CLAUDE_A/RF-052.md): **이미 DONE**, C03 재검증·재승인 금지.
- [RunLab #32 OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md): [20:09 FINAL](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6440428084) 신규 증거 인수: mock SELL `0045749` 체결 확인, BUY `0017713` broker 체결 대비 local event 0, SELL guard `filled_qty=-1` TTL 후 약 10.5h 잔류, Reporter `trade_rows=[]` vs broker 청산 1. **B**는 ORDER RF-012/055의 BUY 제출→local 기록 누락 및 GUARD RF-048 TTL/filled-truth를 read-only/fake로 분리, **A**는 REPORT RF-030/035의 producer 입력 누락·GREEN visibility를 read-only/fake로 분리, **RunLab**은 OCI source 증거·EOD 누락 여부 읽기 전용 확인. FILE_OWNER≠DEFECT_OWNER, `RUN_SOURCE_SHA=UNKNOWN`, `DEV_RESOLVED=NO`, `RUNTIME_VERIFIED=NO`, `SAFETY_HOLD` 유지. 운영 주문/배포/파일·보호 계약 변경 금지.

## 실행 한도 종료 시 필수 증거

- `EXECUTION_LIMIT`로 끝날 때는 D00 §4 형식의 `LIMIT_TYPE | EVIDENCE | LAST_DONE | NOT_DONE | NEXT`를 **실제 제한 신호 기준**으로 함께 남긴다. 제한값·원인 불명은 `UNKNOWN/NOT_VERIFIED`, 추정한 시간·호출수·크레딧을 사실처럼 쓰지 않는다. 가능한 READY RF가 남으면 첫 작업 완료만으로 종료하지 않는다. 한도 도달 전에 이미 분류한 RF·A/B 신규 배정 델타와 미처리 첫 RF·담당을 반드시 구분한다. **단순 HANDOFF 대기 또는 새 증거 없음은 EXECUTION_LIMIT 사유가 아니다.**

## 절대 운영 규칙·현재 스냅샷

- RF 원본의 원래 C1~C5 및 실제 미체크 항목이 정본. C03은 **권고/배정만**, C05만 RF 체크·물리 이동·STATUS/C7, C04만 선별 통합/CI. 같은 SOURCE·동일 범위의 성공 검증 재실행 금지. Owner 주장·정적 parity·독립 peer·CI·운영 실검증은 다른 증거다.
- BLOCKED면 첫 원래 부족 조건/보호 사유와 해제 담당만 남기고 다음 안전 RF로 진행. RF-069/032/034·RunLab 보호 범위를 다른 일반 RF로 확산하지 않는다.
- **실물 STATUS 기준:** RF 93 = PENDING **51** / DEV **9** / PEER **14** / LEAD **0** / DONE **19** / REWORK **0**. 우선 14건 DEV 2 + PEER 12. 직전 C03의 LEAD 3/DONE 16 스냅샷은 C05 완료로 대체됐다. **이번 C03은 RF 체크·실물 이동·통합·DONE 0건**.
