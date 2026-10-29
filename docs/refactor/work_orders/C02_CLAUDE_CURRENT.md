# C02 — Claude A | 연속 구현 명령서

**실행 역할:** 이전 채팅·프로젝트 맥락 없이 이 파일의 **개발·검증 과제 1~6 전부 구현·실행 의무**를 수행한다. 번호는 진행상태 식별자이며 **처리 순서·선행 의존성·조기 종료 기준이 아니다**. RF/큐/D00/CURRENT 재독이나 자율 작업 선정 금지. `hbombheart1230-dotcom/agentra`의 **기존** `work/p15-a-reporter-pure-20261021` 브랜치에서 허용된 소스·테스트만 수정한다. 지시 설계 시 원격 A HEAD `8bdbd5ab32eed6d1b0dddfc799d3bc577ebf9a1e` 확인; 시작 시 HEAD를 다시 확인해 이미 같은 구현이 있으면 중복 커밋하지 말고 다음 번호로 진행한다. **보고서/계획만 작성하고 끝내지 말 것.**


**전체 과제 완료 판정:** 과제 1~3은 실제 새 Owner 파일·wrapper 연결·호출자 동등성·normal/-O PASS가 있어야 `IMPLEMENTED`; 과제 4~5는 명시된 모든 입력 사례를 실제 실행하고 오류가 있으면 수정해야 `IMPLEMENTED`; 과제 6은 지정 B SHA에서 독립 검증을 수행해야 `PEER_EXECUTED`. 모두 `IMPLEMENTED | VERIFIED_ALREADY(원격 근거 SHA) | BLOCKED(원인·재개점) | NOT_RUN`으로 각각 기록한다. 테스트 작성만, 과거 PASS, 최초 커밋, 보고 댓글은 전체 작업 종료 근거가 아니다.

## 1 — 실제 Reporter 대형 파일의 종목 반응 책임 분리 (개발·필수)

**SOURCE:** `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py` (지시 기준 약 467 LOC). **새 Owner:** `libs/reporting/baseline_samsung_hynix/forward_validation/stock_reaction.py`. 새 파일이 이미 있으면 중복 생성하지 않는다.

- 현재 `reaction_reader._stock_reaction` (대략 141~270행) **함수의 실제 계산 본문 전체**를 새 Owner의 `stock_reaction_impl(..., facade)`로 MOVE한다. 기존 공개/테스트 호환 `_stock_reaction(day,target,rows,previous_close,last_available_lookback_sec,collector_override)`는 **signature·이름 동일한 얇은 wrapper**로 남긴다. wrapper가 호출 때 `facade=sys.modules[__name__]`을 전달하고, 새 Owner는 facade import/순환 의존 없이 원래 전역 `_number`, `_pct`, `_point_at`, `_checkpoint_epoch`, `_opening_point`, `_close_point`, `_forward_window`, `_last_available_point_before_close`, `CHECKPOINTS`를 필요한 위치에서 `facade.NAME`으로 사용한다. monkeypatch 동적 호출 보존.
- **변경 금지 의미:** 검증된 collector override만 계산 가능한 관측값, collector integrity_failure이면 legacy fallback 금지와 PENDING 유지, 정말 ABSENT일 때만 legacy timeline fallback, 잘못된 CLOSE를 실제 CLOSE로 쓰지 않기, `return_to_close_pct`는 표시한 권위 있는 CLOSE와 동일 기준, CLOSE PENDING인 경우 관측 window의 `status=PARTIAL` 및 `return_to_close_pct=None`, 09:00의 첫 양수 거래량 캔들, `last_available_point_before_close`는 참고용으로만 출력. 리스트 순서·직렬화 출력 키·예외를 수정하지 않는다.
- 새 `tests/test_p15_stock_reaction_extraction.py`: 기존 함수의 **분리 전 고정 기대 JSON/딕셔너리**를 fixture로 확보한 뒤 fake 종목 캔들 ① 빈 입력 ② 09:00 volume=0 뒤 09:01 양수 ③ CLOSE collector=110 vs legacy=90 ④ CLOSE PENDING ⑤ collector INVALID vs ABSENT ⑥ denominator=0 사례에서 결과가 일치해야 한다. 기존 collector 테스트도 정상/`-O`. 새 Owner **350 LOC 이하**, facade 실제 LOC 감소 보고.

