# C02 — Claude A | 다음 실행 코드·테스트 완결 명령

## 매회 원격 지시 버전·환경 사전점검 (2026-10-29)

- 시작 시 다른 프로젝트 문서나 구 tracking ref를 먼저 읽지 말고 **원격 integration/p1.5의 이 CURRENT 한 파일**을 직접 조회한다. 실제 CANONICAL_HEAD와 ORDER_FILE_BLOB_SHA를 기록한다. 번호별 ORDER_ID = C02 : ORDER_FILE_BLOB_SHA : ITEM_NO. 실행 중 명령서가 바뀌어도 시작 시 고정한 번호를 안전하게 수행하고 다음 회차에서 새 버전을 읽는다.
- 본인 허용 개발 브랜치 원격 HEAD, 로컬 dirty/충돌·코드 소유권을 확인한다. 이어 Python normal/-O pytest 설치 여부와 Git 조회/승인된 push 경로를 점검한다. pytest 부재는 **pytest만 BLOCKED**, push 인증/외부 export 차단은 **push만 BLOCKED**다. 같은 문제로 다른 tmp/fake·읽기 전용 peer·안전한 코드 구현을 전부 중단하지 않는다. 강제 우회·force push·타인 브랜치 쓰기는 허용되지 않는다.
- 각 번호 상태를 PENDING/RUNNING/LOCAL_IMPLEMENTED/PUSHED/TEST_VERIFIED/PEER_VERIFIED/VERIFIED_ALREADY/BLOCKED/NOT_RUN 중 사실대로 기록한다. 실제 로컬 구현·smoke를 원격 정상/-O PASS로 바꾸지 않는다. 같은 SHA·같은 전체 범위의 정확 증거만 재사용한다.
- #11에 실측 START_KST/END_KST/ELAPSED_MIN(실측 없으면 NOT_VERIFIED), CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, 번호별 ORDER_ID/ITEM_STATUS, 정확 OWNER_REMOTE_SHA, 변경 경로, normal/-O 실제 exit, push 검증 SHA 또는 실패 근거, LAST_COMMAND/FUNCTION, UNBLOCK_OWNER, NEXT를 기록한다. 기존 아래 지시의 모든 안전 번호가 각자 완료/차단/한도에 도달하기 전에는 일부 PASS만으로 종료하지 않는다.

**대상:** 기존 `work/p15-a-reporter-pure-20261021` 브랜치의 소유 code/test만 수정·정상 push. 시작 시 원격 A HEAD와 고정 SOURCE `2bce7dcaaadebe9fe825dcf9d2f5e1b1f667ad33` 대조, 진행 중인 작업은 안전 체크포인트까지 마친 후 적용. **1~5 모두 독립적인 필수 개발·계약 과제, 6은 고정 긴급 SOURCE 독립 peer.** 번호는 선행 순서·선택권·회차당 할당량이 아니다. 정확 SHA/범위가 이미 검증된 이전 변경은 중복 수정/재검증하지 않는다. 허용 A 코드·테스트 외 문서/CSV/정책/동결 오라클·타인 브랜치/긴급 브랜치 변경, 실제 시장·브로커·주문·Guard·UEF·Step5C·운영 State/DB/log/RunLab·비격리 CLI 및 force-push 금지. 소켓 차단·fake·`tmp_path`만 사용한다.


## 실행 루프 — 로컬 Codex 방식의 연속 수행 계약 (전 번호 필수)

