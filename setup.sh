#!/usr/bin/env bash
#
# NexusAgile — setup
#
# Installs NexusAgile into a target project AND wires up persistent memory (Engram).
# Memory is what lets NexusAgile learn from its own errors across sessions
# (Auto-Blindaje + mem_save/mem_search at each pipeline phase).
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
ok "Skill, 6 sub-agents and 11 commands installed."

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
    warn "→ NexusAgile still works without it, falling back to a manual MEMORY.md."
  fi
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
  cp "${REPO_ROOT}/.mcp.json" "${MCP_FILE}"
  ok "Wrote ${MCP_FILE} (engram MCP server)."
fi

echo
ok "Done. Restart Claude Code, then:"
echo "    NexusAgile, this is a new project. Read the codebase and generate project-context.md"
echo
say "Optional — for the always-on Memory Protocol (passive capture + session hooks),"
say "install the full Engram plugin from its marketplace:"
echo "    https://github.com/Gentleman-Programming/engram"
