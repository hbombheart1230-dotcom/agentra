# C01 — Codex B | 다음 실행 코드·테스트 완결 명령

**대상:** 기존 `work/p15-b-operator-structure-20261022`에서만 소유 code/test 수정·fast-forward push. 시작 시 원격 B HEAD와 아래 고정 SOURCE `617c8429c69c98ac6f707a820d0e6825766f8642`를 대조한다. 이미 다른 실행이 수정 중인 파일은 안전 체크포인트/HEAD 확인 후 겹치지 않게 이어간다. **1~5는 각기 필수 신규 개발·회귀 과제, 6은 필수 정확-SHA 상대 독립 검증.** 번호는 우선순위·선택권·종료 조건이 아니다. 결과가 이미 정확 SHA/범위로 입증된 것은 중복 실행하지 않고, 새 입력·새 소스·새 결손에만 테스트를 추가한다. 7은 실제 플랫폼 한도로 차단된 별도 동결 게이트로 유지한다. 모든 IO는 `tmp_path`·fake/deny-socket; 운영 파일/로그/주문/브로커/Guard/UEF/Step5C/RunLab, frozen 파일·CI/정책·문서/CSV·타인 브랜치 수정 및 force-push 금지.

## 1 — Q9 compact의 파일 크기 역증가 방지 (개발·필수)

- **확인한 기존 B 코드:** `scripts/maintenance/compact_q9_decision_windows.py::compact_file/_compact_window/main` (B SOURCE, blob `e6d675039516a736c1ab19892a5fb98574836a13`), 공개 호환 entrypoint `scripts/compact_q9_decision_windows.py`(15 LOC import alias/runpy wrapper, **KEEP**). 현재 `compact_file`은 dict JSON을 읽고 window mapping만 유지한 뒤 무조건 `indent=2`로 재기록한다. 작은 압축 입력은 실제로 **46→111 bytes, 398→1188 bytes** 역증가 관찰. `_compact_window`와 `libs.runtime.q9_decision_snapshots._compact_candidates/_compact_mapping`는 변경하지 않는다.
- **정확 수정:** JSON 객체/유효 window를 기존과 동일하게 변환하고 **출력 bytes를 먼저 메모리에서 직렬화**한다. 원본 파일 byte 크기 이상이면 **원본/백업/임시파일에 아무 쓰기도 하지 않고** 기존 결과 dict 키(`path,backup_path,before_bytes,after_bytes,reduced_bytes,reduced_pct,window_count`)를 유지하되 `after_bytes=before_bytes,reduced_bytes=0,reduced_pct=0,backup_path=""`로 반환한다. 실제 축소 때만 기존 백업 1회·임시파일 replace·출력 JSON 구조/값을 유지한다. 공개 `main(argv)`/legacy wrapper 인자·stdout/exit는 그대로. 이미 존재하는 backup은 덮어쓰지 않는다. JSON이 객체가 아니면 원래 `ValueError`·원본 불변.
- **신규 `tests/test_p15_compact_q9_no_growth.py`:** `tmp_path`에 `{"windows":[]}`를 compact JSON bytes로 저장하고 `backup=True` 호출 → 원본 SHA/size/mtime 및 백업·tmp 목록 불변, reduced=0. 둘째로 1개 큰 scanner top20/window payload를 fake JSON으로 구성하여 **실제 줄어드는 경우에만** before>after, backup bytes=원본, 2회째 재실행 시 backup 불변·새로 크기가 늘면 원본 불변. non-dict `[]` → ValueError, bytes 불변. legacy `scripts.compact_q9_decision_windows`와 canonical module이 동일 `compact_file`을 노출하는지 import-only 확인. 외부/운영 경로 사용 금지.
- **실행:** `python -m pytest -q -p no:cacheprovider tests/test_p15_compact_q9_no_growth.py`; `python -O -m pytest -q -p no:cacheprovider tests/test_p15_compact_q9_no_growth.py`. 실제 shrink가 없는 fixture는 임의로 축소 성공을 꾸미지 말고 payload를 충분히 늘려 확정한다. 반환 계약 변경으로 기존 소비자가 실패하면 재현·호환 최소 보정.

