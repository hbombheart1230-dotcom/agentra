# P1.5 T4 + PR5 — tracked source consumer inventory and safe cleanup decisions

Date: 2026-10-15. Integration HEAD scanned: `b05b36a0ad6a41c401f1d75da9c5f27a77883a52`.
Tool: `scripts/refactor/inventory_p15_consumers.py`, smoke `tests/test_p15_consumer_inventory.py`.
Independent GitHub Actions run: [38715884053](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38715884053), **SUCCESS**.
Full JSON evidence: [artifact 11962387571](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38715884053/artifacts/11962387571) (short-lived, 7-day retention).

## Actual read-only scan

| Measure | Count |
|---|---:|
| Tracked source/files in scanned tree | 3,560 |
| Tracked Python files parsed | 2,226 |
| Python parse errors | 0 |
| In-repository static AST import edges | 4,486 |
| Literal dynamic import edges | 162 |
| Nonliteral dynamic import call sites (still unknown) | 58 |
| Root `scripts/*.py` files | 193 |
| Script compatibility wrappers tracked by PR5 (separate contract) | 141 |

Important: 193 root scripts **does not** equal 193 removable wrappers. PR5 explicitly preserves 141 public CLI compatibility wrappers; the other root scripts may have independent operational responsibilities.

Selected entrypoint static consumer counts (not all dynamic/external consumers):
- `graphs/nodes/execute_from_packet.py`: **34**, and dynamic import loader in the source; **SAFETY_LOCK**.
- `graphs/nodes/scanner_node.py`: **36**.
- `graphs/nodes/strategist_node.py`: **32**.
- `graphs/nodes/monitor_node.py`: **27**.
- `graphs/trading_graph.py`: **10**; graph-shaped M17 baseline is not automatically a production LangGraph StateGraph.
- `libs/reporting/live_execution_bundle_runner.py`: **3**.

Selected legacy facade consumers:
| Source | Static consumer count | Consequence |
|---|---:|---|
| `libs/agent/commander.py` | 2 | legacy Commander/tests in use |
| `libs/agent/strategist.py` | 4 | cannot delete |
| `libs/agent/scanner.py` | 3 | old Scanner implementation still wired |
| `libs/agent/monitor.py` | 3 | placeholder but used by compatibility Commander/test |
| `libs/agent/reporter.py` | 16 | real Reporter entry and consumers |
| `libs/agent/executor.py` | 0 observed | not proven unused: dynamic/exports/external callers |
| `libs/agent/router.py` | 1 | must keep |

## Reporter is a substantial coupling problem

The AST import graph contains **133** referenced `libs/reporting/evaluation/*` modules. It has **327 incoming static edges from outside the evaluation subtree**, of which 243 originate in tests, 45 in scripts, 23 in libraries, and 16 in Python tools stored in docs. It also has 68 outgoing cross-subtree edges. These are links, not proven runtime execution counts. **Bulk folder movement of Reporter/Evaluation is NOT approved.**

AST scan found no meaningful byte-identical implementation group to blindly consolidate; same-hash groups consist of blank or boilerplate `__init__.py` modules (and one zero/blank test). Identical placeholder content does not justify deleting Python packages.

## Root tracked file audit

Read-only metadata/reference audit: [38716302208](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38716302208) SUCCESS.

| Root file | Tracked bytes | Textual references in tracked source/docs | Decision |
|---|---:|---:|---|
| `b.jsonl` | 3,514,424 | 10 filename occurrences | REVIEW: no deletion |
| `_health.json` | 167 | 32 filename occurrences | REVIEW: no deletion |

These counts include docs, fixtures and the audit workflow itself, and do not prove an actual runtime read. Conversely, textual absence would not prove absence of external use. **Never classify either file as safe garbage automatically.** No content or private data was printed.

## Actual operational references found in config/deploy

- `scripts/docker_healthcheck.py` appears in Docker Compose and deployment PowerShell paths.
- `scripts/restart_live_session.py` appears in Compose, cutover and rollback scripts.
- `scripts/run_m13_live_loop.py`, `run_session.py`, Q10/Q12 baseline wrappers appear in M31 Windows registration helpers.
- These paths are operating contracts, not safe deletion targets.

## Precise cleanup dispositions (the current decision)

**KEEP:** T4 canonical nodes, all active Reporter interfaces, Supervisor/Executor, all 141 PR5 public CLI wrappers, safe nine PR5 Reporter relocations, existing runtime Owner packages.

**REVIEW_AFTER_CONSUMER_AUDIT:** evaluation/research owner move, legacy Scanner authority and Agent shim retirement, uncertain dynamic imports, large root artifacts, non-runtime Reports generated outputs.

**SAFETY_LOCK:** `execute_from_packet.py`, Broker API/adapters, Supervisor approval, Step5C CAS, UNKNOWN quarantine, UEF-7/8/9 publication and Q10/Q12 production paths.

**SAFE_NOW:** documentation corrections, consumer manifest and diagnostic verification; do not invent a bulk file DELETE list from incomplete evidence. Extract a limited read-only group only after its original static/dynamic callers and tests are enumerated.

## Required independent check before moving any folder

Codex must inspect module-object aliases (`sys.modules`), monkeypatch seams, dynamic path loaders, entrypoint CLI/scheduled launchers, public ABI/DTO, production State/effect boundaries, exact fixture replay and Windows native evidence. No source location move can be accepted on a static-import count alone.

Status: **CONSUMER_INVENTORY_COLLECTED / ARCH_CONVERGENCE_NOT_APPROVED**. T4 integration Linux CI was pending at analysis time; no blanket T4 integration ACCEPT.
