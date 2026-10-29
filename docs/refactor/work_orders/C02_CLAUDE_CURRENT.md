# C02 — Claude A | 다음 실행 완결형 개발 명령

**실행:** 기존 `work/p15-a-reporter-pure-20261021`에서 1~6 **모두 필수**. 번호는 식별자이지 선행 순서·선택권·조기 종료 허가가 아니다. 설계 기준 A SOURCE `32d86ba1135d611d916fbb11d084e0cca0923858`. 이 SHA에는 직전 누적 입력 수정 1~2, preopen/pipeline/report 신규 테스트 3~5 및 B 고정 검증 6의 원격 변경·양 모드 결과가 보고되어 있으므로 **재실행하지 않는다**. 시작 시 자기 원격 HEAD와 현재 지시를 대조하고 이미 완료된 정확 SHA·범위는 재사용한다. 기존 진행 중 작업을 중단하지 말고 안전 체크포인트 후 이 지시를 적용한다. 허용 A 소유 소스/테스트 외 문서·CSV·정책·동결 oracle·타인 브랜치 변경, 실네트워크·브로커·주문·운영 State/DB/RunLab·Step5C/UEF 효과, force-push 금지. 모든 파일 효과는 `tmp_path`·fake/deny-socket으로 격리한다.

## 1 — Latent Forward 캐시 경로의 명시적 격리 주입 (개발·필수)

- **확인 SOURCE:** `libs/reporting/opening_rank1_shadow/latent_forward.py::build_latent_reactivation_forward/_cache_read/_cache_write` (A `32d86ba`). 현재 `cache_root=Path("data/research/opening_rank1_shadow/latent_forward_candles")`가 CWD 상대경로로 고정돼 `output_root`가 임시 경로여도 후보 캔들 캐시를 다른 곳에 쓸 수 있다. `_trigger_day_status`는 `output_root.parent/<day>/opening_rank1_shadow_daily.json`의 VALID를 요구한다.
- **수정:** 공개 `build_latent_reactivation_forward`의 기존 keyword-only 인자를 유지하며 선택적 `cache_root: Path | None = None`만 끝에 추가. `cache_root is None`이면 **기존 상대 캐시 경로를 그대로 사용**해 호출자/기존 운영 캐시 읽기·쓰기 동작을 바꾸지 않는다. 명시 Path를 주면 `_cache_read/_cache_write` 모두 정확히 그 루트만 사용. 기존 결과 JSON/MD, summary, trigger 정렬·실패 처리, `allow_fresh_fetch` 전달 의미 불변. 기본 경로의 전면 재배치는 기존 소비자·캐시 마이그레이션 승인 전 **DEFER**(현재 구현 보존); 명시 temp 인자만 새 격리 경계다.
- **신규 `tests/test_p15_latent_forward_cache_root_injection.py`:** `tmp_path/opening/<day>/opening_rank1_shadow_daily.json`에 `day_status=VALID`, `output_root=tmp_path/opening/latent` 사전 생성, watch 1개/first_signal_evidence epoch·symbol 설정, `cache_root=tmp_path/cache`, fake `load_opening_candles`로 해당 symbol 분봉 2~3행 반환, `load_broker_cost_profile/build_evaluation_cost_bases` fake. 기대 `tmp_path/cache/<day>/<symbol>.json`만 생성, 두 번째 호출 캐시 재사용으로 fake fetch 1회만, 결과 `summary`/JSON/MD 동일, CWD 기본 `data/research` 경로 생성 0. `allow_fresh_fetch=False`가 fake에 그대로 전달되고 유효하지 않은 trigger-day는 캐시/네트워크 없이 제외. default(None) 경로는 운영 파일을 건드리지 않으므로 **실행하지 말고** 코드상 기존 경로 불변만 정적 확인.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_latent_forward_cache_root_injection.py` 및 `python -O -m pytest -q -p no:cacheprovider tests/test_p15_latent_forward_cache_root_injection.py`. CWD 외부 쓰기/실수집 호출 시 즉시 중단·증거 보고하고 다른 안전 과제로 이동.

## 2 — Q9 비교기의 비객체 파일·불량 rank 국소 격리 (개발·필수)

- **확인 SOURCE:** `libs/reporting/baseline_samsung_hynix/q9_comparison.py::_load_q9_rows/build_q9_role_comparison/representative`. JSON `[]`/null 후 `payload.get` 예외, `q9_decision_candidates` 비-list, `rank="bad"`에서 `int(float(...))` ValueError로 **전체 비교 중단**. `B_STRATEGIST_RANKED`의 명시 `q9_selected` 우선과 `ROLES/HORIZONS`는 보존한다.
- **수정:** JSON 로드 뒤 `Mapping` 아닌 파일 skip, candidates는 list만 반복, 행은 Mapping+허용 role만 유지. representative의 rank 키 변환은 TypeError/ValueError/비유한 값을 최하위 sentinel(999)로 취급하여 유효 rank가 먼저 선택되게 하고 안정적인 기존 순서 tie-break 보존. 명시 selected 우선은 유지. 다른 유효 window/role 계산을 불량 한 행 때문에 중단하지 않는다. baseline_summary 호출자/반환 schema/signature는 그대로.
- **신규 `tests/test_p15_q9_malformed_rank_contract.py`:** temp day에 null/[]/문자열 JSON, candidates=object, 정상 P/A/B/C 네 역할 window, A 역할 rank="oops"와 rank=1을 섞고 B selected=True를 별도 제공. `load_q9_forward_candles`와 `attach_forward_outcomes`는 fake로 대체해 네트워크/State 쓰기 0. 기대 `comparable_complete_window_count=1`, 역할 4개×기존 horizon 개수, 유효 rank와 selected 우선, 기존 정상 샘플의 `q9_net`/count 불변, 파일 hash 불변.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_q9_malformed_rank_contract.py`; `python -O -m pytest -q -p no:cacheprovider tests/test_p15_q9_malformed_rank_contract.py`.