## 2 — 거래 이유 체인의 intent/run 오귀속 방지 (개발·필수)

- **기존 코드:** `scripts/diagnostics/query_trade_reason_chain.py::_event_intent_id/_build_rows/main` (B blob `89ff494d90d9c58ced19634cc877a7af82f60172`), `scripts/query_trade_reason_chain.py` legacy wrapper는 KEEP. `_event_intent_id`는 payload/decision_packet/intent의 ID가 충돌하면 `None`, ID가 모두 없으면 `""`; `_build_rows`는 같은 run 내 실행이 정확히 하나이고 legacy 단일 ID-less 문맥일 때만 LLM/decision fallback, verdict는 명시 ID 필수다.
- **수정/검증:** 위 fail-closed 상관관계를 유지하며, 실제 입력에서 다른 intent의 `allowed`·LLM rationale·decision trace가 결합되는지 음성 검사한다. 결함 발견 시 **이 두 B 소유 함수 내부에서만** ID 충돌/다중 실행 문맥 귀속을 좁혀 수정, `_build_rows` 공개 키·필터·정렬과 `main` exit(없는 파일 2, 잘못된 action 3, 정상 0)를 보존. 실행·브로커 코드를 수정하지 않는다.
- **신규 `tests/test_p15_trade_reason_chain_attribution.py`:** temp JSONL ① 같은 run에 BUY intent `I1`, SELL `I2` 및 서로 다른 decision/verdict/LLM → 2행 각자의 rationale/allowed만; ② packet/outer ID 충돌 → 해당 문맥 무귀속; ③ ID 없는 단일 execution → LLM/decision만 fallback, verdict 미귀속; ④ ID 없는 다중 execution → 어느 것도 이전 문맥 누출 없음; ⑤ fake broker_code `0`와 실패 코드 → `only_broker_success`는 성공 행만. `main(["--path",tmp,"--action","SELL","--json"])` stdout JSON·원본 SHA 불변. `iter_jsonl_events` 실제 parser를 temp에서만 사용.
- **실행:** `python -m pytest -q -p no:cacheprovider tests/test_p15_trade_reason_chain_attribution.py` 및 동일 경로 `python -O -m pytest -q -p no:cacheprovider`.

## 3 — Strategist LLM 진단 필터의 NaN/Inf false-positive 봉쇄 (개발·필수)

- **기존 코드:** `scripts/diagnostics/query_strategist_llm_events.py::_to_float/_filtered_events/main` (blob `c45516931dcb365c8283c596345233458c10a41f`), legacy `scripts/query_strategist_llm_events.py` wrapper KEEP. `_to_float("nan")`이 NaN을 반환해 `abs(NaN)<=1e-12`가 false가 되므로 `--only-nonzero-news`에 **유효하지 않은 뉴스 점수**가 들어갈 수 있다.
- **정확 수정:** `_to_float`에서 `math.isfinite`를 확인하여 NaN/±Inf·파싱 실패는 기존 default로 반환. 유한 ±값·0·`1e-12` 임계·필터 순서, `--summary` 카운트와 JSON/human 출력은 그대로. `_filtered_events`의 stage/event, day/run 필터 및 `payload.ok` 판단은 유지; live LLM/network 호출 없음.
- **신규 `tests/test_p15_strategist_llm_event_finite_filter.py`:** temp events에 `strategist_llm/result` score `0,1e-13,0.2,-0.4,"nan","inf","-inf","bad"` 및 다른 stage/day/run 포함. `only_nonzero_news=True`는 0.2/-0.4 두 행만, `only_failures`와 day/run 조합은 기존 정확 필터, `main(["--path",tmp,"--json","--only-nonzero-news"])`의 stdout 2행·원본 해시 불변, missing path exit 2. legacy alias는 같은 함수를 노출해야 한다.
- **실행:** `python -m pytest -q -p no:cacheprovider tests/test_p15_strategist_llm_event_finite_filter.py` 및 동일 경로 `python -O -m pytest -q -p no:cacheprovider`.

## 4 — Entry blocker 진단 CLI의 출력 경계·필터 전달 (개발·필수)

