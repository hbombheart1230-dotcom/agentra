# Agentra P1.5 전체 ROOT→LEAF 리팩터링 현황

**기준선(역사 고정):** `63182ab27ecf889768003f637a40577ba1277f86` · **3,985파일/298디렉터리/93개 RF**. **현행 구조(기준 `d082cee8`): 4,080파일/302디렉터리**; 신규 T01~09 문서 9개가 합쳐지면 **4,089파일/302디렉터리** (커밋 후 HEAD 검산 필요). **RF 상태: pending 74 / verification 10 / rework 4 / DONE 5** (RF-002~006). 과거 'DONE 0'은 오류였으며 이 기록으로 정정.

## 현재 지팀장 판정·다음 실행 (2026-10-25)

- **RF-009·020 (B 1순위 REWORK):** A의 기존 범위 한정 peer PASS는 그대로 보존. RF-009는 Graph 3 owner의 State/ranking/NOOP·외부 소비자 경계, RF-020은 Monitor 30 owner의 dynamic/side-effect·KEEP 소비자 맵 증거가 RF 전체 인수조건에 부족하다. **신규 회귀·소스 버그 확정은 아님.** Codex B가 기존 RF 소유 경로의 최소 코드 delta 또는 exact-SHA 완전 KEEP 근거를 제출, Claude A는 새 증거만 read-only peer. RF-014/019·RF-026의 타 소유권/안전 HOLD는 그대로 보존.
- **RF-067** B SELF normal/-O 각 AST 14/14 및 표적 pytest 7 PASS, B HANDOFF `B-20261025T020000Z`, 신규 코드 없음. **pending→verification/codex** 접수, A read-only peer 우선; 공개 preflight CLI의 브로커·운영 데이터 위험으로 직접 실행 NOT_RUN. NOT_DONE.

- **RF-066** B self normal/-O 각 AST 17/17 및 표적 pytest 7 PASS, BASE/integration/B 17개 소유 경로 diff 0. `pending → verification/codex` 이동; **A read-only peer 1순위**, 브로커 조정·SQLite/intent·Step5D·파일 이동·외부 카탈로그 동기화 CLI **미실행/안전 검토 필요**. NOT_DONE.
- **RF-063** A peer **PASS_SCOPED**(76 소유 blob 동일, normal/-O 각 130 PASS, PYTHONUTF8=1). 13개 위험 키워드 CLI 미실행, cp949 기본 로케일 UnicodeDecodeError 1건은 ENVIRONMENT 확인 필요. **RF-065** A peer **PASS_SCOPED**(54 blob 동일, normal/-O 각 7 PASS, 50개 파일 쓰기 CLI 미실행). 둘 다 전체 소비자·CI 미완료로 verification 유지.
- **RF-018** A BASE/integration 동일 명령 1152 PASS/2 FAIL/57 ERROR 모두 동일: 59건 **BASELINE_EXISTING/HISTORICAL_INVENTORY**, 신규 회귀 0(제출 증거 범위). **RF-014** BASE/integration 각 1102 PASS/3 FAIL 동일: 3건 BASELINE_EXISTING, A 브랜치 Reporter 소비자 2건 CROSS_RF_OWNER. B는 분리된 증거만 독립 검증; 최종 peer PASS 아님.
- **RF-013 (A 1순위 REWORK)** 기존 A 후보의 Reporter 신규 9파일과 RF-074 frozen inventory 충돌을 해결할 **RF-013 소유 경로 한정 합법 최소 source 후보** 제출; RF-030/035 4 consumer wrapper와 RF-074/CI 오라클은 미승인·수정 금지. 기존 (c) 전체 통합 BLOCKED는 지속. **RF-001 (B 1순위 REWORK)** 33 owner 안의 2,308행 core IO/side-effect·19개 divergent owner 경계를 해소하는 소스 delta 또는 완전 KEEP 실증. 기존 PASS_SCOPED는 전체 peer PASS 아님. RF-064는 신규 차단 해소 증거 없어 pending 유지.
- **다음 배정(1→2→3순위):** **A RF-013 / B RF-001→009→020 소유범위 반려 보완 먼저** → A RF-067 등 새 peer, B RF-018·014 신규 실패분류 peer → A RF-019 / B RF-068 신규 개발. 1순위는 각자 완료 가능한 여러 RF를 같은 회차에 순차 처리, 동일 증거 반복 금지. RF-021 안전 HOLD 유지. CI exact integration SHA GREEN 없으면 통합/DONE 금지.

