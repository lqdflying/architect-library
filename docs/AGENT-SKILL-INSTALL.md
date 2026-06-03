# Agent guide: install Architect Document Skills (Cursor / Copilot)

Use this document when the user asks to install, update, or fix skills from the **architect-doc-skill** repository. Follow it literally; do not invent alternate paths.

**Editing this repository?** Cursor loads [`.cursor/rules/`](../.cursor/rules/) automatically. Follow [MAINTAINING-SKILLS.md](MAINTAINING-SKILLS.md) whenever you add a skill, workflow step, or dependency—update those rules, `SKILL.md` `description`, and this install doc—not only scripts or README.

## What you are installing

This repo publishes **six installable folders** under `skills/` (not one monolithic skill):

| Folder | Type | Required |
|--------|------|----------|
| `excalidraw-diagram` | Cursor/Copilot skill | Yes, if diagrams are needed |
| `word-document` | Cursor/Copilot skill | Yes, if DOCX is needed |
| `powerpoint-presentation` | Cursor/Copilot skill | Yes, if PPTX is needed |
| `spreadsheet-document` | Cursor/Copilot skill | Yes, if XLSX/spreadsheet work is needed |
| `pdf-document` | Cursor/Copilot skill | Yes, if PDF work is needed |
| `_shared` | Support files (not a standalone skill) | **Yes** whenever Word, PowerPoint, or spreadsheet skills are installed |

Word, PowerPoint, and spreadsheet skills reference Office tools via `../_shared/office-tools/`. If `_shared` is missing or not a **sibling** of those folders, paths break.

## Agent execution rules (read after install)

When you load a skill, follow its `SKILL.md` and `references/`. These repo-wide rules apply:

| Skill | Before marking the task complete |
|-------|----------------------------------|
| **excalidraw-diagram** | Render `.excalidraw` → PNG, **view** the image, fix in a loop |
| **word-document** | Validate DOCX; explicit table styling; deliver `.docx` only (no generator scripts beside deliverable unless asked) |
| **powerpoint-presentation** | Validate PPTX; run **`thumbnail` layout preview on every deck** (grid + `--per-slide` at 150 DPI), **view** images, fix overflow/overlap; install `bash scripts/install_deps.sh office-system` if `soffice`/`pdftoppm` missing—do not skip preview unless the user waives visual QA |
| **spreadsheet-document** | Deliver `.xlsx`; if formulas: `office_tools.py recalc` until zero errors; `office-system` for recalc |
| **pdf-document** | Deliver `.pdf`; form fills: validation scripts per `references/forms.md` |

**PowerPoint is not done** when the `.pptx` file exists. It is done when layout preview has been run and reviewed (or the user explicitly waived).

**Word** does not require LibreOffice for new docx-js decks. **PowerPoint** requires LibreOffice Impress + Poppler for every delivery. **Spreadsheet** formula recalc requires LibreOffice (`office-system`).

**Source of truth for skill packages:** `<repo>/skills/<name>/`  
**`<repo>/.cursor/`** is tracked in git (project rules and Cursor config). Do **not** copy `skills/*` into `<repo>/.cursor/skills/` — that duplicates `skills/` and confuses installs.

---

## Step 0: Locate the repository root

Set `REPO` to the clone path, for example:

```bash
REPO=/path/to/architect-doc-skill
cd "$REPO"
```

Confirm the layout exists:

```bash
test -f "$REPO/skills/excalidraw-diagram/SKILL.md" && \
test -f "$REPO/skills/word-document/SKILL.md" && \
test -f "$REPO/skills/spreadsheet-document/SKILL.md" && \
test -f "$REPO/skills/pdf-document/SKILL.md" && \
test -f "$REPO/skills/_shared/office-tools/office_tools.py" && \
echo "OK: repo layout valid"
```

If any check fails, stop and ask the user for the correct clone path.

---

## Step 1: Choose install scope

| User intent | Install location |
|-------------|------------------|
| “Use in all my projects” / global Cursor or Copilot | User home skills directory (below) |
| “Only this project” / team repo | Project skills directory (below) |
| Both | Prefer global unless the user explicitly wants project-only |

Do **not** install only `excalidraw-diagram` when the user wants the full architect-doc set.

---

## Step 2: Remove legacy standalone Excalidraw (if present)

Older installs may be a **standalone** Excalidraw skill (single folder, sometimes with its own `.git`), not this monorepo layout.