## 3 — Q9 candle recovery의 명시적 offline 호출자 옵션 (개발·필수)

- **확인 SOURCE:** 같은 `q9_comparison.py::_load_q9_rows`는 `load_q9_forward_candles(...allow_fresh_fetch=True)`를 하드코딩하며 `build_q9_role_comparison` 호출자는 비활성화할 수 없다. 실제 수집/네트워크는 이 회차에 호출하지 않는다.
- **수정:** `_load_q9_rows`와 `build_q9_role_comparison`에 **keyword-only** `allow_fresh_fetch: bool = True`를 추가하고 전달한다. 기존 호출자에 인자 추가를 요구하지 않아 기존 default 동작/공개 반환값은 불변. `False`에서는 `load_q9_forward_candles`로 정확히 False를 전달한다. 호출자나 실행 기본 설정을 일괄 False로 바꾸지 않는다.
- **신규 `tests/test_p15_q9_offline_optout.py`:** temp P/A/B/C 입력, fake `load_q9_forward_candles`로 kwargs 계측. 명시 False → False 1회, 생략 → True 1회(둘 다 fake, 실제 네트워크 0), 결과 schema/count 동일. `attach_forward_outcomes`도 fake로 고정. 불량 rank 테스트와 서로 다른 입력 경계를 증명.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_q9_offline_optout.py tests/test_p15_q9_malformed_rank_contract.py`; `python -O -m pytest -q -p no:cacheprovider` 동일 경로. 두 작업은 같은 소스 파일이므로 충돌 없이 한 코드 커밋으로 묶어도 각 테스트는 필수.

## 4 — 일괄 진단 writer의 zip 무음 절단 차단 (개발·필수)

- **확인 SOURCE:** `libs/reporting/quant_trade_diagnosis/writer.py::write_quant_trade_diagnoses_for_day`에서 `resolved_dirs/models/evaluations/attributions` 네 목록을 `zip`해 길이가 다르면 일부 거래만 기록하면서 `trade_count != written_count`로 정상처럼 반환한다. `write_quant_trade_diagnosis`의 기존 JSON/Markdown 포맷·경로는 유지한다.
- **수정:** 네 목록 생성 완료 직후 **어떤 `write_quant_trade_diagnosis` 호출보다 먼저** 길이 일치를 검증하고 불일치면 목록별 개수를 포함한 `ValueError`를 발생시켜 0건 쓰기. 같은 길이인 경우 현재 순서·반환 스키마·각 보고서 bytes를 유지한다. 실제 `trade_dirs=[]`가 fallback 되는 기존 `or` 동작은 이 작업에서 별도 정책 변경하지 않는다.
- **신규 `tests/test_p15_quant_diagnosis_batch_alignment.py`:** temp reports_root, trade dirs 2, models 2, evaluations 1, attributions 2 → ValueError와 `reports/quant_trade_diagnosis.*` 생성 0; 2/2/2/1도 동일. 2/2/2/2는 fake `build_quant_trade_diagnosis`와 temp write로 `trade_count=written_count=2`, 거래 순서/파일 hash·기존 반환 키 유지. broker·real trades 경로 사용 금지.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_quant_diagnosis_batch_alignment.py`; `python -O -m pytest -q -p no:cacheprovider tests/test_p15_quant_diagnosis_batch_alignment.py`.

## 5 — 모델 카드 생성의 비객체 입력·잘못된 context length 방어 (개발·필수)

