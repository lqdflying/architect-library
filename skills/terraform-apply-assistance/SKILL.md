---
name: terraform-apply-assistance
description: "Use when fixing Terraform validation/plan/apply errors, reviewing a commit hash through HEAD for the current apply scope, creating a focused branch and preparing Terraform fixes for user review, or reviewing Terraform plan output to decide whether apply is OK. Triggers: terraform error, apply failed, plan output, provider error, invalid argument, missing variable, permission issue, destructive plan, replacement, branch workflow, compare new plan, is this plan safe, evaluate apply. Uses Context7 for Terraform provider docs and Microsoft Learn MCP for Azure/RBAC/service behavior."
argument-hint: "<commit-hash optional> plus Terraform error text, plan output, or branch context"
---

# Terraform Apply Fix And Plan Review

## When To Use

Use this skill when the user needs help to:
- Fix a Terraform validation, plan, or apply error in this repo.
- Review all code planned for this apply from a commit hash through `HEAD`, including the hash commit itself.
- Create or switch to a focused branch, edit Terraform, validate the fix, then pause for user review before any commit or push.
- Review a pasted `terraform plan` and say whether apply is OK.
- Compare repeated plan outputs after fixes and confirm whether earlier risks disappeared.
- Evaluate destructive Terraform actions, replacements, identity/RBAC changes, networking/routing changes, data-plane permissions, service configuration changes, cross-phase dependencies, and environment prerequisites.

This is an implementation-and-review workflow, not a broad commit audit. For full commit-range audits, use `terraform-commit-review`.

## Hard Constraints

- This host is a coding/review host only. Do not run `terraform init`, `terraform plan`, `terraform apply`, or `terraform state` locally.
- Terraform plan/apply operations happen on the Terraform operations VM. Ask the user to paste output, then analyze it here.
- Azure CLI may be used here only for read-only inspection when already authenticated and when needed.
- Do not commit or push automatically. After editing and validation, pause and let the user review the diff; commit or push only after the user explicitly instructs you to proceed.
- Do not revert unrelated user work. If the worktree has unrelated edits, preserve them and stage only intended files.

## Required Official Documentation Checks

Use official docs before making or defending a technical claim about provider schema, Azure behavior, RBAC, or service constraints.

- Terraform provider docs: use Context7 tools `mcp_context7_resolve-library-id` and `mcp_context7_query-docs`.
- Azure service docs and RBAC role definitions: use Microsoft Learn MCP tools `mcp_microsoft_lea_microsoft_docs_search`, `mcp_microsoft_lea_microsoft_docs_fetch`, and, for examples, `mcp_microsoft_lea_microsoft_code_sample_search`.
- If a required MCP tool is deferred and not loaded, use `tool_search` first to load the exact tool.
- Cite official source URLs in findings and final explanations when docs were used.

## Workflow

### 1. Establish Apply Scope

If the user provides a commit hash, treat that hash as the start of the current apply scope and include that commit in the review through `HEAD`.

Use these commands to understand the scope:

```bash
git show <commit-hash> --stat
git log --oneline <commit-hash>^..HEAD
git diff --stat <commit-hash>^..HEAD
git diff --name-only <commit-hash>^..HEAD
```

Important: use `<commit-hash>^..HEAD`, not `<commit-hash>..HEAD`, because the start commit itself must be included.

If no commit hash is provided, infer the apply scope from session history and current repo state:
- Recent commits made in the session.
- The active branch and its upstream.
- The latest pushed commit(s) mentioned by the user.
- The resources shown in pasted plan output.
- Any prior plan-review context in the conversation.

If inference is uncertain, say what scope you inferred and what evidence supports it. Ask only if the ambiguity changes whether apply is safe.

### 2. Triage The Error Or Plan

Start from the concrete anchor supplied by the user:
- Terraform error resource address, file, and line.
- Pasted `terraform plan` resource action.
- Commit hash or branch.
- Module/phase name.

Read only enough local code to form one falsifiable hypothesis and one cheap check. Prefer:
- The failing resource block.
- The calling phase module.
- The relevant variables/outputs/provider alias.
- A neighboring resource that already follows the correct pattern.

If the user pasted a plan, classify it first:
- `+ create`: new resources or previously unmanaged resources.
- `~ update in-place`: changed config without replacement.
- `- destroy`: highest-risk bucket; identify why Terraform says it will destroy.
- `-/+ replace`: highest-risk bucket; identify the force-replacement attribute.

Always scan plan output and diffs for new Microsoft Entra service principal or Enterprise Application creation. Highlight these explicitly because some Terraform platform identities do not have directory privileges to create app registrations, service principals, or enterprise applications. Treat direct Entra resources such as `azuread_application`, `azuread_service_principal`, and related password/federated-credential resources as a likely apply blocker unless the required Entra privileges are confirmed. Also call out Azure-managed identities (`azurerm_user_assigned_identity` and `identity { type = "SystemAssigned" }`) because Microsoft documents managed identities as service-principal objects visible under Enterprise Applications; distinguish them from standalone app registrations, but still require the user to confirm the deployment identity is allowed to create those managed identity principals.

