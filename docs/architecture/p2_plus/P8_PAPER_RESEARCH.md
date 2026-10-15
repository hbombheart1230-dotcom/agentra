# P8 — Paper / Stable-Data Experimental Architecture

Status: EARLY RESEARCH PROTOCOL DESIGN ONLY. No papers written, results generated or research claims verified by this preparation.

## 1. Scope and contribution candidates

The scientific question is **not** "did an automatic trading bot make money?" but whether a verifiably safe seven-role Agentra harness offers measurably better decisions/evaluation/reliability under controlled market-data and program evidence.

Proposed separable research questions:

- **RQ1 — Orchestration correctness/engineering**: Does custom vs LangGraph vs pydantic-graph change reproducibility, human maintenance or error handling under identical frozen agent behavior? (Use P1.6 offline benchmark; no spurious profit attribution to framework.)
- **RQ2 — Cross-market context utility**: Do separately clock-correct Q10 US/SOX, Q12 BTC, JPY and domestic regime context improve *out-of-sample discrimination/calibration* over domestic-only controls? Conditional on sufficient fresh samples.
- **RQ3 — Evaluation integrity**: Does UEF-authoritative Q100 attribution reduce false promotion decisions versus fragmented unversioned heuristic research under blinded controls?
- **RQ4 — Memory usefulness**: Do provenance-filtered, retrieved Lessons improve Strategist reasoning/evaluation vs memory-off controls without safety side effects?
- **RQ5 — Safety/reliability**: How effectively do Step5B/C/D/E/6 and the deterministic harness prevent duplicate/unknown broker mutations or unsafe restart when faults occur? This is a safety engineering study, not live fault injection on a funded account.

Choose **one primary research contribution** after reviewing dataset availability and target venue. Others can become supporting studies, not five unconnected claimed breakthroughs.

## 2. Experimental unit / data sources

An episode must record `event_time`, `information_cutoff`, `cohort/hypothesis`, `market/regime`, `candidate/decision/order outcome`, `source freshness and content hash`, UEF binding, and the applicable cost/horizon profile.

Unit alternatives: trading session/day, symbol×day, opportunity episode, candidate pair, order intent, failure scenario. Correlated episodes from a common trading day are **not independent N**; use grouping/blocking by date and program as appropriate.

Build an immutable dataset manifest under P8's future approved environment, not on this design-only branch. It must specify source license/privacy, hashes, exact KST/US/JP exchange session rules, run/source code SHA, dedup method, exclusion log, contaminations, missingness, and evaluator version. Step5C/UEF original DBs remain operational truth, not a sandbox to mutate.

## 3. Pre-registered design and controls

- **Temporal split**: train/design, validation, strictly held-out prospective test; embargo adjacent overlapping return horizons and aligned duplicate event windows. Never select thresholds after inspecting test returns.
- **Arms**: baseline domestic/regime-only, plus US/SOX, plus BTC, plus JPY, plus combined context *only where supported and data complete*. Control for market beta, time of day, liquidity, data freshness, transaction costs and holidays.
- **Ablation**: Strategist with/without specific context source; memory off/on using identical deterministic candidate input; graph-engine swap with frozen synthetic/deterministic Agent callbacks; guard policies never disabled in real execution.
- **Negative controls**: Q11 and predefined null/shifted signals; document false-positive rates and multiple comparisons.
- **Outcome**: primary predeclared metric (e.g. opportunity directional discrimination or error/calibration) chosen with measurable coverage. Cost-adjusted trade PnL, drawdown, slippage, latency, selection quality secondary under explicitly supported sources.
- **Uncertainty**: confidence intervals, block bootstrap by day if needed, effect-size not p-value only, predefined minimum sample / independence threshold, sensitivity to exclusions/freshness.
- **Bias/contamination**: controlled mock date windows with rank contamination excluded or separately flagged; broker partial/UNKNOWN fills censored rather than mislabeled; data captured after cutoff cannot be retroactively used.
- **Reproducibility**: pinned code/deps/seeds, deterministic no-live replay, full manifest/source references, ablation scripts, independent replication after initial validation.

No specific performance lift is asserted by this design. As of the 2026-09-16 research-portfolio snapshot, `EDGE_CONFIRMED=0`; more data or repairs may be needed before any edge/causal claim.

## 4. Design now vs empirical evidence later

**Can do now in parallel with P1.5:** research question choice, hypothesis/variable definitions, planned controls, immutable schema design, dataset quality inventory, statistical analysis plan, negative-control specification, related-work search, chapter structure.

**May do with existing safe production-approved capture:** continue unmodified read-only research evidence collection where already configured and allowed. Do not modify collection, live prompts, trading policy or production writes through a planning branch.

**Must wait until P7 stable:** headline cross-system empirical findings based on accepted full pipeline, final reproducible splits/hashes, safety claims requiring integrated freeze proof, final manuscript figures/tables and claimed generalization.

## 5. Paper artifact layout (proposal only)

```text
Research protocol
├ hypotheses and preregistration
├ data contracts and eligibility
├ controls / negative controls / ablations
├ metrics / sample power feasibility / uncertainty
├ freeze SHA / dataset manifest / fixed artifacts
├ independently reproduced results
└ limitations / threats to validity / reproducibility statement

Manuscript
├ abstract & research question
├ prior work (orchestration, trading agents, provenance, evaluation)
├ architecture and seven-role/authority model
├ dataset / UEF-backed methodology
├ controlled experiments, ablations and negative tests
├ results + effect sizes / uncertainty
├ threats to validity, operational risks, privacy
└ reproducibility and conclusion
```

## 6. Acceptance gates

- Actual P7 accepted frozen code, safe benchmark/evaluation fixtures, ethical/safe data handling.
- Valid UEF binding, no duplicated candidate/order evidence, source time cuts validated.
- Controlled baseline and treatment with no look-ahead, no post-hoc cherry-picking, negative controls.
- Appropriate confidence/independence accounting, no “this proves profit” from conditional/underpowered cohorts.
- Independent statistical audit; another reviewer reproduces main results from approved immutable manifest.
- Any null/negative result is reported without changing the pre-registered question silently.

**P8 success** can be a rigorous *systems safety/reproducibility* paper even if alpha edge is not confirmed. Scientific truth outranks positive-looking trading performance.
