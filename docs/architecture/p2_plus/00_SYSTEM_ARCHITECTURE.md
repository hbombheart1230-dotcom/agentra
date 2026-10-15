# Architecture V2 — Framework-Neutral End-to-End Design

Status: **PROPOSED ARCHITECTURE ONLY**. This consolidates existing `architecture_v2.md`/Q100/UEF ideas; it does not supersede frozen code or canonical evaluation.

## A. End-state intent

Agentra retains **exactly seven specialized roles** and builds a research/evaluation/advisory layer *around*, not inside, the trading authority path. More agents ≠ higher quality; stronger contracts, controlled context, deterministic harness, durable evidence and measurable feedback do.

```text
Outside influences: global overnight (US/SOX/NVIDIA/Micron), KR index, BTC, JPY/FX,
                    Kiwoom quote/order/account, exchange calendars, news
                   |
         [source adapters / snapshot clock / data quality]
                   | (immutable, provenance-marked observation)
                   v
          [Market & Regime Context] <── [Strategy Program Registry / Q10 Q12 etc.]
                   |
            Commander [deterministic routing; P1.6 engine adapter is optional]
                   |
              Strategist [LLM allowed only within existing, gated scope]
                   v
              Scanner [deterministic candidate filtering + rank]
                   v
              Monitor [timing / position policy; OrderIntent or NOOP]
                   v
      Supervisor / Approval / Risk [deterministic, fail closed]
                   v
       Executor [sole broker mutation owner + Step5B/C/D/E guards]
                   v
               Kiwoom Broker
                   |
          Operational Truth Ledger (SQLite / event log; canonical owner)
                   |                    |
                   v                    └────> UEF-7/8/9 (evaluation authority)
           Reporter / Evaluator                   |
                |                                  v
        Structured attribution <─────> Q100 Program / StrategyEvidence read models
                |
           Curated findings/lessons → Knowledge/Experience (advisory only)
                                               |
                                   context-selective retrieval
                                               |
                                        Strategist future inputs
```

**This is a conceptual logical flow**. The actual `graph_spine` is different from production `integrated_chain`; paths, concurrency and code-level signatures are left to the P1.5/P1.6 freeze audits. Conceptual diagram does not authorize an LLM to call a broker or memory to emit a trade.

## B. Role responsibility / permissions

| Role | Single responsibility | LLM decisions | Forbidden |
|---|---|---|---|
| Commander | market-phase, route/stop/retry, config and state binding; deterministic orchestration | None | stock selection as authority; broker mutation |
| Strategist | market regime, scenarios, strategy frame and hypothesis context | Existing Strategist scope only | direct approval, trusted execution order |
| Scanner | candidates, data quality, rank/evidence, score breakdown | None for canonical decision | transforming rank into authority; execution |
| Monitor | position/symbol timing, enter/hold/exit intent or NOOP | None for canonical guards | placing/cancelling orders directly |
| Supervisor | approval/risk/deny; guard policy | None | ownership or broker mutation |
| Executor | authorized durable mutation and broker outcome handling | None | bypassing Supervisor, CAS, UNKNOWN quarantine |
| Reporter | read-only reporting, attribution and optional model-aided narrative/curation | Existing Reporter scope only | rewriting UEF measurements, changing a live strategy |
 
Existing source mismatch: older normative docs mention Supervisor `modify`, while source `Supervisor.allow()` is `allow/reason/details` per `docs/architecture/architecture_v2.md`. New Supervisor `modify` is **not** assumed to exist or implied by this architecture.

## C. Six conceptual concerns; separate authorities

1. **Operational Truth**: broker snapshots, canonical SQLite admission/claims and append-only event provenance. Side-effect authority remains execution layer only.
2. **Evaluation Truth**: frozen UEF-7 candidate, UEF-8 pairwise and UEF-9 binding. Q100 reads but does not recompute. Current status counts are evidence snapshots, not constants.
3. **Market/Strategy Context**: read-only published time-indexed snapshots, strategy program catalog, live-eligible policy only through explicit human-approved deployment gate.
4. **Knowledge**: evidence-linked, curated ExperienceRecord/Lesson; *never* an operational or evaluation authority.
5. **Reasoning/Reporting**: Strategist and Reporter, controlled LLM input/output, evaluation and retrieval. Memory remains optional and advisory.
6. **Execution Safety/Operations**: deterministic approval/guards, single owner lease, Step5B/C→5D/5E→Step6, Docker/host scheduler, incident/recovery controls.

Architecture V2's original six-layer nomenclature remains normative background. This document groups concerns for workstream ownership, **not** a replacement of its Layer 1–6 numbering.

## D. Read flow vs control flow vs proof flow

- **Read/data**: SourceSnapshot → ContextFrame → StrategistFrame → CandidateSet → IntentProposal; every transformation retains `as_of`, source/quality and origin.
- **Control/authority**: human-approved strategy policy → Commander → deterministic intent → Supervisor/guards → unique Executor claim → broker. A report or research score does not link back to this chain as authority.
- **Proof**: run/intent/event/experiment → frozen evaluation records → Q100 attribution → candidate lesson → optional retrieval with explicit `memory_used` trace. A failed or missing link is marked MISSING/BLOCKED, never imputed by an LLM.

## E. Market time and data quality as cross-cutting architecture

Normalize `observed_at` (market local), `captured_at` (system clock), `as_of` (information available to decision), `valid_for_session`, source timezone, market-calendar session label, and data freshness. Prevent a 09:00 Korean trading signal from consuming data captured at 09:05 and calling it pre-open. U.S. overnight session is mapped explicitly to next Korean market day; BTC 24h and JPY snapshots require independent timestamp provenance.

Missing/stale/conflicting data → UNKNOWN/NOT_READY with reason; do not fabricate favorable macro signals or retroactively fill a missed Q12 preopen snapshot with later prices.

## F. Phased maturity

`P2 Strategy Program Integration` (catalog/context/contract, no alpha promotion)
→ `P3 Step5D/5E/6 Safety` (broker truth/controlled recovery/freeze)
→ `P4 Q100-1/2/3 + Reporter v2` (measurable evaluation)
→ `P5 Q100-4/5 Experience Memory` (curated/advisory)
→ `P6 Q100-6 guided self-improvement` (human-bounded, not auto-trading)
→ `P7 Agentra V2 release freeze`
→ `P8 reproducible paper experiment package`.

P2 architecture can be prepared now, but production behavior changes, Step6/V2 runtime adoption and true promotion each require their own gated acceptance.
