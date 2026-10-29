# C01 — Codex B | 연속 구현 명령서

**실행 역할:** 이전 대화나 프로젝트 맥락은 필요 없다. 이 파일의 1→7번만 순서대로 실제 구현한다. 스스로 작업을 선정하거나 RF/큐/D00/CURRENT를 찾아 읽지 않는다. **명령만 설명하고 종료하지 말 것.** `hbombheart1230-dotcom/agentra`의 **기존** `work/p15-b-operator-structure-20261022` 브랜치에서 허용된 소스·테스트만 수정한다. 지시 기준에서 확인한 원격 B HEAD는 `801ca211b83d04d4dc38e78f394f57ffb5dd29e4`(2026-10-29 09시대); 시작 시 실제 HEAD를 확인하고 이미 같은 수정이 포함됐으면 해당 항목은 신규 작업 없이 검증 결과만 재사용하고 다음 번호로 이동한다. 코드가 달라졌으면 최신 코드에 맞춰 **같은 의도**를 구현하되 권한을 넘는 변경은 하지 않는다.

## 1 — 대형 계약 파일의 Strategist 책임 실제 분리 (개발·필수)

**SOURCE:** `libs/contracts/agent_outputs.py` (지시 기준 약 1,915 LOC). **신규 Owner:** `libs/contracts/agent_output_parts/strategist_projections.py` 및 필요 시 해당 패키지의 `__init__.py`. 기존 같은 이름이 있으면 중복 생성 금지.

- 원본의 정확한 **4개 함수 본문** `_build_strategist_trace_summary`, `_build_strategist_decision_frame`, `_build_strategist_news_evidence_ranked`, `_build_global_sentiment_signal_payload`를 하나의 새 모듈로 **MOVE**한다. 순서·조건·기본값·문자열·딕셔너리 키·정렬·예외를 임의 변경하지 않는다. 정식 artifact builder `build_strategist_output_artifact`와 공개 함수 이름·signature·출력 스키마는 그대로 유지한다.
- 원래 `agent_outputs.py`에는 같은 signature의 얇은 wrapper만 남기고, 새 Owner의 구현을 호출시킨다. 새 Owner가 기존 facade를 import하여 순환 의존하지 않도록 `facade=sys.modules[__name__]`처럼 **호출 시점의 module object를 주입**하고, 원래 글로벌 `_dict/_clip/_listify/_safe_int/_format_trace_number/_dedupe_text`는 Owner 안에서 `facade.NAME`으로 참조해 기존 테스트의 monkeypatch 동작을 유지한다. 모듈 수준의 실행 부작용이나 복제 구현 금지.
- 기준 출력: 빈 state, 정상 strategist output, 이미 존재하는 event payload, 누락 theme/news/VIX, numeric/string 입력에서 분리 **전/후 결과가 동일**해야 한다. 변환 전 baseline을 테스트 fixture로 확보한 뒤, 결과를 key/value 단위로 대조한다. 원래 코드 결과를 테스트 중 다시 import하는 방식의 허위 parity 금지.
- 변경 테스트 예: `tests/test_p15_strategist_projection_extraction.py` 신규. 성공·결측·기존 payload 우선순위·monkeypatch 4종을 확인한다. 새 Owner는 권장 150~300 LOC, **350 LOC 초과하지 않는다**. 실제 원본 LOC 감소량을 보고한다.

## 2 — 같은 파일의 Scanner 책임 실제 분리 (개발·필수)

**SOURCE:** 같은 `libs/contracts/agent_outputs.py`. **신규 Owner:** `libs/contracts/agent_output_parts/scanner_projections.py`.

