# C03 — 지팀장 · 수용판정/배정

**매회 외부 입력은 [A #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [B #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [RunLab #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 최신 미처리 댓글만.** D00 공통 규칙 적용. [Lead #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)은 **결정 출력 전용**, 읽어야 할 네 번째 큐가 아니다. 기존 A/B HANDOFF 재독·갱신 금지.

1. **새 댓글이 없어도 기존 미완료 READY 배정·소유 충돌을 재확인하되, 근거 없는 문서 변경/반복 댓글을 남기지 않는다.** 새 Issue 댓글별 `COMMENT_ID → RF → OWNER/PEER → SOURCE SHA → 원래 C1~C5 충족 범위`만 판정. 필요한 RF 원본/정확 코드만 선택 조회; 스코프 PASS를 전체 PASS로 승격하지 않음. C05는 #11/#12 증거로 독립 처리할 수 있으므로 C03의 별도 승인을 기다리지 않는다. C04는 실제 LEAD 큐를 직접 처리한다.
2. 우선 작업: **B full peer RF-015/031**, **A RF-040/061 Owner**, **B RF-065/063 Owner → A peer**, 그 밖의 현재 미완료 RF 안전 범위. 새로운 SHA가 없어도 기존 C 미충족 계약을 배정. B READY RF-044/045, A 슬롯 해제 시 RF-036/037. RunLab #32 신규 실제 관측은 해당 원 owner에게만 source/read-only 조사 배정, RF 결함 확정 전 보호 HOLD.
3. **C03 필수 갱신:** #11·#12·#32 또는 RF 실물 단계에서 Owner·우선순위·최초 차단·다음 실행 RF가 바뀌면 **C01(B)·C02(A)·이 C03을 직접 수정·각 파일 푸시 후 원격 재조회**한다. 필요한 RF/RunLab 인수 문서도 지팀장만 수정한다. 변경 없으면 쓰기 0; 과거 검증표·장문 HANDOFF 복사 금지. 댓글과 RF 원본/STATUS 정본을 일치시키되 동일 이력·검증 표를 복사하지 않는다.
4. **실제 변화가 있을 때만** [Lead #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)에 `C03 | input issue comment | RF | 판정/배정 | 최초 미충족 C | 담당/NEXT` 한 번 보고. 변동 없음 → 문서 쓰기 0, 댓글 0. C03은 원본 RF 체크/물리 이동·CI/DONE 권한 없음.
