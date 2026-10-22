#!/bin/sh
# Install the arf skill for Antigravity, Claude Code and Codex by symlinking this repo.
# Usage: ./install.sh [antigravity|claude|codex|all]   (default: all)
set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-all}"

link() {
  mkdir -p "$(dirname "$2")"
  if [ -e "$2" ] || [ -L "$2" ]; then
    echo "exists, skipped: $2"
  else
    ln -s "$1" "$2" && echo "linked: $2 -> $1"
  fi
}

case "$TARGET" in
  antigravity|all) link "$REPO" "$HOME/.gemini/config/plugins/arf" ;;
esac
case "$TARGET" in
  claude|all) link "$REPO/skills/arf" "$HOME/.claude/skills/arf" ;;
esac
case "$TARGET" in
  codex|all) link "$REPO/skills/arf" "$HOME/.codex/skills/arf" ;;
esac
