#!/usr/bin/env bash
# Install Architect Library (skills + custom agents) to Cursor / Copilot / Claude.
# Default: global install of both libraries to cursor + copilot home directories.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=architect_env.sh
source "$REPO/scripts/architect_env.sh"

SKILL_BUNDLE="excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document verification-before-completion api-and-interface-design deprecation-and-migration terraform-commit-review terraform-apply-assistance _shared"
CURSOR_ONLY_SKILLS="mcp-tool-rules"
AGENT_BUNDLE="code-review security-auditor"

LEGACY_SKILLS="docx pptx xlsx pdf terraform-apply-fix-review"

usage() {
  cat <<'EOF'
Usage: install_library.sh [WHAT] [EDITOR] [SCOPE]

WHAT (default: all):
  all      Install skills and agents
  skills   Install skill library only
  agents   Install custom agent library only

EDITOR (default: both):
  both     Cursor + Copilot + Claude
  cursor   Cursor paths only
  copilot  Copilot paths only
  claude   Claude Code paths only

SCOPE (default: global):
  global   ~/.cursor/, ~/.copilot/, ~/.claude/
  project  .cursor/, .github/, .claude/ under current working directory

Examples:
  bash scripts/install_library.sh
  bash scripts/install_library.sh skills
  bash scripts/install_library.sh agents cursor global
  bash scripts/install_library.sh all both project
EOF
}

WHAT="${1:-all}"
EDITOR="${2:-both}"
SCOPE="${3:-global}"

case "$WHAT" in
  all|skills|agents) ;;
  -h|--help|help) usage; exit 0 ;;
  *) echo "Unknown WHAT: $WHAT" >&2; usage >&2; exit 1 ;;
esac

case "$EDITOR" in
  both|cursor|copilot|claude) ;;
  global|project)
    SCOPE="$EDITOR"
    EDITOR="both"
    ;;
  *)
    echo "Unknown EDITOR: $EDITOR" >&2
    usage >&2
    exit 1
    ;;
esac

case "$SCOPE" in
  global|project) ;;
  *)
    echo "Unknown SCOPE: $SCOPE" >&2
    usage >&2
    exit 1
    ;;
esac

if [[ "$SCOPE" == "global" ]]; then
  BASE="${HOME}"
else
  BASE="$(pwd)"
fi

cursor_skills_dir() { echo "${BASE}/.cursor/skills"; }
copilot_skills_dir() {
  if [[ "$SCOPE" == "project" ]]; then
    echo "${BASE}/.github/skills"
  else
    echo "${BASE}/.copilot/skills"
  fi
}
claude_skills_dir() { echo "${BASE}/.claude/skills"; }
cursor_agents_dir() { echo "${BASE}/.cursor/agents"; }
copilot_agents_dir() {
  if [[ "$SCOPE" == "project" ]]; then
    echo "${BASE}/.github/agents"
  else
    echo "${BASE}/.copilot/agents"
  fi
}
claude_agents_dir() { echo "${BASE}/.claude/agents"; }

install_skills_to() {
  local dest="$1"
  local cursor_only="${2:-false}"
  mkdir -p "$dest"
  for legacy in $LEGACY_SKILLS; do
    rm -rf "${dest}/${legacy}"
  done
  for name in $SKILL_BUNDLE; do
    rm -rf "${dest}/${name}"
    cp -a "${REPO}/skills/${name}" "${dest}/${name}"
  done
  if [[ "$cursor_only" == "true" ]]; then
    for name in $CURSOR_ONLY_SKILLS; do
      rm -rf "${dest}/${name}"
      cp -a "${REPO}/skills/${name}" "${dest}/${name}"
    done
  fi
}

install_agent_file() {
  local name="$1"
  local header="$2"
  local dest="$3"
  local agent_dir="${REPO}/agents/${name}"

  if [[ ! -f "${agent_dir}/${header}" ]] || [[ ! -f "${agent_dir}/INSTRUCTIONS.md" ]]; then
    echo "Agent ${name} missing ${header} or INSTRUCTIONS.md in ${agent_dir}" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$dest")"
  cat "${agent_dir}/${header}" "${agent_dir}/INSTRUCTIONS.md" > "$dest"
}

install_skills() {
  case "$EDITOR" in
    both)
      install_skills_to "$(cursor_skills_dir)" true
      install_skills_to "$(copilot_skills_dir)"
      install_skills_to "$(claude_skills_dir)"
      ;;
    cursor) install_skills_to "$(cursor_skills_dir)" true ;;
    copilot) install_skills_to "$(copilot_skills_dir)" ;;
    claude) install_skills_to "$(claude_skills_dir)" ;;
  esac
}