- **확인 SOURCE:** `libs/llm/model_catalog_store.py::build_model_cards_payload/_derive_tags`. top-level `"junk"`는 마지막 `openrouter_payload.get("model_count")`에서 AttributeError, `context_length="bad"`는 `int` ValueError. 모델 목록에 잘못된 한 행이 있어도 정상 카드 전부를 중단할 필요는 없다.
- **수정:** 입력이 dict가 아니면 빈 유효 payload로 정규화하고 `source_model_count=0/card_count=0/cards=[]`를 반환. `data`는 list만 순회하고 각 row Mapping/모델 ID 유효성 검사. `context_length`는 안전한 비음수 int 또는 0으로 정규화해 `_derive_tags`와 카드의 `context_window`가 동일 값을 쓰게 한다. 잘못된 `model_count`는 유효 카드 수로 fallback. `generated_at/source`, 정렬, 기존 override·정상 카드 bytes(시간 필드 제외), 원래 함수 signature 보존. API 호출·실파일 저장 없음.
- **신규 `tests/test_p15_model_catalog_malformed_cards.py`:** top-level None/"junk"/[] → 카드 0, count 0; `data=[{"id":"provider/good","context_length":2048},{"id":"provider/bad","context_length":"n/a"},null]` → 카드 2, good 2048, bad 0, long_context tag 없음, 정렬, `json.dumps(...allow_nan=False)` 가능, 입력 불변. 유효 context 200000은 long_context 유지. static override 기존 행 회귀를 별도 assert.
- **검증:** `python -m pytest -q -p no:cacheprovider tests/test_p15_model_catalog_malformed_cards.py`; `python -O -m pytest -q -p no:cacheprovider tests/test_p15_model_catalog_malformed_cards.py`.

## 6 — Codex B 정확 SOURCE 독립 검증 (필수·B 쓰기 금지)

- **고정 B SHA:** `44b36a233f42158288d564de3fe026a4e6701e76` (원격 존재 확인). 별도 임시 detached clone/archive에서 `libs/core/log_maintenance.py::apply_log_move_candidates`, `libs/core/event_logger_compat.py::get_event_logger`, `scripts/maintenance/sync_legacy_brief_llm.py::main`만 신규 경계로 독립 확인. 이전 B 동일 SHA의 정상 충돌·이동/동결 16 PASS는 **재실행하지 않는다**.
- **새 독립 입력:** (a) `tmp_path/logs`의 source `../outside.txt`, target `../outside.txt`, 외부 symlink 각 사례 → 외부 파일 SHA/내용/목록 불변, 뒤 정상 후보 계속 이동; 현재 구현이 실패하면 **발견된 FAIL**로 보고하고 B 코드 고치지 않는다. (b) 실제 EventLogger + temp `EVENT_LOG_PATH`: start/end JSONL 동일 run_id, 두 인스턴스 구분, fake keyword/positional/noarg constructor 호환; (c) brief CLI는 명시 tmp reports_root에서 primary 없음/있음 및 두 번 실행, 입력/파일 목록 무변경, JSON trade_count/status 확인.
- **검증:** 격리 clone에서 `python -m pytest -q -p no:cacheprovider <새 독립 probe 파일>`와 `python -O -m pytest -q -p no:cacheprovider <동일 파일>`. probe는 별도 scratchpad에서만 작성, B 저장소 수정·커밋·푸시 0. 새 B HEAD가 나와도 이번 fixed SHA를 바꾸지 않는다. 정확 명령·exit·PASS/FAIL·입력/기대/실제·미검증 원래 범위를 #11에 보고. 발견된 보호/외부 파일 위험은 즉시 C03/C05에 알리고 운영 실행 금지.

## 공통 검증·보고·중단 규칙

1~6 **전부 필수**이며 부분 PASS·커밋·한 항목 BLOCKED로 종료 금지. 차단된 항목은 정확 함수·입력·실패 명령·해제 담당·안전 재개점만 기록하고 다른 모든 안전 항목을 진행한다. 새 코드/테스트는 `python -m pytest -q -p no:cacheprovider <위 정확 경로>` 및 `python -O -m pytest -q -p no:cacheprovider <같은 경로>`로 각각 검증; pytest assertion rewriting을 -O에서 무효라고 일반화하지 않는다. 실제 함수 LOC 전/후·caller 연결·수정 전 FAIL→수정 후 결과·정확 소스/테스트 경로를 남긴다. 허용 A 브랜치에 소유 코드/테스트만 fast-forward commit/push 후 원격 HEAD와 blob 재조회. 인증 실패면 BLOCKED로 기록하되 다른 안전 항목은 계속하고 force push/새 브랜치/문서 변경 금지.

#11에 **실측** `START_KST/END_KST/ELAPSED_MIN`(없으면 `NOT_VERIFIED`), 1~6 각각 `IMPLEMENTED|VERIFIED_ALREADY(정확 SHA)|BLOCKED|NOT_RUN`, 정상/-O 명령·exit, SOURCE SHA, peer 고정 SHA, 마지막 진행 함수/다음 안전 함수, 30분 미만이면 사실에 근거한 사유를 기록. 시간은 예약 길이/댓글 시각/pytest 초로 추정·합산하지 않는다. 30분은 감사 신호이지 강제 실행시간이 아니다. 실제 모든 지정 과제 완료, 전부 실증 BLOCKED 또는 플랫폼 실제 한도 외에는 종료하지 않는다.
