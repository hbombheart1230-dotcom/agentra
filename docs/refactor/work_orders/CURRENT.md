# Agentra P1.5 — CURRENT

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**운영:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · **RF:** [물리 큐](../plan/queue/) · **집계:** [STATUS](../plan/STATUS.md)

**이 브랜치의 CURRENT만 지시 정본이다.** A/B는 자신의 브랜치 CURRENT·구 HANDOFF의 지시를 사용하지 않는다. D00 및 아래 배정 RF만 필요 시 읽어라. 같은 SHA·같은 경계 반복 검증·ACK 문서로 종료하지 마라.


## 상시 실행·작성 규칙 — 지팀장/A/B 공통

**지팀장은 앞으로도 CURRENT를 매번 구체적인 명령문으로 작성하라.** 각 작업에 반드시 담당자, 우선순위, 지금 실행할 RF, 정확한 대상 파일/함수, 검증할 신규 경계, 정상/-O 명령과 exit, 제출 산출물, 막혔을 때 다음 RF를 명시하라. '검토 필요'·'진행 예정'·'결정 대기'만 써 놓고 작업 지시라고 하지 마라. **'확인하라 → 분류하라 → 수정하거나 KEEP하라 → 검증하라 → SHA·exit를 제출하라 → 다음 RF를 실행하라'**로 써라.

**A/B는 지시를 받으면 실제 실행하라.** 매번 integration/p1.5의 최신 CURRENT·HEAD를 읽고 자기 배정 RF만 수행하라. 기존 유효 SHA·동일 테스트는 재실행하지 마라. 앞 작업이 BASELINE/ENV/SAFETY/동결 오라클 때문에 막히면 그 원인과 해제 조건을 적고 즉시 다음 안전한 RF를 수행하라. 소스 수정이 가능하면 실제 commit+normal/-O 증거를, KEEP이면 파일별 소비자·IO/State·예외 근거를, peer면 처음 보는 경계의 독립 증거를 제출하라. ACK·HANDOFF 문서만 수정하고 종료하지 마라.

**지팀장은 이미 나온 증거의 RF 판정·큐 이동·소스 통합을 개발자에게 되돌리지 마라.** 직접 ACCEPT/HOLD/KEEP/FIX/PEER/REWORK/INTEGRATE를 결정하고 물리 큐를 갱신하라. 다음 배정을 확정한 뒤 CURRENT를 마지막에 고쳐라. 이 상시 지시형 운영 규칙을 이후 CURRENT 개정에서도 반드시 유지하라.

## Claude A — `work/p15-a-reporter-pure-20261021`

1. **즉시 실행: RF-031 원개발** [02_DEVELOPING/CLAUDE_A](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-031.md). `libs/reporting/(trade_report_|reporter_|trade_story_)*.py` 22개 독점 owner의 실제 BASE/통합/작업 tree blob 및 책임·소비자·patchability·LLM/IO/State·예외·부작용 차분을 조사하라. RF-074 동결 `test_target_tree_discipline_and_no_forbidden_surface`를 변경 없이 보존하고 owner 변경 가능 경계부터 판별하라. 합법적 최소 코드 FIX가 가능하면 실제 source SHA+표적 normal/-O exit+오라클 PASS를 제출하라. 불가하면 파일별 KEEP와 위험 근거를 제출하고 다음 실행 가능한 RF로 이어가라.
2. **RF-030은 개발 중단 / 지팀장 승인 대기** [01_PENDING/CLAUDE_A](../plan/queue/01_PENDING/CLAUDE_A/RF-030.md). A `03b255e5` 순수 렌더 추출은 인정하지만 원본 RF-074 동결 오라클 변경 전 PASS→후 FAIL. run 102의 16/16 forbidden owner 판정으로 현재 허용 가능한 source 대안 없음. 사용자 승인 없이 frozen test/CI·allowlist 변경하거나 day-loader 패치를 적용하지 마라. 본 후보를 integration에 제안·재검증하지 마라.
3. **RF-063/065 독립 peer의 '새 경계'만 계속** [RF-063](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-063.md) · [RF-065](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-065.md). run 102 AST + 130/130 import-only × BASE/integration × normal/-O byte-identical exit 0은 지팀장이 수용했다. 재실행하지 마라. 운영 CLI/실데이터/쓰기/주문/프로세스가 수반되는 `__main__`은 SAFETY_HOLD. 새 안전 격리 consumer/CLI 경계에 한해 read-only peer하고 SHA·명령·exit·차단 범위를 제출하라.
4. **RF-008** [LEAD](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-008.md) A 기존 1270 PASS/1 BASELINE FAIL·State 5종 peer는 수용 완료. 재실행 금지. standalone `run_strategist`/외부 read-only 시세 fail-soft는 지팀장이 별도 경계를 명시하기 전까지 이관 대기. **RF-007** fastapi ENV 차단, **RF-067** 14 import peer PASS/실제 CLI HOLD 유지. RF-028/029 자체 85/38 KEEP 증거 반복 금지.


