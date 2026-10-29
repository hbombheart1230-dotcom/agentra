# C01 — Codex B | 다음 실행 완결형 개발 명령

**실행:** 기존 `work/p15-b-operator-structure-20261022` 브랜치에서 본문 1~6을 **전부** 수행한다. 번호는 식별자이며 선행 순서·선택권·종료 허가가 아니다. 이 지시를 읽고 이미 시작한 이전 작업이 있으면 그 작업을 끊지 말고 안전 체크포인트까지 끝낸 후 본문과 대조한다. 최신 B 원격 SOURCE `0d8e2777b4af087219878de48df48a6c244277f9`; 시작 시 최신 원격 HEAD를 확인해 이미 구현된 내용은 정확 SHA·테스트 증거로만 인정하고 중복 커밋·동일 SHA/범위 PASS 반복 없이 남은 입력/경계로 진행한다. 소유 코드·테스트 외 문서, RF, 큐, CSV, 동결 오라클, 운영 로그·DB, 타인 브랜치 수정 금지. 실계좌·Broker·Step5C·UEF·RunLab/운영 루트·실네트워크 호출 및 force-push 금지. 명시한 `tmp_path`·fake·격리 환경만 사용한다.

**C03 2026-10-29 긴급 P0 처리/남은 개발 재배정:** 홍사장 요청에 따른 지팀장 직접 안전 보정으로 B 원격 `0d8e2777b4af087219878de48df48a6c244277f9`에 `libs/core/log_maintenance.py`의 루트 탈출 경로 차단을 커밋 `a8b3835c`, 격리 회귀 `tests/test_p15_log_move_root_boundary.py`를 커밋 `0d8e2777`로 푸시하고 두 blob/원격 HEAD 확인. 경로 변형 12개는 **독립 최소 재현 환경** normal 12 PASS/`python -O` 12 PASS; 저장소 트리 전체 pytest·기존 test_log_maintenance·hosted CI 및 A 신 SHA 독립 검증은 **NOT_RUN**이므로 C4/DONE 절대 승격 금지. 이 긴급 수정은 B 전체 RF owner 계약 C1도 완료한 것이 아니다. **#2의 동일 구현 재시도 금지**; B는 새 SHA에 대한 저장소 내 정확 `tests/test_p15_log_move_root_boundary.py tests/test_log_maintenance.py` normal/`-O`를 실행하고 결손만 수정·원격 푸시한다. 비격리 symlink 경합은 추가 권한 판단 전 SAFETY_HOLD. **나머지 미완료 필수 과제 #1/#3/#4/#5/#6은 모두 지속 수행**(기존 1번 MOVE만 VERIFIED_ALREADY); 다른 SHA `fffa761a` peer로 A 고정 `d30c67ab` peer #6 대체 금지. 로컬 HANDOFF 문서 커밋은 개발 산출물이 아님. Git 인증 장애는 해당 push만 BLOCKED, 다른 안전 과제 계속.

## 1 — Strategist/Scanner 추출 후 원래 출력 계약 검증·결손 수정 (개발·필수)

