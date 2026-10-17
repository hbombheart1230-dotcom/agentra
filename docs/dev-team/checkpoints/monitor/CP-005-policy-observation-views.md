# Monitor CP-005: one cohesive policy trace Owner

PREVIOUS_PUSHED_SHA: 405c389069429ccb125547379736bd993b995e75
BASE: d773709ba2f70471fad9badba4f92400f7818319
STATE: ACTIVE_PARTIAL_NOT_ROLE_READY, Work review pending
FEEDBACK_ACK: #12 / 6232275871, no new supplied runtime blocker

Three related trace builders (181 + 56 + 27 original LOC) now share one
policy_trace_views Owner, rather than one tiny Owner per function. Sources are
monitor_strategy_frame, monitor_entry_policy_context and monitor/entry_candidate_policy.
Actual frame/threshold normalization, memory-bias application, ranking, horizon,
sizing, guards and decision functions remain protected by entire-module AST proof.
The original existing graph facade parameter is forwarded unchanged; the other
source's two read callbacks are still resolved at use time. No new LLM/IO authority.
One Owner <350 LOC, typing-only imports, no source import cycles.

53 BASE-only frozen cases (39748 bytes), producer and raw BASE/helper SHA-256 stored.
Real delta callback/constant sources match BASE before import. Exact output/key
order, policy/source precedence, malformed/missing inputs, exception contract,
ordered callback/Traced-dict mutation and nested alias/return identity validated.
Twelve corruptions rejected in normal and -O processes, including unmoved actual
policy functions, module statements and attempted Broker capability substitution.

Initial combined own-role run: 383 PASS / 2 FAIL / 0 SKIP, 49.67s.
Both failures were new negative-test setup: ast.parse of retained UTF-8 BOM source,
with a CP949 child stderr decoder masking that SyntaxError. Explicit UTF-8 capture
and BOM-aware parsing fixed the test, not runtime bodies or expected values.
Intermediate two-test diagnostic failed honestly and retained locally.
Final whole M-005 cohort: 63 PASS / 0 FAIL / 0 SKIP, 11.91s.
Other unchanged cohorts' initial passes are reused, not a fresh combined pass.
Raw roots:
C:/AgentraWork/tmp/monitor_m005_446b1eead601475480bb22b4a70225b6/;
C:/AgentraWork/tmp/monitor_m005_negative_987e79d331034bc58af9bbdf8af087f9/;
C:/AgentraWork/tmp/monitor_m005_final_1bb9069da03b4630aa690f96d38fa234/.
Isolated TEMP/TMP/TMPDIR/cache/runtime; mock/full write audit, no finding.
One final cache_dir warning; no skips or assertion weakening. Scratch retained due
to manual cleanup denial. No shared tests/workflow/official UI changes.

NEXT_READY: M-006 native frozen Monitor replay + unchanged Wave B/consumer scope;
M-007 current whole-role accounting, exact shared follow-up and bounded delivery.
Do not self-accept remaining shared failures; Work integration/independent review
remains mandatory. Paired proposed m005_patch_notes JSON/MD accompanies this CP.
New SHA posted after push; no self-referential commit SHA in this document.
