# Agentra P1.5 Fast Track — first pass across all stages

**Authority:** user direction 2026-10-12: complete the first structural pass from P1.5.2 through P1.5.11 quickly, then revisit remaining large modules for deeper cleanup. This is a **workflow/stage-transition addendum**, not a change to trading, LLM, safety, Docker, UEF or release authority.
**Development:** ONLY `refactor/p1.5`, isolated clones, `main` frozen, live `C:\Agentra` and dirty Q12 worktrees untouched. Claude implementation → Codex independent wave audit → GPT/user final acceptance. No concurrent writes to the same files.

## New goal: breadth-first responsibility decomposition
- **FIRST PASS:** restore canonical responsibility Owners, bounded ≤350 physical LOC for every new/extracted Owner, explicit agent input/output/state adapters and safe compatibility boundaries across P1.5.2–P1.5.10. Preserve all existing behavior, public API/monkeypatch seams, safety/approval/execution ordering.
- **SECOND PASS (debt sprint):** return to oversized façades, numbered Owners, proven dead/duplicate wrappers, naming debt and extra LOC only AFTER broad first-pass coverage. A size waiver is never a statement that the file is optimized.
- **FINAL GATE:** P1.5.11 whole-regression + real provenance parity where required + Docker mock + UEF + zero production write/authority leakage + independent audit and GPT/user explicit freeze/merge approval. Never label unverified items PASS.
- **P1.6:** design benchmark/fixtures may be prepared during P1.5; runtime shadow implementation/graph comparison begins only AFTER accepted P1.5 freeze. No preemptive LangGraph migration.

## Waves (not one-Codex-audit-per-100-lines)
| Wave | Sequential structural first-pass scope | Wave audit |
|---|---|---|
| **A** | P1.5.2 Reporting residual low-risk extraction; P1.5.3 Operator UI/Brief read-model & presentation boundaries | One independent Codex diff+gate audit after all low-risk slices in A |
| **B** | P1.5.4 Strategist; P1.5.5 Scanner; P1.5.6 Monitor: contract / pure policy / state adapters, preserve role and timing | One independent wave audit, **plus immediate isolated guard tests per high-risk boundary** |
| **C** | P1.5.7 Commander; P1.5.8 naming aliases; P1.5.9 Executor **only genuinely pure observability/read projections**; P1.5.10 proven wrapper cleanup, otherwise retain | One independent wave audit; mandatory separate hard authority checks for any Executor-adjacent change |
| **D** | P1.5.11 test conservation, full regression, mock Docker, UEF replay/cross-day invariants, evidence matrix, fix/blocker decisions | Formal full acceptance; may FAIL/BLOCK |
| **NEXT** | P1.6 benchmark current runtime vs LangGraph 1.x vs pydantic-graph without production mutation | Post-freeze shadow evaluation |

## Preauthorized transitions (user already approved first-pass sequencing)
- The user preauthorizes **low-risk structural work** in waves A–C on the single refactor branch. An individual stage can advance to the next stage within the **same wave** after its mandatory focused gates pass, without a separate GPT chat approval. Codex independently audits a pinned SHA at each wave boundary. A PASS or PASS_WITH_FINDINGS **with only nonblocking findings** can authorize the next already-scoped wave after its evidence is recorded; unresolved critical findings STOP the affected path.
- **FIRST_PASS_WITH_DEBT** means structural work recorded, mandatory focused gates PASS, debt explicitly tracked; it is **NOT** FINAL_ACCEPTED / production ready / green for real data. **BLOCKED** means even first-pass safety requirements not demonstrated and no automatic next-stage change that depends on the failing surface. **FINAL_ACCEPTED** is reserved for P1.5.11 evidence and explicit GPT/user authorization.
- Do not allow an unknown trading-output, approval/broker, CAS/idempotency, Q10/Q12/UEF/Step5/R6.2 safety regression, import/ABI regression or **new production-write leakage** to be deferred. Stop that change and report. Every changed stage needs isolated mock/contract/ABI/import/tests, preservation of historical scenarios and an actual 0-production-write audit BEFORE progressing.
- A documented pre-existing unblocked-by-the-change failure may remain OPEN in the cross-stage ledger but cannot be misrepresented as passing the final P1.5.11 gate. Re-run high-risk focused tests immediately; run expensive full-suite/Docker cross-system acceptance once at D unless a scoped regression forces earlier testing.
- **No forced giant-file LOC target by source packing or fake delegations.** At first pass, prioritize independent callable components and one canonical Owner. Record BEFORE/AFTER LOC, size debt and a second-pass candidate; don't burn multiple cycles squeezing small deltas from the same façade. Keep legacy compatibility wrappers without speculative deletion.

## Stage-specific protection
- P1.5.2: real frozen reports/LLM prompt/retry/timeout/call-count parity **BLOCKED/NOT RUN** pending genuine immutable copies; `controlled_mock_lanes` native full-suite write-isolation finding OPEN. 436 Reporting ABI names and 86 moved bodies survive.
- P1.5.3: Brief truth/source and artifact version, persistence authority, API routes and UI/JSON unchanged; allow pure UI read/format moves, no report truth recomputation.
- P1.5.4: Strategist keeps its sole allowed decision LLM role; never change prompt/model/call count/retry/timeout, strategy outputs or trading decision semantics.
- P1.5.5 Scanner rank/selection conservation and soft guidance authority stays; no new Monitor hard timing.
- P1.5.6 Monitor remains intent-only (no broker); entry/exit/stop/risk order preserved.
- P1.5.7 Commander no new LLM; runtime routing, orchestration, checks and state sequence preserved.
- P1.5.8 historical names remain in historical docs/evidence; active runtime alias migration needs exact old/new consumer proof.
- P1.5.9 Executor mutation chain stays ONE owned coordinator, no Step5C/D, Supervisor/BrokerOutcome/UNKNOWN/R6.2/UEF semantic changes. Skip or mark SAFETY_BLOCKED any unsafe size work.
- P1.5.10 delete wrappers ONLY with confirmed dynamic/static/test/CLI consumers, monkeypatch and runtime proof; unknown usage means retain.
- P1.5.11 cannot pass while real truth/LLM parity or test write-safety acceptance remains BLOCKED. No main merge, production deployment or P1.6 runtime until explicitly authorized.

## Reporting and artifact discipline
- Update **both** UI-linked patch notes JSON and MD and short daily patch per integrated wave or meaningful code change; only changed paths in downloadable ZIP (for enormous patch-note files, separate append/delta is acceptable with Git canonical full files).
- Single active `CURRENT.md`, concise SHA/changed paths/test counts/debt ledger; no rerunning or rereading completed history. No fabricated fixture parity, no loosening tests, no unresolved 350+ new Owner, no unbounded pytest artifacts.
- At a wave boundary, Codex audits the **aggregated pinned diff**, not each trivial extraction; if a high-risk change is proposed, isolate it and require immediate independent review or defer to second pass.