- **확인한 실제 구조:** `libs/contracts/agent_outputs.py`의 4 Strategist + 3 Scanner 함수 본문은 `libs/contracts/agent_output_parts/strategist_projections.py`(248행), `scanner_projections.py`(162행)로 이미 이동됐다. 기존 facade에는 같은 공개/내부 signature wrapper가 남는다. **다시 MOVE하지 않는다.** 현행 `tests/test_p15_strategist_projection_extraction.py`(1개), `tests/test_p15_scanner_projection_extraction.py`(1개)는 소수 입력만 검사한다.
- `tests/test_p15_strategist_projection_extraction.py`에 `_build_strategist_trace_summary`의 누락 headline/VIX·빈 reason_chain·0값·event 우선순위와 `_build_strategist_news_evidence_ranked`, `_build_strategist_decision_frame`의 실제 signature를 소스에서 확인한 입력/기대 dict를 추가한다. `tests/test_p15_scanner_projection_extraction.py`에 `_build_scanner_trace_summary`의 0/1/3 후보, positive/negative factors, runner-up 두 개 제한, `_build_scanner_candidate_ranking_table`의 event rows 중 비-dict 필터·custom tie-break, `_build_scanner_candidate_selection_reason`의 빈 후보·fallback을 추가한다. fixture 기대값은 **분리 이전 `801ca211b83d04d4dc38e78f394f57ffb5dd29e4`의 원본 출력** 또는 이미 검증된 계약값에서 고정하고, 현재 출력 자체를 무조건 기대값으로 복사하지 않는다.
- wrapper를 monkeypatch한 `agent_outputs._clip/_safe_float/_listify`가 호출 시 새 Owner에 전달되는지 검증. public `build_strategist_output_artifact` / `build_scanner_output_artifact`의 JSON 직렬화·입력 불변을 추가. **A가 관찰한 custom ranking tie-break와 selection reason tie-break 불일치, ranking runner-up과 preview runner-up 불일치는 원래 의미가 불명확하므로 즉시 출력 정책 변경 금지**: 구체 입력/실제 두 필드/호출자 영향만 보고하고 C05 정책 승인 전 DEFER. wrapper/Owner 회귀가 실제 실패하면 해당 B 소유 코드만 최소 수정.
- `tests/test_p161_agent_output_contract_freeze.py`는 변경 금지. 추출 이후 SHA에서 **최종 완료 결과가 없는** frozen 검증을 정상·`-O`로 수행하되 플랫폼 실제 한도로 중단되면 결과 `NOT_VERIFIED`, 정확 중단점 기록. 이미 유효한 동일 SHA/범위 결과가 나중에 확인되면 재실행하지 않는다.

## 2 — 로그 이동 후보 루트 탈출 안전 패치 **원격 반영, 저장소 검증/독립 peer 잔여**

- **현재 프로덕션 SHA** `0d8e2777b4af087219878de48df48a6c244277f9` (B 기존 브랜치). `apply_log_move_candidates`는 `Path(log_root).resolve()`를 기준으로 두 경로의 절대/빈/`..`/루트 자체/외부 symlink를 `relative_to(root)`로 사전 배제하고 `skipped_unsafe_path`로 다음 후보를 계속 처리하도록 보정됐다. 기존 `skipped_missing_source`, `skipped_destination_exists`, `OSError→failed` 계약은 코드에서 보존. 실제 로그 루트나 운영 파일에 실행한 적 없다.
- **원격 테스트** `tests/test_p15_log_move_root_boundary.py`는 source/target traversal, symlink, absolute/empty/root 6 variant, 후속 정상 이동, 충돌/OSError 뒤 정상 진행을 다룬다. 격리 최소 코드/테스트 replica normal **12 PASS** / `python -O` **12 PASS**; **저장소 원본 import/기존 회귀 및 전체 CI 미실행**. B 작업자는 repo 정확 HEAD에서 `python -m pytest -q -p no:cacheprovider tests/test_p15_log_move_root_boundary.py tests/test_log_maintenance.py` 및 `python -O -m pytest -q -p no:cacheprovider ...`를 실행하고 실패하면 B 소유 코드/테스트만 수정한다. 반복 PASS 증거는 SHA 기준 재사용한다.
- **C4 독립 검증:** Claude A가 정확 B `0d8e2777b4af087219878de48df48a6c244277f9`의 위 3종 위험과 기존 정상/충돌 및 2차 symlink/missing-root 경계를 새 temp 격리에서 재검증해야 함. `A #11 6488643694`의 구 B SHA 3 FAIL은 패치 성공 증거가 아님. 검사→move 사이 symlink 경합은 완전 차단을 주장하지 말고 C03/C05에 추가 HOLD로 보고. `--apply`/비격리 root 금지 불변.

## 3 — brief LLM inspection CLI의 누락·중복·비쓰기 계약 (개발·필수)

