# P4 — Q100-1/2/3 + Reporter V2: Evaluation Architecture

Status: DESIGN ONLY. Q100 is research/evaluation infrastructure, **not** "another Q-numbered strategy" or replacement UEF.

## Scope / separation of already-defined Q100-1–6

The existing `docs/research/q100_research_and_learning_roadmap.md` defines:
- **Q100-1** Program Registry
- **Q100-2** Canonical Evidence Mapping
- **Q100-3** Reporter/Evaluator structured attribution
- **Q100-4** Knowledge & Memory Layer
- **Q100-5** Retrieval Layer
- **Q100-6** Self-Improvement Loop

To avoid building the same capability three times:
- **P2** owns *program identity/context plumbing* as an integration domain; **P4 Q100-1** is its research registry **read-model/analysis owner**, not a duplicate operational registry.
- **P4 owns Q100-1/2/3** and Reporter V2 attribution.
- **P5 owns Q100-4/5** and memory retrieval.
- **P6 owns Q100-6** and a bounded suggestion/review loop.
These are work-package scopes; they do not rewrite Q100's original stage numbering.

## Responsibility and proof chain

```text
P2 ProgramEntry ─┐
UEF canonical    ├─> Q100-1 Registry view + Q100-2 Evidence mapping
records VALID ───┘               |
                                 v
                            StrategyEvidence view (derived; NOT UEF authority)
                                 |
                            Reporter V2 / Q100-3:
                            structured attribution + uncertainty
                                 |
                    daily/weekly/monthly read-only outputs
                                 |
                             P5 memory candidate queue
```

**UEF-9 formal authority** is `VALID` only under its frozen binding or else throws. Q100 may not change UEF-7 normalized records, UEF-8 1:1 pair set, UEF-9 run/binding, identities/statuses or metrics. No new UEF-10. A `CONDITIONAL` pair is not promoted into `COMPARABLE` by Q100 text, and derived aggregates are never canonical records.

## Evaluation categories

| Attribution question | Required sources | Risks/controls |
|---|---|---|
| Strategist regime/scenario | pre-decision frame vs subsequent realized market context | look-ahead, macro data freshness, confounding |
| Scanner ranking | original ranked candidate set, rank1 vs actually selected, time-aligned quotes | selection bias, contaminated periods |
| Monitor timing | proposed entry/exit, hard guard and actual market timing | costs, missing minute data, horizon censoring |
| Supervisor and guard | proposed intent, allowed/blocked reason, risk context | "blocked" cannot be scored as lost profit without counterfactual specification |
| Executor quality | approved intent vs broker request/fill/unknown, latency, slippage | partial fills, retry/UNKNOWN and broker observation gaps |
| Regime/program edge | Q10/Q12/cohort + independent control + cost-adjusted outcome | multiple comparison, tiny N, overlapping sample, false edge |
| Retrieval usefulness (future P5/P6) | paired memory on/off context and held-out forward outcomes | causal leakage, LLM variance, duplicated trade authority |

Outcome attribution should distinguish descriptive decomposition from causal claims. A single trade losing money does not establish the Scanner or Strategist caused the loss; the model needs bounded counterfactual tests.

## Reporter V2 cadence (existing Architecture V2 vision)

**Daily**: event vs decision vs actual trade, Q-program occurrence count, incomplete evidence and next-day observation to verify.  
**Weekly**: recurrence, data completeness and independent program-specific controls, quality of Strategist frame/Scanner rank/Monitor timing, incident review.  
**Monthly**: strategy keep/watch/deprecate *proposals*, OOS findings, confidence/uncertainty, evidence trail, research debt (not autonomous live policy mutation).

The Reporter has a deterministic numeric truth core and an optional AI **interpretive** layer. An LLM may write summary/limitations, but cannot calculate a new authoritative PnL/UEF metric or change Supervisor/Executor. Keep narrative and measured facts separately labeled.

## Derived data contract

```text
AttributionReport
  report_version
  report_window / day/weekly/monthly
  program_id[] / hypothesis_id[] / cohort[]
  uef9_binding_run_id / source_record_ids[] / source_digest
  completeness / missingness / excluded_sessions[] / caveats
  descriptive_metrics[]           (read from UEF, never recomputed as authority)
  attribution_components[]         (method and uncertainty explicitly specified)
  incidents[] / control_lane_results[]
  interpretation[]                (human/LLM, NON-AUTHORITY)
  recommended_research_actions[]  (P6 candidate, not live change)
```

Conservation: every output record must point to source IDs; do not double count a case appearing in both a Q10 cohort and Opening Alpha. Ambiguous relationships get `OVERLAP_UNRESOLVED` and cannot be silently aggregated.

## P4 workstream sequence (architecture only)

1. Agree P2 program IDs/cohort/clock and accepted P3 Step6 boundary; no operational writer duplication.
2. Q100-1 expose research program lifecycle read view (include historical/blocked controls, not only KEEP).
3. Q100-2 bind immutable UEF-7/8/9 evidence with explicit source ref/quality; reject incomplete/invalid authority.
4. Q100-3 design deterministic attribution and controls; separate description from causal inference.
5. Reporter V2 map current daily/weekly/monthly outputs and artifact-compatible read model; preserve UI consumers.
6. Independent parity: old Reporter truth vs derived structured report, no new broker/model calls during tests.
7. Confirm outputs can feed P5 memory candidate **with provenance**; no memory activation here.

## Acceptance and negative cases

- UEF-9 invalid/mismatched → report BLOCKED/CANONICAL_UNAVAILABLE, no "partial-valid" claim.
- Same candidate included multiple source studies → dedup/related refs, not double edge.
- Missing expected fill or UNKNOWN order → report unknown outcome, not guessed PnL.
- Q11 negative control remains negative control, Q15 filter not alpha, Q18 evaluation consumer not independent origin.
- LLM narrative must never override metric sign or source digest.
- Legacy report ref labeled lower-trust; manual observation marked opinion.
- Missing comparable UEF pairs → do not invent pairwise superiority.

**Exit:** versioned attributed derived reports with explicit uncertainty, frozen-source parity, operator evidence and independent audit; P5 may ingest candidates only after P4 acceptance.
