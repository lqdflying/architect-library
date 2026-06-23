---
name: terraform-commit-review
description: "Comprehensive Terraform IaC and documentation review across a git commit range. Use when asked to review commits, summarize changes, audit what a vendor did, or find issues in Terraform changes. Triggers: 'review commits', 'review changes', 'what did vendor change', 'review from commit X to HEAD', 'audit PR', 'cross-phase review'. Covers: correctness, security (OWASP/RBAC), naming conventions, destructive changes, provider argument validation, missing trailing newlines, cross-phase dependency consistency, documentation/runbook accuracy, and apply execution summaries."
argument-hint: "<from-commit>..<to-commit> or just <from-commit> (defaults to HEAD). The from-commit itself is always included in the review."
---

# Terraform Commit Review

## When to Use
- User asks to review a commit range (`from X to HEAD`, `since commit X`)
- User asks what a vendor/team changed and whether it's correct
- User wants a comprehensive audit of Terraform changes before `terraform apply`
- User wants to catch issues after a PR merge

## Procedure

### Step 1 — Establish Commit Range
```bash
# Show the from-commit itself
git show <from-commit> --stat

# Show all commits AFTER the from-commit up to HEAD
git log --oneline <from-commit>..HEAD
git diff <from-commit>..HEAD --stat
```
The `<from-commit>` itself **must also be reviewed** — run `git show <from-commit>` to read its full diff. Then review all commits after it. Understand the full scope before diving in.

### Step 2 — Read Each Changed File in Parallel
Group files by phase/module/docs and read them concurrently:
- `modules/*/main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`
- `phase*/main.tf`, `provider.tf`, `variables.tf`, `terraform.tfvars`
- `phase*/rbac_*.json`, `phase*/rbac_*.json`
- Documentation and runbooks changed in the same range: `README.md`, `docs/**/*.md`, `changes/**/*.md`, phase/module `README.md`, and any `*.example` files that document variables or apply steps

> **Documentation parity rule:** Reviews must not only check whether Terraform code is correct. They must also diff all related vendor-provided documentation and runbooks, then verify that the docs accurately describe the code, required environment variables, apply order, phase ownership, prerequisites, outputs, post-deployment steps, and known pending work. If a document is wrong, stale, incomplete, or contradicts code, include it as a normal review issue in the output.

> **Example tfvars classification rule:** `*.tfvars.example`, `*.tfvars.oa.example`, `*.tfvars.prod.example`, and similar example/template files are documentation aids, not the deployed Terraform variable files. Missing or stale values in these files are documentation/template issues by default. Do **not** classify them as `CRITICAL`, and do **not** mark them as blocking Terraform validation/plan/apply unless the same missing value also affects a real deployable file such as `terraform.tfvars`, `*.auto.tfvars`, module inputs, or root module configuration.

### Step 3 — Verify Against Official Docs (MANDATORY)

For **any** finding, fix proposal, or design question — before flagging or confirming correctness, always look up the authoritative source using the available MCP tools:

1. **Context7** (`mcp_context7_resolve-library-id` → `mcp_context7_query-docs`): Use for Terraform provider docs (AzureRM, Databricks, Kubernetes, etc.), provider resource arguments, resource constraints, and known library behaviour.
2. **Microsoft Learn MCP** (`mcp_microsoftdocs_microsoft_docs_search` / `mcp_microsoftdocs_microsoft_docs_fetch`): Use for Azure service behaviour, Azure RBAC built-in roles, Azure Networking constraints, AKS, Databricks on Azure, and any Azure-specific limits or immutability requirements.

> **Rule:** Do not rely solely on training-data knowledge when answering questions about Terraform provider arguments, Azure service limits, or RBAC role definitions. Always verify against the official source first, then cite the source URL in the findings.

> **Learning & Explanation Rule:** When the user asks a learning or explanation question (e.g. "how does X work", "what is Y", "why does Z happen"), also look up the topic via Context7 and/or Microsoft Learn MCP and **include the source URL(s) at the end of the answer** so the user can read further.

