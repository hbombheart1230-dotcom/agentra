# Agentra P1.5 전체 ROOT→LEAF 리팩터링 현황

**기준선(역사 고정):** `63182ab27ecf889768003f637a40577ba1277f86` · **3,985파일/298디렉터리/93개 RF**. **현행 구조(기준 `d082cee8`): 4,080파일/302디렉터리**; 신규 T01~09 문서 9개가 합쳐지면 **4,089파일/302디렉터리** (커밋 후 HEAD 검산 필요). **RF 상태 (2026-10-26 14시 KST, 물리 큐 검증): pending 69 / verification 14 / rework 0 / DONE 10** (RF-002~006, 009, 020, 068). 과거 'DONE 0'은 오류였으며 이 기록으로 정정.

## 추가 큐·개발 배정 판정 (2026-10-26 14시 KST)
- **RF-017 PENDING→DONE:** 기존 Commander 5 owner BASE↔integration·tests 변경 0, A 273문장 100% self normal/-O 및 B `RF017_KEEP_PEER_OK 7` integration read-only peer normal/-O exit 0 재사용. KEEP_NOOP_VERIFIED, 신규 Supervisor/Executor RF-048/060/044는 독립 HOLD, 지팀장 pytest NOT_RUN.
- **RF-019 PENDING→VERIFICATION/CLAUDE:** A 29/29 owner KEEP/FIX0, 99.7% scoped 소비자·State/IO·효과 판정 제출, B 기존 evidence/guard/practical/overlay/build offline peer normal/-O scoped PASS, BASE↔integration `libs/runtime/scanner/**` 및 tests 변경 0. **개발 종료, 지팀장 최종 인수조건/KEEP_NOOP 판단만 남음.**
- **신규 A 개발 배정:** RF-028(85 owner, Reporter trade_report) → RF-029(38 owner, trade_story), 정본 pending RF 상단에 A owner 명시. 기존 RF-013/017/019 반복 개발 금지.
- **물리 큐:** pending **69** / verification **14** / rework **0** / DONE **10** (93). CSV는 BASE 소유권의 역사적 `UNVERIFIED` 표기이므로 다른 DONE RF처럼 불변 유지.

