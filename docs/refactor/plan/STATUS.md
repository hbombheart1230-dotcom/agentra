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
| Claude A | `a03102dd52eb9ee70df84b909411d480e8e8db3a` (역할문서-only; 최신 원개발 fixture SHA `7797b793`) | [#11 run139](https://github.com/hbombheart1230-dotcom/agentra/issues/11): RF-028 in-process writer fake, RF-014 Top1 selected fixture, RF-034 schema-valid source fixture 추가. B의 신규 scoped peer 결과는 #12에 도착; 최종 RF 게이트/LEAD 판정 필요. 운영 source 변경 0. RF-030 frozen oracle 보호 HOLD |
| Codex B | `47d6e04d013dbed26d39e395e3ae707337508c51` (역할문서-only; 최신 peer SHA `2e2d24d6`) | [#12](https://github.com/hbombheart1230-dotcom/agentra/issues/12): RF-031 downstream JSON-only 복구·RF-050 cache reload·RF-014 selected Top1·RF-028 in-process writer·RF-034 valid source·RF-033 corrupt partial consumer 추가 scoped peer normal/`-O` 결과. RF-063 NameError는 현재 B source에서 미재현 보고(원 SHA 비교 필요). **운영 source 변경 0, 전체 DONE 아님** |

작업 연결: **D00 = 상시 관리·검증 계약**, C00 = 지팀장 이번 작업, C01/C02 = 각 개발자 다음 실행 큐, HANDOFF·#11/#12 = 증거·선택한 다음 RF. 기존 Issue 본문의 과거 작업 브랜치는 현재 D/C보다 우선하지 않는다. 문서·fixture 진척을 RF DONE으로 계산하지 않는다.

## LEAD 14 — 최초 남은 해제 경계

| RF | 지금 남은 실행·담당 |
|---|---|
| 014 | A selected Top1 fixture로 **B scoped peer 완료**; 실 runtime Graph/NOOP 전체 소비자 게이트는 지팀장 재판정 |
| 015 | Monitor 역사 11 BASE FAIL 분리, B-only 2파일 소비자 근거 **B** → 새 근거에 **A peer** |
| 016 | facade 예외 transparency 범위 수용, nested State 예외 projection **B** |
| 028 | A in-process fake로 **B writer scoped peer 완료**; 실제 외부 rich schema 소비자·fail-open 영향 판정 필요 |
| 029 | external truth-root 실제 읽기/실패·State 예외 **B** |
| 031 | B downstream JSON-only 복구 scoped peer 보고; 실제 caller·State 최종 소비자 및 재현 하네스 검토, pytest 부재는 ENV |
| 032 | Stage2 부분 OSError scoped 수용, validation_id trust / Exit Horizon **B**; 보호 UEF는 사용자 승인 |
| 033 | B published corrupt partial JSON consumer fail-closed scoped peer 보고; 실제 producer/consumer 최종 게이트 판정 |
| 034 | A valid source fixture로 **B scoped peer 완료**; casebook→Scanner/cache 전체 소비자 추가 확인. 보호 closeout만 별도 보호 승인 |
| 050 | B temp cache 저장→reload scoped peer 완료; 모델 fallback·State 최종 게이트 판정 |
| 063 | A pinned BASE에서 `day` NameError 재현, B 현 source에서는 미재현 보고. **B Owner가 정확 SHA·BASE 차이 확인 후 일반 RF로 즉시 보완**, A 독립 peer. Windows·운영 경로 보호 유지 |
| 065 | 안전 Linux peer 소진; 실데이터·Windows Scheduler·보호 CLI 별도 안전 환경/승인 필요 |
| 067 | 안전 delegated target peer 소진; Windows PowerShell·보호 preflight/UEF 경계 환경/승인 필요 |
| 069 | historical UEF5 snapshot **path/SHA/use-scope 승인 전 SAFETY_HOLD** |

기존 valid normal/`-O`·CI는 정확 source/test/workflow tree에 한해 재사용한다. 신규 CI 실행 **NOT_RUN**. 기존 확인 Safety SUCCESS `40332899631@0da98a47`, Web SUCCESS `40073316192@1374d371`은 다른 SHA의 전체 PASS 근거가 아니다.

## RunLab·안전 / 남은 조치

- [#32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 마지막 인수: **2026-10-27 09:38 KST**. mock SELL `0045749` 체결·보유 출처 UNKNOWN, 전일 SELL `0020349` 로컬 누락·출처 UNKNOWN, broker/local·guard·Reporter 불일치 및 OCI `RUN_SOURCE_SHA=UNKNOWN` 유지. 런타임 버전별 **BLOCKED**; 운영 주문·재배포·안전 계약 변경 금지.
- **일반 RF 전 범위 개발은 포괄 허용:** A/B는 배정·자율 CLAIM한 일반 RF를 별도 사용자·지팀장 승인 대기 없이 구현·검증·커밋·푸시한다. 지팀장은 독립 검증을 인수해 최종 DONE 및 Owner 동기화만 수행한다. 보호 구간은 D00의 별도 명시적 승인 전 HOLD.
- 지팀장 다음 행동: B `2e2d24d6`의 새 scoped peer·A `7797b793` fixture를 영향 RF에서 직접 재판정하고, 가능하면 DONE 처리. 매 예약 RF 실물 큐·A/B HEAD·HANDOFF·#11/#12와 이 STATUS를 대조하여 변화 있는 항목만 갱신한다. **이번 회차는 운영 소스·RF 물리 이동·테스트 실행 없이 정책 문서 동기화만 수행**.