Before copying, remove outdated global copies so Cursor does not load stale `SKILL.md`:

```bash
# Cursor legacy
rm -rf ~/.cursor/skills/excalidraw-diagram

# Copilot legacy (if it exists)
rm -rf ~/.copilot/skills/excalidraw-diagram
```

Only remove project-local copies if the user asked to refresh **this** project:

```bash
rm -rf .cursor/skills/excalidraw-diagram
rm -rf .github/skills/excalidraw-diagram
```

---

## Patch / upgrade Cursor skills (agent default)

When the user says **patch**, **upgrade**, **install**, or **refresh** skills — or you just changed skills in this repo — **run this** (global Cursor). Do not stop at editing only `$REPO/skills/`.

| Action | What happens under `~/.cursor/skills/` |
|--------|----------------------------------------|
| **New** skill in repo | Folder copied in the bundle (e.g. `spreadsheet-document`) |
| **Existing** skill (Word, PPT, …) | Old folder **removed**, fresh `cp -a` from repo (**patch**) |
| **`_shared`** | Always refreshed with Word/PPT/spreadsheet installs |

```bash
REPO=/path/to/architect-doc-skill
CURSOR=~/.cursor/skills
BUNDLE="excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document _shared"

mkdir -p "$CURSOR"
for legacy in docx pptx xlsx pdf; do rm -rf "$CURSOR/$legacy"; done
for name in $BUNDLE; do
  rm -rf "$CURSOR/$name"
  cp -a "$REPO/skills/$name" "$CURSOR/$name"
done
```

Then: verify layout (Step 6), tell the user to **open a new agent chat**.

Project-local install: same loop with `CURSOR=.cursor/skills` from the user’s project root.

Repo rule: [`.cursor/rules/architect-doc-skill-cursor-patch.mdc`](../.cursor/rules/architect-doc-skill-cursor-patch.mdc).

---

## Step 3: Install for Cursor

### Global (recommended for individuals)

```bash
REPO=/path/to/architect-doc-skill
mkdir -p ~/.cursor/skills

for name in excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document _shared; do
  rm -rf ~/.cursor/skills/"$name"
  cp -a "$REPO/skills/$name" ~/.cursor/skills/"$name"
done
```

### Per project (from the user’s project root)

```bash
REPO=/path/to/architect-doc-skill
mkdir -p .cursor/skills

for name in excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document _shared; do
  rm -rf .cursor/skills/"$name"
  cp -a "$REPO/skills/$name" .cursor/skills/"$name"
done
```

**Use `cp -a`** (or `cp -r`) from `$REPO/skills/`, not a symlink to the repo, unless the user explicitly wants a symlinked dev setup.

**Do not** copy the whole `architect-doc-skill` repo into `~/.cursor/skills/` — only the skill folders inside `skills/` (plus `_shared`).

---

## Step 4: Install for VS Code GitHub Copilot

Copilot Agent Skills use different paths than Cursor.

### Global (all workspaces)

```bash
REPO=/path/to/architect-doc-skill
mkdir -p ~/.copilot/skills

for name in excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document _shared; do
  rm -rf ~/.copilot/skills/"$name"
  cp -a "$REPO/skills/$name" ~/.copilot/skills/"$name"
done
```

### Per workspace (project root)

```bash
REPO=/path/to/architect-doc-skill
mkdir -p .github/skills

for name in excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document _shared; do
  rm -rf .github/skills/"$name"
  cp -a "$REPO/skills/$name" .github/skills/"$name"
done
```

Tell the user to **reload VS Code** after installation. Slash commands may appear as `/excalidraw-diagram`, `/word-document`, `/powerpoint-presentation`.

---

## Step 5: Install for Claude Code / OpenCode (optional)

```bash
REPO=/path/to/architect-doc-skill
mkdir -p .claude/skills

for name in excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document _shared; do
  rm -rf .claude/skills/"$name"
  cp -a "$REPO/skills/$name" .claude/skills/"$name"
done
```

Run from the **user’s project root**, not from inside `architect-doc-skill`, unless they develop only in this repo.

---

## Step 6: Verify installation

Run these checks and report results to the user.

### Layout and siblings

