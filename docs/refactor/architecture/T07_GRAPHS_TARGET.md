# T07 — graphs/ 실운영 그래프 진입점과 Node 책임
> RF-008~012. 현재 45파일. **`graphs/trading_graph.py` M17 테스트 spine과 `graphs/commander_runtime.py` 실운영 path는 서로 다르다.**

## 목표 폴더트리
```text
graphs/
├── commander_runtime.py              # actual operational orchestration ENTRY, KEEP
├── trading_graph.py                  # M17 test graph/STUB, KEEP
├── nodes/
│   ├── commander_node.py
│   ├── strategist_node.py             # thin graph adapter target, pure owner under libs
│   ├── scanner_node.py                # one canonical rank/Top-1 owner
│   ├── monitor_node.py                # OrderIntent only, broker submit 금지
│   ├── reporter_node.py
│   ├── executor_node.py               # M17 STUB ONLY
│   ├── execute_from_packet.py         # actual EXECUTOR EFFECT: SAFETY_LOCK
│   ├── {scan_candidates,select_candidate,decide_trade}.py
│   ├── {assemble_decision_packet,build_*}.py
│   ├── {load_state,save_state,update_state_after_execution}.py
│   └── 기타 기존 노드
└── pipelines/
    ├── live_cycle.py
    ├── runtime_tick.py
    ├── eod_report.py
    ├── offhours_validation.py
    └── m*_*.py                        # historical/public compatibility proof before consolidation
```

## 최종 Owner·파일별 조치 후보
| 원본 | 최종 목표 | RF/조건 |
|---|---|---|
| `graphs/commander_runtime.py` | 실제 런타임/스케줄 orchestration entry KEEP; pure helper만 libs/agents/commander 또는 libs/runtime/commander에 단일 Owner | RF-008/012, State/timing parity |
| `graphs/trading_graph.py`, `graphs/nodes/executor_node.py` | 테스트 M17 stub로 KEEP; 실제 주문 경로라고 기술 금지 | RF-008/011 |
| `graphs/nodes/strategist_node.py` | graph State adapter만; 전략 Frame과 현행 LLM 호출 계약 분리 | RF-010~012; prompt/LLM count/repair sequence |
| `graphs/nodes/scanner_node.py`, `scan_candidates.py`, `select_candidate.py` | 단일 Scanner Owner/Top-1 rank authority; graph adapter 최소화 | RF-009; score/rank/tie-break/candidate |
| `graphs/nodes/monitor_node.py`, `portfolio_guard_node.py` | monitor signal/Intent vs portfolio guard 분리 | RF-010~012; broker-write zero |
| `graphs/nodes/execute_from_packet.py`, `execute_order.py` | 승인 이후 real guarded order mutation / SAFETY_LOCK | RF-011/012: no unsafe move |
| `graphs/nodes/{decide_trade,update_state_after_execution}.py` | State/authority mutation 그대로 KEEP; 순수 부분만 소비자/효과 입증 후 | RF-010~012 |
| `graphs/nodes/{build_market_snapshot,build_portfolio_snapshot,build_open_order_snapshot,build_risk_context}.py` | bounded read projection; no second source of truth | RF-008~012 |
| `graphs/nodes/{load_state,save_state,log_decision_trace}.py` | State IO/evidence writer 권한 명시, side-effects 유지 | RF-008~012 |
| `graphs/pipelines/{live_cycle,runtime_tick,eod_report,offhours_validation}.py` | canonical entry candidate, caller inventory 검증 후 결정 | RF-008~012 |
| `graphs/pipelines/m10_live_pipeline.py`, `m11*_live_pipeline.py`, `m13_*.py` | 역사/호환 pipeline candidate, scheduler/CLI 참조 제로 증명 전 KEEP | RF-008~012 |

## 완료 조건
- 별개의 실행 경로 지도를 첨부: actual `commander_runtime → execute_from_packet → risk/approval/guard/execution/kiwoom`, test `trading_graph` stub.
- 7개 역할 독립 호출은 실제 owner 함수로 연결하고 순환 import·입력/출력 State 패치·callable identity 확인.
- 준비·포지션·주문·기록의 부작용 및 UNKNOWN/Step5C/UEF 실운영 동등성. 새 Broker/LLM 실행 금지.
- 역사 `m*` 파이프라인 삭제는 보존 증거와 consumer-zero가 있을 때만 승인.