### A: 이번 회차 실행 순서 — 아래를 실제 수행하라

1. **RF-031의 22개 원소유 파일부터 확정하라.** BASE 63182ab2, 최신 integration, A 브랜치의 blob을 파일별로 비교하고 호출자, import, use-time monkeypatch, LLM, State, 파일 IO, 예외 전파를 분류하라. 결과를 각 파일의 KEEP / FIX 후보 / SAFETY_HOLD로 구분하라. 단순 소스 동일성만으로 DONE이라고 보고하지 마라.
2. **수정 가능성을 동결 오라클로 먼저 가려라.** 원본 tests/test_work_reporter_seed_migration.py의 closed-path 검사와 충돌하는 owner는 편집하지 마라. RF-030의 금지 렌더 후보를 RF-031 명목으로 우회하지 마라. 충돌한다면 정확한 파일·오라클 조건·변경 전후 증거를 제출하고 그 파일은 KEEP 또는 HOLD로 분리하라.
3. **허용되는 최소 원소유 코드 FIX가 있을 때만 구현하라.** BASE와 후보에 동일 fake 입력·환경을 사용해 정상 Python 및 python -O 테스트 명령, 실제 exit, PASS/FAIL 노드, 공개 호출·State/IO·예외·출력 차분을 제출하라. 변경 코드가 생기면 UI patchnotes JSON/MD를 동기화하라. 허용되는 FIX가 없다면 수정하지 말고 다음 작업을 진행하라.
4. **RF-031이 막히면 RF-063/065의 새로운 안전한 독립 경계를 수행하라.** 130/130 import-only를 반복하지 마라. 외부 소비자 중 네트워크/프로세스/SQLite/주문/파일 쓰기를 차단할 수 있는 최초 offline/mock 경계를 하나 이상 선정해 normal/-O로 검증하라. 실제 CLI main 실행은 안전 입증 전 보류하라.
5. **HANDOFF_A와 Issue #11에 사실만 제출하라.** RF 번호 | source SHA | 파일별 KEEP/FIX/HOLD | 최초 테스트 명령 | normal/-O exit | BASE 차이 | peer 필요 여부 | 다음 안전 RF를 적어라. 큐와 CURRENT를 작업 브랜치에서 변경하지 마라.

**출력:** 자신의 작업 브랜치에서 실제 source SHA·새 테스트 명령/normal/-O exit·미검증 경계·안전 HOLD만 HANDOFF_A 및 Issue #11로 제출. 작업 브랜치 CURRENT를 덮어쓰거나 지팀장 큐를 이동하지 마라.

## Codex B — `work/p15-b-operator-structure-20261022`

1. **최우선 RF-001 사후 통합 정확-SHA 검증** [LEAD](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-001.md). `integration/p1.5` HEAD SHA를 즉시 확인하고 별도 read-only 격리 checkout에서 `tests/test_p153_operator_ui_moved_bodies.py`, `tests/test_operator_ui_data_access_phase2.py`, `tests/test_operator_ui.py`를 각각 normal/`python -O`로 실행, 정확한 SHA·명령·exit·노드 결과를 제출하라. 기존 격리 후보 734×2 / UI 53×2 / A 최초 peer는 **재실행하지 마라**. HEAD 이동 시 최신 SHA에서 최초 1회만 증명하라. 코드·동결 테스트 수정 금지.
2. **RF-028/029 최초 B peer** [RF-028](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-028.md) · [RF-029](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-029.md). A 85/38 owner blob BASE 동일·자체 KEEP 증거 수용. RF-028의 동적 소비자·IO/State·예외 새 위험 경계, RF-029의 `trade_story_pipeline.py` / `read_artifact_selection.py` 입력 우선순위·예외·효과 경계를 offline/read-only normal/-O 최초 확인하고 SHA·명령·exit를 제출하라. RF-030 A 후보는 frozen 오라클 HOLD이므로 독립 peer 실행하지 마라.
3. **RF-066** [개발](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md): 기존 `build_demo_catalog` normal marker 및 optimized exit-only 반복 금지. 임시 경로·가짜 `OrderClient`를 강제한 소비자/요청형태·실패 입력 normal/-O의 **독립적인 성공 marker**를 만들고 exit 0을 증명하라. 실제 `main()`/broker/order·운영 경로 쓰기 금지; 격리 실패면 해당 경계만 NOT_RUN 후 다른 RF 진행.
4. **RF-070** [개발](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md): 85/142 wrapper 기존 scoped PASS 재사용, 잔여 25개의 실행 소비자·IO·State/효과 AST 분류를 끝내라. 32 위험 launcher 실행 금지. **RF-018** [peer](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-018.md) 기존 BASE 동일 prose fallback 분류 반복하지 말고 미검증 경계가 있을 때만 신규 peer; **RF-069** [LEAD](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-069.md) UEF5 승인된 snapshot 없는 ENV BLOCK 유지.