install_agents() {
  for name in $AGENT_BUNDLE; do
    if [[ ! -d "${REPO}/agents/${name}" ]]; then
      echo "Missing agent source: ${REPO}/agents/${name}" >&2
      exit 1
    fi
  done

  if [[ "$EDITOR" == "both" || "$EDITOR" == "cursor" ]]; then
    for name in $AGENT_BUNDLE; do
      install_agent_file "$name" "cursor.header.md" "$(cursor_agents_dir)/${name}.md"
    done
  fi

  if [[ "$EDITOR" == "both" || "$EDITOR" == "copilot" ]]; then
    for name in $AGENT_BUNDLE; do
      install_agent_file "$name" "copilot.header.md" "$(copilot_agents_dir)/${name}.agent.md"
    done
  fi

  if [[ "$EDITOR" == "both" || "$EDITOR" == "claude" ]]; then
    for name in $AGENT_BUNDLE; do
      install_agent_file "$name" "claude.header.md" "$(claude_agents_dir)/${name}.md"
    done
  fi
}

echo "Architect Library install_library.sh"
echo "  REPO=$REPO"
echo "  WHAT=$WHAT EDITOR=$EDITOR SCOPE=$SCOPE"

case "$WHAT" in
  all)
    install_skills
    install_agents
    ;;
  skills) install_skills ;;
  agents) install_agents ;;
esac

verify_skills_at() {
  local dir="$1"
  test -f "${dir}/_shared/office-tools/office_tools.py" || return 1
  test -f "${dir}/word-document/SKILL.md" || return 1
  test -f "${dir}/api-and-interface-design/SKILL.md" || return 1
  test -f "${dir}/deprecation-and-migration/SKILL.md" || return 1
  test -f "${dir}/terraform-commit-review/SKILL.md" || return 1
  test -f "${dir}/terraform-apply-assistance/SKILL.md" || return 1
}

verify_cursor_agents() {
  local dir="$1"
  test -f "${dir}/code-review.md" || return 1
  test -f "${dir}/security-auditor.md" || return 1
  grep -q 'readonly: true' "${dir}/code-review.md" || return 1
  grep -q 'readonly: true' "${dir}/security-auditor.md" || return 1
}

verify_copilot_agents() {
  local dir="$1"
  test -f "${dir}/code-review.agent.md" || return 1
  test -f "${dir}/security-auditor.agent.md" || return 1
  grep -q 'disallowedTools: edit' "${dir}/code-review.agent.md" || return 1
  grep -q 'disallowedTools: edit' "${dir}/security-auditor.agent.md" || return 1
}

verify_claude_agents() {
  local dir="$1"
  test -f "${dir}/code-review.md" || return 1
  test -f "${dir}/security-auditor.md" || return 1
  grep -q 'permissionMode: plan' "${dir}/code-review.md" || return 1
  grep -q 'permissionMode: plan' "${dir}/security-auditor.md" || return 1
}

verify() {
  local ok=0
  if [[ "$WHAT" == "all" || "$WHAT" == "skills" ]]; then
    if [[ "$EDITOR" == "both" || "$EDITOR" == "cursor" ]]; then
      verify_skills_at "$(cursor_skills_dir)" || ok=1
    fi
    if [[ "$EDITOR" == "both" || "$EDITOR" == "copilot" ]]; then
      verify_skills_at "$(copilot_skills_dir)" || ok=1
    fi
    if [[ "$EDITOR" == "both" || "$EDITOR" == "claude" ]]; then
      verify_skills_at "$(claude_skills_dir)" || ok=1
    fi
  fi
  if [[ "$WHAT" == "all" || "$WHAT" == "agents" ]]; then
    if [[ "$EDITOR" == "both" || "$EDITOR" == "cursor" ]]; then
      verify_cursor_agents "$(cursor_agents_dir)" || ok=1
    fi
    if [[ "$EDITOR" == "both" || "$EDITOR" == "copilot" ]]; then
      verify_copilot_agents "$(copilot_agents_dir)" || ok=1
    fi
    if [[ "$EDITOR" == "both" || "$EDITOR" == "claude" ]]; then
      verify_claude_agents "$(claude_agents_dir)" || ok=1
    fi
  fi
  if [[ "$ok" -ne 0 ]]; then
    echo "VERIFY: some checks failed" >&2
    exit 1
  fi
  echo "VERIFY: OK"
}

verify
echo "Done."
