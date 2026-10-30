# C01 — Codex B | 신규 BODY MOVE 8건 B1~B8 · RF-044 Commander shadow advisory
> 2026-10-30 10:40 KST 지팀장 신규 주문. **이전 C01 6건(B stage4 + adjustment2)은 10:35 C04 통합 완료: 재배정·재시험·성과 중복 0.** 이 파일을 새 단일 실행 주문으로 사용한다.

## 시작·Owner·검증 전제
- 진입점은 **원격 `integration/p1.5`의 이 C01 한 파일**. RF/INDEX/D00/HANDOFF/STATUS/큐 읽기 금지. 자신의 기존 `work/p15-b-operator-structure-20261022` 브랜치의 아래 SOURCE/TARGET/TEST만 수정·commit/push. A reporting/타인 코드·문서·CI·frozen oracle·운영 DB/State/실계좌/실주문/네트워크/Broker/Guard/Supervisor/Executor/Step5C/UEF 변경 금지.
- C03 원격 실측: B `libs/contracts/agent_outputs.py` Git blob **`174fa6f671e8834211cf5675415d3ecc1c8d66ee`**, 총 **1271 LOC**. 이 문서의 새 TARGET 2개 B 원격 모두 **404** 확인. 기존 `commander_shadow_advice.py`(이전 완료)와 `commander_shadow_runtime/evidence.py`는 KEEP. **RF-044 단독 B owner**; A 수정 경로 교집합 0. B HEAD가 전진하면 각 원본 함수가 이미 thin wrapper인지 새 target이 존재하는지 먼저 비교. 이미 원격 MOVE됐으면 `ALREADY_MOVED`로 보고하며 재수정·재테스트·신규 성과 계상 금지.
- 먼저 `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID=C01:<ORDER_FILE_BLOB_SHA>:B1..B8` 고정; dirty tree/원격 blob·python/pytest/승인 push 경로 검사. 진행 중 새 주문 발행은 시작 주문을 소급 무효화하지 않는다.
- **모두 필수 8건.** 한 item PASS·로컬 commit·push 실패·짧은 시간 경과 후 종료 금지. 한 item BLOCKED면 다른 7건 중 독립 안전 과제 계속. 8건이 모두 완료/정당 차단된 후만 종료. 신규 작업 자율 선택 금지; C03이 다음 회차에 보충한다.

## 공통 MOVE 계약
- SOURCE 각 `def`의 **실제 계산·텍스트 본문**을 신규 TARGET의 유일 Owner로 옮기고, SOURCE에는 **기존 이름·정확 인자/기본값을 유지한 thin wrapper**만 남긴다. `_r3_sys.modules[__name__]`를 `facade=`로 전달하고 TARGET은 `agent_outputs`를 import하지 않는다. `_dict/_clip` 등은 `facade._dict/_clip` **호출 시점**에 조회; dict/list alias·키 삽입 순서·문구·형 변환·예외·branch precedence·monkeypatch 완전 보존. 기존 Commander advisory는 **관측 전용**(실제 실행/승인 결론 변경 금지).
- B1~B5는 신규 `libs/contracts/agent_output_parts/commander_shadow_advice_extended.py`에 순차 추가. B6~B8은 신규 `libs/contracts/agent_output_parts/commander_shadow_assessments.py`에 순차 추가. 각 SOURCE 함수만 bounded-hunk patch; 잘린 도구 출력이나 인코딩 오염 금지. SOURCE 이전 golden vs wrapper/OWNER 직접호출, 예외·입력불변, helper patch seam 2~4 fixture/item.
- 각 TEST 신규 8파일 아래. `python -m py_compile` 변경 source/target/test, 정상 `python -m pytest -q -p no:cacheprovider <8개 신규 테스트 경로>` 1회 exit0 또는 pytest 부재 시 재현 가능한 stdlib smoke exit0. `-O`·full suite·full peer·hosted CI 전수는 **필수 아님**. commit/승인 경로 push 후 `git ls-remote` 및 원격 SOURCE/TARGET/TEST blob 재조회. push 실패는 `PUSH_BLOCKED`, 로컬 commit은 G1 아님; 다른 item 계속.

