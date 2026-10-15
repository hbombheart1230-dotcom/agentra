# P2 / 2.E6 — Strategy Program Integration Architecture

Status: ARCHITECTURE DESIGN ONLY. **No new alpha, parameter, score or live trade behavior** is approved here.

## Problem

Q-series research, context feeds and tactical signals accumulated as partly overlapping families. UEF-9 provides frozen evaluation authority, but **program integration sits on top of it**, not `UEF-10`. P1.5 separates Agent ownership and P1.6 will decide the graph harness; P2 must not rebuild Strategist/Scanner/Monitor, nor auto-promote a study into a trading signal.

## Domain boundaries (future logical components, no module-path commitment)

1. **Research Program Catalog** — identity, study family, cohort, hypothesis, status, control lane, source contract, evidence quality, window, ownership.
2. **Context Source Registry** — provenance/freshness for overnight U.S./SOX, Micron/NVIDIA, Korean indexes/stocks, BTC, JPY/FX, events. Never infer freshness from current price alone.
3. **Signal Projection** — immutable candidate `ProgramObservation`: program_id + pre-specified clock + signal direction/strength + status + methodology/version; NO OrderIntent.
4. **Strategy Selection Frame** — Strategist consumes only policy-eligible and quality-labeled context; an observation-only family stays read-only and cannot overwrite Commander policy or ranking.
5. **Scanner/Monitor Adapters** — allowed non-authoritative context hints (soft weights) only if an explicit accepted strategy policy enables; existing rank/hard timing guard authority unchanged by default.
6. **Program Evaluation Adapter** — references UEF record IDs, cost, cohorts, censoring and missingness; no parallel trade PnL recomputation.
7. **Operator Catalog Read View** — status/coverage/blocked reasons, independent of execution; human promotion workflow is separate.

## Program inventory snapshot and important exceptions

The historical `docs/research/research_portfolio_freeze_2026-09-16.md` describes **5 KEEP, 3 WATCH, 3 retained controls**, `EDGE_CONFIRMED=0` as of that date. This is not assumed to be today's live state; the future P2 baseline must read latest status from actual evidence. In particular:
- **Q10 Index** splits **SEMICONDUCTOR** vs **INDEX** cohorts; prior forward substudies F/G/H lack sufficient repeatable evidence. Treat U.S. index/SOX → Samsung/Hy­nix and KOSPI/KOSDAQ as hypotheses, never deterministic prediction.
- **Q12 Calc2 BTC→우리기술투자(041190)** is WATCH, subject to missing 08:55 BTC pre-open snapshots and clean forward-session count; a 24h breakout is not causation. Q12 Calc1 was not an independent hypothesis; Q12 Calc3 has documented source/timing blockers.
- **Opening Alpha** broad unconditional Rank-1 is DEPRECATE_REVIEW; only narrow conditional lanes are active review. Q11 is a negative control, Q15 a defensive selection filter, not a promoted alpha. Do not merge them into a profitable super-signal.
- **Q8→Q18 post-reclaim-pullback**: Q8 evidence underlies the hypothesis; Q18 is an **evaluation consumer**, not the primary alpha source. Preserve this identity.
- **JPY/FX**: add as a context/diagnostic source registry item with explicit timezone, pair, source, observation cutoff and missingness; it has no proven trading edge simply because it was added.
- Regime/overnight/macro are context discriminators. Demonstrating correlation is distinct from out-of-sample robust net edge.

## Context contract (conceptual)

```text
ProgramObservation
  program_id / hypothesis_id / cohort / methodology_version
  observed_session / as_of_utc / freshness / source_snapshots[]
  raw_signal_ref / signal_summary / confounders[]
  eligible_for: OBSERVE_ONLY | EVALUATE_ONLY | POLICY_REVIEW_REQUIRED
  uef_record_ref[] (if applicable; no fabricated reference)
  missingness / data_quality / status / reason_codes[]
```

An incoming source may be syntactically complete but economically stale or window-misaligned; treat completeness and credibility separately. No operator/UI copy changes eligibility by itself.

## Data-flow contract

```text
raw feeds & clock
 -> immutable captured SourceSnapshot + quality/freshness
 -> per-program hypothesis observation (never mutates trade state)
 -> morning Regime/Strategist Context Frame
 -> deterministic Scanner ranking / Monitor hard confirmation
 -> preserved baseline Supervisor & Executor
 -> UEF evidence (read-only from strategy registry)
 -> Reporter/Q100 downstream
```

The only bridge to live policy is a **future separately approved strategy policy change**, with replay/OOS, expected cost/slippage and operator gate. P2 cataloging is not such an approval.

## Cross-market clock requirements

| Family | Time rule / false inference to avoid |
|---|---|
| US / SOX / semiconductors | End of latest *completed* U.S. session in market-local calendar; label Korean next-session association and DST |
| KOSPI/KOSDAQ / Samsung / Hynix | Preserve open/gap/reaction vs actual local decision time; same symbol and source identity |
| BTC 24h/breakout / Woori | Frozen configured 08:55 capture cutoff, 24h window/endpoints, independent missingness; never fill after open |
| JPY FX | State whether JPY/KRW, USD/JPY or cross derived; source timestamp/holidays and conversion provenance |
| Overnight regime | Derive only from known-at-cutoff constituent snapshots; missing cells limit confidence |
| Opening conditional rank | Preserve canonical Scanner rank-1 vs actual selected runner-up and reason trace |

## P2 subphases (business/capability design, not filenames)

- **P2.A Catalog:** inventory existing program owners, co­horts, control vs alpha, freeze statuses and dependency/missingness; dedupe labels, keep historical IDs.
- **P2.B Context adapters:** source registry, snapshot-time truth, Korea/US/Japan/BTC calendar map, offline completeness tests.
- **P2.C Routing contract:** Strategist context frame → Scanner candidate hints → Monitor intent; no authority leakage, no new LLM role.
- **P2.D Evaluation projection:** map ProgramEntry/hypothesis to UEF binding plus per-program coverage diagnostics and negative controls; no metric recompute.
- **P2.E Policy governance:** observation→eligible research→shadow candidate→human promotion proposal with OOS, costs, risk. LIVE gate deferred and separate.
- **P2.F Acceptance:** reconciled P1.6 agent ABI, exact baseline output parity (unless explicit separate strategy change approved), UEF/cross-day and clock integrity, operator read-only visibility.

## Required tests/evidence (design specification)

- Schema/provenance negative: duplicate program/cohort, missing as_of, source and session mismatch, invalid symbol, clock DST, delayed 08:55 capture.
- Idempotent capture reference, canonical rank vs selected, already-blocked study cannot silently alter live policy.
- UEF binding VALID + pair identity/conservation; no unsafe synthetic "COMPARABLE".
- Confounded market scenarios / placebo/control / independent time splits for claims.
- End-to-end no new broker call, same Supervisor denial, no reporter/LLM model call explosion.
- Coverage/staleness/status displayed as evidence-quality constraints, not a green "strategy successful" dashboard.

**Exit:** agreed registry/context/dataflow ABI and quality guard proof, explicitly no live alpha claims. Only after accepted P1.6 decision and code audit can implementation owner/file names and test entrypoints be frozen.