## 2 — 동일 파일의 Collector 무결성 책임 분리 (개발·필수)

**SOURCE:** `reaction_reader.py::_collector_raw_row` (지시 기준 약 340~419행). **새 Owner:** `libs/reporting/baseline_samsung_hynix/forward_validation/collector_observations.py`.

- 함수 body를 `collector_raw_row_impl(*, day,index_name,slot,root,facade)`로 MOVE하고 기존 `_collector_raw_row`는 signature 유지 wrapper로 만든다. 관측기 `observation_for_slot`와 `_has_verification_evidence`는 **함수 안에서 지연 import**하던 기존 구조 유지. 새 Owner는 기존 facade를 import하지 않는다. 원본 `_number`, `market_epoch`, `_COLLECTOR_ABSENT_STATES`, `_COLLECTOR_VERIFIED_STATES`를 호출 시 facade에서 참조하게 한다.
- 결과 상태 3종을 변경하지 않는다: `availability=MISSING` + `never_attempted=True`는 **None(ABSENT)**; `LATE_MISSED/CORRUPT_STATE/미검증 시간`은 `integrity_failure=True`와 이유·시각·참고 관측값; `AVAILABLE/PARTIAL`이라도 검증 증거·index component가 없으면 INVALID, 두 검증이 모두 참일 때만 `ts,close,open,source,capture_status`를 반환한다. 실제 수집기·Kiwoom API 호출 금지.
- **확인된 실패 입력 추가:** `availability="AVAILABLE"`, 유효한 index 가격, fake `_has_verification_evidence=True`이지만 `market_epoch(index_row)=None`인 조합에서 현재 `int(None)` TypeError가 발생한다. 새 Owner의 최종 `ts` 구성 전에 market timestamp를 한 번 검증하여 이 경우 `integrity_failure=True`·사유 `market_timestamp_missing`(또는 기존 소비자와 호환되는 구체 사유)을 반환하고 **legacy fallback을 절대 허용하지 않는다**. 정상 VERIFIED timestamp/가격/소스 필드는 바꾸지 않는다. 실패 전 재현과 수정 후 JSON 계약을 둘 다 테스트한다.
- `tests/test_p15_collector_observations_extraction.py`: 가짜 `observation_for_slot` 및 검증 함수 주입으로 ABSENT/INVALID/VERIFIED/오류 시간/해당 index 누락·market timestamp None을 각각 비교; 새 Owner는 **350 LOC 이하**. 기존 `tests/test_q10_collector_fix3.py`, `tests/test_q10_reaction_reader_collector_integration.py` 정상/`-O` 통과 조건. 읽기 전용 mock/임시 파일만 사용.

## 3 — 동일 파일의 지수 시계열 파일 IO 분리 (개발·필수)

**SOURCE:** `reaction_reader.py::load_index_timeline` (대략 271~291행). **새 Owner:** `libs/reporting/baseline_samsung_hynix/forward_validation/index_timeline.py`.

- `load_index_timeline_impl(*, day,macro_root,index_name,facade)`로 기존 파일 읽기·JSON 파싱·시간 변환·중복 timestamp 마지막 값 선택·정렬 기능 본문을 MOVE. 기존 `load_index_timeline` 이름/키워드 인자는 wrapper 유지. Owner는 facade의 `_number`를 호출 시 사용. 파일 read는 호출될 때만 수행하며 import 자체는 IO 0.
- `tmp_path/day/*_macro_indicators.json` 가짜 파일로 ① 정상 입력 두 건의 timestamp 순서 ② 동시각 두 건에서 정렬 후 마지막 entry 선택 ③ JSON 손상/날짜 누락/인덱스 없음/숫자 변환 실패 건은 기존대로 skip ④ 빈 폴더 빈 리스트 ⑤ 입력 파일 수정 0을 확인. **확인된 예외:** JSON 배열 `[]`는 현재 `payload.get` AttributeError로 전체 로딩을 중단한다. 새 Owner에서 `isinstance(payload, Mapping)` 및 중첩 `korea_indices/indices`의 Mapping 여부를 `.get` 전에 확인해 비객체/비정상 schema 파일만 건너뛰고 다음 정상 파일을 계속 읽는다. malformed 배열+정상 객체가 함께 있을 때 정상 객체만 결과에 남고 입력 파일 변경 0이어야 한다. 정상 객체의 기존 `except` 범위·`open/high/low` falsy fallback·누락 volume None은 유지한다. 신규 `tests/test_p15_index_timeline_extraction.py` 및 정상/`-O`.
- 세 분리의 마지막에는 `reaction_reader.py` 자체 실제 물리 LOC와 세 신설 모듈 LOC, 분리 전후 call graph/참조, 종합 SOURCE SHA를 기록. **소스 줄 이동이 아니라 wrapper가 실제 새 Owner 함수를 호출하는지** 검증한다.

