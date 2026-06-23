# terraform-commit-review

Comprehensive Terraform IaC code review skill for auditing changes across a git commit range. Covers provider/HCL correctness, security & RBAC, destructive change detection, naming conventions, cross-phase consistency, and code quality.

## Use when

- Reviewing a commit range (`from X to HEAD`, `since commit X`)
- Auditing what a vendor or team changed and whether it is correct
- Pre-apply review of Terraform changes
- Post-merge issue detection

## Prerequisites

- **Git** — commit range diffs (`git show`, `git log`, `git diff`)
- **Context7 MCP server** — Terraform provider docs (AzureRM, Databricks, Kubernetes, etc.)
- **Microsoft Learn MCP server** — Azure service behavior, RBAC built-in roles, networking constraints

No Python, Office, or Node.js runtime dependencies are required.

## Related skills

- `verification-before-completion` — evidence before completion claims
- `security-auditor` (agent) — broader security review beyond Terraform

Install: `bash scripts/install_library.sh skills cursor` from the architect-library repo.
