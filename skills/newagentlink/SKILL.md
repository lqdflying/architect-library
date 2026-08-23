---
name: newagentlink
description: >-
  Writes a one-shot continuation markdown so a new Cursor agent can proceed
  without the old transcript. One read on the new agent's first turn, then
  never reuse or update that file. Use when the user types /newagentlink, asks
  for a new-agent brief, continuation file, or "too much context / start a new
  agent".
disable-model-invocation: true
---

# New agent link (`/newagentlink`)

Write **one** markdown file a **new** agent can read **once** and then discard.

This is **not** a living ledger. It is **not** the review protocol in
`user-rules/cursor/review-handoff-reconciliation.mdc` (installed as
`~/.cursor/rules/review-handoff-reconciliation.mdc`). That file is updated
across reviewer/fixer rounds and writes `/tmp/<topic>-handoff.md`.
`/newagentlink` is a **single snapshot** for starting a new session.

Do not implement more product work in the same turn unless the user also asked.

## One-shot rule (mandatory)

| Who | After `/newagentlink` |
| --- | --- |
| **Writer** (this chat) | Create or overwrite the file **once**. Do not edit it in later turns of this conversation. A later `/newagentlink` is a **new** snapshot, not an append. |
| **Reader** (new / sub agent) | Read the file on the **first turn only**. Absorb the facts. Then work from the user, live git, and code. **Do not** re-read, cite as ongoing source, append, or update the file in later rounds. |

Put this banner at the top of every generated file (keep the wording):

```markdown
> **One-shot.** Read this file on the first turn only. After that, ignore it.
> Do not update, append, or re-read it in later rounds. Live git and the user
> are the source of truth from turn two onward.
```

The starter prompt must say the same.

## Path

```text
/tmp/<short-topic>-newagentlink.md
```

- `<short-topic>`: 2–5 kebab-case words from the user's extra text after
  `/newagentlink`, else from the current branch slug or the live task (example:
  `/newagentlink ci sandbox` → `/tmp/ci-sandbox-newagentlink.md`).
- If the user runs `/newagentlink` again for the same topic, **overwrite** with a
  fresh snapshot. Do not append a round log.
- Write to `/tmp`. Do **not** commit it, put it in the repo, or
  `git format-patch` unless the user asks.
- Never write or overwrite `/tmp/<topic>-handoff.md`. That path is the review
  ledger. If a review ledger already exists for the topic, leave it alone.

## Gather before writing (required)

Run a **single** batch of read-only checks. Do not guess SHAs or tags.

```bash
git branch --show-current
git status -sb
git log -1 --format='%H %s'
```

Plus, when they exist: `package.json` version; `git tag -l 'v*-canary.*' | sort -V | tail`;
`git -C wiki branch -avv` and `git -C wiki log -1 --oneline` if `wiki/` is a
separate clone; any in-flight workflow URL the user already cares about.

Read repo `AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` only enough to **point
at** them. Do not paste those rules into the snapshot.

## File contents (required sections)

Write for a reader who has **not** seen this chat. Lead with the one-shot
banner, then live state.

1. **How to start** — read this file **once** on turn one; then follow First
   actions. Do not keep the file in the working set.
2. **Header** — date/time (UTC and user TZ if known), workspace path, previous
   transcript id if available, product name.
3. **Live state** — branch (must name it), HEAD SHA + subject, dirty paths,
   ahead/behind, last GA / canary tag if this repo ships images, wiki SHA if
   relevant, in-flight CI/workflow.
4. **Current task** — what is in progress, what is done, what the next agent
   should do **first**. Mark blocked vs waiting-on-user vs implement-next.
5. **Hard constraints** — do-not list (wrong branch, full test suite, push/tag,
   recreate-the-wrong-service, etc.). Point at `AGENTS.md` instead of restating
   the whole workflow.
6. **Facts already proven** — root cause, official URLs, commands run and
   results, production layout. Include **disproved** theories so they are not
   re-investigated.
7. **Key files** — paths the next agent should open, not a whole-tree dump.
8. **Git / release** — stay on the named branch; whether a canary already
   shipped; push/tag/GA only if the user asks in that turn.
9. **First actions** — numbered, copy-pasteable.

Optional: a short “if X still fails, check Y in this order” section. No novel
fixes unless they are already in the branch.

## Quality bar

- Specific SHAs, paths, commands, and URLs. No “the recent fix”.
- Continuation-oriented. Not a review findings list unless the live task *is*
  a review.
- Short enough to load once: prefer tables and bullets. Omit resolved chat
  tangents.
- Never dump secrets, tokens, message bodies, or Axiom payload content.

## Chat reply (after the file exists)

State the path. Give the starter prompt. Do **not** paste the file back.
Do not offer to keep the snapshot updated.

Starter prompt to give the user:

```text
Read /tmp/<short-topic>-newagentlink.md once on this first turn, then ignore
that file. Do not re-derive the prior investigation. Do not update the
newagentlink file in later rounds.
```
