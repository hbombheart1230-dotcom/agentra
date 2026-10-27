# C05 — 지팀장③ 최종 인수·원본 RF/STATUS·DONE
> 현재 노트 · 예약 직접 진입 파일 · 권장 시작 매시 50분 · `integration/p1.5`

**상위 공통 규칙:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md). 구 `CURRENT.md`를 진입점으로 사용하거나 자동 갱신하지 않는다.

## 이번 역할의 목표·단독 쓰기 권한
- **RF의 C1~C7 체크·물리 단계·STATUS·LEAD_CURRENT 정합성과 DONE 최종 책임자.** C03의 `LEAD_READY`와 C04의 통합/CI 장부를 인수하되, **실제 증거/SHA/원래 RF 게이트**를 직접 판단한다.
- 수정: **C05**, 해당 **원본 RF 체크·증거 메타·실물 이동**, [STATUS](../plan/STATUS.md), [LEAD_CURRENT](../plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md), 관련 상태/CSV 정합성만. `D00`·A/B 소스·C01/C02/C03/C04·통합 소스는 수정하지 않는다.
- **중요:** 최종 승인자는 한 명(C05)이다. C03의 권고는 PASS 선언이 아니고, C04의 CI 기록은 C7 완료가 아니다.

## 매회 실행 순서
1. **DONE 가능한 것부터:** 물리 LEAD 후보에 대해 C04의 `SOURCE SHA → integration SHA → CI` 신규 증거를 확인한다. 원래 C1~C5가 이미 유효하고 **C6 MET**(필수 CI PASS 또는 근거 있는 NOT_REQUIRED 포함)가 되면 **이 C05 회차에 C6 체크 + C7 이동/STATUS까지 완료**한다. 별도 승인 대기 회차를 만들지 않는다.
2. **새 LEAD 진입 판정:** C03 제안 및 A/B 새 HANDOFF를 보고, 해당 원본 RF의 **C1~C5 전체 MET/적법 N/A + 정확 SOURCE SHA에 반대 peer 원래 전체 범위 PASS**를 확인한 경우에만 `03_PEER_REVIEW → 04_LEAD_ACCEPTANCE` 실물 이동. C04가 다음 예약에서 C6를 수행하도록 인수 정보를 남긴다.
3. **DEV/PEER 경로 정리:** Owner가 C1~C3/해당 C5 완료 주장·근거를 제출했을 때만 `02_DEVELOPING → 03_PEER_REVIEW`. 신규 누락은 최초 C 하나와 Owner/Peer를 적어 적합한 DEV/PEER에 남기거나 반환한다. 직접적 신규 회귀/원래 계약 위반에 한정해 `06_REWORK` 심사.
4. **체크 진실성:** 원본 `## DONE 체크` 7항목은 실제 근거가 확인된 `MET`/적법 `N/A`만 체크. 체크가 빈 경우 과거 Owner/peer 제출을 1회 대조하되 자동 PASS 금지. `SCOPED_PASS`와 `SAFETY_BLOCKED`가 남으면 DONE·LEAD 진입 불가.
5. **상태 쓰기 원자성:** 파일을 정확한 Owner/실물 큐 한 곳에만 두고, 체크·SOURCE SHA·peer·안전 사유·LEAD/DONE/REWORK를 정리한 뒤 `python docs/refactor/tools/sync_rf_checklist_status.py --write` → `--check` 실행. 동기화 자체는 PASS 승인 아님. **STATUS의 링크·카운트·NEXT 및 LEAD_CURRENT**를 바뀐 RF에 한정해 함께 맞춘다.
6. 다른 예약의 HEAD/문서 변경과 경합 시 안전한 최신 HEAD에 재적용한다. 커밋이나 예약 횟수를 DONE으로 세지 않는다. 완료할 수 없으면 `RF | 첫 blocker | 해제 담당 | NEXT` 기록하고 다음 정상 RF로 이동.

## 시작 스냅샷 (2026-10-27 STATUS; 실제 변경 사항이 있으면 갱신)
- **전체 93건:** PENDING 51 / DEV 9 / PEER 14 / LEAD 3 / DONE 16 / REWORK 0. 과거 'LEAD 14'는 반환된 **DEV 2 + PEER 12** 이력이며 현재 LEAD 실물 0.
- **우선 14:** RF-063·065 DEV(B), RF-067·069 PEER(B), RF-014·015·016·028·029·031·032·033·034·050 PEER(A). 기존 STATUS 기준 **MET 4 / N/A 14 / 미완료 80**(총 98 체크). 미완료 원래 체크는 조건이 해제되기 전까지 추측으로 메우지 않는다.
- **이미 종결:** RF-043/053 `KEEP_VERIFIED` DONE; B 독립 peer exact source와 integration offline safety CI 근거를 활용해 완료됨. 다시 이동/재실행하지 않는다.
- C04가 인수할 실물 LEAD 3건: RF-052 수정 통합, RF-046/047 KEEP CI. C6/DONE 아직 아님. **C03 권고가 와도 C05가 먼저 엄격히 LEAD 게이트를 확인**한다.

## RunLab 관련 RF 상태
- RunLab #32 사건 접수·A/B 배정은 C03, 원본 운영 증상과 승인 전 read-only 관측은 별도 RunLab 담당. C05는 **RF 소유/단계/STATUS에 실제 새 변화가 있을 때만** 반영한다.
- 적용 이미지 `RUN_SOURCE_SHA=UNKNOWN`, `DEFECT_OWNER_PENDING`이면 실제 런 원인 확정/운영 종결 금지. 개발 RF DONE(`DEV_RESOLVED`)과 사건 `RUNTIME_VERIFIED`를 합치지 않는다. 무관한 RF 종결은 계속한다.

## 금회 인수·종결 장부 (실제 변경분만)
| RF | Owner SOURCE SHA·반대 peer | C1~C5 게이트 | C04 integration SHA·CI | 물리 이전→이후 | C6/C7·STATUS | NEXT |
|---|---|---|---|---|---|---|
| RF-052 | A receipts@10283d8f, B 40/40 + Windows | C1~C4 MET, C5 N/A | C04 integration/CI PENDING | PEER→LEAD | C6/C7 PENDING | C04 통합/CI → C05 DONE |
| RF-046 | A/B/int 2 owner 동일, B 63/63 | C1~C4 MET, C5 N/A | C04 KEEP/CI PENDING | PEER→LEAD | C6/C7 PENDING | C04 CI → C05 DONE |
| RF-047 | A/B/int 4 owner 동일, B 63/63 | C1~C4 MET, C5 N/A | C04 KEEP/CI PENDING | PEER→LEAD | C6/C7 PENDING | C04 CI → C05 DONE |

**다음 실행:** C04의 RF-052/046/047 C6 완료 후보 **즉시 DONE**, 다음 C03의 전체 수용 범위 충족 후보 **LEAD 실물 이동**, 변경 RF 정합성만 갱신. 보고: `RF | OWNER/PEER SHA | C1~C5 | integration SHA·CI | DONE/LEAD/BLOCKED | STATUS/queue | NEXT`.
