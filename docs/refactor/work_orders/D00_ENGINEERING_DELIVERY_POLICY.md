# D00 — Agentra P1.5 단일 실행·권한 계약

**A/B 단일 작업서 원칙(2026-10-29 최우선):** RF 상세설계 93개는 **지팀장 C03 설계 자료**이며 **A/B 실행 진입점이 아니다**. 각 개발자에게 SOURCE 원함수, TARGET 새 파일/함수, MOVE 방법, 테스트, KEEP 근거, 재개점을 **C01 또는 C02 한 파일 본문에 직접 기재**한다. A/B는 해당 파일 한 개만 먼저 읽고 실행 코드/테스트 파일 이외의 INDEX·RF 상세·D00·Txx·HANDOFF 탐색 불필요. C03이 매시 C01/C02 본문 큐를 보충, 클라우드 작업자는 지시서만 실행. 정당 KEEP 즉시 통과, 원본/타깃 교차 Actor 0, 실효과 보호는 그대로.


## 2026-10-29 RF 93개 실구현 계약 — 본 절 최우선

- 동결 목표: T00~T09 및 TREE_V3_FROZEN 그대로. [93개 설계](../plan/rf_details/INDEX.md)의 SOURCE→FUNCTION→TARGET 및 RFC 원본 파일 독점권을 사용. 세부 파일이 미조회 함수라고 표기하면 **C03이 실제 소스를 열고 함수명을 확정한 후** A/B에 배정; 임의 추측 구현 금지.
- **KEEP_OK 즉시 통과:** 정해진 폴더 위치, 단일 책임, 적절한 길이와 기존 호환 또는 합리적인 공개 CLI/State/effect 경계가 만족되면 KEEP_OK|path|한줄사유|blob으로 승인. 같은 blob 재시험/peer/장문 검토 금지. KEEP은 구조 목표 충족으로 수용하며 신규 CODE_MOVE 성과에 포함하지 않는다.
- **MOVE 진척:** 원본 함수의 실제 몸체 제거 → 목표 단일 Owner 함수에 옮김 → 원시그니처 얇은 wrapper → caller/monkeypatch/출력/예외 보존. 이중 구현·파일명만 이동은 실패. 실제 변경한 함수의 기존 출력과 새 출력/예외를 fake fixture로 비교하여 정상 targeted pytest/unittest 1회(exit0). 반복 -O/full-suite/full-peer/hosted CI 금지.
- **다중 RF:** C03은 A/B 각각 4~6개 이상 서로 독립적인 실제 함수 과제를 C01/C02에 공급, 한 Item PASS/KEEP/차단 뒤 다른 안전 항목 계속. A/B 원본/신규 target 파일 소유권 충돌 0; 각 자신의 branch code/test만. C04 묶음 통합, C05 READY 묶음 종결, C06 MOVE와 KEEP 분리 감사.
- 기존 26개 DONE 및 모든 이전 검증 이력은 보존. DONE에도 남은 목표 부채가 확인되면 TARGET_GAP_OPEN(정확 SOURCE::함수/TARGET::함수)로 다음 구현에 배정하되 DONE을 일괄 취소하거나 과거 PASS 반복하지 않는다. 실거래/운영 DB/State·Broker/Guard/Step5C/UEF/frozen oracle 변경 금지. 긴급 트랙은 **클라우드 인증/pytest/push 등 실제 환경 차단 해결에만** 사용하고 별도 구조개발 트랙으로 운영하지 않는다.


**정본:** `integration/p1.5`. 이 문서는 **지팀장 C03~C05의 작업 설계·안전·수용 정본**이다. A/B는 개별 회차 실행 명령인 C01/C02만 진입점으로 읽으며, 이 문서나 RF/큐를 매회 재독하지 않는다. 지팀장이 필요한 보호 조건을 작업별 명령서에 명시한다. 작업 지시: [C01](C01_CODEX_CURRENT.md) Codex B · [C02](C02_CLAUDE_CURRENT.md) Claude A · [C03](C03_LEAD_TRIAGE_CURRENT.md) 지팀장 배정 · [C04](C04_LEAD_INTEGRATION_CURRENT.md) 통합/CI · [C05](C05_LEAD_CLOSEOUT_CURRENT.md) 최종 STATUS. 구 핸드오프와 회차별 문서는 역사 자료이며 새 보고 경로가 아니다.

