#!/usr/bin/env bash
# Full setup for the Excalidraw render pipeline.
# Installs: system libraries for Chromium, uv, Python deps, and Chromium itself.
#
# Usage:
#   cd <installed-skills-root>/excalidraw-diagram/references
#   bash install_deps.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Step 1: Check for curl (needed for uv install) ---
if ! command -v curl &>/dev/null; then
  echo "ERROR: curl is required but not installed."
  echo "Install it first: sudo apt-get install curl / sudo dnf install curl"
  exit 1
fi

# --- Step 2: Install uv (Python package manager) if not present ---
if command -v uv &>/dev/null; then
  echo "✓ uv is already installed: $(uv --version)"
else
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Make uv available in this script's session
  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v uv &>/dev/null; then
    echo "ERROR: uv was installed but not found on PATH."
    echo "Run: source \"\$HOME/.local/bin/env\" and re-run this script."
    exit 1
  fi
  echo "✓ uv installed: $(uv --version)"
fi

# --- Step 3: Install system libraries for headless Chromium ---
detect_pkg_manager() {
  if command -v apt-get &>/dev/null; then
    echo "apt"
  elif command -v dnf &>/dev/null; then
    echo "dnf"
  elif command -v yum &>/dev/null; then
    echo "yum"
  elif command -v pacman &>/dev/null; then
    echo "pacman"
  elif command -v zypper &>/dev/null; then
    echo "zypper"
  else
    echo ""
  fi
}

PKG_MGR=$(detect_pkg_manager)

case "$PKG_MGR" in
  apt)
    echo "Detected apt (Debian/Ubuntu) — installing Chromium system deps..."
    sudo apt-get update -qq
    sudo apt-get install -y --no-install-recommends \
      libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 \
      libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libasound2 libnss3
    ;;
  dnf|yum)
    echo "Detected $PKG_MGR (RHEL/Oracle Linux/Rocky/Alma/Fedora) — installing Chromium system deps..."
    sudo "$PKG_MGR" install -y \
      atk at-spi2-atk cups-libs libXcomposite libXdamage \
      libXrandr mesa-libgbm pango alsa-lib nss
    ;;
  pacman)
    echo "Detected pacman (Arch Linux) — installing Chromium system deps..."
    sudo pacman -S --needed --noconfirm \
      atk at-spi2-atk cups libxcomposite libxdamage \
      libxrandr mesa pango alsa-lib nss
    ;;
  zypper)
    echo "Detected zypper (openSUSE/SLES) — installing Chromium system deps..."
    sudo zypper install -y \
      libatk-1_0-0 at-spi2-atk libcups2 libXcomposite1 libXdamage1 \
      libXrandr2 libgbm1 libpango-1_0-0 alsa-lib mozilla-nss
    ;;
  *)
    echo "WARNING: Could not detect a supported package manager (apt, dnf, yum, pacman, zypper)."
    echo "You may need to manually install: atk, at-spi2-atk, cups-libs, libXcomposite,"
    echo "  libXdamage, libXrandr, mesa-libgbm, pango, alsa-lib, nss"
    echo "Continuing anyway — Chromium may fail to launch if libraries are missing."
    ;;
esac

echo "✓ System dependencies handled"

# --- Step 4: Install Python deps and Playwright Chromium ---
echo ""
echo "Installing Python dependencies (requires Python >= 3.11)..."
cd "$SCRIPT_DIR"
uv sync

echo ""
echo "Installing Playwright Chromium..."
uv run python -m playwright install chromium

echo ""
echo "========================================="
echo "  Setup complete! Render pipeline ready."
echo "========================================="
echo ""
echo "Test with:"
echo "  cd $SCRIPT_DIR"
echo "  uv run python render_excalidraw.py <your-file.excalidraw>"