## 4 — 반응→점수→보고 전체 호출자 회귀 (새 결함 시 최소 수정)

**SOURCE:** `libs/reporting/baseline_samsung_hynix/forward_validation/{scoring.py,shadow_comparison.py,report.py,pipeline.py}` 및 1~3번의 wrapper.

- 합성 입력으로 `build_actual_reactions` → `score_semiconductor_signal`/해당 점수 함수 → `build_shadow_comparison` → `render_forward_validation_report`의 기존 진짜 소비자 호출을 확인한다. 해당 함수 signature가 정확히 다르면 **소스의 실제 연결 관계를 그대로 사용**, 가짜 adapter/미존재 함수를 만들어 PASS 내지 않는다.
- ① CLOSE가 없는 지수는 참고가격이 수익률/entry 결과에 섞이지 않음 ② VERIFIED collector CLOSE는 표시 가격·수익률 동일 ③ 09:00 volume=0 오프닝 제외 ④ 이전 종가 0·누락 ⑤ 결측 scoring 데이터가 `INSUFFICIENT_EVIDENCE`인 기존 경계 ⑥ 거래 없는 날/빈 목록 ⑦ 결과 행 정렬·표본 수·문장 출력이 기존 계약과 일치함을 확인한다.
- **실제 소스 결함을 명시적으로 수정:** `shadow_comparison.py::build_shadow_comparison`에서 POSITIVE expected row와 `points={"09:00":{"ts":1,"price":100},"CLOSE":{"price":110}}`, `path=[]`, `cost_pct=0`, `slippage_pct=0`을 입력하면 OBSERVED outcome의 `mfe_pct/mae_pct=None` 이후 summary의 `float(None)` TypeError가 발생한다(원본 127~128행). summary `average_mfe_pct/average_mae_pct`는 **관측 가능한 숫자만** 평균 내고 유효 관측 0건이면 `None`; `trade_count`/`average_return_pct`와 기존 정상 path 출력은 불변. 결측을 임의 `0.0`으로 대체하지 않는다. `tests/test_p15_forward_validation_parity_chain.py`에 빈 path 1건, 빈 path+정상 path 혼합 2건, 정상 path만 1건의 정확 기대 dict와 오류 재현→수정 후 PASS를 추가한다.
- 실제 결함이 재현되면 **이 범위의 A 소유 파일**에서만 최소 수정하고 수정 전 실패/수정 후 PASS 증거를 남긴다. 외부 네트워크·시장 실거래·운영 state·배포 실행 금지. 신규 `tests/test_p15_forward_validation_parity_chain.py` + 기존 `tests/test_q10_index_close_fallback.py`, `tests/test_q10_lead_market_forward_validation.py` 정상/`-O`.

## 5 — BTC 기존 성과·리포트 계약 보강 (후속 안전 작업)

**SOURCE:** `libs/reporting/baseline_btc_woori_tech/forward_returns.py`, `libs/reporting/baseline_btc_woori_tech/vnext/report.py`.

- 실제 함수 `attach_forward_returns`, `summarize`, `summarize_policy_variant`, `aggregate`, `render`를 사용해 임시·합성 데이터의 결측/0 기준/한 거래/여러 거래/입력 순서·정렬·표본 수·불변 입력을 검증한다. **현재 구현의 실제 출력에 근거한** 명시적인 기대값을 고정한다.
- 실질 코드 결함이 나오면 해당 A 소유 소스만 최소 수정. 재현되지 않으면 테스트만 보강하고 6번으로 이동. 새로운 투자 정책·시장 데이터 호출은 넣지 않는다. 신규 `tests/test_p15_btc_forward_report_parity.py`, 정상/`-O`.

