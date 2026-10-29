# C02 — Claude A | 다음 실행 완결형 코드·테스트 명령

## FAST-3 속도 최우선 (2026-10-29)

- **D00 §2 FAST-3가 이 문서의 과거 full peer·전수 Owner·모든 -O/전체 suite·동결 게이트/모든 번호 완료 강제보다 우선**한다. 원래 C1~C7은 비차단 이력이다. RF 완료 조건은 G1 코드·Owner/KEEP 확인 → G2 변경 부분 정상 pytest 또는 stdlib smoke 1회 → G3 최소 통합·관련 검증·STATUS DONE 세 개다.
- 아래 기존 번호 #1~#7은 **개발 후보 백로그/참고**이고, 해당 RF가 READY를 달성했으면 불필요한 전체 독립 peer/#7 frozen 반복으로 완료를 지연시키지 않는다. 가능한 1~3개 실제 변경·오류 수정부터 구현·정상 테스트·본인 브랜치 push에 집중한다. 특정 번호가 BLOCKED여도 다른 READY RF를 진행한다.
- 수정 없는 모듈은 기존 SHA와 최소 소비자 검증을 재사용. 상대 검증자 전체 원본 파일/모든 -O를 기다리지 않는다. 필요한 경우 상대에게 변경 함수만 비차단 리뷰 요청. G1/G2 확보 즉시 #11(A)/#12(B)에 정확 SOURCE/normal exit와 C03/C05용 READY 인계.
- 모의투자 mock/paper 동작 테스트는 모의 모드·계정 확인 후 가능하며, 실제 런검증은 개발 완료 후 별도 단계. 실계좌 real 주문/모드 활성화 금지. 기존 브랜치·Git 인증·원격 SHA·승인된 경로 사용과 결과 사실성은 유지한다.

## 원격 버전·환경 preflight (모든 번호 공통)

- 시작 첫 행동은 원격 `integration/p1.5`의 **이 C02 파일 하나**를 직접 조회하여 `CANONICAL_HEAD`, `ORDER_FILE_BLOB_SHA`, 허용 A 브랜치의 `OWNER_REMOTE_SHA`를 각각 고정하는 것이다. 번호별 `ORDER_ID=C02:ORDER_FILE_BLOB_SHA:ITEM_NO`를 만든다. 진행 중 새 명령서가 발행돼도 시작 당시 버전을 소급 실패 처리하지 않고 안전 체크포인트 뒤 다음 회차에 새 버전을 적용한다. 오래된 로컬 지시·HANDOFF/세션 기억은 사용하지 않는다.
- 기존 원격 A SOURCE `8e370ccafade4dbb7689536791e4b89f5fdc033f`를 고정한 뒤 `work/p15-a-reporter-pure-20261021`의 실제 HEAD, dirty·경합·허용 파일, `python -m pytest --version` / `python -O -m pytest --version`, 승인된 Git read/push 경로를 점검한다. A가 이전에 수정·검증한 `openai_provider._is_retryable_error`, KOFIA, global sentiment, strategy_memory, state_store 테스트의 **동일 SHA/입력 재실행·재구현 금지**. 아래는 별도의 미충족 함수/negative 입력이다.
- pytest 미설치 시 해당 번호의 `TEST_BLOCKED`, Git HTTPS 인증/private export 실패 시 `PUSH_BLOCKED`만; 다른 안전한 구현·tmp/fake 테스트 준비·독립 read-only peer는 계속한다. 무승인 force/새 브랜치/타인 소스 쓰기 금지. 실제 시장·HTTP·브로커/주문/Guard/Step5C/UEF/RunLab·운영 DB/State/log·비격리 `--apply`·frozen oracle·정책/CSV/작업 문서 수정 금지.
- 번호별 `ITEM_STATUS=PENDING/RUNNING/LOCAL_IMPLEMENTED/PUSHED/TEST_VERIFIED/PEER_VERIFIED/VERIFIED_ALREADY/BLOCKED/NOT_RUN`. #11에 `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID/ITEM_STATUS | CHANGED_PATHS | NORMAL_EXIT/-O_EXIT | PUSH_REMOTE_SHA or exact BLOCKED | LAST_COMMAND/FUNCTION | ERROR | UNBLOCK_OWNER | NEXT | START_KST/END_KST/ELAPSED_MIN`을 남긴다(원시 시간 없으면 NOT_VERIFIED). 30분 미만 종료에는 실제 사유/남은 안전 번호를 기록하되 시간을 채우지 않는다. 로컬 구현·compile/stdlib smoke·테스트 파일 존재를 원격 pytest PASS로 간주하지 않는다.

## 연속 실행 루프