- 아래 3개 함수 본문만 MOVE: `_build_scanner_trace_summary`, `_build_scanner_candidate_ranking_table`, `_build_scanner_candidate_selection_reason`. 기존 함수명/signature는 facade에 얇게 유지. `build_scanner_output_artifact` 본체 및 검증·직렬화 공개 계약은 수정하지 않는다.
- 1번과 같이 Owner는 facade를 import하지 않고 호출 시점 `facade` 주입으로 원래 `_dict/_listify/_safe_float/_safe_int/_clip/_dedupe_text`를 참조. score rounding, runner-up 2개, fallback tie-break 문구, event payload 우선순위, missing flags, 빈 후보 목록은 **바이트 동등한 JSON 출력을 목표**로 한다.
- `tests/test_p15_scanner_projection_extraction.py`에서 0/1/3 후보, 동점, 양·음수 factor, candidate preview 누락, 명시적 ranking/selection event payload 우선순위, facade monkeypatch를 확인. 신규 Owner **350 LOC 이하**, 실제 facade LOC 감소 보고.
- **동결 테스트/오라클 수정 금지:** `tests/test_p161_agent_output_contract_freeze.py`, `tests/fixtures/p1_5_t35_agent_outputs/**`는 그대로 유지한다. 분리 후 반드시 이 기존 계약 검증을 정상/`python -O`로 실행한다. 출력 parity가 깨지면 해당 extraction만 롤백·정확한 차이 제출 후 다음 3번으로 이동한다.

## 3 — 실제 EventLogger 호출자 무음 누락 해결 확인 (수정 필요 시 개발)

**SOURCE:** `libs/core/event_logger_compat.py`; `get_event_logger`, `_NodeEventLogger.start/end`. 직전 확인된 소스 수정이 이미 존재하므로 **기존 통과 테스트를 그대로 반복하지 않는다**.

- 실제 `get_event_logger` 사용 지점을 코드에서 찾고 (Graph는 **읽기 전용**), 임시 `EVENT_LOG_PATH`와 가짜 payload로 생성된 JSONL의 `stage`, `event` 순서 `start,end`, 동일 `run_id`를 확인한다. 명시적 `log_path`를 받는 현재 EventLogger와 레거시 `node=` / positional / no-arg fake constructor도 기존 동작 유지.
- **A의 실제 독립 음성 검증에서 남은 구멍(정확 B `e33929dd`):** `start(payload=[1])`·`end(payload="bad")`의 JSONL `payload={}` 정규화와 `get_event_logger("node")` 두 인스턴스 간 `run_id` 상이(한 인스턴스 start/end는 동일)를 `tests/test_p15_event_logger_caller_bridge.py`에 반드시 포함한다. 기존 B 테스트에서 이 두 변이가 통과했던 반례를 실패→PASS로 닫고, 원본 로그 내용/순서/파일 위치를 tmp 경로로 검증한다. 테스트에 운영 `data/logs`를 쓰지 않는다.
- 다르면 B가 소유한 compat 어댑터만 최소 수정한다. `tests/test_p15_event_logger_caller_bridge.py` 신규. Graph·실제 로그 파일·기본 계좌 경로·실네트워크는 건드리지 않는다. 실제 버그가 없으면 새 경계 검증만 추가하고 **4번으로 진행**한다.

## 4 — 로그 유지보수의 목적지 충돌·부분 실패 (실제 결함 판단)

**SOURCE:** `libs/core/log_maintenance.py::apply_log_move_candidates`.

- 완전히 격리한 `tmp_path`의 source/destination 2개를 준비. 기존 destination이 있을 때 삭제/덮어쓰기, source 보존, 동일 명령 재실행, 중간 실패(가짜 `shutil.move` 예외)의 행동을 재현하여 테스트에 고정한다. 테스트에서 저장소 운영 루트를 사용하지 않는다.
- 기존의 의도된 덮어쓰기 정책/호출자와 충돌하지 않는 최소 버그 수정만 B 소유 소스에 반영한다. **덮어쓰기 정책 자체를 바꿔야 하거나 영향이 불명확하면 원본을 수정하지 않고** 정확한 before/after 위험과 지팀장 결정 필요를 #12에 남긴 뒤 5번으로 이동한다.
- 테스트 예 `tests/test_p15_log_move_collision_contract.py`. 정상 및 `-O` 양 모드.

