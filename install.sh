#!/usr/bin/env bash
#
# Remote installer for agent-skills.
#
#   curl -fsSL https://raw.githubusercontent.com/JakobHavtorn/agent-skills/main/install.sh | bash
#
# Links skills into harness directories. Config management is handled
# by the dotfiles repo (chezmoi).
# All flags after the pipe are forwarded to bin/setup:
#
#   curl ... | bash -s -- --agent claude
#   curl ... | bash -s -- --all

set -euo pipefail

REPO_URL="https://github.com/JakobHavtorn/agent-skills.git"
INSTALL_DIR="${AGENT_SKILLS_DIR:-$HOME/.agent-skills}"

# --- Clone or update ---------------------------------------------------

if [[ -d "$INSTALL_DIR/.git" ]]; then
  echo "Updating $INSTALL_DIR ..."
  git -C "$INSTALL_DIR" pull --ff-only
else
  echo "Cloning to $INSTALL_DIR ..."
  if [[ -d "$INSTALL_DIR" ]]; then
    echo "error: $INSTALL_DIR exists but is not a git repo" >&2
    exit 1
  fi
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

# --- Run local setup ---------------------------------------------------

exec "$INSTALL_DIR/bin/setup" "$@"
