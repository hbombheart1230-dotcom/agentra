# Cross-Phase Contract & Evidence-Lineage Architecture

Status: CONCEPTUAL CONTRACTS, **not** deployed DTO fields or authoritative schema modifications. Existing frozen UEF/Step5C contracts supersede conflicting suggestions.

## 1. Identity namespaces — do not conflate

| Concept | Illustrative identity | Owner | Authority |
|---|---|---|---|
| Runtime cycle | `run_id` | Commander/event context | Correlation, not mutation admission |
| Broker order intent | `intent_id` / canonical physical-order fingerprint | Step5C Execution Owner | Admission/CAS/trading authority only inside existing guarded code |
| Strategy program | `program_id` (`Q10`, `Q12`, `OPENING_ALPHA`) | P2 registry | Research catalog label; not strategy promotion |
| Hypothesis/experiment | `hypothesis_id` / `experiment_id` | research and UEF adapters | Evaluation cohort identity |
| Source observation | `snapshot_id`, content digest, `as_of` | market source adapter | Provenance of what was known when |
| Frozen evaluation | UEF `evaluation_record_id`, UEF-7/8/9 run IDs | UEF canonical authority | Source of accepted evaluation facts, conditional on VALID binding |
| Q100 derived view | `strategy_evidence_view_id` | Q100 | Read-only aggregation/reference, not metric authority |
| Memory record | `experience_id` / source evaluation IDs | P5 knowledge store | Advisory only |
| Paper dataset | `dataset_version` / manifest digest | P8 experimental freeze | Reproducibility, not live trading |

IDs never substitute: `run_id != intent_id`, Q100 derived evidence ID != UEF record ID, `memory_id != approval`. Do not generate a "valid" broker intent ID from an LLM memory entry.

## 2. Conceptual value objects — names/fields illustrative

```text
SourceSnapshot {
 source_id, snapshot_id, raw_digest, captured_at_utc, observed_at_market,
 as_of_utc, market_session, exchange_timezone, validity_window, data_quality,
 missing_fields, origin_uri_or_artifact_ref, clock_policy_version
}

MarketContextFrame {
 context_id, decision_cutoff_utc, korea_trading_day, source_snapshot_ids[],
 regime_assessment, overnight_us_semiconductor, btc_24h, jpy_fx,
 domestic_index_context, limitations[], no_lookahead_proof
}

ProgramEntry {
 program_id, title, version, hypothesis_id[], cohort[], observation_mode,
 research_status, evidence_coverage, upstream_dependencies[], exclusions[],
 validation_policy_ref, promotion_policy_ref, owner_docs[], last_reviewed
}

StrategyEvidenceView {
 program_id, window_start, window_end, source_uef_binding_run_id,
 source_record_ids[], eligibility, pair_statuses, known_limitations[],
 derived_at, attribution_views[], confidence_annotation
}

AttributionFinding {
 program_id, outcome_window, source_evidence_ids[], category,
 observed_effect, uncertainty, confounders[], dataset_coverage, method_version,
 proposed_action, operator_review_required
}

ExperienceRecord {
 experience_id, source_program_id, source_evaluation_record_ids[],
 source_class, evidence_cutoff_utc, promotion_stage, promoted_by,
 promoted_at, confidence_basis, caveats[], superseded_by, expiry_or_review_at
}

ExperimentManifest {
 research_question, hypothesis_version, preregistered_metrics[],
 eligible_sessions, forbidden_contamination_windows[], data_hashes[],
 code_sha, evaluation_authority_binding, arm_definitions,
 randomization_or_matching_policy, time_split, exclusion_log, analysis_version
}
```

These are **interface language** for P2–P8. Actual P1.5 DTO names, typing, property keys and file modules are NOT frozen by this document. Phase implementation must reuse canonical owners and document exact migration rules.

## 3. Data quality states / fail-closed propagation

- Source: `AVAILABLE_FRESH` / `STALE` / `MISSING` / `INVALID` / `UNKNOWN_CLOCK`. Names are a conceptual layer, **not** a change to existing runtime enums.
- Research eligibility: `ELIGIBLE` / `BLOCKED` / `DIAGNOSTIC_ONLY`. These are separate from portfolio status KEEP/WATCH/DEPRECATE_REVIEW and separate from UEF-9 `VALID` (or exception).
- Recommendation: `NO_ACTION`, `REVIEW_CANDIDATE`, `REJECTED` (human workflow) — distinct from actual trade approval.
- No fresh evidence → no positive inference; no UEF valid binding → no canonical evidence-based promotion; incomplete counterfactual → no causal attribution.

