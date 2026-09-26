# Edit scope

Applies in every VS Code Copilot chat. Write only in the current code repository, plus the outside paths named below.

Goal: no write lands in another code repository.

- Current workspace: the repository root open in this chat.
- In scope: files, folders, or symbols in that workspace the user named, attached, or selected in this request, plus new files they asked to create.
- Auto-read is allowed everywhere. Search, open, and reference any file without asking, including unnamed files in the current repo, other code repositories, `/tmp`, `~/.cursor/`, `~/.copilot/`, and other paths. Reading is not a write.
- Other code repositories may be read freely. Do not write there unless this message names that repo or its files.
- Allowed writes outside the repo: `/tmp`, `~/.cursor/`, and `~/.copilot/`, only for the write this request or an installed protocol requires (review handoff, newagentlink, install or patch of rules, skills, or agents). Do not edit unrelated files under those trees.
- Any other path outside the current repo stays out of write scope until this message names it.
- Inside an in-scope file, change only what the request requires. No unrelated refactor, rename, reformat, import reorder, comment edit, or dead-code removal.
- Modify includes editor writes, create/delete/rename/move, and terminal commands that write (formatters, linters with `--fix`, codemods, package installs that change manifests or lockfiles, git checkout/reset/stash/clean, regenerating generated files).
- If the task needs an out-of-scope write, stop before making it. Report the file(s), why, and the proposed diff. Wait.
- Approval must be explicit and covers only the files listed in the proposal it answers. Silence, or approval inferred from earlier turns, is not approval.
