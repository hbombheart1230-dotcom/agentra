# CURRENT — Agentra P1.5 단일 라우팅 인덱스

> 과거 C00 장문 상태표는 **2026-10-28부터 실행 지시 아님**. 여기에는 날짜별 기록/큐 수치를 다시 쌓지 않는다. 이전 이력은 Git history와 원본 Issue 댓글에서 확인한다.

**A/B 유일한 작업 진입점:** Codex B는 [C01](C01_CODEX_CURRENT.md), Claude A는 [C02](C02_CLAUDE_CURRENT.md) **각 한 파일만 먼저 읽고 그 회차의 구체 지시를 실행**한다. [D00](D00_ENGINEERING_DELIVERY_POLICY.md)의 RF·안전·권한·수용 판단은 지팀장 C03~C05가 수행하고 필요한 제약은 C01/C02에 직접 기재한다.

| 역할 | 실행 진입점 | 최근 보고/입력 |
|---|---|---|
| Codex B | [C01](C01_CODEX_CURRENT.md) | [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12) (자기 코드/독립 peer 댓글) |
| Claude A | [C02](C02_CLAUDE_CURRENT.md) | [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11) (자기 코드/독립 peer 댓글) |
| 지팀장 배정 | [C03](C03_LEAD_TRIAGE_CURRENT.md) | **#11·#12·#32의 최신 댓글만 입력** |
| 지팀장 통합·CI | [C04](C04_LEAD_INTEGRATION_CURRENT.md) | 동일 3 Issue / 실제 LEAD RF |
| 지팀장 체크·종결 | [C05](C05_LEAD_CLOSEOUT_CURRENT.md) | 동일 3 Issue / RF·[STATUS](../plan/STATUS.md) |
| RunLab | [런 검증 CURRENT](../../runtime/validation/CURRENT.md) | [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) |

지팀장의 판정 출력은 [Issue #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36). **문서/RF/STATUS/patchnotes 수정은 지팀장만**, A/B는 각 작업 브랜치의 소스 코드·테스트만 수정하고 각 자기 Issue에 결과 댓글. RunLab 실행/안전은 별도 R00/D04를 따른다. 구 A/B HANDOFF는 과거 기록으로만 보존.
