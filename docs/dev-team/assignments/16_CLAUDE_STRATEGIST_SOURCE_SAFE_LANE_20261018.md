# Agentra P1.5 — Claude Developer Strategist S5 Closed-Scope Work Order (2026-10-18)

**Author:** GPT (architect, on-demand). **Status:** **APPROVED FOR CLAUDE DEVELOPER SOURCE WORK, strictly inside this closed set**. Supersedes earlier blanket S3–S6 "not yet authorized" solely for these EIGHT named S5 low-risk helper extractions. S3 mass target relocation, S4 module migration, other S5 or S6 ROLE_READY are NOT authorized. **Claude independent auditor is a DIFFERENT session** and owns review of Codex integrated candidate; do not duplicate that audit from this developer session.

## Verified source anchors; refresh actual live refs first

- Approved Strategist input source `integration/p15-t4-pr5-convergence-20261015` @ `d269c906ebadad75a0b833778ebc6a632a388e7c`; the earlier S1 study asserted `libs/graphs/apps/scripts/tests` unchanged from frozen BASE `d773709ba2f70471fad9badba4f92400f7818319`.
- Existing S1/S2 evidence branch `evidence/p15-strategist-s1-s2-20261017` @ `fcf79594728a345501cb81cfb868949507d912f1`; commit `402253a7e0d3dbcd40d4ab909ce1741939eaf3d6` contains evidence-only fixture repair.
- Reporter `work/reporter-role-20261017` @ `443f90362ad5970a4731685311a45e8e0f6b55e4`.
- Monitor `work/monitor-role-20261017` @ `4bc4250844093050438d8a9c29f5842991ad1c3a`.
- **Codex shared candidate is NOW AVAILABLE**, `integration/p15-monitor-shared-20261018` @ `95c11cacb9c73ae3d97d89e2061372762efff12b`, Issue #14. **Do not use its branch as a writer or edit its T3/T4/CI/shared tests.** It is assigned to separate Claude AUDITOR. Developer may read candidate mapping to foresee merge conflicts, nothing more.
- Issue #15 tracks future S2-F1 theme-strength ranking no-op. No behavior fix during P1.5.

## Developer branch and sandbox

Create `work/strategist-role-20261018` based on the verified `d269c906` source parent in a **new verified registered Agentra git worktree** under the already approved Agentra repository/worktree parent. Never change the existing Reporter, Strategist evidence, Monitor, Codex integration candidate or main worktrees. If the branch exists, inspect, do not overwrite. Always follow [15_P15_WORKSPACE_SANDBOX_POLICY_20261018.md](15_P15_WORKSPACE_SANDBOX_POLICY_20261018.md): exact writable checkout roots only, ignored session-scoped `.agentra-worktmp/<run-id>`, inherited Windows env, no broad permissions or profile/OS writes. Parent `C:\Agentra` or `C:\AgentraEvidence` is not blanket permission.

Read only:
- this order; [11 current policy](11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md);
- S1 classification ledger at `fcf79594`; [S1/S2 charter](13_STRATEGIST_S1_S2_SCOPED_CHARTER_20261017.md);
- `graphs/nodes/strategist_node.py` 8 target defs and their call sites, identified runtime owner imports; relevant T4-C and existing R3 facade tests.
Do not reread all Reporter/Monitor tasks or whole project history.

## Exact authorized source change set: EIGHT helper bodies only

These eight `graphs/nodes/strategist_node.py` definitions have an S1 `SAFE_MOVE_CANDIDATE` disposition, but each still requires actual proof:
- Numeric/value helpers: `_clamp`, `_to_float`, `_to_int`, `_round_optional`, `_unit_score`, `_is_trueish`.
- Text parsing helpers: `_strip_fenced_block`, `_parse_text_list_fragment`.

Goal: make thin **R3 facade wrappers** in `graphs/nodes/strategist_node.py` and place moved bodies in small purpose-specific bounded modules **within existing `libs/runtime/strategist` package**, avoiding any mass `libs/agents/strategist` relocation or new package-level identities. Prefer `libs/runtime/strategist/context/value_helpers.py` for numeric/value helpers and `libs/runtime/strategist/llm/text_fragment_helpers.py` for textual parsing, or another genuinely grounded current ownership module if it avoids duplicating semantics. Each owner <=350 physical lines. **Do not move preexisting other owners or alter schema, thresholds, output/LLM requests, trade policies, candidate ordering, truth priorities or run-time environment.**