- **SOURCE:** `scripts/maintenance/sync_legacy_brief_llm.py::_iter_trade_dirs/_sync_trade/main`. 현재 `--reports-root` 절대경로, `--day`, `--json`, `--dry-run`으로 canonical 존재 여부만 출력한다. 기존 `tests/test_rf066_sync_legacy_brief_llm_cli.py`의 단일 `20261029/TRD_1` dry 사례는 유효하므로 **반복하지 않는다**.
- 신규 `tests/test_p15_sync_legacy_brief_no_write_cli.py`: `tmp_path/reports/trades/2026-10-01/T1/reports/brief_llm_response.json`를 만들고 (a) 빈 day는 `trade_count=0, rows=[]`, (b) primary 있음은 `canonical_present`/절대 `canonical_path`, (c) primary 없음은 `skip_no_primary`, (d) dry/non-dry 및 2회 반복은 모든 입력 bytes·파일 목록 변화 0, (e) stdout JSON은 `ok=True,day,reports_root,dry_run,trade_count,rows[*].status`, exit 0을 검증한다. 실제 `iter_trade_dirs`가 어떤 디렉터리를 반환하는지 구현을 읽어 fixture를 맞추고 없는 API를 꾸미지 않는다.
- `scripts/maintenance/sync_legacy_brief_llm.py`에서 재현된 결함만 최소 수정. 기본 `reports` 경로/운영 root 사용 금지, fake/temp 외 효과 0. 정상·`-O` 양 모드.

## 4 — 유지보수 CLI의 dry/apply 집계·부분 실패 계약 (개발·필수)

- **SOURCE:** `scripts/maintenance/run_log_maintenance.py::main/_load_candidates`, `libs/core/log_maintenance.py::write_log_inventory/apply_log_move_candidates`. 현재 `--apply`가 없어도 지정 log-root 아래 `dev/catalog/log_inventory_latest.json/.md`는 기록한다. 이 기존 동작을 무단 무쓰기 정책으로 바꾸지 않는다.
- 신규 `tests/test_p15_run_log_maintenance_temp_cli.py`: `--log-root <tmp_path/logs> --json` (apply 없음) → source `offhours_a.jsonl` 보존, `moved_total=0`, `move_results=[]`, inventory JSON/MD만 temp 안에 생성. `--apply` (동일한 완전 임시 트리) → source가 `dev/analysis/offhours`로 이동, `moved_total=1`, `move_results[0].status="moved"`; 두 번째 실행 `moved_total=0` 확인. destination 선점 충돌 → 원본 보존/`skipped_destination_exists`/`moved_total=0`; monkeypatch `shutil.move`가 첫 후보에서 `OSError`를 던질 때 다음 후보는 이동, `failed`와 `moved` 결과를 각각 기록하고 `moved_total=1`. inventory `warning_total`은 실제 반환 JSON과 일치해야 한다.
- 이 테스트는 `--apply`라도 **tmp_path에서만** 실행. 결과 불일치가 입증되면 B 소유 `run_log_maintenance.py` 또는 core helper를 최소 수정. 실제 `data/logs` 실행·삭제·이동 금지.

## 5 — EventLogger legacy constructor 경계 및 실제 JSONL 호환 (개발·필수)

- **SOURCE:** `libs/core/event_logger_compat.py::get_event_logger/_NodeEventLogger.start/end`; 현재 실제 dataclass `log_path` shape는 `resolve_event_log_path()`로 연결하고 payload 비-dict는 `{}`, 인스턴스별 run_id를 유지한다. `tests/test_p15_event_logger_caller_bridge.py`의 기존 1개 정상·`-O` PASS는 재실행하지 않는다.
- 신규 `tests/test_p15_event_logger_constructor_matrix.py`에서 `libs.core.event_logger.EventLogger`를 monkeypatch한 **세 가지 가짜 클래스**(keyword `node=`만 수용, positional name만 수용, no-arg 후 node 설정)와 실제 dataclass `log_path`를 별개로 검증. 각 shape에서 `get_event_logger("scanner")`가 올바른 node/path로 생성되고 `TypeError` fallback 외 예외를 숨기지 않으며, 실제 dataclass의 `start({"x":1})`/`end({"y":2})`는 temp `EVENT_LOG_PATH`에 순서·stage·payload·동일 run_id로 기록되고 다른 인스턴스 run_id는 달라야 한다. 외부 운영 JSONL 사용 금지.
- 새 테스트에서만 드러난 호환 결함은 B 소유 compat 모듈에서 최소 수정. fake 클래스가 `start/end`를 직접 제공하면 기존 signature를 보존하고 불필요한 래핑을 강요하지 않는다. 현재 `_NodeEventLogger`의 동작을 의미 없이 다시 구현하지 않는다.

