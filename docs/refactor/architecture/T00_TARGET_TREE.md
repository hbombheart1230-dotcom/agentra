# T00 — Agentra P1.5 ROOT→LEAF 전체 목표 폴더트리 (인덱스)

> **정본:** D00 작업·안전 규칙, [HYBRID-7 V3 FROZEN](TREE_V3_FROZEN.md) 역할·안전 동결 아래의 **전체 저장소 목표 디렉터리·Owner 경계 인덱스**.
> **범위:** 루트 10개 디렉터리 + 루트 파일 11개. `libs/` 26개 패키지를 포함하되 **libs에 국한하지 않음**.
> **작성 기준:** `integration/p1.5@d082cee8` 실제 4,080 tracked files/302 directories, RF 기준선 `63182ab2` 3,985 files/298 dirs. T01~09의 9개 신규 문서가 합쳐진 직후는 4,089 files/302 dirs로 예상하며 최종 Git HEAD에서 검산한다.
> **권한:** 이 문서는 목표·소유권을 명료화한 **DESIGN/NO_RUNTIME_CHANGE**. SOURCE_PATH→TARGET_PATH 물리 이동은 별도 RF 소비자/안전/독립 검증 및 지팀장 승인 필요.

## 1. 9개 비-libs 루트 — 최종 세부 목표 바로가기

| T 문서 | 대상(실존 폴더) | 핵심 목표 | 실제 기준선 RF |
|---|---|---|---|
| [T01 — CI](T01_GITHUB_CI_TARGET.md) | `.github/` | 확인된 2-workflow 계약, 기존 7→2 축소 **재감사 금지** | RF-092 |
| [T02 — Apps](T02_APPS_TARGET.md) | `apps/` | API/Operator UI/React 책임·파일별 Owner, UI Byte parity | RF-001~007 |
| [T03 — Config](T03_CONFIG_TARGET.md) | `config/` | 환경·스킬 config 단일 경계, 실제 기본값 보호 | RF-090 |
| [T04 — Data](T04_DATA_TARGET.md) | `data/` | 버전 고정 데이터·민감/운영 state 경계 | RF-091 |
| [T05 — Deploy](T05_DEPLOY_TARGET.md) | `deploy/` | Compose/Docker/OS 스케줄러·진입점 안전 | RF-087~089 |
| [T06 — Docs](T06_DOCS_TARGET.md) | `docs/` | D00/T00/STATUS/CURRENT 단일 정본과 역사 증거 보존, 파일 수 정합 | RF-079~086 |
| [T07 — Graphs](T07_GRAPHS_TARGET.md) | `graphs/` | 실제 Commander/Executor와 M17 stub 분리, 노드 adapter | RF-008~012 |
| [T08 — Scripts](T08_SCRIPTS_TARGET.md) | `scripts/` | 기존 공개 CLI 유지, 순수 내부 구현 분리, 418파일 전수 RF | RF-063~071 |
| [T09 — Tests](T09_TESTS_TARGET.md) | `tests/` | 회귀/fixture·test conservation, 658파일 전수 RF | RF-072~078 |

9개 상세 문서에 **현재 폴더 구조/파일명/책임별 개선 목표/목표 경로 처리/안전 HOLD/검증 조건**을 기록한다. 대형 범위의 전체 SOURCE_PATH·RF 증거는 각 문서의 펼침 인벤토리 또는 기존 파일 소유권 CSV로 연결한다. T00에 트리를 반복 붙이지 않는다.

## 2. 10번째 루트 libs/ — 기존 V3 고정 및 26 package 책임

```text
libs/
├── agents/{commander,strategist,scanner,monitor,reporter,supervisor,executor}/  # 최종 7개 PUBLIC roles
├── agent/                                     # legacy compatibility
├── ai/ approval/ catalog/ contracts/ core/ data_quality/
├── diagnostics/ execution/ kiwoom/ llm/ market/ market_data/
├── news/ performance/ read/ reporting/ research/ risk/
├── runtime/ skills/ storage/ strategies/ supervisor/ tools/
└── __init__.py                                # 총 26 first-level packages + file
```

- **미완성 2개 공개 역할의 책임 경계:** `libs/agents/supervisor/`는 RF-060(보호된 Supervisor 소스의 순수 공개 계약 검토), `libs/agents/executor/`는 RF-048(보호된 Executor 소스의 순수 공개 계약 검토)의 **설계 검토 책임**으로 연결한다. 실제 새 파일을 RF-060/048에서 임의 쓰기하는 권한이 아니라, RF-017(공용 agents export), RF-044(공유 DTO), 그래프 소비자와 경로 소유권을 GPT가 사전 합의한 후 사용자 안전 승인을 별도 받아야 한다.
- 현재 26개 패키지는 모두 존재. `libs/agents/supervisor/`, `libs/agents/executor/`의 **독립 공개 역할 인터페이스**는 목표이며 실제 실행·안전 엔진을 이관하거나 빈 decorative packages를 만들라는 지시가 아니다.
- 상세 소유권·기존 실제 하위 구조: [TREE_V3_FROZEN](TREE_V3_FROZEN.md) · [ALL_LIBS_OWNERS](P15_ALL_LIBS_OWNERS_20261018.md) (과거 snapshot) · [ROOT→LEAF reality](P15_ROOT_TO_LEAF_REALITY_AND_CLEANUP_20261018.md) (과거 snapshot). **기존 최신 RF-013~062**가 각 `libs/` 경계를 담당하며 새로운 미승인 task가 아니다.
- `libs/{approval,execution,kiwoom,risk,supervisor}/`, 실운영 `graphs/nodes/execute_from_packet.py`, UEF publisher, Step5C/UNKNOWN 등은 SAFETY_LOCK. 메인/실거래/CI oracle 무승인 변경 금지.

## 3. 루트 파일 11개 — RF-093

`.dockerignore`, `.gitignore`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `_health.json`, `b.jsonl`, `conftest.py`, `pytest.ini`, `requirements.txt`, `sitecustomize.py`.

프로젝트 실행/테스트/업무 규칙은 유지하되 `_health.json`·`b.jsonl` 등 provenance 미확정 후보는 직접 소비자·안전·민감 정보 확인 전 삭제하지 않는다.

## 4. 완료 기준과 수량 오류의 정본

- **작업 순서:** [CURRENT](../work_orders/CURRENT.md) → [D00](../../ENGINEERING_DELIVERY_POLICY.md) → T00 → 해당 Txx·RF → [STATUS](../plan/STATUS.md). 불변 문서 반복 전문 열람 금지.
- **전체 baseline CSV 3,985/3,985**, 중복 RF 없음. `d082cee8` 현재 4,080중 과거 경로 일치 3,968, 새로운 docs 경로 112개, 사라진 경로 17개. 이유와 RF-079 문서-owner 델타는 [T06](T06_DOCS_TARGET.md)에 고정.
- **목표 트리 != 현재 트리:** 디렉터리 인덱스와 목표 경계가 일치해도 파일별 최종 `TARGET_PATH` + `OWNER` + `CONSUMERS` + `EVIDENCE`가 승인된 것이 아니다.
- **P1.5 DONE 조건:** 루트 10개+루트 파일 및 26 libs package 모든 FILE Owner/keep·move·wrapper 판정 → 93 RF 독립 evidence DONE → 12개 P1.5.0~11 기준·exact integration SHA normal/-O/필수 CI·UEF/Docker/replay/보안 → 지팀장/사용자 Freeze 승인. 문서 추가나 폴더 개수 충족만으로 DONE 불가.
