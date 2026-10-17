# Agentra P1.5 Reporter — whole-role continuous refactor

**Assignment:** Reporter entire role, not merely 12 relocated modules.  
**Existing worker branch:** work/reporter-role-20261017  
**Observed branch HEAD (2026-10-17):** d17d33c0c0e7b789b320b872eb386184fd6ce357  
**Runtime base cited in prior work order:** d773709ba2f70471fad9badba4f92400f7818319 (verify ancestry before using).  
**Integration policy:** no merger into main until the complete P1.5 refactor has passed integration gates.

## 1. Verified repository anchors

The following real files were read on the Reporter branch:

- libs/reporting/trade_story_pipeline.py
- tests/test_p152_facade_symbol_ledger.py
- tests/test_p152_facade_abi_and_authority_boundary.py
- tests/test_p152_r3_moved_bodies.py

The historic ledger file is docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json. Historical ABI test pins BASE **52508ade9d0d246fa4e848525fe62f2fe067acb7**; moved-body test pins R3 **ba6618d483e6d617f4ee56b2cb5647392c777071**. Do not alter historical pins to make a new HEAD pass.

The existing R3 moved-body test checks dynamic facade global resolution, AST equivalence after qualification reversal, no eager callable snapshots, no unresolved globals, owners <=350 LOC, and no owner importing a facade. Reuse this pattern where semantically valid rather than moving AST bodies blindly.

**Inventory starting observations from preceding work (NOT independently re-counted here):** ~500 Python files in libs/reporting, ~85 under libs/reporting/trade_report, three facade sizes: trade_story_pipeline.py ~498 lines; trade_report_markdown_clean.py ~1,325 lines; trade_report_ai.py ~1,656 lines; previous R3 ~141 owner moves. Recount at actual HEAD and record actual values before claiming completion. Do not presume all 500 are Reporter-owned.

## 2. Ownership taxonomy (required per file and function)

Classify each symbol as:

- REPORTER_CANONICAL: Reporter-owned implementation should move to canonical owner.
- REPORTER_FACADE: stable compatibility/export/orchestration shell (may intentionally remain).
- SHARED_CONTRACT: DTO, stable formatter, common read model with cross-role consumers; do not steal.
- RESEARCH_EVALUATION: experiments/backtests/evidence review rather than runtime Reporter.
- OPS_SCHEDULER: lifecycle, jobs, CLI, deployment; inventory consumers without changing execution.
- EXTERNAL_AUTHORITY: broker, Supervisor, Executor, trading decisions; forbidden scope.
- DUPLICATE_CANDIDATE: prove replacement/retirement safety; **do not remove under this order**.
- BLOCKED_WITH_PROOF: exact missing capability, importer/patch semantics, or cross-role dependency.

Inventory fields: old path, symbol/signature, purpose, static and dynamic importers, runtime producer/consumer, monkeypatch/global references, current owner, proposed owner, source tests, status, proof SHA, next action. Track **all** 85 trade_report files and the three facades, plus relevant adjacent Reporter files. For all other libs/reporting modules, count/classify by responsible subsystem; deep-dive only if Reporter-owned or a dependency.

## 3. Internal execution waves — run continuously

| Wave | Scope | Exit proof | If blocked |
|---|---|---|---|
| RP0 | Freeze HEAD, map importers, enumerate file/symbol ownership, baseline focused tests | Versioned current-head inventory; baseline metrics and NOT_RUN reasons | Investigate adjacent safe modules |
| RP1 | Distinguish pinned historical ledgers from current-head rules, add strict additive tests | Pinned tests unchanged; new current-head ownership/parity negative tests | Work on independent pure functions |
| RP2 | trade_story_pipeline facade + trade_story_facade_parts | Live-global references, byte/story contract, exceptions, facade ABI | Skip unsafe symbol, log precise proof, continue |
| RP3 | trade_report_markdown_clean facade (format/narrative/read-model) | Exact Markdown bytes/order/escaping; before/mid-call patches | Continue safe deterministic helpers |
| RP4 | trade_report_ai facade deterministic input/projection/output builders | Deterministic report parity; LLM execution/retry/router/cost/write untouched | Continue read-model/formatters |
| RP5 | trade_read_model, trade_memory projections, compact input and related safe parts | JSON keys/order, default semantics, side-effect boundaries | Move to producer-consumer inventory |
| RP6 | 85-file subtree audit and necessary canonical ownership moves; shared/research/ops excluded | Every file disposition with evidence; no bulk move of unrelated files | Mark exact dependency |
| RP7 | producers/consumers/schedulers/duplicates, output paths, UI-connected patch notes | Dependency map, no deletion/disable, report output contract tests | Document unapproved changes separately |
| RP8 | role-wide targeted/broader tests, negative guards, new owner/facade LOC statistics, handoff | Role-ready SHA, remaining justified facade shells, ZIP only changed files, independent audit request | Blocked-only if all safe authorized work exhausted |

