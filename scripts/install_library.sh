#!/usr/bin/env bash
# Install Architect Library (skills + custom agents + user-global rules)
# to Cursor / Copilot / Claude / Codex.
# The legacy CLI default "both" means Cursor + Copilot + Claude.
# Generic install requests use explicit cursor and copilot commands (see AGENTS.md).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_BUNDLE="excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document verification-before-completion newagentlink api-and-interface-design deprecation-and-migration github-markdown terraform-commit-review terraform-apply-assistance security-audit review-handoff _shared"
# Cursor + Copilot + Codex (never Claude). SKILL.<editor>.md wins over SKILL.md.
EDITOR_VARIANT_SKILLS="mcp-tool-rules context7-docs notion-mcp-ops"
AGENT_BUNDLE="code-review security-auditor"
CURSOR_RULE_BUNDLE="review-handoff-reconciliation response-style edit-scope branch-strategy docs-lookup temp-validators"
COPILOT_INSTRUCTION_FRAGMENTS="response-style edit-scope branch-strategy review-handoff docs-lookup temp-validators"
CODEX_INSTRUCTION_FRAGMENTS="$COPILOT_INSTRUCTION_FRAGMENTS"
CLAUDE_RULE_BUNDLE="$COPILOT_INSTRUCTION_FRAGMENTS"

LEGACY_SKILLS="docx pptx xlsx pdf terraform-apply-fix-review mcp-tool-rules-copilot handoff"
LEGACY_CURSOR_RULES="code-review-handoff response-and-edit-scope"

usage() {
  cat <<'EOF'
Usage: install_library.sh [WHAT] [EDITOR] [SCOPE]

WHAT (default: all):
  all      Install skills, agents, and supported user instructions
  skills   Install skill library only
  agents   Install custom agent library only
  rules    Install Cursor rules, Copilot instructions, Claude rules, or Codex AGENTS.md

EDITOR (default: both):
  both     Cursor + Copilot + Claude
  all      Cursor + Copilot + Claude + Codex
  cursor   Cursor paths only
  copilot  Copilot paths only
  claude   Claude Code paths only
  codex    Codex skills, agents, and user instructions (requires Python 3)

SCOPE (default: global):
  global   ~/.cursor/, ~/.copilot/, ~/.claude/, ~/.agents/skills/, $CODEX_HOME (default ~/.codex)
  project  .cursor/, .github/, .claude/, .agents/skills/, .codex/agents/ under cwd
           Copilot, Claude, and Codex project installs do not write user instructions

Examples:
  bash scripts/install_library.sh
  bash scripts/install_library.sh skills
  bash scripts/install_library.sh agents cursor global
  bash scripts/install_library.sh rules cursor
  bash scripts/install_library.sh rules copilot
  bash scripts/install_library.sh all codex
  bash scripts/install_library.sh all all
  bash scripts/install_library.sh all both project
EOF
}

WHAT="${1:-all}"
EDITOR="${2:-both}"
SCOPE="${3:-global}"

case "$WHAT" in
  all|skills|agents|rules) ;;
  -h|--help|help) usage; exit 0 ;;
  *) echo "Unknown WHAT: $WHAT" >&2; usage >&2; exit 1 ;;
esac

case "$EDITOR" in
  both|all|cursor|copilot|claude|codex) ;;
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

selected() {
  [[ "$EDITOR" == "$1" || "$EDITOR" == "all" || ( "$EDITOR" == "both" && "$1" != "codex" ) ]]
}

cursor_skills_dir() { echo "${BASE}/.cursor/skills"; }
cursor_rules_dir() { echo "${BASE}/.cursor/rules"; }
copilot_skills_dir() {
  if [[ "$SCOPE" == "project" ]]; then
    echo "${BASE}/.github/skills"
  else
    echo "${BASE}/.copilot/skills"
  fi
}
claude_skills_dir() { echo "${BASE}/.claude/skills"; }
claude_rules_dir() { echo "${BASE}/.claude/rules"; }
codex_skills_dir() { echo "${BASE}/.agents/skills"; }
codex_home_dir() { echo "${CODEX_HOME:-${HOME}/.codex}"; }
codex_agents_dir() {
  if [[ "$SCOPE" == "project" ]]; then
    echo "${BASE}/.codex/agents"
  else
    echo "$(codex_home_dir)/agents"
  fi
}
cursor_agents_dir() { echo "${BASE}/.cursor/agents"; }
copilot_agents_dir() {
  if [[ "$SCOPE" == "project" ]]; then
    echo "${BASE}/.github/agents"
  else
    echo "${BASE}/.copilot/agents"
  fi
}
claude_agents_dir() { echo "${BASE}/.claude/agents"; }

