# IaC handoff guide

Reference for `iac-handoff-pdf`. A handoff tells one reader, usually an application vendor or a developer team, what an environment provides after the apply and how to use it. The reader has no access to the IaC repository. Write for someone who will copy names, run commands, and report failures.

## Section catalog

Number the sections. Order them in the reader's work order: what exists, how to reach it, who they are, then each task they perform, then what is missing and whom to ask. Keep a section only when the environment has something for it.

| Section | Keep when | Content |
|---------|-----------|---------|
| Title block | Always | The PIL logo on the left. On the right: title `<PROJECT ENV> Infrastructure Handoff`, subtitle `<scope> · <sender> to <recipient> · <region>`, version line `Version N · <date>`. Then one paragraph: provisioned and verified on `<date>`, every topic in section order, which environments are not provisioned yet, and `Secret values are not included.` |
| New in version N | Every version after 1.0 | `**New in version N**, applied on <date>:` followed by one bullet per change since the previous version, each with the section it touches: `A Windows VM, <name> at <ip>, is provisioned. See section 9.` |
| Before you start | The reader must request access before anything works | Amber note box. One numbered item per request: what to request, from which team, and what it unblocks. Example: VPN access to private endpoints from the network team. |
| Environment | Always | Item / Value table: subscription, tenant ID, region, resource group, and the jump host or entry address the reader uses. |
| Provisioned resources | Always | Purpose / Name / Configuration table: one row per resource with its exact name and the settings the reader relies on (version, size, TLS, keys disabled). Then one paragraph: which resources have public network access disabled, and what is not provisioned yet. |
| Private endpoints and host names | Private endpoints, custom DNS, or controlled egress exist | Host name / Address / Port table. Tell the reader to use the normal host name, not the `privatelink` name. Then one paragraph: the egress address or range, and whom to ask for another destination. |
| Identities and access | Always | Identity / Used by / Access granted table, one row per sign-in account, cluster account, and workload identity. Show only the IDs the reader configures, usually the client ID. When two accounts share a name, add `These are different accounts. Do not use one in place of another.` Bullets after the table: what fails without the identity (for example, access keys disabled) and whom to ask for another role. |
| Sign in and check access | People sign in to a jump host, portal, or cluster | Ordered steps, a copy-ready command block, then `What <account> can do:` with one bullet per allowed action and one for what it cannot do. |
| Task sections | One per task the reader performs | Publish the application, read secrets, connect to a database, pull images, store files, deploy. Each follows the task pattern below. |
| Guardrails | A policy denies requests | Object / Rule table: what is denied, on which operation, and what to use instead. Existing objects keep running. |
| Secrets | The application reads secrets | When the reader cannot write the vault, open with a callout that names the request path: `To add or change any secret in <vault>, submit a <request type> to <team>.` Then Secret name / Purpose / Readable by / Status (`Entered`, `Waiting for your value`, `Not created`). Who supplies each value and who enters it. The reference format or client call that reads it. Never a value. |
| Settings you own | IaC sets values once and then ignores changes | Which settings the reader owns, which properties IaC manages (`the next apply reverts the change`), and what to restore if the resource is recreated. |
| Cutover or first deployment | A change needs coordination | Numbered steps that name who acts in each step and what confirms it. Then the rollback and the window it stays available. |
| What is not ready yet | Anything designed is not applied | One bullet per item: what is missing, who confirms it, and the effect on the reader until then (`connections time out`). |
| What this document does not include | Always | The secrets, admin credentials, and permissions that are withheld. Then `Reply to <sender> if <A>, <B>, or <C> fails`, listing each failure point the document describes. |
| Whom to contact | More than one team owns something the reader needs | Need / Team table. |
| Appendix: topology | The repo has a topology diagram | Landscape page, the existing PNG, one caption line naming the environment the addresses belong to. |

## Task pattern

Each task section has four parts, in this order:

1. What to do, with exact names: namespace, service account, host, port, secret name.
2. A copy-ready block. Use real names. Use `<placeholder>` only for a value the reader chooses, and say which values those are. A CI fragment says `Generic job fragment, not a complete workflow. Replace all REPLACE_WITH_* values.`
3. The check command and the expected result: `Under parent gateway/internal, Accepted and ResolvedRefs must be True.`
4. The traps, stated as facts:
   - A negative example: `registry.example.io/app-api:1.0.0 is denied because the name does not start with app/.`
   - A misplacement: `A label on the Deployment metadata is not enough.`
   - What not to set: `The webhook sets AZURE_CLIENT_ID. Do not set it in the manifest.`
   - A behavior change from the previous platform: `The old timeout limited the wait between two reads; this one limits the whole request.`

## Writing rules

- Every value comes from applied state. Sources, in order: the environment roots and their outputs, the apply guide, the design document, then a live query. A value designed but not applied goes to "What is not ready yet", not to "Provisioned resources".
- Use the exact resource name every time. No shortened names, no "the database" when two databases exist.
- Give an address with its port and protocol: `172.16.62.4, TCP 443`.
- One fact per sentence. Active voice. Present tense for what exists.
- Name the actor in every step that crosses teams: `<sender> changes the secret, and you deploy the token version.`
- Cross-reference by section number: `See section 6.` After renumbering, search the script for every `section N`.
- Name teams, not people, unless the project assigned named contacts for that support path.
- Do not explain IaC internals the reader cannot act on (module names, state layout, apply phases).
- A handoff states what exists and how to use it. It asks the reader nothing: send open questions in a separate message, not in the PDF.