For apply-scope reviews, read the changed Terraform and documentation files from the inferred or provided range. Focus on deployable inputs and resource behavior first, then docs/runbooks that affect prerequisites or apply decisions.

### 3. Create Or Confirm A Working Branch

Before editing Terraform, inspect git state:

```bash
git status --short --branch
git branch --show-current
git remote -v
```

If this session already created or switched to a non-protected branch for Terraform apply assistance, continue using that same branch for subsequent blockers, follow-up fixes, plan iterations, or vendor-requested tweaks in the same apply workflow. Do not create a new branch just because the next error is in a different phase or resource. Treat the current session branch as the working branch unless the user explicitly asks for a separate branch or project instructions say the branch is protected/mainline.

For a concrete Terraform validation, plan, or apply error that requires editing deployable Terraform inputs or code, create the focused fix branch before the first edit only when the current branch is protected/mainline or no session apply-fix branch has been checked out yet. Treat branches named by project instructions as protected, mainline, release, apply, or integration branches as unsuitable working branches for error fixes. If project instructions do not identify which branches are protected/mainline and the current branch is not obviously a session apply-fix branch, ask the user to identify the correct base/working-branch policy before editing.

If no suitable branch exists yet, create one date-based session branch instead of a per-error branch. Prefer this naming pattern:

```bash
git switch -c terraform-apply-fix-YYYYMMDD
```

If a branch with that date already exists, add a short suffix such as `terraform-apply-fix-YYYYMMDD-2` or `terraform-apply-fix-YYYYMMDD-<short-scope>`. Do not push the new branch unless the user explicitly instructs you to push it. If a non-protected session branch already exists for the active apply workflow, continue on it. Avoid creating stacked/unrelated branches unless the user asks.

### 4. Diagnose With Docs And Local Evidence

Use local code and official docs together:

- For AzureRM resource arguments, use Context7 to verify exact attributes, types, identity blocks, provider aliases, and computed values.
- For Azure service behavior, data-plane permissions, RBAC roles, networking behavior, immutability, replacement risk, SKU constraints, or service limits, use Microsoft Learn MCP.
- For external design repos, scripts, runbooks, or application code referenced by the user, read the real implementation before deciding required permissions or prerequisites.

Do not infer permissions, dependencies, or safety from resource names alone. Map the actual operation to the minimum required capability:
- Read operations need read permissions on the exact source object or scope.
- Write/import/update operations need write permissions only on the exact target object or scope.
- One side of a data movement flow does not automatically require the same permissions as the other side.
- A deployment identity, runtime identity, and sync/automation identity may each need different permissions.

### 5. Make The Smallest Correct Edit

Patch only the files needed for the apply blocker or confirmed plan risk.

Typical edit surfaces:
- `phase*/main.tf`, `variables.tf`, `outputs.tf`, `provider.tf`.
- `modules/*/main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`.
- Relevant docs/instructions only when they would otherwise mislead the next apply.

Avoid unrelated refactors and broad formatting. Run `terraform fmt` only on touched `.tf` or real `.tfvars` files, not on `*.tfvars.example` files because Terraform fmt does not process those extensions.

### 6. Validate Locally Without Plan/Apply

After the first substantive edit, immediately run the narrowest available checks:

```bash
terraform fmt -check <touched .tf/.tfvars files>
terraform -chdir=<phase_dir> validate
git diff --check -- <touched files>
```

If `terraform validate` cannot run because providers are not initialized on this host, say that clearly and rely on formatting, diff checks, and plan output from the operations VM.

Never claim the fix is complete until fresh validation output confirms it.

### 7. Pause For User Review Before Commit Or Push

When validation passes and the agent changed Terraform code, stop before committing or pushing. Give the user a concise review package:

- Branch name.
- Files changed.
- Validation commands and results.
- Short explanation of the fix and any remaining risks.
- Suggested commit message, if useful.

Do not run `git add`, `git commit`, or `git push` unless the user explicitly instructs you to do so after reviewing the changes. When the user does instruct you to commit or push, stage only intended files:

```bash
git status --short --branch
git add <intended files>
git commit -m "<concise imperative message>"
git push
git status --short --branch
```

After a user-approved commit or push, report the final git state. If the user has not approved commit or push yet, final status should clearly show the uncommitted reviewable changes.

### 8. Review The Next Terraform Plan

When the user pastes a new plan, compare it against:
- The previous plan output in the conversation.
- The intended code changes.
- Recent commits that caused the plan behavior.
- Current config and external design docs when relevant.