## 파일별 TARGET_PATH 직접 계약 — 2026-10-25

- `RF-001~093` **93/93개 문서에 각자 파일별 SOURCE→TARGET 표 삽입**; 기준선 CSV 3,985행 + 신규 docs 121행 = **4,106행**. 실제 HEAD 4,089파일과 차이는 역사 이동·퇴역 17개를 포함하기 때문이며, 실제 파일을 추가/이동한 것이 아니다.
- 분류: `COMPAT_OWNER_REVIEW` 6; `KEEP_CANDIDATE` 3549; `KEEP_VERIFIED_EXISTING_DONE` 169; `MOVED_CURRENT_PATH` 12; `NEW_DOC_KEEP_CANDIDATE` 121; `OWNER_SPLIT_REVIEW` 164; `RESTRICTED_REVIEW_KEEP` 5; `RETIRED_HISTORICAL` 5; `SAFETY_HOLD_KEEP` 75.
- **정확한 정의:** KEEP_CANDIDATE는 현재 경로의 **보존 후보**이며 확인된 최종 목표 위치나 책임 분리 완료 판정이 아니다. A/B는 검토 때마다 실제 함수·소비자·호출 계약을 증명해 TARGET/ACTION/Owner 확정. 안전·교차 Owner 임의 MOVE 금지.
- 과거 DONE RF-002~006의 169개 파일은 기존 KEEP_VERIFIED 판정과 증거를 **소급 기록만** 했다. 기존 DONE/peer/CI 판정 변경·재실행 없음. RF-021 안전 HOLD 및 EX1~EX6 제한 유지.

## 지팀장 차단 해소 책임표 (D00 §6; 2026-10-25)

| RF | 결정 책임 / 수행·독립 검증 | 차단을 푸는 **다음 구체적 증거** | 재개 상태 |
|---|---|---|---|
| [013](rework/claude/RF-013.md) | **A 소유 RF만 REWORK / GPT 교차 승인 / B peer** | 신규 9경로를 frozen inventory에 추가하지 않는 RF-013 자체 최소 후보, RF-030/035 wrapper는 읽기만 | `REWORK_OWNER_LOCAL / CROSS_RF_HOLD` |
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
| `apps/` | 240 | [RF-001](rework/codex/RF-001.md) · [RF-002](done/RF-002.md) · [RF-003](done/RF-003.md) · [RF-004](done/RF-004.md) · [RF-005](done/RF-005.md) · [RF-006](done/RF-006.md) · [RF-007](verification/codex/RF-007.md) | 미판정 |
| `config/` | 8 | [RF-090](pending/RF-090.md) | 미판정 |
| `data/` | 25 | [RF-091](pending/RF-091.md) | 미판정 |
| `deploy/` | 33 | [RF-087](pending/RF-087.md) · [RF-088](pending/RF-088.md) · [RF-089](pending/RF-089.md) | 미판정 |
| `docs/` | 1313 | [RF-079](pending/RF-079.md) · [RF-080](pending/RF-080.md) · [RF-081](pending/RF-081.md) · [RF-082](pending/RF-082.md) · [RF-083](pending/RF-083.md) · [RF-084](pending/RF-084.md) · [RF-085](pending/RF-085.md) · [RF-086](pending/RF-086.md) | 미판정 |
| `graphs/` | 45 | [RF-008](verification/codex/RF-008.md) · [RF-009](rework/codex/RF-009.md) · [RF-010](pending/RF-010.md) · [RF-011](pending/RF-011.md) · [RF-012](pending/RF-012.md) | 미판정 |
| `libs/` | 1227 | [RF-013](rework/claude/RF-013.md) · [RF-014](verification/claude/RF-014.md) · [RF-015](verification/claude/RF-015.md) · [RF-016](verification/claude/RF-016.md) · [RF-017](pending/RF-017.md) · [RF-018](verification/claude/RF-018.md) · [RF-019](pending/RF-019.md) · [RF-020](rework/codex/RF-020.md) · [RF-021](pending/RF-021.md) · [RF-022](pending/RF-022.md) · [RF-023](pending/RF-023.md) · [RF-024](pending/RF-024.md) · [RF-025](pending/RF-025.md) · [RF-026](pending/RF-026.md) · [RF-027](pending/RF-027.md) · [RF-028](pending/RF-028.md) · [RF-029](pending/RF-029.md) · [RF-030](pending/RF-030.md) · [RF-031](pending/RF-031.md) · [RF-032](pending/RF-032.md) · [RF-033](pending/RF-033.md) · [RF-034](pending/RF-034.md) · [RF-035](pending/RF-035.md) · [RF-036](pending/RF-036.md) · [RF-037](pending/RF-037.md) · [RF-038](pending/RF-038.md) · [RF-039](pending/RF-039.md) · [RF-040](pending/RF-040.md) · [RF-041](pending/RF-041.md) · [RF-042](pending/RF-042.md) · [RF-043](pending/RF-043.md) · [RF-044](pending/RF-044.md) · [RF-045](pending/RF-045.md) · [RF-046](pending/RF-046.md) · [RF-047](pending/RF-047.md) · [RF-048](pending/RF-048.md) · [RF-049](pending/RF-049.md) · [RF-050](pending/RF-050.md) · [RF-051](pending/RF-051.md) · [RF-052](pending/RF-052.md) · [RF-053](pending/RF-053.md) · [RF-054](pending/RF-054.md) · [RF-055](pending/RF-055.md) · [RF-056](pending/RF-056.md) · [RF-057](pending/RF-057.md) · [RF-058](pending/RF-058.md) · [RF-059](pending/RF-059.md) · [RF-060](pending/RF-060.md) · [RF-061](pending/RF-061.md) · [RF-062](pending/RF-062.md) | 미판정 |
| `scripts/` | 418 | [RF-063](verification/codex/RF-063.md) · [RF-064](pending/RF-064.md) · [RF-065](verification/codex/RF-065.md) · [RF-066](verification/codex/RF-066.md) · [RF-067](pending/RF-067.md) · [RF-068](pending/RF-068.md) · [RF-069](pending/RF-069.md) · [RF-070](pending/RF-070.md) · [RF-071](pending/RF-071.md) | 미판정 |
| `tests/` | 658 | [RF-072](pending/RF-072.md) · [RF-073](pending/RF-073.md) · [RF-074](pending/RF-074.md) · [RF-075](pending/RF-075.md) · [RF-076](pending/RF-076.md) · [RF-077](pending/RF-077.md) · [RF-078](pending/RF-078.md) | 미판정 |
| 루트 파일 | 11 | [RF-093](pending/RF-093.md) | 미판정 |

