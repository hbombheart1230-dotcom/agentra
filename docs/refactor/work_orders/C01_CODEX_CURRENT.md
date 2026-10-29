# C01 — Codex B | FAST-3 안전 수정·환경 재개 (다음 실행)

**허용 소스:** `work/p15-b-operator-structure-20261022`의 code/test만. 실계좌·운영 로그/State·실주문·비격리 apply·Broker/Step5C/UEF·frozen oracle·문서/STATUS/타인 브랜치/force push 금지. 현재 B 원격 `617c8429c69c98ac6f707a820d0e6825766f8642`; 로컬 `2055bc6fb3090766f87dc343f656c267d65ed2b7`는 **원격 미푸시**다.

## 0 — 시작 버전 고정·차단 분리

1. **원격 integration의 이 C01 파일 한 개**를 조회하고 `CANONICAL_HEAD`, `ORDER_FILE_BLOB_SHA`, `OWNER_REMOTE_SHA`를 원격에서 실측. `ORDER_ID=C01:<ORDER_FILE_BLOB_SHA>:<ITEM_NO>`로 번호별 기록. 실행 중 C01 변경은 현재 실행을 소급 실패시키지 않는다. 로컬 작업 트리 dirty/경합·기존 미푸시 커밋 보존 확인. 이전 HANDOFF/로컬 C01 대체 금지.
2. `python -m pytest --version`, `python -m pip --version`, `git ls-remote origin refs/heads/work/p15-b-operator-structure-20261022` 및 승인된 정상 push 경로를 **최소 1회** 점검. Python 환경 허용 시 격리 venv+정책상 승인된 index의 pytest만 설치 시도 가능. Git 자격증명/private export 실패는 `PUSH_BLOCKED`, pytest 부재는 `TEST_BLOCKED`로 각각 기록; 임의 PAT·force·비승인 외부 전송·새 브랜치 금지. **둘 다 차단이면 새 로컬 전용 구현·커밋 금지**; 이미 보고된 차단을 무의미하게 재실행하지 않고 아래 코드 경계만 read-only로 검토하여 `ENV_BLOCKED_BOTH`와 해제 담당·재개점을 #12에 남긴다.
3. 기존 로컬 Q9 no-growth·LLM finite source/테스트는 **다시 만들지 않는다**. 승인 push가 실제 복구되면 기존 로컬 code/test-only commit의 변경 경로·원격 blob을 비교하고, 충돌/금지 문서가 없을 때만 허용 B 브랜치로 정상 푸시. 원격 HEAD/blob 재조회 전 `PUSH_VERIFIED` 금지. 관련 pytest 또는 새 stdlib smoke **정상 exit0** 한 번만 G2 증거로 제출. 이미 같은 SHA·입력의 PASS는 재사용.

## 1 — EventLogger 복사 경계 결함 (승인된 원격 쓰기 복구 시 실행)

- **정확 원본:** B `617c8429c69c98ac6f707a820d0e6825766f8642`, `libs/core/event_logger_compat.py::_NodeEventLogger.__getattr__` blob `941f7485f708790fe0251d15fba01e4af1d24293`. 현재 `return getattr(self._logger, attr)`가 `copy.copy`·`copy.deepcopy`의 `__setstate__` 탐색 중 아직 `_logger`가 없는 복사본에서 재귀 호출한다. A 정확 B SHA 독립 #11 `6495308964`: 정상/-O **각 2 FAIL(RecursionError)+2 PASS**, 재현 근거로 재사용하고 **기존 A peer를 반복 실행하지 않는다**.
- **최소 수정:** `__getattr__`에서 `self.__dict__.get("_logger")`로 직접 내부 상태를 읽고, `_logger`가 아직 없거나 요청이 `_logger` 또는 미정의 dunder 속성이면 즉시 `AttributeError(attr)`를 발생시킨다. 그 밖의 공개 속성만 기존 `getattr(logger,attr)`로 위임. `get_event_logger` 생성자 분기, `start/end`의 동일 `_run_id`/stage·payload dict 정규화, `EventLogger` 본체/JSONL 포맷·실로그 경로는 바꾸지 않는다. `copy`/deepcopy가 지원되지 않는 다른 구형 logger 형태가 있으면 그 형태는 명시적 실패로 분리하고 무리한 global patch 금지.
- **신규 B 소유 `tests/test_p15_event_logger_copy_guard.py`**: stdlib `unittest`+fake `log(run_id,stage,event,payload)` 수집기만 사용. `_NodeEventLogger("node_x",fake)`에 대해 (a) copy.copy, (b) copy.deepcopy가 RecursionError 없이 종료하고 `node=="node_x"`, `_run_id` 원본과 동일; (c) 원본 start/end 이벤트 2개가 같은 run_id, payload non-dict→`{}`; (d) 없는 공개 속성은 AttributeError, 존재 속성은 원래 fake에 위임; (e) 원본/복사본 초기화 순서와 외부 파일·네트워크 쓰기 0. **기대 실패를 완화하지 않는다.** 명령 `python -m unittest discover -s tests -p 'test_p15_event_logger_copy_guard.py' -v` 정상 exit0, pytest 설치된 경우 `python -m pytest -q -p no:cacheprovider tests/test_p15_event_logger_copy_guard.py`; `python -O`는 선택적 추가 검증(FAST-3 필수 아님).
- 실제 코드·테스트만 정상 커밋/푸시하고 B 원격 SHA/blob 재조회 → #12 `ORDER_ID, ITEM_STATUS, CHANGED_PATHS, NORMAL_EXIT, OPT_EXIT 또는 NOT_RUN, PUSH_REMOTE_SHA, FIRST_BLOCKER, NEXT` 기록. A의 기존 FAIL은 **수정 후 새 B SHA의 새 범위 검증 전** 자동 PASS로 승격하지 않는다. C04 최소 통합·targeted smoke, C05 G1/G2/G3·DONE 인계.

## 2 — 보고·재개

#12에 `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID/ITEM_STATUS | CHANGED_PATHS | NORMAL_EXIT/-O_EXIT or NOT_RUN | PUSH_REMOTE_SHA or PUSH_BLOCKED | LAST_COMMAND/FUNCTION | ERROR | UNBLOCK_OWNER | NEXT | START_KST/END_KST/ELAPSED_MIN`(실측 없으면 NOT_VERIFIED) 기록. 환경 양쪽 차단이면 마지막 안전 체크포인트는 **B `617c8429` / `_NodeEventLogger.__getattr__` / A `6495308964` 2 FAIL / 승인 push·pytest 복구 대기**이며 새 로컬-only 커밋 0. G1/G2는 C05, G3 최소 통합은 C04, DONE/STATUS는 C05 권한. 원래 전체 peer·매 RF -O·hosted 전체 CI는 강제하지 않는다.
