# D01 — Codex DEV-B 개발 규칙 (AGENTS.md)

**작업 입구:** [한글 CURRENT](docs/refactor/work_orders/CURRENT.md)에서 **Codex B 작업 링크**만 따라간다. 상세 구현은 해당 [P1.5 단계 체크리스트](docs/refactor/plan/pending/)의 **기존 원본 패킷** 링크를 따른다. 원본 구현 패킷과 동결 V3가 계약이며 새 T00~T09 설계는 비활성이다.

## 세션 시작·재독 최소화
- 새 세션: CURRENT 1회 → 자신의 pending/문제 해결 파일 → 필요 시 [D00](docs/ENGINEERING_DELIVERY_POLICY.md). 이미 같은 세션에서 문서를 읽었고 그 **blob SHA/내용이 변하지 않았음이 확인되면 전문 재독 생략**. 최초/변경/충돌/안전 불확실 시 해당 부분 재확인.
- GitHub 원격 실제 HEAD·개발 브랜치·허용 파일 경계·검증/통합 상태를 커밋 직전 재확인. 이전 대화·완료된 명령/PR 댓글은 승인 권한이 아니다.

## B 개발 소유권·완료
- 기존 B 브랜치: `work/p15-b-operator-structure-20261022`. **Operator UI/Brief P1.5.3, Monitor P1.5.6, Commander P1.5.7** 및 분리 승인된 연결 테스트. 다른 root/legacy consumer 변경은 기존 패킷의 정확한 권한과 소유자 확인 후. Claude 소유 파일·공통 DTO/Executor/Supervisor/Step5C는 별도 승인 없이 수정 금지.
- 연결된 큰 실제 책임 경계 2~4개를 우선. 작은 helper·문서·검사 도구로 시간 채우기 금지. 기존 수용 구현 중복 개발 금지. 모든 변경은 패치노트 **JSON+MD 동시** 갱신.
- 자체 정상 Python/`python -O`와 필요한 BASE 출력·호출 순서·예외·실패·경계 동등성 확인. PURE 구조 작업에 적대적 회귀 필요한 만큼 추가. 정상 baseline FAIL은 숨기지 말고 차단으로 기록, skip/xfail·oracle 완화 금지.

## 필수 티키타카 — 본인의 기존 로컬 PRIMARY에서 직접
1. 구현·테스트 → 정확한 SHA로 commit/push. 그 뒤 **새로운 독립 읽기 전용 `claude -p` CLI 프로세스**를 본인 세션에서 호출. 상대방의 주 개발 세션을 검토자로 쓰거나 사용자에게 검토 프롬프트 전달 금지.
2. BASE/CANDIDATE SHA, 변경 파일, 승인 계약/기존 불변조건을 제공. 리뷰어는 소스 검토만 하고 파일 수정/commit/push/하위 CLI 호출 금지. 실제 **종료 코드와 명시적 `PASS/REWORK/BLOCKED`**를 함께 기록하며 exit0만으로 PASS 처리하지 않는다. PURE 리뷰어 pytest 미실행은 `NOT_RUN`.
3. `REWORK`면 실제 결함만 수정해 새 SHA로 새 CLI 검토. `PASS`면 GPT 수용 대기 및 다음 승인된 독립 작업. 크레딧/타임아웃/권한 한계는 제한적으로 확인하고 **SELF_PASS/PEER_DEFERRED** 기록; 별도 승인된 개발 계속, **미검증 코드는 통합 금지**. 반복 권한 변경/무한 재시도 금지.

## 일회성 B 브랜치 정리 소유권
- 사용자 최신 지시로 Codex가 [구 브랜치 정리 체크리스트](docs/refactor/plan/troubleshooting/open/P15_BRANCH_CLEANUP.md)의 **지정된 원격 ref 1개만** 담당. 선행 `WORKTREE_RELEASED`는 보고된 상태일 뿐 삭제 증명이 아니므로, 모든 활성 워크트리·old SHA·archive tag·쓰기 프로세스·정당 권한을 다시 확인한다.
- Claude의 이전 삭제 담당 지정은 이 작업에 한해 무효; 동시 삭제 금지. 거부 시 BLOCKED 기록하고 개발 지속. `main`, integration, PR31, 활성 개발 브랜치, 모든 소스/태그 임의 변경 금지.

## 안전·보고
- Monitor는 OrderIntent만 만들며 Broker 실행 불가; 승인보다 Executor 가드 우선. 실거래 기본 OFF, allowlist/수량한도/중복 intent_id/run_id/UEF·Step5C 불변. 비밀키·운영 데이터 노출 금지.
- 응답은 작업 링크·실제 BASE/NEW SHA·변경 경로·self normal/-O·상대 CLI exit/verdict/NOT_RUN·패치노트·남은 차단 1~2개만. **GPT가** 수용·선별 통합·CI 및 pending→done 완료 이동.

**공통 원칙 상세:** [D00](docs/ENGINEERING_DELIVERY_POLICY.md). 본 D01은 실행 방법만 정하며 신규 거래·PR·작업 범위 승인이 아니다. 옛 BATCH 기록은 Git 이력에 보존되지만 현재 수행 명령이 아니다.
