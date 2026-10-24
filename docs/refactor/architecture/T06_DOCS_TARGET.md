# T06 — docs/ 목표 문서 체계·정본 분리·파일 경로 정합성
> RF-079~086. 가장 큰 역사/증거 범위. docs 파일 **작성 직전 1,413개** (integration @ d082cee8). 본 T01~T09 신규 9문서 작성 뒤는 **1,422개 예상**, Git HEAD에서 확인해야 확정이다.

## 목표 정보 아키텍처
```text
docs/
├── ENGINEERING_DELIVERY_POLICY.md           # D00 안전·작업 정본
├── refactor/
│   ├── README.md                             # 정본 탐색 시작
│   ├── work_orders/
│   │   ├── CURRENT.md                        # 현재 RF·양쪽 배정 포인터
│   │   ├── archive/                          # 오래된 작업지시 비활성
│   │   └── evidence/                         # 감사 수신 기록
│   ├── architecture/
│   │   ├── TREE_V3_FROZEN.md                 # HYBRID-7 고정 역할·안전
│   │   ├── T00_TARGET_TREE.md                # 10루트 목차/전체 원칙
│   │   ├── T01_GITHUB_CI_TARGET.md
│   │   ├── T02_APPS_TARGET.md
│   │   ├── T03_CONFIG_TARGET.md
│   │   ├── T04_DATA_TARGET.md
│   │   ├── T05_DEPLOY_TARGET.md
│   │   ├── T06_DOCS_TARGET.md
│   │   ├── T07_GRAPHS_TARGET.md
│   │   ├── T08_SCRIPTS_TARGET.md
│   │   └── T09_TESTS_TARGET.md
│   ├── plan/
│   │   ├── STATUS.md                         # 배정·검증·DONE 유일 현황
│   │   ├── FILE_COVERAGE_63182ab2.csv        # PINNED historical baseline
│   │   ├── criteria/P1.5.0~11.md             # 12 acceptance criteria
│   │   ├── pending/RF-xxx.md
│   │   ├── verification/{claude,codex}/
│   │   ├── done/RF-xxx.md
│   │   └── troubleshooting/{open,closed}/
│   └── evidence/                             # immutable pinned historical proof
├── daily_patch/                              # release/incident log archive
├── trading_agent_patch_notes_detailed_update/# UI patchnotes provenance/history
├── architecture/, plan/, dev-team/, development/, ... # 기존 도메인·역사 자료: 확인 후 분류
└── 기타 기존 루트 문서                      # TO_BE_CLASSIFIED/KEEP_WITH_INDEX
```

