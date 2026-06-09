# Shared machine-local npm paths (sourced by install_node.sh and vendor_excalidraw.sh).
# Never under the repository tree.

architect_npm_bootstrap_dir() {
  printf '%s\n' "${ARCHITECT_NPM_BOOTSTRAP:-${XDG_CACHE_HOME:-$HOME/.cache}/architect-library/npm-bootstrap}"
}

architect_vendor_excalidraw_build_dir() {
  printf '%s\n' "${ARCHITECT_VENDOR_BUILD:-${XDG_CACHE_HOME:-$HOME/.cache}/architect-library/vendor-excalidraw-build}"
}
