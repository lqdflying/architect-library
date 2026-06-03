#!/usr/bin/env bash
# Setup for shared DOCX/PPTX office tools.
# Installs uv if needed, then installs Python dependencies into this folder.
# Optional system packages can be installed with: bash install_deps.sh --with-system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WITH_SYSTEM="${1:-}"

if ! command -v curl &>/dev/null; then
  echo "ERROR: curl is required but not installed."
  echo "Install it first with your system package manager, then re-run this script."
  exit 1
fi

if command -v uv &>/dev/null; then
  echo "uv is already installed: $(uv --version)"
else
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v uv &>/dev/null; then
    echo "ERROR: uv was installed but not found on PATH."
    echo "Run: source \"$HOME/.local/bin/env\" and re-run this script."
    exit 1
  fi
  echo "uv installed: $(uv --version)"
fi

install_system_deps() {
  if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y --no-install-recommends libreoffice poppler-utils
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y libreoffice poppler-utils
  elif command -v yum &>/dev/null; then
    sudo yum install -y libreoffice poppler-utils
  elif command -v pacman &>/dev/null; then
    sudo pacman -S --needed --noconfirm libreoffice-still poppler
  elif command -v zypper &>/dev/null; then
    sudo zypper install -y libreoffice poppler-tools
  else
    echo "WARNING: Could not detect a supported package manager."
    echo "Install LibreOffice and Poppler manually if you need conversion or thumbnails."
  fi
}

if [[ "$WITH_SYSTEM" == "--with-system" ]]; then
  echo "Installing optional system dependencies for Office conversion..."
  install_system_deps
elif [[ -n "$WITH_SYSTEM" ]]; then
  echo "ERROR: Unknown option: $WITH_SYSTEM"
  echo "Usage: bash install_deps.sh [--with-system]"
  exit 1
else
  echo "Skipping optional system packages."
  echo "Install LibreOffice and Poppler later if you need PDF conversion, tracked-change acceptance, or PPT thumbnails."
fi

cd "$SCRIPT_DIR"
echo "Installing Python dependencies..."
uv sync

echo "Office tools setup complete."
echo "Test with: cd $SCRIPT_DIR && uv run python3 office_tools.py --help"
