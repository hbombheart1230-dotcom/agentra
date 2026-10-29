# C02 — Claude A | FAST-3 순수 Owner KEEP·관련 테스트 (다음 실행)

**허용 브랜치:** `work/p15-a-reporter-pure-20261021`의 code/test만. 실계좌·실주문·운영 State/로그/네트워크·Broker/Executor/Step5C/UEF·frozen oracle·문서/RF/CSV/STATUS·타인 브랜치·force push 금지. A 최신 원격 SOURCE `bed173058613ad97f830001771d0bd7b3c191f30`.

## 0 — 원격 버전·환경 preflight

- 시작 시 원격 integration의 **이 C02 파일 한 개**를 읽고 `CANONICAL_HEAD`, `ORDER_FILE_BLOB_SHA`, A `OWNER_REMOTE_SHA`를 고정, `ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:<ITEM_NO>`를 만든다. 진행 중 새 문서가 발행돼도 시작한 작업을 소급 실패 처리하지 않는다. dirty/동시 수정·허용 파일·`python -m pytest --version`·승인 push 경로 확인. 원격 A가 `bed17305`보다 진전됐으면 변경 함수/테스트 blob 비교 후 중복 수정·중복 PASS 금지.
- 이전 C02의 OpenAI decision/signal alias(15 PASS), Korea index finite(10 PASS), playbook finite(13 PASS), ProposalStore append(5 PASS)와 기존 import guard 수정은 A #11 `6495308964`의 원격 `bed17305`에서 **완료·푸시·관련 normal/-O exit0**. **다시 실행·재구현하지 않는다.** A의 B `617c8429` EventLogger copy/deepcopy 음성은 2 FAIL+2 PASS로 확인된 B 결함; A가 B 코드를 수정하거나 그 동일 FAIL을 반복하지 않는다. 다음 두 번호는 원래 KEEP 후보의 **새 범위**다.
- FAST-3은 변경 부분 정상 pytest 또는 재현 가능한 stdlib smoke exit0 **한 번**으로 G2 충족 가능. 매-RF -O·전체 peer·전체 suite/hosted CI를 강제하지 않는다. 실제 기능 FAIL만 최소 수정하고 기존 공개 facade/호출자 호환을 보존. 실패·차단은 번호별 분리, 다른 안전 번호 계속.

## 1 — Scanner macro focus의 주입형 facade/use-time KEEP (A 소유)

- **정확 원본:** `libs/agents/scanner/context/macro_focus.py::_scanner_macro_focus_r3_impl` A 및 integration 동일 blob `24170e434adbf11ff35c6c0c86a72f2bb6f88c29`. 현재 함수는 `facade._clamp`를 **호출 시점**에 조회하고 playbook/priority/risk_tone/aggressiveness에서 6개 가중치를 계산한다. 이 함수는 기존 KEEP가 적절하면 **코드 변경 0**; facade를 직접 import하거나 동결된 정적 lookup으로 이동하지 않는다.
- **신규 A 소유 `tests/test_p15_fast3_scanner_macro_focus.py`**: fake `SimpleNamespace(_clamp=lambda x,lo,hi: min(hi,max(lo,x)))` 주입. `playbook="breakout", scanner_priority=["trend","volume","low_risk"], risk_tone="conservative", trade_aggressiveness="low"` → `trend_alignment=1.15,relative_strength=1.10,adx_trend=1.0,volume_accumulation=1.25,breakout_base=1.25,risk_balance=1.45` (float 근사 비교), 6키 유지·입력 리스트 불변. 이어 같은 module import를 재사용한 상태에서 `facade._clamp`를 새 spy로 교체해 6번 호출·최종값 0.5~1.5 clamp 확인. `scanner_priority=None`, unknown playbook → 기본 6키 1.0. 실제 네트워크/파일/State 효과 0. 이 **새 입력만** 시험하고 이전 Scanner cold import 20/20 재실행 금지.
- **실행:** `python -m pytest -q -p no:cacheprovider tests/test_p15_fast3_scanner_macro_focus.py` (exit0), 선택적으로 `python -O -m pytest -q -p no:cacheprovider tests/test_p15_fast3_scanner_macro_focus.py`. 코드가 이미 맞으면 테스트만 A 브랜치 정상 푸시·원격 blob 확인, `KEEP_VERIFIED` 근거로 #11 보고. 실패 시 해당 A 소유 함수만 최소 수정 후 새 정상 테스트, 공개 facade 이름·함수 인자/리턴·주입 시점 호환 유지.

## 2 — Monitor state-transition event payload의 순수 투영 KEEP (A 소유)

- **정확 원본:** `libs/agents/monitor/events/cycle_event_payloads.py::build_state_transition_event_payload` A 및 integration 동일 blob `633f9afbb422c6970cb1597aecb5e24b358d5481`. 함수는 전달받은 9개 인자에서 `previous/current_posture`, reason, `state_changed` 및 `trigger_delta` 8개 필드를 만든다. 모니터 facade·운영 event writer·Guard/주문 코드 수정 금지.
- **신규 A 소유 `tests/test_p15_fast3_monitor_transition_payload.py`**: `previous_monitor_state={"active_exit_axis":"risk"}`, `exit_info={"active_exit_axis":"time","triggered":True}`, `entry_info={"triggered":False,"pattern":"pullback"}`, `entry_transition_trace={"became_ready_this_cycle":True,"last_blocking_axis":"risk","transition_readiness_score":0.75}`, 이전/현재 posture `WAIT/EXIT`, reason `hold/risk_exit`, `state_changed=True` → 키·값 정확 확인(`previous_active_exit_axis="risk"`, `current_active_exit_axis="time"`, exit=True, entry=False, pattern="pullback", ready=True, last_axis="risk", score=0.75). 입력 deepcopy 전후 동일. 두 번째 입력은 dict 필드 비어 있고 `state_changed=0` → bool False·빈 문자열 기본·triggered False·score None, 외부 쓰기 0. 이 **새 함수 계약**만 검사; 기존 19-owner cold import/전체 monitor suite 반복 금지.
- **실행:** `python -m pytest -q -p no:cacheprovider tests/test_p15_fast3_monitor_transition_payload.py` (exit0), `python -O`는 선택. 이미 정상 동작하면 생산 코드 KEEP·신규 테스트만 푸시; 실패 시 A 소유 함수의 최소 수정·공개 caller 호환 확인. 원격 A HEAD/blob 확인 후 #11에 `G1 KEEP 후보/G2 normal exit0`와 C04/C05 인계 요청.

## 3 — 증거·후속

각 번호 `ITEM_STATUS`는 PENDING/RUNNING/LOCAL_IMPLEMENTED/PUSHED/TEST_VERIFIED/VERIFIED_ALREADY/BLOCKED/NOT_RUN 중 사실대로 기록. #11에 `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID/ITEM_STATUS | CHANGED_PATHS | NORMAL_EXIT/-O_EXIT or NOT_RUN | PUSH_REMOTE_SHA or exact BLOCKED | LAST_COMMAND/FUNCTION | ERROR | UNBLOCK_OWNER | NEXT | START_KST/END_KST/ELAPSED_MIN`(원시 기록 없으면 NOT_VERIFIED). 두 항목은 독립이므로 하나 차단 시 다른 안전 항목 진행. 테스트 성공은 C05의 G1/G2 판단 자료이고, C04만 최소 통합/KEEP+targeted smoke, C05만 DONE/STATUS. 기존 RF-016의 재시험·전수 peer·새 hosted CI 의무 부활 금지.
