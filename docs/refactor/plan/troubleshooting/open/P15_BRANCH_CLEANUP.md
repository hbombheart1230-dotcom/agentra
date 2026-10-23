# P1.5 브랜치 정리 — 구 Codex UI 브랜치 1개

- **상태:** `REMOTE_REF_DELETED_VERIFIED / LOCAL_EXIT_EVIDENCE_PENDING`
- **담당:** Codex B 로컬 PRIMARY CLI (사용자 최신 지시; Claude는 동일 원격 ref를 삭제하지 않음)
- **목표:** 증거 보존 후 구 브랜치 1개만 6→5개 정리. PR #31 stage 정리는 별도 통합 이후.
- **구 브랜치:** `work/p15-b-operator-live-overview-20261020` @ `70843da4ac237c667b41c831a9aad9051626844f`
- **보존 태그:** `archive/p15-20261022/b-operator-historical` → 정확히 같은 원본 SHA (작업 직전 재확인)
- **선행 증거:** [Issue #20의 Codex `WORKTREE_RELEASED` 보고](https://github.com/hbombheart1230-dotcom/agentra/issues/20#issuecomment-6340349296) — 로컬 detach/clean 보고이지 원격 삭제 증명 아님

## 원격 재확인 (2026-10-23)
- GitHub REST 원격 branches 5개 확인. `refs/heads/work/p15-b-operator-live-overview-20261020` 404; `refs/tags/archive/p15-20261022/b-operator-historical` commit SHA `70843da4ac237c667b41c831a9aad9051626844f` 정상 보존. 원격 삭제는 완료되었으나 마지막 로컬 exit/프로세스 및 PR 소비자 확인 증거는 미검증 상태.
- 예약 보고에서 `REMOTE_DELETE_PENDING`이라고 한 것은 원격 현황과 상충함. 중복 삭제 금지.

## 종료 조건
- [ ] 현재 모든 관련 worktree·쓰기 프로세스·dirty/staged/untracked/lock 재확인
- [ ] 원격 보존 태그 SHA 검증 완료(`70843da4`); 활성 PR/CI 소비자 없음은 별도 검증
- [ ] 정당한 도구/권한으로 정확한 ref 하나만 SHA-lease 방식 삭제, 실패 시 재시도/설정 우회 금지
- [x] GitHub 원격 refs API/branches 목록에서 삭제 확인 (현재 5개); 현장 `git ls-remote` CLI 근거는 미확인
- [ ] 증거 SHA·명령 종료 코드·BLOCKED 이유 기록 후 GPT가 `closed/` 이동 및 CURRENT 갱신

**금지:** 원격 main·integration·A/B 활성 ref 변경, 로컬 소스 리셋, PR31 삭제, 포괄적 prune·force·권한 우회. 차단되어도 승인된 다른 개발 계속.