Always cite the source URL for every finding in the final report.

### Step 4 — Run the Review Checklist

#### A. Provider / HCL Correctness
- [ ] Attribute types match the provider schema (scalar vs list/set, `destination_port_range` vs `destination_port_ranges`)
- [ ] No deprecated arguments (check provider version constraints in `versions.tf`)
- [ ] Resource attribute combinations are compatible (e.g. `data_security_mode = USER_ISOLATION` requires `num_workers >= 1`)
- [ ] Cluster policies / SKU constraints respected (e.g. Event Hub `partition_count` is **immutable** on Standard SKU)
- [ ] `depends_on` not used where implicit reference already exists

#### B. Security & RBAC (OWASP-aligned)
- [ ] No `Contributor` at resource group scope without documented justification and env guard
- [ ] Sensitive variables (`*_password`, `*_secret`, `*_key`) are `sensitive = true` and set via env vars, not hardcoded in `.tfvars`
- [ ] No credentials committed in any file (`*.tfvars`, `*.json`, `provider.tf`)
- [ ] Least-privilege: verify each new role assignment is the minimum needed (check MS Learn for built-in role definitions)
- [ ] UAMI vs SAMI appropriate for the use case
- [ ] Comments/docs accurately describe what the code does — misleading comments near security config are flagged

#### C. Destructive Change Detection
- [ ] `partition_count` changes on existing Event Hubs (Standard SKU — immutable, forces destroy/recreate)
- [ ] `name` changes on any resource (forces destroy/recreate)
- [ ] `subnet_id` changes on VMs, AKS node pools
- [ ] Storage account `account_replication_type` or `account_kind` changes
- [ ] Key Vault `sku_name` changes
- [ ] Any `lifecycle { prevent_destroy }` removed

#### D. Naming Conventions
Check resource names against the project's naming convention. Define a convention such as `{org}-{env}-{service}-{region}-{seq}-{type}` (hyphenated) / `{org}{env}{service}{region}{seq}{name}` (no-hyphen for globally unique resources like storage accounts). Teams should document their convention in the repo and reference it here.
- [ ] Resource names follow the convention for their type
- [ ] Storage container names are lowercase-only, max 63 chars
- [ ] No uppercase in storage account names or ACR names

#### E. Cross-Phase Consistency
- [ ] New outputs added in Phase N that are consumed in Phase N+1/N+2 exist in the correct `outputs.tf`
- [ ] `terraform_remote_state` keys match the backend state keys defined in `provider.tf`
- [ ] Variables added to modules are passed from the phase that calls the module
- [ ] `terraform.tfvars.example` updated to include any new required variables (especially sensitive ones with `export TF_VAR_...` instructions). If this is missing only from example files, report it as documentation/template drift, not as an apply blocker.

#### F. Code Quality
- [ ] All files end with a trailing newline (POSIX requirement, causes noisy diffs if missing)
- [ ] No placeholder values left that must be replaced before apply (backend.tfvars documented correctly)
- [ ] Comments are accurate and not misleading
- [ ] Hardcoded versions that could be managed by data sources (e.g. `spark_version`, `node_type_id`)

#### G. Documentation / Runbook Consistency
- [ ] Every changed Terraform behavior is reflected in related docs (`README.md`, `docs/**`, `changes/**`, phase READMEs)
- [ ] Vendor change logs list the same affected phases/modules as the actual diff
- [ ] Apply order in docs matches cross-phase dependencies and remote-state consumption
- [ ] New required variables are documented in `.tfvars.example`, READMEs, and runbooks, including whether they are set in `.tfvars` or via `TF_VAR_*`
- [ ] Sensitive values are documented as environment variables and are not shown as hardcoded committed values
- [ ] Post-deployment TODOs are accurate, scoped, and not presented as completed work
- [ ] Documentation issues are added to **Issues Found** and **Summarization to Vendor** like code issues, with clickable file links and exact line anchors

### Step 5 — Produce the Summary

Structure the output as:

> **Heading requirement:** Every top-level report section must be a level-2 Markdown heading (`##`). Do not use bold-only labels for the main sections.