## 5 — 지정된 CLI의 진짜 temp-only 효과 계약 (구현/검증)

**SOURCE:** `scripts/maintenance/sync_legacy_brief_llm.py::main`.

- 명시적 **절대경로** `--reports-root <tmp_path>`만 사용한다. `--day 2026-10-01 --json`으로 ① 파일 없음 `trade_count=0` ② canonical `trades/<day>/<trade>/reports/brief_llm_response.json` 존재 ③ `--dry-run` ④ 중복 실행을 검증. 원본 파일 내용과 디렉터리 목록이 변경되지 않아야 한다.
- JSON의 `ok/day/reports_root/dry_run/trade_count/rows[*].status`, exit 0을 확인. 필요한 경로가 구현의 실제 trade-dir 인식 구조와 다르면 **소스를 읽어 정확한 fixture 경로만 조정**하고 임의 기능 추가 금지. 결함을 재현하면 해당 소유 파일만 최소 수정한다.
- 신규 `tests/test_p15_sync_legacy_brief_no_write_cli.py`, 정상 및 `-O`.

## 6 — 상대 코드 독립 검증 (수정·푸시 금지)

- Claude A **고정 SOURCE SHA** `8bdbd5ab32eed6d1b0dddfc799d3bc577ebf9a1e`의 `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py`와 `tests/test_q10_index_close_fallback.py`, `tests/test_q10_reaction_reader_collector_integration.py`를 **격리된 임시 복사본에서만 읽기·실행**한다. A 브랜치 체크아웃을 공유 작업 폴더에 덮어쓰거나 A 소스를 수정·푸시하지 않는다.
- `_stock_reaction`과 `_collector_raw_row`의 ABSENT→legacy fallback, INVALID→PENDING, VERIFIED→해당 collector 값 우선, CLOSE 없음→수익률 계산 미사용을 fake 데이터로 독립 검증. 기존 scoped PASS를 무의미하게 재실행하지 말고 **새로 본 호출자/예외 경계**만 점검한다. 반례 발견 시 재현 input, output, 고정 SHA, 실패 코드와 A에게 필요한 수정 내용을 #12에 보고한다.

## 7 — 종료·보고(모든 개발 항목 공통)

- **순서 1→6의 실질 작업을 가능한 만큼 모두 수행한다.** 첫 PASS·한 건 커밋·타인 SHA 대기·댓글 1개가 종료 조건이 아니다. 차단 항목은 첫 차단 원인과 해제 담당을 기록하고 **다음 번호로 즉시 진행**한다. 실제 플랫폼 실행 한도 때는 마지막 완료 번호·미완료 코드 위치·다음 명령부터의 체크포인트를 남긴다. 30분·건수 목표 없음.
- 새 변경 테스트 및 표적 회귀는 **`python -m pytest -q -p no:cacheprovider <paths>`**, **`python -O -m pytest -q -p no:cacheprovider <same paths>`** 두 모드로 실행한다. 테스트 환경 의존성/불가 상황은 PASS라 쓰지 말고 NOT_RUN/차단 근거 기록.
- 본인 기존 B 브랜치에 **코드+테스트만** 커밋하고 원격 실제 HEAD·변경 blob을 재조회 확인. Git shell push 인증 실패면 이미 허용된 GitHub 연결 쓰기 경로로 동일 브랜치 fast-forward 가능한 경우에만 사용한다. main/integration/타인 브랜치 쓰기·force push·새 브랜치/PR·동결 오라클·문서/CSV/RF/STATUS 변경 금지.
- GitHub Issue **#12 댓글**: `START_KST / END_KST / ELAPSED_MIN` **실측**, 완료 번호와 파일별 `OLD_LOC→NEW_LOC`, 실제 코드 수정·테스트·normal/-O/exit, 정확 원격 SHA, 상대 독립 검증 결과, 번호별 BLOCKED/NOT_RUN 및 다음 미수행 번호. 앞뒤 실행 시간을 합쳐 추정하지 않는다. 끝내지 못했더라도 실제 성과를 제출한다.
