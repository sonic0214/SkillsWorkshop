#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  validate.sh <target-dir>
EOF
}

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 2
fi

TARGET_DIR="$1"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Target dir does not exist: $TARGET_DIR" >&2
  exit 2
fi

required=(
  "AGENTS.md"
  "context/facts.md"
  "context/architecture.md"
  "context/decisions.md"
  "skills/_templates/spec.md"
  "skills/vibe-task-execution/SKILL.md"
)

missing=()
for p in "${required[@]}"; do
  if [[ ! -f "$TARGET_DIR/$p" ]]; then
    missing+=("$p")
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "Missing required files under target dir:" >&2
  for p in "${missing[@]}"; do
    echo "  - $p" >&2
  done
  exit 1
fi

echo "OK: vibe kit installed in $TARGET_DIR"

