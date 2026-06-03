# PowerPoint Presentation Skill

Create, edit, and validate Microsoft PowerPoint architecture presentations.

## Use When

- The user asks for a `.pptx` file.
- The artifact is an executive deck, solution overview, technical walkthrough, migration plan, roadmap, or architecture review pack.
- The task requires template analysis, slide duplication, thumbnails, text extraction, or PPTX validation.

## Setup

Install the shared Office toolkit dependencies from the installed skills root:

```bash
cd ../_shared/office-tools
bash install_deps.sh
```

For creating PPTX files from scratch, install the Node package used by the guide:

```bash
npm install -g pptxgenjs
```

Optional icon generation support:

```bash
npm install -g react-icons react react-dom sharp
```

## References

- `SKILL.md` - agent workflow
- `references/pptx-guide.md` - PPTX creation, template editing, and visual QA details
- `../_shared/office-tools/` - validation, unpack, pack, thumbnail, slide, cleanup, and extraction tools
