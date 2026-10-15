# P3 — Execution Safety: Step5D → Step5E → Step6

Status: ARCHITECTURE / FUTURE IMPLEMENTATION GATED. Not an order-recovery script; no broker read/write issued here.

## Source baseline / why sequence matters

`docs/development/step5c_execution_owner.md` declares:
- Step5B classifies broker outcomes with at-most-once physical mutation; ambiguous submission → **UNKNOWN**.
- Step5C owns canonical intent/admission, approved→executing SQLite CAS, normalized physical-order claim and duplicate protection.
- An UNKNOWN stays nonterminal, claim held, reconciliation_required=True. **NO implicit replay**.
- Step5D answers **what actually happened at the broker**; Step5E owns **safe operator recovery**; Step6 confirms integrated safety. Existing Step5C freeze is not authority to bypass those stages.

## Step5D — broker-truth reconciliation *read-first*

Contract:
```text
(input) canonical IntentState + Admission + PhysicalClaim + BrokerOutcome
        + broker/account/order/fill READ snapshot with broker request IDs
        + session/source/clock/reliability
(output) ReconciliationAssessment {
   canonical_intent_id,
   claimed_fingerprint,
   observed_order_id(s) / fill evidence refs,
   evidence_time_window / source_quality,
   result: MATCHED | MISMATCH | NOT_FOUND | PARTIAL | UNKNOWN,
   ambiguity_reasons[], operator_review_required,
   proposed_safe_next_step, immutable_evidence_ref
 }
```
These status words are *conceptual*, not declared existing enums. Broker absence is **not proof that no order was sent**: pagination, late visibility, partial fill, canceled order, wrong account/session, broker outage and API retries require disambiguation. A timeout **cannot** be interpreted as NOT_SENT once physical dispatch might have occurred.

Step5D may generate **read-only assessment and a controlled reconciliation record** in a dedicated authoritative owner after explicit review of existing storage. It may not release held claims or submit a replacement order merely because a broker read returns missing. Cross-path broker API calls remain exactly-once/at-most-once guarded.

## Step5E — approved operator recovery

Separate state machine for incident lifecycle:
```text
QUARANTINED → EVIDENCE_COLLECTED → REVIEW_REQUIRED
                                  ├ insufficient/conflicting → HOLD
                                  ├ confirmed fill           → close/reconcile accounting
                                  ├ confirmed rejected/no-fill → approved terminal resolution
                                  └ unknown                 → HOLD / escalate
     (each permitted transition audited, scoped, idempotent)
```
A recovery action needs: unique incident/action ID; canonical intent/fingerprint; versioned broker proof; operator identity/role; reason; expected previous state; second review for real execution when policy requires; atomic CAS transition; immutable before/after evidence. Never accept LLM "repair", memory lesson or graph checkpoint as authority. All manual actions have dry-run preview and fail-closed stale version detection.

## Step6 — integrated final execution safety freeze

Acceptance dimensions (each independent):
1. Safety role boundary: Monitor intent-only; Supervisor authorization; Executor alone broker mutation.
2. Step5B after-dispatch exception and UNKNOWN state never downgraded to NOT_SENT.
3. Step5C proof of canonical admission, unique intent/physical fingerprint, CAS and ownership loss behavior.
4. Step5D broker truth: duplicates/partial fills/late acknowledgements/orphans/delayed API/search gaps.
5. Step5E operator: permissions, stale CAS/review, cancel/replace only when explicit supported safety path.
6. Live envelope: Docker/host single owner, heartbeat/lease, SIGTERM drain, forced crash/restart matrix and recovery gates.
7. Cross-day correctness: post-closeout/UEF processing cannot be mistaken for pending order recovery.
8. Observability: reasoned audit trail and anti-tamper evidence; redacted accounts/tokens.
9. Code/test isolation: offline path writes 0 production artifacts and sends 0 broker requests.
10. Rollback/runbook: disable new operator workflow without disabling underlying held-UNKNOWN quarantine.

## Required fault-injection table (illustrative)

| Fault | Correct response |
|---|---|
| HTTP timeout **before** dispatch proven | pre-dispatch classification only if confidently proven |
| HTTP timeout **after** dispatch | UNKNOWN held; no automatic replay |
| Duplicate intent or same physical order under different IDs | Step5C deny duplicate; no double submission |
| Broker report delayed/partial/paginated | INCOMPLETE/UNKNOWN until authoritative evidence complete |
| Broker says fill but SQLite pending | explicit discrepancy + safe accounting/reconciliation path, not blind replay |
| Unresolved SELL during closeout | preserve open exposure assessment and quarantine, not assumed flat |
| Owner lease lost mid-tick | block new tick / new mutation |
| Operator retries stale/replayed recovery action | CAS rejection / idempotent no-op; full audit |
| Read-model and authoritative DB disagree | authoritative store wins, alert and stop |
| Memory/LLM suggests "retry buy" | ignored by Supervisor/Executor |

## Non-goals / caution

No order auto-healing after UNKNOWN, no CAS schema rewrite for convenience, no copy of original broker ledger into a graph checkpoint, no memory feedback directly into execution. Step5D/5E implementation must be separately safety-reviewed against the actual P3 baseline SHA and running system version. Post-Step6 V2 operational features can be activated only under the acceptance gate in `docs/architecture/architecture_v2.md`.

## Phase exit

`P3_ACCEPTED` requires independently replayable incident evidence, safety-lock diff review, all critical/failure tests, separately permitted operational exercise and GPT/user signoff; architecture docs alone do not pass.
