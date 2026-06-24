# terraform-apply-fix-review

Fix Terraform validation/plan/apply errors, create fix branches, and review plan output to decide whether apply is safe. Includes a plan evaluation rubric (Usually OK / Needs Confirmation / Not OK Until Fixed) and iterative plan comparison across fix cycles.

## Use when

- Fixing a Terraform validation, plan, or apply error
- Creating a branch, committing, and pushing a Terraform fix
- Reviewing pasted `terraform plan` output for safety
- Comparing successive plan outputs after fixes
- Evaluating destructive actions, replacements, identity/RBAC changes

## Prerequisites

- **Git** — branch, commit, push workflow
- **Context7 MCP server** — Terraform provider docs (AzureRM, Databricks, Kubernetes, etc.)
- **Microsoft Learn MCP server** — Azure service behavior, RBAC built-in roles, networking constraints

No Python, Office, or Node.js runtime dependencies are required. Terraform CLI is not run locally (plan/apply happen on the operations VM).

## Related skills

- `terraform-commit-review` — full commit-range audit (broader scope)
- `verification-before-completion` — evidence before completion claims

Install: `bash scripts/install_library.sh skills cursor` from the architect-library repo.