## 1. Intent Summary

What did the changes set out to do? (2–4 sentences per major feature)

## 2. Per-Phase Change Table

For each phase/module changed:

| Change | Correct? | Notes |
|--------|----------|-------|
| ... | ✅ / ⚠️ / ❌ | ... |

## 3. Issues Found

Ordered by severity:

| # | Severity | Issue | File | Blocks Terraform Apply? | Status |
|---|----------|-------|------|-------------------------|--------|
| 1 | CRITICAL | ... | ... | Yes — validation/plan/apply blocker | Open |

For **Blocks Terraform Apply?**, use one of these direct forms:
- `Yes — validation blocker`
- `Yes — plan/apply blocker`
- `No — runtime risk`
- `No — security/promotion risk`
- `No — code quality / maintainability risk`

Do not leave apply impact implicit in the severity or prose. The user must be able to scan the table and immediately know whether Terraform can continue.

## 4. Summarization to Vendor

For every issue in **Issues Found** with `Status = Open`, provide a vendor-ready comment block using the mandatory wrapper format below. This section is meant to be copied into GitHub review comments.

> **Hard requirement:** Never collapse this section into a normal review comment or a standalone GitHub comment body. Every open issue must include the rendered title, clickable `Code position:` line, exact source snippet, `Comment in GitHub as follows:`, and fenced `text` copy block. If any of those wrapper elements are missing, the report is incomplete.

For each issue, include:

1. The matching issue ID from the **Issues Found** table (for example, `Issue ID: #1`) outside the copy block.
2. A rendered Markdown title outside the copy block so the reviewer can quickly identify the issue.
3. A `Blocks Terraform Apply?` line outside the copy block, using the same value as the **Issues Found** table.
4. A `Code position:` line with a clickable workspace-relative file link anchored to the exact starting line, the Terraform resource/module/symbol name (or documentation section/key), and the line range.
5. A short source snippet from the reviewed file so the reviewer can cross-check the exact code being discussed.
6. The line `Comment in GitHub as follows:`.
7. A fenced `text` block containing the Markdown comment body to paste into GitHub. Use a `text` fence so Copilot Chat does not render the Markdown comment prematurely.

Mandatory per-issue vendor format:

`````markdown
## #<issue_number> — <Concise Issue Title>

Issue ID: **#<issue_number>**

Blocks Terraform Apply? **<Yes/No — exact value matching Issues Found table>**

Code position: [<filename>](<workspace-relative/path.tf>#L<start>), `<terraform_resource_or_symbol_or_doc_section>`, around lines <start>-<end>

Source snippet to cross-check:

```hcl
<small exact snippet from the file>
```

Use `hcl` for Terraform snippets, `json` for RBAC JSON snippets, and `markdown` for documentation/runbook snippets.

Comment in GitHub as follows:

````text
### #<issue_number> — <Concise Issue Title>

In `<workspace-relative/path.tf>`, <state the problem in one or two clear sentences>.

Current config:
- `<key line 1>`
- `<key line 2>`
- `<key line 3>`

Impact: <say whether this blocks Terraform plan/apply or is a runtime/security/promotion risk>.

Recommendation: <specific fix request for the vendor>.

Suggested config:
- `<suggested line 1>`
- `<suggested line 2>`

Docs:
- <official source URL>
- <official source URL>
````
`````

