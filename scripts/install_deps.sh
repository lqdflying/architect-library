#!/usr/bin/env bash
# Convenience installer for the architect document skill set.
# Usage:
#   bash scripts/install_deps.sh              # install Excalidraw + Office Python deps
#   bash scripts/install_deps.sh excalidraw   # install only Excalidraw renderer deps
#   bash scripts/install_deps.sh office       # install only Office Python deps
#   bash scripts/install_deps.sh office-system # Office deps plus LibreOffice/Poppler
#   bash scripts/install_deps.sh pdf           # PDF skill Python deps only

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-all}"

run_excalidraw() {
  bash "$ROOT_DIR/skills/excalidraw-diagram/references/install_deps.sh"
}

run_office() {
  bash "$ROOT_DIR/skills/_shared/office-tools/install_deps.sh" "${1:-}"
}

run_pdf() {
  bash "$ROOT_DIR/skills/pdf-document/references/install_deps.sh"
}

case "$TARGET" in
  all)
    run_excalidraw
    run_office
    run_pdf
    ;;
  excalidraw)
    run_excalidraw
    ;;
  office)
    run_office
    ;;
  office-system)
    run_office --with-system
    ;;
  pdf)
    run_pdf
    ;;
  -h|--help|help)
    sed -n '1,14p' "$0"
    ;;
  *)
    echo "Unknown target: $TARGET"
    echo "Use one of: all, excalidraw, office, office-system, pdf"
    exit 1
    ;;
esac
