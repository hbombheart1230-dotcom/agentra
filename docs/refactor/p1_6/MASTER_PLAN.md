# Agentra P1.6 — Identity, Architecture and Structural Pruning Master Plan

**Status: DESIGN CANDIDATE / NOT IMPLEMENTED (2026-10-30).** This plan captures the product-owner direction; all untested mechanisms are proposals, not assertions about existing functionality. Formal architecture freeze requires a separate P1.6 acceptance after P1.5 completion.

## 1. Why P1.6 exists

P1.5 mechanically restores module boundaries and existing behavior. **P1.6 then fixes the product identity and ownership boundaries, inventories every function, eliminates unnecessary runtime surface, and decides whether an orchestration framework genuinely helps.** Do not add another strategy framework, new agent or report pipeline before this simplification.

Identity: **Autonomous AI Quant Trading Desk** for Korean short-horizon trading. Target operating style: scalping to intraday and 2–3 day swing, around three simultaneous holdings. Long-term investing, passive buy-and-hold portfolio management and unrelated Agentco capabilities are outside this product. The position count and horizon are future policy targets, not silent live configuration edits.

The research philosophy remains brokerage-quant-like and AI-centered:
- Strategist studies global/Korean markets, regime, news, themes, hypotheses and trading playbooks.
- Scanner finds and ranks investable symbols **within strategy context**, but may challenge a weak theme and propose a new discovery for strategic review.
- Monitor watches candidate and position structure, timing, liquidity and exit; may autonomously propose a better entry/exit tactic and request re-evaluation.
- The default flow from market hypothesis to selected symbol to timing is meaningful **specialization**, not a reason to force every department to be called in a fixed serial cycle.

## 2. Seven departments: autonomous analysis, centralized investment choice

| Department | Accountable output | Autonomous scope | Forbidden authority |
|---|---|---|---|
| Commander | PortfolioDecision / research assignments | Independently investigates, challenges evidence, tasks others, resolves conflicts, chooses portfolio actions and resource budget | Bypass Supervisor, own broker mutation, silently alter immutable risk limits |
| Strategist | InvestmentThesis + proposed StrategyPolicy | Market regime, themes, playbooks, independent research and policy suggestions | Unreviewed account orders or changing hard risk rails |
| Scanner | RankedCandidateSet / candidate objections | Theme-bound quantitative selection; reject a weak theme; discover alternatives and request Strategist review | Execute order, redefine account risk, force a Top-1 trade |
| Monitor | TradeSetup / entry-exit objection | Continuous candidate/held-position monitoring; adaptive tactics and timing proposals; raise urgent hazards | Broker call or unapproved strategy mutation; override deterministic emergency protection |
| Supervisor | RiskDecision | Deterministic approval/deny/limits under frozen risk and guard contracts; optional advisory AI has no veto override | New investment thesis or safety-rule exemption |
| Executor | ExecutionResult / reconciliation evidence | Deterministic authorized order lifecycle with existing idempotency/UNKNOWN quarantine | New investment decisions, duplicate broker submissions |
| Reporter | Structured attribution + learning candidates | Independently diagnose failures/opportunity cost, flag findings and propose research tasks | Rewrite trade truth, independently alter production strategy or approve orders |

**Commander is a reasoning-based investment leader, not the entire low-level scheduler.** A separate runtime orchestrator owns clock/events, queueing, lifecycle, retries and state. Commander may initiate studies without waiting for other departments. Specialist opinions can disagree; retain dissent, evidence and provenance rather than forcing consensus.

**Two tempos:** AI research/planning is slower and event-driven; market observation/approved plan execution is fast and deterministic. Never require a fresh LLM answer at each scalping tick. A TradeMandate/PolicyVersion may define bounded opportunities and preauthorized conditions; proposed in-session policy updates must pass separate authorization and remain within hard risk rails. No hot deployment of changed Python into an active brokerage session.

## 3. Contracts and data authority

Future contract chain (names are conceptual, do not overwrite current DTOs before migration review):

1. InvestmentThesis — why this market/theme/playbook; confidence, evidence, horizon, expiry.
2. RankedCandidateSet — who to trade; rank, alternatives, rejection reasons, liquidity and source data.
3. TradeSetup — entry, invalidation, exit, risk and timing; may challenge an upstream thesis.
4. PortfolioDecision / TradeMandate — Commander accepts, rejects, defers or requests new research; bounded account allocation.
5. OrderIntent → Supervisor/Guard → Executor — existing protected execution authority unchanged.
6. ExecutionResult → Reporter → immutable evidence / reviewed learning candidate.

All causal records must retain run/proposal/intent identifiers, timestamp and point-in-time evidence lineage. Distinguish proposed/advisory values from effective approved values and runtime/broker truth. Future adapters migrate current inputs/outputs incrementally; never infer that M15 or a design document describes today's exact code.

## 4. Adaptive policy and model routing: design interfaces, not P1.6 rollouts

**Adaptive Policy:** current Strategist-to-Scanner/Monitor strategy-policy and weights are an asset. Separate immutable guard ceilings from candidate *bounded* weights, source policies, entry/exit heuristics and research recommendations. Version every policy with proposer, approving authority, market-regime context, permitted bounds, expiry, UEF/Q evidence and rollback reference. Scanner/Monitor may challenge or suggest adjustments. Adaptive weights and improved tactics must be shadow-tested before they influence live trading; no unconstrained real-time threshold optimization or modifying live positions without explicit policy review.

