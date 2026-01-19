#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL="$SCRIPT_DIR/install.sh"
VALIDATE="$SCRIPT_DIR/validate.sh"

tmpdir="$(mktemp -d 2>/dev/null || mktemp -d -t vibe-kit-smoke)"
cleanup() { rm -rf "$tmpdir" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "[smoke] temp dir: $tmpdir"

echo "[smoke] default install"
bash "$INSTALL" "$tmpdir"
bash "$VALIDATE" "$tmpdir" >/dev/null

echo "[smoke] idempotent install"
bash "$INSTALL" "$tmpdir"
bash "$VALIDATE" "$tmpdir" >/dev/null

echo "[smoke] force install (should create backups + logs)"
bash "$INSTALL" "$tmpdir" --force
bash "$VALIDATE" "$tmpdir" >/dev/null

if [[ ! -d "$tmpdir/.vibe-kit-backups" ]]; then
  echo "Expected backup dir not found: $tmpdir/.vibe-kit-backups" >&2
  exit 1
fi

if [[ ! -d "$tmpdir/.vibe-kit-install/logs" ]]; then
  echo "Expected log dir not found: $tmpdir/.vibe-kit-install/logs" >&2
  exit 1
fi

log_count="$(find "$tmpdir/.vibe-kit-install/logs" -type f 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$log_count" -lt 1 ]]; then
  echo "Expected at least 1 install log under: $tmpdir/.vibe-kit-install/logs" >&2
  exit 1
fi

echo "[smoke] OK"