- **기존 코드:** `scripts/diagnostics/analyze_entry_blockers.py::main` (blob `4d343359ed9515c0ae2d59dfca1e2c8bc3424a0e`), legacy `scripts/analyze_entry_blockers.py` import/runpy wrapper KEEP. CLI는 `--canonical-root`, `--date`, `--symbol`, `--family`, `--limit`, `--json-out`, `--md-out`를 `build_entry_blocker_day_summary`/render에 전달하고 지정 경로에만 쓰는 구조다.
- **실행 범위:** 실제 reports/canonical 접근 금지. `build_entry_blocker_day_summary`와 `render_entry_blocker_summary_markdown`를 monkeypatch fake로 대체해 정확 kwargs `(tmp/canonical, day="2026-10-28", symbol="005930", family="liquidity", limit=2)`와 반환 dict `{"rows":[{"symbol":"005930"}],"total":1}`를 확인. `--json` stdout JSON, 기본 stdout Markdown, `--json-out/--md-out`가 지정된 tmp 두 파일만 기록하고 두 번 실행 시 결과 동일. 다른 경로 파일 목록/내용 불변. 필요 시 B 소유 `main`에서 **증명된** CLI 전달/파일 예외만 최소 보정하고 인자·출력 계약 유지.
- **신규 `tests/test_p15_entry_blocker_cli_temp_contract.py`**; `python -m pytest -q -p no:cacheprovider tests/test_p15_entry_blocker_cli_temp_contract.py`, `python -O -m pytest -q -p no:cacheprovider tests/test_p15_entry_blocker_cli_temp_contract.py`.

## 5 — LLM 보고서 분류 CLI의 dry-run·집계 호환 (개발·필수)

- **기존 코드:** `scripts/maintenance/organize_llm_reports.py::main` (blob `280cdbf991f069152d322d90bf2b9678cac7ff9b`), legacy `scripts/organize_llm_reports.py` wrapper KEEP. 실제 `organize_llm_day`는 파일을 이동할 수 있으므로 **절대 운영 root에 호출하지 않는다**.
- **신규 `tests/test_p15_organize_llm_reports_cli_contract.py`:** `sys.argv`를 `["cmd","--date","2026-10-28","--reports-root",tmp/reports,"--active-grace-sec","120","--dry-run"]`으로 fake, `organize_llm_day`를 spy fake로 대체하여 `Path(tmp/reports),day,active_grace_sec=120,dry_run=True` 정확 전달. 반환 `[{"category":"success"},{"status":"blocked"},{"category":"success"},{}]` → stdout JSON `counts={"success":2,"blocked":1,"unknown":1}`, `date`/dry_run 불변, exit 0, temp 밖 파일 0. 명시 tmp `--dry-run` 없음도 fake를 통해 False 전달만 검사(실제 이동 금지). legacy wrapper의 import-only 동일 `main` 확인. 결함 발견 시 이 B 소유 CLI에서만 수정; 기본 grace=180/기존 args 보존.
- **실행:** `python -m pytest -q -p no:cacheprovider tests/test_p15_organize_llm_reports_cli_contract.py` 및 동일 경로 `python -O -m pytest -q -p no:cacheprovider`.

## 6 — Claude A 6개 AI Owner 고정 SOURCE 독립 검증 (필수·상대 쓰기 금지)

