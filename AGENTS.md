# D01 — Codex B 개발 규칙

> **역사적 CI provenance (재활성화 금지):** Issues #16–#19 are CLOSED · DOC_FREEZE는 완료된 문서 동결 단계 · REVIEW_ONLY_NO_NESTED_CLI는 지금도 유효한 읽기 전용 검증 경계. P1.5.2 OPEN/P1.5.3 문구는 과거 단계 기록이며 CURRENT의 RF 배정을 대체하지 않는다.

**작업 입구:** [CURRENT](docs/refactor/work_orders/CURRENT.md)의 **이번 Codex 배정 RF 링크** → [pending 개발 RF](docs/refactor/plan/pending/) 및 [verification/claude 리뷰 RF](docs/refactor/plan/verification/claude/)의 해당 파일 → 그 파일의 기존 동결 원본 패킷. [전체 현황](docs/refactor/plan/STATUS.md)과 [P1.5.0~11 합격 기준](docs/refactor/plan/criteria/)은 필요할 때만 본다. P1.5 단계 번호는 새로운 순차 배정이 아니다.

- **로컬 예약 실행:** `C:\Users\홍훈\Agentra-P15\dev-b`에서 시작. 매번 최신 원격 CURRENT만 확인하고 **그 시점에 배정된 모든 RF·일회성 정리 건을 순회**, 각 건의 수행/보류/차단을 각각 보고한다. 한 작업에 남은 구현이 없거나 PEER_DEFERRED라도 다른 배정 작업을 이어서 점검한다. 미배정 RF는 임의 수행 금지. D00/D01/D02 및 원본은 최초·변경·충돌·안전 의심 시에만 재독.
- **재독 최소화:** 새 세션에는 CURRENT부터 읽고 작업 링크를 확인한다. 같은 세션에서 이미 읽었고 문서 SHA/내용이 불변이면 전문을 다시 읽지 않는다. 변경·충돌·안전 의심 시 다시 확인. 공통 헌법은 [D00](docs/ENGINEERING_DELIVERY_POLICY.md).
- **담당:** A/B 영구 역할 고정 금지. CURRENT의 최신 배정이 우선이다. 기존 Codex 전문 작업은 Operator UI, Monitor, Commander. RF마다 [파일 전수 소유권](docs/refactor/plan/FILE_COVERAGE_63182ab2.csv)을 확인해 **해당 RF 소유 파일만** 수정한다. 타 RF 소유 공유 계약/State/테스트가 필요하면 지팀장에게 조정 요청. 동일 파일 A/B 동시 수정 금지.
- **개발:** 기존 구현과 CI 증거부터 재사용, 의미 있는 큰 Owner/폴더 경계 우선. 소비자 검증 없이 공개 import/CLI/path 이동 금지. 기존 값·순위·직렬화·LLM 호출·State·예외·안전/실거래 기본 OFF 불변. 테스트·검증 오라클 완화 금지.
- **테스트/패치노트:** 정상 및 `python -O`, BASE parity·경계 실패 검증 후 commit/push. 코드 변경 시 UI 연결 patch_notes JSON/MD 동시 갱신. 테스트 산출물은 세션별 격리·성공 자동정리·실패 제한 보존.
- **티키타카:** 로컬에서는 본인 주 CLI에서 커밋 SHA를 대상으로 **새 읽기 전용 `claude -p` 독립 프로세스**를 직접 호출한다. 클라우드에서는 CURRENT가 배정한 `verification/claude/RF-xxx.md`의 **Claude 구현 SHA**를 독립 Codex 세션에서 읽기 전용으로 검증하며 근거가 있는 경우에만 `REMOTE_PEER_PASS` 후보로 보고한다. 직접 CLI 실행과 원격 검증을 섞어 기록하지 않는다. 리뷰어는 파일 수정/commit/push/재귀 CLI 실행 금지. exit code와 명시적 `PASS/REWORK/BLOCKED`를 확인; exit0 자체는 PASS 아님. REWORK면 실제 수정 새 SHA로 재검토. 리뷰어 테스트 미실행은 `NOT_RUN`.
- **크레딧 부족:** `SELF_PASS/PEER_DEFERRED`로 기록 후 다른 승인된 독립 RF 계속 가능. **독립 검증 미완료 코드는 GPT 통합 금지**. 무한 재시도·권한 우회 금지.
- **검증 후 통합·CI 책임 (사용자 승인):** Codex는 `verification/claude/`의 Claude 구현 RF를 독립 검증 PASS한 후, **읽기 전용 리뷰 세션 밖의 별도 제한 통합 단계**에서 승인된 RF 범위만 `integration/p1.5`에 반영한다. 원격 최신 HEAD·단일 writer/CAS·독점 소유 경계 확인에 실패하면 즉시 `INTEGRATION_BLOCKED`로 보고하고 Push 금지. 통합 SHA에서 normal/`python -O` 관련 회귀와 필수 GitHub Actions의 실제 결론을 확인해 SHA·URL·exit·PASS/FAIL/NOT_RUN을 RF에 남긴다. CI 실패/미실행/대기 중이면 최종 DONE 금지. GPT에 통합/CI 증거를 전달하고 **GPT만** `done/` 이동한다. 구 4-HEAD 합성 `d73be191`, main·실거래·안전·CI 오라클은 위임 범위가 아니다.
- **일회성 정리:** [구 B UI 브랜치](docs/refactor/plan/troubleshooting/open/P15_BRANCH_CLEANUP.md) 안전 삭제는 현재 Codex 단독 담당. 실제 worktree/태그/원격 SHA 확인 후 단일 ref만 조치; 차단 시 BLOCKED. Claude 동시 삭제 금지.
- **금지:** 무승인 main·실거래·Supervisor/Executor/Step5C·UEF 안전 변경, PR31 통째 병합, 타 RF 소유 파일 변경.
- **인수인계/보고:** 구현 RF는 기존 RF 파일에 최소 인수인계(BASE/후보 SHA·branch/PR·변경 경계·normal/-O 명령/exit·patchnotes·HOLD)를 기록하고 구현자 기준 `verification/codex/` 이동 후보로 제출한다. 검증 RF는 변경 없이 검증 SHA·명령·exit·판정/NOT_RUN을 동일 파일에 덧붙일 증거로 제출한다. 공용 상태 변경은 GPT/승인된 queue publisher만 반영한다. 동일 RF 파일을 복제하지 말고 이동 시 상대 링크를 보정한다. 기존 보고 필드도 유지한다. Codex는 본인이 검증한 Claude RF의 제한 통합/CI를 수행·보고하고, **GPT만** 독립 근거를 확인해 `verification → done` 이동한다. 이로써 `pending → verification/<author> → done` 3단계가 된다.