## 실제 45파일 — 경로별 기존 RF 전수
- `graphs/commander_runtime.py` — RF-011
- `graphs/nodes/assemble_decision_packet.py` — RF-012
- `graphs/nodes/build_decision_context.py` — RF-012
- `graphs/nodes/build_execution_readiness.py` — RF-012
- `graphs/nodes/build_market_snapshot.py` — RF-012
- `graphs/nodes/build_open_order_snapshot.py` — RF-012
- `graphs/nodes/build_portfolio_snapshot.py` — RF-012
- `graphs/nodes/build_risk_context.py` — RF-012
- `graphs/nodes/build_snapshots.py` — RF-012
- `graphs/nodes/commander_node.py` — RF-011
- `graphs/nodes/decide_trade.py` — RF-012
- `graphs/nodes/decision_node.py` — RF-012
- `graphs/nodes/ensure_token.py` — RF-012
- `graphs/nodes/execute_from_packet.py` — RF-012
- `graphs/nodes/execute_order.py` — RF-012
- `graphs/nodes/executor_node.py` — RF-012
- `graphs/nodes/hydrate_skill_results_node.py` — RF-012
- `graphs/nodes/load_state.py` — RF-012
- `graphs/nodes/log_decision_trace.py` — RF-012
- `graphs/nodes/monitor_node.py` — RF-010
- `graphs/nodes/plan_api.py` — RF-012
- `graphs/nodes/portfolio_guard_node.py` — RF-012
- `graphs/nodes/prepare_api_call.py` — RF-012
- `graphs/nodes/prepare_order_dry_run.py` — RF-012
- `graphs/nodes/read_account_balance.py` — RF-012
- `graphs/nodes/reporter_node.py` — RF-012
- `graphs/nodes/risk_cash_truth.py` — RF-012
- `graphs/nodes/save_state.py` — RF-012
- `graphs/nodes/scan_candidates.py` — RF-009
- `graphs/nodes/scanner_node.py` — RF-009
- `graphs/nodes/select_candidate.py` — RF-009
- `graphs/nodes/skill_contracts.py` — RF-012
- `graphs/nodes/strategist_node.py` — RF-008
- `graphs/nodes/update_state_after_execution.py` — RF-012
- `graphs/pipelines/eod_report.py` — RF-012
- `graphs/pipelines/live_cycle.py` — RF-012
- `graphs/pipelines/m10_live_pipeline.py` — RF-012
- `graphs/pipelines/m11_2_live_pipeline.py` — RF-012
- `graphs/pipelines/m11_live_pipeline.py` — RF-012
- `graphs/pipelines/m13_eod_report.py` — RF-012
- `graphs/pipelines/m13_live_loop.py` — RF-012
- `graphs/pipelines/m13_tick.py` — RF-012
- `graphs/pipelines/offhours_validation.py` — RF-012
- `graphs/pipelines/runtime_tick.py` — RF-012
- `graphs/trading_graph.py` — RF-011

## 공통 RF 완료 게이트
- **계획이지 이동 승인은 아님.** 실제 import·API·launcher·scheduler·State·serialization·effect 소비자를 확인한 뒤 해당 RF에 path별 MOVE / KEEP_VERIFIED / COMPAT / SAFETY_HOLD / REMOVE_PROVEN 결정을 남긴다.
- 기존 baseline normal/optimized, 신규 exact-SHA independent read-only review, integration SHA hosted CI, 롤백 기준을 증명한다. 승인 없는 main·실거래·CI oracle 변경 금지.
- 정본 링크: [T00](T00_TARGET_TREE.md) / [D00](../../ENGINEERING_DELIVERY_POLICY.md) / [STATUS](../plan/STATUS.md) / [RF baseline CSV](../plan/FILE_COVERAGE_63182ab2.csv).
