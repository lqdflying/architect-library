# iac-handoff-pdf

Agent skill for the environment handoff a platform team sends to an application vendor or developer team after an IaC apply. The output is a versioned PDF built from a generator script committed in the IaC repository.

## Setup

- `uv` runs `scripts/handoff_template.py`; its inline metadata pins `reportlab==4.5.1`.
- Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`) for verification: `bash scripts/install_deps.sh office-system` from the architect-library root.
- Optional: Liberation Sans and DejaVu Sans Mono under `/usr/share/fonts`. Without them the template uses Helvetica and Courier.

Build the template sample:

```bash
uv run --script scripts/handoff_template.py /tmp/handoff-sample.pdf
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Agent workflow and delivery checklist |
| `references/handoff-guide.md` | Section catalog, task pattern, writing rules, secrets policy, versioning, layout, verification commands |
| `scripts/handoff_template.py` | reportlab template: page theme, helpers, automatic section numbers with linked references and PDF bookmarks, version history, placeholder story, optional landscape topology appendix |
| `scripts/pil-logo.png` | Title-block logo; copy it next to the generator |

## Design sources

The structure combines two applied handoffs: an AKS vendor letter ("Changes" summary, account disambiguation, task sections with checks, guardrail table, "What this letter does not include") and an App Service handoff ("Before you start" box, private endpoint table, secret status, settings ownership, contact table, topology appendix). The visual theme follows the App Service handoff. Code blocks use the AKS letter's shaded box, and the title block carries the PIL logo.
