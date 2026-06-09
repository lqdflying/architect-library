# Architecture Document Principles

Use these principles across the Architect Library document-oriented skills. They apply to diagrams, Word documents, and PowerPoint decks. For general spreadsheet or PDF tasks, use `spreadsheet-document` or `pdf-document`; apply these principles when the deliverable is architecture-related (models, review packs, exported PDFs).

## Core Standard

Architecture documents should explain decisions, not just describe components. The reader should understand what changed, why it matters, what alternatives were considered, and how the design will be operated safely.

## Required Thinking

Before producing an artifact, identify:

- Audience: executive, architect, engineer, operator, security, or delivery team
- Document purpose: HLD, LLD, ADR, solution overview, migration plan, operating model, roadmap, or review pack
- Decision status: proposal, recommended option, approved design, implementation guide, or post-implementation record
- Evidence: source system facts, constraints, requirements, diagrams, data contracts, APIs, SLAs, cost signals, risks, and assumptions
- Review path: who must approve, what questions they will ask, and what traceability they need

## Document Shape

For substantial architecture documents, cover the relevant sections from this list:

- Executive summary
- Context and goals
- Scope and non-goals
- Current state
- Target state
- Architecture overview
- Key decisions and rationale
- Alternatives considered
- Component design
- Integration and data flows
- Security, privacy, and compliance
- Reliability, availability, and recovery
- Scalability and performance
- Operations, observability, and support
- Migration or rollout plan
- Risks, assumptions, issues, and dependencies
- Cost and licensing considerations
- Testing and validation approach
- Open questions
- Appendices and references

Use only the sections that help the reader. Do not add ceremonial sections with empty content.

## Evidence Rules

- Prefer concrete names, real interfaces, sample payloads, and exact constraints over generic placeholders.
- Mark assumptions explicitly when facts are missing.
- Keep decision records traceable: decision, rationale, alternatives, consequence, and owner.
- Align diagrams, tables, and prose so they tell the same story.
- Word tables: one styling approach per doc (docx-js explicit fills, or python-docx built-in theme + header row—not mixed); verify visually in Word; 9pt table text for dense ADD/compliance docs.
- Parallel subsections should use parallel structure (if 5.1.1 is a tool table, 5.1.2 and 5.1.3 are tables too).
- Deliver `.docx` only; generator scripts live under `scripts/` unless the user requests otherwise.
- PowerPoint decks: **always** run layout preview (`office_tools.py thumbnail` grid + per-slide JPEGs) and inspect images before delivery; install LibreOffice Impress + Poppler (`install_deps.sh --with-system`) if missing.
- Validate generated Office files or rendered diagrams before delivery when tools are available.

## Architecture Decision Records (ADR)

Use ADRs for significant technical decisions — framework choice, data model, auth strategy, API architecture, hosting platform, or any decision expensive to reverse.

### Storage and naming

- **Markdown (in-repo):** `docs/decisions/NNN-short-title.md` with sequential numbering (`001-use-postgresql.md`).
- **Word deliverable:** use the same section structure below in a `.docx` ADR (see `word-document` skill).

### Lifecycle

```
PROPOSED → ACCEPTED → (SUPERSEDED or DEPRECATED)
```

Do not delete old ADRs — they capture historical context. When a decision changes, write a new ADR that references and supersedes the old one.

### ADR template

```markdown
# ADR-NNN: [Short decision title]

## Status
Proposed | Accepted | Superseded by ADR-XXX | Deprecated

## Date
YYYY-MM-DD

## Context
What problem are we solving? Constraints, requirements, and forces at play.

## Decision
What we decided — be specific.

## Alternatives considered

### [Alternative A]
- Pros: …
- Cons: …
- Rejected because: …

### [Alternative B]
…

## Consequences
Positive and negative outcomes, follow-up work, and operational impact.

## Owner
[Name or role accountable for the decision]
```

For Word ADRs, map each heading to a styled heading level and keep alternatives in a table or parallel subsections.

## Tone

Architecture writing should be precise, calm, and decision-oriented. Avoid marketing language unless the artifact is explicitly an external sales or executive pitch deck. Keep wording useful for reviewers who need to approve or implement the design.
