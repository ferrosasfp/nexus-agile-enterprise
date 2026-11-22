#!/usr/bin/env bash
#
# NexusAgile — setup
#
# Installs NexusAgile into a target project AND wires up persistent memory (Engram).
# Memory keeps the project's experience across HUs: lessons approved by a person,
# environment traps (project or global scope), facts tied to git blob hashes and
# work claims. The analyst and the architect read it; Docs and the orchestrator
# write it at DONE. See .claude/skills/nexus-agile/references/engram_protocol.md.
#
# Engram is a separate, open-source project by Gentleman Programming
# (https://github.com/Gentleman-Programming/engram, MIT). NexusAgile integrates it
# as its reference memory engine — it does NOT vendor the binary.
#
# Usage:
#   ./setup.sh [TARGET_DIR]      # default TARGET_DIR = current directory
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$(pwd)}"

say()  { printf '\033[1;36m▸ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m! %s\033[0m\n' "$*"; }

# ── 1. Copy the methodology (skill + agents + commands) ─────────────────────
say "Installing NexusAgile into: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}/.claude/skills" "${TARGET_DIR}/.claude/agents" "${TARGET_DIR}/.claude/commands"
cp -r "${REPO_ROOT}/.claude/skills/nexus-agile/" "${TARGET_DIR}/.claude/skills/"
cp "${REPO_ROOT}/.claude/agents/nexus-"*.md      "${TARGET_DIR}/.claude/agents/"
cp "${REPO_ROOT}/.claude/commands/nexus-"*.md    "${TARGET_DIR}/.claude/commands/"
mkdir -p "${TARGET_DIR}/.claude/hooks"
cp "${REPO_ROOT}/hooks/nexus_hook.py" "${TARGET_DIR}/.claude/hooks/"
ok "Skill, $(ls "${REPO_ROOT}/.claude/agents/nexus-"*.md | wc -l) sub-agents, $(ls "${REPO_ROOT}/.claude/commands/nexus-"*.md | wc -l) commands and the hook script installed."
warn "To enforce gates, add the hooks block to .claude/settings.json: see references/enforcement.md"

# ── 2. Ensure the Engram binary (the memory engine) ─────────────────────────
if command -v engram >/dev/null 2>&1; then
  ok "Engram already installed: $(engram --version 2>/dev/null || echo present)"
else
  say "Engram not found — installing the memory engine…"
  if command -v brew >/dev/null 2>&1; then
    brew install gentleman-programming/tap/engram
  elif command -v go >/dev/null 2>&1; then
    go install github.com/Gentleman-Programming/engram/cmd/engram@latest
    warn "Make sure \$(go env GOPATH)/bin is on your PATH."
  else
    warn "Could not auto-install Engram: neither Homebrew nor Go found."
    warn "Install it manually (one option), then re-run this script:"
    warn "  brew install gentleman-programming/tap/engram"
    warn "  # or:  go install github.com/Gentleman-Programming/engram/cmd/engram@latest"
    warn "Docs: https://github.com/Gentleman-Programming/engram"
    warn "→ NexusAgile still works without it, falling back to doc/sdd/_LECCIONES.md."
  fi
fi

# ── 2b. Pin the Engram project for this repo ────────────────────────────────
# Without it, Engram guesses the project from the folder and memories land in
# the wrong place (a home folder, system32...). Use the same name as
# memory_project in project-context.md.
if command -v engram >/dev/null 2>&1; then
  if [ -f "${TARGET_DIR}/.engram/config.json" ]; then
    ok "Engram project already pinned: $(cat "${TARGET_DIR}/.engram/config.json" | tr -d '\n ')"
  else
    # Lowercase, and anything that is not a letter, digit, dot or dash becomes a dash: "Mi Proyecto_X" -> "mi-proyecto-x".
    PROJECT_NAME="${NEXUS_MEMORY_PROJECT:-$(basename "$(cd "${TARGET_DIR}" && pwd)" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9.-]+/-/g; s/^-+|-+$//g')}"
    if (cd "${TARGET_DIR}" && engram init "${PROJECT_NAME}") >/dev/null 2>&1; then
      ok "Engram project pinned as '${PROJECT_NAME}' (.engram/config.json, commit it). Use it as memory_project in project-context.md."
      [ -n "${NEXUS_MEMORY_PROJECT:-}" ] || warn "Set NEXUS_MEMORY_PROJECT=<name> before running this script to choose another name."
    else
      warn "engram init failed: run 'engram init ${PROJECT_NAME}' in ${TARGET_DIR} by hand. The rest of the setup continues."
    fi
  fi
fi

# ── 2c. Restore the memory backup, if there is one ──────────────────────────
BRAIN_DIR="${NEXUS_BRAIN_DIR:-$HOME/nexus-brain}"
if command -v engram >/dev/null 2>&1 && [ -f "${BRAIN_DIR}/memoria.json" ]; then
  say "Memory backup found in ${BRAIN_DIR}. To load it on this machine (safe to repeat):"
  echo "    python3 ${REPO_ROOT}/.claude/skills/nexus-agile/scripts/nexus_brain.py restaurar --dir ${BRAIN_DIR}"
fi

# ── 3. Wire the Engram MCP server into the target project ───────────────────
MCP_FILE="${TARGET_DIR}/.mcp.json"
if [ -f "${MCP_FILE}" ]; then
  if grep -q '"engram"' "${MCP_FILE}"; then
    ok ".mcp.json already declares the engram server — leaving it untouched."
  else
    warn "${MCP_FILE} exists but has no 'engram' server."
    warn "Merge this block into its \"mcpServers\" object manually:"
    warn '  "engram": { "command": "engram", "args": ["mcp", "--tools=agent"] }'
  fi
else
  cp "${REPO_ROOT}/setup/mcp.json" "${MCP_FILE}"
  ok "Wrote ${MCP_FILE} (engram MCP server)."
fi

echo
ok "Done. Restart Claude Code, then:"
echo "    NexusAgile, this is a new project. Read the codebase and generate project-context.md"
echo
say "Optional — for the always-on Memory Protocol (passive capture + session hooks),"
say "install the full Engram plugin from its marketplace:"
echo "    https://github.com/Gentleman-Programming/engram"
