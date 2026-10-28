# C02 — Claude A · 코드/독립 peer만

1. **읽기:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) → [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11)의 자기 최신 댓글/중단점 → 필요할 때 [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12)의 대응 peer 결과 → **지금 작업할 RF 원본**. HANDOFF·STATUS 전체 재독 금지.
2. **실행:** A 브랜치 `work/p15-a-reporter-pure-20261021`에서 **소스 코드·테스트만** 수정/검증/커밋/푸시. B 코드 독립 peer는 read-only. 우선순위: **A RF-040·061 원래 C2/C3 (CLAIM 2/2)**, **B RF-065·063 및 066/070/071의 안전한 독립 peer**, A RF-015·031의 B가 지적한 실제 C 간극. 다음 A 안전 READY RF-036→037→039→038은 CLAIM 슬롯이 비었을 때.
3. **대기 금지:** 새로운 B SHA/지팀장 배정이 없어도 원래 미완료 RF/안전 READY 진행. 한 경계가 보호/환경 BLOCKED면 다음 안전 작업. RF-061 Step5C·RF-057 보호 인접/UEF 실런은 임의 실행 금지.
4. **유일 보고:** 결과를 [Issue #11 댓글](https://github.com/hbombheart1230-dotcom/agentra/issues/11)로 `RF | OWNER/PEER | 정확 SOURCE_SHA | 수정 코드/테스트 경로 | 실제 normal/-O 결과 | 첫 미충족 C | PUSH VERIFIED/FAILED | NEXT`. **HANDOFF_A 및 다른 MD/CSV/patchnotes/큐/STATUS 수정 금지**. 필요한 문서/patchnotes는 지팀장 요청 댓글.

Owner/peer 증거의 수용·실물 이동/DONE은 지팀장 권한이다.