## 신규 B1~B8 · 각각 독립 구현·검증
| ID | SOURCE (모두 `libs/contracts/agent_outputs.py`) | 유일 TARGET (상기 두 신규 모듈) | 정확 이전할 의미 / 필수 회귀 | 신규 TEST |
|---|---|---|---|---|
| **B1** | `_commander_shadow_llm_call_advice` L970–990 | `commander_shadow_advice_extended.py::llm_call_advice` | `strategist_llm` vs observations status, SKIP market_changed/repeated 우선, blocked/error/fallback→RETRY_MINIMAL, partial/salvaged/repaired→RETRY_COMPACT, 기본 ALLOW; None/malformed·precedence 및 bytes | `tests/test_p15_shadow_llm_call_advice_owner.py` |
| **B2** | `_commander_shadow_suggested_action` L991–1007 | `...advice_extended.py::suggested_action` | POSITION_ALREADY_OPEN monitor_only, NO_MARKET_CHANGE/REPEATED skip reuse, RETRY_COMPACT/MINIMAL, default allow; 충돌 우선순위/원문 exact | `tests/test_p15_shadow_suggested_action_owner.py` |
| **B3** | `_commander_shadow_next_action_recommendation` L1008–1029 | `...advice_extended.py::next_action_recommendation` | POSITION_ALREADY_OPEN→HOLD_OBSERVE, retry/set, wait reasons, `facade._clip` monitor decision BUY/SELL/HOLD, NO_ACTION; 우선순위/patch spy | `tests/test_p15_shadow_next_action_owner.py` |
| **B4** | `_commander_shadow_reason_summary` L1030–1054 | `...advice_extended.py::reason_summary` | 11개 reason→정확 영어 문구 dict, `facade._clip`으로 llm/monitor/executor, fallback 원문; 문구 bytes/unknown/None/patch | `tests/test_p15_shadow_reason_summary_owner.py` |
| **B5** | `_commander_shadow_recommendation_gap` L1055–1073 | `...advice_extended.py::recommendation_gap` | strategist executed/LLM called True·False·None; skip vs refresh 우선, 마지막 aligned; None/미지정 경계 | `tests/test_p15_shadow_recommendation_gap_owner.py` |
| **B6** | `_commander_shadow_pre_strategist_snapshot` L1074–1097 | `commander_shadow_assessments.py::pre_strategist_snapshot` | prior_context dict, market_changed/repeated/status, `facade._clip` symbol/playbook/reason 180, dict 8키 순서·원본 alias | `tests/test_p15_shadow_pre_strategist_owner.py` |
| **B7** | `_commander_shadow_post_strategist_assessment` L1098–1119 | `...assessments.py::post_strategist_assessment` | strategist_output/llm status fallback, executed/llm_called/cache, regime/sentiment, context_delta_summary 원객체 alias, 정확 키 순서 | `tests/test_p15_shadow_post_strategist_owner.py` |
| **B8** | `_commander_shadow_post_monitor_assessment` L1120–1134 | `...assessments.py::post_monitor_assessment` | monitor decision, entry reason, passed/failed first 8, axis, original monitor_gate_details alias 및 `facade._clip` patch, 키 순서 | `tests/test_p15_shadow_post_monitor_owner.py` |

### KEEP/안전·보고
- `build_commander_shadow_artifact` 상위 orchestration, `_commander_shadow_has_open_order`·gate 결정/실주문, 기존 Owner `commander_shadow_advice/runtime/evidence` 본문 **KEEP**. 이 8개는 Advisor snapshot/text 계산만 분리하며 실행·승인·Guard 경로 변경 0.
- **#12에 결과 1회:** `ORDER_ID | B1..B8 item 상태 | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOBS | TEST_PATHS | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA/ERROR | FIRST_BLOCKER | NEXT`. 실측 START/END/ELAPSED, 원격 검증 실패시 `NOT_DELIVERED` 명시. C04 최소 통합, C05 G1/G2/G3 및 DONE 권한 유지.
