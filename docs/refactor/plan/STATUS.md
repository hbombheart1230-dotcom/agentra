# Agentra P1.5 전체 ROOT→LEAF 리팩터링 현황

**전수 기준:** `63182ab27ecf889768003f637a40577ba1277f86` · **3985개 파일 / 298개 디렉터리** · RF 독립작업 **93건** · 검증 대기/BLOCKED **6건** · 증거로 최종 확인된 완료 **0건**, 나머지는 이전 부분 개발·통합 검증 필요.

## 우선순위 / 잔여 작업
| 우선 | 목적 | 미검증 RF |
|---|---|---:|
| P1 | 크고 순수한 구조 개선 | 19 |
| P2 | 저위험 이동·호환 | 20 |
| P3 | 계약·IO 책임 | 32 |
| P4 | 전수 유지·역사 분류 | 14 |
| P5 | 거래 안전·최종 게이트 | 8 |

## 루트 폴더 전체
| 범위 | 파일 | 독립 작업 | 상태 |
|---|---:|---|---|
| `.github/` | 7 | [RF-092](pending/RF-092.md) | 미판정 |
| `apps/` | 240 | [RF-001](verification/codex/RF-001.md) · [RF-002](verification/codex/RF-002.md) · [RF-003](pending/RF-003.md) · [RF-004](pending/RF-004.md) · [RF-005](pending/RF-005.md) · [RF-006](pending/RF-006.md) · [RF-007](pending/RF-007.md) | 미판정 |
| `config/` | 8 | [RF-090](pending/RF-090.md) | 미판정 |
| `data/` | 25 | [RF-091](pending/RF-091.md) | 미판정 |
| `deploy/` | 33 | [RF-087](pending/RF-087.md) · [RF-088](pending/RF-088.md) · [RF-089](pending/RF-089.md) | 미판정 |
| `docs/` | 1313 | [RF-079](pending/RF-079.md) · [RF-080](pending/RF-080.md) · [RF-081](pending/RF-081.md) · [RF-082](pending/RF-082.md) · [RF-083](pending/RF-083.md) · [RF-084](pending/RF-084.md) · [RF-085](pending/RF-085.md) · [RF-086](pending/RF-086.md) | 미판정 |
| `graphs/` | 45 | [RF-008](pending/RF-008.md) · [RF-009](pending/RF-009.md) · [RF-010](pending/RF-010.md) · [RF-011](pending/RF-011.md) · [RF-012](pending/RF-012.md) | 미판정 |
| `libs/` | 1227 | [RF-013](verification/claude/RF-013.md) · [RF-014](verification/claude/RF-014.md) · [RF-015](pending/RF-015.md) · [RF-016](pending/RF-016.md) · [RF-017](pending/RF-017.md) · [RF-018](verification/claude/RF-018.md) · [RF-019](pending/RF-019.md) · [RF-020](verification/codex/RF-020.md) · [RF-021](pending/RF-021.md) · [RF-022](pending/RF-022.md) · [RF-023](pending/RF-023.md) · [RF-024](pending/RF-024.md) · [RF-025](pending/RF-025.md) · [RF-026](pending/RF-026.md) · [RF-027](pending/RF-027.md) · [RF-028](pending/RF-028.md) · [RF-029](pending/RF-029.md) · [RF-030](pending/RF-030.md) · [RF-031](pending/RF-031.md) · [RF-032](pending/RF-032.md) · [RF-033](pending/RF-033.md) · [RF-034](pending/RF-034.md) · [RF-035](pending/RF-035.md) · [RF-036](pending/RF-036.md) · [RF-037](pending/RF-037.md) · [RF-038](pending/RF-038.md) · [RF-039](pending/RF-039.md) · [RF-040](pending/RF-040.md) · [RF-041](pending/RF-041.md) · [RF-042](pending/RF-042.md) · [RF-043](pending/RF-043.md) · [RF-044](pending/RF-044.md) · [RF-045](pending/RF-045.md) · [RF-046](pending/RF-046.md) · [RF-047](pending/RF-047.md) · [RF-048](pending/RF-048.md) · [RF-049](pending/RF-049.md) · [RF-050](pending/RF-050.md) · [RF-051](pending/RF-051.md) · [RF-052](pending/RF-052.md) · [RF-053](pending/RF-053.md) · [RF-054](pending/RF-054.md) · [RF-055](pending/RF-055.md) · [RF-056](pending/RF-056.md) · [RF-057](pending/RF-057.md) · [RF-058](pending/RF-058.md) · [RF-059](pending/RF-059.md) · [RF-060](pending/RF-060.md) · [RF-061](pending/RF-061.md) · [RF-062](pending/RF-062.md) | 미판정 |
| `scripts/` | 418 | [RF-063](pending/RF-063.md) · [RF-064](pending/RF-064.md) · [RF-065](pending/RF-065.md) · [RF-066](pending/RF-066.md) · [RF-067](pending/RF-067.md) · [RF-068](pending/RF-068.md) · [RF-069](pending/RF-069.md) · [RF-070](pending/RF-070.md) · [RF-071](pending/RF-071.md) | 미판정 |
| `tests/` | 658 | [RF-072](pending/RF-072.md) · [RF-073](pending/RF-073.md) · [RF-074](pending/RF-074.md) · [RF-075](pending/RF-075.md) · [RF-076](pending/RF-076.md) · [RF-077](pending/RF-077.md) · [RF-078](pending/RF-078.md) | 미판정 |
| 루트 파일 | 11 | [RF-093](pending/RF-093.md) | 미판정 |