#1~#4는 서로 독립적인 A 소유 개발/회귀, #5는 정확 B SOURCE 독립 peer이며 **모두 필수**다. 번호는 선행 순서·할당량이 아니다. 각 개발 번호는 신규 입력 실패 재현 → A 소유 최소 코드/테스트 수정 또는 정확 동작 증명 → 정상/`-O` 실제 exit → 공개 caller/State/IO/예외 parity·LOC 전후 → A 허용 브랜치 정상 fast-forward commit/push → GitHub 원격 HEAD/blob 재확인. 막힌 번호만 명령·오류·해제 담당·재개점으로 분리하고 나머지를 계속한다. 단일 PASS/커밋/댓글/상대 SHA 부재는 종료 사유가 아니다. 전체 완료, 남은 항목 전부 실증 차단 또는 실제 플랫폼 한도 외에는 중단하지 않는다.

## 1 — OpenAI response adapter의 누락된 decision/signal alias (A 소유)

- **실제 SOURCE:** `libs/ai/providers/openai_provider.py::OpenAIStrategist.decide` (A blob `341296b5b58f195f62c011745aab17afb6e00cd4`, 728 LOC). 608~677행의 native intent, chat nested intent, direct action, decision, signal, malformed fallback 중 **decision/signal alias 두 형태**의 meta/attempts·예외 parity가 아직 미검증이다. `_post_json`은 모듈 전역 use-time patch, `_CB_STATE`는 클래스 공유 상태다. 공개 decide/constructor/`_post_with_retry` 시그니처와 기존 HTTPError retry 수정 유지.
- **신규 `tests/test_p15_openai_adapter_alias_edges.py`:** fake `_post_json`가 `choices[0].message.content`로 (a) `{"decision":"NOOP","reason":"risk_limit"}`, (b) `{"signal":"NOOP","reason":"missing_data"}`, (c) `{"signal":"BUY","symbol":"005930","qty":1,"price":100,"order_type":"limit"}`, (d) `{"signal":[]}`, (e) `not json`을 반환. (a)/(b)는 NOOP, (c)는 유효 BUY/005930/qty1/price100, (d)/(e)는 기존 schema가 정하는 안전 NOOP/오류→NOOP와 정확 meta.attempts=1을 검사. fake StrategyInput/clock/CB 상태 복원, 네트워크·주문 0, 원본 입력 불변. 새 결함만 A 함수에서 최소 보정하고 **nonfinite BUY/SELL limit 정책은 별도 안전 통합 판단 전 변경 금지**.
- **DEFER:** 응답 adapter의 새 Owner MOVE는 위 5형태 parity, module monkeypatch와 CB identity 호환을 증명한 뒤 설계. 현재 728 LOC를 이유로 무리한 이동/중복 구현 금지.
- **normal/-O:** `python -m pytest -q -p no:cacheprovider tests/test_p15_openai_adapter_alias_edges.py` / `python -O -m pytest -q -p no:cacheprovider tests/test_p15_openai_adapter_alias_edges.py`.

## 2 — Korea index sanity의 비유한 수치 경계 (A 소유)

- **실제 SOURCE:** `libs/market/korea_index_sanity.py::_to_float/korea_index_sanity` (blob `9963d5dc660ea4f7d7e3ff54fb6db22871b7b511`, 97 LOC). 현재 `float("nan")/float("inf")`가 통과해 warning/JSON에 비유한 값이 전파될 수 있다.
- **수정:** `_to_float` 변환 뒤 `math.isfinite`를 확인하고 비유한 값은 기존 default(None)로 처리. 정상 6% warning/10% critical, high/low/current 경고 임계값과 공개 반환 키는 그대로. 네트워크/시장 파일 효과 0.
- **신규 `tests/test_p15_korea_index_sanity_finite.py`:** `indices.KOSPI={change_pct:"nan",high:"inf",low:"10",current:"10"}`, `KOSDAQ={change_pct:"6.5",current:"101",high:"100",low:"99"}` → KOSPI 허위 경고 0, KOSDAQ extreme + outside-range 2건, status warning, `json.dumps(result,allow_nan=False)` 성공, 입력 불변. 유효 10.1% critical, high<low critical, 빈/nonmapping indices status ok.
- **normal/-O:** `python -m pytest -q -p no:cacheprovider tests/test_p15_korea_index_sanity_finite.py` / `python -O -m pytest -q -p no:cacheprovider tests/test_p15_korea_index_sanity_finite.py`.

## 3 — Playbook 통계의 비유한 return·불량 recent_window (A 소유)