## 6 — Claude A 고정 소스 독립 검증 (필수·상대 수정/푸시 금지)

- **SOURCE SHA 고정:** `d30c67abc03a8c6b33909558f624242c76ab979f` (A). 임시 detached/격리 복사본에서만 `libs/reporting/baseline_samsung_hynix/forward_validation/{reaction_reader.py,stock_reaction.py,collector_observations.py,index_timeline.py,shadow_comparison.py}`와 `tests/test_p15_{stock_reaction_extraction,collector_observations_extraction,index_timeline_extraction,forward_validation_parity_chain}.py`를 확인한다.
- 독립 입력: verified collector 가격은 legacy보다 우선, `market_epoch=None`은 `integrity_failure=True` 및 legacy fallback 금지, macro JSON `[]` 뒤 정상 객체는 정상만 로드·파일 불변, CLOSE 없는 `path=[]`은 `average_mfe_pct/average_mae_pct=None`(TypeError 아님), 정상+결측 혼합은 유효 숫자만 평균. 고정 SHA의 A 작성 테스트를 반복하는 것에 그치지 말고 **별도 fake/temp 입력의 새 경계**를 추가해 기존 `test_q10_collector_fix3.py` 등 관련 회귀와 비교한다.
- A 소스·테스트 수정/푸시 0. 명령·기대/실제 dict·normal/-O·정확 SHA·독립 검증 범위와 미검증 원래 범위를 Issue #12에 보고. 새로운 A HEAD가 생겨도 이번 고정 SHA를 임의 변경하지 않는다.

## 공통 검증·종료·원격 보고

모든 1~6은 필수이며 하나라도 `NOT_RUN`이면 전체 완료가 아니다. `yaml`/`exchange_calendars`가 없는 환경에서 관련 모듈 수집이 실패하면 **그 정확 테스트 경로만** `BLOCKED(MODULE_NOT_FOUND)`로 표시하고 동일 실패 명령을 재실행하지 않는다. 사용 가능한 기존 프로젝트 가상환경/lockfile 설치본이 있는지만 확인하며 임의 인터넷 다운로드·운영 의존성 변경 금지. 독립적인 위 1~5의 fake/tmp 테스트와 다른 안전 과제는 즉시 계속한다. 상대 검증은 현재 지정된 A 고정 SHA만 인정하고, 다른 SHA의 부분 peer는 대체하지 않는다. 안전 차단은 해당 과제만 `BLOCKED(정확 함수·명령·오류·해제 담당·재개점)`로 두고 다른 안전 과제를 전부 계속한다. 각 신규/변경 테스트는 `python -m pytest -q -p no:cacheprovider <exact paths>`와 `python -O -m pytest -q -p no:cacheprovider <same paths>`를 실제 실행한다. `python -O`의 pytest assertion rewriting을 무효라고 일반화하지 않는다. 동결 파일은 읽기/실행만, 원본·fixture 변경 0. 실제 새 Owner/코드·테스트 LOC 전후, caller 연결, 실패→수정 후 결과, 정확 커밋 SHA를 남긴다. 허용된 B 브랜치에 소유 코드·테스트만 정상 fast-forward 커밋·푸시하고 원격 HEAD/blob 재조회. 인증 장애면 허용된 GitHub 연결 경로를 이용하되 force push·새 브랜치 금지.

#12에 **실측** `START_KST/END_KST/ELAPSED_MIN`(없으면 `NOT_VERIFIED`), 과제별 `IMPLEMENTED|VERIFIED_ALREADY(SHA)|BLOCKED|NOT_RUN`, normal/-O 실제 명령·exit·PASS/FAIL, 정확 SOURCE SHA, 상대 고정 SHA, 미완료 과제의 다음 안전 함수·재개점과 30분 미만 종료 사유를 기록한다. 시간은 댓글 간격/예약 길이/테스트 초로 추정하지 않는다. 30분은 감사 신호이지 실행시간 목표가 아니다. 이미 완료된 과제만 빠르게 끝나면 남은 모든 안전 과제를 계속하고, 모두 끝났을 때만 완료 보고한다.
