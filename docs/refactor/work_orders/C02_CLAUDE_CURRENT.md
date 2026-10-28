# C02 — Claude A · 코드/독립 peer만

1. **진입:** [D00 §1.1](D00_ENGINEERING_DELIVERY_POLICY.md) → [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11)의 자기 최신 댓글/중단점 → 필요할 때 [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12)의 대응 peer 결과 → **지금 작업할 RF 원본**. HANDOFF·STATUS 전체 재독 금지.
2. **실행:** A 브랜치 `work/p15-a-reporter-pure-20261021`에서 **소스 코드·테스트만** 수정/검증/커밋/푸시. B 독립 peer는 read-only. **(1) RF-040·061 Owner (CLAIM 2/2):** A `b4cb5878`까지 test-only normal/-O 근거를 재사용; C1 RF-040 shadowed `executor.py` KEEP/삭제 판단과 RF-061 두 ToolFacade 계약을 증거로 제시, C2/C3는 RF-040 executor_agent 및 RF-061 Step5C 보호 범위만 SAFETY_HOLD, B C4 peer 대기. **(2) RF-045 신규 B source `85d5332d`/`http_client.py` blob `824d7c8f`를 독립 temp/mock normal/-O peer**, injected session vs requests 부재 fail-closed와 기존 소비자/예외·효과 범위 확인, 원격 B exact SHA 보고. **(3) RF-031:** A `b4cb5878`의 writer+caller 15 PASS를 재사용, 미검증 live caller는 실행하지 말고 read-only 호출/State 경계만 정리하여 B full peer에 전달. **(4) RF-015:** #11 `6458324310`의 역사 11 FAIL 분류를 B에 전달, 기존 253/11 전체 재실행 금지. 이후 B RF-065/063/066/070/071의 새로운 안전 peer 경계. RF-036→037→039→038은 C05가 CLAIM 슬롯을 해제한 후만. 새 SHA 없어도 남은 안전 C1/C2/C4를 수행하고 `NO_DELTA`로 중단하지 않는다.
3. **연속 실행:** 첫 1건·새 B SHA·새 지팀장 배정에서 멈추지 말고 실행 가능한 동안 다음 미완료 RF/안전 READY까지 처리. 한 경계가 보호/환경 BLOCKED면 다음 안전 작업. RF-061 Step5C·RF-057 보호 인접/UEF 실런은 임의 실행 금지.
4. **유일 보고:** 실제 작업 결과·코드 SHA가 새로 생겼을 때만 [Issue #11 댓글](https://github.com/hbombheart1230-dotcom/agentra/issues/11)로 `RF | OWNER/PEER | 정확 SOURCE_SHA | 수정 코드/테스트 경로 | 실제 normal/-O 결과 | 첫 미충족 C | PUSH VERIFIED/FAILED | NEXT`. **HANDOFF_A 및 다른 MD/CSV/patchnotes/큐/STATUS 수정 금지**. 필요한 문서/patchnotes는 지팀장 요청 댓글.

**이 C02의 다음 RF·우선순위 갱신은 C03 지팀장만 한다.** A는 매회 최신 C02와 실제 RF 큐를 재조회하되 이 문서를 수정하거나 C03 갱신을 기다려 개발을 멈추지 않는다.

Owner/peer 증거의 수용·실물 이동/DONE은 지팀장 권한이다.
