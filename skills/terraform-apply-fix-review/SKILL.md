---
name: terraform-apply-fix-review
description: "Use when fixing Terraform validation/plan/apply errors, creating a branch/commit/push for Terraform code fixes, or reviewing Terraform plan output to decide whether apply is OK. Triggers: terraform error, apply failed, plan output, provider error, invalid argument, missing variable, permission issue, destructive plan, replacement, branch commit push, compare new plan, is this plan safe, evaluate apply. Uses Context7 for Terraform provider docs and Microsoft Learn MCP for Azure/RBAC/service behavior."
argument-hint: "Terraform error text, plan output, or commit/branch context"
---

# Terraform Apply Fix And Plan Review

## When To Use

Use this skill when the user needs help to:
- Fix a Terraform validation, plan, or apply error in this repo.
- Create a branch, edit Terraform, commit, and push the fix.
- Review a pasted `terraform plan` and say whether apply is OK.
- Compare repeated plan outputs after fixes and confirm whether earlier risks disappeared.
- Evaluate destructive Terraform actions, replacements, identity/RBAC changes, networking/routing changes, data-plane permissions, service configuration changes, cross-phase dependencies, and environment prerequisites.

This is an implementation-and-review workflow, not a broad commit audit. For full commit-range audits, use `terraform-commit-review`.

## Hard Constraints

- This host is a coding/review host only. Do not run `terraform init`, `terraform plan`, `terraform apply`, or `terraform state` locally.
- Terraform plan/apply operations happen on the Terraform operations VM. Ask the user to paste output, then analyze it here.
- Azure CLI may be used here only for read-only inspection when already authenticated and when needed.
- Push project branches to the project remote (e.g. `origin`) unless the user explicitly asks for another remote.
- Do not revert unrelated user work. If the worktree has unrelated edits, preserve them and stage only intended files.

## Required Official Documentation Checks

Use official docs before making or defending a technical claim about provider schema, Azure behavior, RBAC, or service constraints.

- Terraform provider docs: use Context7 tools `mcp_context7_resolve-library-id` and `mcp_context7_query-docs`.
- Azure service docs and RBAC role definitions: use Microsoft Learn MCP tools `mcp_microsoft_lea_microsoft_docs_search`, `mcp_microsoft_lea_microsoft_docs_fetch`, and, for examples, `mcp_microsoft_lea_microsoft_code_sample_search`.
- If a required MCP tool is deferred and not loaded, use `tool_search` first to load the exact tool.
- Cite official source URLs in findings and final explanations when docs were used.

## Workflow

### 1. Triage The Error Or Plan

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

### 2. Create Or Confirm A Working Branch

Before editing Terraform, inspect git state:

```bash
git status --short --branch
git branch --show-current
git remote -v
```

If the user has not already placed you on a suitable branch, create a focused branch:

```bash
git switch -c fix/<short-problem-name>
git push -u origin fix/<short-problem-name>
```

If a branch already exists for the active fix, continue on it. Avoid creating stacked/unrelated branches unless the user asks.

### 3. Diagnose With Docs And Local Evidence

Use local code and official docs together:

- For AzureRM resource arguments, use Context7 to verify exact attributes, types, identity blocks, provider aliases, and computed values.
- For Azure service behavior, data-plane permissions, RBAC roles, networking behavior, immutability, replacement risk, SKU constraints, or service limits, use Microsoft Learn MCP.
- For external design repos, scripts, runbooks, or application code referenced by the user, read the real implementation before deciding required permissions or prerequisites.

Do not infer permissions, dependencies, or safety from resource names alone. Map the actual operation to the minimum required capability:
- Read operations need read permissions on the exact source object or scope.
- Write/import/update operations need write permissions only on the exact target object or scope.
- One side of a data movement flow does not automatically require the same permissions as the other side.
- A deployment identity, runtime identity, and sync/automation identity may each need different permissions.

### 4. Make The Smallest Correct Edit

Patch only the files needed for the apply blocker or confirmed plan risk.

Typical edit surfaces:
- `phase*/main.tf`, `variables.tf`, `outputs.tf`, `provider.tf`.
- `modules/*/main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`.
- Relevant docs/instructions only when they would otherwise mislead the next apply.

Avoid unrelated refactors and broad formatting. Run `terraform fmt` only on touched `.tf` or real `.tfvars` files, not on `*.tfvars.example` files because Terraform fmt does not process those extensions.

### 5. Validate Locally Without Plan/Apply

After the first substantive edit, immediately run the narrowest available checks:

```bash
terraform fmt -check <touched .tf/.tfvars files>
terraform -chdir=<phase_dir> validate
git diff --check -- <touched files>
```

If `terraform validate` cannot run because providers are not initialized on this host, say that clearly and rely on formatting, diff checks, and plan output from the operations VM.

Never claim the fix is complete until fresh validation output confirms it.

### 6. Commit And Push The Fix

When validation passes and the agent changed Terraform code, commit and push the fix unless the user explicitly says not to. Commit only intended files:

```bash
git status --short --branch
git add <intended files>
git commit -m "<concise imperative message>"
git push
git status --short --branch
```

Final git state should be clean and synced with the remote branch.

### 7. Review The Next Terraform Plan

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
- Any change to remote-state outputs, module inputs, provider aliases, backend config, required variables, or cross-phase contracts.
- Any broadening of access, public exposure, egress allowlists, admin privileges, or shared-service scope.
- Any plan that includes placeholders, unknown operational readiness, manually managed resources, or resources shared by multiple environments.

### Not OK Until Fixed

- The original validation/plan/apply blocker is still present.
- Provider docs show an invalid argument, wrong type, deprecated-only pattern, or incompatible resource combination.
- Azure service docs show the change is unsupported, will cause unexpected replacement, or risks data loss.
- A live dependency will be destroyed or replaced without a verified migration, replacement, or rollback path.
- Required inputs are missing: identity, role assignment, federated credential, provider alias, remote-state output, backend value, environment variable, secret, certificate, DNS prerequisite, or manually provisioned dependency.
- The plan removes or weakens required access for a runtime/deployment identity, or grants broader access than the verified operation needs without explicit approval.

## Response Format For Plan Reviews

Keep plan answers short but decisive:

```markdown
This plan is <OK / conditionally OK / not OK> for apply.

Resolved since last plan:
- ...

Expected changes:
- ...

Risks to confirm before apply:
- ...

Blocking issues:
- ...

Recommendation: <apply / do not apply / apply only after confirming X>.
```

If the plan is broad, say so even when the immediate fix is correct.

## Completion Checks

Before saying the task is done:
- A branch exists and is pushed to the remote when code was changed.
- All intended edits are committed, unless the user explicitly asked not to commit.
- `git status --short --branch` is clean or any remaining changes are explained.
- Fresh validation output has been run and checked.
- Any pasted plan has been evaluated for create/update/destroy actions.
- Any unresolved risk is explicitly raised again.
- Official docs have been consulted for provider/Azure/RBAC claims.

## Example Prompts

- `/terraform-apply-fix-review Terraform apply failed with this error: ...`
- `/terraform-apply-fix-review Review this Phase 1 plan and tell me if apply is OK: ...`
- `/terraform-apply-fix-review Fix this AzureRM provider error, create a branch, commit, and push.`
- `/terraform-apply-fix-review Compare this new plan with the previous one and tell me what risk remains.`