## 기존 문서의 진짜 목표 처리
| 경로·파일 | 최종 책임 / 처리 | RF |
|---|---|---|
| `docs/ENGINEERING_DELIVERY_POLICY.md` | D00 업무·안전 정본(중복 이슈 회차 보고 금지) | RF-086 / 규칙은 D00 우선 |
| `docs/refactor/work_orders/CURRENT.md` | 1~2KB 작업 배정 링크만; 회차 테스트 로그 금지 | RF-079 |
| `docs/refactor/architecture/TREE_V3_FROZEN.md` | 7개 역할·안전 위상 불변 | RF-079 |
| `docs/refactor/architecture/T00_TARGET_TREE.md`, T01~T09 | **구조 목차 vs 각 루트 상세 파일 목표**만; 작업상태/검증로그 중복 금지 | RF-079 신규 경로 |
| `docs/refactor/plan/STATUS.md` | 유일 전수 RF 진행판, baseline vs current 분리 | RF-079 신규 경로 |
| `docs/refactor/plan/FILE_COVERAGE_63182ab2.csv` | 3,985 historical baseline 보존, **변경된 현재 목록으로 덮어쓰지 않음** | RF-079 신규 경로 |
| `docs/refactor/plan/criteria/P1.5.0.md` … `P1.5.11.md` | 12개 최종 승인 계약, 이미 옮긴 `pending/P1.5.*` 경로 재생성 금지 | RF-079 |
| `docs/refactor/plan/{pending,verification,done}/RF-xxx.md` | 각각 **한 상태 폴더에 단 한 번만** 위치, 93건; 임의 DONE 이동 금지 | RF-079 관리 문서, 각 RF 자기 증거 |
| `docs/refactor/plan/troubleshooting/{open,closed}/` | 미해결/해결 증거, 실패를 PASS로 덮지 않음 | RF-079 |
| `docs/daily_patch/`, `docs/trading_agent_patch_notes_detailed_update/` | 역사/화면 연결 이력 원형 보존, 의미 있는 코드 변경에 JSON/MD 동기 | RF-080 |
| `docs/{plan,roadmap}/` | 전략·과거 계획으로 분리, CURRENT 권한과 충돌하는 지시 무효 표시 | RF-081 |
| `docs/{architecture,dev-team,development,dev}/` | 역사 설계/팀 작업 로그. T00을 대체하는 병행 정본 금지 | RF-079(architecture)/RF-084(alignment)/RF-086(기타 dev-team·development) |
| `docs/{operations,runtime,execution_plan,commander_control,kiwoom_truth,observability,web_observability}/` | 해당 운영/도메인 운영 계약 유지, 링크 유효성 확인 | RF-085 |
| `docs/{research,evaluation,offline_alpha,quant_trade_diagnosis}/` | 연구·평가 출처/증거 보존, UEF actual publisher를 docs로 재배치 금지 | RF-082 / 세부 CSV |

**RF-079과 RF-086 분리:** D00은 기준선 CSV에서 RF-086, `docs/refactor/architecture/T00~T09` 및 refactor RF·STATUS 관리경로는 논리상 RF-079 델타이다. `docs/research/`는 RF-082이며, RF-079로 소유권을 덮어쓰지 않는다.

## 수량·경로 오류의 정밀 해소 (PINNED baseline → d082cee8)
- 기준선 `63182ab2`: 3,985파일 / 298디렉터리. 기준선 CSV **3,985/3,985 하나의 RF만** 지정, 중복 0·누락 0.
- 실제 T00 작성 후 `d082cee8`: **4,080파일 / 302디렉터리**. 기준선 대비 추가된 경로 **112**, 사라진 경로 **17**, 순증 95.
- 112개 신규 경로 구성: **RF 문서 93개**, 기존 pending에서 이동한 **합격 기준 12개**, `STATUS.md` 1개, `FILE_COVERAGE_63182ab2.csv` 1개, troubleshooting 신규 2개, verification `.gitkeep` 2개, T00 1개.
- 없어진 17개 중 **12개는 원 `plan/pending/P1.5.0~11.md`의 옛 경로**, **5개는 역사 CI workflow 경로**. Workflow 7→2의 기존 검증은 [T01](T01_GITHUB_CI_TARGET.md)에 **검증 완료/재논쟁 금지**로 고정했다.
- 최신 4,080 중 **3,968개 기존 경로가 baseline CSV와 정확히 일치**(97.25%); 미등록 경로 112개는 모두 **새 관리 문서/이동 경로**, **새 소스 누락 없음**. 신규 T01~09 9경로 역시 docs/refactor/architecture 내부 **RF-079 논리 Owner**로 분류. 새 RF 추가 필요 없음.
- `STATUS.md` 첫 문단의 **DONE 0**은 잘못된 오래된 문장: Git 폴더 내 DONE RF-002~006 **5건**이 실제 기록. STATUS를 같이 정정한다.
- 기준선 소유권 CSV는 역사적 원본으로 고정. 현재 경로 신규 문서들의 Owner는 본 T06을 델타 정합성 근거로 사용하되, **RF-079 완료 심사 때 신규 경로를 최종 owner inventory에 실제 매핑했다는 증거도 필요**하다. 역사 파일을 몰래 다시 쓰지 않는다.