## 4. Temporal correctness

Separate signal `decision_cutoff` from data `capture_time` and `evaluation_horizon`. For a 09:00 KST trade, it is forbidden to treat a 09:05 source read as 08:55 information. BTC's 24h lookback window, US previous-session close, SOX/Micron/NVIDIA, JPY spot/future and market holidays use explicit matching to Korean trading dates. Choose benchmark windows in exchange-local clocks; daylight-saving transition and Japanese holidays require tests.

A missing Q12 08:55 snapshot remains missing — never fill backward after observing the outcome. UEF same-day replay derives the same IDs when semantic inputs are unchanged. Read from canonical freeze manifests; no authority from docs themselves.

## 5. Evidence lineage contract

```text
source captured + hash + freshness
  -> program signal with decision-time cutoff
  -> candidate/intent decision trace (not always executed)
  -> order/actual outcome (maybe none/UNKNOWN)
  -> UEF canonical candidate/pair + binding VALID
  -> Q100 derived read model / method+version
  -> finding with source_evaluation_record_ids
  -> Lesson only after independent validation
  -> retrieved context pack (advisory, optional)
```

Every junction must expose its input IDs, output IDs, quality/errors and owned transformation version. A memory entry with no source evaluation record cannot advance above Daily Observation (Q100 existing rule). Old/legacy evaluation gets lower trust and visible label.

## 6. Exact hard invariants borrowed from frozen owners

- UEF-9 is **only** `VALID` if all binding validations pass; otherwise raises `UEF9AuthorityError`. No `partial-valid` or confidence score in the authority layer.
- UEF-7/8 candidate/pair conservation, unique IDs, status count reconciliation, same-day replay determinism, current/latest publish after COMPLETE, no diagnostic canonical writes.
- Step5C canonical intent/admission/physical order CAS with duplicate at-most-once and UNKNOWN nonterminal quarantine; don't replay broker mutation after a timeout.
- Guard precedence is not affected by Strategist, memory or Q100; changing signals cannot weaken risk controls.
- Reporter/Q100 memory may have measured *confidence annotations* but never alter the UEF authority status.

## 7. Read/write matrix (architectural target)

| Layer | Reads | May write | Forbidden writes |
|---|---|---|---|
| P2 Strategy registry | previous program docs + source snapshots | research registry/context projections in isolated namespace | operational intent/admission/broker/UEF |
| P3 Safety | canonical intent/approval/claim+broker evidence | only explicitly approved guarded reconciliation/operator records | replaying broker requests from UNKNOWN; rewriting frozen Step5C |
| P4 Q100/Reporter | UEF canonical records, read-only actual report/event | versioned derived analysis/reports | UEF canonical metrics/authority input |
| P5 Memory | Q100 validated evaluation | versioned advisory Lesson and portable vault exports | SQLite/trading authority, original UEF records |
| P6 Improvement | eval/lesson/controls | review/suggestion/approval queue | auto live parameter/prompt/guard/trade modifications |
| P7 Freeze | all immutable test/artifact evidence | freeze manifest/tag and approved operator runbook | rewriting prior evidence |
| P8 Paper | frozen dataset, code/metadata, approved anonymized records | controlled experiment outputs/manuscript | production trading/order/account state |

## 8. Privacy, observability and growth

Record only necessary market/decision metadata; redact secrets, account numbers, raw sensitive payloads. Provenance paths are references and hashes, not copies of production SQLite into Obsidian or Git. Bound data retention for temporary tests and local generated fixtures. Production write detection and path isolation must be actively tested at implementation time.

## 9. Proposed change workflow

Each phase will translate this conceptual contract into `P<n>_IMPLEMENTATION_BLUEPRINT` using **that phase's frozen predecessor source SHA**, an exact old→new field map, runtime consumers, compatibility adapters, negative tests and independent acceptance. This document by itself authorizes no migration.
