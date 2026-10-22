# D02 — Claude DEV-A 개발 규칙 (CLAUDE.md)

**작업 입구:** [한글 CURRENT](docs/refactor/work_orders/CURRENT.md)에서 **Claude A 작업 링크**만 따라간다. 상세 구현은 해당 [P1.5 단계 체크리스트](docs/refactor/plan/pending/)의 **기존 원본 패킷** 링크를 따른다. 기존 V3/원본 P1.5 단계가 동결 계약이며 새 T00~T09 설계는 비활성이다.

## 세션 시작·재독 최소화
- 새 세션: CURRENT 1회 → 자신의 pending 단계 파일 → 필요 시 [D00](docs/ENGINEERING_DELIVERY_POLICY.md). 같은 세션에서 **blob SHA/문서 내용이 변하지 않았음이 확인되면 상세 재독을 생략**. 새 세션/변경/충돌/안전 불확실 때 필요한 부분 다시 확인.
- GitHub 원격 실제 HEAD·승인된 파일 범위·통합/검증 현황을 커밋 직전 재확인. 옛 Issue/완료된 작업 지시는 신규 수행권이 아니다.

## A 개발 소유권·완료
- 기존 A 브랜치: `work/p15-a-reporter-pure-20261021`. **Reporter P1.5.1~2, Strategist P1.5.4, Scanner P1.5.5**, 해당 승인 테스트. Codex의 Monitor/Commander/Operator UI·공통 계약·Executor/Supervisor·Step5C는 별도 승인 없이 변경 금지.
- 폴더/책임 경계에서 크고 의미 있는 PURE 코드 작업을 우선하고 이미 수용된 Reporter 코드를 중복 개발하지 않는다. 변경은 UI 패치노트 JSON/MD 동시 보존 및 정합성 확인.
- 구현 후 정상 Python·`python -O`·필요한 BASE 동등성(출력/예외/부작용/LLM/호출 순서)과 실패/경계 테스트. 동결 핀이나 거부된 권한·안전 오라클은 바꾸지 않는다.

## 필수 티키타카 — 본인의 기존 로컬 PRIMARY에서 직접
1. 구현/자체 테스트 후 정확한 커밋 SHA로 push; **새로운 독립 읽기 전용 `codex exec` CLI**를 본인 세션에서 호출한다. 기존 Codex 주 개발 세션을 검토자로 쓰거나 사용자에게 프롬프트 복사 요청 금지.
2. BASE/CANDIDATE, 변경 경로, frozen 계약을 전달. 리뷰어는 읽기 전용 소스 검토, 수정·커밋·푸시·하위 CLI 재호출 불가. 실제 CLI 종료 코드와 `PASS/REWORK/BLOCKED` 판정을 별도 확인; exit0만으로 PASS 불가. PURE 리뷰어 측 pytest 미실행은 `NOT_RUN`.
3. 실제 결함은 REWORK→새 SHA→신규 독립 CLI 재검토. 크레딧 부족/무응답 시 제한적 확인 후 **SELF_PASS/PEER_DEFERRED**; 승인된 독립 작업은 계속해도 **미완료 독립 검증을 통합 완료로 주장하거나 통합할 수 없음**. 권한 우회·무한 재시도 금지.

## 크레딧 부족 시
- Codex는 **현재 승인된 구 UI 브랜치 정리 작업**의 유일한 원격 삭제 담당. Claude는 관련 브랜치/tag/ref를 병렬 변경하지 않는다. 본인 크레딧이 부족하면 검증만 deferred로 남기고 재개 시 갭을 해결; 다른 개발자의 독립 진행을 막지 않는다.

## 안전·보고
- Scanner 순위/soft chart-fit와 Monitor hard 진입권한을 혼동하지 않는다. Reporter I/O·LLM·기존 byte/ledger 동등성, 거래 안전·UEF/Step5C·실거래 기본 OFF·키/데이터 격리를 보존한다.
- 보고는 작업 파일 링크와 정확한 BASE/NEW SHA, 변경 경로, normal/-O, 신선한 상대 CLI exit+판정/NOT_RUN, 패치노트·차단. **GPT가** 최종 수용·선별 통합·필수 CI·pending→done 이동.

**공통 원칙 상세:** [D00](docs/ENGINEERING_DELIVERY_POLICY.md). D02는 방법이지 신규 파일/브랜치/안전 수정 허가가 아니다. 이전 BATCH/CURRENT 텍스트는 Git 이력에서 확인할 수 있지만 새 지시가 아니다.
