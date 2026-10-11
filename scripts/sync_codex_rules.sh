#!/usr/bin/env bash
# Generate Codex user instructions from the canonical Cursor user rules.
# Usage: bash scripts/sync_codex_rules.sh [--check]
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAIRS="response-style:response-style edit-scope:edit-scope branch-strategy:branch-strategy review-handoff-reconciliation:review-handoff docs-lookup:docs-lookup temp-validators:temp-validators"
MODE="${1:-write}"
case "$MODE" in
  write|--check) ;;
  -h|--help) sed -n '2,3p' "$0"; exit 0 ;;
  *) echo "Unknown argument: $MODE" >&2; exit 1 ;;
esac

render() {
  awk '
    NR == 1 && $0 == "---" { fm = 1; next }
    fm == 1 { if ($0 == "---") { fm = 0; after_fm = 1 }; next }
    after_fm == 1 && $0 == "" { after_fm = 0; next }
    {
      after_fm = 0
      if (!opener && sub(/^Applies in every (Cursor )?project\./, "Applies in every Codex chat.")) opener = 1
      gsub(/~\/\.cursor\/skills\//, "~/.agents/skills/")
      gsub(/`~\/\.cursor\/`/, "the active Codex home (`$CODEX_HOME`, default `~/.codex/`)")
      gsub(/~\/\.copilot\//, "~/.agents/")
      print
    }
  ' "$1"
}

[[ "$MODE" == "--check" ]] || mkdir -p "${REPO}/user-rules/codex"
stale=0
for pair in $PAIRS; do
  src="${REPO}/user-rules/cursor/${pair%%:*}.mdc"
  dest="${REPO}/user-rules/codex/${pair##*:}.md"
  if [[ ! -f "$src" ]]; then
    echo "Missing Cursor source: ${src}" >&2
    exit 1
  fi
  if [[ "$MODE" == "--check" ]]; then
    if ! cmp -s <(render "$src") "$dest"; then
      echo "Stale Codex fragment: ${dest} (run: bash scripts/sync_codex_rules.sh)" >&2
      stale=1
    fi
  else
    render "$src" > "$dest"
    echo "Wrote ${dest}"
  fi
done
exit "$stale"
