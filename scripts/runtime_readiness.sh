#!/usr/bin/env bash
# Print artifact runtime readiness (Node, npm globals, python-docx) and capability hints.
# Usage: bash scripts/runtime_readiness.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=architect_env.sh
source "$ROOT_DIR/scripts/architect_env.sh"
NPM_PREFIX="${NPM_CONFIG_PREFIX:-$HOME/.npm-global}"
OFFICE_DIR="$ROOT_DIR/skills/_shared/office-tools"

status_ok() { echo "OK"; }
status_miss() { echo "MISSING"; }

has_node() {
  if command -v node &>/dev/null; then
    return 0
  fi
  local candidate
  for candidate in \
    "$HOME/.cursor-server/bin/linux-x64"/*/node \
    /usr/bin/node; do
    if [[ -x "$candidate" ]]; then
      return 0
    fi
  done
  return 1
}

npm_global_installed() {
  local pkg="$1"
  if [[ -d "$NPM_PREFIX/lib/node_modules/$pkg" ]]; then
    return 0
  fi
  export PATH="$NPM_PREFIX/bin:${PATH:-}"
  if command -v npm &>/dev/null; then
    npm list -g "$pkg" --depth=0 &>/dev/null && return 0
  fi
  return 1
}

has_python_docx() {
  if [[ ! -d "$OFFICE_DIR" ]]; then
    return 1
  fi
  (
    cd "$OFFICE_DIR"
    uv run python3 -c "import docx" &>/dev/null
  )
}

npm_cli_status="MISSING"
node_status="MISSING"
docx_npm_status="MISSING"
pptx_npm_status="MISSING"
python_docx_status="MISSING"

if command -v npm &>/dev/null; then
  npm_cli_status="OK"
fi

if has_node; then
  node_status="OK"
fi
if npm_global_installed docx; then
  docx_npm_status="OK"
fi
if npm_global_installed pptxgenjs; then
  pptx_npm_status="OK"
fi
if has_python_docx; then
  python_docx_status="OK"
fi

echo ""
echo "=== Runtime readiness (artifact skills) ==="
printf "  Node.js:              %s\n" "$node_status"
printf "  npm CLI:              %s\n" "$npm_cli_status"
printf "  npm global docx:      %s  (Word — new DOCX via docx-js)\n" "$docx_npm_status"
printf "  npm global pptxgenjs: %s  (PowerPoint — new decks from scratch)\n" "$pptx_npm_status"
printf "  python-docx (uv):     %s  (Word fallback when npm/docx missing)\n" "$python_docx_status"
echo ""
echo "Capability without full Node/npm:"
echo "  Word new DOCX:  docx-js if docx OK; else python-docx if python-docx OK"
echo "  PPT new deck:   pptxgenjs only — if MISSING, use template/XML path or ask user to run: bash scripts/install_deps.sh node"
echo "  PPT / Word edit, validate, preview: office_tools + office-system (LibreOffice for PPT thumbnail)"
echo ""
