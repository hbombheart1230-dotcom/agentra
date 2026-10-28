# C04 — 지팀장 · 선별 통합/CI

**입력:** [Issue #11 Claude A](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [Issue #12 Codex B](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [Issue #32 RunLab](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 **새 댓글 delta만** → C05가 실제 `04_LEAD_ACCEPTANCE`로 이동한 RF. [D00](D00_ENGINEERING_DELIVERY_POLICY.md) 준수. [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)은 결과 출력 전용. 오래된 A/B HANDOFF 재독·갱신 금지.

## 현재 할 일
- **새 #11/#12 댓글이 없어도 LEAD 큐의 미완료 C6를 계속 처리한다.** 한 건이 실행환경/권한 때문에 막히면 그 이유만 적고 다른 LEAD를 처리한다. 새 사실 없는 문서 커밋 금지.
- **RF-067 CLOSED (C05 실물 종결 2026-10-28):** B SOURCE `29eff7f7`, A independent full wrapper peer `23e54e01`, 14/14 KEEP 확인. `integration/p1.5@beca55b47e4ad2cde1bc8fc9fe2b8db6cec07989` [Actions `40623624802`](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/40623624802)에서 normal/`-O` 각각 SUCCESS. 이후 C05 문서/큐/STATUS만 변경했고 D00 §2.2 `CI_PASS_AT_BASE + DOC_ONLY_EQUIVALENT_AT_HEAD`로 인수, `05_DONE/CODEX_B/RF-067.md` 이동 완료. 이 RF는 **재검증·재-디스패치·재통합 금지**, 실제 protected diagnostics/운영 target은 별도 NOT_RUN/SAFETY_HOLD. **현재 물리 LEAD 0건**; 다음 신규 LEAD만 처리.
- C04는 새로 들어온 **진짜 LEAD** 각각에 대해 C1~C5 인수와 정확 SOURCE/PEER SHA 확인 → 소스 KEEP 동일성 또는 승인된 **최소 파일** 선별 통합(A/B 브랜치 전체 병합 금지) → 원래 요구 CI의 정확 integration SHA **또는 D00 §2.2의 엄격한 문서 전용 동등성** 확인 → C05에 C6 인계. `.github/workflows/p15-shared-candidate.yml`의 docs-only push 필터로 HEAD CI가 자동 발생하지 않더라도 **D00 §2.2 동등성 충족 시 새 dispatch 요구 금지**. 불충족 시에만 정상 권한 경로로 실행/검증하며 실행 수단이 없으면 `CI_NOT_RUN/BLOCKED`로 보고. 보호 정책 임의 완화/워크플로 변경 금지.
- 다른 LEAD가 있으면 한 건 차단 때문에 종료하지 않고 계속한다. C04는 통합 소스·통합에 필요한 기술 문서만 수정 가능; RF C 체크·물리 큐·STATUS·DONE은 **C05 단독**.
- **C04 필수 갱신:** 실제 LEAD 후보·통합 SOURCE SHA·CI 결과·첫 차단/NEXT가 바뀌면 **이 C04 파일의 현재 작업만 교체·푸시·원격 재조회**한다. C01/C02/C03/C05는 수정하지 않고, A/B가 문서를 대신 갱신하게 하지 않는다. 변화 없으면 C04 쓰기 0.
- **새 사실이 있을 때만** [Lead #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36) 댓글: `C04 | RF | source/peer SHA | KEEP/INTEGRATED | integration SHA & CI run/pass/NOT_RUN | C6 evidence | C05 NEXT`. 증거 없는 동일 내용 문서 덧쓰기 금지. 0 신규 인계라도 미완료 RF-067 C6를 무시하지 않는다.