## 6 — B 코드 독립 검증 (상대 브랜치 수정 금지)

- B **고정 SOURCE SHA** `801ca211b83d04d4dc38e78f394f57ffb5dd29e4`의 `libs/contracts/agent_outputs.py`에서 `_build_strategist_trace_summary`, `_build_scanner_trace_summary`, `build_strategist_output_artifact`, `build_scanner_output_artifact`를 임시 격리 복사본으로 독립 검증한다. B 소스에 어떤 쓰기·푸시도 하지 않는다.
- 기존 `tests/test_p161_agent_output_contract_freeze.py` 동결 오라클의 **변경 없는 실행**과, 이벤트 우선순위·누락뉴스·0 후보·runner-up tie-break·serializable 결과의 새 음성/경계 입력을 확인한다. 자체 소스 검증과 혼동하지 않고 B SOURCE SHA/실행 명령/기대값·실제값을 Issue #11에 보고한다. frozen fixture/CI·B 테스트 소스 변경 금지.
- B의 변경 SHA가 이후 도착해도 이번 검증 고정 SHA는 바꾸지 않는다. 신 SHA 전체 피어 수용은 다음 C03에서 새 지시로 배정한다. 기존 같은 입력·SHA scoped PASS의 기계적 반복 금지.

## 7 — 필수 실행·원격 보고

- **1~6 모든 과제는 독립적인 필수 이행 의무다.** 순서 없이 진행할 수 있으며 한 과제의 성공·실패·선행 결과를 기다리느라 다른 과제를 멈추지 않는다. **지시한 모듈 분리·호출자 회귀·BTC 검증·상대 peer 중 하나라도 미이행이면 이번 명령은 미완료**다. 작업자 스스로 '이만하면 됐다', '지난번 PASS가 있다', '몇 건 수정했으니 충분하다', '시간이 부족할 듯하다'고 판단해 조기 종료하거나 항목을 누락시키지 마라. 실제 동일 구현 완료가 원격 SHA와 테스트로 입증된 경우에만 VERIFIED_ALREADY; 과제 1~3은 새 Owner로 함수 본문을 실제 MOVE하고 wrapper를 연결해야 구현 완료다. 결함이 재현되지 않는 과제 4~5도 **명시한 전체 경계 테스트 실행은 필수**다. **오직 명시적 안전 위험·실제 도구/권한/환경 차단·플랫폼 실행 한도**에만 해당 항목을 BLOCKED/NOT_RUN으로 기록한다. 개별 차단은 나머지 항목의 중단 이유가 아니며 모든 다른 과제를 이어서 수행한다. 한도 도달 시 미완료 과제별 현재 코드 위치·명령·재개점을 정확히 남긴다. 시간·건수 할당량 없음.
- 매 수정 패키지마다 신규 표적 테스트 `python -m pytest -q -p no:cacheprovider <paths>`와 동일 테스트의 `python -O -m pytest -q -p no:cacheprovider <paths>` 양 모드를 **실제 실행**. CI 전체 PASS나 peer 전체 PASS를 부분 검증만으로 주장하지 않는다. 의존성 부재는 NOT_RUN/환경 차단.
- A 기존 작업 브랜치에 소유 코드·테스트만 커밋/푸시, 원격 HEAD·추가된 파일 blob까지 확인. Git CLI 인증 실패면 허용된 GitHub 연결 쓰기를 fast-forward 조건에서만 사용. `main`/`integration`/B 코드/새 브랜치/PR/force push/문서/CSV/RF/STATUS/동결 oracle 변경 금지.
- Issue **#11 댓글**에 실제 `START_KST,END_KST,ELAPSED_MIN` (추정 금지), **번호별** 바뀐 소스·테스트·before→after LOC·normal/-O exit·실제 원격 SHA·독립 peer SOURCE SHA·남은 안전 작업/차단 및 해제 담당 기록. 완료됐다고 판단한 번호는 증거로만 표시하고 지팀장 C05가 공식 완료 판정한다.
