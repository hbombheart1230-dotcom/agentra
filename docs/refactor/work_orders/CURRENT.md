# Agentra CURRENT — P1.5 전체 리팩터링

> 새 세션: CURRENT → 내 RF 작업 링크. 동일 세션에서 문서 내용/SHA 불변이면 재독하지 않는다.

- **전체:** 3985파일 / 298폴더, 루트 10개 + 루트 파일, libs 26패키지.
- **[상황판](../plan/STATUS.md):** 독립 RF 93개 · 최종 DONE 0건(기존 일부 구현은 검증 필요) · [전수 단독 소유권](../plan/FILE_COVERAGE_63182ab2.csv).
- **기존 P1.5.0~11:** [12개 최종 합격 기준](../plan/criteria/)이며 작업 순서가 아니다.
- **역사적 고정 출처(비활성):** `DOC-A` · `DOC_FREEZE` · `P1.5.2 OPEN` · `P1.5.3`는 과거 단계 provenance다. `Issue #20`의 역사 기록 및 Issues #16–#19 CLOSED는 유지하지만 현재 RF93 배정·완료 권한은 오직 CURRENT가 가진다. 기존 기록을 신규 작업으로 재활성화하지 않는다.
- **참고 SHA:** 기존 integration `63182ab2`, A `a21401db`, B `a3d60e37`, PR31 `8b98fe74` (작업 시 HEAD 재확인).

| 담당 | 이번 할 일·파일 링크 |
|---|---|
| Claude A (`C:\Users\홍훈\Agentra-P15\dev-a`) | [RF-013 Reporter](../plan/pending/RF-013.md) · [RF-018 Strategist](../plan/pending/RF-018.md) · 기존 후보 먼저 재사용 |
| Codex B (`C:\Users\홍훈\Agentra-P15\dev-b`) | [RF-001 Operator UI](../plan/pending/RF-001.md) · [RF-020 Monitor](../plan/pending/RF-020.md) · [구 브랜치 원격 삭제 확인·종료 검증](../plan/troubleshooting/open/P15_BRANCH_CLEANUP.md) |
| 지팀장 GPT | [A/B/PR31 선별 수용·통합·CI](../plan/troubleshooting/open/P15_SOURCE_ADMISSION.md), 다음 RF 배정·완료 판정 |

- **예약 작업:** 매 실행 시 각 로컬 작업장에서 원격 `origin/integration/p1.5`의 **CURRENT만 최신으로 확인**한다. D00/D01/D02·원본 패킷은 최초 또는 변경·충돌·안전 불확실 시에만 재독한다. CURRENT에 배정된 **RF 전부 + 일회성 정리**를 빠짐없이 순회하며 각 건의 `수행/검증 대기/BLOCKED/NO_WORK`를 보고한다. 1건 정체로 전체 실행 종료 금지; 다른 RF 소유 파일은 건드리지 않는다.
- **CI 차단:** [최신 integration CI 1/5 PASS 및 역사 고정 게이트 충돌](../plan/troubleshooting/open/P15_DOC_CI_COMPAT_20261023.md) — 패치노트 필수 필드 보정, 기존 CI 계약은 완화 없이 검토.
- **확인할 문제:** [RF-020/001 범위·예약 실행 조기 종료](../plan/troubleshooting/open/P15_RF020_SCOPE_AND_BATCH_SCHEDULER_20261023.md) (RF-010/026/075 공유 경계와 브랜치 정리 점검).
- **다음:** [RF-022 Commander](../plan/pending/RF-022.md) 등 P1~P2 큰 독립작업을 상황에 따라 1~5개 이상 가변 배정. 파일 중복 수정 금지.
- **완료:** 실제 source SHA·normal/`python -O`·상대 CLI PASS·지팀장 선별 통합·그 SHA CI PASS → GPT만 done 이동.
- **운영:** [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D01](../../../AGENTS.md) · [D02](../../../CLAUDE.md) · [기존 전체 로드맵](../p1_5_p1_6_master_plan.md).
- **금지:** main·실거래·안전 권한 임의 변경, 과거 BATCH/T00 재활성, 검증 없는 병합, #20 댓글 남발.
