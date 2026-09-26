#!/usr/bin/env bash
# Regenerate the Copilot always-on fragments in user-rules/copilot/ from the
# Cursor sources in user-rules/cursor/, so the two editors cannot drift.
#
# Transform per file:
#   - drop the Cursor YAML frontmatter and the blank line after it
#   - first "Applies in every project." / "Applies in every Cursor project."
#     becomes "Applies in every VS Code Copilot chat."
#   - ~/.cursor/skills/ becomes ~/.copilot/skills/
#
# Usage:
#   bash scripts/sync_copilot_rules.sh          # rewrite user-rules/copilot/*.md
#   bash scripts/sync_copilot_rules.sh --check  # exit 1 if any fragment is stale
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# cursor source name : copilot fragment name
PAIRS="response-style:response-style edit-scope:edit-scope review-handoff-reconciliation:review-handoff"

MODE="${1:-write}"
case "$MODE" in
  write|--check) ;;
  -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
  *) echo "Unknown argument: $MODE" >&2; exit 1 ;;
esac

render() {
  awk '
    NR == 1 && $0 == "---" { fm = 1; next }
    fm == 1 { if ($0 == "---") { fm = 0; after_fm = 1 }; next }
    after_fm == 1 && $0 == "" { after_fm = 0; next }
    {
      after_fm = 0
      if (!opener && sub(/^Applies in every (Cursor )?project\./, "Applies in every VS Code Copilot chat.")) opener = 1
      gsub(/~\/\.cursor\/skills\//, "~/.copilot/skills/")
      print
    }
  ' "$1"
}

stale=0
for pair in $PAIRS; do
  src="${REPO}/user-rules/cursor/${pair%%:*}.mdc"
  dest="${REPO}/user-rules/copilot/${pair##*:}.md"
  if [[ ! -f "$src" ]]; then
    echo "Missing Cursor source: ${src}" >&2
    exit 1
  fi
  if [[ "$MODE" == "--check" ]]; then
    if ! cmp -s <(render "$src") "$dest"; then
      echo "Stale Copilot fragment: ${dest} (run: bash scripts/sync_copilot_rules.sh)" >&2
      stale=1
    fi
  else
    render "$src" > "$dest"
    echo "Wrote ${dest}"
  fi
done

exit "$stale"
