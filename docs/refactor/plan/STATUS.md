# Agentra P1.5 — STATUS (현재 상태)

**정본:** `integration/p1.5:docs/refactor/work_orders/CURRENT.md`(C00), 고정 계약 [D00](../work_orders/D00_ENGINEERING_DELIVERY_POLICY.md), 개발 큐 C01/C02. A/B 실제 작업 근거는 각 브랜치의 HANDOFF 및 [#11](https://github.com/hbombheart1230-dotcom/agentra/issues/11)/[#12](https://github.com/hbombheart1230-dotcom/agentra/issues/12), 런검증은 [#32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). 지팀장이 매 예약 현재 상태를 대조·필요 시 갱신한다.

## RF 큐·검증 범위

| PENDING | DEVELOPING | PEER | LEAD | DONE | REWORK | 합계 |
|---:|---:|---:|---:|---:|---:|---:|
| 61 | 3 | 1 | 14 | 14 | 0 | **93** |

**이 집계는 직전 정본의 보고값**이며, 이번 문서 정합성 수정에서는 RF-001~093 원격 실물 경로 전수 집계를 재실행하지 않았다(`PHYSICAL_QUEUE_NOT_VERIFIED`). 신규 DONE **확인 0**, integration 운영 소스 통합 **0**. LEAD: **014/015/016/028/029/031/032/033/034/050/063/065/067/069**. Scoped peer PASS를 전체 DONE으로 승격하지 않는다.

## 최신 A/B 인수 (2026-10-27 확인)

| 담당 | 확인 브랜치 HEAD | 새 근거·다음 행동 |
|---|---|---|
| Claude A | `7797b7937e6e1e2065b32836d8ef8dfa5ca6cd60` | [#11 run139](https://github.com/hbombheart1230-dotcom/agentra/issues/11): RF-028 in-process writer fake, RF-014 Top1 selected fixture, RF-034 schema-valid source fixture 추가. A 보고 normal/`-O` 안전 4모드; **B 독립 peer 필요**. 운영 source 변경 0. RF-030은 frozen oracle 승인 HOLD |
| Codex B | `7f376b5afc3d43aff1478e7558e2e2deb6331b1e` | [#12 최신 체크포인트](https://github.com/hbombheart1230-dotcom/agentra/issues/12): 실제 검증 결과의 마지막 구현 근거는 `69b093e9`; 이후 `7f376b5a`는 루트 AGENTS 진입점 동기화. RF-050 cache / 016 예외 / 033 storage failure / 032 Stage2 부분 OSError scoped 증거. RF-014/028/034은 A 신규 fixture로 다음 독립 검증. 전체 DONE 아님 |

작업 연결: **D00 = 상시 관리·검증 계약**, C00 = 지팀장 이번 작업, C01/C02 = 각 개발자 다음 실행 큐, HANDOFF·#11/#12 = 증거·선택한 다음 RF. 기존 Issue 본문의 과거 작업 브랜치는 현재 D/C보다 우선하지 않는다. 문서·fixture 진척을 RF DONE으로 계산하지 않는다.

## LEAD 14 — 최초 남은 해제 경계

| RF | 지금 남은 실행·담당 |
|---|---|
| 014 | A selected Top1 fixture 이용한 runtime ranking/NOOP 경계 **B 독립 peer** |
| 015 | Monitor 역사 11 BASE FAIL 분리, B-only 2파일 소비자 근거 **B** → 새 근거에 **A peer** |
| 016 | facade 예외 transparency 범위 수용, nested State 예외 projection **B** |
| 028 | A in-process fake 이용 rich schema 실제 writer·소비자 **B peer** |
| 029 | external truth-root 실제 읽기/실패·State 예외 **B** |
| 031 | Reporter 부분 파일 실패 이후 downstream 복구 소비자, 재현 하네스·exit **B**; pytest 부재는 ENV |
| 032 | Stage2 부분 OSError scoped 수용, validation_id trust / Exit Horizon **B**; 보호 UEF는 사용자 승인 |
| 033 | provider/storage 실패 scoped 수용, published partial artifact 소비자 **B** |
| 034 | A valid source fixture로 casebook→Scanner/cache 소비자 **B peer**; 보호 closeout은 사용자 승인 |
| 050 | temp cache 산출 scoped 수용, cache reload 소비자 **B** |
| 063 | A CLI 독립 scoped 검증 인수; `run_m23_closeout_check` 기존 BASE `day` NameError는 B Owner 수정·A peer 필요. 실제 Windows/운영 경로 무단 실행 금지 |
| 065 | 안전 Linux peer 소진; 실데이터·Windows Scheduler·보호 CLI 별도 안전 환경/승인 필요 |
| 067 | 안전 delegated target peer 소진; Windows PowerShell·보호 preflight/UEF 경계 환경/승인 필요 |
| 069 | historical UEF5 snapshot **path/SHA/use-scope 승인 전 SAFETY_HOLD** |

기존 valid normal/`-O`·CI는 정확 source/test/workflow tree에 한해 재사용한다. 신규 CI 실행 **NOT_RUN**. 기존 확인 Safety SUCCESS `40332899631@0da98a47`, Web SUCCESS `40073316192@1374d371`은 다른 SHA의 전체 PASS 근거가 아니다.

## RunLab·안전 / 남은 조치

- [#32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 마지막 인수: **2026-10-27 09:38 KST**. mock SELL `0045749` 체결·보유 출처 UNKNOWN, 전일 SELL `0020349` 로컬 누락·출처 UNKNOWN, broker/local·guard·Reporter 불일치 및 OCI `RUN_SOURCE_SHA=UNKNOWN` 유지. 런타임 버전별 **BLOCKED**; 운영 주문·재배포·안전 계약 변경 금지.
- 지팀장 다음 행동: A `7797b793` fixture를 B peer 큐에 반영하고, 기존 B 신규 scoped 증거의 영향 RF를 직접 판정·가능한 DONE 처리. 다음 예약마다 RF 실물 큐·A/B HANDOFF·#11/#12와 이 STATUS를 대조해 실제 변화가 있는 항목만 갱신.
- 이번 승인 범위는 **D00·C00·STATUS 문서 관리 정합성**이다. RF 실물 이동·운영 소스·A/B 브랜치·런타임·예약 변경은 수행하지 않는다.