Run RP waves by dependencies; parallelize independent RP5/RP6 when feasible. Commits are recovery points, not final reports. Each wave may contain many internal commits. **Never stop and await Work/Codex after RP2 or a single small batch.**

## 4. Implementation rules

1. Define a symbol-level refactor, not a simple directory relocation.
2. Preserve public exports, signatures, decorator behavior, original facade call sites, exceptions, aliases, callbacks, and function-object identity where tests/consumers rely on it.
3. For moved implementations, resolve former facade globals **at use time**, including monkeypatch applied before-call **and** during callback/mid-call. Avoid import-time captured callable snapshots.
4. Assess change in global namespace and closures; source AST similarity alone is not enough.
5. Respect owner <=350 physical LOC where the existing R3 test requires it; do not game LOC with obscure one-liners.
6. Keep historical facade ledger contract and pinned SHA semantics immutable. Add a distinct current-head ownership ledger/test; do not delete assertions, add skip, or downgrade to broad exclusions.
7. Use explicit runtime parity fixtures for pure Markdown/JSON and failure-path tests for AI facade. Preserve output bytes where exact fixtures exist; characterize non-deterministic/LLM paths as mock-only.
8. Do not modify real LLM execution, retries, routing, token/cost budgets, report writes, truth-source precedence, real order path, or risk/guard behavior.
9. UI patch notes: locate the actual connected patch-note source and update it for user-visible changes; if not located, record evidence and a precise integration request. Do not claim an arbitrary new note is UI-connected.
10. No mass tests/artifact accumulation in repo; successes cleaned, failure evidence retained within bounded ignored storage.
11. Keep consumer-facing compatibility wrappers if needed; completion means proven responsibility transfer, **not zero-line legacy facades**.

## 5. Proof matrix

| Contract | Required evidence |
|---|---|
| Historical ABI | Exact current test execution, pinned assertions unchanged |
| Name/signature/export | Existing facade ABI test + current-head public API test |
| Dynamic facade resolution | Monkeypatch before call and within callback/mid-call |
| Semantic parity | Changed bodies vs pinned R3 where applicable; inputs/output/exception fixtures |
| Rendered reports | Byte parity Markdown/JSON with deterministic fixtures |
| Side effects | No new file/network/broker/LLM calls; mocked/guarded pathways |
| Authority | No execution approval, guard, broker, trade-policy mutation |
| Ownership | Complete file+symbol inventory with canonical owner and evidence |
| Regression | Focused tests per batch; broader role suite at RP8 |
| Change surface | Changed-path audit, reasoned approval for shared tests |
| Patches | UI-connected notes updated or explicit limitation documented |

Test examples (discover exact environment first): python -m pytest -q tests/test_p152_facade_symbol_ledger.py tests/test_p152_facade_abi_and_authority_boundary.py tests/test_p152_r3_moved_bodies.py. These are **commands to attempt**, not evidence of PASS.

## 6. Done means ROLE_READY, not subset-complete

RP0–RP8 covered with explicit disposition of every in-scope file; movable logic relocated and equivalence checked; facade LOC and remaining wrappers documented; all active tests PASS, or each FAIL/NOT_RUN characterized; UI note state documented; final SHA + changed-file-only ZIP prepared; independent Codex audit requested for the final SHA. Main stays untouched. This is the *only* default terminal state for the whole-role work order.

If credits/context/session actually end: push a checkpoint and issue comment with final SHA, next READY batch and blockers; the external runner (if configured) or next manually initiated CLI must resume from that point, without re-reading completed work or repeating entire test history.