## 개선 품질 기준
- 문서 검색 1단계: CURRENT → D00 → T00 → 해당 T01~T09 또는 libs frozen V3 → RF → STATUS. 역사 자료가 CURRENT보다 우선하는 상황 제거.
- 오래된 `docs/refactor/architecture/P15_*.md`는 evidence/snapshot로만 사용, 새로운 T00과 목표 소유권이 충돌하면 D00/T00/Txx로 해결. 역사를 대량 삭제하거나 과거 SHA·근거 재작성 금지.
- docs 하위 83개 실제 디렉터리는 모두 현재 인덱스로 존재한다. 다른 디렉터리로 실제 MOVE는 외부/이전 링크·CI glob·파일 참조 전수 확인 후만. 구조 목표가 특정 모든 문서를 물리적으로 `refactor/` 아래로 옮기라는 뜻이 아니다.

## 파일명 대표 인덱스
- `docs/refactor/P15_SECOND_PASS_GPT_MASTER_DESIGN_2026_10_12.md` — RF-079
- `docs/refactor/README.md` — RF-079
- `docs/refactor/architecture/P15_TECHLEAD_MASTER_20261018.md` — RF-079
- `docs/refactor/architecture/T00_TARGET_TREE.md` — RF-079 신규 관리 경로
- `docs/refactor/architecture/TREE_V3_FROZEN.md` — RF-079
- `docs/refactor/p1_6/MASTER_PLAN.md` — RF-079
- `docs/refactor/p1_6/README.md` — RF-079
- `docs/refactor/plan/STATUS.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/criteria/P1.5.0.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/criteria/P1.5.11.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/done/RF-002.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/done/RF-003.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/done/RF-004.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/done/RF-005.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/done/RF-006.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/pending/RF-009.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/pending/RF-010.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/pending/RF-011.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/pending/RF-012.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/pending/RF-017.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/pending/RF-019.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/verification/claude/RF-013.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/verification/claude/RF-014.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/verification/claude/RF-015.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/verification/claude/RF-016.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/verification/claude/RF-018.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/verification/codex/RF-001.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/verification/codex/RF-007.md` — RF-079 신규 관리 경로
- `docs/refactor/plan/verification/codex/RF-008.md` — RF-079 신규 관리 경로
- `docs/refactor/work_orders/CURRENT.md` — RF-079
- `docs/refactor/work_orders/README.md` — RF-079
- `docs/refactor/work_orders/archive/CURRENT_2026-10-15_INTEGRATION.md` — RF-079
- `docs/refactor/work_orders/archive/CURRENT_R2_THROUGH_341CEDC_2026-10-12.md` — RF-079
- `docs/refactor/work_orders/archive/CURRENT_R3_CODEX_HANDOFF_THROUGH_923D1E2_2026-10-12.md` — RF-079
- `docs/refactor/work_projects/README.md` — RF-079
- `docs/refactor/work_projects/STATUS.json` — RF-079

모든 기존 1,413 문서 파일명을 여기 재인쇄하면 이 문서가 두 번째 역사 자료 저장소가 된다. 전체 실제 명세는 Git tree, 역사 소유권은 CSV, 추가 문서의 계약/범위는 본 문서로 연결한다. 문서명·기능별 특이사항은 해당 RF에서 증명한다.

## 공통 RF 완료 게이트
- **계획이지 이동 승인은 아님.** 실제 import·API·launcher·scheduler·State·serialization·effect 소비자를 확인한 뒤 해당 RF에 path별 MOVE / KEEP_VERIFIED / COMPAT / SAFETY_HOLD / REMOVE_PROVEN 결정을 남긴다.
- 기존 baseline normal/optimized, 신규 exact-SHA independent read-only review, integration SHA hosted CI, 롤백 기준을 증명한다. 승인 없는 main·실거래·CI oracle 변경 금지.
- 정본 링크: [T00](T00_TARGET_TREE.md) / [D00](../../ENGINEERING_DELIVERY_POLICY.md) / [STATUS](../plan/STATUS.md) / [RF baseline CSV](../plan/FILE_COVERAGE_63182ab2.csv).