activate_skill_variant() {
  local dir="$1" editor="$2"
  if [[ -f "${dir}/SKILL.${editor}.md" ]]; then
    mv "${dir}/SKILL.${editor}.md" "${dir}/SKILL.md"
  fi
  find "$dir" -maxdepth 1 -name 'SKILL.*.md' -delete
}

install_skills_to() {
  local dest="$1"
  local editor="$2" name legacy
  mkdir -p "$dest"
  for legacy in $LEGACY_SKILLS; do
    rm -rf "${dest}/${legacy}"
  done
  for name in $SKILL_BUNDLE; do
    rm -rf "${dest}/${name}"
    cp -a "${REPO}/skills/${name}" "${dest}/${name}"
    activate_skill_variant "${dest}/${name}" "$editor"
  done
}

install_editor_variants() {
  local dest="$1"
  local editor="$2" name
  for name in $EDITOR_VARIANT_SKILLS; do
    rm -rf "${dest}/${name}"
    cp -a "${REPO}/skills/${name}" "${dest}/${name}"
    activate_skill_variant "${dest}/${name}" "$editor"
  done
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

install_cursor_newagentlink_command() {
  if ! selected cursor; then
    return 0
  fi
  if [[ "$SCOPE" != "global" ]]; then
    return 0
  fi
  local src dest_dir dest
  src="${REPO}/skills/newagentlink/cursor.command.md"
  dest_dir="${HOME}/.cursor/commands"
  dest="${dest_dir}/newagentlink.md"
  if [[ ! -f "$src" ]]; then
    echo "Missing Cursor command source: ${src}" >&2
    exit 1
  fi
  mkdir -p "$dest_dir"
  rm -f "${dest_dir}/handoff.md"
  cp -a "$src" "$dest"
}

install_skills() {
  local editor dest
  for editor in cursor copilot claude codex; do
    selected "$editor" || continue
    dest="$("${editor}_skills_dir")"
    install_skills_to "$dest" "$editor"
    if [[ "$editor" != "claude" ]]; then
      install_editor_variants "$dest" "$editor"
    fi
  done
  install_cursor_newagentlink_command
}

# Project-scope from this clone (repo root or any subdirectory) would copy
# user-global rules into a .cursor/rules/ under the maintainer tree. Skip.
skip_cursor_rules_into_repo() {
  [[ "$SCOPE" == "project" ]] || return 1
  local here repo_root
  here="$(pwd -P)"
  repo_root="$(cd "$REPO" && pwd -P)"
  case "$here" in
    "$repo_root"|"$repo_root"/*) return 0 ;;
  esac
  return 1
}

install_cursor_rules() {
  if ! selected cursor; then
    echo "Skip Cursor user-global rules (EDITOR=$EDITOR)"
    return 0
  fi
  if skip_cursor_rules_into_repo; then
    echo "Skip Cursor user-global rules (project-scope from architect-library clone would copy into maintainer .cursor/rules/)"
    return 0
  fi
  local dest src name legacy
  dest="$(cursor_rules_dir)"
  mkdir -p "$dest"
  for legacy in $LEGACY_CURSOR_RULES; do
    rm -f "${dest}/${legacy}.mdc"
  done
  for name in $CURSOR_RULE_BUNDLE; do
    src="${REPO}/user-rules/cursor/${name}.mdc"
    if [[ ! -f "$src" ]]; then
      echo "Missing Cursor user-global rule: ${src}" >&2
      exit 1
    fi
    rm -f "${dest}/${name}.mdc"
    cp -a "$src" "${dest}/${name}.mdc"
  done
}

assemble_copilot_instructions() {
  local dest="$1"
  local name src first=1
  for name in $COPILOT_INSTRUCTION_FRAGMENTS; do
    src="${REPO}/user-rules/copilot/${name}.md"
    if [[ ! -f "$src" ]]; then
      echo "Missing Copilot instruction fragment: ${src}" >&2
      return 1
    fi
    if [[ "$first" -eq 1 ]]; then
      cat "$src" > "$dest"
      first=0
    else
      printf '\n' >> "$dest"
      cat "$src" >> "$dest"
    fi
  done
}

install_copilot_instructions() {
  if ! selected copilot; then
    echo "Skip Copilot always-on instructions (EDITOR=$EDITOR)"
    return 0
  fi
  if [[ "$SCOPE" != "global" ]]; then
    echo "Skip Copilot always-on instructions (project scope does not write .github/copilot-instructions.md)"
    return 0
  fi
  local dest
  dest="${HOME}/.copilot/copilot-instructions.md"
  mkdir -p "${HOME}/.copilot"
  rm -f "$dest"
  assemble_copilot_instructions "$dest" || exit 1
}

install_claude_rules() {
  selected claude || return 0
  if [[ "$SCOPE" != "global" ]]; then
    echo "Skip Claude user rules (project scope does not write .claude/rules/)"
    return 0
  fi
  local dest name
  dest="$(claude_rules_dir)"
  mkdir -p "$dest"
  for name in $CLAUDE_RULE_BUNDLE; do
    rm -f "${dest}/${name}.md"
    cp -a "${REPO}/user-rules/claude/${name}.md" "${dest}/${name}.md"
  done
}

codex_instructions() {
  local mode="$1" name
  local fragments=()
  for name in $CODEX_INSTRUCTION_FRAGMENTS; do
    fragments+=("${REPO}/user-rules/codex/${name}.md")
  done
  python3 "${REPO}/scripts/codex_install.py" instructions "$mode" \
    "$(codex_home_dir)/AGENTS.md" "${fragments[@]}"
}

codex_agent() {
  local mode="$1" name="$2"
  python3 "${REPO}/scripts/codex_install.py" agent "$mode" \
    "$(codex_agents_dir)/${name}.toml" "${REPO}/agents/${name}"
}

install_codex_instructions() {
  selected codex || return 0
  if [[ "$SCOPE" != "global" ]]; then
    echo "Skip Codex user instructions (project scope does not write AGENTS.md)"
    return 0
  fi
  codex_instructions write
}

install_agents() {
  for name in $AGENT_BUNDLE; do
    if [[ ! -d "${REPO}/agents/${name}" ]]; then
      echo "Missing agent source: ${REPO}/agents/${name}" >&2
      exit 1
    fi
  done

  if selected cursor; then
    for name in $AGENT_BUNDLE; do
      install_agent_file "$name" "cursor.header.md" "$(cursor_agents_dir)/${name}.md"
    done
  fi

  if selected copilot; then
    for name in $AGENT_BUNDLE; do
      install_agent_file "$name" "copilot.header.md" "$(copilot_agents_dir)/${name}.agent.md"
    done
  fi

  if selected claude; then
    for name in $AGENT_BUNDLE; do
      install_agent_file "$name" "claude.header.md" "$(claude_agents_dir)/${name}.md"
    done
  fi
  if selected codex; then
    for name in $AGENT_BUNDLE; do
      codex_agent write "$name"
    done
  fi
}

# Check selected sources and Codex conflicts before touching any install target.
preflight() {
  local editor name src
  if selected codex; then
    command -v python3 >/dev/null || { echo "Codex installation requires Python 3" >&2; return 1; }
  fi
  for editor in cursor copilot claude codex; do
    selected "$editor" || continue
    if [[ "$WHAT" == "all" || "$WHAT" == "skills" ]]; then
      for name in $SKILL_BUNDLE; do
        src="${REPO}/skills/${name}"
        if [[ "$name" == "_shared" ]]; then
          test -f "$src/office-tools/office_tools.py" || { echo "Missing shared Office tools: $src" >&2; return 1; }
        elif [[ ! -f "$src/SKILL.${editor}.md" && ! -f "$src/SKILL.md" ]]; then
          echo "Missing $editor skill source: $src" >&2; return 1
        fi
      done
      if [[ "$editor" != "claude" ]]; then
        for name in $EDITOR_VARIANT_SKILLS; do
          src="${REPO}/skills/${name}"
          if [[ ! -f "$src/SKILL.${editor}.md" && ! -f "$src/SKILL.md" ]]; then
            echo "Missing $editor skill source: $src" >&2; return 1
          fi
        done
      fi
      if [[ "$editor" == "cursor" && "$SCOPE" == "global" ]]; then
        test -f "${REPO}/skills/newagentlink/cursor.command.md" || return 1
      fi
      if [[ "$editor" == "codex" ]]; then
        test -f "${REPO}/skills/newagentlink/agents/openai.yaml" || return 1
      fi
    fi
    if [[ "$WHAT" == "all" || "$WHAT" == "agents" ]]; then
      for name in $AGENT_BUNDLE; do
        if [[ "$editor" == "codex" ]]; then
          codex_agent preflight "$name" || return 1
        else
          test -f "${REPO}/agents/${name}/${editor}.header.md" && \
            test -f "${REPO}/agents/${name}/INSTRUCTIONS.md" || { echo "Missing $editor agent source: $name" >&2; return 1; }
        fi
      done
    fi
  done
  if [[ "$WHAT" == "all" || "$WHAT" == "rules" ]]; then
    if selected cursor; then
      for name in $CURSOR_RULE_BUNDLE; do
        test -f "${REPO}/user-rules/cursor/${name}.mdc" || { echo "Missing Cursor rule: $name" >&2; return 1; }
      done
    fi
    if selected copilot; then
      bash "${REPO}/scripts/sync_copilot_rules.sh" --check || return 1
    fi
    if selected claude; then
      bash "${REPO}/scripts/sync_claude_rules.sh" --check || return 1
      if [[ "$SCOPE" == "global" && "$WHAT" == "rules" && ! -f "$(claude_skills_dir)/review-handoff/SKILL.md" ]]; then
        echo "Missing review-handoff skill (run: bash scripts/install_library.sh skills claude)" >&2
        return 1
      fi
    fi
    if selected codex; then
      bash "${REPO}/scripts/sync_codex_rules.sh" --check || return 1
      if [[ "$SCOPE" == "global" ]]; then
        codex_instructions preflight || return 1
        if [[ "$WHAT" == "rules" && ! -f "$(codex_skills_dir)/review-handoff/SKILL.md" ]]; then
          echo "Missing review-handoff skill (run: bash scripts/install_library.sh skills codex)" >&2
          return 1
        fi
      fi
    fi
  fi
}

preflight
# shellcheck source=architect_env.sh
source "$REPO/scripts/architect_env.sh"

echo "Architect Library install_library.sh"
echo "  REPO=$REPO"
echo "  WHAT=$WHAT EDITOR=$EDITOR SCOPE=$SCOPE"

case "$WHAT" in
  all)
    install_skills
    install_agents
    install_cursor_rules
    install_copilot_instructions
    install_claude_rules
    install_codex_instructions
    ;;
  skills) install_skills ;;
  agents) install_agents ;;
  rules)
    install_cursor_rules
    install_copilot_instructions
    install_claude_rules
    install_codex_instructions
    ;;
esac

verify_skills_at() {
  local dir="$1"
  local name
  for name in $SKILL_BUNDLE; do
    [[ "$name" == "_shared" ]] || test -f "${dir}/${name}/SKILL.md" || return 1
    test -z "$(find "${dir}/${name}" -maxdepth 1 -name 'SKILL.*.md' -print)" || return 1
  done
  test -f "${dir}/_shared/office-tools/office_tools.py" || return 1
  test -f "${dir}/word-document/SKILL.md" || return 1
  test -f "${dir}/api-and-interface-design/SKILL.md" || return 1
  test -f "${dir}/deprecation-and-migration/SKILL.md" || return 1
  test -f "${dir}/terraform-commit-review/SKILL.md" || return 1
  test -f "${dir}/terraform-apply-assistance/SKILL.md" || return 1
  test -f "${dir}/security-audit/SKILL.md" || return 1
  test -f "${dir}/newagentlink/SKILL.md" || return 1
  grep -q 'disable-model-invocation: true' "${dir}/newagentlink/SKILL.md" || return 1
  test ! -d "${dir}/handoff" || return 1
}

verify_editor_variants_at() {
  local dir="$1"
  for name in $EDITOR_VARIANT_SKILLS; do
    test -f "${dir}/${name}/SKILL.md" || return 1
    # No leftover variant files at destination
    test ! -f "${dir}/${name}/SKILL.cursor.md" || return 1
    test ! -f "${dir}/${name}/SKILL.copilot.md" || return 1
    test ! -f "${dir}/${name}/SKILL.codex.md" || return 1
  done
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

verify_copilot_instructions() {
  local dest expected name
  dest="${HOME}/.copilot/copilot-instructions.md"
  expected="$(mktemp)"
  assemble_copilot_instructions "$expected" || { rm -f "$expected"; return 1; }
  test -f "$dest" || { rm -f "$expected"; return 1; }
  cmp -s "$expected" "$dest" || { rm -f "$expected"; return 1; }
  rm -f "$expected"
  for name in $COPILOT_INSTRUCTION_FRAGMENTS; do
    test -f "${REPO}/user-rules/copilot/${name}.md" || return 1
  done
  grep -q '/tmp/<topic>-handoff.md' "$dest" || return 1
  grep -q 'Applies in every VS Code Copilot chat.' "$dest" || return 1
  grep -q '# Response style' "$dest" || return 1
  grep -q '# Edit scope' "$dest" || return 1
  grep -q '# Branch strategy' "$dest" || return 1
  grep -q '# Review handoff' "$dest" || return 1
  grep -q '# Docs lookup' "$dest" || return 1
  grep -q '# Temporary validators' "$dest" || return 1
  if grep -q 'alwaysApply' "$dest"; then
    return 1
  fi
}

# The always-on review-handoff trigger points at this skill; a rules-only install needs it present.
verify_review_handoff_skill() {
  local dir="$1"
  local editor="$2"
  if [[ ! -f "${dir}/review-handoff/SKILL.md" ]]; then
    echo "Missing ${dir}/review-handoff/SKILL.md (run: bash scripts/install_library.sh skills ${editor})" >&2
    return 1
  fi
}

verify_claude_rules() {
  local dir="$1"
  local name
  for name in $CLAUDE_RULE_BUNDLE; do
    cmp -s "${REPO}/user-rules/claude/${name}.md" "${dir}/${name}.md" || return 1
  done
}

verify_cursor_rules() {
  local dir="$1"
  local name legacy
  for name in $CURSOR_RULE_BUNDLE; do
    test -f "${dir}/${name}.mdc" || return 1
    grep -q 'alwaysApply: true' "${dir}/${name}.mdc" || return 1
  done
  for legacy in $LEGACY_CURSOR_RULES; do
    test ! -f "${dir}/${legacy}.mdc" || return 1
  done
}

verify() {
  local ok=0 name
  if [[ "$WHAT" == "all" || "$WHAT" == "skills" ]]; then
    if selected cursor; then
      verify_skills_at "$(cursor_skills_dir)" || ok=1
      verify_editor_variants_at "$(cursor_skills_dir)" || ok=1
      if [[ "$SCOPE" == "global" ]]; then
        test ! -d "${HOME}/.cursor/skills/handoff" || ok=1
        test ! -f "${HOME}/.cursor/commands/handoff.md" || ok=1
        test -f "${HOME}/.cursor/commands/newagentlink.md" || ok=1
        cmp -s "${REPO}/skills/newagentlink/cursor.command.md" "${HOME}/.cursor/commands/newagentlink.md" || ok=1
      fi
    fi
    if selected copilot; then
      verify_skills_at "$(copilot_skills_dir)" || ok=1
      verify_editor_variants_at "$(copilot_skills_dir)" || ok=1
    fi
    if selected claude; then
      verify_skills_at "$(claude_skills_dir)" || ok=1
    fi
    if selected codex; then
      verify_skills_at "$(codex_skills_dir)" || ok=1
      verify_editor_variants_at "$(codex_skills_dir)" || ok=1
      grep -q 'allow_implicit_invocation: false' "$(codex_skills_dir)/newagentlink/agents/openai.yaml" || ok=1
    fi
  fi
  if [[ "$WHAT" == "all" || "$WHAT" == "agents" ]]; then
    if selected codex; then
      for name in $AGENT_BUNDLE; do
        codex_agent verify "$name" || ok=1
      done
    fi
    if selected cursor; then
      verify_cursor_agents "$(cursor_agents_dir)" || ok=1
    fi
    if selected copilot; then
      verify_copilot_agents "$(copilot_agents_dir)" || ok=1
    fi
    if selected claude; then
      verify_claude_agents "$(claude_agents_dir)" || ok=1
    fi
  fi
  if [[ "$WHAT" == "all" || "$WHAT" == "rules" ]]; then
    if selected cursor; then
      if skip_cursor_rules_into_repo; then
        :
      else
        verify_cursor_rules "$(cursor_rules_dir)" || ok=1
        verify_review_handoff_skill "$(cursor_skills_dir)" cursor || ok=1
      fi
    fi
    if selected copilot; then
      bash "${REPO}/scripts/sync_copilot_rules.sh" --check || ok=1
      if [[ "$SCOPE" == "global" ]]; then
        verify_copilot_instructions || ok=1
        verify_review_handoff_skill "$(copilot_skills_dir)" copilot || ok=1
      fi
    fi
    if selected claude; then
      bash "${REPO}/scripts/sync_claude_rules.sh" --check || ok=1
      if [[ "$SCOPE" == "global" ]]; then
        verify_claude_rules "$(claude_rules_dir)" || ok=1
        verify_review_handoff_skill "$(claude_skills_dir)" claude || ok=1
      fi
    fi
    if selected codex; then
      bash "${REPO}/scripts/sync_codex_rules.sh" --check || ok=1
      if [[ "$SCOPE" == "global" ]]; then
        codex_instructions verify || ok=1
        verify_review_handoff_skill "$(codex_skills_dir)" codex || ok=1
      fi
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