1. **진입 즉시 작업 테이블 확정:** 현재 원격 A HEAD 및 이 문서 #1~#6을 비교한다. 번호마다 `DONE_WITH_EVIDENCE / IMPLEMENT / TEST / BLOCKED / NOT_RUN`을 구분하고 기존 정확 SHA·범위의 normal/-O PASS만 재사용한다.
2. **실제 코드·테스트로 진행:** 신규 입력의 재현 → 허용 A Owner의 최소 보정·격리 회귀 → normal/-O 실제 exit → A 브랜치 정상 커밋·원격 HEAD/blob 확인. 변경이 불필요하면 원래 계약을 검증한 정확 입력과 결과를 제출한다. #6 긴급 소스 peer는 **상대 수정 없이** 독립 격리 테스트한다.
3. **중간 종료 금지:** 첫 PASS·첫 커밋·첫 댓글에서 종료하지 않는다. #1~#6 모든 번호를 계속 순회하며, 안전한 번호는 순서와 관계없이 빠짐없이 실행한다. 기존 결과를 다시 출력하는 것으로 신규 구현을 대신하지 않는다.
4. **부분 장애 처리:** 인증·의존성·플랫폼 한도는 해당 push/테스트만 BLOCKED로 분리하고 다른 안전 과제를 연속 수행한다. 운영 접속·실거래·보호 파일 변경 등 허용되지 않은 효과로 장애를 우회하지 않는다.
5. **종료 및 인계:** 모든 번호의 원격 코드/테스트·normal/-O·상대 peer 증거가 확보되거나, 남은 번호 각각의 정확한 장애·해제 담당·재개점과 안전 작업 소진을 증명할 때만 종료한다. 도구 제한으로 중단되면 #11에 마지막 함수/명령/실제 결과를 남기고 다음 회차에 그 지점부터 재개한다. 실행 길이는 성과의 대리 지표가 아니다.

**이번 회차 작업량:** #1~#5 서로 독립인 코드·회귀 5건과 #6 긴급 고정 SOURCE 검증 1건을 **전부** 다룬다. 기계적인 시험 반복 대신 결함의 실패→수정→재검증 근거를 우선한다.

## 1 — AI 6개 Owner의 실제 factory/HTTP/intent/consumer 계약 완성 (개발·필수)

- **고정 A SOURCE:** `libs/ai/intent_schema.py`, `libs/ai/strategist.py`, `libs/ai/strategist_config.py`, `libs/ai/strategist_factory.py`, `libs/ai/providers/__init__.py`, `libs/ai/providers/openai_provider.py` (A `2bce7dca`). 이 여섯 파일은 동일 소스 범위에서 integration/B와 blob 일치. 공개 `get_strategist_from_env`, `OpenAIStrategist.from_env/_post_with_retry/decide`, `normalize_intent`와 read-only 소비자 `graphs/nodes/decide_trade.py`의 기존 signature·모듈 경로를 유지한다.
- **실제 개발:** 각 6파일의 공개 API/동적 importer/constructor/IO·State·예외·효과/LOC와 `KEEP/WRAPPER/MOVE/SAFETY_HOLD` 판단 근거를 코드에서 검증한다. `openai_provider.py` 대형(약 727 LOC)이라도 무리한 전면 MOVE는 하지 않는다. 의미 있는 책임 분리가 caller·fake parity로 안전하게 입증될 때만 작은 Owner로 분리하고 원래 facade wrapper/monkeypatch 연결을 보존. 안전한 분리 선행조건이 부족하면 정확 함수·호출자·이유를 **DEFER**로 제출하고 현재 구현을 보존한다. API의 네트워크 기본 호출 금지.
- **신규 `tests/test_p15_ai_factory_decision_edges.py`:** monkeypatch env/HTTP/clock/CB 전역 상태 복원. (a) 키/endpoint 없음 → `BlockedStrategist`/NOOP, (b) rule/legacy 기본 차단·명시 opt-in만 생성, (c) `OpenAIStrategist.from_env` fake 생성 성공/예외→Blocked, (d) `_post_with_retry` fake timeout/backoff/최대 횟수·비재시도, (e) circuit open/recovery 후 실제 네트워크 0, (f) `normalize_intent` 유효 BUY/SELL/NOOP·수량/가격·입력 불변, (g) `decide_trade.py` fake consumer가 주문/State 쓰기 없이 올바른 결과/예외를 받는지. 각 테스트에서 정확 기대 class/dict/호출 횟수와 실제 SOURCE blob 기록; 기존 fake HTTP 테스트와 같은 SHA/범위 반복 금지.
- **주의:** 긴급 별도 SOURCE `1f372f2ffce56f54b732e5e06d83d6ead80afda3`에는 **nonfinite limit price 차단 코드**가 있지만 현재 A 여섯 Owner와 다르다. 이 변경을 A에 복사하거나 통합된 것으로 간주하지 않는다. A SOURCE의 `NaN/Inf` BUY/SELL limit 입력이 actionable이면 **격리 재현/실제 결과만** 제출하고 C04/C05의 안전 통합 판단 전 원본 정책 변경 금지.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_ai_factory_decision_edges.py` 및 `python -O -m pytest -q -p no:cacheprovider tests/test_p15_ai_factory_decision_edges.py`. 실제 파일별 first unmet/DEFER/다음 안전 작업은 #11 댓글로 전달.

## 2 — KOFIA 채권 수익률 비유한 숫자·불량 정책의 국소 격리 (개발·필수)

- **기존 SOURCE:** `libs/market/korea_bond_yields.py::_to_float/_indicator_from_rows/fetch_korea_bond_yield_overrides` (A blob `1e996cbfbb492e6c4f555026163f07f9993a67e6`). 현재 `_to_float("nan"/"inf")`가 유효 float로 통과하여 `_indicator_from_rows`의 `status="ok"`/delta에 비유한 값이 섞일 수 있다. `timeout_sec=float(...)`와 `days=int(float(...))`는 외부 fetch try 바깥이라 잘못된 정책값에 예외가 날 수 있다.
- **수정:** `_to_float`는 `math.isfinite`인 수치만 반환하고 나머지는 None. `_indicator_from_rows`의 현재 값이 무효면 기존 `status="unavailable",reason="kofia_value_missing"`, 이전 값만 무효면 정상 현재 값은 유지하고 `delta/previous` 생략. policy timeout/lookback은 외부 호출 전에 유한 양수/허용 최소 일수로 안전 정규화하되 **유효한 정책과 기본 네트워크 enabled 설정/요청 XML/키/단위는 불변**, 비정상 정책은 기존 기본 8.0/14로 대체한다. 기본 네트워크 호출을 직접 실행하지 않는다.
- **신규 `tests/test_p15_kofia_nonfinite_policy_contract.py`:** `_indicator_from_rows`에 `val2="nan",val3="inf"`와 정상 `3.5/3.4` 2행을 주고 unavailable/유한 delta 각각 검증. `_fetch_kofia_xml`를 fake spy로 대체하고 `korea_bond_yield_timeout_sec="bad"`, lookback `"nan"`을 줘 예외 없이 fake 호출·결과 dict 키 유지, 비정상 값이 네트워크로 전달되지 않음. 정상 `timeout=4,lookback=7`은 동일 전달, provider disabled 시 fake 호출 0. 실제 urlopen/socket 0.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_kofia_nonfinite_policy_contract.py` 및 `python -O -m pytest -q -p no:cacheprovider tests/test_p15_kofia_nonfinite_policy_contract.py`.