Vendor-summary rules:
- The issue number in each vendor block MUST match the `#` value from the **Issues Found** table. Do not renumber, omit, or infer issue IDs from section order.
- The rendered title outside the copy block MUST start with `## #<issue_number> — ...`.
- The `Issue ID: **#<issue_number>**` line outside the copy block MUST appear in every vendor block.
- The GitHub-copy block title MUST start with `### #<issue_number> — ...`.
- Keep wording direct and short; do not include long explanations.
- Do not include `vscode-file://`, `file://`, local absolute paths, or editor-generated links.
- The `Code position:` file reference outside the GitHub-copy block MUST be a clickable Markdown link with a workspace-relative path and `#LNN` anchor. Do not wrap that file link in backticks.
- The `Blocks Terraform Apply?` line outside the GitHub-copy block MUST appear in every vendor block and MUST match the issue's **Issues Found** table value.
- The `Code position:` display text MUST be the filename only (for example, `[main.tf](apex_phase1_networking/main.tf#L942)`), while the target contains the full workspace-relative path and exact line anchor.
- The `Code position:` line number MUST be exact. Before writing the vendor section, run `grep_search` for each issue's resource/symbol/key line and use the returned 1-based line number. Do not guess or use only approximate line ranges.
- The `Impact:` line inside each GitHub-copy block MUST explicitly say whether the issue blocks Terraform validation/plan/apply. Use phrasing like `Impact: This blocks Terraform validation/plan/apply for Phase 1.` or `Impact: This does not block Terraform apply; it is a runtime/security/promotion risk.`
- Use only official source URLs already consulted for the finding.
- If the issue is not a Terraform apply blocker, state that clearly and label the impact as runtime/security/promotion risk.
- If the issue has no concrete suggested config, replace `Suggested config:` with `Acceptance criteria:` and list what the fix must satisfy.

Vendor-summary self-check before finalizing:
- [ ] Every open issue in **Issues Found** has a matching vendor block.
- [ ] Every vendor block starts with `## #<issue_number> — <Concise Issue Title>` outside the copy block.
- [ ] Every vendor block has `Issue ID: **#<issue_number>**` outside the copy block, matching the **Issues Found** table row.
- [ ] Every vendor block has `Blocks Terraform Apply? **<value>**` outside the copy block, matching the table.
- [ ] Every vendor block has a clickable `Code position:` file link with a workspace-relative `#LNN` anchor outside the copy block.
- [ ] Every `Code position:` link jumps to an exact line returned by `grep_search`.
- [ ] Every vendor block has `Source snippet to cross-check:` followed by a fenced snippet using the correct language (`hcl`, `json`, `markdown`, etc.).
- [ ] Every vendor block has `Comment in GitHub as follows:` followed by a fenced `text` block.
- [ ] The fenced `text` block contains the GitHub comment body only; the outer wrapper stays outside the copy block.
- [ ] The fenced `text` block title starts with `### #<issue_number> — ...`, matching the outer issue ID and the **Issues Found** table row.
- [ ] Every row in **Issues Found** has a `Blocks Terraform Apply?` value.
- [ ] Every vendor-block `Impact:` line explicitly says whether Terraform validation/plan/apply is blocked.
- [ ] Documentation/runbook issues are included as normal issues when found, not only mentioned in prose.
- [ ] If there are no open apply-blocking issues, the report includes `## 7. Execution Summary` with apply status, environment-variable prerequisites before any apply-order command block, phase order, apply commands, validation checks, and vendor-doc tally.
- [ ] Top-level report sections use `## 1. Intent Summary`, `## 2. Per-Phase Change Table`, `## 3. Issues Found`, `## 4. Summarization to Vendor`, `## 5. New Issues Discovered`, `## 6. Source URLs`, and, when applicable, `## 7. Execution Summary`.

### Linking Policy for Tables (MANDATORY)

Every row in the **Per-Phase Change Table** and the **Issues Found** table MUST include a clickable file link in the File/Phase column so the user can jump directly to the relevant code. Follow these exact rules:

1. **Always include a link** — never put a plain-text filename.

2. **Link format** — use a workspace-relative path with a line anchor:
   ```
   [filename](relative/path/to/file.ext#LNN)
   ```
   - Display text: **filename only** (e.g. `main.tf`), NOT the full path.
   - Target: workspace-relative path + `#LNN` (1-based line number).
   - Example: `[main.tf](modules/networking/main.tf#L329)`

3. **Get exact line numbers** — before writing the report, run `grep_search` to locate the exact line of each changed rule/resource. Do NOT guess or estimate line numbers.

4. **Why short display text** — VS Code chat linkification requires the display text to match only the filename (not the full path) when a `#L` anchor is appended. Using the full path as display text breaks the clickable link.

