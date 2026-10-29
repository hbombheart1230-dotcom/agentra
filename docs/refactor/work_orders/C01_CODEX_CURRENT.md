# C01 — Codex B | FAST-3 실행·환경 복구 / 실적 우선

**정본:** GitHub `hbombheart1230-dotcom/agentra` / `integration/p1.5`.
**허용 소유 브랜치:** `work/p15-b-operator-structure-20261022`의 코드·테스트만 작성·정상 푸시. README/문서/RF/STATUS/CI·D00·타인 브랜치·운영 State·실계좌·실주문·비격리 `--apply` 수정·효과 금지.

## 최상위 계약 — 기존 #1~#8 반복 의무 폐기

- **D00 §2 FAST-3 우선:** RF 개발 DONE은 G1(원격 소스) + G2(영향받은 경계의 실제 pytest **또는 재현 가능한 stdlib Python smoke normal exit0 1회**) + G3(C04 최소 통합/KEEP, 관련 테스트/기존 유효 CI, C05 DONE)만 필수다. 원래 전체 C4 peer, 매번 `python -O`, 전체 hosted CI, frozen 장시간 테스트는 신규 DONE 필수 게이트가 아니다. 정확 SHA의 기존 PASS를 재사용한다.
- 이전 C01의 #1~#8은 **역사 작업 항목**이며 모두를 매회 다시 개발/테스트하라는 요구를 종료한다. 특히 RF-016은 이미 C05가 `04_LEAD_ACCEPTANCE`로 옮겨 G1/G2 MET, C04 G3만 남았다. RF-016 원래 full C4·q15 mutation 추가·94 migration 재실행은 지금 B의 완료 조건이 아니며 **새 독립 peer는 선택사항**이다.
- **환경 미준비를 작업자 태만으로 취급하지 않는다.** 그러나 접근 불가 환경에서 10개 미푸시 소스/테스트를 계속 복제·재커밋하는 것은 개발 진도가 아니다.

## 0 — 시작 시 고정·환경 복구 단 한 차례

1. 최신 원격 **이 C01 한 파일**과 `integration/p1.5` HEAD·C01 blob SHA, 본인 원격 B HEAD를 먼저 고정. B 로컬 작업 트리의 unpushed commit과 dirty 파일의 보존 여부 확인. 과거 `2055bc6fb3090766f87dc343f656c267d65ed2b7`의 코드/테스트-only 로컬 변경은 **보존**하고, 막연한 rebase/reset/cherry-pick·다른 커밋으로 덮어쓰기 금지.
2. `python --version`, `python -m pip --version`, `python -m pytest --version`을 각각 실제 실행. 테스트 의존성 부재면 **환경이 허용하는 범위에서 단 한 번** 격리 venv + `pip install pytest`를 시도할 수 있다(정책상 허용된 인터넷/패키지 인덱스만, 우회 금지). 실패하면 `PYTEST_BLOCKED`로 고정하고 새 코드에 한해서 실제 `python -c ...`/stdlib harness normal exit0로 G2를 검증한다. pytest 명령의 `No module named pytest` exit1을 기능 테스트 FAIL로 표시하지 않는다.
3. `git push origin HEAD:work/p15-b-operator-structure-20261022`를 **현재 깨끗한 승인 owner 브랜치 commit에 한해서 한 번** 확인. Git HTTPS username/자격증명이 없으면 승인된 GitHub 연결 도구가 **이미 제공하는** owner-branch contents/commit/ref 쓰기 기능 유무만 확인해, 허용된 경로가 있으면 그 경로만 사용한다. 브라우저에서 보이는 GitHub 계정 연결이 곧 VM Git credentials라는 가정은 금지. PAT 노출·새 토큰 요구·원격 보호 우회·private 소스의 비승인 외부 반출·force push 금지.
4. `pytest` 및 승인 원격 쓰기가 **모두** 계속 차단이면 `ENV_BLOCKED_BOTH`를 제출하고, **새 로컬 전용 구현·커밋 생산을 중단**한다. 가능한 소스 read-only 검토와 재현 가능한 stdlib smoke만 1건 수행하고 정확 첫 차단을 보고한 후 종료. 매 회차 같은 실패를 8회 반복하지 않는다. 복구/설정 변경이 확인될 때만 본 개발을 재개한다.