## 최신 지팀장 판정 (2026-10-26 14시 KST)
- **RF-013 VERIFICATION→DONE 물리 이동:** 기존 Reporter 67/67 owner는 BASE `63182ab2` ↔ integration `2f77bd95`에서 변경 0, tests/** 변경 0. A 원복 `e7471a2e` normal/-O 각 2863 PASS/4 SKIP, B 독립 RF-074/p171 각 134 PASS normal/-O, A 마지막 4 owner BASE↔integration normal/-O byte-identical, 90% 미만 owner 0. **KEEP_NOOP_VERIFIED**, source 통합 0. 신규 9+4 거부 후보는 원복·통합 제외. 지팀장 직접 pytest NOT_RUN(기존 증거+코드·테스트 blob 동등성 재사용).
- **RF-001 두 owner 선별 소스 통합 완료, RF 자체 미종결:** B `b994a133` → integration monitor-notes `4f73570f` / core `0666538f` blob 정확 일치, 코드 커밋 `6d8f8234`, `f9126467`; patchnotes JSON/MD 보존 병합 `6224a979`, `2f77bd95`. 격리 normal/-O 734×2·A peer 734×2/17 differential·B UI 53×2 기존 PASS 수용. **반영 exact integration HEAD normal/-O NOT_RUN**: B 1회 read-only 검증 후 지팀장 DONE 게이트 판단. 개발 RF-001 재배정 금지.
- **큐:** pending **71** / verification **13** / rework **0** / DONE **9**. 다른 RF·main·안전·오라클 변경 없음. A 다음 개발 RF-019→017, B 다음 RF-070→066. D03 최신 수신 A 완료/B PENDING. 예약 변경 없음.

## 최신 지팀장 판정 (2026-10-26 13:35 KST)
- A/B **신규 owner 소스 SHA 0**. RF-001 최초 격리 peer A `ae860f9c`: normal/-O 734×2 PASS·differential 17건 수용, `PEER_SCOPED_PASS`; `test_operator_ui.py`는 A fastapi 미설치로 NOT_RUN → B 격리 환경 UI normal/-O·patchnotes 후 ADMIT 재판정. RF-013 A `2026-10-26T0428Z` normal/-O 격리 하네스 11+2 PASS, 67 owner coverage 92% → KEEP_SCOPED; 잔여 4 경계 미완료. **소스 통합·RF 이동·DONE 0**, pending 71 / verification 14 / rework 0 / DONE 8. D03 변경 blob `89826e10` A/B 정책 재수신 아직 PENDING. RF-066 실제 주문·고정 파일 쓰기만 HOLD, 정적·안전 격리 mock은 계속 허용.

## 최신 큐 판정 (2026-10-26 12:33 KST)

- **RF-070 pending→verification/codex 이동 확인:** 기존 안전 순수 wrapper 85/142에 대한 A/B 독립 offline/mock normal/-O scoped PASS 재사용, 잔여 57은 32 SAFETY_HOLD + 25 read-only 위험·소비자 분류로 제한. 구 pending 경로 404, 새 verification RF 문서 존재; CURRENT도 verification 지시. **71 pending / 14 verification / 0 rework / 8 DONE.** 전체 RF PASS/DONE 아님. A/B 신규 소스 SHA 없음(`e7471a2e`→A HEAD HANDOFF만, `b994a133`→B HEAD HANDOFF만). RF-001 두 owner blob은 B/격리 `cdc3599f` 동일, integration 미반영; A 최초 격리 조합 peer 및 `test_operator_ui.py` normal/-O와 통합 exact-SHA 테스트 전 ADMIT/DONE HOLD. RF-018 202×2/잠재 폴백 3건은 12:26 기존 판정 재사용. 이번 회차 소스 통합·새 pytest NOT_RUN, 예약·main·안전·오라클 변경 없음.

## 이전 지팀장 판정 (2026-10-26 09:00 KST)

- **RF-001 물리 큐 복구 완료:** B CODE `53416d4c` 17 owner KEEP 복귀에 대한 A `f633d6cd` 독립 peer scoped PASS 수용. 기존 `rework/codex/RF-001.md` 전 내용이 `verification/codex/RF-001.md`에 포함됨을 확인 후 구 중복 사본 삭제. 원개발자 소유 후보 회귀가 복귀되었으므로 REWORK→VERIFICATION/BLOCKED; B branch composite frozen 28 FAIL은 교차 RF/history inventory로 분리하되 전체 frozen PASS로 간주하지 않음. 신규 source/테스트/오라클/통합 없음. **72 pending / 13 verification / 0 rework / 8 DONE.**
- **다음 실행:** B는 A RF-019 신규 위험 경계 peer와 RF-070 잔여 25개 기타 구현 read-only 소비자·효과 분류. A는 RF-019 잔여 21 owner 및 RF-017 normal/-O 새 경계. RF-013 9+4 미승인, RF-070 위험 32 실행 금지, RF-069 UEF5 환경 차단 유지. Issue #32 신규 댓글 0; hosted CI 제외(D03), 지팀장 pytest NOT_RUN.

## 이전 지팀장 판정·다음 실행 (2026-10-26)

- **08:00 KST 큐 집계 정합성 수정:** RF-001은 CURRENT·`rework/codex/RF-001.md`의 최신 원개발자 REWORK 판정이 정본이며, 구 `verification/codex/RF-001.md`는 도구 삭제 안전 차단으로 남은 **물리 중복 사본**이므로 논리 큐에서 제외한다. 이에 따라 **pending 72 / verification 12 / rework 1 / DONE 8**로 집계한다. 물리 큐 일치 PASS 아님. B 새 `RF001_REWORK_ACK`·수정 CODE_SHA는 아직 없고, A/B 원격은 최신 HANDOFF-only(새 소스·테스트 0). RF-070 85/142 행동 scoped peer 및 잔여 57/57 정적 분류, RF-066 정적 peer, RF-019 8파일 101 PASS는 기존 판정 유지. Issue #32 신규 댓글 없음, 통합/직접 테스트 NOT_RUN, hosted CI 조회 제외(D03).


- **03:33 KST 신규 독립 증거:** A RF-070 첫 3 wrapper offline/mock normal/-O peer exit 0 + trace 소비자 각 3 PASS 수용(3/142 scoped, 전체 PENDING 유지); 지팀장 B/integration 다음 3 wrapper blob 동일성 확인, B mock→A peer 배정. RF-001 A 신규 16 alias·90 parity normal/-O scoped PASS이나 B 후보 동결 구조 734 중 각 28 FAIL(현 integration 각 734 PASS)로 원자 admission HOLD; B 원소유 대안/KEEP 분리, 오라클 변경 불허. A/B 소스 SHA 불변, 이번 회차 통합·DONE·큐 이동 없음. **상태 72/13/0/8 불변**, 지팀장 pytest NOT_RUN, Issue #32 신규 증거 없음, hosted CI 조회 제외.

- **02:29 KST 신규 증거 판정:** B HEAD `02919e45` RF-018 역사 2 node BASE/integration normal/-O 동일 2 FAIL, `HISTORICAL_INVENTORY`로 분리(새 회귀 아님). 57 shared-contract collection 양측 exit 0은 과거 57 ERROR 해소 증거 아님; RF-018 VERIFICATION 유지. RF-070 142개 KEEP inventory 수용, 지팀장 기존 3개 15행 compatibility wrapper 소스 직접 확인해 B offline/mock·A peer 첫 범위 지정(동작 NOT_RUN). A HEAD `6d6fcc16` 신규 소스 없음. RF-013 신규 9+4 NOT_ADMITTED 유지, Issue #32 새 증거 없음. **상태 72/13/0/8 불변; 통합/DONE 추가 없음.**


- **02:04 KST RF-020 DONE:** Monitor 30/30 owner BASE/integration/B blob 동일 KEEP, A 독립 소비자 19파일 normal/-O 각 528 PASS/exit 0, B 보조 221+8 PASS 재사용. peer `16ed53e4`→integration `7c4668e2` 비교에서 Monitor·tests 변경 0; 외부 Operator Brief 2·refactor helper 1 변경은 별도 소유. 역사 B-stage 64 FAIL과 RF-026 안전 순환 import HOLD는 분리하고, 특정 신규 결함 없는 추상적 전수 요구는 D03 §3A로 해제. 소스 선별 통합 NOOP, 통합 동일 코드/테스트 범위 기존 normal/-O 수용, 현행 문서 HEAD 직접 pytest NOT_RUN. **verification/codex → done; 72/13/0/8.** hosted CI 불요. Issue #32 신규 댓글 없음.

- **01:28 KST RF-009 DONE:** Graph 3/3 owner integration/B/BASE blob KEEP, A detached peer normal/-O 각 145 PASS + rank/State/fallback/monkeypatch 표적 각 33 PASS 수용. 과거 integration `958431c3`→현행 `cd1cccb8` GitHub compare 코드·테스트 변경 0(AGENTS/CLAUDE·docs만 변경) 확인, 통합 코드 동등성으로 기존 normal/-O 재사용(현행 문서 HEAD 직접 실행 NOT_RUN). 구체 미충족 위험 없는 일반적 '전수 미입증' 요구는 D03 §3A로 해제, **verification/codex → done**, source 선별 통합 NOOP. RF-069 A 신규 2 CLI offline/mock peer normal/-O exit 0 수용, UEF5 승인 snapshot 부재로 verification 유지. **72/14/0/7**. CI 조회·GREEN 대기는 제외, Issue #32 신규 댓글 없음. 새 source/안전/오라클 변경 없음.


- **01:03 KST RF-068 DONE:** A 독립 8/8 peer 경계 normal/-O 기존 PASS(11/15/5 offline/12), B·integration 8/8 소스 blob 동일 KEEP. GitHub `f097690b → integration` 및 `ac7bf5ac → integration` compare에서 변경 경로 전부 문서, 소스·테스트·오라클 0 변경을 확인. D03 §3A에 따라 과거 **각 integration 정확한 코드 SHA**의 normal/-O PASS를 현행 동일 코드·테스트 트리에 재사용(현행 문서 HEAD 물리 재실행 NOT_RUN, hosted CI 불요). 소스 선별 통합 NOOP, RF-068 `verification/codex → done`; **72/15/0/6**. 신규 코드·안전·오라클 변경 없음. RF-069 잔여 2 CLI offline/mock + UEF5 환경 차단은 유지. A/B 신규 소스 없음, Issue #32 신규 댓글 없음.

- **00:30 KST 신규 상태 전환:** A 최신 `0f31a9b6` RF-068 8/8 독립 peer scoped 증거 수용, 지팀장 integration `5807be6f` ↔ B `2a86eb17`의 8개 generator blob 직접 8/8 동일 확인. RF-068 KEEP_VERIFIED, 소스 통합 delta 0; 통합 SHA normal/-O 실행 증거만 NOT_RUN, DONE 보류. RF-069는 A 신규 독립 normal/-O 9+9 및 소비자 47+47 scoped PASS, 7/7 owner blob 동일 확인으로 **pending→verification/codex** 이동. 미검증 CLI 2경계 및 UEF5 offline snapshot 부재 ENVIRONMENT/CROSS_RF는 별도 차단; B 잔여 mock·A 신규 peer, 이후 RF-070 read-only 범위. **상태 72/16/0/5**. CI 조회·대기 제외(D03), 신규 source/오라클/안전 변경 없음. Issue #32 새 댓글 없음.

## 이전 판정 (2026-10-25)

- **23:31 KST 상태 전환:** RF-068 8개 generator B/integration 소스 diff 0 KEEP 후보. B offline/mock 3경계 normal/-O exit 0, A 별도 peer 같은 3경계 normal/-O exit 0 신규 수용; 기존 metrics/ops 2경계 A peer 재사용. **5/8 peer scoped**, strategist/symbol 2경계 B self 15+15 및 daily_report 기존 5테스트는 최종 독립 확인 미완. RF-068 `pending → verification/codex` 이동, **73/15/0/5**. A 잔여 peer, B 신규 RF-069 배정. 통합 SHA normal/-O NOT_RUN, DONE 증가 없음. hosted CI 조회는 D03에 따라 제외. RF-013 9+4 NOT_ADMITTED 유지; Issue #32 신규 증거 없음.


> **최신 판정 우선 (21:27 KST):** 아래 19:35 이전 항목의 `74/11/3/5`, RF-001/009/020 REWORK 배정은 **역사 기록**이며 현재 큐 상태가 아니다. 아래 최신 회차 결정과 CURRENT가 우선한다.

- **10/25 22:26 KST 신규 판정:** B `B-20261025T131257Z` RF-013 기존 67경로 frozen test normal/-O **각 105 PASS** → `PEER_SCOPED_PASS` 수용(전체 계약/통합 아님). 신규 read_models 9 및 RF-030/035 wrapper 4는 원본 RF-074 104 PASS/1 FAIL로 NOT_ADMITTED 유지. A `sched-64` RF-068 metrics/ops normal/-O **각 11 PASS** 독립 peer 인정, B strategist/symbol normal/-O **각 15 PASS** 자체 증거 추가. 지팀장 직접 GitHub에서 operator_summary와 M28 호환 entrypoint 2개의 실제 코드를 읽고 offline/mock 미검증 경계를 B에 구체 배정, A에는 신규 15 peer 배정. **RF 큐 74/14/0/5 불변, 신규 source/통합/DONE 없음.** 지팀장 pytest NOT_RUN. Issue #32 신규 댓글 없음. exact integration CI GREEN 미확인.
- **10/25 21:27 KST 지팀장 실제 신규 판정:** A HEAD `73c5ad86`(HANDOFF-only), B HEAD `c9919aa7`(HANDOFF-only), 원격 새 source 없음. A RF-009 독립 peer normal/-O **각 33 PASS** 신규 근거 수용(기존 각 145 PASS 재사용), `PEER_SCOPED_PASS / NOT_DONE`. B RF-013 후보 `a21401db`에 RF-074 **원본 frozen test** blob `cabcecfe` overlay normal/-O **각 104 PASS/1 FAIL**, node `test_target_tree_discipline_and_no_forbidden_surface`; 지팀장도 GitHub에서 A 수정 test blob `915fca9c`의 신규 9 allowlist 확인. **9 read_models NOT_ADMITTED**, RF-030/035 4 wrapper 통합 제외, RF-074 오라클 불변. RF-013 **기존 67 owner KEEP 경로**를 B가 integration 기준 별도 read-only peer로 검증하도록 범위 재설정; 신규 9+4 반복 테스트·무승인 코드 수정 금지. B RF-068 8 generator 소스 B↔integration 변경 0, metrics/ops 2 테스트 normal/-O 각 **11 PASS**로 `SELF_PASS_SCOPED / PENDING`, A 신규 peer 배정, B 나머지 6 generator의 안전한 표적 경계 확인. **RF 큐 숫자 변화 없음, source 통합/DONE 없음**. 이전 20:32 기록의 CI는 역사값; 이번 정확한 integration `e1bb2191` combined statuses 0, PR-triggered runs 0 = **CI UNKNOWN**. Issue #32 신규 댓글 없음. 지팀장 직접 pytest **NOT_RUN**(GitHub 소스·증거 검토만 수행).
- **10/25 20:32 KST 지팀장 실제 조치:** A/B 최신 HANDOFF는 각각 A `sched-63`(D03 구 SHA `b99533ca`), B `B-20261025T111454Z`(D01 구 SHA `81daa098`); 둘 다 새 D03 §3A ACK 없음. 이전 코드 SHA 대비 각 브랜치의 신규 커밋은 HANDOFF만 1건(A/B 각 1), 신규 소스/peer PASS 없음. **D03 §3A를 실제 적용**하여 신규 소스 결함이 재현되지 않은 RF-001·009·020을 `rework/codex → verification/codex` 이동. 기존 normal/-O·독립 scoped PASS 보존, **전체 peer PASS/통합/DONE 아님**. RF-001: integration↔B diff `data_access*` 19변경 = 과거 2경로 scoped 수용 이력 + 남은 17경로 미수용 검토, B 신규 `apps/operator_ui/read_models/` 6경로 별도 승인 보류; 문서 HEAD와 코드 후보 SHA 구분. RF-009: Graph 3/3 blob 동일, A 145 PASS·B 20/12 PASS 유지. RF-020: Monitor 30/30 동일, A 528 PASS·B 8 PASS 유지. A는 **변경·미검증 경계만 peer**; B는 RF-013 read-only peer 후 RF-068 개발.
- **RF-013 직접 교차 증거:** A 후보 `a21401db`는 신규 read_models 9, RF-030/035 wrapper 4 외에 **RF-074 동결 테스트 `tests/test_work_reporter_seed_migration.py` 자체도 수정**(+47/-4, integration blob `cabcecfe` vs A `915fca9c`), A 테스트에 신규 9경로 allowlist가 들어 있음. **오라클 변경 승인 없음**, 후보의 확장 오라클 PASS는 정본 동결 테스트 PASS로 간주 불가. 9경로는 RF-013/A CANDIDATE/NOT_ADMITTED, wrapper 2+2는 RF-030/035, 테스트는 RF-074 동결 유지. **B=RF-013 독립 read-only peer**, RF-030/035 wrapper 변경이 꼭 필요하다는 근거가 나올 때만 **B 조건부 구현/A 독립 peer**를 CURRENT에 별도 활성 배정. 현 단계 wrapper·테스트 소스 수정 금지. RF-013 VERIFICATION/BLOCKED/NOT_DONE 유지.
- **CI/런검증:** 통합 최신 코드/문서 HEAD `280cd4af`에서 combined status **0건**, 조회 가능한 PR-triggered Actions run **0건** → `CI UNKNOWN`(RED 아님, GREEN도 아님). 이번 회차 source 통합·hosted CI 실행·로컬 pytest **NOT_RUN**. 런검증 Issue #32는 기존 INITIAL_SETUP 댓글 1건뿐, 신규 검증 댓글 없음; Docker/UI 관찰 PASS, 전체 키움 Paper+LLM 장중 검증 NOT_RUN, `C:\\AgentraRunLab` 프로젝트 등록 및 image revision 메타데이터 부재 차단 유지. `main`·실거래·안전·CI 오라클 변경 없음.


- **10/25 19:35 KST 추가 운영:** A 원격 `a519f75b` / B `612fe374`, 직전 원격 HEAD 대비 양쪽 모두 HANDOFF만 변경(신규 소스/독립 peer PASS 없음). A RF-017 가상환경 53건 수집 PASS; 4표적 normal/-O 각 178 PASS·56 FAIL은 BASE 동일 56 FAIL로 `BASELINE_EXISTING` 자체 근거 분리, RF-017 PENDING 유지. B RF-009 Scanner→Monitor hydration offline/mock normal/-O 각 12 PASS 신규 자체 증거, rank/tie/NOOP·side-effect 및 peer 미완료로 REWORK 유지. **RF-013 교차 Owner 지팀장 결정:** 신규 read_models 9경로 논리 Owner RF-013/A(수용·통합 미승인), 4 wrapper는 RF-030 2경로·RF-035 2경로(실행자 미배정, source 쓰기 금지), RF-074 frozen 테스트/오라클 동결. B에게 RF-013 후보 `a21401db` 9+4경로 **최초 read-only 소비자·부작용 독립 증거만** 허용; 새 writer 배정은 실제 수정 필요 증거가 있을 때. #32 신규 댓글 없음. 74/11/3/5 유지, 선별 통합/DONE 없음, exact-SHA hosted CI GREEN 미확인.

- **10/25 19:04 KST 신규 B HANDOFF 판정:** B는 RF-001 `test_p15_operator_run_detail_projection.py` normal/-O 각각 22 PASS/exit 0을 자체 보고했으나, 이번 원격 변경은 HANDOFF 1파일뿐(신규 소스 없음). 보고한 `CODE_CANDIDATE=9184e428`은 기존 검토 `8bde643d`보다 23커밋 오래된 조상 SHA여서 현행 전체 B tree exact 검증 SHA가 아님. RF-001에 **SELF_PASS_SCOPED / REWORK 유지**와 33 owner·19 divergent·core 동적 계약·정확한 checkout SHA 증거 요구를 기록. RF-009·020 REWORK 대기, A 신규 코드/peer 없음. 통합 `723a3a91` status 0 / 조회 가능한 PR-triggered workflow 0 → **CI UNKNOWN**, 통합/DONE 없음. Issue #32 신규 증거 없음.

- **10/25 신규 A sched-59 / 지팀장 정체 조치:** A는 D00·D03·D02 SHA 재독 확인, RF-019 29 owner KEEP blob parity와 표적 normal 72 PASS/1 FAIL·-O 111 PASS/1 FAIL 제출. 실패는 Reporting 소비자 이동 관련 `CROSS_RF_OWNER` 의심으로 RF-019에 분리 기록, BASE 독립 재현 전 오라클 수정 금지. RF-017 5 owner KEEP, Operator UI 2개 collection ERROR는 traceback·BASE 미확인 `UNKNOWN`으로 RF-017에 기록. B 새 원격 코드/HANDOFF 없음, RF-001→009→020 우선 REWORK 유지. RF-013 CSV 소유권 오류 정정: wrapper 4개 중 **RF-030 2개**(operator_period_summary, operator_visibility), **RF-035 2개**(metrics_report_generator, phase_runtime_health). RF-013 peer 큐 포인터를 Claude A(자기검증 오류)에서 **Codex B**로 바로잡음. 신규 독립 전체 PASS/선별 통합/DONE 없음; 74/11/3/5 유지.


- **RF-009·020 (B 1순위 REWORK):** A의 기존 범위 한정 peer PASS는 그대로 보존. RF-009는 Graph 3 owner의 State/ranking/NOOP·외부 소비자 경계, RF-020은 Monitor 30 owner의 dynamic/side-effect·KEEP 소비자 맵 증거가 RF 전체 인수조건에 부족하다. **신규 회귀·소스 버그 확정은 아님.** Codex B가 기존 RF 소유 경로의 최소 코드 delta 또는 exact-SHA 완전 KEEP 근거를 제출, Claude A는 새 증거만 read-only peer. RF-014/019·RF-026의 타 소유권/안전 HOLD는 그대로 보존.
- **RF-067** B SELF normal/-O 각 AST 14/14·7 PASS 후 A `f88ee1ea` HANDOFF에서 독립 정적/소비자 `7+17 PASS`씩 **PASS_SCOPED 보고**(정확한 개별 명령·시점/exit는 보강 필요). 14개 공개 preflight CLI 직접 실행·Windows/Unix PATH·Task Scheduler·stdout/exit/환경·부작용 계약은 NOT_RUN/미확정. **VERIFICATION 유지 / NOT_DONE**. B는 위험 CLI를 실행하지 않고 격리 offline/mock 계약 증거·명령/exit 보강, A는 새 근거만 peer. 통합 없음.

- **RF-066** B self normal/-O 각 AST 17/17 및 표적 pytest 7 PASS, BASE/integration/B 17개 소유 경로 diff 0. `pending → verification/codex` 이동; **A read-only peer 1순위**, 브로커 조정·SQLite/intent·Step5D·파일 이동·외부 카탈로그 동기화 CLI **미실행/안전 검토 필요**. NOT_DONE.
- **RF-063** A peer **PASS_SCOPED**(76 소유 blob 동일, normal/-O 각 130 PASS, PYTHONUTF8=1). 13개 위험 키워드 CLI 미실행, cp949 기본 로케일 UnicodeDecodeError 1건은 ENVIRONMENT 확인 필요. **RF-065** A peer **PASS_SCOPED**(54 blob 동일, normal/-O 각 7 PASS, 50개 파일 쓰기 CLI 미실행). 둘 다 전체 소비자·CI 미완료로 verification 유지.
- **RF-018** A BASE/integration 동일 명령 1152 PASS/2 FAIL/57 ERROR 모두 동일: 59건 **BASELINE_EXISTING/HISTORICAL_INVENTORY**, 신규 회귀 0(제출 증거 범위). **RF-014** BASE/integration 각 1102 PASS/3 FAIL 동일: 3건 BASELINE_EXISTING, A 브랜치 Reporter 소비자 2건 CROSS_RF_OWNER. B는 분리된 증거만 독립 검증; 최종 peer PASS 아님.
- **RF-013 (VERIFICATION/BLOCKED)** A 최신 `b94a25d4`가 기존 RF-013 67 owner 파일 불변·신규 read_models 9파일은 RF-030/035 4 wrapper만 소비한다고 보고. 지팀장 BASE→`a21401db` GitHub compare로 신규 9경로 및 wrapper 4경로 변경을 확인했으나 소비자 전수성은 미검증. **독립 실행 가능한 RF-013 단독 소유 소스 수정 지시를 철회**, 원 RF를 rework/claude→verification/claude 반환. GPT가 RF-030/035/074 owner·inventory 승인 경계를 결정할 때까지 BLOCKED/NOT_DONE; A는 RF-019 등 다음 작업으로 이동. 기존 (c) 전체 통합 BLOCKED는 지속. **RF-001 (B 1순위 REWORK)** 33 owner 안의 2,308행 core IO/side-effect·19개 divergent owner 경계를 해소하는 소스 delta 또는 완전 KEEP 실증. 기존 PASS_SCOPED는 전체 peer PASS 아님. RF-064는 신규 차단 해소 증거 없어 pending 유지.
- **다음 배정(1→2→3순위):** **A 반려 없음 / B RF-001→009→020 소유범위 반려 보완 먼저** → A RF-067 후속 신규 근거가 있을 때만 peer, B RF-018·014 신규 실패분류 peer → A RF-019 / B RF-068 신규 개발. 1순위는 각자 완료 가능한 여러 RF를 같은 회차에 순차 처리, 동일 증거 반복 금지. RF-021 안전 HOLD 유지. CI exact integration SHA GREEN 없으면 통합/DONE 금지.

## 파일별 TARGET_PATH 직접 계약 — 2026-10-25

- `RF-001~093` **93/93개 문서에 각자 파일별 SOURCE→TARGET 표 삽입**; 기준선 CSV 3,985행 + 신규 docs 121행 = **4,106행**. 실제 HEAD 4,089파일과 차이는 역사 이동·퇴역 17개를 포함하기 때문이며, 실제 파일을 추가/이동한 것이 아니다.
- 분류: `COMPAT_OWNER_REVIEW` 6; `KEEP_CANDIDATE` 3549; `KEEP_VERIFIED_EXISTING_DONE` 169; `MOVED_CURRENT_PATH` 12; `NEW_DOC_KEEP_CANDIDATE` 121; `OWNER_SPLIT_REVIEW` 164; `RESTRICTED_REVIEW_KEEP` 5; `RETIRED_HISTORICAL` 5; `SAFETY_HOLD_KEEP` 75.
- **정확한 정의:** KEEP_CANDIDATE는 현재 경로의 **보존 후보**이며 확인된 최종 목표 위치나 책임 분리 완료 판정이 아니다. A/B는 검토 때마다 실제 함수·소비자·호출 계약을 증명해 TARGET/ACTION/Owner 확정. 안전·교차 Owner 임의 MOVE 금지.
- 과거 DONE RF-002~006의 169개 파일은 기존 KEEP_VERIFIED 판정과 증거를 **소급 기록만** 했다. 기존 DONE/peer/CI 판정 변경·재실행 없음. RF-021 안전 HOLD 및 EX1~EX6 제한 유지.

## 지팀장 차단 해소 책임표 (D00 §6; 2026-10-25)

| RF | 결정 책임 / 수행·독립 검증 | 차단을 푸는 **다음 구체적 증거** | 재개 상태 |
|---|---|---|---|
| [013](verification/claude/RF-013.md) | **GPT 교차 Owner/인벤토리 결정 / A 기존 67경로 KEEP 증거 / B peer** | 신규 9경로 단일 writer 및 RF-030/035 wrapper·RF-074 frozen inventory 충돌 없는 승인/증거 | `VERIFICATION/BLOCKED_CROSS_RF_OWNER` |
| [014](verification/claude/RF-014.md) | **GPT** RF-009/019/030/035/074 경계 결정 / **A** 실패 2 node 원인 분리 / **B** peer | RF-014 20개와 output payload·Reporter consumer, BASE/후보 실패 대조 | `VERIFY_BLOCKED` |
| [018](verification/claude/RF-018.md) | **GPT** RF-026/import·역사 CI 원인 판정 / **A** 2 FAIL·57 ERROR 그룹 증명 / **B** peer | 실패 node와 BASE/후보 동일 명령, RF-026 경계 분리 | `PEER_BLOCKED` |
| [064](pending/RF-064.md) | **GPT** 외부 8경로 Owner·승인 범위 판정 / **B** source 2개·실패 대조 / **A** peer | 8경로 원소유+30 PASS/10 FAIL/57 ERROR 원인별 BASE 대조 | `PENDING/BLOCKED` |

- **고정 운영:** 매 지팀장 점검 때 CURRENT→새 HANDOFF/후보→위 RF의 **새 증거 여부**를 확인하고, 증거가 있으면 **그 회차에 GPT가 경로별 결정·다음 작업을 해당 RF에 기록**, 실행 대상만 CURRENT에 연결한다. 없으면 같은 SHA 재검증 없이 A/B가 다음 독립 RF를 진행한다. 역할·안전·테스트 오라클 권한은 D00 제약 불변.
- **분명한 상태:** 위 표는 해결·재배정·코드 변경이 완료됐다는 뜻이 아닌 **지팀장 실제 실행 지시의 고정 위치**다. 최종 DONE은 독립 검증과 exact integration SHA CI 뒤에만 판정한다.

## T00~T09 ↔ RF-93 목표 커버리지 대조 (2026-10-24)

아래 표는 **기존 RF 범위의 목표 참조 매핑**이며, 목표 위치로 파일 이동 완료 또는 최종 PASS를 뜻하지 않는다. 93건은 기준선 CSV 3,985개 파일에 한 RF씩 유일하게 매칭되고, 새 문서 경로는 RF-079 논리 Owner 델타로 분리한다.

| 목표 | 기준선 책임 RF | RF 수 | 실물 기반 핵심 보완·차단 |
|---|---|---:|---|
| [T02 apps](../architecture/T02_APPS_TARGET.md) | 001~007 | 7 | API services/domain/route는 003/004/005, Operator Brief는 001, 템플릿은 002(DONE), Web features 006(DONE), shell/E2E 007. **T02 잘못된 소유 표기 교정** |
| [T07 graphs](../architecture/T07_GRAPHS_TARGET.md) | 008~012 | 5 | Strategist 008, Scanner 009, Monitor 010, Commander 011, 실제 Executor·State·pipeline 안전 012. **실행 stub 혼동 교정** |
| [V3 libs](../architecture/TREE_V3_FROZEN.md) | 013~062 | 50 | 26 패키지 baseline 전수. 7-role public interface 중 2개(`agents/supervisor`, `agents/executor`) 부재: RF-060·048의 안전 설계 검토와 RF-017/044 계약 선행, 물리 생성 미승인 |
| [T08 scripts](../architecture/T08_SCRIPTS_TARGET.md) | 063~071 | 9 | 진단 063, refactor 064, research 065, examples/maintenance 066, checks 067, generators 068, capture/build 069, launch 070, 기타 root/restart/cleanup 071. **공개 CLI 경로 보존** |
| [T09 tests](../architecture/T09_TESTS_TARGET.md) | 072~078 | 7 | fixture 072, API/deploy 073, reporting/operator 074, agents 075, safety 076, legacy API 077, global/misc 078. `test_patch_notes_sync.py`는 RF-078 |
| [T06 docs](../architecture/T06_DOCS_TARGET.md) | 079~086 | 8 | D00=RF-086, refactor/T00~09 신규 docs=RF-079 논리 Owner, research docs=RF-082, 역사·CI 링크 보존 |
| [T05 deploy](../architecture/T05_DEPLOY_TARGET.md) | 087~089 | 3 | compose/docker 087, trading SAFETY_LOCK 088, m28/m31 OS templates 089 |
| [T03 config](../architecture/T03_CONFIG_TARGET.md) | 090 | 1 | 시험 설정 8개, safe env/Skill order capability 분리 |
| [T04 data](../architecture/T04_DATA_TARGET.md) | 091 | 1 | 25개 specs/eval/historic data, `.env` 의심 파일 내용 노출 금지 |
| [T01 CI](../architecture/T01_GITHUB_CI_TARGET.md) | 092 | 1 | 7→2 축소 이슈 기존 증거로 종결. **신규 SHA의 필수 CI는 별도 검증** |
| [T00 루트 파일](../architecture/T00_TARGET_TREE.md) | 093 | 1 | 공개 진입·test configs·역사 artifact 11개 |
| **합계** | **001~093** | **93** | **범위 소유권 100%; 목표별 실행·검증 완료율 별도 미판정** |

**정합성 체크:** 7+5+50+9+7+8+3+1+1+1+1=93. 보완된 주요 RF 개별 문서는 기존 `pending/`·`verification/`·`rework/` 안에서 상태/기존 증거를 보존하며 TARGET/CONSUMERS/ACCEPTANCE 조건을 추가했다. `done/RF-002~006`의 기존 지팀장 승인·SHA는 재작성하지 않았다.

**아직 최종 DONE 불가:** 목표 파일의 실제 OWNER/DESTINATION별 소비자 증거·합격 기준 12개·보호 경계 승인과 exact integration SHA regression/CI가 필요. 미완료 2개 public role의 신규 파일은 소유권 사전 승인 전 물리 생성 불가.

## T00 목표·현행 구조 정합성 (2026-10-24, 문서-only)
- [**T00 전체 목표 인덱스**](../architecture/T00_TARGET_TREE.md) → T01~T09는 `.github/apps/config/data/deploy/docs/graphs/scripts/tests` 루트별 **파일 이름·개선 구조·RF**를 제시한다. 26 libs package는 동결 V3와 RF-013~062를 따른다.
- **현행 Git `d082cee8`**: root singles 11, `.github` **2**, `apps` 240, `config` 8, `data` 25, `deploy` 33, `docs` **1,413**, `graphs` 45, `libs` 1,227, `scripts` 418, `tests` 658 = **4,080**.
- **이번 문서-only T01~09 추가(+9, 타 경로 변경은 내용만)**: `docs` **1,422**, 전체 **4,089** 예상. 실제 커밋/트리 결과가 다르면 즉시 이 줄을 다시 대조한다. directory 302 기존 유지.
- 구 CSV 3,985행은 3,985개 원래 경로에 **중복·누락 없이 한 RF**. `d082cee8`에서 신규 경로 112·소멸 경로 17(내역 [T06](../architecture/T06_DOCS_TARGET.md)); 새 경로 전체는 docs 문서 관리, 논리 owner RF-079. 현행 파일 분모 4,080 중 old-path 3,968 직접 매칭 = **97.25%**; 신규 경로가 소스 미소유를 뜻하는 것은 아니다.
- **CI 7→2 재점검 중단:** `.github/workflows/` 현행 2개, 축소 사실과 기존 successful exact-source Actions 근거는 [T01](../architecture/T01_GITHUB_CI_TARGET.md)에 고정. 삭제 5개를 다시 검증·복원 대상으로 언급하지 않는다. **향후 통합 코드 변경의 exact-SHA CI는 별도 필수 게이트**이며 문서-only HEAD CI NOT_RUN을 GREEN이라고 주장하지 않는다.
- 93개 RF 완료는 TARGET_PATH/단일 Owner/동등성·독립검증·통합 SHA 및 12개 최종 합격 기준 충족과 함께 판정한다. 임의 신규 RF 생성 금지.

## 기준선 RF 우선순위 분류 (완료 건 포함)
| 우선 | 목적 | 전체 RF 수 |
|---|---|---:|
| P1 | 크고 순수한 구조 개선 | 19 |
| P2 | 저위험 이동·호환 | 20 |
| P3 | 계약·IO 책임 | 32 |
| P4 | 전수 유지·역사 분류 | 14 |
| P5 | 거래 안전·최종 게이트 | 8 |

## 루트 폴더 전체 — 아래 파일 수는 **3,985 기준선** (현행 수량이 아님)
| 범위 | 기준선 파일 | 독립 작업 | 상태 |
|---|---:|---|---|
| `.github/` | 7 | [RF-092](pending/RF-092.md) | 미판정 |
| `apps/` | 240 | [RF-001](verification/codex/RF-001.md) · [RF-002](done/RF-002.md) · [RF-003](done/RF-003.md) · [RF-004](done/RF-004.md) · [RF-005](done/RF-005.md) · [RF-006](done/RF-006.md) · [RF-007](verification/codex/RF-007.md) | 미판정 |
| `config/` | 8 | [RF-090](pending/RF-090.md) | 미판정 |
| `data/` | 25 | [RF-091](pending/RF-091.md) | 미판정 |
| `deploy/` | 33 | [RF-087](pending/RF-087.md) · [RF-088](pending/RF-088.md) · [RF-089](pending/RF-089.md) | 미판정 |
| `docs/` | 1313 | [RF-079](pending/RF-079.md) · [RF-080](pending/RF-080.md) · [RF-081](pending/RF-081.md) · [RF-082](pending/RF-082.md) · [RF-083](pending/RF-083.md) · [RF-084](pending/RF-084.md) · [RF-085](pending/RF-085.md) · [RF-086](pending/RF-086.md) | 미판정 |
| `graphs/` | 45 | [RF-008](verification/codex/RF-008.md) · [RF-009](rework/codex/RF-009.md) · [RF-010](pending/RF-010.md) · [RF-011](pending/RF-011.md) · [RF-012](pending/RF-012.md) | 미판정 |
| `libs/` | 1227 | [RF-013](verification/claude/RF-013.md) · [RF-014](verification/claude/RF-014.md) · [RF-015](verification/claude/RF-015.md) · [RF-016](verification/claude/RF-016.md) · [RF-017](pending/RF-017.md) · [RF-018](verification/claude/RF-018.md) · [RF-019](pending/RF-019.md) · [RF-020](rework/codex/RF-020.md) · [RF-021](pending/RF-021.md) · [RF-022](pending/RF-022.md) · [RF-023](pending/RF-023.md) · [RF-024](pending/RF-024.md) · [RF-025](pending/RF-025.md) · [RF-026](pending/RF-026.md) · [RF-027](pending/RF-027.md) · [RF-028](pending/RF-028.md) · [RF-029](pending/RF-029.md) · [RF-030](pending/RF-030.md) · [RF-031](pending/RF-031.md) · [RF-032](pending/RF-032.md) · [RF-033](pending/RF-033.md) · [RF-034](pending/RF-034.md) · [RF-035](pending/RF-035.md) · [RF-036](pending/RF-036.md) · [RF-037](pending/RF-037.md) · [RF-038](pending/RF-038.md) · [RF-039](pending/RF-039.md) · [RF-040](pending/RF-040.md) · [RF-041](pending/RF-041.md) · [RF-042](pending/RF-042.md) · [RF-043](pending/RF-043.md) · [RF-044](pending/RF-044.md) · [RF-045](pending/RF-045.md) · [RF-046](pending/RF-046.md) · [RF-047](pending/RF-047.md) · [RF-048](pending/RF-048.md) · [RF-049](pending/RF-049.md) · [RF-050](pending/RF-050.md) · [RF-051](pending/RF-051.md) · [RF-052](pending/RF-052.md) · [RF-053](pending/RF-053.md) · [RF-054](pending/RF-054.md) · [RF-055](pending/RF-055.md) · [RF-056](pending/RF-056.md) · [RF-057](pending/RF-057.md) · [RF-058](pending/RF-058.md) · [RF-059](pending/RF-059.md) · [RF-060](pending/RF-060.md) · [RF-061](pending/RF-061.md) · [RF-062](pending/RF-062.md) | 미판정 |
| `scripts/` | 418 | [RF-063](verification/codex/RF-063.md) · [RF-064](pending/RF-064.md) · [RF-065](verification/codex/RF-065.md) · [RF-066](verification/codex/RF-066.md) · [RF-067](verification/codex/RF-067.md) · [RF-068](pending/RF-068.md) · [RF-069](pending/RF-069.md) · [RF-070](verification/codex/RF-070.md) · [RF-071](pending/RF-071.md) | 미판정 |
| `tests/` | 658 | [RF-072](pending/RF-072.md) · [RF-073](pending/RF-073.md) · [RF-074](pending/RF-074.md) · [RF-075](pending/RF-075.md) · [RF-076](pending/RF-076.md) · [RF-077](pending/RF-077.md) · [RF-078](pending/RF-078.md) | 미판정 |
| 루트 파일 | 11 | [RF-093](pending/RF-093.md) | 미판정 |

## libs/ 26개 패키지 — **기준선/현행 파일수 동일**, 최종 Owner 판정 별도
| 패키지 | 파일 | 독립 작업 | 상태 |
|---|---:|---|---|
| `libs/agent/` | 14 | [RF-040](pending/RF-040.md) | 미판정 |
| `libs/agents/` | 119 | [RF-013](verification/claude/RF-013.md) · [RF-014](verification/claude/RF-014.md) · [RF-015](verification/claude/RF-015.md) · [RF-016](verification/claude/RF-016.md) · [RF-017](pending/RF-017.md) | 미판정 |
| `libs/ai/` | 6 | [RF-041](pending/RF-041.md) | 미판정 |
| `libs/approval/` | 2 | [RF-042](pending/RF-042.md) | 미판정 |
| `libs/catalog/` | 6 | [RF-043](pending/RF-043.md) | 미판정 |
| `libs/contracts/` | 16 | [RF-044](pending/RF-044.md) | 미판정 |
| `libs/core/` | 10 | [RF-045](pending/RF-045.md) | 미판정 |
| `libs/data_quality/` | 2 | [RF-046](pending/RF-046.md) | 미판정 |
| `libs/diagnostics/` | 4 | [RF-047](pending/RF-047.md) | 미판정 |
| `libs/execution/` | 19 | [RF-048](pending/RF-048.md) | 미판정 |
| `libs/kiwoom/` | 5 | [RF-049](pending/RF-049.md) | 미판정 |
| `libs/llm/` | 8 | [RF-050](pending/RF-050.md) | 미판정 |
| `libs/market/` | 8 | [RF-051](pending/RF-051.md) | 미판정 |
| `libs/market_data/` | 2 | [RF-052](pending/RF-052.md) | 미판정 |
| `libs/news/` | 12 | [RF-053](pending/RF-053.md) | 미판정 |
| `libs/performance/` | 4 | [RF-054](pending/RF-054.md) | 미판정 |
| `libs/read/` | 17 | [RF-055](pending/RF-055.md) | 미판정 |
| `libs/reporting/` | 500 | [RF-028](pending/RF-028.md) · [RF-029](pending/RF-029.md) · [RF-030](pending/RF-030.md) · [RF-031](pending/RF-031.md) · [RF-032](pending/RF-032.md) · [RF-033](pending/RF-033.md) · [RF-034](pending/RF-034.md) · [RF-035](pending/RF-035.md) | 미판정 |
| `libs/research/` | 110 | [RF-036](pending/RF-036.md) · [RF-037](pending/RF-037.md) · [RF-038](pending/RF-038.md) · [RF-039](pending/RF-039.md) | 미판정 |
| `libs/risk/` | 3 | [RF-056](pending/RF-056.md) | 미판정 |
| `libs/runtime/` | 322 | [RF-018](verification/claude/RF-018.md) · [RF-019](pending/RF-019.md) · [RF-020](rework/codex/RF-020.md) · [RF-021](pending/RF-021.md) · [RF-022](pending/RF-022.md) · [RF-023](pending/RF-023.md) · [RF-024](pending/RF-024.md) · [RF-025](pending/RF-025.md) · [RF-026](pending/RF-026.md) · [RF-027](pending/RF-027.md) | 미판정 |
| `libs/skills/` | 6 | [RF-057](pending/RF-057.md) | 미판정 |
| `libs/storage/` | 3 | [RF-058](pending/RF-058.md) | 미판정 |
| `libs/strategies/` | 21 | [RF-059](pending/RF-059.md) | 미판정 |
| `libs/supervisor/` | 4 | [RF-060](pending/RF-060.md) | 미판정 |
| `libs/tools/` | 3 | [RF-061](pending/RF-061.md) | 미판정 |

**RF 상태(최신 큐 판정):** pending **71건** / verification **14건** / rework **0건** / done **8건** = **총 93건**. RF-001은 `verification/codex` 단일 경로이며 `PASS_SCOPED / BLOCKED / NOT_DONE`. 완료 판단은 D03 §3을 따른다. 과거 회차 수치와 지시는 역사 기록으로만 보존한다.

**현재 배정:** [CURRENT](../work_orders/CURRENT.md)가 유일한 최신 작업 큐. 이 STATUS의 과거 회차 배정은 실행 지시로 사용하지 않는다.

**전수 소유권:** [3985파일↔RF CSV](FILE_COVERAGE_63182ab2.csv) · [P1.5.0~11 합격 기준](criteria/). 회차별 실행 이력은 Git 이력·RF·HANDOFF에서 확인한다.
