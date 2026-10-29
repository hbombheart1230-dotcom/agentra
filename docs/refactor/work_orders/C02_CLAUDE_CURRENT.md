# C02 — Claude A | 다음 실행 완결형 개발 명령

**실행:** 기존 `work/p15-a-reporter-pure-20261021` 브랜치에서 과제 1~6 **모두** 실행한다. 번호는 식별자이며 선행 순서·선택권·조기 종료 기준이 아니다. 직전 지시의 1~6은 원격 `d30c67abc03a8c6b33909558f624242c76ab979f`에서 함수 MOVE·수정·테스트·상대 고정 SHA peer까지 보고되어 **다시 실행하지 않는다**. 새 지시 설계 기준 SOURCE는 위 SHA; 시작 시 최신 HEAD와 해당 구현을 확인해 동일 구현·정확 SHA/범위 결과는 재사용하고 새 경계로 진행한다. 허용된 A 소유 소스·테스트 외 문서/RF/큐/CSV/동결 oracle, 타인 브랜치, 운영 상태·계좌·Broker·Step5C·UEF·RunLab 및 실네트워크 수정·호출 금지. 테스트는 `tmp_path`, fake provider, fake state, socket deny로 격리한다. 진행 중인 작업은 안전 체크포인트까지 마친 뒤 새 지시와 대조한다.

## 1 — Q10 누적 입력의 비객체 JSON·outcomes 오염을 안전하게 격리 (개발·필수)

- **SOURCE:** `libs/reporting/baseline_samsung_hynix/forward_validation/cumulative.py::build_cumulative(root)` (현재 약 71행). `root.glob("*/q10_forward_validation/q10_shadow_entry_comparison.json")`을 정렬 순회하며 JSON 읽기 후 바로 `payload.get`, `outcomes` 각 `row.get`을 호출한다. JSON `[]`, `null`, `"text"`, `outcomes=[null,7,{}]`는 현재 `AttributeError` 또는 비정상 집계를 일으킬 수 있다.
- 신규 `tests/test_p15_q10_cumulative_malformed_inputs.py`: `tmp_path/<ACTIVATION_DAY 이상 날짜>/q10_forward_validation/q10_shadow_entry_comparison.json`에 (a) 비객체 최상위 3종, (b) 객체이지만 `outcomes` 비-list, (c) list에 비-Mapping 원소, (d) 깨진 JSON, (e) 정상 객체 하나를 서로 다른 날짜에 배치. **기대:** 불량 파일/행만 건너뛰고 정상 `OBSERVED` 1개만 집계, `day_count=1`, `observed_outcome_count=1`, 날짜 정렬, 입력 파일 SHA256·디렉터리 목록 불변, 예외 0. `PENDING` 행은 집계 제외. `ACTIVATION_DAY` 이전은 무시한다.
- `build_cumulative`의 `payload.get` 전에 `isinstance(payload, Mapping)`, `outcomes` 반복 전에 `list`와 각 `Mapping`을 확인해 **읽기 전용 fail-closed**. 기존 유효 입력·반환 schema·함수 signature·정렬·그룹 키·IO 경로 유지. `pipeline.py` 호출자는 수정하지 않는다. 기존 정상 값에 대한 전후 JSON 고정 비교를 추가한다.

## 2 — Q10 누적 수익률 결측/비숫자 OBSERVED 행 (개발·필수)

- **SOURCE:** 동일 `cumulative.py::build_cumulative`에서 `float(row["net_eod_return_pct"])`와 `float(row.get("mfe_pct") or 0.0)`·`mae_pct`를 수행한다. `OBSERVED`이지만 `net_eod_return_pct=None` 또는 `"bad"`이면 현재 집계 전체가 실패한다. 1번과 같은 파일을 **중복 수정하지 말고 하나의 정상 커밋으로 결합 가능**하되 각 테스트/입력 계약은 별도로 증명한다.
- 신규 `tests/test_p15_q10_cumulative_numeric_boundary.py`: 동일 그룹의 유효 `net_eod_return_pct=2.0,-1.0`, `mfe_pct=3.0,1.0`, `mae_pct=-0.5,-2.0`와 결측/비숫자 수익 행을 섞는다. **기대:** 유효 2건만 `trade_count=2`, `average_return_pct=0.5`, `median_return_pct=0.5`, `profit_factor=2.0`, `win_rate=50.0`, `average_mfe_pct=2.0`, `average_mae_pct=-1.25`; `observed_outcome_count`/days는 실제 채택 행만 반영. 유효 행이 전혀 없으면 `summary=[]`, 0 count, 예외 0. 기존 유효 결과 불변.
- **구현:** `float` 변환 실패 행은 집계 전 제외하고, 유효 관측을 임의 `0.0`으로 채워 수익률을 왜곡하지 않는다. `mfe/mae` 결측 처리의 기존 의미(0 취급)는 별도 승인 없이 바꾸지 않는다. NaN/inf 입력이 발견되면 그 실제 사례·후속 계약 판단을 보고하고 숫자 정책을 임의 확장하지 않는다. 모든 IO는 `tmp_path` 읽기만.