### B: 이번 회차 실행 순서 — 아래를 실제 수행하라

1. **RF-001 통합 정확-SHA 검증을 지금 실행하라.** 최신 원격 integration/p1.5 HEAD와 반영된 data_access_core.py 및 data_access_brief_monitor_notes.py blob을 기록하라. 해당 HEAD를 read-only 격리 checkout한 뒤 세 지정 테스트 파일을 각각 정상 Python과 python -O로 실행하라. 각각의 명령·exit·PASS/FAIL node·실행 SHA를 제출하라. 기존 후보 734×2/53×2는 재실행하지 마라. fastapi 부재는 ENV_BLOCK으로만 기록하고 RF-001 코드 REWORK로 만들지 마라.
2. **RF-029 신규 B peer를 수행하라.** trade_story_pipeline.py, trade_read_model_parts/read_artifact_selection.py에서 누락/빈 값/복수 후보/잘못된 입력의 우선순위, 예외/fail-soft, 읽기 전용 IO·State 불변을 fake artifact/tmp 경계로 normal/-O 독립 검증하라. A의 38 owner KEEP 및 49 테스트를 반복하지 마라.
3. **RF-028 신규 B peer를 수행하라.** A의 85 owner BASE 동일과 fake LLM 11개는 재사용하고, 아직 독립 검증하지 않은 trade_report 동적 소비자 1~2개를 선정해 use-time lookup, monkeypatch, State/IO, 예외 계약을 독립적으로 확인하라. 부분 PASS를 전체 DONE으로 표현하지 마라.
4. **RF-066에서 fake OrderClient 경계를 새로 검증하라.** 기존 build_demo_catalog 마커를 재실행하지 말고 별도 임시 디렉터리, fake OrderClient, 차단된 네트워크/브로커/운영 파일을 사용하라. 요청 입력과 오류 입력에 대해 정상/-O 양쪽에서 실제 assertion 기반 성공 마커와 exit를 제출하라. 격리 불가 시 NOT_RUN/HOLD 기록 후 RF-070으로 넘어가라.
5. **RF-070 남은 25개 launcher 분류를 끝내라.** 파일별 CLI 소비자·인수 전달·subprocess·IO·State·부작용을 KEEP/WRAPPER/SAFETY_HOLD로 정리하라. 기존 85개 wrapper 반복 검증 금지, 위험 32개 launcher의 효과 있는 실행 금지. RF-018 기존 BASE fallback 및 RF-069 UEF5 ENV 차단은 재실행하지 마라.
6. **HANDOFF_B와 Issue #12에 실제 신규 증거를 제출하라.** RF | exact tested SHA | 명령 | normal/-O exit | 최초 독립 경계 | 외부 효과 차단 | BLOCKED 해제 조건 | 다음 RF를 적어라. 지팀장 대신 큐를 이동하거나 전체 브랜치를 병합하지 마라.

**출력:** 신규 코드 SHA·실제 명령·normal/-O exit·독립 peer·HOLD를 HANDOFF_B 및 Issue #12로 제출. 전체 브랜치 병합이나 RF 판정·큐 이동 금지.

## 지팀장 — `integration/p1.5`