- **고정 A SOURCE:** `2bce7dcaaadebe9fe825dcf9d2f5e1b1f667ad33`. 격리 detached temp clone의 `libs/ai/{intent_schema.py,strategist.py,strategist_config.py,strategist_factory.py}`, `libs/ai/providers/{__init__.py,openai_provider.py}`와 read-only `graphs/nodes/decide_trade.py`만 검사. 각 Owner의 public 함수·호출자/동적 import·IO/예외·source blob을 정리하고 **실제 fake/deny-socket** 독립 probe를 작성한다. 타인 코드·테스트·브랜치/운영 경로 수정 금지.
- **정확 입력/기대:** `get_strategist_from_env` 키/endpoint 누락→Blocked/NOOP, 명시 legacy opt-in과 기본 차단, `OpenAIStrategist.from_env` fake 생성·예외→Blocked, `OpenAIStrategist._post_with_retry` fake timeout/backoff/최대 횟수·non-retry 예외, `_CB_STATE` 격리 circuit-open/recovery, `normalize_intent` 유효 가격/수량·미지 action·입력 불변, `decide_trade.py` fake consumer에서 실제 주문/State 쓰기 0. **긴급 SOURCE `1f372f2ffce56f54b732e5e06d83d6ead80afda3`의 비유한 가격 patch는 이 A SOURCE에 없음**: `NaN/Inf`가 ACTIONABLE이면 그 사실만 별도 안전 이슈로 인계하고 A 코드 임의 수정 금지.
- **검증:** 새 B 독립 test `tests/test_p15_peer_a_ai_six_owner_edges.py`를 **B 브랜치에만** 작성하고 `PYTHONPATH=<isolated-A-tree> python -m pytest -q -p no:cacheprovider tests/test_p15_peer_a_ai_six_owner_edges.py` 및 `PYTHONPATH=<isolated-A-tree> python -O -m pytest -q -p no:cacheprovider tests/test_p15_peer_a_ai_six_owner_edges.py` (import 경로가 B 로컬과 섞이지 않도록 `sys.path`/module file SHA 먼저 검증). SOURCE·normal/-O exit·새 probe·첫 미검증 소비자/효과를 #12에 제출. 기존 고정 A 다른 모듈 검증 결과는 이 여섯 Owner의 PASS가 아니다.

## 7 — frozen 계약 검증의 실제 도구 한도 재개점 (차단 별도, 필수 게이트)

- `tests/test_p161_agent_output_contract_freeze.py`는 수정 금지. B SOURCE `617c8429c69c98ac6f707a820d0e6825766f8642`에서 기존 실행은 **단일 명령 약 30.5초 플랫폼 한도에 도달해 종료코드 없음**, 최종 normal/-O `NOT_VERIFIED(PLATFORM_LIMIT)`. 같은 환경·SHA·범위에서 시간만 낭비하는 재실행 금지. **실제로 더 긴 명령 실행이 허용되는 환경**이 확인된 뒤 `python -m pytest -q -p no:cacheprovider tests/test_p161_agent_output_contract_freeze.py` 및 `python -O -m pytest -q -p no:cacheprovider tests/test_p161_agent_output_contract_freeze.py`로 정확 exit 제출. 해제 담당 B 실행 환경/C04; 한도 지속 시 1~6의 안전 과제를 계속하고 해당 게이트만 BLOCKED 유지.

## 모든 항목 공통 실행·보고

각 개발 패키지는 수정 전 재현(새 입력)→B 소유 최소 code/test 변경→새 정상/최적화(-O) pytest 실제 exit→정확 변경 경로/LOC 전후·caller 호환→허용 B 브랜치 commit/fast-forward push→GitHub 원격 HEAD/blob 재조회. 신규 테스트가 이미 존재하거나 정확 범위 결과가 있으면 해당 번호 `VERIFIED_ALREADY(SHA)`로만 보고, 다른 새 안전 번호 계속. `git HTTPS` 인증 장애는 실제 확인한 **허용된 GitHub 연결 경로**로 정상 push할 수 있는 경우만 사용하고 force/새 브랜치 금지. 플랫폼/의존성/안전 BLOCKED는 해당 번호의 정확 명령·exit·담당·안전 재개점 기록 후 다른 번호 진행. 모든 안전 번호 완료 또는 각 잔여 실증 차단/실제 실행 한도 외에는 종료하지 않는다.

#12에 실제 `START_KST/END_KST/ELAPSED_MIN`(원시 기록 없으면 `NOT_VERIFIED`), 1~7 번호별 `IMPLEMENTED/VERIFIED_ALREADY/BLOCKED/NOT_RUN`, SOURCE/상대 고정 SHA, 새 코드·테스트·정상/-O 명령/exit, 원격 push, 다음 안전 함수, 30분 미만 종료의 실제 사유를 기록. 댓글 간격·예약 길이·pytest 초로 세션 시간을 만들지 않는다. **30분은 감사 경보이지 실행시간 목표가 아니다.**
