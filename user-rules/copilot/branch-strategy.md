# Branch strategy

Applies in every VS Code Copilot chat. One working branch at a time. The branch you are already on is that branch.

- **`main` is protected against writes. Checking it out is allowed.** Never edit, commit, or push on `main`. Read-only use is fine and expected: check it out, read it, fast-forward it (`git fetch origin main:main`), or stand on it while deleting a finished branch. The rule bites at the first write. If `main` is checked out and a file must change, create the working branch first and make every edit there. Being on `main` is not permission to write, and a request to edit files while on `main` means leave `main` before the first edit.
- Any other current branch is the non-main working branch. Stay on it for the task already in progress and for the next task, whatever the topic. Do not create or check out another branch because the work is a fix, a new task, a different phase, or a different subject from the branch name.
- Do not switch away from a branch that holds unmerged commits or uncommitted files. The new branch cannot see that work, so switching strands it. Once its commits are merged into `main` and the tree is clean, switching is safe.
- A new branch is allowed when the current branch is `main` (the normal way a task starts) or when the current branch is already a non-main working branch and the user explicitly asks for one. Create that branch from `main`.
- **One branch and one push may carry several unrelated topics.** A commit on a different subject (a naming fix landing on a tagging branch, a docs change landing on a feature branch) is expected. Do not propose splitting a branch, moving a commit to its own branch, or requiring one PR per topic unless the user asks for that split. The branch is a workstream, not a topic.
- Pause for user confirmation before `git commit` or `git push`.