Important R3 semantics: moved implementation must be byte-/AST-equivalent after substituting module globals with **use-time facade lookups**. E.g. `_unit_score` must resolve `facade._clamp` at EACH use, even if node `_clamp` is patched just before/mid-call; textual parser must preserve exact `facade.json`, `facade.ast`, `facade.re` alias/use-time behavior where those are public patch surfaces. No caching globals at import/entry time. Match signatures, annotations, exceptions, exception strings on the *same interpreter*, values, ordering, monkeypatch behavior and call counts. Preserve Python optimized-mode behavior; no `assert` as a security/authority guard.

### Bounded ordered packets — continue automatically inside this charter

**S5-A / smallest 2:** start with `_clamp` and `_to_float` only; add static exact BASE-body guard + runtime argument/exception/mutant tests and compatibility imports. Test normal and `python -O`. If they fail, narrow fix while within approved body/owner paths; don't adjust T4-C golden.

**S5-B / remaining value 4:** `_to_int`, `_round_optional`, `_unit_score`, `_is_trueish`. Require `_unit_score` facade-level monkeypatch test to prove call-time `_clamp` resolution; test before/mid-call rebinding, NaN/inf/None/invalid types where safely available, exception class/message stability per interpreter. Compare populated paths, not solely equal errors.

**S5-C / text 2:** `_strip_fenced_block`, `_parse_text_list_fragment`; preserve `json.loads`→`ast.literal_eval` order, `re.split` order, list/set iteration effects and unicode/newline semantics. Add strict same-function AST restoration + planted mutation cases. No prompt/LLM policy bytes changed.

**S5-D / integration-readiness proof:** run T4-C Strategist frozen whole-State/effects goldens, earlier S1-057 and pinned Wave B/C test subsets, exact own-body/scope guard and existing relevant user-facing tests, normal / -O. Distinguish `PASS`/`FAIL`/`NOT_RUN` and BASE known failures from new regressions. S1/S2 evidence test `test_analysed_source_is_the_pinned_base_for_libs_and_graphs` expressly asserts `libs/graphs` unchanged; it **must be run on its original evidence branch** as a frozen S1 provenance test, not copied into this changed-source branch and weakened to make it green. Use new **source-migration parity tests** on this branch. If a required shared gate needs a path mapping (T3/T4/CI), write a precise integration request in Issue #14; **Codex alone edits shared gates in its integration branch**. Do not mark integration PASS while this remains unverified.

**S5-E / bounded finish and relay:** Publish a SHA-bound checkpoint, touched-symbol ledger, commands/outputs, negative mutants and exact list of shared gate follow-ups on the Strategist source branch and optionally Issue #11. Correct the **proposal** UI note for a verified structural change only; actual UI-linked store is changed only by shared integrator to avoid branch conflict. Continue by preparing **read-only Commander/Orchestrator API/owner/test inventory** on another evidence-only branch if safe and useful after S5-D. This is a meaningful pre-authorized next lane, not an instruction to rewrite Commander source. No repeating S1/S2 full inventory.

### Never do the following

- Never merge into `main` or the Codex candidate, rewrite Git history, `git clean` other worktrees, change shared `.github/workflows`, T3/T4 or their historical frozen fixtures.
- No Broker, Kiwoom orders, Executor/Supervisor/Commander runtime authority, Q10/Q12, UEF, Step5C, real LLM/network/production writes, strategy rank/threshold/LLM requests or Agentco files.
- No relaxing tests, silent exclusions, mutating production data or dumping model/tool credentials.
- Do not wait for other-session independent audit to finish S5-A/B/C. Other Claude AUDITOR should review Codex `95c11cac` at its own exact SHA, and Codex continues integration separately.
- A session cannot run forever by written instruction alone; when capacity or approved queue is exhausted, checkpoint exact SHA and reason. Do not fabricate more authorized source migrations. User approval is required for broad S3/S4 or any policy/authority expansion.

## Developer output at each checkpoint

```
ACTOR=CLAUDE_DEVELOPER
ROLE=STRATEGIST_S5_SAFE_HELPERS
ACTIVE_BRANCH=<verified>
HEAD=<exact 40-char SHA>
DONE=S5-A|S5-B|S5-C|S5-D|S5-E
NEXT_READY=<specific permitted packet>
TESTS={PASS,FAIL,NOT_RUN with exact commands/interpreter}
SANDBOX_ROOT=<verified path>
SHARED_GATE_BLOCKERS=<precise file/contract, if any>
MAIN_MERGED=NO
LIVE_TRADING=NO
```

**Purpose:** keep Claude development productive on scoped physical modularization, independent of Codex shared integration and another Claude verification session, without asking user for per-packet approval.