## 1. 진입점·원격 보고의 단일 정본
| 담당 | 소스 작업 브랜치 | **새 결과의 유일한 보고 위치** |
|---|---|---|
| Claude A | `work/p15-a-reporter-pure-20261021` | [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11) 댓글 |
| Codex B | `work/p15-b-operator-structure-20261022` | [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12) 댓글 |
| RunLab | 별도 관측 환경(개발 브랜치 금지) | [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 댓글 |
| **로컬 긴급 트랙**(Codex 개발·Claude 독립 검증) | `emergency/p15-fixes` (단일 브랜치, 아래 §1.2 한정) | 원격 브랜치 커밋/코드·테스트 증거 → 지팀장 [Issue #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36) 판정 댓글 |
| 지팀장 C03/C04/C05 | `integration/p1.5` | [Issue #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36) 판정·변경 **출력 전용** |

- **예약 A/B·RunLab**의 외부 delta 입력은 **#11·#12·#32 최근 신규 댓글 3곳만**이다. 읽은 댓글 ID/시각 이후의 새 사실만 처리한다. **별도 사용자 승인 긴급 트랙**은 §1.2의 `emergency/p15-fixes` 원격 HEAD/신규 커밋만 조건부 추가 확인한다(아직 없으면 `NOT_CREATED`이며 추가 이슈 탐색 금지). #36은 지팀장 판정 출력처이지 네 번째 필수 댓글 입력이 아니다. 최초 정합성 확인이나 사건 참조가 필요할 때만 원본 RF·코드·CI·STATUS를 선택적으로 열며 매회 전수 재독 금지.
- A/B는 **자신의 기존 브랜치에서 소스 코드·코드 테스트만 수정/커밋/푸시**한다. 문서·Markdown·CSV·RF 원본·큐·STATUS·CURRENT·HANDOFF·patchnotes·manifest·policy·GitHub Issue 본문 수정은 **지팀장 독점**이다. A/B는 자기 이슈 **댓글만 작성**하고, 문서·patchnotes가 필요하면 해당 코드 SHA를 근거로 지팀장에 요청한다. 과거 HANDOFF는 읽기 전용 이력이며 절대 갱신하지 않는다.
- 지팀장 C03은 코드 검토·실행할 파일/함수/수정·이동 방법/상대 SHA 검증을 구체적으로 결정·C01/C02 작성하며 RunLab 접수와 작업 진입점 수정을 맡고, C04는 승인된 최소 소스 선별 통합·정확 SHA CI, C05는 RF FAST-3 G1~G3 판정·RF 원본/큐/STATUS·LEAD_CURRENT 단일 작성자다. **문서 수정 권한은 지팀장에게만** 있고 C03~C05 사이에서도 같은 대상의 동시 쓰기를 금지한다. 지팀장이 코드 통합을 수행할 때만 `integration/p1.5` 소스를 수정한다.
**C01~C05 지시서 갱신 책임(필수):** C03은 #11·#12·#32 신규 결과와 실제 원본 코드·소유권·보호 경계를 직접 분석하고 **C01(B), C02(A)**를 다음 회차에 수행할 정확한 파일·함수·구체 수정/이동/검증/상대 SHA·커밋·푸시 명령으로 작성·교체·푸시한다. C03 자신 문서는 자신의 작업 설계 규칙이 실질적으로 변할 때만 갱신한다. C01/C02에는 RF 번호, 큐 탐색, D00 재독, 장황한 과거 기록, 자율 작업 선정을 넣지 않는다. C04는 LEAD 후보·통합/CI 근거가 바뀌면 **C04 본인 문서**를, C05는 RF 단계·체크·DONE/STATUS가 바뀌면 **C05 본인 문서**를 같은 실행에서 수정·푸시한다. **다른 담당의 C파일을 수정하지 않는다. A/B의 어떤 문서 쓰기도 금지.** 세 담당은 변경 후 원격 파일을 재조회하고 다음 예약이 바로 실행 가능한 최신 지시인지 확인한다. 변화가 없으면 C파일 수정·문서 커밋 0. 과거 기록을 누적하지 않고 기존 행을 교체하며 내용은 실행 순서·차단 조건·다음 안전 RF만 유지한다.

- A/B의 **C01/C02에 명시된** 구현·테스트·반대 peer·자기 브랜치 커밋/푸시는 사전 승인된 작업이다. 지정된 **모든 항목을 각각 필수 과제로 수행**한다. 번호는 순서/선택권을 뜻하지 않으며, 첫 PASS·커밋·부분 장애로 종료하지 않는다. 한 과제가 막히면 **다른 안전한 지정 과제 전부를 계속** 수행한다. 새 작업은 A/B가 고르지 않고 C03이 다음 회차 명령서에 쓴다. 작업별 명령서가 위험·권한 조건을 명시하지 못한 경우 불명확한 효과를 실행하지 말고 지팀장에 즉시 차단 사실을 알린다. `NO_DELTA`는 지정된 안전 작업이 실제로 모두 완료·차단되고 새 명령도 없을 때만 적는다. Git 인증 실패·pytest 부재는 `BLOCKED`이며 `PUSH_VERIFIED` 아님.

## 1.1 작업 원본 탐색·승인 (지팀장 전담)
- **C03/C05**는 `origin/integration/p1.5`에서 현재 RF 원본의 정확한 경로·단계·Owner·독점 파일 범위 및 G1~G3(기존 7항목은 역사) 조건을 조회한다. C03은 코드·테스트·호출자·효과와 기존 증거를 확인하고 A/B가 수행할 **개별 파일·함수·수정/이동/검증 단계**만 C01/C02에 작성한다. 다른 Owner/보호 코드 변경이 필요하면 C03/C05 권한 판단 전 지시하지 않는다.
- **A/B는 C01/C02 단일 진입점만 읽는다.** D00·CURRENT·RF 원본·큐 탐색은 작업자가 매회 할 일이 아니다. 지팀장이 현재 단계, 안전 조건, 허용 범위와 상대 검증 SHA를 누락 없이 전달할 책임이 있다. 실행 중 새 지시로 바뀌어도 시작 때 읽은 작업을 끝내거나 실제 한도를 기록한 뒤 다음 회차에 반영한다.
- **C05**는 원격 SOURCE SHA·G1~G3 근거로 실제 단계와 STATUS를 수용·종결한다. A/B가 RF Markdown·체크박스·큐·CSV·STATUS를 수정하거나 옮기지 않는다. C04의 통합·CI 및 C05의 DONE 권한은 그대로 유지한다.

## 1.2 런검증 PC 긴급 개발 트랙 — 제한적 예외 (홍사장 직접 승인 2026-10-29)

- **승인 범위:** `integration/p1.5`의 원격 정본을 기준으로 런검증 PC의 **별도 클론**에서 **단 하나의 브랜치 `emergency/p15-fixes`**를 생성해 안전한 소스·테스트 수정/정상 푸시를 수행할 수 있다. 이는 기존 예약 Claude A/ Codex B 작업 브랜치와 독립적이다. 신규 A/B 긴급 브랜치, `main` 직접 수정, `integration/p1.5` 직접 수정·병합, 강제 푸시·이력 재작성은 승인하지 않는다. 원격에 해당 브랜치가 아직 없으면 `NOT_CREATED`로 분리하며 생성됐다고 가정하지 않는다.
- **작업 흐름:** 로컬 **Codex가 긴급 브랜치에서 개발·테스트·커밋·푸시**하고, **홍사장의 2026-10-29 추가 직접 지시**에 따라 **지팀장 C03도 기존 동일 `emergency/p15-fixes` 브랜치의 안전한 code/test에 한해 직접 최소 수정·정상 푸시**할 수 있다. 로컬 **Claude는 정확 SOURCE SHA의 별도 격리 checkout/clone을 읽기 전용으로 독립 검증**한다. **Codex와 C03은 같은 파일 수정 전 원격 HEAD·blob과 각자 작업 중인 경로를 확인하고, 선행 상대 작업을 덮어쓰지 않으며 경합 시 작업을 멈추고 안전 병합/다른 파일로 전환**한다. 같은 작업 트리의 동시 수정·테스트 산출물 공유 금지. Claude의 리뷰는 선택적 비차단 검증이며 FAST-3 G2의 필수 선행 조건이 아니다.
- **진입·권한:** 긴급 로컬 Codex/Claude에 C01/C02/C03/CURRENT를 따를 의무를 부과하지 않는다. C03이 짧고 구체적인 긴급 프롬프트로 파일·함수·테스트·안전 범위를 전달하거나 **위에서 승인된 좁은 긴급 code/test 수정을 직접 수행**한다. 그렇더라도 이 **D00 §2 FAST-3와 Owner·real-mode 경계**를 준수하며 코드/코드 테스트 이외의 D00·CURRENT·C문서·RF·큐·CSV·STATUS·patchnotes·CI workflow/보호 정책 작성은 긴급 개발자가 수행하지 않는다. **지팀장의 D00·C03 관리문서 변경은 사용자 명시 요청 시 그 본래 역할로만 수행**한다. 이 예외는 과거 타인 A/B 브랜치에 대한 C03의 코드 쓰기를 소급 승인하지 않는다.
- **실행 PC 분리:** RunLab과 **동일 PC일 수 있으나** 반드시 운영 checkout·컨테이너·실계좌·실주문·운영 로그·DB·State·캐시/보고 디렉터리와 물리적으로 다른 작업 디렉터리·테스트 임시 root를 사용한다. mock/fake/temp 검증만 허용한다. 운영 `--apply`, 브로커/Guard/Supervisor/Executor/Step5C/UEF 실효과, live network 호출, frozen oracle/CI 보안 완화 및 운영 재배포는 기존 승인 없이는 금지한다.
- **C03 매회 추가 점검:** `emergency/p15-fixes` 원격 브랜치 **존재 여부·HEAD/BASE·신규 커밋/변경 파일/관련 테스트 결과**를 확인한다. 예약 A/B 및 `integration/p1.5`의 최신 소스·수정 경로와 대조해 **중복·충돌·선행 통합**을 판별한다. 원격 파일 존재와 pytest normal/`python -O` 수행·Claude 독립 peer·hosted CI는 각각 **별개의 증거**로 기록한다. 로컬 PC 세션·테스트 로그가 제공되지 않았다면 `NOT_VERIFIED`; commit timestamp를 작업 실측시간으로 만들지 않는다. 신규 원격 변화가 없으면 재조사·중복 댓글/문서 커밋 없이 종료한다.
- **인계/수용:** 실제 신규 수정이 안전하고 필요하면 C03이 `EMERGENCY_SHA | BASE_SHA | CHANGED_PATHS | A/B_OVERLAP | TEST_NORMAL/-O | PEER | FIRST_UNMET_G1-G3 | NEXT`를 #36에 기록해 **C04 선별 통합·정확 통합 SHA CI**와 **C05 RF 단계·STATUS·DONE 수용**에 인계한다. #36은 신규 긴급 판정 발생 때만 읽는 선택적 인계 자료이며 C04의 상시 4번째 delta 입력이 아니다. **전체 브랜치 자동 병합·무검증 cherry-pick·RF DONE 승격 금지.** 필요 시 C04가 본인 C04 지시서에 정확 긴급 SHA/선별 경로를 반영하여 실행한다. 긴급 개발·테스트 완료(`DEV_RESOLVED`)는 RunLab의 `RUNTIME_VERIFIED`와 구별하며 운영 사건의 종결 조건을 대신하지 않는다.
- **정책/CI 효력:** 이 D00 개정은 긴급 트랙 개설과 **지팀장 본인의 단일 긴급 브랜치 code/test 직접 수정**에 대한 **명시적·제한적 허가**이지 현재 유효한 §2 FAST-3만 적용하며 과거 7항목·Hosted CI 의무는 개발 DONE의 필수 게이트가 아니다. 안전·권한 규칙 변화에 영향을 받는 CI 증거는 C04/C05가 재판정하고 과거 CI를 자동 상속하지 않는다. **2026-10-29 홍사장의 긴급 직접 수행 추가 지시를 반영한 이번 개정** 후에도 C03 예약 실행은 별도 승인 없이 D00을 반복 수정하지 않는다.

## 2. RF FAST-3 수용 계약 — 2026-10-29 홍사장 속도 우선 승인

**효력:** 이 절은 과거 C1~C7 전수 체크·§2.1/§2.2 전체 peer/매-RF -O/엄격 재CI의 요구를 대체한다. RF마다 현재 효력 있는 체크는 아래 **G1/G2/G3 세 개뿐**이다. 기존 C1~C7 증거·이력은 보존하지만 신규 DONE의 필수 게이트가 아니다. C03~C06 및 상태 동기화 도구·RF 문서·예약이 이 계약보다 오래된 조건을 요구하면 이 절이 우선한다. **개인 연구·모의투자 개발** 단계의 빠른 반복을 목적으로 한다.

### G1 — CODE_READY (원격 소스 확인)
- RF에 지정된 Owner와 변경/유지(KEEP) 범위를 확인한다. 변경 파일·기능·핵심 호출자에 실제 문제 없거나 발견 결함을 수정하고 원격 코드 SHA를 확보하면 MET. 기존 전체 파일의 MOVE/KEEP/WRAPPER/SAFETY_HOLD 판정표나 전체 IO/State/예외 전수 보고는 **필수 아님**. 미변경 파일은 기존 증거 또는 blob 동일성으로 신속 KEEP.
- 원격에 새 변경이 없는 RF도 본래 동작·책임 분리가 이미 적절하면 KEEP_VERIFIED로 MET 가능. 모든 Owner마다 재시험/새 문서 생성 금지.

### G2 — TEST_READY (변경 범위의 빠른 테스트)
- 실제 변경한 함수와 직접 영향받는 호출자 중심으로 **관련된 pytest 또는 재현 가능한 Python smoke 정상 실행 exit0** 1회면 MET. 버그 수정은 가능한 경우 실패 재현 하나와 회귀 하나를 유지하되, RF 전체 suite·모든 Owner 전수 테스트·모든 RF의 python -O 중복 테스트·상대팀 full-C4 독립 PASS는 **필수 아님**.
- 상대팀 peer는 선택적인 비차단 병렬 리뷰다. 실제 위험이 큰 변경이나 새 오류 발견 시 대상 함수 한정 음성 테스트를 권장하지만 기다리느라 RF 전체를 막지 않는다. 정확 SOURCE SHA와 테스트 종료코드만 기록한다. pytest가 없는 예약 환경에서는 재현 가능한 최소 stdlib smoke(exit0) 또는 해당 코드 범위의 기존 GitHub CI PASS를 G2 근거로 수용할 수 있다. 실행 안 한 검사를 PASS로 기록하지 않는다.
- 알려진 실패가 변경 기능/모의 런을 실제로 깨면 고치거나 별도 OPEN_BUG로 기록해 후속 RF에 넘길 수 있다. **실제 실계좌 활성화 위험**은 이 예외에서 제외한다.

### G3 — INTEGRATED_DONE (통합 + 결과 반영)
- C04 또는 승인된 통합 담당이 현재 원격 integration/p1.5에 최소 소스 반영 또는 동일 소스 KEEP을 확인한다. 대상 변경의 **관련 smoke/targeted CI 정상 실행 또는 해당 integration SOURCE SHA의 기존 성공 증거** 1개로 충분하다. 전체 프로젝트 hosted normal/-O CI, 모든 RF별 새 Actions dispatch, 전체 suite Green은 필수 아님.
- C05는 G1/G2/G3를 체크하고 RF를 05_DONE으로 이동하여 STATUS를 동기화한다. 이 이동은 본 **리팩터링 개발 DONE**이며 운영/실런 RUNTIME_VERIFIED를 뜻하지 않는다. RF가 특별한 이유 없이 PEER/LEAD 큐에서 장기 정체되면 C05는 G1/G2 충족 즉시 통합을 배정한다.
- CHECKED 상태는 MET 또는 이유가 있는 N/A만 가능; 미충족은 PENDING/PARTIAL/MISSING/BLOCKED로 둔다. 역사 7항목의 미체크는 새 G1~G3 판단을 막지 않는다. G1/G2가 MET면 기존 02/03 단계를 건너뛰어 04_LEAD_ACCEPTANCE로 전진할 수 있다. G3 MET 뒤 05_DONE. 06_REWORK는 실제 대상 기능 실패 확인 시만 사용한다.

### 모의투자와 실제 런검증 분리
- 모의투자(mock/paper) 주문·상태 변경은 **별도 모의 계정/테스트 경로와 모드가 검증된 경우** 개발 중 허용하며, 버그는 수정 후 다시 시험한다. 모든 매매 코드 변경에 실거래 수준의 2인 검증/전체 효과 매트릭스/UEF 과거 스냅샷 승인을 강제하지 않는다.
- 실제 런검증(RunLab)의 배포/운영 증거는 리팩터링 RF의 G1~G3 DONE 뒤 별도 단계에서 수행한다. 런검증 실패가 확인돼도 RF DONE을 자동 취소하지 않고 새 오류로 추적한다.
- **실계좌·실금전 거래/real mode enable은 이 승인 범위 밖**이다. mock임을 확인할 수 없거나 실계좌 가능성이 있으면 real 실행은 차단하고 별도 명시 승인 필요. 비밀정보, 사용자의 개인 파일/운영 자산, 강제 푸시·이력 변경·타인 브랜치 무단 쓰기 금지도 유지한다.

## 3. 안전 경계·작업 격리
- 무승인 실계좌·실주문·브로커/운영 외부 쓰기, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, frozen test/oracle/CI, 비밀정보, 운영 DB·State·데이터, 배포·예약 변경/실행 금지. 별도의 명시적 사용자 승인이 필요하다. mock/temp/fake 우선, 실런 RunLab와 개발 테스트를 구별한다.
- RF-069 UEF5 historical snapshot은 경로·SHA·use-scope 및 사용자/증거 소유자 승인 전 `NOT_RUN/SAFETY_BLOCKED`. RF-032/034 UEF·closeout 보호를 우회하지 않는다. RunLab #32의 `RUN_SOURCE_SHA=UNKNOWN`은 운영 버전 검증 차단이지 자동 코드 회귀 판정이 아니다.
- **기본적으로** 새 브랜치·tag·PR·worktree, `main` 변경, force push, 이력 rewrite 금지. **유일한 명시적 예외:** §1.2에서 홍사장이 승인한 `emergency/p15-fixes` 브랜치 **1개**의 생성과 해당 브랜치로의 정상 코드·테스트 푸시만 허용한다. 다른 신규 브랜치/PR/worktree·원격 보호 우회는 예외 아님. 허용된 브랜치 최신 HEAD/소유 파일 확인 후 작업, 경합 시 재조회. UI code와 patchnotes 등 문서 동반 변경이 필요하면 지팀장 작업을 별도로 요청한다.

## 4. 이슈 댓글·진척 기록
- A/B는 신규 성과·막힘 발생 시 **자기 Issue 댓글만**: `ORDER_STEP | SOURCE_SHA | CHANGED_CODE/TEST_PATHS | COMMAND + normal/-O result or NOT_RUN | PUSH_VERIFIED/FAILED | BLOCKER/NEXT` (RF/C1~C7 귀속 판정은 지팀장 담당). 실험은 실제 명령과 종료코드 구분. 댓글에 반복 증거 전체 복사 금지; 이미 공유한 댓글 링크로 재사용. 코드 변화 없는 문서/검증 기록용 커밋 금지.
- 지팀장은 #11·#12·#32의 **신규** 사실 및 §1.2의 **긴급 브랜치 신규 원격 커밋**만 인수해 필요한 RF 원본을 직접 확인한다. 실제 배정·상태 변경 시에만 C문서/RF/STATUS 등을 갱신. **새 판정만 #36 댓글**: `C03|C04|C05 | INPUT_COMMENT 또는 EMERGENCY_SHA | RF | DECISION | SOURCE/PEER SHA | CI | UPDATED_PATHS | BLOCKER/NEXT`. 변경 없으면 쓰기/댓글 0.
- RF 원본 이동/체크 갱신 시 C05가 `python docs/refactor/tools/sync_rf_checklist_status.py --write` 및 `--check` 실행(실행 환경이 없으면 `NOT_RUN` 명시), 총 93 RF 유일성과 stage 수 검증. G3 대상 smoke/CI 또는 동일 소스 증거 확인 전 DONE 증가 금지.
- 장애와 제한은 구분: `NO_DELTA`(실제로 새 안전 작업도 없음), `BLOCKED`(권한/환경/정확 C 차단), `EXECUTION_LIMIT`(실제 도구 한도 신호 확인). 한도 때만 `LIMIT_TYPE | EVIDENCE | LAST_DONE | NOT_DONE | NEXT` 기록; 추정 수치·크레딧 원인 단정 금지.

## 5. RunLab 분리
- 정본 [R00](../../runtime/validation/R00_RUNTIME_VALIDATION_RULES.md)·[D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md)·[RunLab CURRENT](../../runtime/validation/CURRENT.md)·[Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). RunLab은 관측·새 사실을 #32 댓글로만, 지팀장은 신규 건만 사건 대장에 접수/원 RF owner 판정. 개발 `DEV_RESOLVED` ≠ 런타임 `RUNTIME_VERIFIED`; 승인된 적용 이미지·실증 없이 사건 CLOSED 불가. 안전 HOLD는 영향 경계에만 적용한다.

## 6. 예약 연동·재개 계약 (홍사장 2026-10-29 승인)

본 절은 현재 §2 FAST-3에 종속된다. Owner 독점, 실계좌 차단과 런검증 분리는 유지한다. 원래 C1~C7 전수 peer·hosted normal/-O CI 의무는 삭제되었다. 예약 시작은 완료/실행시간/푸시 권한 보장이 아니다.

### 6.1 단계별 예약·인수
- 속도 우선 1시간 순환(KST): C03 매시 분00 RF 작업 배정 → Codex B 매시 분10 변경·테스트(Claude A 외부 예약 별도) → C04 매시 분35 G1/G2 충족 RF를 최소 통합·targeted smoke → C05 매시 분45 G1~G3 확인·READY 승격 또는 즉시 DONE/STATUS. C06은 4시간 간격 분55에 비차단 성과 감사. 앞 담당이 끝나지 않았어도 완료된 다른 RF는 즉시 처리한다. 예: 10:00/10:10/10:35/10:45, 다음 11:00 반복.
- 시각만으로 앞 단계 완료를 가정하지 않는다. 앞 담당이 IN_PROGRESS/BLOCKED/NOT_RUN이면 최신 실제 원격 코드·Issue·RF·CI 증거로 가능한 단계만 수행한다. 앞 단계 미완료는 새 RF의 통합·DONE을 허용하지 않는다.
- C06은 독립 읽기 전용 감사이며 C06_AUDIT_CURRENT.md를 단일 감사 지침으로 사용한다. #37 감사 출력, #11/#12 개발자 증거, #36 지팀장 인계다.

### 6.2 A/B 단일 지시 버전·환경·재개
- A/B는 실행 때 원격 integration/p1.5의 C01 또는 C02 한 파일을 직접 읽어 CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, OWNER_REMOTE_SHA를 고정하고 번호별 ORDER_ID = C01|C02 : ORDER_FILE_BLOB_SHA : ITEM_NO를 만든다. 오래된 local ref·세션 메모·HANDOFF를 대신 사용하지 않는다. 실행 중 C03이 바꾸면 시작 당시의 원격 지시를 완료하거나 실제 체크포인트 후 다음 회차에 새 버전을 적용한다.
- 첫 행동으로 owner 원격 SHA, 작업 트리 dirty/경합 및 허용 파일, Python 정상/-O pytest 모듈 존재, Git 원격 읽기/승인된 push 경로를 점검한다. 실제 push 성공은 이후 원격 blob을 별도 확인한다.
- 번호별 ITEM_STATUS는 PENDING / RUNNING / LOCAL_IMPLEMENTED / PUSHED / TEST_VERIFIED / PEER_VERIFIED / VERIFIED_ALREADY / BLOCKED / NOT_RUN. VERIFIED_ALREADY는 정확 SOURCE SHA·대상 변경 범위·실제 smoke/pytest exit 근거가 있을 때만 쓴다. RF 물리 단계/현재 G1~G3은 C05 독점 판정이며 ITEM_STATUS와 같지 않다.
- 매회 #11/#12에 최소 ORDER_ID, ORDER_FILE_BLOB_SHA, OWNER_SOURCE_SHA, 번호별 상태, CHANGED_PATHS, normal/-O 실제 exit 또는 NOT_RUN, PUSH_REMOTE_SHA 또는 정확 차단, LAST_COMMAND/FUNCTION, ERROR, UNBLOCK_OWNER, NEXT, 실측 START_KST/END_KST/ELAPSED_MIN(없으면 NOT_VERIFIED)을 남긴다. 로컬 구현·compile/smoke·테스트 파일 존재를 원격 PASS로 간주하지 않는다.
- pytest 부재는 해당 테스트만 BLOCKED, 인증/private export 금지는 push만 BLOCKED, 플랫폼 실행 한도는 그 명령만 BLOCKED. 나머지 허용 코드·tmp/fake 테스트·peer는 계속한다. 정책 우회·임의 새 브랜치·force push 금지. 중단 시 마지막 실제 명령/함수와 재개점을 남긴다.

### 6.3 C05 사전/사후 수용·문서·감사
- C05 사전 단계: G1 원격 범위/소스와 G2 변경 부분 smoke/pytest 증거로 LEAD 승격. 반대팀 전체 독립 peer를 기다리지 않는다. C04는 LEAD를 최소 통합/KEEP 후 관련 smoke 또는 동일 SHA의 성공 CI 증거를 제출. C05 사후 단계는 G3 충족 즉시 DONE/STATUS 완료. 긴급 DEV_RESOLVED는 이 과정 및 RunLab RUNTIME_VERIFIED를 대체하지 않는다.
- D00은 정책이 변할 때만 갱신한다. C03은 새 C01/C02에도 이 절의 실행 preflight/버전/보고 요구를 넣고, C03~C05 각 문서는 현재 규칙·다음 실행 조건만 유지한다. 오래된 테스트·중복 PASS·회차 로그는 문서에 누적하지 않고 Issue/원본 RF/CI 링크로 참조한다.
- C06은 신규 원격 변화 및 첫 미충족 C를 중심으로 실효 성과(원격 변경, G1/G2, G3 통합, DONE 증가, 차단 해소)를 감사한다. 시간/테스트 수는 보조 지표. 신규 시정사항에만 #37과 필요한 대상 Issue를 작성하며 반복 댓글을 만들지 않는다.
- GitHub Actions의 기존 정확 SHA CI 결과 읽기·증거 검증은 허용된 운영 범위에서 이용하되 FAST-3에는 전체 hosted CI가 필수는 아니다. 신규 workflow/CI 보안·branch protection·frozen oracle 변경이나 Git push 이벤트로 ChatGPT/Claude/Codex 세션을 직접 기동하는 별도 실행기는 이 절만으로 승인되지 않는다.
