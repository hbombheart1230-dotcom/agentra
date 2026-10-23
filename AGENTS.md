# D01 — Codex B 개발·검증 규칙 (로컬·클라우드 동일)

> **역사 보존:** Issues #16–#19 are CLOSED · DOC_FREEZE · P1.5.2 OPEN / P1.5.3는 현재 배정이 아니다. 과거 로컬 상대 CLI 호출·티키타카 의무는 폐지. [CURRENT](docs/refactor/work_orders/CURRENT.md)와 [D00](docs/ENGINEERING_DELIVERY_POLICY.md)가 최우선.

- **시작:** 매 실행 integration/p1.5 최신 CURRENT 확인 → 본인 배정 pending RF **전부** 및 일회성 할 일 → `verification/claude/` 큐 확인. D00·원본은 최초·변경·충돌·안전 불확실 시에만 재독. 한 건 BLOCKED여도 다른 할 일 계속.
- **환경:** 로컬 작업장 `C:\Users\홍훈\Agentra-P15\dev-b`; 클라우드 GitHub checkout 사용. 항상 BASE/HEAD/원격 인증·push 권한 확인. A/B 소유 경계는 CURRENT와 `docs/refactor/plan/FILE_COVERAGE_63182ab2.csv` 기준, 타 RF 소유 파일은 읽기 전용. **integration과 개발 브랜치가 갈라진 것만으로 BLOCKED 처리하지 않는다.** integration CURRENT/RF를 읽고 실제 코드는 해당 기존 작업 브랜치에 기록한다. 로컬 새 커밋과 같은 원격 A/B HEAD 사이에서 fast-forward 가능하면 정상 push. 해당 원격 A/B HEAD 변경·소유권 충돌·권한 거부일 때만 BLOCKED.
- **개발:** 기존 구현 재사용, 의미 있는 Owner 분리 또는 KEEP_VERIFIED. 호출·import·DTO/IO·State·출력·예외·side effect 동등성 보존. normal/`python -O`·실패/경계 회귀, UI patchnotes JSON/MD, 격리 테스트 산출물 정리.
- **인수인계:** 기존 A/B 브랜치에 비강제 SHA push 후 RF 원본에 BASE/후보 SHA·변경 경로·명령/exit·patchnotes·HOLD를 기록하고 작성자 큐 `verification/codex/`로 넘긴다. 공용 metadata 이동은 GPT/승인 publisher만 한다. divergence·인증 실패 시 force/rebase/무단 신규 브랜치 금지, BLOCKED 보고.
- **독립 검증:** 상대 작성 큐 `verification/claude/`의 정확한 SHA를 **별도 읽기 전용 세션**에서 검증. 로컬도 클라우드도 상대 CLI를 직접 호출하지 않는다. 리뷰 세션 코드 수정/commit/push/다른 CLI 호출 금지. 자체 검증을 PEER_PASS로 간주하지 말고 실제 명령·exit/NOT_RUN, PASS/REWORK/BLOCKED 명시.
- **검증 후 통합:** 독립 PASS의 정상 RF만 리뷰 세션과 분리된 단계에서 승인 경로를 최신 integration에 단일 writer/CAS·비강제 반영하고 **그 SHA**의 normal/`-O` 및 필수 Actions 확인. 충돌/CI RED·PENDING이면 INTEGRATION_BLOCKED/CI_PENDING. 예외 CI 오라클/4-HEAD/PR31·공유 안전 계약은 GPT 승인 필수; GPT만 `done/` 결정.
- **안전:** main·실거래·Broker/Supervisor/Executor·Step5C·UEF·검증 오라클 무승인 변경 금지. 추적 파일을 덮는 부정 테스트 금지. 임시 브랜치 생성은 지팀장 승인된 특별 예외 외 불허.
- **보고:** RF별 수행/검증 대기/BLOCKED/NO_WORK, 구현/검토/통합 SHA, 실행 테스트/exit, CI URL·상태, 다음 할 일만 간결하게.

## 예약 실행 인수인계
- 매 예약 실행에서 CURRENT의 모든 배정 RF 및 일회성 작업을 확인하고 RF별 IN_PROGRESS, VERIFY_PENDING, BLOCKED, NO_WORK를 기록한다.
- 실제 원격 push를 다시 조회해 SHA를 검증한다. 테스트 normal 및 python -O의 명령, exit, PASS 수 또는 NOT_RUN, 독립 검증 PASS/REWORK/PEER_PENDING을 구분한다.
- 종료 보고 필수 항목: RUN_ID, ROLE, INTEGRATION_SHA, WORK_BRANCH, START_SHA, END_REMOTE_SHA, RF_RESULTS, TEST_NORMAL, TEST_OPTIMIZED, PEER_VERDICT, CI, PUSH_VERIFIED, GPT_ACTION_REQUIRED.
- GPT_ACTION_REQUIRED에는 지팀장이 결정할 소스 수용, 계약 충돌, CI 차단, 검증 큐 이동, 통합, RF 완료와 최소 다음 행동을 명시한다. 없으면 NONE.
- 원격에 저장하지 못한 결과는 HANDOFF_NOT_PERSISTED로 표시한다. 빈 커밋, 임의 신규 브랜치, Issue 댓글은 금지한다. 예약 실행 알림만으로 GitHub 인수인계를 완료했다고 주장하지 않는다.
