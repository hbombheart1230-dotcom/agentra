# RF-039 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-039.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 16개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/research/existing_evidence_mining/analysis.py` blob `8b79cb4376757d738f02f26ad5aeca84a1c024a3` (381 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/research/existing_evidence_mining/analysis.py::blocked_opportunity_analysis` L179-263 | MOVE_BODY | `libs/research/existing_evidence_mining/analysis_blocked_opportunity_analysis.py::blocked_opportunity_analysis` | 85행 · 순수 후보 |
| `libs/research/existing_evidence_mining/analysis.py::actual_trade_analysis` L314-381 | MOVE_BODY | `libs/research/existing_evidence_mining/analysis_actual_trade_analysis.py::actual_trade_analysis` | 68행 · 순수 후보 |
| `libs/research/existing_evidence_mining/analysis.py::classify` L191-253 | KEEP_CLASS_OR_EXTRACT | `libs/research/existing_evidence_mining/analysis.py::classify` | 63행 · 순수 후보 |
| `libs/research/existing_evidence_mining/analysis.py::summarize_rows` L21-71 | MOVE_BODY | `libs/research/existing_evidence_mining/analysis_summarize_rows.py::summarize_rows` | 51행 · 순수 후보 |
| `libs/research/existing_evidence_mining/analysis.py::discovery_cohorts` L143-178 | MOVE_BODY | `libs/research/existing_evidence_mining/analysis_discovery_cohorts.py::discovery_cohorts` | 36행 · 순수 후보 |
| `libs/research/existing_evidence_mining/analysis.py::score_component_diagnostics` L109-142 | MOVE_BODY | `libs/research/existing_evidence_mining/analysis_score_component_diagnostics.py::score_component_diagnostics` | 34행 · 순수 후보 |

### blocked_opportunity_analysis — 원본 85행
- **확인된 책임:** `libs/research/existing_evidence_mining/analysis.py` L179–263; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/research/existing_evidence_mining/analysis_blocked_opportunity_analysis.py::blocked_opportunity_analysis` (Owner Claude A, RF-039). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### actual_trade_analysis — 원본 68행
- **확인된 책임:** `libs/research/existing_evidence_mining/analysis.py` L314–381; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/research/existing_evidence_mining/analysis_actual_trade_analysis.py::actual_trade_analysis` (Owner Claude A, RF-039). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### classify — 원본 63행
- **확인된 책임:** `libs/research/existing_evidence_mining/analysis.py` L191–253; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/research/existing_evidence_mining/analysis.py::classify` (Owner Claude A, RF-039). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### summarize_rows — 원본 51행
- **확인된 책임:** `libs/research/existing_evidence_mining/analysis.py` L21–71; 직접 호출 helper `_observed_return`. 감지된 효과: 없음.
- **목표:** `libs/research/existing_evidence_mining/analysis_summarize_rows.py::summarize_rows` (Owner Claude A, RF-039). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### discovery_cohorts — 원본 36행
- **확인된 책임:** `libs/research/existing_evidence_mining/analysis.py` L143–178; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/research/existing_evidence_mining/analysis_discovery_cohorts.py::discovery_cohorts` (Owner Claude A, RF-039). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### score_component_diagnostics — 원본 34행
- **확인된 책임:** `libs/research/existing_evidence_mining/analysis.py` L109–142; 직접 호출 helper `_observed_return`. 감지된 효과: 없음.
- **목표:** `libs/research/existing_evidence_mining/analysis_score_component_diagnostics.py::score_component_diagnostics` (Owner Claude A, RF-039). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/research/__init__.py` | `libs/research/__init__.py` | `f6d0353cdd83` / 957B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/evidence_ledger.py` | `libs/research/evidence_ledger.py` | `91f141a2a903` / 4993B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/existing_evidence_mining/__init__.py` | `libs/research/existing_evidence_mining/__init__.py` | `1170f12657af` / 95B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/existing_evidence_mining/analysis.py` | `libs/research/existing_evidence_mining/analysis.py` | `8b79cb437675` / 16305B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/research/existing_evidence_mining/contracts.py` | `libs/research/existing_evidence_mining/contracts.py` | `c9b744d42457` / 862B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/existing_evidence_mining/episodes.py` | `libs/research/existing_evidence_mining/episodes.py` | `f3cad530d99f` / 7072B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/existing_evidence_mining/loaders.py` | `libs/research/existing_evidence_mining/loaders.py` | `f9523a245ebe` / 10592B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/existing_evidence_mining/pipeline.py` | `libs/research/existing_evidence_mining/pipeline.py` | `e4aecda75c31` / 10742B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/existing_evidence_mining/report.py` | `libs/research/existing_evidence_mining/report.py` | `5a9b9aa18220` / 13938B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/horizon_revision_backtest/__init__.py` | `libs/research/horizon_revision_backtest/__init__.py` | `c4ca24ebcca2` / 97B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/horizon_revision_backtest/analysis.py` | `libs/research/horizon_revision_backtest/analysis.py` | `a1a3e266b936` / 10016B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/horizon_revision_backtest/loaders.py` | `libs/research/horizon_revision_backtest/loaders.py` | `87670411cede` / 2869B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/horizon_revision_backtest/pipeline.py` | `libs/research/horizon_revision_backtest/pipeline.py` | `1160c5996a6f` / 1639B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/horizon_revision_backtest/report.py` | `libs/research/horizon_revision_backtest/report.py` | `fddeeca5ec10` / 6512B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/strategy_feedback_builder.py` | `libs/research/strategy_feedback_builder.py` | `7e3b7a75ebea` / 13305B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/strategy_memory_store.py` | `libs/research/strategy_memory_store.py` | `14a18608e157` / 14918B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-039|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
