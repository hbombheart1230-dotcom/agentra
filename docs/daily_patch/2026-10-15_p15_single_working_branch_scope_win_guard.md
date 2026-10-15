# 2026-10-15 — Single development branch, T4-D scope and Windows full audit

- User direction: **one active development branch**. Work solely on `integration/p15-t4-pr5-convergence-20261015`, no new branches, main remains protected until acceptance. After successful integration, preserve valuable unmerged design docs and collapse to main-only.
- Root cause old integrated T4 Linux [38716792220](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38716792220): T4-D whitelist compared BASE..integration HEAD; PR5 `libs/diagnostics/__init__.py` was incorrectly deemed a T4-D change. Keep whitelist over immutable BASE..T4 FINAL and add immutable T4 module+forbidden authority checks over T4 FINAL..integration HEAD.
- Windows baseline test at SHA 8405ed8: 2/2 passed, but `conftest.py` fast-tier reported directory-only `data/originals`, `data/specs` mtime deltas; do not claim overall PASS. Switch *only the isolated Windows baseline contract job* to full production FILE manifest (stronger per-file coverage) and preserve unresolved metadata P2.
- Production modules, fixtures, safety gate prefixes, real trading rights, Broker, Step5C CAS, UNKNOWN, UEF unchanged. No cleanup by deleting unmatched files.
- Independent Codex audit and required same-SHA Linux/Windows CI remain the acceptance gates.