5. **Do NOT use backticks** around file links — wrapping in backticks disables linkification.

Example correct rows:
```markdown
| [main.tf](modules/networking/main.tf#L329) | New rule `allow-os-and-ms-updates` | ⚠️ | ip.im present |
| [main.tf](phase1_networking/main.tf#L79)   | Budget resource                    | ⚠️ | Missing provider |
```

Severity levels:
- **CRITICAL**: Will fail `terraform plan` or `terraform apply`
- **HIGH**: Will fail silently or cause data loss / security breach
- **MEDIUM**: Security risk or will cause problems when promoted to OA/PROD
- **LOW**: Code quality, maintainability, best practice violations

`*.tfvars.example` and other example/template file issues must normally be **LOW** documentation/template issues with `Blocks Terraform Apply? = No — code quality / maintainability risk`. Escalate above LOW only when the example-file defect also proves a real deployable configuration, module interface, or runbook command will fail or create a security/runtime risk.

## 5. New Issues Discovered

Any issues found during the deep review that weren't in the original report.

## 6. Source URLs

List all official documentation URLs consulted.

## 7. Execution Summary

Include this section whenever there are **no open issues** whose **Blocks Terraform Apply?** value starts with `Yes —`.

Keep it concise and operational. It must answer:
- Whether Terraform apply is blocked or can proceed with non-blocking risks accepted
- Environment-variable prerequisites **before** any apply-order command block:
   - New environment variables introduced by the reviewed range
   - Existing environment variables still required for the affected phases
   - Phase-specific object IDs or sensitive `TF_VAR_*` values required by affected phases
- Which phases need to be applied, in exact order, and which phases do **not** need apply
- Recommended operations-VM commands (`init -backend-config=backend.tfvars`, `plan -out=tfplan`, `apply tfplan`)
- Post-apply validation checks and any documented runtime follow-ups
- Whether the execution summary tallies with vendor-provided docs/change logs; if not, name the doc issue and include it in **Issues Found**

> **Prerequisites ordering rule:** Treat required `ARM_*` and `TF_VAR_*` values as deployment prerequisites. In the execution summary, list them before the apply-order or operations-VM command block, not after it.

## General Terraform Review Principles

### Provider Argument Types
- Always verify scalar vs collection attribute names against the provider schema — a common mistake is using the singular form (e.g. `destination_port_range`) when a list is needed (requires `destination_port_ranges`)
- Check the provider version in `versions.tf` and look up arguments against that exact version via Context7

### Immutable Resource Properties
Common Azure resources with immutable fields that force destroy/recreate if changed:
- **Event Hub** (`azurerm_eventhub`): `partition_count` — immutable on Basic/Standard SKU
- **Storage Account** (`azurerm_storage_account`): `account_kind`, `account_replication_type`
- **Key Vault** (`azurerm_key_vault`): `sku_name`
- **Subnet** (`azurerm_subnet`): changing `address_prefixes` may affect dependent resources
- Any resource `name` change → destroy/recreate

### Security Baselines
- Sensitive variables (`*_password`, `*_secret`, `*_key`, `*_token`) must be `sensitive = true` and set via env vars, not hardcoded in any committed file
- `Contributor` at resource group scope is a high-privilege grant — flag if not clearly justified and env-guarded
- RBAC follows least-privilege: always verify the minimum sufficient built-in role via Microsoft Learn MCP

### Cross-Module/Phase Consistency
- Every new `output` added in a lower phase must be consumed correctly by the higher phase referencing it via `terraform_remote_state`
- Every new `variable` added to a module must be passed from the calling phase
- `terraform.tfvars.example` must document every new required variable, especially sensitive ones with `export TF_VAR_...` instructions. Missing entries in example tfvars files alone are documentation/template drift and should not be marked as blocking Terraform apply.

### Code Quality
- All files must end with a trailing newline (POSIX standard)
- `depends_on` is redundant when an implicit reference already exists on the same attribute
- Hardcoded resource SKUs or versions should use data sources where the provider supports them