- **실제 SOURCE:** `libs/performance/playbook_stats.py::_safe_float/_extract_return/calculate_playbook_stats` (blob `f61800edcb08eb3a242798dd07113c317070b53f`, 179 LOC). 현재 `nan/inf`가 return/avg/recent 배열에 전파되고 `int("nan")` recent_window는 예외를 낸다.
- **수정:** `_safe_float`에서 nonfinite는 기존 finite default; `_extract_return`은 authoritative truth/fallback return의 유한 숫자만 수용해 비유한 것은 None/기존 다음 후보로 처리, `values`에 넣지 않는다. recent_window 불량·0·음수는 기본 5 또는 기존 최소1로 정규화. 유효 score/정렬/usage_count/스키마/UTC timestamp 불변. **타인 `extract_truth_outcome_from_bundle`·실제 broker truth/PnL 해석은 수정 금지**, 운영 report writer 호출 금지.
- **신규 `tests/test_p15_playbook_stats_finite_contract.py`:** fake truth `{"available":true,"return":"nan"}`, 정상 `0.2`, fallback `trade_outcome.return_pct="inf"/"bad"/"0.1"`. 비유한 score는 avg/win/recent에 없음, 정상 0.2/0.1은 유지, `json.dumps(...,allow_nan=False)` 성공. recent_window `"nan"/0/-2` 안전 처리, 유효 3 기존 parity, 입력 불변.
- **normal/-O:** `python -m pytest -q -p no:cacheprovider tests/test_p15_playbook_stats_finite_contract.py` / `python -O -m pytest -q -p no:cacheprovider tests/test_p15_playbook_stats_finite_contract.py`.

## 4 — ProposalStore append 전 직렬화 실패의 빈 파일 생성 방지 (A 소유)

- **실제 SOURCE:** `libs/storage/proposal_store.py::ProposalStore.__init__/save` (blob `a7def15b4c818d3c13e0af5b5737509e884e019f`, 12 LOC). 현재 `open("a")` 이후 `json.dumps`가 실패하면 빈 파일이 생길 수 있다.
- **수정:** `save`에서 `line=json.dumps(proposal,ensure_ascii=False)+"\n"`을 파일 open 이전에 계산하고 성공 후 기존 UTF-8 append. 기본 생성자 경로/JSONL/한글/예외 TypeError 유지, rename·삭제/운영 기본 경로 실행 금지.
- **신규 `tests/test_p15_proposal_store_append_serialization.py`:** 명시 `tmp_path/"proposals.jsonl"`에 `{"symbol":"005930","memo":"한글"}` 2회 append→두 줄/순서/UTF-8; 이어 `{"bad":object()}`→TypeError·기존 파일 SHA/size 불변; 새 temp 경로 첫 저장 실패→빈 JSONL조차 없음(초기 parent 생성은 기존 계약). 입력 불변, temp 밖 파일 0.
- **normal/-O:** `python -m pytest -q -p no:cacheprovider tests/test_p15_proposal_store_append_serialization.py` / `python -O -m pytest -q -p no:cacheprovider tests/test_p15_proposal_store_append_serialization.py`.

## 5 — Codex B EventLogger adapter copy/deepcopy 독립 음성 peer (상대 read-only)

- **고정 B SOURCE:** `617c8429c69c98ac6f707a820d0e6825766f8642`, `libs/core/event_logger_compat.py::_NodeEventLogger/__getattr__/get_event_logger` blob `941f7485f708790fe0251d15fba01e4af1d24293`, 실제 `libs/core/event_logger.py::EventLogger` blob `de869be7efe526b83b5d5cf75a4a6908a09e0d87`. **새 미검증 범위는 `copy.copy`/`copy.deepcopy` 시 `__getattr__` 초기화 순서에 따른 RecursionError 및 run_id identity**다. 이전 constructor/JSONL PASS를 반복하지 않는다.
- **독립 `tests/test_p15_peer_b_event_logger_copy_boundary.py`:** A 자기 브랜치에만 작성, 별도 detached temp B checkout의 import `__file__`/blob 검증. `EVENT_LOG_PATH=tmp_path/"events.jsonl"`에서 `get_event_logger("node")` 후 copy/deepcopy 실행; 예외 여부 또는 새 인스턴스 `node/_run_id` 보존 여부를 정확 기록. 원본 start/end의 tmp JSONL 두 줄·동일 run_id와 외부 쓰기 0을 확인. **RecursionError가 재현되면 FAIL/LOW 결함으로 B에 인계**, 테스트 기대를 완화하거나 B 코드 수정 금지. 해당 새로운 음성만 실행, 타인 브랜치/실로그 쓰기 0.
- **normal/-O:** `PYTHONPATH=<isolated-B-tree> python -m pytest -q -p no:cacheprovider tests/test_p15_peer_b_event_logger_copy_boundary.py` / `PYTHONPATH=<isolated-B-tree> python -O -m pytest -q -p no:cacheprovider tests/test_p15_peer_b_event_logger_copy_boundary.py`. 실제 import provenance/exit/첫 누락/해제 담당을 #11에 기록. 이는 상대 전체 C4 승인 아님.

## 후속 인수

#1~#4는 실제 A 코드·테스트와 normal/-O exit, 정상 fast-forward push 및 원격 blob을 제출한다. #5는 고정 B SHA 독립 판정만 제출한다. C04만 선별 통합·정확 SHA hosted CI, C05만 원래 C1~C7/LEAD/DONE/STATUS 판정. 새 안전 차단은 담당·정확 함수·실패 명령·다음 체크포인트로 남기고 다른 안전 항목을 계속한다.
