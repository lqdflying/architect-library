#!/usr/bin/env bash
# Build a self-contained Excalidraw ESM bundle for offline PNG rendering.
#
# Usage (from repository root):
#   bash scripts/vendor_excalidraw.sh
#
# Output:
#   skills/excalidraw-diagram/references/vendor/excalidraw.bundle.mjs

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/scripts/vendor_excalidraw"
OUT_DIR="$ROOT_DIR/skills/excalidraw-diagram/references/vendor"
OUT_FILE="$OUT_DIR/excalidraw.bundle.mjs"
NPM_BOOTSTRAP="$BUILD_DIR/.npm-bootstrap"

find_node() {
  if [[ -n "${NODE_BIN:-}" ]] && [[ -x "$NODE_BIN" ]]; then
    echo "$NODE_BIN"
    return
  fi
  if command -v node &>/dev/null; then
    command -v node
    return
  fi
  for candidate in \
    "$HOME/.cursor-server/bin/linux-x64"/*/node \
    /usr/bin/node; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  done
  return 1
}

NODE_BIN_RESOLVED="$(find_node)" || {
  echo "ERROR: node is required to vendor Excalidraw."
  echo "Install Node.js (https://nodejs.org/) or set NODE_BIN to your node binary."
  exit 1
}

run_npm() {
  if command -v npm &>/dev/null; then
    npm "$@"
  else
    if [[ ! -f "$NPM_BOOTSTRAP/bin/npm-cli.js" ]]; then
      echo "Bootstrapping npm (no system npm found)..."
      mkdir -p "$NPM_BOOTSTRAP"
      curl -fsSL "https://registry.npmjs.org/npm/-/npm-10.9.2.tgz" -o "$NPM_BOOTSTRAP/npm.tgz"
      tar -xzf "$NPM_BOOTSTRAP/npm.tgz" -C "$NPM_BOOTSTRAP"
      rm -f "$NPM_BOOTSTRAP/npm.tgz"
      if [[ -d "$NPM_BOOTSTRAP/package" ]]; then
        mv "$NPM_BOOTSTRAP/package/"* "$NPM_BOOTSTRAP/"
        rmdir "$NPM_BOOTSTRAP/package"
      fi
    fi
    "$NODE_BIN_RESOLVED" "$NPM_BOOTSTRAP/bin/npm-cli.js" "$@"
  fi
}

run_npx() {
  if command -v npx &>/dev/null; then
    npx "$@"
  else
  "$NODE_BIN_RESOLVED" "$NPM_BOOTSTRAP/bin/npx-cli.js" "$@"
  fi
}

mkdir -p "$OUT_DIR"

echo "Installing vendor build dependencies..."
(cd "$BUILD_DIR" && run_npm install --no-fund --no-audit)

echo "Bundling @excalidraw/excalidraw@0.17.6..."
(cd "$BUILD_DIR" && run_npx esbuild entry.mjs \
  --bundle \
  --format=esm \
  --platform=browser \
  --target=es2022 \
  --outfile="$OUT_FILE" \
  --banner:js="/* @excalidraw/excalidraw@0.17.6 — offline render bundle */
var global=globalThis;
var process={env:{NODE_ENV:\"production\"}};")

# Remove legacy esm.sh stub files if present.
rm -f "$OUT_DIR/excalidraw.js" "$OUT_DIR/excalidraw-bundle-only.mjs"

echo "✓ Wrote $OUT_FILE"
echo "  Render offline via references/vendor/excalidraw.bundle.mjs"
