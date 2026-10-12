# R3 offline audit harness — copyable Windows PowerShell templates (Guard 006)

Both tools are **fail-closed**: they refuse (exit 2 / pytest UsageError) before importing Reporting, collecting tests, scanning trees or opening outputs unless the root is an explicit absolute path to an **isolated separate Git clone**, `cwd == root`, `PYTHONDONTWRITEBYTECODE=1`, inputs exist, and outputs are NEW files outside the clone. `C:\Agentra` and everything below/above it is always refused (lexical check only; never stat'ed). Extra protected roots: `--protected-root` / `R3_PROTECTED_ROOTS` (`;`-separated). Never use `C:\Agentra` as `Set-Location`.

## A. Seam challenge / direct differential (one tree per run)
```powershell
$clone = 'C:\AgentraEvidence\r3_seam_clone'          # isolated clone of origin/refactor/p1.5 (NOT C:\Agentra)
$in    = 'C:\AgentraEvidence\p152_r3_moved_free_names.json'   # copy of evidence/p152_r3_moved_free_names.json
$out   = 'C:\AgentraEvidence\r3_seam_out_001.json'   # must not exist yet, outside the clone
$env:PYTHONDONTWRITEBYTECODE = '1'
Set-Location -LiteralPath $clone
& "$clone\venv\Scripts\python.exe" -I -B scripts\refactor\p152_r3_seam_challenge.py `
    --root $clone --moved-free $in --out $out
# use any project interpreter that is NOT started from, or pointed into, C:\Agentra's source tree
```
## B. Call-recorder plugin (same test list in baseline and feature clones; diff the two logs)
```powershell
$clone = 'C:\AgentraEvidence\r3_seam_clone'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH   = "$clone\scripts\refactor"
$env:R3_ROOT      = $clone
$env:R3_NAMES     = 'C:\AgentraEvidence\p152_r3_moved_names.json'
$env:R3_LOG       = 'C:\AgentraEvidence\r3_calls_feature_001.json'   # NEW file outside the clone
Set-Location -LiteralPath $clone
python -B -m pytest -p p152_r3_call_recorder -p no:cacheprovider -q <explicit test files>
```
Optional: `$env:R3_PROTECTED_ROOTS = 'D:\other\protected'`. Repeat with a different clone/log for the baseline tree. Remove `R3_*` variables afterwards (`Remove-Item Env:R3_*`).

## Known limits
- Guard fails closed on any symlink/junction/reparse component, `..`, 8.3 short names (`AGENTR~1`) and relative paths; it does not resolve aliases it refuses.
- The interpreter itself may be located anywhere; the guard only governs the audited root and I/O paths. `__pycache__` of the plugin module can be written to `scripts\refactor` of the chosen clone before the guard runs if `-B`/the env var is omitted — always set both.