## 1 — 기존 B 로컬 2055bc6f 결과 보존/원격 반영 (환경 해제 때만)

**기존 로컬 범위**(Issue #12 [6495081990](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6495081990)): `scripts/maintenance/compact_q9_decision_windows.py`의 소형 Q9 JSON no-growth, `scripts/diagnostics/query_strategist_llm_events.py`의 NaN/Inf 제외, RF-031 caller 및 CLI 전달 등 **기존 8개 신규 테스트**. 새 작업으로 다시 만들지 말 것.

- 원격 B `617c8429...` 이후 동일 소스/테스트가 이미 반영됐는지 경로와 blob을 비교. 원격에 없다면 로컬 소유 commit의 변경 경로·기능·실제 source diff를 확인하고 금지 문서/HANDOFF/보호 파일 0인 경우에 한해 **기존 승인 B owner branch로 정상 push**. 푸시 경로가 계속 없으면 재커밋 금지, `LOCAL_ONLY_UNPUBLISHED`로 명시.
- 정상 test 환경이면 바뀐 함수와 직접 caller에 대한 **관련 pytest 하나**, 아니면 함수의 특정 입력/기대 결과를 명시한 **실제 normal stdlib smoke(exit0)** 하나를 수행해 G2 범위와 명령을 보고. 조용한 `compileall`만으로 동작 검증 주장 금지.
- `2055bc6f` 및 `7cf68e33/f833ec44` 등 서로 다른 과거 로컬 버전의 내용을 섞거나 타인 브랜치를 수정하지 않는다.

## 2 — 환경이 복구된 경우에만 1개 신규 안전 과제

**대상:** `scripts/maintenance/compact_q9_decision_windows.py`의 컴팩션이 파일보다 커지는 경우 **원본 유지·임시파일 미생성·감소량 0**을 실제 tmp-only로 검증. 기존 `tests/test_p15_compact_q9_no_growth.py`가 정확 SHA에서 이미 확인되면 `VERIFIED_ALREADY`로 처리하고 불필요한 중복 테스트/코드 작성 금지. 새 실패 입력이 나타난 경우에만 B 소유 최소 수정·관련 normal pytest 또는 stdlib smoke(exit0)·허용 브랜치 원격 push. 다른 레거시 #1~#8을 마음대로 계속 배정하지 않는다.

## 3 — 보고·종료 조건

#12에 **실측** `START_KST, END_KST, ELAPSED_MIN`(불가하면 NOT_VERIFIED), `CANONICAL_SHA / C01_BLOB / B_REMOTE_SHA / B_LOCAL_SHA / CHANGED_PATHS / G1 / G2 / G3_PENDING`, 해당 명령/정확 exit, 실제 normal/-O 수행 여부, 승인 push 성공 또는 처음 발생한 인증/정책 차단, `UNBLOCK_OWNER/NEXT`를 1개 짧은 댓글로 제출.

- `ENV_BLOCKED_BOTH`이면 B 개발 산출물의 원격 SHA가 **없다는 사실**을 분명히 기록하고, **로컬 Codex + C03 긴급 승인 브랜치**의 검증/구현으로 이관할 대상 파일명·재현 입력만 지정한다. A/B·integration 브랜치에 대한 무단 우회 쓰기 금지.
- G1/G2 판정은 C05, G3 KEEP/통합은 C04, `05_DONE`·STATUS는 C05가 수행. B가 해당 권한을 대신 행사하거나 실험 성공을 DONE이라고 보고하지 않는다.
- 30분 강제 작업량 및 형식적인 8번씩 출력을 금지. **원격 코드·G2 증거 또는 처음 확인된 환경 차단 근거**가 있으면 종료 가능. 복구되지 않은 동일 차단은 다음 회차 한 줄 참조하고 재시도 실패만 누적하지 않는다.
