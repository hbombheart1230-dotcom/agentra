# P1.5 Codex developer: Reporter P2 and CI portability

Candidate only; independent Claude audit pending. Overall integration remains FAIL.

Reporter exception wording now accepts only the same too-many-unpack direction,
identical expected arity, and an optional `, got M` detail. Two present got counts
must match. Wrong direction, arity/count changes and malformed strings fail.
Frozen 2565-case fixture and runtime sources are unchanged.

Hosted run 39088517687 at 5cb90b39d00cee483be292272b893d8e8a4c6e78
actually executed: Linux Python 3.12 normal/-O each 2893 PASS, 3 FAIL, 24 SKIP;
Windows Python 3.13 normal/-O each 2895 PASS, 1 FAIL, 24 SKIP.
The earlier hosted NOT_RUN statements were historical authoring-time observations;
REST run/job records now establish execution. Two Linux failures are evidence
serialization incompatibilities, and UEF9 is the independently BASE-reproduced
remaining failure. No UEF expectation, policy or frozen hash is changed.

The Monitor evidence dump uses a fixed CPython 3.14 schema profile to reproduce
existing hashes on 3.12/3.13/3.14. Only declared empty-list and optional-None
fields are omitted. Constants, bodies, imports and unknown fields stay visible.
The source-provenance check and retained-symbol producer share this serializer.
Negative tests mutate source constants rather than monkeypatching ast.dump.

The existing complete hosted contract matrix also triggers on the Codex branch.
Optimized execution propagates PYTHONOPTIMIZE=1 to spawned interpreters.
Full integration checks remain mandatory and retain the unwaived UEF9 failure.
See docs/dev-team/integration/CODEX_P2_CI_CHECKPOINT_20261018.md for results.

Web build and desktop/mobile visual smoke: NOT_RUN. No product UI changed;
paired patch-note schema/API validation is recorded separately. Genuine persisted
real-artifact parity remains NOT_RUN; existing 24 SKIP are not converted to PASS.