## 3 — 글로벌 감성 Korea 지표 비유한 입력의 유효값 보존 (개발·필수)

- **기존 SOURCE:** `libs/market/global_sentiment.py::_as_float/_normalize_korea_index_packet/_compute_korea_raw` (A blob `8523d4ca9b36efca8e060040738a74d5947754c5`). 현재 `_as_float("nan")`는 NaN을 그대로 반환하며 `_normalize_korea_index_packet`은 `int(_as_float(...))`에서 NaN/Inf로 ValueError/OverflowError를 발생시킬 수 있다.
- **수정:** `_as_float`는 유한 숫자만 수용, 비유한/파싱 실패는 **기존 default**. 기존 `_normalize_korea_index_packet`의 out_indices 원본 필드/카운트/상승·하락·보합·breadth 계산, `_compute_korea_raw` 정상 값은 불변. `compute_global_sentiment`이 status unavailable일 때 의도적으로 NaN을 반환하는 **별도 공개 계약은 수정 금지**. 네트워크 수집·실제 시장 파일 효과 없음.
- **신규 `tests/test_p15_global_sentiment_korea_finite.py`:** mock `indices={"KOSPI":{"change_pct":"nan","rising":"inf","falling":"2"},"KOSDAQ":{"change_pct":"1.5","rising":"1","falling":"0"}}` → 예외 없음, 유효 KOSDAQ 1.5% 유지, breadth=(1-2)/3, nonfinite KOSPI 변화 0으로 계산, 원본 dict 불변. 정상 양쪽 변화/카운트는 이전 결과 parity, `compute_global_sentiment_signal`의 DRY_RUN은 socket 호출 0. 공개 unavailable→NaN은 직접 의도된 의미만 정적 확인하고 새 정책으로 바꾸지 않는다.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_global_sentiment_korea_finite.py` 및 `python -O -m pytest -q -p no:cacheprovider tests/test_p15_global_sentiment_korea_finite.py`.

## 4 — Strategy memory의 잘못된 playbook usage_count 국소 실패 방지 (개발·필수)

- **기존 SOURCE:** `libs/performance/strategy_memory.py::_safe_float/_safe_int/build_strategy_memory/write_strategy_memory` (A blob `4427c7877b9361724795d9560e54f25b0e3ac943`). `build_strategy_memory`는 best/worst 및 snapshot에서 `int(float(playbooks[*].usage_count))`를 직접 호출하여 `"bad"/"nan"/"inf"`에서 전체 메모리 생성이 실패한다. `_safe_float`도 비유한 숫자를 그대로 전달한다.
- **수정:** `usage_count` 변환을 `_safe_int`로 통일하고, `_safe_int/_safe_float`에서 비유한 값은 기존 default로 국소 처리. 유효 `usage_count>=2`·승률·수익률·정렬·best/worst mutual exclusion·`advisory_only=True`/JSON 키/시간 외 bytes는 불변. 실제 `write_strategy_memory`의 기본 reports_root/환경 설정·운영 파일은 실행 금지, pure `build_strategy_memory` 중심.
- **신규 `tests/test_p15_strategy_memory_malformed_usage.py`:** `playbooks={"good":{"usage_count":3,"win_rate":0.8,"avg_return":0.1,"stability_score":0.7},"bad":{"usage_count":"nan","win_rate":"inf","avg_return":"oops"}}`, summary 최소 dict → 예외 없음, good best에만, bad 제외, `json.dumps(memory,allow_nan=False)` 가능, 입력 불변. `usage_count=2`·정상 두 playbook에서는 이전 best/worst 순서·snapshot/count 유지. `write_strategy_memory(tmp_path,...,summary=...,playbook_stats=...)`는 **명시 temp**에서만 허용하며 파일이 temp 아래 한 곳에만 생기는지 확인; reporter digest reader는 temp/fake.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_strategy_memory_malformed_usage.py` 및 `python -O -m pytest -q -p no:cacheprovider tests/test_p15_strategy_memory_malformed_usage.py`.

