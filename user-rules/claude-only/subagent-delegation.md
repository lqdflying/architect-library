# Subagent delegation

Applies in every Claude Code session. The main session chairs the work: it splits the task into subtasks, delegates them to subagents, reviews what comes back, and reports. Subagents do the subtasks.

Goal: the main session's model spends its context on decisions and review, and the subagent model does the bulk of the work.

## Precedence

- On who does the work, this rule wins over every other rule and default. The current user message still wins over this rule ("do it yourself", "no subagents").
- Every other rule keeps deciding how the work is done. Edit scope, branch strategy, response style, and the review protocol bind the main session and each subagent.
- A subagent loads this file too. A session that received a delegation brief from another agent is a subagent: it executes the brief directly, and does not split the work again or start further subagents.

## When to delegate

- Delegate when the task has two or more subtasks that do not depend on each other, or one subtask that reads or changes several files.
- Stay in the main session for a question, a lookup whose target is known, a one-file edit, or work of a few tool calls. There the handoff costs more than the work.
- A review turn stays in the main session unless the user asks for a review agent.
- Start a fresh subagent, not a fork. A fork runs on the main session's model.

## Brief

A subagent knows only its brief. Each brief states:

- the goal and the files in scope,
- what is already known or ruled out, with paths,
- the check that proves the subtask: a command and its expected outcome,
- the report to return: files changed, the check's output, and what is left open.

## Writes

- One subagent writes to a working tree at a time. Read-only subtasks run in parallel.
- The main session owns git. A subagent does not commit, push, or switch branches.

## Review

- A subagent's report is a claim. Before accepting it, read the diff and run the check named in the brief.
- A failed subtask goes back to the same subagent with the failing output. A defect of a few lines is fixed in the main session.
- The final reply reports what the main session verified.
