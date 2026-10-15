# P6 — Bounded Self-Improvement & Human-in-the-Loop Governance (Q100-6)

Status: DESIGN ONLY. Never infer permission for autonomous strategy authoring or production parameter mutation.

## Scope: Q100's seven-level maturity ladder

| Level | Description | Allowed under current program? |
|---|---|---|
| 1 | Manual review of experiments | YES |
| 2 | Structured Reporter attribution, human decides | YES after P4 |
| 3 | Advisory memory retrieval | YES after P5 |
| 4 | Guided research-status / policy suggestion, explicit human approval | TARGET |
| 5 | Bounded automatic **flagging** or Findings→Lesson promotion candidates under rules, **no trading mutation** | TARGET, additional audited controls |
| 6 | Autonomous strategy-parameter tuning | **OUT OF SCOPE** |
| 7 | Autonomous strategy authorship/retirement | **OUT OF SCOPE** |

Do not redefine Levels 6–7 as "future defaults"; they are documented prohibited scope. Self-improvement in P6 means **improve recommendations, evaluation quality and research status governance**, not autonomously trade differently.

## Closed evaluation feedback loop (human bounded)

```text
P2 Program Status / hypothesis
      ↓
P4 verified UEF-derived evaluation and reasoned findings
      ↓
P5 validated memory (+ negative evidence / caveats)
      ↓
P6 suggestion engine (deterministic gating; optional Reporter explanation)
      ↓
[HUMAN review: APPROVE / REJECT / REQUEST_MORE_EVIDENCE]
      ↓
Research registry status change or future experiment proposal
      ↓
New independent evaluation window — never retroactively relabel old evidence
```

Research status changes and actual **live trading promotion** must use separate authority gates. `KEEP/WATCH/DEPRECATE_REVIEW` are research governance statuses, not orders, profitability proof or permission to change position sizing.

## Suggestion contract

```text
ImprovementProposal
  proposal_id, source_program_id, current_research_status,
  recommendation_type: REVIEW | FLAG | CONTINUE_OBSERVATION | DEPRECATE_REVIEW,
  source_uef_binding_ids[], source_evaluation_record_ids[],
  observed_metric_refs[], uncertainty/cost, historical_control_refs[],
  confounders[], independent_validation, quality_exclusions[],
  proposed_next_experiment, evidence_cutoff, expires_at,
  author: reporter_deterministic | reporter_ai_review | human,
  approval_required, decision_status, approved_by, decided_at, audit_reason
```

This is a conceptual DTO, **not** a runnable patch to program status or Settings. If no independent, data-quality-verified metric evidence exists → `REQUEST_MORE_EVIDENCE` with no promotion recommendation. A weak sample or only conditional pair should yield an appropriately limited claim.

## Governance separation

- **Evaluation Authority:** UEF immutable truth. P6 read-only.
- **Research Authority:** human-approved lifecycle changes with audit; bounded Level-5 auto flags may only create a queue item.
- **Trading Policy Authority:** explicit, separately approved release/config/change window after dedicated safety and causal proof — **not P6 automatic output**.
- **Broker Authority:** Supervisor/Executor/Step5C/Step6; never P6.

A model-produced proposal cannot directly modify strategy weights, risk limits, prompts used in live trading, live switches, executable code, timers, order queues or claims. Human approval of a *research status* is not implicit authorization to deploy a new strategy.

## Evidence requirements and safeguards

- Paired/same-window controls where feasible; forward held-out/OOS, not training/evaluation on the same episodes. Pre-register metric and hypotheses.
- Decompose source validity, actual realized outcome, costs and attribution uncertainty. Repeated logging of same underlying episode does not increase N.
- Include negative-control lanes (Q11, etc.), invalid/UNKNOWN outcomes, coverage thresholds and contamination periods.
- Track candidate selection and multiple-hypothesis testing; positive-only lesson promotion is unacceptable.
- Keep a proposal register with idempotent approvals and full decision reasons; orphaned/expired candidate cannot be accepted silently.
- Bound proposal rate and LLM token budget; operators can pause/revoke suggestions without touching live market safety.
- Treat malformed, stale or contradictory memory inputs as untrusted. Reviewer can downgrade/reject a Lesson and keep reproducible history.

## Metrics for P6 maturity

Precision/recall of recommended research reviews versus independent expert outcomes, false promotions/retractions, evidence volume, operator time, calibration, future study completion, data quality, retrieval-use delta, LLM/cost budget. Profitability/causal claims require formal P8 experimental controls; P6 cannot claim edge improvement from raw before/after PnL.

## Acceptance

Level 4: 100% human-approved status changes, independent replay and unchanged trading policy.  
Level 5: bounded flag generation and knowledge candidate proposal, no auto live effects, stop/revoke proof, high-quality provenance, independent audit.  
Level 6/7: not implemented or planned for implementation in this program.

**Exit:** controlled research-learning governance with proven zero live-mutation authority. Any later autonomous trading roadmap is a *different*, expressly authorized program.