For every plan iteration, explicitly state:
- What disappeared from the previous plan.
- What new actions remain.
- Which actions are expected.
- Which actions are risky or require confirmation.
- Whether the plan is OK to apply, not OK to apply, or conditionally OK.

Re-raise any unresolved risk every time. Do not stop mentioning a destructive action just because it was already discussed. Mark it as accepted only if the user explicitly confirms the operational intent.

## Plan Evaluation Rubric

### Usually OK

- In-place updates that match verified provider schema and do not remove an existing dependency.
- Creating new supporting resources that are referenced by the configuration, have clear ownership, and do not conflict with existing names or scopes.
- Adding a missing least-privilege permission, identity binding, provider alias, variable, or output that is required by verified code/design.
- Adding documentation, examples, tags, diagnostics, or outputs that do not change live resource behavior.
- Creating additive records, rules, listeners, routes, or endpoints for a planned rollout when existing production paths remain intact.

### Needs Confirmation

- Any destroy or replacement, even if Terraform explains it as missing from configuration.
- Any change to routing, DNS, firewall, NSG, private endpoint, load balancer, gateway, origin, listener, probe, backend, or path mapping behavior.
- Any identity, RBAC, access policy, secret, certificate, key, public access, or private access change.
- Any new Microsoft Entra service principal or Enterprise Application, including standalone AzureAD app/SP resources and managed identities that will create service-principal objects behind the scenes.
- Any change to remote-state outputs, module inputs, provider aliases, backend config, required variables, or cross-phase contracts.
- Any broadening of access, public exposure, egress allowlists, admin privileges, or shared-service scope.
- Any plan that includes placeholders, unknown operational readiness, manually managed resources, or resources shared by multiple environments.

### Not OK Until Fixed

- The original validation/plan/apply blocker is still present.
- Provider docs show an invalid argument, wrong type, deprecated-only pattern, or incompatible resource combination.
- Azure service docs show the change is unsupported, will cause unexpected replacement, or risks data loss.
- A live dependency will be destroyed or replaced without a verified migration, replacement, or rollback path.
- Required inputs are missing: identity, role assignment, federated credential, provider alias, remote-state output, backend value, environment variable, secret, certificate, DNS prerequisite, or manually provisioned dependency.
- The plan explicitly creates Microsoft Entra app registrations, service principals, or Enterprise Applications and the Terraform platform identity's Entra privileges are not confirmed.
- The plan removes or weakens required access for a runtime/deployment identity, or grants broader access than the verified operation needs without explicit approval.

## Response Format For Plan Reviews

Use grouped tables so large plans stay readable. Do not put every resource into one giant table.

When this skill is explicitly invoked, always include `## 7. Execution Summary` after the review tables, regardless of whether the user supplied a commit hash. If there are blockers, the execution summary must say apply is blocked and list what must be fixed first. If there are no blockers, it must provide the evaluated apply steps and prerequisites.

```markdown
This plan is <OK / conditionally OK / not OK> for apply.

## Summary

| Result | Assessment |
|---|---|
| Apply scope | <commit hash through HEAD, or inferred session scope> |
| Terraform blocker | <none / present> |
| Overall apply status | <OK / conditionally OK / not OK> |
| Main risk | <short statement> |
| Recommendation | <apply / do not apply / apply only after confirming X> |

## Adds

| Group | Action | What will be added | Risk / note |
|---|---|---|---|
| <DNS / Networking / Identity / App / Data / Docs / Other> | `+ create` | ... | ... |

## Changes

| Group | Action | What will change | Risk / note |
|---|---|---|---|
| <group> | `~ update in-place` | ... | ... |

## Destroys / Replacements

| Group | Action | What will be removed or replaced | Risk / required confirmation |
|---|---|---|---|
| <group> | `- destroy` / `-/+ replace` | ... | ... |

## Risks To Highlight

| Risk | Why it matters | Required confirmation or fix |
|---|---|---|
| ... | ... | ... |

## Conclusion

<Short apply recommendation. If there is risk, highlight it directly and repeat the required confirmation.>

## 7. Execution Summary

Terraform apply is <blocked / not approved yet / conditionally OK / OK> because <short reason>. State whether `terraform init/plan/apply/state` was not run locally because this host is review-only and Terraform operations belong on the operations VM.

Apply scope: <commit hash through HEAD, or inferred session scope with evidence>.

Environment prerequisites before apply:

- Global prerequisites (set once for all phases):

```bash
export ARM_TENANT_ID="..."
export ARM_CLIENT_ID="..."
export ARM_CLIENT_SECRET="..."
```

- Common prerequisite(s) shared by multiple phases (only list when needed):

```bash
export TF_VAR_default_subscription_id="..."
```

- Phase-specific prerequisites and evaluated apply order (split per phase, one command block each):

## Phase 1: <phase_dir>

Additional env vars for this phase (exclude global/common vars):
- `<phase-specific TF_VAR_* or readiness prerequisite>`

```bash
cd <phase_dir>
terraform init -backend-config=backend.tfvars
terraform plan -out=tfplan
terraform apply tfplan
```

## Phase 2: <next_phase_dir>

Additional env vars for this phase (exclude global/common vars):
- `<phase-specific TF_VAR_* or readiness prerequisite>`
- `None` if there are no additional env vars.

```bash
cd ../<next_phase_dir>
terraform init -backend-config=backend.tfvars
terraform plan -out=tfplan
terraform apply tfplan
```

Phases that do not need apply: <Phase list and reason, or none known from code/plan review alone>.

Post-apply validation checks:

- <Terraform output / Azure resource / DNS / route / health probe / RBAC check>.
- <Runtime or connectivity validation>.
- <Follow-up plan should show no unexpected drift>.

Docs alignment: <State whether vendor docs/change logs align with evaluated code and plan. If not, identify the drift and whether it is captured as a risk/finding.>

Remaining risks: <None, accepted risks, or unresolved risks that must be raised again.>
```