```bash
CURSOR=~/.cursor/skills   # or .cursor/skills for per-project

ls -1 "$CURSOR" | sort
# Expect: _shared  excalidraw-diagram  pdf-document  powerpoint-presentation  spreadsheet-document  word-document

test -f "$CURSOR/_shared/office-tools/office_tools.py" && echo "OK: office-tools"
test -f "$CURSOR/word-document/SKILL.md" && echo "OK: word SKILL.md"
```

### No nested git in installed skills

```bash
find "$CURSOR" -maxdepth 2 -name .git -type d
# Expect no output
```

If `.git` appears inside an installed skill, remove that folder and re-copy from `$REPO/skills/` (legacy clone mistake).

### Installed copy matches repo (optional)

```bash
REPO=/path/to/architect-doc-skill
diff -q "$REPO/skills/excalidraw-diagram/SKILL.md" "$CURSOR/excalidraw-diagram/SKILL.md" && echo "OK: excalidraw in sync"
```

### Runtime smoke (optional, after first-time prep)

Only if the user needs PNG rendering or Office XML tools:

```bash
cd "$REPO" && bash scripts/install_deps.sh
cd "$REPO/skills/_shared/office-tools" && uv run python3 office_tools.py --help
```

See [README.md](../README.md) → **First-time preparation** for full runtime setup.

---

## Step 7: Tell the user to reload the editor

After copying skills:

- **Cursor:** start a **new chat** or reload the window so updated `SKILL.md` files load.
- **VS Code:** reload the window.

Skills are matched by the `description` field in each `SKILL.md`; the user does not need to type a slash command for basic use.

---

## First-time machine setup (separate from skill copy)

Installing skills into Cursor/Copilot is **not** the same as installing Python/Playwright/Office runtimes.

| Task | When | Command (from repo root) |
|------|------|---------------------------|
| Skill copy | Per user request / after `git pull` | Steps 3–5 above |
| Runtimes | Once per machine | `bash scripts/install_deps.sh` |
| LibreOffice + Poppler | Once per machine (**required for PowerPoint skill**) | `bash scripts/install_deps.sh office-system` — mandatory PPTX layout preview every delivery; also PDF export, DOCX accept-changes. Word-only / docx-js can skip |
| Offline Excalidraw bundle | Once per machine (optional) | `bash scripts/vendor_excalidraw.sh` |
| New DOCX / PPTX via Node | Once per machine (optional) | `npm install -g docx` / `pptxgenjs` |

Do not run `install_deps.sh` inside `~/.cursor/skills/` — run it from the **repository clone**.

---

## Common mistakes (avoid)

| Mistake | Why it fails |
|---------|----------------|
| Copy only `excalidraw-diagram` | Word/PPT break; user misses new skills |
| Omit `_shared` | `../_shared/office-tools/` paths in Word/PPT skills break |
| Copy repo root into `~/.cursor/skills/` | Wrong layout; Cursor expects one folder per skill name |
| Leave old `~/.cursor/skills/excalidraw-diagram` with nested `.git` | Stale instructions, not from monorepo |
| Copy `skills/*` into `<repo>/.cursor/skills/` | Duplicates `skills/`; use `skills/` as source and `~/.cursor/skills/` or `.cursor/skills/` only for editor install |
| Run `install_deps.sh` in the skills install dir | Dependencies belong in the repo clone paths |
| Deliver PPTX without `thumbnail` layout preview | Run `office_tools.py thumbnail`; install `office-system` first; see `powerpoint-presentation/references/layout-preview.md` |
| Use `file://` for Excalidraw render testing | Use `render_excalidraw.py` (loopback HTTP); see excalidraw README |

---

## Quick reference: paths

| Editor | Global | Per project |
|--------|--------|-------------|
| Cursor | `~/.cursor/skills/<skill-name>/` | `.cursor/skills/<skill-name>/` |
| GitHub Copilot | `~/.copilot/skills/<skill-name>/` | `.github/skills/<skill-name>/` |
| Claude Code | — | `.claude/skills/<skill-name>/` |

Each `<skill-name>` is one of: `excalidraw-diagram`, `word-document`, `powerpoint-presentation`, `spreadsheet-document`, `pdf-document`, `_shared`.

---

## When the user updates the repo (`git pull`) or patches skills

Re-run **Patch / upgrade Cursor skills** (or Step 2 + Step 3): replace every bundle folder under `~/.cursor/skills/`. Then ask them to open a new agent chat.

Optionally verify with `diff` against `$REPO/skills/` as in Step 6.