## 3 — Q10 preopen capture 시간 창·기존 스냅샷 보존 (개발·필수)

- **SOURCE:** `libs/reporting/baseline_samsung_hynix/forward_validation/pipeline.py::_capture_window/_preopen_snapshot/capture_q10_preopen_snapshot` (약 200행 전체 파일). 기존 `_capture_window`는 08:50~08:59:59 KST, `_preopen_snapshot`은 기존 유효 JSON 우선, 시간 전 `WAITING` 무쓰기, 시간 후 `MISSED` snapshot 저장, 시간 내 fake provider `capture(as_of=now)` 호출 후 `CAPTURED` 또는 `DATA_UNAVAILABLE`.
- 신규 `tests/test_p15_q10_preopen_capture_temp_contract.py`: `day="2026-10-29"`, 명시 `now=datetime(...,tzinfo=KST)`, `reports_root/state_path` 모두 `tmp_path`, fake `LeadMarketProvider.capture` 호출 횟수 계측. 08:49:59 → `WAITING`, 파일 없음, provider 0회; 09:00:00 → `MISSED`/reason `08:50_preopen_capture_window_missed_no_backfill`, 지정 JSON 한 개 생성, provider 0회; 08:50:00·08:59:59의 **별도 tmp 루트** → provider 1회, 스냅샷 상태/경로 반환. 같은 경로에 유효 snapshot을 미리 쓰면 호출 0회, 내용 해시 보존·backfill 금지. provider가 전부 `UNAVAILABLE`이면 `DATA_UNAVAILABLE`, `CAPTURED`로 둔갑 금지. 사전 활성일은 `NOT_ACTIVE_PROSPECTIVE_ONLY`/무쓰기.
- 기존 반환 `q10_preopen_capture_status/day/captured_at_kst/reason/path`와 JSON 키 불변. 결함 재현 시 `pipeline.py` 최소 수정. `YFinanceLeadMarketProvider` 실제 생성/호출 금지(항상 fake 인스턴스 주입).

## 4 — Q10 종단 pipeline의 정확한 temp 파일/호출자/재실행 계약 (개발·필수)

- **SOURCE:** `pipeline.py::build_q10_forward_validation`, `reaction_reader.py::build_actual_reactions`, `expected_actual.py::build_expected_actual`, `shadow_comparison.py::build_shadow_comparison`, `cumulative.py::build_cumulative`, `report.py::render_forward_validation_report`. 현재 출력 4 JSON(스냅샷·reactions·expected·shadow) + 1 Markdown + 상위 `output_dir.parent/q10_forward_validation_cumulative.json`. **원래 호출자 경로와 signature를 그대로 유지**하고 fake adapter를 만들어 PASS 내지 않는다.
- 신규 `tests/test_p15_q10_forward_pipeline_temp_contract.py`: `output_dir=tmp_path/reports/evaluation/baseline_samsung_hynix/2026-10-29`, `state_path=tmp_path/state.json`, `macro_root=tmp_path/macro`, `candle_map={}`, `cost_pct=0,slippage_pct=0`, fake provider + 08:51 KST로 진짜 함수 호출. 반환 경로 6개가 **전부 tmp_path 안**에 있고 존재, 각 JSON에 schema/program/day 등 기존 필드, 보고서에 `prospective_shadow_only`와 disabled-orders 문구, 임의 주문/실네트워크/운영 CWD 파일 0을 확인한다. 같은 fake 입력으로 재호출하면 누적 `day_count`/채택 outcome 수가 부풀지 않고 기존 스냅샷 hash가 동일해야 한다. `day<ACTIVATION_DAY`이면 상태 `NOT_ACTIVE_PROSPECTIVE_ONLY`, 새 파일 0.
- `_write`의 `.tmp`→replace, `_read`의 malformed fallback은 기존 동작을 보존한다. 테스트가 실제 호출자 실패를 재현할 때만 A 소유 함수 최소 수정. 운영 파일·실수집기 호출·Step5C 정책 변경 금지.

## 5 — Reporter Markdown 결측/관측 불가 표시 계약 (개발·필수)