## libs/ 26개 패키지 — **기준선/현행 파일수 동일**, 최종 Owner 판정 별도
| 패키지 | 파일 | 독립 작업 | 상태 |
|---|---:|---|---|
| `libs/agent/` | 14 | [RF-040](pending/RF-040.md) | 미판정 |
| `libs/agents/` | 119 | [RF-013](rework/claude/RF-013.md) · [RF-014](verification/claude/RF-014.md) · [RF-015](verification/claude/RF-015.md) · [RF-016](verification/claude/RF-016.md) · [RF-017](pending/RF-017.md) | 미판정 |
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

**RF 상태:** [pending](pending/) **74건** → [verification/claude](verification/claude/) **4건** / [verification/codex](verification/codex/) **6건** ↔ [rework/claude](rework/claude/) **1건** / [rework/codex](rework/codex/) **3건** → [done](done/) **5건** = **총 93건**. verification에는 검증 대기·PASS_SCOPED·BLOCKED가 포함된다. rework에는 지팀장이 구체적 소유 경로 보완을 확정한 원개발자 RF만 이동하며, 동일 RF를 여러 상태에 중복 보관하지 않는다. DONE은 peer PASS·선별 통합·정확한 integration SHA normal/-O 및 필수 hosted CI GREEN 후 지팀장만 판정한다.

**현재 배정:** [CURRENT](../work_orders/CURRENT.md)의 A RF-013 / B RF-001·009·020 1순위 rework → 2순위 verification → 3순위 pending 개발. 각 회차에서 실행 가능한 복수 RF 처리, BLOCKED만 건너뛴다.

**전수 소유권:** [3985파일↔RF CSV](FILE_COVERAGE_63182ab2.csv) · [P1.5.0~11 합격 기준](criteria/). 회차별 실행 이력은 Git 이력·RF·HANDOFF에서 확인한다.
