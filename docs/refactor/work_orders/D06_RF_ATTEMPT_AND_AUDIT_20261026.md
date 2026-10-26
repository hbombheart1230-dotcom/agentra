# D06 — RF 시도 계수·핑퐁 차단·정합성 (2026-10-26 KST)

> D00·D03·D05 하위의 운영 정본. 동일 증거 반복 실행과 HANDOFF-only 진척 착시를 방지한다.

## RF별 최소 메타데이터
- `RF_ID`, `STAGE`, `ORIGINAL_OWNER=CLAUDE_A|CODEX_B|UNASSIGNED`, `ACTIVE_ACTOR`
- `DEV_ATTEMPT_COUNT`: 신규 코드 후보 SHA 제출 횟수(문서·HANDOFF 제외)
- `PEER_ATTEMPT_COUNT`: 서로 다른 후보 SHA 또는 최초 검증 경계의 독립 peer 실행 횟수
- `REWORK_COUNT`: 재현 결함을 개발자로 실제 되돌린 횟수
- `LEAD_DECISION_COUNT`: 근거·판정·다음 단계가 있는 지팀장 실제 결정 횟수
- `SOURCE_SHA`, `PEER_EVIDENCE_REF`, `INTEGRATION_SHA`, `LAST_VALIDATED_SHA`, `NEXT_ACTION`, `BLOCKER`, `UNBLOCK_CONDITION`

## 상태 전환 검증
1. RF는 오직 하나의 물리 경로. D05 폴더명과 문서 STAGE·STATUS·CURRENT가 불일치하면 큐 전환 중지.
2. 같은 `(RF_ID, SOURCE_SHA, test_scope, mode, base_sha)` 증거를 다시 요청하지 않는다. 이전 PASS/FAIL은 유효한 범위에서 재사용.
3. PEER PASS는 자동 DONE이 아니다. 하지만 LEAD_ACCEPTANCE로 **즉시 이동**하여 A/B 활성 개발 큐에서 제거한다.
4. LEAD_ACCEPTANCE는 지팀장 우선 FIFO. 한 번의 예약 실행에 실제 판정/통합 또는 정확한 불가 원인·담당자·실행 명령이 필수. 막연한 `PASS_SCOPED` 재반복 금지.
5. 코드 미변경 KEEP_NOOP는 blob 동일성·소비자·IO/State/효과·독립 peer 증거로 판정한다. 코드 변경 ADMIT은 D03 exact integration SHA 정상/-O 검증 전 DONE 금지.
6. 완료 카운트는 파일 개수와 RF ID 집합으로 산출한다. `DONE` 숫자 수기 선언만으로 통과하지 않는다.
7. 실행 기록은 기존 RF/HANDOFF/Issue 링크를 재사용한다. RF마다 attempt-N 파일을 자동 생성하지 않는다. 날짜·시간은 KST로 기록한다.

## 최초 적용 유의
- RF-013/017/019는 2026-10-26 14시 KST 기준 DONE 기록을 유지하며 새 REWORK를 생성하지 않는다.
- RF-001은 두 owner가 integration에 반영되었으나 exact SHA 검증 미완료로 LEAD_ACCEPTANCE 후보이다. 통합 완료를 검증 완료로 둔갑시키지 않는다.
- 이 문서 자체는 RF 이동·테스트 PASS·예약 변경의 증거가 아니다.
