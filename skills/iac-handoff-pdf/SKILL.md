---
name: iac-handoff-pdf
description: Write or update an environment handoff PDF that tells an application vendor or developer team what an IaC repository provisioned and how to use it (access, identities, network, secrets, deployment). Use when asked for an IaC, infrastructure, environment, vendor provisioning, or developer handoff document or PDF. Not the review-handoff ledger. Done when the generator script and the PDF are in the IaC repository, every value traces to applied IaC or a live query, the secret scan prints nothing, and every rendered page was viewed.
---

# IaC Handoff PDF

Write the handoff a platform team sends once an environment is applied. The reader cannot see the IaC repository. The handoff gives exact names, addresses, identities, copy-ready commands, the check for each task, and what is withheld or not ready yet.

**REQUIRED SUB-SKILL:** `verification-before-completion` before you claim the PDF is delivered.

## Load First

- `references/handoff-guide.md`: section catalog, task pattern, writing rules, secrets policy, versioning, layout, verification commands.
- `scripts/handoff_template.py`: runnable reportlab template with the page theme, helpers, and a placeholder story for every catalog section.
- `scripts/pil-logo.png`: the title-block logo the template loads from its own folder.

For other PDF work (merge, extract, forms), use `pdf-document`. Change the topology diagram only with `excalidraw-diagram`, and only when the user asks.

## Setup

- `uv`. The template declares `reportlab==4.5.1` as PEP 723 inline metadata, so `uv run --script` installs it in an isolated environment. Do not install reportlab into system Python.
- Poppler for `pdfinfo`, `pdftotext`, and `pdftoppm`. Install with `bash scripts/install_deps.sh office-system` from the architect-library root, or the system package `poppler-utils`.
- Optional fonts: Liberation Sans and DejaVu Sans Mono under `/usr/share/fonts`. Without them the template uses Helvetica and Courier.

`<skill-root>` is `skills/iac-handoff-pdf` in this repo, and `~/.cursor/skills/iac-handoff-pdf`, `~/.copilot/skills/iac-handoff-pdf`, `~/.claude/skills/iac-handoff-pdf`, or `~/.agents/skills/iac-handoff-pdf` when installed.

## Workflow

1. **Scope.** Confirm the environment, the reader, the sender, and the version. If the repo already has a handoff PDF and generator for that environment, this is an update: read both and add the new version at the top of `HISTORY`.
2. **Gather facts from applied state.** Read the environment roots, their outputs, the apply guide, and the design document. Query live values that the repo does not record (read-only `terraform output`, `terraform state show`, `az ... show`). Do not run `plan` or `apply` for the handoff. List each value you will state with its source. Designed but unapplied items go to "What is not ready yet".
3. **Pick sections.** Walk the catalog in `references/handoff-guide.md`. Keep a section only when the environment has something for it. Order tasks the way the reader performs them.
4. **Write the generator.** Copy `<skill-root>/scripts/handoff_template.py` to `scripts/build_<env>_handoff.py` and `<skill-root>/scripts/pil-logo.png` to `scripts/pil-logo.png` in the IaC repo, or edit the existing generator. Set `PROJECT_ENV`, `SCOPE`, `REGION`, `SENDER`, `RECIPIENT`, `AUDIENCE`, and `HISTORY`. Replace every placeholder section with real content, following the task pattern. Delete the `section()` calls you did not keep: numbers and `[[key]]` references follow. An existing generator without `HISTORY` and `section(key, title, ...)` predates this template: move its text into a fresh copy, and fill the earlier `HISTORY` entries from its git log.
5. **Build.** `uv run --script scripts/build_<env>_handoff.py docs/<project>-<env>-<audience>-handoff.pdf`, adding `--diagram design-docs/<topology>.png` when the repo has a topology PNG. Keep an existing PDF file name.
6. **Verify.** Run the commands under "Verification commands" in the guide: metadata, secret scan, placeholder scan, render each page, view each PNG. Fix and rebuild until all pass.
7. **Deliver.** Report the PDF path, the version, the page count, and the open items from "What is not ready yet". Commit the generator, `scripts/pil-logo.png`, and the PDF together only after the user confirms. `git add -n` must list all three; force-add one the IaC repo ignores (`*.png`, `*.pdf`) with `git add -f`. The commit message lists the content changes.

## Rules that are easy to skip

| Shortcut | Do instead |
|----------|------------|
| Copy a value from the design document | Confirm it is applied: environment outputs, apply guide status, or a live query |
| Paste a connection string to show the format | Name the secret and where it lives; show the format with `<placeholder>` |
| Write "the database" or a short name | Use the exact resource name each time |
| Leave a template placeholder such as `<team>` | Replace it, or delete the sentence |
| Describe a task without a check | Add the check command and the expected result |
| Treat a built PDF as delivered | View every rendered page |
| Edit the PDF directly | Edit the generator and rebuild |
| Add a questions section | Send open questions in a separate message; the handoff states what exists |
| Type a section number in the text | Write `[[key]]`; the template prints the number as a link and fails the build on a key that matches no section |
| Leave a missing item for the last pages | Repeat it in the "Not ready yet" line on the first page |
| Bold a request the reader must make to another team, or an action they lack permission for | One `note_box` at the top of that section, with the rule as its heading. Steps, checks and plain facts stay in body text |

## Delivery Checklist

1. Generator at `scripts/build_<env>_handoff.py`, logo at `scripts/pil-logo.png`, and PDF under `docs/` in the IaC repository.
2. `pdfinfo` Title and Subject show the new version.
3. Secret scan prints nothing.
4. Placeholder scan shows only values the reader chooses.
5. Every rendered page viewed: logo and title block, the "Not ready yet" line and "Before you start" box on page 1, header and footer, tables, code blocks, no orphan heading or lead-in line, appendix readable.
6. Every name, address, and port in the Environment, Provisioned resources, and host name tables traced to applied IaC or a live query.