## libs/ 26개 패키지
| 패키지 | 파일 | 독립 작업 | 상태 |
|---|---:|---|---|
| `libs/agent/` | 14 | [RF-040](pending/RF-040.md) | 미판정 |
| `libs/agents/` | 119 | [RF-013](verification/claude/RF-013.md) · [RF-014](verification/claude/RF-014.md) · [RF-015](pending/RF-015.md) · [RF-016](pending/RF-016.md) · [RF-017](pending/RF-017.md) | 미판정 |
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
| `libs/runtime/` | 322 | [RF-018](verification/claude/RF-018.md) · [RF-019](pending/RF-019.md) · [RF-020](verification/codex/RF-020.md) · [RF-021](pending/RF-021.md) · [RF-022](pending/RF-022.md) · [RF-023](pending/RF-023.md) · [RF-024](pending/RF-024.md) · [RF-025](pending/RF-025.md) · [RF-026](pending/RF-026.md) · [RF-027](pending/RF-027.md) | 미판정 |
| `libs/skills/` | 6 | [RF-057](pending/RF-057.md) | 미판정 |
| `libs/storage/` | 3 | [RF-058](pending/RF-058.md) | 미판정 |
| `libs/strategies/` | 21 | [RF-059](pending/RF-059.md) | 미판정 |
| `libs/supervisor/` | 4 | [RF-060](pending/RF-060.md) | 미판정 |
| `libs/tools/` | 3 | [RF-061](pending/RF-061.md) | 미판정 |

**RF 상태 3단계:** [pending 개발 대기](pending/) → [verification/claude (Claude 구현·Codex 검증)](verification/claude/) 또는 [verification/codex (Codex 구현·Claude 검증)](verification/codex/) → [done](done/). 현재 verification 6건(RF-013/018/014→Codex 검증, RF-001/020/002→Claude 검증), pending 87건, done 0건이다. 이 경로는 실제 검증 완료를 주장하지 않으며, 구현 SHA와 self 정상/-O 명령 및 인수인계가 없는 이동은 무효다.\n\n**단일 파일 소유권:** [3985파일↔RF CSV](FILE_COVERAGE_63182ab2.csv). [pending 독립작업](pending/) · [done 검증완료](done/) · [P1.5.0~11 합격 기준](criteria/) · [CURRENT](../work_orders/CURRENT.md).

**2026-10-24 08:58 KST 큐 접수:** 4건은 검증 차단 상태를 보존한 대기이며 PASS/DONE이 아니다. 개발 병렬 배정은 A RF-014(20파일), B RF-002(9파일). 역사 CI_RED는 별도 트랙, 검증 차단으로 개발을 멈추지 않는다.\n\n**완료 판정:** 지팀장이 source/peer 실제 PASS·정확한 통합 SHA 필수 CI 후에만 verification→done과 상태 숫자를 갱신하며, 수정 없는 KEEP_VERIFIED도 증거로 인정. 기존 안전 예외 별도 처리.

**2026-10-24 09:55 KST 추가 큐 접수:** RF-014(Scanner, Claude 작성→Codex 검증, self 921 PASS/2 역사 게이트 FAIL), RF-002(UI, Codex 작성→Claude 검증, 9/9 KEEP + 81 normal/-O 독립 범위 PASS). 둘 다 최종 DONE/CI GREEN 아님. 다음 개발 A RF-015, B RF-003. 기존 RF-013/018/001/020 큐 보존.