1. A run 102의 RF-030 16/16 frozen closed path 위반·RF-063/065 130 import-only peer와 B RF-066 부분 검증을 인수했다. **RF-030→PENDING/CLAUDE_A HOLD, RF-031→DEVELOPING/CLAUDE_A 배정**. RF-063/065는 PEER_SCOPED_ACCEPTED지만 실제 CLI 미완료이므로 PEER 유지. RF-001/008/069은 LEAD 유지, RF-028/029/018은 새 peer 결과 전 PEER 유지. 이번 회차 코드 선별 통합 0, DONE 0.
2. Issue [#32](https://github.com/hbombheart1230-dotcom/agentra/issues/32): 예약 미구성·실행 이미지 SHA 미입증은 RUNLAB 환경, 모의 BUY ACCEPTED의 FILL/CANCEL/TTL 관측은 UNKNOWN. RUNLAB 17/19시 신규 증거를 기다려 재현된 코드 결함만 기존 소유 RF에 연결하라. 런타임/예약/실거래 무승인 수정 금지.
3. 매 회차 [troubleshooting/open](../plan/troubleshooting/open/) 및 [closed](../plan/troubleshooting/closed/) 확인. 현재 open 4/closed 0; 해결 조건 충족한 건만 원자 이동하고 STATUS 갱신. 소스 통합 허용은 owner exact blob·상대 신규 peer·동결 오라클 normal/-O·patchnotes 증명이 모두 있는 최소 범위만.
4. **다음 실행 순서:** A/B 신규 소스·peer·Issue #32 수신 → 지팀장 직접 RF FIX/KEEP/PEER/INTEGRATE/BLOCKED 및 큐 판정 → 허용 소스만 선별 통합·정확 SHA 검증 → 다음 소유 RF 배정 → **마지막 CURRENT/STATUS 동기화**. main/거래 안전/동결 test·CI/예약 무승인 변경 금지.


### 지팀장 상시 자기 지시 — 앞으로 매 회차 이 순서로 실행하라

1. **먼저 integration/p1.5의 CURRENT를 읽어라.** 다른 브랜치 CURRENT는 사용하지 말고, CURRENT에서 연결한 D00·배정 RF만 필요한 만큼 읽어라.
2. **A/B 실제 신규 진척을 찾아라.** 원격 HEAD, source diff, HANDOFF_A/B, Issue #11/#12, 런검증 Issue #32의 마지막 인수 이후 증거를 확인하라. 기존 판정·동일 SHA·동일 입력 검증을 반복하지 마라. 문서-only 변경을 코드 진척이라고 보고하지 마라.
3. **직접 RF를 판정하라.** 각 신규 증거를 CODE / BASELINE / ENV / SAFETY·OWNER / UNKNOWN으로 분리하고 RF에 KEEP/FIX/PEER/INTEGRATE/HOLD/REWORK 및 정확한 해제 조건을 기록하라. 환경·런타임 SHA 미입증·모의 BUY 체결 UNKNOWN을 코드 REWORK로 넘기지 마라. 판정을 개발자에게 되돌려 보내지 마라.
4. **허용된 코드만 직접 선별 통합하라.** 원소유 정확한 blob, 독립 peer, 동결 테스트/CI, 표적 normal/-O, UI patchnotes 조건을 점검하라. 통과한 코드만 최소 파일/블록 단위로 integration에 반영하고 통합된 exact SHA의 필수 검증을 수용하라. 실패/미수행 범위는 HOLD하고 DONE으로 옮기지 마라.
5. **물리 RF 큐와 트러블슈팅을 정리하라.** 93개 RF의 단일 경로 및 각 큐 수량을 확인하라. 이동 시 원본 삭제와 대상 생성을 한 커밋에서 처리하라. troubleshooting/open과 closed를 모두 확인하고 실제 종료 조건이 증명된 장애만 closed로 이동하라. STATUS는 실제 변화가 있을 때만 갱신하라.
6. **A/B에 다음 실행을 직접 배정하라.** 정확한 RF 번호, 소유 파일, 첫 실행할 신규 경계와 테스트, SHA/exit 산출물, 금지 영역, 실패 시 차선 RF를 모두 명령형으로 써라. '검토 필요'·'다음 보고 대기'만으로 배정을 끝내지 마라. 안전한 실행 가능 RF가 남아 있으면 새 작업을 이어가게 하라.
7. **최종 단계에서 CURRENT를 갱신하라.** 신규 코드/peer 진척 → 지팀장 실제 RF·큐·통합 조치 → 테스트/정확 SHA 결과 → 다음 A/B 명령 순으로 적어라. 위의 지시형 작성 규칙을 다음 개정에도 보존하라. main, 실거래, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, 동결 테스트/CI, 예약은 사용자 사전 승인 없이 변경하지 마라.

**물리 큐 기준(2026-10-26 지팀장 A 슬롯):** PENDING **66** (UNASSIGNED **65**, CLAUDE_A **1: RF-030 HOLD**) / DEVELOPING **3** (A RF-031; B RF-066/070) / PEER **10** / LEAD **3** / REWORK **0** / DONE **11** = **93 RF**. RF-071은 미배정. 전체 DONE은 완전 인수·필수 정확-SHA 증명까지 유보한다.
