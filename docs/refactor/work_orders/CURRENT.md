# P1.5 CURRENT Work Order — P15-R2-R0R1-001

Status: READY_FOR_LOCAL_BASELINE (NOT IMPLEMENTATION PASS)
Created: 2026-10-09
Branch: refactor/p1.5 ONLY
Observed remote source HEAD BEFORE this work-order-doc update: 6bdeb3ca783f99fcef2e1c0d048bf40623438490
Frozen main baseline: 2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb
Local HEAD: UNKNOWN — Claude must record and reconcile it WITHOUT reset/clean.
Local primary workspace: C:\Agentra
Work type: AUDIT/BEFORE CHARACTERIZATION ONLY. NO RUNTIME PYTHON EDITS IN THIS WORK ORDER.

## Authoritative instructions

- docs/refactor/P15_EXECUTION_PROTOCOL.md
- docs/refactor/p1_5_small_owner_policy_and_rollback_decision_v1_2.md
- docs/refactor/p1_5_reporting_implementation_packet_v1_2.md
- docs/refactor/p1_5_reporting_implementation_packet_v1_1.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_1_to_11_responsibility_alignment_v1_1.md

## Objective

Prove the existing R2-A/B/C lineage is safe to CONTINUE rather than whole rollback. Produce a pinned local reporting BEFORE baseline and a complete owner/caller map for ONE first <=350-LOC read-only section extraction **for the NEXT** work order. Do NOT create new modules or alter runtime in this first work order.

## Claude task — local C:\Agentra

1. Inspect branch, actual HEAD, status, main ancestry, git worktrees. Do not disturb two Q12 dirty worktrees. Abort on unexplained local divergence.
2. Measure physical LOC, defs, public/private exports, patchable symbols, direct production/test imports/callers and dependencies for libs/reporting/trade_report/sections.py (remote observed 2,233 physical LOC) and related trade_report_ai.py façade (remote observed 3,039).
3. Build one function-by-function owner/consumer ledger: current line number, KEEP/MOVE/WRAPPER/DEAD/SAFETY-LOCK, responsibility, proposed SINGLE owner and target <=350 LOC, side effects/LLM, monkeypatch binding and test evidence.
4. Choose ONE smallest cohesive read-only section builder as candidate for NEXT tranche; name exact functions, destination module, LOC estimate, call-time patch compatibility and its direct golden tests. If no safe candidate, mark BLOCKED.
5. Capture representative report JSON/Markdown/truth/provenance and prompt/retry/call-count BEFORE evidence using existing READ-ONLY real local report fixtures. Never regenerate a production artifact path, mutate broker or touch UEF production files.
6. Run non-destructive relevant focused pytest with isolated temp output and write exact commands, pass/fail/skip totals; compare availability of historical 337+12 tests with local collection. If not run, explicitly state NOT RUN.
7. Record all findings in the Claude evidence report. Commit only the evidence documentation and meaningful UI patch notes+daily patch as appropriate. Do not modify Python or fixtures.

Claude report path: docs/refactor/work_orders/evidence/P15-R2-R0R1-001-CLAUDE.md

## Codex task — independent local verification

Read the exact SHA that Claude reports and independently reproduce the function/consumer/monkeypatch and local pytest evidence. Verify the proposed single owner is really independent, <=350 LOC projected and output/truth/LLM-safe; find hidden callers and any missing test categories. Do not change source or fix Claude's report silently. Record PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED with actual executed checks and unresolved gates.

Codex report path: docs/refactor/work_orders/evidence/P15-R2-R0R1-001-CODEX.md

## Acceptance and stop criteria

- Both reports cite pinned actual local and submitted SHAs, with no incorrect branch/worktree claims.
- No runtime Python, test-fixture or production artifact mutation.
- Full ledger, independent consumer/patch surface, BEFORE baseline with safe redacted evidence, test counts, proposed bounded <=350-LOC implementation scope.
- No assertion of current local test PASS without an actual run; safety/UEF/Docker marked NOT RUN where applicable.
- GPT reviews Codex verdict, records next decision; CURRENT.md not changed by Claude/Codex.
- STOP on local dirty/unexpected branch, missing owner proof, real-order path, Q12 worktree interference, failed/non-equivalent baseline or unknown production-write risk.
