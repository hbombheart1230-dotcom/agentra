# Agentra P1.5 — RF-001~RF-093 구현 세부 설계 인덱스

## 2026-10-30 상세설계 검토·A/B 인라인 명령 기준 (기존 표보다 우선)

- **93/93개 RF 상세 파일 존재 및 파일별 SOURCE/TARGET 경로 등록 완료.** Frozen T00~T09 및 TREE_V3_FROZEN은 수정하지 않았다. 단일 기준 FILE_COVERAGE CSV의 원본 4,106 path-owner 행을 사용하며, 소스 Python 2,458개 모두 함수 본문을 완독·독립 검증했다는 뜻은 아니다.
- **구체 코드 설계:** RF-001, RF-008/018, RF-031, RF-041, RF-044 및 RF-055/057/059/061/063/065/070/071에는 실제 함수명·일부 정확한 줄·TARGET Python 모듈·효과 KEEP·테스트 fixture를 명시했다. RF-002~054 다른 항목에는 확인한 대표 원본의 함수 정의/KEEP 후보를 기술했지만 전체 RF Python 함수 전수분석은 아니므로 구현 전 C03이 누락 함수/기존 Owner·소비자 충돌을 판정한다.
- **비코드 RF:** RF-072~078은 T09 fixture/test discovery 보존, RF-079~086은 T06 canonical/history link 보존, RF-087~089는 T05 deploy/OS schedule entry 보존, RF-090 config, RF-091 data, RF-092 GitHub CI, RF-093 root contracts를 각각 특정 사유의 정당 KEEP 우선으로 설계. 이들에는 신규 Python 함수명이 존재하지 않는 것이 올바르다.
- **A/B 절대 단일 진입점:** A는 `docs/refactor/work_orders/C02_CLAUDE_CURRENT.md` 한 파일, B는 `C01_CODEX_CURRENT.md` 한 파일만 먼저 읽는다. **이 인덱스 및 개별 RF 상세파일을 A/B에 읽으라고 지시하지 않는다.** C03이 실제 함수/목표/테스트를 결정해 C01/C02 본문에 인라인 배정·푸시한다. 현재 각각 여섯 개의 독립 실구현 Item이 있으며 완료한 동일 blob은 재개하지 않는다.
- **성과 구분:** `KEEP_OK`는 적절한 위치·단일 책임·호환 계약을 확인해 한 줄 사유+Git blob으로 종결한다. 함수 몸체가 실제 SOURCE에서 삭제되어 TARGET 단일 Owner에 구현·테스트·푸시되었을 때만 `REFACTOR_CHANGED`. 본 설계 commit은 **코드 변경 실적 0건**. 과거 05_DONE과 CI/test 이력은 유지하고 신규 Txx TARGET_GAP은 기존 RF 작업으로 해결.
- **명세 품질 구분:** `SOURCE_VERIFIED_EXACT` = 실제 소스 본문·함수 확인; `PATH_OWNER_VERIFIED` = 경로·blob·소유권만 확인(함수 목록 추측 금지); `KEEP_IF` = 구조 조건부 후보, 실제 KEEP 수용 아님. 완료 판정에는 조건부 KEEP를 확정 PASS로 자동 계상하지 않는다.


기준 `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062` · 실제 FILE_COVERAGE 4106 경로 · 93개 RF 독점 Actor 배치. T00~T09/V3 원형 유지.

**완료 의미:** 설계 파일이 작성됐다는 의미이며 소스 리팩터링 코드가 전부 DONE된 것은 아니다. 대표 대형 모듈은 함수명을 확정했고, 나머지는 정확한 파일/blob/크기와 우선 분석 원본을 지정했으며 함수 실사 미완료를 표시한다. 미실사 상태를 분석 완료로 간주하지 않는다.

