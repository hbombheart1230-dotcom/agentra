# RF-072 — 코드 구조/함수 재배치 설계 (T09)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-072.md` blob `2378040e9b3eff8bf0dffa56a0fcdb197347a238`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 33개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `tests/fixtures/p1_5_p058_repeat_guard/cases.json` → `tests/fixtures/p1_5_p058_repeat_guard/cases.json` | 224767 | `d39186b00977` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_strategist_s1_057/cases.json` → `tests/fixtures/p1_5_strategist_s1_057/cases.json` | 130843 | `3fdeab76d230` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t35_agent_outputs/golden_inputs_outputs.json.gz` → `tests/fixtures/p1_5_t35_agent_outputs/golden_inputs_outputs.json.gz` | 1692348 | `aa8457e0813f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t35_agent_outputs/golden_variant_digests.json.gz` → `tests/fixtures/p1_5_t35_agent_outputs/golden_variant_digests.json.gz` | 269312 | `8bdf04b36ffe` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t35_agent_outputs/manifest.json` → `tests/fixtures/p1_5_t35_agent_outputs/manifest.json` | 59851 | `0b1999512f80` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t35_agent_outputs/public_surface.json` → `tests/fixtures/p1_5_t35_agent_outputs/public_surface.json` | 1664 | `2155de0ed4f3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4a_scanner_node/FREEZE_COMMIT.txt` → `tests/fixtures/p1_5_t4a_scanner_node/FREEZE_COMMIT.txt` | 41 | `7e7a4483e283` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4a_scanner_node/manifest.json` → `tests/fixtures/p1_5_t4a_scanner_node/manifest.json` | 1213 | `0fe7f71e6e37` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4a_scanner_node/scanner_node_golden.json.gz` → `tests/fixtures/p1_5_t4a_scanner_node/scanner_node_golden.json.gz` | 1136427 | `226560b5ef6c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4b_monitor/FREEZE_COMMIT.txt` → `tests/fixtures/p1_5_t4b_monitor/FREEZE_COMMIT.txt` | 41 | `19d499e10ea4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4b_monitor/manifest.json` → `tests/fixtures/p1_5_t4b_monitor/manifest.json` | 181 | `c564630d1b59` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4b_monitor/monitor_golden.json.gz` → `tests/fixtures/p1_5_t4b_monitor/monitor_golden.json.gz` | 3148427 | `7ff642ddc848` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4c_strategist/FREEZE_COMMIT.txt` → `tests/fixtures/p1_5_t4c_strategist/FREEZE_COMMIT.txt` | 41 | `26bae96dc488` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4c_strategist/manifest.json` → `tests/fixtures/p1_5_t4c_strategist/manifest.json` | 137 | `1dcef7695694` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4c_strategist/strategist_golden.json.gz` → `tests/fixtures/p1_5_t4c_strategist/strategist_golden.json.gz` | 1688749 | `9bbbc2c6f30f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4d_commander_ui/FREEZE_COMMIT.txt` → `tests/fixtures/p1_5_t4d_commander_ui/FREEZE_COMMIT.txt` | 41 | `1549b8fadf69` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4d_commander_ui/commander_ui_golden.json.gz` → `tests/fixtures/p1_5_t4d_commander_ui/commander_ui_golden.json.gz` | 2899692 | `9a4e917b0ae3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_t4d_commander_ui/manifest.json` → `tests/fixtures/p1_5_t4d_commander_ui/manifest.json` | 264 | `ec4ab7ed8ae9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_v1052_candidate_risk/cases.json` → `tests/fixtures/p1_5_v1052_candidate_risk/cases.json` | 44260 | `465f210b7d48` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_v2053_scanner_context/cases.json` → `tests/fixtures/p1_5_v2053_scanner_context/cases.json` | 60936 | `c532d0a29b6a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_v3055_scanner_projections/cases.json` → `tests/fixtures/p1_5_v3055_scanner_projections/cases.json` | 6512156 | `9fb9d8d7c2bb` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/p1_5_v4056_scanner_policy/cases.json` → `tests/fixtures/p1_5_v4056_scanner_policy/cases.json` | 191074 | `59e584e6de05` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/uef9_synthetic/.gitattributes` → `tests/fixtures/uef9_synthetic/.gitattributes` | 32 | `9c18c9ccd2a6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/uef9_synthetic/reports_inputs.json` → `tests/fixtures/uef9_synthetic/reports_inputs.json` | 2290 | `6eca7a1e95ea` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_monitor/contracts.json` → `tests/fixtures/work_monitor/contracts.json` | 150031 | `17df032c56a9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_monitor/m001.json` → `tests/fixtures/work_monitor/m001.json` | 26164 | `442d1101fcb0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_monitor/m002.json` → `tests/fixtures/work_monitor/m002.json` | 18283 | `b861b6cd806a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_monitor/m003.json` → `tests/fixtures/work_monitor/m003.json` | 3839 | `47ca612536d3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_monitor/m004.json` → `tests/fixtures/work_monitor/m004.json` | 23034 | `a9851ba46015` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_monitor/m005.json` → `tests/fixtures/work_monitor/m005.json` | 39747 | `2c4a651e9cb2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_monitor/m008.json` → `tests/fixtures/work_monitor/m008.json` | 33345 | `d14612752d61` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_reporter/seed_cases.json.gz` → `tests/fixtures/work_reporter/seed_cases.json.gz` | 56805 | `a232726dc7be` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/fixtures/work_reporter/seed_cases.provenance.json` → `tests/fixtures/work_reporter/seed_cases.provenance.json` | 671 | `a7670c232cb3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
