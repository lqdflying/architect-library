---
name: newagentlink
description: Write a one-shot /tmp continuation markdown for a new agent
---

Follow the global skill at `~/.cursor/skills/newagentlink/SKILL.md`.

Write `/tmp/<short-topic>-newagentlink.md` once so a new agent can continue this
task. It is a single snapshot: the new agent reads it on the first turn only,
then never reuses or updates it. Gather live git state first. In chat, return
only the path plus this starter prompt (do not paste the file):

Read /tmp/<short-topic>-newagentlink.md once on this first turn, then ignore that file. Do not re-derive the prior investigation. Do not update the newagentlink file in later rounds.