**Model Gateway:** provider-neutral task-specific routing across OpenRouter, direct OpenAI API and other approved providers. Retain a stable model registry/profile with structured-output validity, latency, timeout, reliability, cost and context limit evidence. Benchmark Agentra-specific tasks rather than choose on novelty alone; pin model/prompt/policy version per decision. Subscription/API benefits, pricing, quotas, authentication and model availability are external operational concerns, not hardcoded architectural assumptions. Codex development access and trading inference API are separate use cases. Never send account secrets to model providers.

**Experience:** Q9–Q18, Q10/11/12 variants, Opening Alpha, EOD reports, trade/skip/exit evidence and UEF results are valuable assets, **not** interchangeable, proven profitable strategies. UEF remains measurement/evaluation authority (including comparison limitations); Q100 is later research/knowledge authority and never recalculates UEF metrics. Design read-only retrieval across all reasoning departments, with provenance, known negative evidence, cohort, comparable status, context/horizon and sample quality. Initial narrow Reporter→Strategist feedback remains advisory. Do not mutate original records or promote weak/blocked evidence to an executable trading rule.

**Reporter:** make the machine-readable event/evaluation/evidence outputs durable; aggressively review duplicated human-facing narratives, per-trade prose, UI summaries and repeated LLM report generation. Human notifications default to operational risk, incidents, meaningful decisions and material experiment findings. Removing a presentation must not erase an underlying audit trail or Q100/UEF consumer.

## 5. Trading desk vs AI Engineering Lab

The Trading Desk may react during the day using **previously approved policies and bounded settings**. The Engineering Lab is out-of-band: independently analyzes failures and Q/UEF evidence, proposes strategy/weight/model/code improvements, runs replay/shadow evaluation and requests explicit promotion. A daily post-close experiment cycle is the initial candidate; no assumed promise of ongoing automation or unattended live deployment. A code editor or Codex never gets broker authority. Keep run-time service credentials and engineering write credentials separate.

This architecture defines seams now; P4 Q100/Reporter, P5 memory/Obsidian, P6 self-improvement and P7/P8 freeze/paper evidence activate the deeper capabilities on their existing roadmap. P2 remains owner of strategy program integration and P3 of later execution safety expansion. P1.6 must not preempt their implementation scopes.

## 6. Feature inventory and structural pruning

Prepare a versioned inventory **at accepted P1.5 freeze SHA**; cover actual imports/calls, runtime configuration, job/CI/RunLab, artifacts, tests, consumers and historical dependencies. For each runtime surface record:

- Feature/owner; implementation files; runtime mode and caller; tests; data owner; operational consumers; research/evidence consumers; security/guard/UEF dependencies; target future stage; fate; confidence and proof.
- Classification: **KEEP** essential and owned; **CONSOLIDATE** overlapping implementations; **REBUILD** essential but unsuitable boundary; **ARCHIVE** history/research not runtime; **DELETE** only proven dead/unreferenced functionality.
- Never equate “not called in one sampled run” with dead code. Check dynamically loaded modules, CLI, scheduled work, migration adapters, freeze manifests, plugin hooks and CI negative tests. Keep original artifacts and audit lineage.
- Every proposed deletion must show exact consumer map, removal impact, negative tests and rollback. Protected safety code, live-trading state, Q/UEF provenance and immutable reports are excluded from opportunistic pruning.

**Deliverable:** a single Feature Disposition Ledger in the P1.6 folder **after freeze**, not an additional packet for each feature. Do not create it prematurely or fill it with guessed inventory.

## 7. Phased decisions and outputs

| Gate | P1.6 work | Minimum output |
|---|---|---|
| A — P1.5 handoff | Accepted baseline SHA, live architecture map, callable role contracts and test/RunLab status | Verified freeze reference; unresolved gaps separately assigned |
| B — Identity/ownership | Owner-approved role boundaries, non-goals, autonomy and authorized policy changes | Frozen Identity + Architecture decision in this master plan or one ADR |
| C — Inventory/pruning | Complete caller/consumer evidence; classify and carefully remove redundant runtime code | Feature Disposition Ledger + verified deletion/rollback receipts |
| D — Framework decision | Benchmark **custom vs LangGraph vs pydantic-graph** for eligible read/decision workflows | Measured ADR: KEEP / ADOPT / DEFER; no winner preselected |
| E — P1.6 closure | No unintended behavior/safety/report/evidence changes; deterministic rollback | Independent tests + RunLab evidence + product-owner approval |

Original graph-spine state patch/deletion semantics, mode split, injection seams and test fixtures in archived files remain useful **hypotheses** to re-check at Gate D. Newly proposed autonomous collaborations are *future behavior capabilities*, not candidates for false exact-output parity against the old deterministic pipeline. First prove structural equivalence where needed; validate new behaviors separately in non-executing shadow experiments.

## 8. Scope and approval boundary

During active P1.5: **documentation consolidation only**. No P1.6 runtime changes, test execution, graph dependency changes, scheduled automation edits or prod strategy modification. P1.5 C01–C06 and RunLab follow their current contracts and continue without interruption.

After P1.5 freeze: conduct A→E with explicit scope approval, separate coding and independent test/review evidence, no production brokerage until all specified deployment/safety gates and owner approval. Existing D00, canonical execution owner/CAS, UEF frozen semantics, broker UNKNOWN and protected operational files retain their authority. P1.6 is complete only with verified evidence, not a signed design alone.
