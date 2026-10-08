# 2026-10-08 — P1.5 Reporting branch consolidation (design authority)

## Decision
Keep only one active P1.5 design branch and one active Reporting refactoring branch.

- CANONICAL DESIGN: `design/p1.5-p1.6-modernization`
- CANONICAL REPORTING CODE: `codex/p1.5-reporting`
- Integration origin: original design at `920ebd0` was fast-forwarded to v1.1 revision `8ce75d0`.
- v1.0 and v1.1 authority docs remain intact on the original design branch.
- The canonical Reporting code starts from the cumulative `fbfab9b` implementation commit; P1.5.1/R2-A/R2-B/R2-C are already its ancestors.
- Former tranche/date-stamped branches are HISTORY ONLY; no new development on them. Removal requires successful ref cleanup and no open PR dependencies.
- Production `main` and live Docker/UEF/broker execution were not modified.

## Branch rule
Further P1.5 design changes: commit only to canonical DESIGN.
Further P1.5 Reporting implementation changes: commit only to canonical REPORTING CODE.
ZIP: GitHub Actions changed-files artifact, not a permanent artifacts/* branch.
Temporary CI trigger branches are not to be created.
UI patch notes remain append-only with source paths validated.

## Safety
This is reference and documentation consolidation. Do not infer that P1.2/P1.3 acceptance, full P1.5.2 final acceptance, main merge or production deployment is now authorized.
