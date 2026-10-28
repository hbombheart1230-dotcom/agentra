# C01 — Codex B · 코드/독립 peer만

1. **진입:** [D00 §1.1](D00_ENGINEERING_DELIVERY_POLICY.md) → [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12)의 자기 최신 댓글/중단점 → 필요할 때 [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11)의 대응 peer 결과 → **지금 작업할 RF 원본**. HEAD·소유권만 새로 확인. HANDOFF·STATUS 전체 재독 금지.
2. **실행:** B 브랜치 `work/p15-b-operator-structure-20261022`에서 **소스 코드·테스트만** 수정/검증/커밋/푸시. A 독립 peer는 read-only. **우선 (1) RF-015:** A #11 `6458324310`의 역사 11 FAIL BASE/후보 node 분류를 exact 범위로 독립 판정하고 19-owner State/event/consumer 잔여 C1~C4만 처리(119 PASS 재실행 금지); **(2) RF-031:** A `b4cb5878`의 writer+caller 신규 테스트 15건과 22-owner caller/State/실패 경계 full peer(기존 8 PASS 반복 금지); **(3) B RF-065→063:** 각각 C1 54-owner/잔여 63-owner ACTION·효과/소비자 증거를 채운다. **B RF-045:** 원격 `85d5332d`의 `libs/core/http_client.py` blob `824d7c8f` 반영 확인, 10-owner C1~C3를 안전하게 보강하고 A exact-SHA peer 대기; **RF-044:** 16-owner C1 소비자 분류. RF-044/045는 현재 `01_PENDING/UNASSIGNED`이므로 C05 물리 CLAIM 전 임의 RF 이동·중복 Owner 변경 금지(지팀장 배정 B, Peer A). 이어 A RF-014/016/028/029/032/033/034/050 peer 및 안전 READY RF-024→010→011→059. 보호·중복 검증 금지.
3. **연속 실행:** 첫 1건·새 A SHA·새 지팀장 배정에서 멈추지 말고 실행 가능한 동안 다음 미완료 RF까지 처리. 보호/환경 blocker는 첫 원래 C 한 개와 오류를 명시하고 다음 안전 작업으로 이동. 기존 scoped PASS ≠ full PASS.
4. **유일 보고:** 실제 작업 결과·코드 SHA가 새로 생겼을 때만 [Issue #12 댓글](https://github.com/hbombheart1230-dotcom/agentra/issues/12)로 `RF | OWNER/PEER | 정확 SOURCE_SHA | 수정 코드/테스트 경로 | 실제 normal/-O 결과 | 첫 미충족 C | PUSH VERIFIED/FAILED | NEXT`. **HANDOFF_B 및 다른 MD/CSV/patchnotes/큐/STATUS 수정 금지**. 문서 요청은 댓글로 지팀장에게 전달한다.

**이 C01의 다음 RF·우선순위 갱신은 C03 지팀장만 한다.** B는 매회 최신 C01과 실제 RF 큐를 재조회하되 이 문서를 수정하거나 C03 갱신을 기다려 개발을 멈추지 않는다.

완료는 RF 수용 판정이 아니라 지팀장이 결정한다. 일반 개발은 자동 승인, 보호 실런은 별도 승인.
