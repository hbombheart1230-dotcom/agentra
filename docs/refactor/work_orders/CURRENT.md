# Agentra CURRENT — P1.5 전체 리팩터링

> 새 세션: CURRENT → 내 RF 작업 링크. 동일 세션에서 문서 내용/SHA 불변이면 재독하지 않는다.

- **전체:** 3985파일 / 298폴더, 루트 10개 + 루트 파일, libs 26패키지.
- **[상황판](../plan/STATUS.md):** 독립 RF 93개 · 검증 대기 0건 · 최종 DONE 0건(기존 일부 구현은 검증 필요) · [전수 단독 소유권](../plan/FILE_COVERAGE_63182ab2.csv).
- **기존 P1.5.0~11:** [12개 최종 합격 기준](../plan/criteria/)이며 작업 순서가 아니다.
- **역사적 고정 출처(비활성):** `DOC-A` · `DOC_FREEZE` · `P1.5.2 OPEN` · `P1.5.3`는 과거 단계 provenance다. `Issue #20`의 역사 기록 및 Issues #16–#19 CLOSED는 유지하지만 현재 RF93 배정·완료 권한은 오직 CURRENT가 가진다. 기존 기록을 신규 작업으로 재활성화하지 않는다.
- **기준 SHA (2026-10-23):** 검증된 integration `b768b2b3`(필수 6/6 PASS), A `a21401db`, B `a3d60e37`, PR31 stage `8b98fe74`. **4-HEAD 합성 후보 [`d73be191`](https://github.com/hbombheart1230-dotcom/agentra/commit/d73be1916b7a8adaea5e4419092e808cc5d9588d)** (기존 `stage/p15-four-branch-consolidation-20261023`, 현재 보존 태그 `archive/p15-20261023/stage-p15-four-branch-consolidation-20261023`)는 120 변경 경로를 보존했으나 신설 SHA normal/-O, 독립 상대 CLI, Actions 아직 NOT_RUN이므로 `SOURCE_ADMISSION_PENDING`.

| 담당 | 이번 할 일·파일 링크 |
|---|---|
| Claude A (`C:\Users\홍훈\Agentra-P15\dev-a`) | [RF-013 Reporter](../plan/pending/RF-013.md) · [RF-018 Strategist](../plan/pending/RF-018.md) · 기존 후보 먼저 재사용 |
| Codex B (`C:\Users\홍훈\Agentra-P15\dev-b`) | [RF-001 Operator UI](../plan/pending/RF-001.md) · [RF-020 Monitor](../plan/pending/RF-020.md) · [구 브랜치 원격 삭제 확인·종료 검증](../plan/troubleshooting/open/P15_BRANCH_CLEANUP.md) |
| 독립 검증 대기 | [Claude 구현 → Codex 검증](../plan/verification/claude/) · [Codex 구현 → Claude 검증](../plan/verification/codex/) · 현재 0건(정확한 구현 SHA 및 인수인계 확인 후 CURRENT에서 배정) | 
| 지팀장 GPT | 합성 후보 `d73be191` 소스·호환성 독립 검증 → [A/B/PR31 수용·통합·CI](../plan/troubleshooting/open/P15_SOURCE_ADMISSION.md). 4-HEAD 역사 합성은 완료, integration 소스 수용은 미완료. 다음 RF 배정·완료 판정 |

- **3단계 RF 흐름:** [pending](../plan/pending/) → [verification/claude](../plan/verification/claude/) 또는 [verification/codex](../plan/verification/codex/) → [done](../plan/done/). 검증 폴더는 **구현자 기준**이며 반대편이 독립 검증한다. RF 원본에 BASE/후보 SHA, 작업 경계, normal/`python -O` 테스트·exit, 패치노트, HOLD를 기록하고 이동 시 상대 링크를 보정한다. 인수인계·self PASS만으로 DONE 아님; GPT/승인된 publisher만 공용 상태를 반영한다.
- **신규 RF 검증자 통합/CI 위임:** Claude 작성 RF는 Codex, Codex 작성 RF는 Claude가 독립 검증한다. 실제 PASS 이후 **읽기 전용 리뷰와 분리된 통합 단계**에서 검증 담당자가 승인된 RF 경로만 최신 HEAD·단일 writer/CAS 조건으로 `integration/p1.5`에 제한 반영하고, **그 통합 SHA**의 normal/`python -O` 관련 회귀·필수 Actions 결과(URL/PASS/FAIL/NOT_RUN)를 RF에 남겨 GPT에게 보고한다. 충돌·소유권 위반·잠금 불명·CI FAIL/PENDING이면 `INTEGRATION_BLOCKED/CI_PENDING`으로 멈춘다. **GPT만** `verification → done` 최종 이동한다. 기존 합성 후보 `d73be191`/PR31의 GPT source-admission/CI 게이트, main·실거래·안전 권한은 위임하지 않는다. **문서만 수정한 이번 운영정책 개정 때문에 개발자가 별도 수동 full CI를 돌릴 필요는 없다.**
- **브랜치 정책 ([D00](../../ENGINEERING_DELIVERY_POLICY.md)):** 상시 `main` / `integration/p1.5` / Claude A / Codex B **4개 유지**. 설계 브랜치는 이미 통합돼 삭제됐고, stage `d73be191`·`8b98fe74`는 정확한 원격 보존 태그 확인 후 브랜치를 정리했다. **미수용 코드 후보는 검증/CI가 끝난 게 아니며** 현재 GPT source-admission 게이트가 유지된다. 신규 RF별 브랜치 생성 금지; 필수 격리 예외만 승인·정리 조건을 명시한다.\n- **트리거 결정 대기:** 2시간 예약 vs GitHub 이벤트는 **NOT_ENABLED/미확정**. 트리거는 CURRENT 확인 신호이지 배정 권한이 아니며 (RF, 역할, SHA) 중복 실행 및 누락 작업 재조회가 필수다.
- **예약 작업:** 매 실행 시 로컬 작업장 또는 클라우드 GitHub checkout에서 원격 `origin/integration/p1.5`의 **CURRENT만 최신으로 확인**한다. D00/D01/D02·원본 패킷은 최초 또는 변경·충돌·안전 불확실 시에만 재독한다. CURRENT에 배정된 **RF 전부 + 일회성 정리**를 빠짐없이 순회하며 각 건의 `수행/검증 대기/BLOCKED/NO_WORK`를 보고한다. 1건 정체로 전체 실행 종료 금지; 다른 RF 소유 파일은 건드리지 않는다.
- **CI 기준 회복:** 이전 [문서 CI 충돌](../plan/troubleshooting/open/P15_DOC_CI_COMPAT_20261023.md)은 `b768b2b3`에서 필수 GitHub Actions **6/6 PASS**로 회복. **새 합성 후보 `d73be191`의 소스 수용은 별개**이며 current-stage 구조 게이트, normal/`python -O`, 반대 CLI 독립 검토, exact-SHA hosted CI 확인 전 `integration/p1.5`에 코드 반영·기존 브랜치 삭제 금지.
- **확인할 문제:** [RF-020/001 범위·예약 실행 조기 종료](../plan/troubleshooting/open/P15_RF020_SCOPE_AND_BATCH_SCHEDULER_20261023.md) (RF-010/026/075 공유 경계와 브랜치 정리 점검).
- **다음:** [RF-022 Commander](../plan/pending/RF-022.md) 등 P1~P2 큰 독립작업을 상황에 따라 1~5개 이상 가변 배정. 파일 중복 수정 금지.
- **완료:** 실제 source SHA·normal/`python -O`·상대 CLI 또는 증거 있는 원격 독립 검증 PASS·검증자 제한 통합·그 SHA CI PASS → GPT 최종 검토 후 done 이동.
- **운영:** [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D01](../../../AGENTS.md) · [D02](../../../CLAUDE.md) · [기존 전체 로드맵](../p1_5_p1_6_master_plan.md).
- **금지:** main·실거래·안전 권한 임의 변경, 과거 BATCH/T00 재활성, 검증 없는 병합, #20 댓글 남발.
