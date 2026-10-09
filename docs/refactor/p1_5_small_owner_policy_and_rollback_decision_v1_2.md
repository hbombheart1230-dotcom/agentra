# P1.5 Implementation Policy v1.2 — Strict Small Owners, No Blanket Rollback

Date: 2026-10-09
Canonical branch: refactor/p1.5 (the only active P1.5 development branch)
Base main: 2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb
Reviewed refactor HEAD before this doc: 453084b3a17c0cfa562c73f74b7e7ea0b844a381
Authority: P1.5 Constitution, detailed v1.0/v1.1 packets and P1.5.11 safety freeze, all retained.
Operator handoff: P1.2 CLOSED, P1.3 FULL_DOCKER_FROZEN, 2 GiB production memory ceiling. This document does not itself revalidate the local Docker environment.

## Decision — CONTINUE, not reset
Keep the entire P1.5.1 and R2-A/R2-B/R2-C commit history and current implementations. Do not hard-reset refactor/p1.5 to main, revert the whole Reporting tree, recreate modules from scratch, delete historical regression tests, or disturb either dirty Q12 worktree.

Why: prior R2-A/B/C extractions reduced public façades without evidence of systemic behavioral failure; existing historical Python CI showed 337 Reporting tests and 12 seam/UI tests passing. The remaining debt is large extracted Owner modules and incomplete owner/tests acceptance, not proof the original extraction should be undone. Those prior CI runs are NOT proof that the actual local C:\Agentra working copy remains equivalent today.

Before implementation: local Claude reads C:\Agentra branch/HEAD/status, validates main ancestry, maps real output fixtures / saved trading evidence read-only, checks hidden imports/monkeypatches and snapshots BEFORE artifacts. If local files diverge from remote or unknown dirty changes are present, STOP rather than reset/clean. Only local Claude implements; Codex independently audits and does not simultaneously edit the same files. If a new bounded slice fails parity, revert only that slice without history rewrite and preserve failure evidence. Whole-work rollback requires a demonstrable systemic correctness violation and operator approval.

## Mandatory new/extracted file-size limits
- Every NEW or materially expanded implementation-owner Python file: **150–300 physical LOC preferred, 350 physical LOC HARD MAXIMUM before tranche acceptance**.
- A short, cohesive file (<150) is fine; no artificial padding or function-per-file fragmentation.
- If an extracted file would exceed 350, partition by *genuinely distinct responsibilities* with single canonical owners first. Merely moving 2,000 lines into a newly named "service.py" is a FAIL.
- No circular owner->façade imports; no wildcard reexports, module __getattr__ magic, broad proxy hacks, second LLM/decision authority or duplicate source of truth to game LOC.
- Pre-existing oversized extracted Owner files are DEBT and must be subdivided by the appropriate stage before it is declared fully accepted. An oversized untouched frozen external package does not mandate off-scope surgery.
- A stable existing façade may exceed 350 temporarily ONLY when consumer/monkeypatch evidence proves wrapper retention necessary. Explicit KEEP/WRAPPER/MOVE/DEAD/SAFETY-LOCK ledger with caller and P1.5.10 removal status. Report size NOT MET, never pass a size waiver as achieved.
- **Executor sole ordering coordinator is the exception to the 350-line module hard cap**. Non-authority modules extracted from Executor must obey <=350. Safety sequencing remains in one auditable path; no new broker submitters.

Every slice must record physical LOC BEFORE/AFTER for façade and ALL new/extracted owners, symbol-to-Owner inventory, circular imports, imported compatibility symbols, targeted and broad test results, real-data output equality, authority/production-write leakage checks, independent Codex audit and UI-linked patch-note update. Temporary test paths must be session isolated, PASS cleaned, FAIL bounded. ZIP contains only changed paths.

## Quantified goals (aspirational, not production correctness promises)
Original six non-Executor façade groups design target: 2,700–5,100 total LOC, from original 53,657; extracted code survives elsewhere. Existing three Reporting façade files are ~3,039 / 3,043 / 948 LOC. Already extracted giant owners include sections.py 2,233, story_assembly.py 1,356, human_payloads.py 1,337, markdown_summary.py 1,275; these are NOT final small-owner PASS.

Executor execute_from_packet.py baseline ~4,189 LOC. Revised **interim** size band 2,600–3,200; **aspirational final** size band 1,200–1,800 if and only if strict safety equivalence is proven. If not achievable, record SIZE_DEFERRED or SAFETY_BLOCKED with the single ordering coordinator preserved; do not change authority to hit metrics.

Together eleven primary façade files would aspirationally total ~3,900–6,900 LOC, excluding intraday_monitor_signals.py. This is NOT total repository LOC reduction.

## Safety and handoff
No change to seven agents/topology, real entry/exit/rank/formula/prompts, cost_edge/stops/BTC/Q identifiers, P1.2 UEF frozen core/current/latest/registry and canonical COMPLETE, P1.3 Docker/2 GiB, Step5C CAS, Step5D recovery, immutable R6.2 readiness/current owner+generation, Supervisor authority, broker submit/UNKNOWN handling. No new Q/LLM role. Never replay real orders for testing. All P1.5 implementation from local C:\Agentra; GitHub refactor/p1.5 alone receives versioned commits; main only after final P1.5.11 full pytest/Docker/UEF/Codex/human acceptance.

Precedence: original v1.0 packets preserve historical intent and exact invariant order. New Reporting v1.2 and Executor v1.1 govern subsequent work. No baseline freeze is reopened for cosmetic refactor.
