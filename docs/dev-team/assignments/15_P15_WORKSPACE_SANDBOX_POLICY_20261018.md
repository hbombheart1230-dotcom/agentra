# Agentra P1.5 — Local Workspace / Git Worktree Sandbox Policy

**Authoritative from 2026-10-18.** Applies to Claude Code, Codex CLI, their remote-controlled local sessions and any optional Agentco helper. This is an **operational directory and tool-use policy**, not an automatic OS/filesystem sandbox or a grant of full-host permissions. It supplements [11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md](11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md). Do not weaken project safety/role authorization.

## 1. Allowed filesystem roots: discover actual roots before work

Before ANY write, run and record `pwd` / `Get-Location`, `git rev-parse --show-toplevel`, `git remote get-url origin`, `git status --short`, and `git worktree list --porcelain` from the active checkout. Validate that all editable roots belong to **hbombheart1230-dotcom/agentra**, exist or were created deliberately by `git worktree add`, and resolve to real paths without an unexpected symlink/junction/reparse-point escape.

**Writable only, per worker:**
- The **already existing Agentra repository checkout** and its **actually registered Agentra Git worktrees** used for the authorized branch/role. Treat each as an exact path, not a blanket allow on its parent drive.
- A **new isolated worktree only when the current task explicitly authorizes a new integration or evidence lane**, created with `git worktree add` underneath the already approved Agentra development/worktree parent. A worktree's `.git` pointer and common Git metadata belong to the same verified Agentra repository, but Git internal/protected writes may still require tool approval.
- Test captures, fixtures and scratch files only under `<active-worktree>/.agentra-worktmp/<run-id>/` (ignored, session isolated) **or** an already provisioned, independently verified Agentra-only scratch directory that is explicitly included as a writable root. Do not silently use `C:\Windows\Temp`, profile `AppData`, project-unrelated `%TEMP%`, the drive root or another repository.
- Existing `C:\AgentraEvidence\reporter_role` was *previously reported* as a Reporter checkout; it is **not automatically trusted or assumed to still exist**. Verify `git` worktree registration/remote/branch before using it. Similarly, do not guess the Codex/Monitor checkout path.

**Branch-specific writers:** Claude can modify its Reporter or isolated Strategist evidence branch; Codex can modify its Monitor or isolated shared integration candidate branch. They may read other worktrees for review but **must not write active other-worker trees**, `main`, or existing dirty user state. Agentco, if used, is read-only by default.

## 2. Absolute write/execute boundaries

Never edit outside verified allowed roots. Specifically no `C:\\`, `C:\Users\<user>\`, Agentco `C:\Agentco`, Windows/system directories, global Git config, `~/.ssh`, `~/.aws`, `~/.codex`, `~/.claude`, browser profiles, broker credentials, production DBs/data/volumes, existing `.env` or external network shares. Read access to a required tool's global settings must be deliberately narrow and never copied into reports.

**Prohibited operations unless user separately approves:** force-push, `git reset --hard`, `git clean -fd(x)`, history rewrite, recursive worktree deletion, branch deletion, live trading, broker/Executor/Supervisor policy writes, production deployment, user credential access, globally installed hook/config alteration. No `danger-full-access`, `--yolo`, `bypassPermissions` or `--dangerously-skip-permissions` as a generic workaround.

Git fetch/push, remote issue comments, dependency downloads, edits to protected `.git` metadata and attempts to expand writable roots can still trigger a **legitimate permission request**. Do not claim prompts are fully eliminated. Ask only once for a precise, unavoidable operation; if it is denied, keep working on other approved tasks and checkpoint the blocker. Never silently self-escalate.

## 3. Temporary output / test hygiene

- At the beginning of each test run make `<active-worktree>/.agentra-worktmp/<run-id>` and verify it is ignored (`git check-ignore`). If it is NOT ignored, place only a narrowly scoped `.git/info/exclude` rule inside the verified repo's Git metadata **if authorized**, or obtain a writable existing external Agentra-only scratch root; do not accidentally stage temporary artifacts.
- Set `TMP`, `TEMP`, `TMPDIR` and pytest `--basetemp` / pytest cache path to this scoped scratch as supported. Pass the same scoped `cwd` and **inherited OS environment** to subprocesses; never strip Windows `SystemDrive`/system environment values. Do not assume every tool honors the temporary directory settings; check actual output locations.
- Keep only source, tests and deliberately versioned small evidence in Git. Test caches, OS `.db`, crash dumps, OS cache directories, virtual environments and generated replay artifacts must stay untracked and out of the source tree.
- On success, remove **only the run's exact scratch directory** after verifying its canonical path; on failure, keep bounded evidence with an explicit retention cap (e.g. last three failed runs or seven days) and never delete unrelated data.
- Before commit run `git status --short` and the Reporter R11 hygiene check if present. No destructive cleanup outside the scoped scratch root.

## 4. Recommended Codex CLI settings (native Windows, only for a trusted local project)

The operator configures exact real paths in `%USERPROFILE%\.codex\config.toml` or in trusted project `.codex/config.toml`; **workers must not change user-level configuration themselves**. Example only, with placeholders that MUST be replaced after `git worktree list` verification:

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
writable_roots = [
  "C:\\AgentraEvidence\\<ACTUAL_AGENTRA_WORKTREE>",
  "C:\\AgentraEvidence\\<ACTUAL_AGENTRA_INTEGRATION_WORKTREE>"
]
```

The session's active checkout is the primary writable root; add only truly needed additional exact roots, not `C:\` or `C:\AgentraEvidence` wholesale if that parent contains anything else. Some Codex clients use newer permission presets; the actual app/remote session configuration, command-line options, trusted-project status and managed policies may supersede a file. **Check the effective per-session permission mode.** Do not assume settings in local Windows will govern an OpenAI-hosted remote sandbox.

## 5. Recommended Claude Code settings (local remote-controlled CLI)

Start from the **verified existing Agentra worktree**. Use `--permission-mode acceptEdits` for routine in-scope code edits. Only when another *verified Agentra worktree* must be inspected, use `--add-dir <exact-existing-path>` or the `/add-dir` command; permissions still apply. Avoid broad `Bash`/whole-disk grants. Deny/write boundaries are implemented by actual tool configuration/OS permissions, not by prompt text alone.

## 6. Startup acknowledgment and escalation

At the beginning of every Claude/Codex checkpoint output:
```
SANDBOX_ROOT: <verified exact checkout>
GIT_COMMON_DIR: <verified exact location>
WORKTREES_ALLOWED: <exact paths, each verified>
SCRATCH_ROOT: <verified ignored path>
CURRENT_BRANCH / HEAD / DIRTY_STATUS: <observed>
PERMISSION_MODE_EFFECTIVE: <observed or UNKNOWN>
OUTSIDE_ROOT_WRITES: NONE
```
If a path is missing, untrusted, outside the allowlist, or the sandbox cannot be enforced, STOP **that write**, record `SANDBOX_SCOPE_BLOCKED` and request narrowly scoped operator authorization; continue read-only or independent safe work instead. The goal is fewer avoidable approvals within verified worktrees, not full-machine access.

**No main merge, trading-authority change, automatic Work monitoring, or unattended runner activation is authorized.**
