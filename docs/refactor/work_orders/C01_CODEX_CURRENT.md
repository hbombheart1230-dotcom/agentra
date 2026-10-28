# C01 — Codex B · 코드/독립 peer만

1. **읽기:** **RF 탐색은 [D00 §1.1](D00_ENGINEERING_DELIVERY_POLICY.md)의 `integration/p1.5` 큐에서 번호로 유일 경로를 찾은 다음, 원래 `실제 작업 목표→독점 파일 범위→선행 조건→DONE 체크`를 읽는다.**  [D00](D00_ENGINEERING_DELIVERY_POLICY.md) → [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12)의 자기 최신 댓글/중단점 → 필요할 때 [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11)의 대응 peer 결과 → **지금 작업할 RF 원본**. HEAD·소유권만 새로 확인. HANDOFF·STATUS 전체 재독 금지.
2. **실행:** B 브랜치 `work/p15-b-operator-structure-20261022`에서 **소스 코드·테스트만** 수정/검증/커밋/푸시. A 코드에 대한 독립 peer는 read-only로 수행. 출발 우선순위: **A RF-015→031의 미충족 full-peer 계약**, **B RF-065→063 Owner**, A RF-014/016/028/029/032/033/034/050 peer; 다음 B 안전 READY RF-044→045→024→010→011→059. 소유/CLAIM/보호 확인, 선행 작업 반복 금지.
3. **대기 금지:** 새로운 A SHA/지팀장 배정이 없어도 위 기존 미완료 RF를 계속 진행. 보호/환경 blocker는 첫 원래 C 한 개와 오류를 명시하고 다음 안전 작업으로 이동. 기존 scoped PASS ≠ full PASS.
4. **유일 보고:** 결과를 [Issue #12 댓글](https://github.com/hbombheart1230-dotcom/agentra/issues/12)로 `RF | OWNER/PEER | 정확 SOURCE_SHA | 수정 코드/테스트 경로 | 실제 normal/-O 결과 | 첫 미충족 C | PUSH VERIFIED/FAILED | NEXT`. **HANDOFF_B 및 다른 MD/CSV/patchnotes/큐/STATUS 수정 금지**. 문서 요청은 댓글로 지팀장에게 전달한다.

완료는 RF 수용 판정이 아니라 지팀장이 결정한다. 일반 개발은 자동 승인, 보호 실런은 별도 승인.
