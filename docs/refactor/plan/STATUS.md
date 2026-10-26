# Agentra P1.5 — STATUS (현재 상태만)

**정본:** `integration/p1.5`의 [CURRENT](../work_orders/CURRENT.md), 상시 정책은 [D00](../work_orders/D00_ENGINEERING_DELIVERY_POLICY.md). 2026-10-27 07시 KST 기준 원격 큐; 지난 회차 상세·명령·로그는 개별 RF와 Git 커밋 이력에 보존.

## 실물 현황

| PENDING | DEVELOPING | PEER | LEAD | DONE | REWORK | 합계 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 61 | 3 | 1 | 14 | 14 | 0 | **93** |

93개 RF는 각 1개 경로만 존재한다. 최근 LEAD 신규 DONE **0**, 신규 운영 소스 통합 **0**. 최근 반복 회차는 개별 RF의 scoped synthetic 증거를 보강했지만 **코드 진척으로 계산하지 않는다**. 최신 확인 A `3565cac5`(run132 HANDOFF/증거 3개만; 운영 소스 변화 0), B `c18ad0b0`(신규 없음). A의 RF-032 scorecard/cumulative writer 및 RF-034 scanner diagnostics normal/-O 성공은 **원개발자 scoped 증거**로만 분류; B 독립 peer·전체 owner 종결을 대신하지 않는다. 같은 테스트 재실행 금지.

**현재 LEAD:** RF-014/015/016/028/029/031/032/033/034/050/063/065/067/069. RF-069만 역사적 UEF5 승인 자료 부재의 `SAFETY_HOLD`; 나머지는 아래 **최초 미충족 게이트**가 있는 `HOLD/NOT_DONE`. 동일 증거 재실행 금지.

## LEAD 14건 — 최초 새 해제 게이트만

| RF | 미충족 소비자·효과·독립 검증 / 다음 실행 책임 |
| --- | --- |
| 014 | Scanner 실제 dynamic ranking/NOOP chain; B 독립 peer |
| 015 | Monitor 기존 11 FAIL의 BASE 동일 조건 원인·B-only 2파일 소비자; B |
| 016 | news-query→strategic_answers 실제 facade/State·예외; B 독립 peer |
| 028 | trade-report 정식 rich schema→read/render/writer 외부 소비자; B |
| 029 | story bundle v1/v2 및 external-root truth facade; B |
| 031 | Reporter 실 day-cache+8 writer·부분 OSError; B temp-only fake LLM |
| 032 | public `validation_id` 경계, Exit Horizon, scorecard→Stage2 부분 실패(B); cumulative 신규 writer(A); 보호 UEF 사용자 승인 |
| 033 | InputWorker→storage·Windows Thread 예외; A/B 신규 독립 경계 |
| 034 | casebook→Scanner와 latent producer cache/output-root; B, closeout 안전 범위 승인 |
| 050 | Operator 3-stage LLM primary/repair/line fallback·State; B 독립 peer |
| 063 | diagnostics effectful CLI·cp949/Windows·스케줄러; A/B |
| 065 | research effectful Stage2·scheduler·외부 IO; A/B |
| 067 | delegated diagnostics·Windows PATH/exit/fail-closed; B |
| 069 | 사용자/증거 소유자가 승인 historical UEF5 snapshot **path/SHA/use-scope** 제공 전 수행 금지 |

**통합 CI 인수 범위:** Safety SUCCESS `40332899631@0da98a47`와 `graphs/libs/scripts/tests/apps/.github` 대상 소스 tree 동일한 범위의 기존 normal/-O만 재사용. Web SUCCESS `40073316192@1374d371`와 `apps/web`·`apps/api`·Web workflow 동일 범위만 재사용. 문서-only HEAD에 CI를 실행했다고 주장하지 않는다. 실제 코드 수정이 생기면 그 SHA에서 필요한 새 검증을 실시.

## 실제 변경·미해결

- **개발 작업:** A run132가 RF-032 scorecard/cumulative·RF-034 scanner diagnostics를 완료해 반복 금지. A 다음 최초 경계는 RF-033 InputWorker→storage 소비자이며, 추가 증거만 늘리는 미검증 범위 확대를 멈추고 독립 B 결과/정확 승인된 구현 필요성을 확인한다. B는 RF-031 unstubbed 8-writer → RF-050 3-stage LLM → RF-016 dynamic facade → RF-032 Stage2 → RF-034 casebook. 안전한 실제 구현이 필요하면 사용자 승인 범위를 먼저 확인한다.
- **RunLab #32:** broker SELL `0020349` local 누락, BUY guard stale, Operator GREEN vs reconciliation mismatch, OCI 실행 SOURCE_SHA UNKNOWN. `SAFETY_HOLD`, 실제 운용/재배포·안전 수정 승인 전 금지.
- **troubleshooting:** open 4 (`BRANCH_CLEANUP`, `RF012_FINITE`, `RF020_SCOPE`, `SOURCE_ADMISSION`); closed 1 (`DOC_CI`). 해제 증거 없이 임의 이동하지 않는다.
- **브랜치:** 정상 작업 범위는 `main`(보호)/`integration/p1.5`/A/B, 합계 4개. 잔존 `lead/*` 3개는 각각 docs/RF 이력 중심이고 integration과 diverged; 삭제 전 고유 commit·백업·외부 사용/권한을 확인한다. 신규 lead 브랜치 생성 금지. 삭제 도구가 없어 이번 처리에서 원격 삭제는 `NOT_RUN`.
- **운영 문서 안정화:** CURRENT/STATUS 누적 회차 삭제, D00은 단일 규칙. 처리할 신규 변화가 없으면 `NO_DELTA`로 RF/문서/코드 쓰기를 모두 생략한다.
