# Agentra CURRENT — P1.5 전체 리팩터링

> 새 세션: CURRENT → 내 RF 작업 링크. 동일 세션에서 문서 내용/SHA 불변이면 재독하지 않는다.

- **전체:** 3985파일 / 298폴더, 루트 10개 + 루트 파일, libs 26패키지.
- **[상황판](../plan/STATUS.md):** 독립 RF 93개 · 최종 DONE 0건(기존 일부 구현은 검증 필요) · [전수 단독 소유권](../plan/FILE_COVERAGE_63182ab2.csv).
- **기존 P1.5.0~11:** [12개 최종 합격 기준](../plan/criteria/)이며 작업 순서가 아니다.
- **참고 SHA:** 기존 integration `63182ab2`, A `a21401db`, B `a3d60e37`, PR31 `8b98fe74` (작업 시 HEAD 재확인).

| 담당 | 이번 할 일·파일 링크 |
|---|---|
| Claude A | [RF-013 Reporter](../plan/pending/RF-013.md) · [RF-018 Strategist](../plan/pending/RF-018.md) · 기존 후보 먼저 재사용 |
| Codex B | [RF-001 Operator UI](../plan/pending/RF-001.md) · [RF-020 Monitor](../plan/pending/RF-020.md) · [구 브랜치 안전 정리](../plan/troubleshooting/open/P15_BRANCH_CLEANUP.md) |
| 지팀장 GPT | [A/B/PR31 선별 수용·통합·CI](../plan/troubleshooting/open/P15_SOURCE_ADMISSION.md), 다음 RF 배정·완료 판정 |

- **다음:** [RF-022 Commander](../plan/pending/RF-022.md) 등 P1~P2 큰 독립작업을 상황에 따라 1~5개 이상 가변 배정. 파일 중복 수정 금지.
- **완료:** 실제 source SHA·normal/`python -O`·상대 CLI PASS·지팀장 선별 통합·그 SHA CI PASS → GPT만 done 이동.
- **운영:** [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D01](../../../AGENTS.md) · [D02](../../../CLAUDE.md) · [기존 전체 로드맵](../p1_5_p1_6_master_plan.md).
- **금지:** main·실거래·안전 권한 임의 변경, 과거 BATCH/T00 재활성, 검증 없는 병합, #20 댓글 남발.
