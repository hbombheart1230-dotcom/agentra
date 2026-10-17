# Retired Agentra branches — recoverable history

Seven completed/obsolete design, plan and implementation branches are preserved in `retired_branches.bundle`. This is a small incremental Git bundle, NOT a full repository copy. It preserves exact commit/tree/blob history unique to these branches, including original designs and audit evidence. No source from these branches is blindly merged into runtime.

Prerequisites: existing repository objects reachable from integration commit `eeb742a33b16f6271ff364a904e187b470561c7e`. Keep normal integration history. Clone the repository and fetch that commit if necessary; then run `git bundle verify docs/refactor/retired_branches/2026-10-17/retired_branches.bundle`. The bundle header lists its exact prerequisite boundary commits.

Recovery: `git fetch docs/refactor/retired_branches/2026-10-17/retired_branches.bundle refs/remotes/origin/<original-branch>:refs/heads/recovered/<original-branch>`. Use the exact original name from manifest.json. Compare restored SHA with manifest before pushing a recovered branch. Do not overwrite active role branches.

Delete only if current remote HEAD still equals manifest, no open PR uses the ref, and no active worker depends on it. Local worker worktrees are not deleted by this operation. main plus integration/Reporter/Monitor stay active. The manifest records preservation; final UI/API branch inventory is deletion evidence, not a claim embedded before deletion occurs.