## 5 — StateStore broker truth 보존·원자적 tmp 실패 계약 (개발·필수)

- **기존 SOURCE:** `libs/storage/state_store.py::_broker_truth_revision/_preserve_newer_broker_truth/_replace_with_retry/StateStore.load/save` (A blob `6545242962899e65109c242408bea9db35dcf6ee`). `save`는 현재 JSON을 읽고 authoritative revision이 새로울 때 보호 키를 보존, `*.tmp.<pid>.<thread>`에 fsync 후 `os.replace`하며 finally에서 temp 삭제한다. 운영 broker truth 키·timestamp 우선순위를 **임의 변경 금지**.
- **신규 `tests/test_p15_state_store_truth_atomicity.py`:** `tmp_path/state.json`만 사용. (a) 저장 파일 current `broker_truth_position_reconciliation={"authoritative":True,"generated_at":"2026-10-29T10:00:00Z"}`, `mock_positions=[{"symbol":"A"}]`, 입력 state marker 09:00Z와 `mock_positions=[]` → 새 파일의 최신 current protected keys 보존, 다른 일반 키는 새 입력값 유지; (b) current marker가 더 오래되면 새 입력 protected 값 적용; (c) 파일이 손상 JSON이면 load 기본 schema, save 새 유효 JSON; (d) `os.replace` 첫 호출 PermissionError, 다음 성공 fake sleep→파일 원자 교체·tmp 잔여 0; (e) 모든 retry 실패면 PermissionError 전달·기존 파일 SHA 불변·tmp 잔여 0. 오직 tmp root, fake os.replace/time.sleep/fsync 사용; 원본 dict 불변·실제 운영 DB/State 쓰기 0. 코드 결함이 발견되더라도 protected key 세트/우선순위/실제 broker 판단을 바꾸지 않고 **해당 helper의 안전한 임시파일 정리만** 최소 수정. 정책 변경 필요 시 `SAFETY_HOLD`와 정확 증거를 C03/C05에 인계.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_state_store_truth_atomicity.py` 및 `python -O -m pytest -q -p no:cacheprovider tests/test_p15_state_store_truth_atomicity.py`.

## 6 — 긴급 SOURCE 두 P0 패치의 정확 SHA 독립 검증 (필수·긴급 브랜치 쓰기 금지)

- **고정 SOURCE:** `1f372f2ffce56f54b732e5e06d83d6ead80afda3` (`emergency/p15-fixes`). 원격 `libs/core/log_maintenance.py::write_log_inventory`의 dev/catalog·JSON/MD symlink 외부 쓰기 차단 및 `libs/ai/intent_schema.py::_to_float/normalize_intent`의 nonfinite limit price NOOP patch. 원본 테스트 `tests/test_p15_log_inventory_write_root_boundary.py`, `tests/test_p15_intent_nonfinite_limit_price.py`는 변경 금지.
- **독립 temp detached clone:** (a) `tmp_path/logs/dev` 또는 `dev/catalog` symlink가 외부 디렉터리, `log_inventory_latest.json/.md`가 외부 파일 symlink → 외부 SHA/목록 불변, 안전한 temp 정상 catalog 쓰기만; (b) BUY/SELL `price="nan","inf","-inf"` 및 float NaN/Inf → `NOOP`, 유한 limit·시장가/기존 valid action 동작·입력 불변. socket deny, broker/real order 호출 0. `write_log_inventory`의 검사→쓰기 TOCTOU는 별도 HOLD, 비격리 운영 `--apply` 금지.
- **검증:** `PYTHONPATH=<isolated-emergency-tree> python -m pytest -q -p no:cacheprovider tests/test_p15_log_inventory_write_root_boundary.py tests/test_p15_intent_nonfinite_limit_price.py` 및 `PYTHONPATH=<isolated-emergency-tree> python -O -m pytest -q -p no:cacheprovider` 동일 경로(반드시 실제 import file SHA/checkout 확인). 별도 독립 음성 probe `tests/test_p15_peer_emergency_boundaries.py`는 **A 자신의 브랜치에서만** 작성해 고정 emergency clone으로 검증; 긴급 브랜치 코드·테스트/원본 A 보호 정책 변경 0. SOURCE/정상/-O exit·원본/독립 경계·첫 미검증 안전 계약을 #11에 보고. 이 결과는 전체 원본 Owner 독립 C4나 RunLab 실증 완료를 의미하지 않는다.

## 모든 항목 공통 실행·보고

각 개발 과제의 신규 입력/결손→최소 A code/test 수정 또는 기존 동작 검증→normal/최적화(-O) 실제 명령·exit→변경 함수/LOC 전후·호출자/State/IO/예외 parity→A 허용 브랜치 정상 fast-forward commit/push→원격 SHA/blob 재조회. 정확 SHA·범위가 이미 PASS면 반복하지 않고 다른 신규 항목 진행. 외부 모듈/인증/도구/안전 장애는 해당 번호의 `BLOCKED(정확 명령/원인/해제 담당/재개점)`만 기록하고 나머지 안전 과제 계속. 완료되지 않은 번호를 임의 생략하지 않는다.

#11에 **실측** `START_KST/END_KST/ELAPSED_MIN`(원시 기록 없으면 `NOT_VERIFIED`), 1~6 번호별 `IMPLEMENTED/VERIFIED_ALREADY/BLOCKED/NOT_RUN`, 새 코드·테스트·정확 SOURCE/peer SHA, normal/-O exit·원격 push, 마지막 진행/다음 안전 함수, 30분 미만이면 실제 종료 이유를 기록. 게시 시각·예약 간격·테스트 초로 소요시간을 추정하거나 합산하지 않는다. **30분은 감사 경보일 뿐 시간 채우기 지시가 아니다.** 실제 모든 안전 과제 완료, 각 잔여 과제 실증 차단 또는 플랫폼 실제 한도 외에는 종료하지 않는다.
