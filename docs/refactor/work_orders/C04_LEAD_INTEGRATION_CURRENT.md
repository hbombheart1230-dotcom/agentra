# C04 — 지팀장 · 선별 통합/CI

**입력:** [Issue #11 Claude A](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [Issue #12 Codex B](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [Issue #32 RunLab](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 **새 댓글 delta만** → C05가 실제 `04_LEAD_ACCEPTANCE`로 이동한 RF. [D00](D00_ENGINEERING_DELIVERY_POLICY.md) 준수. [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)은 결과 출력 전용. 오래된 A/B HANDOFF 재독·갱신 금지.

## 현재 할 일
- **새 #11/#12 댓글이 없어도 LEAD 큐의 미완료 C6를 계속 처리한다.** 한 건이 실행환경/권한 때문에 막히면 그 이유만 적고 다른 LEAD를 처리한다. 새 사실 없는 문서 커밋 금지.
- **RF-067:** [실물 LEAD RF](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-067.md) 14 공개 wrapper의 B Owner/A full wrapper-scope peer 증거를 C05가 C1~C4 MET/C5 N/A로 인수한 상태. 코드 `KEEP_SOURCE_VERIFIED`; **정확 integration SHA의 요구 normal/-O CI는 아직 미확보**, C6/C7 **PENDING**, DONE 아님. 기존 source CI `7cfb26d8` 결과를 다른 HEAD CI로 속이지 않는다. CLI·protected target 실제 실행 금지.
- C04는 새로 들어온 **진짜 LEAD** 각각에 대해 C1~C5 인수와 정확 SOURCE/PEER SHA 확인 → 소스 KEEP 동일성 또는 승인된 **최소 파일** 선별 통합(A/B 브랜치 전체 병합 금지) → 원래 요구 CI의 **정확 integration SHA** 확인 → C05에 C6 인계. `.github/workflows/p15-shared-candidate.yml`의 docs-only push 필터 때문에 해당 HEAD CI가 자동 발생하지 않으면 **수동 workflow_dispatch 가능한 정상 권한 경로 확인 후** 실행/검증. 실행 수단이 없으면 `CI_NOT_RUN/BLOCKED`로만 보고. 보호 정책 임의 완화/워크플로 변경 금지.
- 다른 LEAD가 있으면 한 건 차단 때문에 종료하지 않고 계속한다. C04는 통합 소스·통합에 필요한 기술 문서만 수정 가능; RF C 체크·물리 큐·STATUS·DONE은 **C05 단독**.
- **새 사실이 있을 때만** [Lead #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36) 댓글: `C04 | RF | source/peer SHA | KEEP/INTEGRATED | integration SHA & CI run/pass/NOT_RUN | C6 evidence | C05 NEXT`. 증거 없는 동일 내용 문서 덧쓰기 금지. 0 신규 인계라도 미완료 RF-067 C6를 무시하지 않는다.