## Secrets policy

- Never put a secret value in the handoff, the generator, a commit message, or the chat: passwords, keys, connection strings, tokens, kubeconfig contents, SAS URLs.
- Client IDs, tenant IDs, subscription IDs, object IDs, and private addresses are identifiers, not secrets. Include one only when the reader configures or checks it.
- Name the secret and where it lives. The opening paragraph ends `Secret values are not included.`

## Versioning

- Version 1.0 is the first handoff. Each content change bumps the version: 1.1, 1.2, and so on. Set `VERSION` and `REVISED`; `ISSUED` stays the date of version 1.0, and the footer shows both.
- Every version after 1.0 starts with "New in version N".
- Send the handoff after the apply that creates what it describes. If it goes out before an apply, that item belongs in "What is not ready yet".
- Rebuild the PDF and commit it together with the generator and `scripts/pil-logo.png`. The commit message lists the content changes, for example `Update the <PROJECT ENV> handoff to version 1.4` followed by one line per changed section.

## File layout in the IaC repository

| File | Purpose |
|------|---------|
| `scripts/build_<env>_handoff.py` | Generator copied from `scripts/handoff_template.py`. Holds the text, `VERSION`, `ISSUED`, `REVISED`, and `CHANGES`. |
| `scripts/pil-logo.png` | Title-block logo, copied from `<skill-root>/scripts/pil-logo.png`. |
| `docs/<project>-<env>-<audience>-handoff.pdf` | The built handoff. Keep an existing file name when the repo already has one. |
| `design-docs/<topology>.png` | Existing diagram for the appendix. Do not create one for the handoff. |

One generator and one PDF per environment and audience.

## Layout

The template implements this layout. Keep it unless the repo already has a different handoff style.

- A4 portrait, 18 mm side margins. Header: `<PROJECT ENV> infrastructure handoff for <recipient>` on the left, the audience marking (`Internal and vendor use`) on the right, 7.6 pt muted grey, above a thin rule. Footer: a thin rule, then `Prepared by <sender>, <issued> · Version N, revised <date>` on the left and the page number on the right.
- Title block: the PIL logo, 14 mm high, on the left; the title, subtitle, and version line on the right, vertically centred.
- Fonts: Liberation Sans for text and DejaVu Sans Mono for identifiers and code, found under `/usr/share/fonts`. Without them the template falls back to Helvetica and Courier, which keep the same metrics.
- Colors: ink `#111111`, navy `#1f3a5f` for the title and headings, muted `#5f6b7a` for subtitle, notes, header, and footer, rule `#c7d0da`, table header fill `#e8eef6`, code box fill `#f3f5f7` with border `#c9cfd6` and text `#1f2933`, note box `#fff3dc` with border `#d4900f` and heading `#8a5a00`.
- Sizes: title 21 pt, subtitle 11 pt, section heading 12.5 pt, subsection heading 9.8 pt, body 9.4 pt, table cells 8.2 pt, code 7.6 pt. Identifiers (`` `name` `` in the template helpers) render in monospace at 6.8 pt.
- Callouts: the amber note box (`note_box`) marks what the reader must do before or instead of acting alone: the "Before you start" access requests, and a request path that replaces a permission the reader lacks, such as adding a secret. Put the callout at the top of its section, with a heading that states the rule, and use at most one per section. A plain fact stays in body text. Bold text alone is not a callout.
- Tables: header row repeats on each page, top-aligned cells, light grid. Column widths are fractions that sum to 1; give the long column the most width.
- Code blocks: shaded box with a thin border, one block per command group, short enough to fit on one page. Wrap a lead-in line and the block or list it introduces in `keep()`.
- `section()` keeps each heading with its first flowable, or with the whole group when the first flowable is a `keep()`, so no heading ends a page. Pass `style=H3` for a subsection.
- PDF metadata: title `<PROJECT ENV> infrastructure handoff, version N`, author is the sender, subject includes the recipient and the version.

## Verification commands

Run from the IaC repository root. `<pdf>` is the built handoff.

```bash
uv run --script scripts/build_<env>_handoff.py <pdf> [--diagram design-docs/<topology>.png]
pdfinfo <pdf> | grep -E 'Title|Subject|Pages'
pdftotext <pdf> - | grep -n -i -E '(password|passwd|pwd|secret|token|key)=[^[:space:]<]|AccountKey=|SharedAccessKey=|-----BEGIN|eyJ[A-Za-z0-9_-]{10,}\.|[?&]sig=|[A-Za-z0-9+/]{40,}={0,2}'
pdftotext <pdf> - | grep -n -E '<[A-Za-z][^>]*>'
pdftoppm -r 80 -png <pdf> <scratch-dir>/page
```

- `pdfinfo`: Title and Subject show the new version.
- The secret scan prints nothing. A hit is a stop: remove the value, rebuild, rescan.
- The placeholder scan lists every `<...>` left in the text. Each one must be a value the reader chooses, such as `<tag>`. Template placeholders like `<team>` mean the handoff is unfinished.
- View every rendered page: header and footer on each page, no clipped table cell or code line, no heading alone at a page bottom, appendix readable.
- Compare each name, address, and port in the Environment, Provisioned resources, and host name tables against its source once more.
