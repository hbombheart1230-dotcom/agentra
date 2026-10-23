# D02 — Claude A 개발 규칙

> **역사적 CI provenance (재활성화 금지):** Issues #16–#19 are CLOSED · DOC_FREEZE는 완료된 문서 동결 단계 · REVIEW_ONLY_NO_NESTED_CLI는 지금도 유효한 읽기 전용 검증 경계. P1.5.2 OPEN/P1.5.3 문구는 과거 단계 기록이며 CURRENT의 RF 배정을 대체하지 않는다.

**작업 입구:** [CURRENT](docs/refactor/work_orders/CURRENT.md)의 **이번 Claude 배정 RF 링크** → [pending 개발 RF](docs/refactor/plan/pending/) 및 [verification/codex 리뷰 RF](docs/refactor/plan/verification/codex/)의 해당 파일 → 원본 동결 구현 패킷. [전체 현황](docs/refactor/plan/STATUS.md), [P1.5.0~11 합격 기준](docs/refactor/plan/criteria/)은 필요할 때만 읽는다. 단계 번호는 순차 개발 명령이 아니다.

- **로컬 예약 실행:** `C:\Users\홍훈\Agentra-P15\dev-a`에서 시작. 매번 최신 원격 CURRENT만 확인하고 **Claude 배정 RF 전부를 순회**, 수행/보류/차단을 각 건 별도 보고한다. 첫 작업에 진척 없다고 다음 배정 RF를 누락하지 말 것. 미배정 RF 신규 착수 금지. D00/D01/D02 및 원본은 최초·변경·충돌·안전 의심 시에만 재독.
- **재독 최소화:** 새 세션 CURRENT부터 읽는다. 같은 세션에서 이미 읽었고 문서 SHA/내용이 같으면 전문 재독하지 않는다. 변경·충돌·안전 불확실 시 재확인. 전 팀 공통 규칙은 [D00](docs/ENGINEERING_DELIVERY_POLICY.md).
- **담당:** RF는 Claude/Codex 영구 배정이 아니라 CURRENT에서 지팀장이 탄력 지정. 기존 Claude 전문 영역은 Reporter, Strategist, Scanner. [파일별 RF 소유권](docs/refactor/plan/FILE_COVERAGE_63182ab2.csv) 확인 후 해당 RF 파일만 수정. 타 RF의 공유 DTO·State·graph·테스트는 읽기 전용이며 변경 필요 시 조정 요청. A/B 동시 수정 금지.
- **개발:** 이미 구현/수용된 코드 재개발 금지. 의미 있는 큰 PURE Owner 분리와 기존 서비스 재사용. 공개 import·graph 호출·rank/Top1·State·프롬프트/LLM retries·출력·예외 동등성 보장. 파일 이동 전 동적/CLI/테스트/배포 소비자 검증.
- **테스트/패치노트:** normal 및 `python -O`, BASE parity·실패/경계 회귀 후 SHA push. 변경 시 UI patch_notes JSON/MD 동시 기록. 성공 임시 산출물 자동정리, 실패 제한 보존. 오라클 완화 금지.
- **티키타카:** 로컬에서는 자신의 주 CLI에서 새 독립 읽기 전용 `codex exec` 프로세스를 직접 호출. 클라우드에서는 CURRENT가 배정한 `verification/codex/RF-xxx.md`의 **Codex 구현 SHA**를 독립 Claude 세션에서 읽기 전용으로 검증하며 근거가 있는 경우에만 `REMOTE_PEER_PASS` 후보로 보고한다. 직접 CLI 실행과 원격 검증을 섞어 기록하지 않는다. BASE/후보 SHA·변경 파일·동결 경계 전달. 리뷰어는 수정/commit/push/다른 CLI 재호출 금지. 실제 종료 코드와 명시적 `PASS/REWORK/BLOCKED` 확인; exit0만으로 PASS 금지. REWORK면 새 SHA 재검토. 테스트 미실행은 `NOT_RUN`.
- **크레딧 부족:** `SELF_PASS/PEER_DEFERRED` 후 다른 승인된 독립 RF 계속 가능. **GPT는 미검토 코드를 통합할 수 없다.** 권한 우회/무한 재시도 금지.
- **브랜치 정리:** 현재 [구 B UI 브랜치](docs/refactor/plan/troubleshooting/open/P15_BRANCH_CLEANUP.md)는 Codex 단독. Claude는 동일 ref·태그를 변경하지 않는다.
- **안전:** Scanner의 soft chart-fit를 Monitor hard veto로 전환 금지; Broker·승인·실거래·UEF/Step5C 및 main 무승인 변경 금지. 비밀값/운영데이터 분리.
- **인수인계/보고:** 구현 RF는 기존 RF 파일에 최소 인수인계(BASE/후보 SHA·branch/PR·변경 경계·normal/-O 명령/exit·patchnotes·HOLD)를 기록하고 구현자 기준 `verification/claude/` 이동 후보로 제출한다. 검증 RF는 변경 없이 검증 SHA·명령·exit·판정/NOT_RUN을 동일 파일에 덧붙일 증거로 제출한다. 공용 상태 변경은 GPT/승인된 queue publisher만 반영한다. 동일 RF 파일을 복제하지 말고 이동 시 상대 링크를 보정한다. 기존 보고 필드도 유지한다. GPT 단독 선별 통합·CI·완료 이동.