- **SOURCE:** `libs/reporting/baseline_samsung_hynix/forward_validation/report.py::_value/render_forward_validation_report` (약 127행). 현재 `None -> "-"`, `float -> 소수점 4자리`, `unverified_observation`은 `Captured But Not Calculation-Usable` 표에 표시, 수익/스코어 계산에 사용하지 않는다.
- 신규 `tests/test_p15_q10_report_missing_value_contract.py`: 합성 `preopen={"capture_status":"DATA_UNAVAILABLE","signals":{}}`, `reactions={"targets":{"KOSPI":{"points":{"CLOSE":{"price":None,"unverified_observation":{"price":101.2,"capture_status":"PENDING","observed_at_kst":"2026-10-29T15:25:00+09:00"}}},"forward_windows":{"09:00":{"return_to_close_pct":None,"mfe_pct":None,"mae_pct":None,"status":"PARTIAL"}}}}}`, 빈 expected/shadow/cumulative를 넣어 `render_forward_validation_report` 직접 호출. **기대:** `DATA_UNAVAILABLE`, `Captured But Not Calculation-Usable`, `101.2000`, `PENDING`, `PARTIAL`, missing return `-`, `prospective_shadow_only`, disabled-orders 문구 포함; `None`이 `0.0000`으로 표시되지 않음. 정상 수익 1.25는 `1.2500%`, 정렬/표 머리글·마지막 newline 유지, 입력 dict 불변.
- 본문에서 unverified price를 계산 가능한 CLOSE로 승격하거나 새로운 거래 정책을 추가하지 않는다. 실제 결함 시 report renderer만 최소 수정; 기존 호출 signature/문장 계약 보존.

## 6 — Codex B 고정 SOURCE 독립 검증 (필수·상대 쓰기 금지)

- **고정 SOURCE SHA:** `44b36a233f42158288d564de3fe026a4e6701e76` (B). 격리 임시 detached 복사본에서 `libs/contracts/agent_outputs.py`, `libs/contracts/agent_output_parts/{strategist_projections.py,scanner_projections.py}`, `libs/core/log_maintenance.py`, `scripts/maintenance/run_log_maintenance.py`, `tests/test_p15_{strategist_projection_extraction,scanner_projection_extraction}.py`, `tests/test_log_maintenance.py`를 읽고 실행한다.
- 독립 신규 입력: facade `_clip/_safe_float` monkeypatch가 새 Owner 함수까지 전달되는지; event ranking의 비-dict row 제외, custom tie-break/selection reason의 **현행 불일치**는 구체 출력만 기록(정책 수정 금지); log destination 이미 존재할 때 원본·목적지 모두 hash 보존; `shutil.move` 한 후보 실패 후 다음 후보는 `moved`, `run_log_maintenance.main(["--log-root",str(tmp_path/logs),"--apply","--json"])`의 `moved_total`이 실제 이동 수와 같고 `move_results`를 제공하는지. 운영 root가 아닌 tmp에서만 수행.
- 동결 `tests/test_p161_agent_output_contract_freeze.py`는 **읽기·변경 없는 실행만**. 같은 SHA/동일 범위에 이미 유효한 PASS 증거가 있다면 재실행하지 말고 그 증거를 명시. B 코드/테스트 수정·푸시 0. 정상·`-O` 명령·기대/실제·정확 SOURCE SHA·검증 범위와 미검증 원래 범위를 Issue #11에 기록. 새 B SHA가 도착해도 이 고정 SHA를 임의로 변경하지 않는다.

## 공통 검증·종료·원격 보고

1~6 전부 필수. 한 항목 `BLOCKED`면 정확 함수/입력/실패 명령/해제 담당/재개점과 함께 격리하고 **다른 모든 안전 항목을 계속 수행**. 이미 유효한 같은 SHA·범위 PASS 재실행·빈 커밋·무의미한 이력 복사 금지. 신규/변경 테스트는 `python -m pytest -q -p no:cacheprovider <exact paths>` 및 `python -O -m pytest -q -p no:cacheprovider <same paths>`를 실제 실행하고 exit/FAIL/PASS 기록. 변경 전/후 실제 LOC·함수·call graph·입력/기대/실제와 오류 재현을 제출. 본인 A 브랜치에 허용 코드·테스트만 fast-forward 커밋·푸시하고 원격 HEAD/변경 blob 재확인. C04 통합/CI, C05 수용/DONE은 수행하지 않는다.

#11 댓글에 **실측** `START_KST/END_KST/ELAPSED_MIN`(없으면 `NOT_VERIFIED`), 각 번호별 `IMPLEMENTED|VERIFIED_ALREADY(정확 SHA)|BLOCKED|NOT_RUN`, 테스트 normal/-O 명령·exit·SOURCE SHA, peer 고정 SHA, 미완료 번호·다음 안전 함수/재개점과 30분 미만 종료 사유를 기록. 예약 간격·댓글 시각·테스트 시간으로 경과시간을 추정하지 않는다. 30분은 감사 경보이지 강제 실행시간이 아니다. 모든 지정 안전 과제 완료 또는 실증 차단/실제 플랫폼 한도 외에는 종료하지 않는다.
