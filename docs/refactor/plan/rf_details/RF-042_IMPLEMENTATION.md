# RF-042 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-042.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 2개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/approval/service.py` blob `067821068bd12cec2b2985dc8a9fbe7c21fed009` (576 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/approval/service.py::list_intents` L542-576 | KEEP_CLASS_OR_EXTRACT | `libs/approval/service.py::list_intents` | 35행 · 순수 후보 |
| `libs/approval/service.py::admit_pre_approved_intent` L195-227 | KEEP_EFFECT_SPLIT_PURE | `libs/approval/service.py::admit_pre_approved_intent` | 33행 · BROKER |
| `libs/approval/service.py::reject` L324-356 | KEEP_CLASS_OR_EXTRACT | `libs/approval/service.py::reject` | 33행 · 순수 후보 |
| `libs/approval/service.py::_resolve_intent` L271-296 | KEEP_CLASS_OR_EXTRACT | `libs/approval/service.py::_resolve_intent` | 26행 · 순수 후보 |

### list_intents — 원본 35행
- **확인된 책임:** `libs/approval/service.py` L542–576; 직접 호출 helper `_unwrap_intent`. 감지된 효과: 없음.
- **목표:** `libs/approval/service.py::list_intents` (Owner Codex B, RF-042). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### admit_pre_approved_intent — 원본 33행
- **확인된 책임:** `libs/approval/service.py` L195–227; 직접 호출 helper `_execution_order`. 감지된 효과: BROKER.
- **목표:** `libs/approval/service.py::admit_pre_approved_intent` (Owner Codex B, RF-042). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### reject — 원본 33행
- **확인된 책임:** `libs/approval/service.py` L324–356; 직접 호출 helper `_resolve_intent`, `_latest_row`, `_state_status`, `_safe_state_transition`, `_append_marker`. 감지된 효과: 없음.
- **목표:** `libs/approval/service.py::reject` (Owner Codex B, RF-042). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _resolve_intent — 원본 26행
- **확인된 책임:** `libs/approval/service.py` L271–296; 직접 호출 helper `_safe_state_ensure`, `_unwrap_intent`, `_latest_row`. 감지된 효과: 없음.
- **목표:** `libs/approval/service.py::_resolve_intent` (Owner Codex B, RF-042). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/approval/__init__.py` | `libs/approval/__init__.py` | `51fc1716f087` / 19B | 짧은 단일 책임이면 KEEP_OK |
| `libs/approval/service.py` | `libs/approval/service.py` | `067821068bd1` / 26831B | 위 실측 함수 이동·효과 경계 먼저 |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-042|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