Recommended grouping categories:
- DNS and name resolution.
- Network security and routing.
- Identity, RBAC, access policies, secrets, keys, and certificates.
- Application Gateway, load balancers, Front Door, gateways, listeners, probes, origins, and routes.
- Compute, AKS, Databricks, app services, and application backends.
- Storage, databases, Event Hubs, data-plane services, and private endpoints.
- Terraform wiring: providers, variables, outputs, remote state, backend, modules.
- Documentation and runbooks.

For small plans, omit empty sections. For broad plans, keep each table focused and summarize repeated resources by group instead of listing every low-value nested block.

### Execution Summary Rules

The execution summary is mandatory when this skill is explicitly called, even for a plan-only review and even when no commit hash is provided.

It must answer:
- Whether Terraform apply is blocked or can proceed with risks accepted.
- The evaluated apply scope: provided hash through `HEAD`, or inferred session scope.
- Environment-variable prerequisites before any apply command summary:
	- Global `ARM_*` prerequisites listed once at the beginning.
	- Common prerequisites shared by multiple phases listed once (for example `TF_VAR_default_subscription_id`) when applicable.
	- Phase-specific object IDs or sensitive `TF_VAR_*` values listed only under each affected phase.
- Which phases need apply, in exact evaluated order, and which phases do not need apply.
- For each phase that needs apply, use a `## Phase N: <phase_dir>` heading, include an "Additional env vars" list for that phase, and provide one fenced `bash` command block with `terraform init -backend-config=backend.tfvars`, `terraform plan -out=tfplan`, and `terraform apply tfplan`.
- Post-apply validation checks and runtime follow-ups.
- Whether docs/change logs align with the evaluated apply path; if not, mention the drift but keep the execution guidance based on code/config/plan evidence.

If the apply is not OK, do not provide commands as if the user should run them. Instead, list the blocked command stage and the fix/confirmation needed before proceeding.

Use the runbook style for `## 7. Execution Summary`: short conclusion paragraph, global prerequisite block first, optional common prerequisite block second, then per-phase sections titled `## Phase N: <phase_dir>` with additional env vars and per-phase fenced `bash` command blocks. Do not repeat global `ARM_*` vars in each phase section. Keep post-apply validation as plain bullets. Do not use task-list bullets (`- [ ]`) by default unless the user explicitly asks for a checklist.

## Completion Checks

Before saying the task is done:
- Apply scope is clear: either a provided commit hash through `HEAD`, or a stated scope inferred from session history.
- A focused branch exists when Terraform code was changed, unless the current branch was already the user-approved working branch.
- Intended edits are validated and left for user review; no commit or push has been made unless the user explicitly instructed it after review.
- `git status --short --branch` is reported, and any uncommitted reviewable changes are explained.
- Fresh validation output has been run and checked.
- Any pasted plan has been evaluated for create/update/destroy actions.
- Any unresolved risk is explicitly raised again.
- Official docs have been consulted for provider/Azure/RBAC claims.
- The final answer includes `## 7. Execution Summary` with apply decision, prerequisites, phase order, operations-VM command guidance, post-apply checks, docs alignment, and remaining risks.

## Example Prompts

- `/terraform-apply-assistance Terraform apply failed with this error: ...`
- `/terraform-apply-assistance 10509e26872a539eee1dd7110e93d65efc238a0e Review this apply scope and plan.`
- `/terraform-apply-assistance Review this Phase 1 plan and tell me if apply is OK: ...`
- `/terraform-apply-assistance Fix this AzureRM provider error, create a branch, validate, and pause for my review before commit or push.`
- `/terraform-apply-assistance Compare this new plan with the previous one and tell me what risk remains.`
