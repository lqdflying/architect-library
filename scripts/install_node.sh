#!/usr/bin/env bash
# Install Node/npm if possible and global docx + pptxgenjs for Word/PPT skills.
# Usage: bash scripts/install_node.sh
#
# Tries, in order: existing PATH node/npm, Cursor-server node, system package
# manager (dnf/apt with sudo), then bootstraps npm beside node if needed.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=npm_bootstrap_common.sh
source "$ROOT_DIR/scripts/npm_bootstrap_common.sh"
# shellcheck source=architect_env.sh
source "$ROOT_DIR/scripts/architect_env.sh"
NPM_BOOTSTRAP="$(architect_npm_bootstrap_dir)"
NPM_PREFIX="${NPM_CONFIG_PREFIX:-$HOME/.npm-global}"

find_node() {
  if [[ -n "${NODE_BIN:-}" ]] && [[ -x "$NODE_BIN" ]]; then
    echo "$NODE_BIN"
    return 0
  fi
  if command -v node &>/dev/null; then
    command -v node
    return 0
  fi
  local candidate
  for candidate in \
    "$HOME/.cursor-server/bin/linux-x64"/*/node \
    /usr/bin/node; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

bootstrap_npm() {
  if [[ -f "$NPM_BOOTSTRAP/bin/npm-cli.js" ]]; then
    return 0
  fi
  echo "Bootstrapping npm (no system npm found)..."
  mkdir -p "$NPM_BOOTSTRAP"
  curl -fsSL "https://registry.npmjs.org/npm/-/npm-10.9.2.tgz" -o "$NPM_BOOTSTRAP/npm.tgz"
  tar -xzf "$NPM_BOOTSTRAP/npm.tgz" -C "$NPM_BOOTSTRAP"
  rm -f "$NPM_BOOTSTRAP/npm.tgz"
  if [[ -d "$NPM_BOOTSTRAP/package" ]]; then
    mv "$NPM_BOOTSTRAP/package/"* "$NPM_BOOTSTRAP/"
    rmdir "$NPM_BOOTSTRAP/package"
  fi
}

try_system_node() {
  if command -v node &>/dev/null && command -v npm &>/dev/null; then
    return 0
  fi
  if ! command -v sudo &>/dev/null; then
    return 1
  fi
  if command -v dnf &>/dev/null; then
    echo "Attempting: sudo dnf install -y nodejs npm ..."
    if sudo dnf install -y nodejs npm; then
      return 0
    fi
  fi
  if command -v apt-get &>/dev/null; then
    echo "Attempting: sudo apt-get install -y nodejs npm ..."
    if sudo apt-get update -qq && sudo apt-get install -y nodejs npm; then
      return 0
    fi
  fi
  return 1
}

run_npm() {
  local node_bin="$1"
  shift
  if command -v npm &>/dev/null; then
    npm "$@"
  else
    bootstrap_npm
    "$node_bin" "$NPM_BOOTSTRAP/bin/npm-cli.js" "$@"
  fi
}

NODE_BIN_RESOLVED=""
if NODE_BIN_RESOLVED="$(find_node)"; then
  :
elif try_system_node && NODE_BIN_RESOLVED="$(find_node)"; then
  echo "✓ Node.js installed via system package manager"
else
  echo "WARNING: Node.js not found and could not be installed automatically." >&2
  echo "  Without Node/npm: Word new DOCX may still work via python-docx (bash scripts/install_deps.sh office)." >&2
  echo "  New PowerPoint decks from scratch need pptxgenjs — use template/XML editing or install Node." >&2
  echo "  Options:" >&2
  echo "    - RHEL/Oracle: sudo dnf install -y nodejs npm" >&2
  echo "    - Debian/Ubuntu: sudo apt-get install -y nodejs npm" >&2
  echo "    - https://nodejs.org/ or set NODE_BIN to your node binary" >&2
  echo "  Then re-run: bash scripts/install_deps.sh node" >&2
  bash "$ROOT_DIR/scripts/runtime_readiness.sh" || true
  exit 0
fi

echo "Using node: $NODE_BIN_RESOLVED"
mkdir -p "$NPM_PREFIX/bin"
export NPM_CONFIG_PREFIX="$NPM_PREFIX"
export NODE_BIN="$NODE_BIN_RESOLVED"
architect_path_prepend_once "$NPM_PREFIX/bin"
architect_path_prepend_once "$(dirname "$NODE_BIN_RESOLVED")"

if ! command -v npm &>/dev/null; then
  bootstrap_npm
fi
architect_ensure_npm_shim "$NODE_BIN_RESOLVED"

echo "Installing global npm packages: docx, pptxgenjs ..."
run_npm "$NODE_BIN_RESOLVED" install -g docx pptxgenjs --no-fund --no-audit

echo "✓ npm global packages installed (prefix: $NPM_PREFIX)"
architect_write_env_file "$NODE_BIN_RESOLVED"
architect_ensure_shell_profile
architect_apply_env
echo "  Env file: $(architect_env_file) (sourced by install scripts; loaded in new shells via ~/.bashrc)"
bash "$ROOT_DIR/scripts/runtime_readiness.sh" || true