| RF | 담당 | 목표 | 파일수 | 세부 설계 |
|---|---|---|---:|---|
| RF-001 | Codex B | T02 | 33 | [상세](./RF-001_IMPLEMENTATION.md) |
| RF-002 | Codex B | T02 | 9 | [상세](./RF-002_IMPLEMENTATION.md) |
| RF-003 | Codex B | T02 | 25 | [상세](./RF-003_IMPLEMENTATION.md) |
| RF-004 | Codex B | T02 | 35 | [상세](./RF-004_IMPLEMENTATION.md) |
| RF-005 | Codex B | T02 | 40 | [상세](./RF-005_IMPLEMENTATION.md) |
| RF-006 | Codex B | T02 | 60 | [상세](./RF-006_IMPLEMENTATION.md) |
| RF-007 | Codex B | T02 | 38 | [상세](./RF-007_IMPLEMENTATION.md) |
| RF-008 | Codex B | T07 | 1 | [상세](./RF-008_IMPLEMENTATION.md) |
| RF-009 | Codex B | T07 | 3 | [상세](./RF-009_IMPLEMENTATION.md) |
| RF-010 | Codex B | T07 | 1 | [상세](./RF-010_IMPLEMENTATION.md) |
| RF-011 | Codex B | T07 | 3 | [상세](./RF-011_IMPLEMENTATION.md) |
| RF-012 | Codex B | T07 | 37 | [상세](./RF-012_IMPLEMENTATION.md) |
| RF-013 | Claude A | T00/V3 | 67 | [상세](./RF-013_IMPLEMENTATION.md) |
| RF-014 | Claude A | T00/V3 | 20 | [상세](./RF-014_IMPLEMENTATION.md) |
| RF-015 | Claude A | T00/V3 | 19 | [상세](./RF-015_IMPLEMENTATION.md) |
| RF-016 | Claude A | T00/V3 | 8 | [상세](./RF-016_IMPLEMENTATION.md) |
| RF-017 | Claude A | T00/V3 | 5 | [상세](./RF-017_IMPLEMENTATION.md) |
| RF-018 | Codex B | T00/V3 | 47 | [상세](./RF-018_IMPLEMENTATION.md) |
| RF-019 | Claude A | T00/V3 | 29 | [상세](./RF-019_IMPLEMENTATION.md) |
| RF-020 | Codex B | T00/V3 | 30 | [상세](./RF-020_IMPLEMENTATION.md) |
| RF-021 | Claude A | T00/V3 | 32 | [상세](./RF-021_IMPLEMENTATION.md) |
| RF-022 | Codex B | T00/V3 | 40 | [상세](./RF-022_IMPLEMENTATION.md) |
| RF-023 | Codex B | T00/V3 | 21 | [상세](./RF-023_IMPLEMENTATION.md) |
| RF-024 | Codex B | T00/V3 | 18 | [상세](./RF-024_IMPLEMENTATION.md) |
| RF-025 | Codex B | T00/V3 | 13 | [상세](./RF-025_IMPLEMENTATION.md) |
| RF-026 | Codex B | T00/V3 | 15 | [상세](./RF-026_IMPLEMENTATION.md) |
| RF-027 | Codex B | T00/V3 | 77 | [상세](./RF-027_IMPLEMENTATION.md) |
| RF-028 | Claude A | T00/V3 | 85 | [상세](./RF-028_IMPLEMENTATION.md) |
| RF-029 | Claude A | T00/V3 | 38 | [상세](./RF-029_IMPLEMENTATION.md) |
| RF-030 | Claude A | T00/V3 | 16 | [상세](./RF-030_IMPLEMENTATION.md) |
| RF-031 | Claude A | T00/V3 | 38 | [상세](./RF-031_IMPLEMENTATION.md) |
| RF-032 | Claude A | T00/V3 | 135 | [상세](./RF-032_IMPLEMENTATION.md) |
| RF-033 | Claude A | T00/V3 | 76 | [상세](./RF-033_IMPLEMENTATION.md) |
| RF-034 | Claude A | T00/V3 | 59 | [상세](./RF-034_IMPLEMENTATION.md) |
| RF-035 | Claude A | T00/V3 | 119 | [상세](./RF-035_IMPLEMENTATION.md) |
| RF-036 | Codex B | T00/V3 | 34 | [상세](./RF-036_IMPLEMENTATION.md) |
| RF-037 | Claude A | T00/V3 | 21 | [상세](./RF-037_IMPLEMENTATION.md) |
| RF-038 | Codex B | T00/V3 | 39 | [상세](./RF-038_IMPLEMENTATION.md) |
| RF-039 | Claude A | T00/V3 | 16 | [상세](./RF-039_IMPLEMENTATION.md) |
| RF-040 | Claude A | T00/V3 | 19 | [상세](./RF-040_IMPLEMENTATION.md) |
| RF-041 | Claude A | T00/V3 | 7 | [상세](./RF-041_IMPLEMENTATION.md) |
| RF-042 | Codex B | T00/V3 | 2 | [상세](./RF-042_IMPLEMENTATION.md) |
| RF-043 | Claude A | T00/V3 | 6 | [상세](./RF-043_IMPLEMENTATION.md) |
| RF-044 | Codex B | T00/V3 | 27 | [상세](./RF-044_IMPLEMENTATION.md) |
| RF-045 | Codex B | T00/V3 | 24 | [상세](./RF-045_IMPLEMENTATION.md) |
| RF-046 | Claude A | T00/V3 | 2 | [상세](./RF-046_IMPLEMENTATION.md) |
| RF-047 | Claude A | T00/V3 | 4 | [상세](./RF-047_IMPLEMENTATION.md) |
| RF-048 | Codex B | T00/V3 | 19 | [상세](./RF-048_IMPLEMENTATION.md) |
| RF-049 | Claude A | T00/V3 | 5 | [상세](./RF-049_IMPLEMENTATION.md) |
| RF-050 | Claude A | T00/V3 | 11 | [상세](./RF-050_IMPLEMENTATION.md) |
| RF-051 | Claude A | T00/V3 | 15 | [상세](./RF-051_IMPLEMENTATION.md) |
| RF-052 | Claude A | T00/V3 | 2 | [상세](./RF-052_IMPLEMENTATION.md) |
| RF-053 | Claude A | T00/V3 | 12 | [상세](./RF-053_IMPLEMENTATION.md) |
| RF-054 | Claude A | T00/V3 | 5 | [상세](./RF-054_IMPLEMENTATION.md) |
| RF-055 | Claude A | T00/V3 | 17 | [상세](./RF-055_IMPLEMENTATION.md) |
| RF-056 | Codex B | T00/V3 | 3 | [상세](./RF-056_IMPLEMENTATION.md) |
| RF-057 | Claude A | T00/V3 | 6 | [상세](./RF-057_IMPLEMENTATION.md) |
| RF-058 | Claude A | T00/V3 | 3 | [상세](./RF-058_IMPLEMENTATION.md) |
| RF-059 | Claude A | T00/V3 | 21 | [상세](./RF-059_IMPLEMENTATION.md) |
| RF-060 | Codex B | T00/V3 | 4 | [상세](./RF-060_IMPLEMENTATION.md) |
| RF-061 | Claude A | T00/V3 | 3 | [상세](./RF-061_IMPLEMENTATION.md) |
| RF-062 | Codex B | T00/V3 | 1 | [상세](./RF-062_IMPLEMENTATION.md) |
| RF-063 | Codex B | T08 | 76 | [상세](./RF-063_IMPLEMENTATION.md) |
| RF-064 | Codex B | T08 | 58 | [상세](./RF-064_IMPLEMENTATION.md) |
| RF-065 | Codex B | T08 | 54 | [상세](./RF-065_IMPLEMENTATION.md) |
| RF-066 | Codex B | T08 | 30 | [상세](./RF-066_IMPLEMENTATION.md) |
| RF-067 | Codex B | T08 | 14 | [상세](./RF-067_IMPLEMENTATION.md) |
| RF-068 | Codex B | T08 | 8 | [상세](./RF-068_IMPLEMENTATION.md) |
| RF-069 | Codex B | T08 | 7 | [상세](./RF-069_IMPLEMENTATION.md) |
| RF-070 | Codex B | T08 | 142 | [상세](./RF-070_IMPLEMENTATION.md) |
| RF-071 | Codex B | T08 | 42 | [상세](./RF-071_IMPLEMENTATION.md) |
| RF-072 | Codex B | T09 | 33 | [상세](./RF-072_IMPLEMENTATION.md) |
| RF-073 | Claude A | T09 | 21 | [상세](./RF-073_IMPLEMENTATION.md) |
| RF-074 | Codex B | T09 | 75 | [상세](./RF-074_IMPLEMENTATION.md) |
| RF-075 | Claude A | T09 | 88 | [상세](./RF-075_IMPLEMENTATION.md) |
| RF-076 | Codex B | T09 | 59 | [상세](./RF-076_IMPLEMENTATION.md) |
| RF-077 | Claude A | T09 | 7 | [상세](./RF-077_IMPLEMENTATION.md) |
| RF-078 | Codex B | T09 | 375 | [상세](./RF-078_IMPLEMENTATION.md) |
| RF-079 | Claude A | T06 | 386 | [상세](./RF-079_IMPLEMENTATION.md) |
| RF-080 | Codex B | T06 | 313 | [상세](./RF-080_IMPLEMENTATION.md) |
| RF-081 | Claude A | T06 | 198 | [상세](./RF-081_IMPLEMENTATION.md) |
| RF-082 | Codex B | T06 | 115 | [상세](./RF-082_IMPLEMENTATION.md) |
| RF-083 | Claude A | T06 | 60 | [상세](./RF-083_IMPLEMENTATION.md) |
| RF-084 | Codex B | T06 | 41 | [상세](./RF-084_IMPLEMENTATION.md) |
| RF-085 | Claude A | T06 | 104 | [상세](./RF-085_IMPLEMENTATION.md) |
| RF-086 | Codex B | T06 | 96 | [상세](./RF-086_IMPLEMENTATION.md) |
| RF-087 | Claude A | T05 | 10 | [상세](./RF-087_IMPLEMENTATION.md) |
| RF-088 | Codex B | T05 | 9 | [상세](./RF-088_IMPLEMENTATION.md) |
| RF-089 | Claude A | T05 | 14 | [상세](./RF-089_IMPLEMENTATION.md) |
| RF-090 | Codex B | T03 | 8 | [상세](./RF-090_IMPLEMENTATION.md) |
| RF-091 | Claude A | T04 | 25 | [상세](./RF-091_IMPLEMENTATION.md) |
| RF-092 | Codex B | T01 | 7 | [상세](./RF-092_IMPLEMENTATION.md) |
| RF-093 | Claude A | T00 | 11 | [상세](./RF-093_IMPLEMENTATION.md) |

**중복 금지:** 원본 path는 CSV에서 단일 RF가 소유. 변경 목적지 경로가 다른 RF 영역이면 소유 actor가 같은지 확인하고 C03이 target 소유권을 먼저 고정. 다른 개발자의 동시 쓰기 금지.
