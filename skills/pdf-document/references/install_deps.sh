#!/usr/bin/env bash
# Python dependencies for pdf-document skill scripts.
# Usage: bash references/install_deps.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v curl &>/dev/null; then
  echo "ERROR: curl is required."
  exit 1
fi

if command -v uv &>/dev/null; then
  echo "uv: $(uv --version)"
else
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

cd "$SCRIPT_DIR"
uv sync
echo "PDF tools setup complete."
echo "Optional: qpdf, pdftk, poppler-utils; OCR: pip install pytesseract pdf2image + system tesseract"
