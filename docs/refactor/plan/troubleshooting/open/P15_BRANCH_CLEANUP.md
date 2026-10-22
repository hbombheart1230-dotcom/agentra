# P1.5 브랜치 정리 — 구 Codex UI 브랜치 1개

- **상태:** `WORKTREE_RELEASED_REPORTED / REMOTE_DELETE_PENDING`
- **담당:** Codex B 로컬 PRIMARY CLI (사용자 최신 지시; Claude는 동일 원격 ref를 삭제하지 않음)
- **목표:** 증거 보존 후 구 브랜치 1개만 6→5개 정리. PR #31 stage 정리는 별도 통합 이후.
- **구 브랜치:** `work/p15-b-operator-live-overview-20261020` @ `70843da4ac237c667b41c831a9aad9051626844f`
- **보존 태그:** `archive/p15-20261022/b-operator-historical` → 정확히 같은 원본 SHA (작업 직전 재확인)
- **선행 증거:** [Issue #20의 Codex `WORKTREE_RELEASED` 보고](https://github.com/hbombheart1230-dotcom/agentra/issues/20#issuecomment-6340349296) — 로컬 detach/clean 보고이지 원격 삭제 증명 아님

## 종료 조건
- [ ] 현재 모든 관련 worktree·쓰기 프로세스·dirty/staged/untracked/lock 재확인
- [ ] 실제 원격 구 브랜치 SHA와 태그 peeled SHA 일치, 활성 PR/CI 소비자 없음
- [ ] 정당한 도구/권한으로 정확한 ref 하나만 SHA-lease 방식 삭제, 실패 시 재시도/설정 우회 금지
- [ ] `git ls-remote --heads origin` 및 GitHub 브랜치 목록에서 6→5 확인 (동시 변경 시 실측 수)
- [ ] 증거 SHA·명령 종료 코드·BLOCKED 이유 기록 후 GPT가 `closed/` 이동 및 CURRENT 갱신

**금지:** 원격 main·integration·A/B 활성 ref 변경, 로컬 소스 리셋, PR31 삭제, 포괄적 prune·force·권한 우회. 차단되어도 승인된 다른 개발 계속.
