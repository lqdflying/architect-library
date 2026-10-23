---
name: review-handoff
description: >-
  Review handoff ledger for code review and fix rounds. Creates or appends
  /tmp/<topic>-handoff.md with reviewer and fixer roles and FIX, DEFER, KEEP,
  DO NOT APPLY, FIXED, and RECONCILED dispositions, then purges closed rounds
  into /tmp/<topic>-handoff-archive.md. Use when asked to review, audit,
  check, or find issues in a commit, diff, branch, file, or PR; to verify
  another model's or agent's work; or to fix, triage, or reconcile findings
  from a /tmp/*-handoff.md file or pasted review feedback. Done when the
  ledger is created or appended this turn, closed rounds are purged when more
  than the latest two remain, and chat gives the path plus a short prioritized
  summary. Not the newagentlink one-shot snapshot.
---

# Review handoff and reconciliation

This protocol is the living review ledger at `/tmp/<topic>-handoff.md` (append across reviewer/fixer rounds). It is **not** the `newagentlink` skill, which writes a one-shot `/tmp/<topic>-newagentlink.md` for a new chat. Do not overwrite a review ledger. Do not append to a newagentlink file.

Treat each turn as **one role** unless the user explicitly asks for both phases:

- **Reviewer** — review, audit, check, find issues, or verify a coding-model response. Inspect and report; do not implement fixes unless explicitly asked.
- **Fixer** — implement, fix, build, or apply an existing reviewer handoff. Validate first, then make authorized changes.

Reading or assessing a handoff is not authorization to edit. On a planning or triage request, classify the feedback and give a fix plan without changing files. A role does not broaden authorization: review readiness never authorizes edits, installs into the review repo, or other remote mutations; implementation never authorizes a push, tag, build, deployment, or release.

Repository `AGENTS.md` / `CLAUDE.md` remain authoritative for that project's branch, documentation, verification, and commit rules.

## When to write a handoff

When asked to review, check, audit, find issues, or reconcile a prior handoff for a commit, diff, branch, file, or PR, write `/tmp/<short-topic>-handoff.md` without being asked.

Skip a handoff when the *only* work is authoring editor rules, plans, or other meta docs. If the user also asks to review a commit, diff, or PR, write the handoff for that review.

Handoff markdown lives under `/tmp`, not in the repo, unless the user asks to commit it.

## One file per session

- Path: `/tmp/<short-topic>-handoff.md`
- First review in a session: create the file (or reopen it if review continues).
- Later reviews in the same session: **append** to that same file only. No `-v2` or parallel files.
- Across sessions: a new `/tmp` file is OK for a new review topic. The prior active file stays until **RECONCILED**. Its archive stays on disk and is not read on an ordinary turn.
- While any **FIX** items are open, keep appending to the same path.

In chat: state the path, then a short prioritized summary. Do not paste the file back.

Chat-only review without a handoff update is not done.

### Codex read-only custom agents

The Codex `code-review` and `security-auditor` agents return a proposed ledger
path and a complete labeled round to the parent; they do not write even to
`/tmp`. The parent appends the round, then purges closed rounds with
`scripts/purge_handoff.py`. Until the parent confirms the write, describe the
ledger update as pending. Do not weaken the sandbox or use shell writes to
bypass it. Ordinary Codex sessions with write access continue to maintain the
ledger directly.

## Ledger file discipline

Append the new round first. The only rewrite of an existing `/tmp/<topic>-handoff.md` is `scripts/purge_handoff.py`, after that append.

**Forbidden:**

- Replacing the ledger from memory (`Write` of the whole path, `cat > file`, truncate, `rm` + recreate)
- Deleting the archive, or editing it by hand
- A `-v2` or parallel file that replaces the ledger

**Allowed:**

- **Create** the active file only when that path does not exist yet
- **Append** the new round: `printf '%s\n' '…' >> /tmp/<topic>-handoff.md`
- **Surgical** edits of the header (everything before the first `## Round` or `## Fixer` line): **Status**, **Must fix**, **Standing**, **Closed**, and the one line `Purge-ready: yes`
- **Purge** by the script, which moves closed rounds verbatim into `/tmp/<topic>-handoff-archive.md`

**If content was already wiped this turn:** stop. Recover prior text from the archive, then the chat or transcript. Write that recovered body plus the new round once. Record the incident under **Already verified**. Later purges go through the script only.

## Purge closed rounds

Later turns read the active ledger only. Closed rounds sit in the archive so they do not enter context.

After the append, purge when the file has more than two `## Round` or `## Fixer` sections. With two or fewer, do not purge.

A round is one `## Round …` or `## Fixer …` section, including every later `##` heading until the next round. `## Already verified` and finding titles stay inside that round.

In the round you append, restate each open **FIX** or unanswered question that is not already stated in full in the round which will remain (path, what is wrong, **Fix:**, **Test:**). Put that text under a `### Still open` subsection of the new round. Do not add a `## Still open` section.

1. **Standing** — one header line per live **DEFER**, **KEEP**, and **DO NOT APPLY**, with the reason. Use `**Standing:** none` when there are none.
2. **Closed** — one header line per **FIXED** item whose round will leave the active file: id, `path:line`, and the evidence. Use `**Closed:** none` when there are none.
3. Add a header line `Purge-ready: yes` only after steps 1–2. The header must already contain `**Status:**`, `**Must fix:**`, `**Standing:**`, and `**Closed:**`.
4. Run `scripts/purge_handoff.py` from the same directory as this `SKILL.md`:

```bash
python3 <skill-dir>/scripts/purge_handoff.py /tmp/<topic>-handoff.md
```

Installed skill directories: `~/.cursor/skills/review-handoff/`, `~/.copilot/skills/review-handoff/`, `~/.agents/skills/review-handoff/`, `~/.claude/skills/review-handoff/`.

The script keeps the header and the two newest rounds. It appends every older round verbatim to `/tmp/<topic>-handoff-archive.md` and removes `Purge-ready: yes`. It changes nothing when the header is not ready. A fenced `## Round` line stays inside its round, including when the closing fence has trailing spaces. If the script refuses, fix the header and run it again. Do not rewrite the ledger by hand.

Read the archive only when a closed item is contested or an open item's full text is missing. Do not read it on an ordinary review or fix turn.

When the script moves sections, add one chat line: the archive path and how many sections moved.

## Dispositions (both sides)

- **FIX** — must change before calling the work done. Highlight at the top ("Must fix").
- **DEFER** — valid, not blocking; say why and what would trigger it. Never drop silently.
- **KEEP** — intentional product/behavior decision; do not change unless the user changes it.
- **DO NOT APPLY** — wrong or unsafe; do not implement.
- **FIXED** — done; cite evidence (file + what changed + how verified).
- **RECONCILED** — no FIX items remain; list each item's final disposition.

Map older labels once: accepted → **FIX** (then **FIXED**); rejected → **DO NOT APPLY**; already resolved → **FIXED** or **KEEP**; product decision → **KEEP** or **DEFER**; optional → **DEFER**.

Do not accept a reviewer's conclusion without checking the current tree. Disagree with file-level evidence, not deference.

## Reviewer

### Scope

Never assume "the local commit" means only `HEAD`. Honor an explicit user scope (named commit, range, file, or PR).

- For "local," "unpushed," or "my changes," use `@{upstream}..HEAD` plus staged, unstaged, and untracked changes. Confirm ahead count with `git branch -avv`.
- For a branch or PR, use the target branch's merge-base so pushed and unpushed commits are both included.
- Do **not** use `git log --branches --not --remotes` as the sole scope.
- If no upstream or target exists, inspect history and remotes, choose a base, and state the rationale.
- Repeat for every affected repository (including a separate docs/wiki clone if present). State repository, branch, base, exact commit range, and worktree scope.
- Review the range as one body of work. Anchor each finding at the **current** file state.

### Read-only worktree

Review does **not** change the repository under review. The only allowed writes are `/tmp/<topic>-handoff.md` and, when purging, `/tmp/<topic>-handoff-archive.md`.

- Prefer read-only inspection: `git diff`, `git status`, read files, syntax-check commands that do not write into the tree.
- Do not install, build, patch, copy artifacts, or run project-scoped library install into the review repo unless the user explicitly asks.
- If verification must touch the tree (tests, local install, generated files): prefer `/tmp`, a throwaway worktree, or global paths (for example `~/.cursor/` or `~/.copilot/`) first.
- When a command must write into the review repo anyway: record `git status` (and untracked paths) **before** the command; undo every change before the review turn ends (`git restore`, remove untracked artifacts the command created); confirm the tree matches the pre-test baseline except for the user's in-scope diff. Record what ran and what was restored under **Already verified**.
- A review turn is not done while the review repo still carries verification side effects the reviewer introduced.

### Handoff contents

Verify every finding against current code before recording it. Prefer the smallest correct fix. Distinguish correctness issues from optional improvements. Point at the repo's `AGENTS.md` / `CLAUDE.md` instead of restating them. Flag docs-only findings.

On first create, put a header at the top: **Status**, **Must fix**, **Standing**, **Closed**, repositories/branches/bases/ranges, worktree scope. On later turns, surgically update those header lines, append the round, then purge closed rounds.

Then (in the first create, and again inside each appended round as needed):

1. **Already verified** — commands run and results, plus known limits.
2. **Findings, in priority order.** Each: exact `path/to/file.ts:LINE`; what is wrong and why (concrete failure); a **Fix:** paragraph; a **Test:** note; severity up front; disposition.
3. **Behavior to confirm with the user** — no code change until they decide.
4. **Explicit NON-issues** — flagged then disproved, with evidence.
5. **Documentation impact** and copy-pasteable follow-up verification commands.

On every review turn, **append** a labeled round (for example `## Round — <date or commit>`), then purge closed rounds. Do not rewrite the file any other way.

Do not create `.patch` files, run `git format-patch`, or commit the `/tmp` handoff unless the user asks.

## Fixer

When the user points at `/tmp/<topic>-handoff.md` (or pastes review feedback), the role is **fixer**. Process the handoff; do not re-review from scratch; do not treat the reviewer's word as ground truth.

1. Read the active ledger, not the archive. Independently validate every finding, claim, open question, and NON-issue against the current branch. Open the archive only for a closed item that is contested or an open item whose full text is missing.
2. Classify with the dispositions above. Explain disagreements with file-level evidence.
3. On a planning or triage turn, record classifications and a fix plan for **FIX** items — no edits.
4. Do not change a NON-issue, **KEEP**, or **DO NOT APPLY** unless current evidence disproves it or the user changes the decision.
5. On an implementation turn, fix every **FIX** with the smallest correct change. A wrong path in reviewer prose does not invalidate an otherwise real finding — correct the prose explicitly.
6. Verify in proportion to risk. Inspect new assertions for vacuous mocks. Do not rerun an expensive check the handoff recorded as passed unless later changes could invalidate it.
7. Do not treat an unrelated ancestor Git root as an affected repository merely because a task file is beneath it. Never stage a previously untracked configuration or tool-state subtree solely to manufacture a commit.
8. **Do not auto-commit.** Commit only when the user explicitly asks or the active repository's rules require a commit on this turn. Never push. If verification is blocked, record the blocker and do not describe the round as complete.
9. Append a labeled response section (`## Fixer — …`) to the **same** file, then purge closed rounds. Do not rewrite the file any other way.

The response section must include:

- **Items actioned** — per-item **FIXED** (or restored / confirmed) with file + change + how verified.
- **Per-layer checks** when a fix spans layers (each layer touched).
- **Items deferred or declined** — **DEFER** / **DO NOT APPLY** with the reason.
- **Still open after this round** — remaining **FIX** items.
- **Verification results** — actual command output; flag pre-existing failures and unrunnable suites.
- **Commits this round** — hashes and subjects, or an explicit note that no commit was made; plus "no remote actions taken" when push/tag was not authorized.
- **Branch state** — unpushed commits + clean-tree confirmation (or remaining dirty paths).

## Reconciliation loop

The active ledger stays small. Reviewer appends `## Round — <date or commit>`; fixer appends `## Fixer — …`. Then purge. Closed round text lives in the archive. The header keeps **Status**, **Must fix**, **Standing**, and **Closed**. Do not rewrite the file to refresh status.

On a later review round: read the active ledger first, then independently verify fixer claims against current code. Confirm each **FIXED** is present. Record suspected-then-disproved items as NON-issues.

Continue until a round produces **zero new FIX items and zero open questions**. Record **RECONCILED** (which round, final commit SHAs). If a finding stays contested after one evidence exchange, stop and escalate to the user.

A reconciled review still does not authorize a push, tag, build, deployment, or release. Refer other sessions to local commits, not patch files.

### Post coding-model fix (user re-review)

When the user asks to review after another model fixed **FIX** items:

1. Re-read the session handoff and the current tree (`git status`, `git diff`). Do not trust a prior **RECONCILED** label without re-checking.
2. Independently validate every open **FIX**, every claimed **FIXED**, and any diffs since the last round.
3. Append `## Round — <date> post-fix re-review`, surgically update the header, then purge closed rounds.
4. Chat session summary (required):
   - If any **FIX** remains: heading **Remaining FIX** with numbered items.
   - If none: heading **All reconciled**.
   - Always add **Deferred / workflow** (non-blocking).
5. Implementation turn fixes only **FIX** items unless the user overrides.
