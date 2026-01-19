#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  install.sh <target-dir> [--force] [--dry-run]

Options:
  --force    Overwrite existing files (backup first)
  --dry-run  Print actions without writing files
EOF
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

TARGET_DIR=""
FORCE="0"
DRY_RUN="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE="1"; shift ;;
    --dry-run) DRY_RUN="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      if [[ -z "$TARGET_DIR" ]]; then
        TARGET_DIR="$1"
        shift
      else
        echo "Unknown argument: $1" >&2
        usage >&2
        exit 2
      fi
      ;;
  esac
done

if [[ -z "$TARGET_DIR" ]]; then
  echo "Missing <target-dir>" >&2
  usage >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(cd "$SCRIPT_DIR/../assets/kit" && pwd)"

timestamp() { date +"%Y%m%d-%H%M%S"; }

ts="$(timestamp)"
INSTALL_META_DIR="$TARGET_DIR/.vibe-kit-install"
INSTALL_LOG_DIR="$INSTALL_META_DIR/logs"
BACKUP_DIR="$TARGET_DIR/.vibe-kit-backups/$ts"
LOG_FILE="$INSTALL_LOG_DIR/$ts.log"

log() {
  local msg="$1"
  printf "%s %s\n" "$(date -Iseconds)" "$msg" | tee -a "$LOG_FILE" >/dev/null
}

ensure_dirs() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] mkdir -p \"$TARGET_DIR\" \"$INSTALL_LOG_DIR\""
    if [[ "$FORCE" == "1" ]]; then
      echo "[dry-run] mkdir -p \"$BACKUP_DIR\""
    fi
    return 0
  fi
  mkdir -p "$TARGET_DIR" "$INSTALL_LOG_DIR"
  if [[ "$FORCE" == "1" ]]; then
    mkdir -p "$BACKUP_DIR"
  fi
}

have_rsync() {
  command -v rsync >/dev/null 2>&1
}

backup_conflicts() {
  [[ "$FORCE" == "1" ]] || return 0

  while IFS= read -r -d '' src_file; do
    rel="${src_file#"$KIT_DIR"/}"
    dest="$TARGET_DIR/$rel"
    if [[ -e "$dest" ]]; then
      if [[ "$DRY_RUN" == "1" ]]; then
        echo "[dry-run] backup \"$dest\" -> \"$BACKUP_DIR/$rel\""
        continue
      fi
      mkdir -p "$(dirname "$BACKUP_DIR/$rel")"
      cp -p "$dest" "$BACKUP_DIR/$rel"
    fi
  done < <(find "$KIT_DIR" -type f -print0)
}

copy_with_rsync() {
  if [[ "$FORCE" == "1" ]]; then
    if [[ "$DRY_RUN" == "1" ]]; then
      echo "[dry-run] rsync -a \"$KIT_DIR/\" \"$TARGET_DIR/\""
      return 0
    fi
    rsync -a "$KIT_DIR/" "$TARGET_DIR/"
    return 0
  fi

if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] rsync -a --ignore-existing \"$KIT_DIR/\" \"$TARGET_DIR/\""
    return 0
  fi
  rsync -a --ignore-existing "$KIT_DIR/" "$TARGET_DIR/"
}

copy_with_cp() {
  while IFS= read -r -d '' src_file; do
    rel="${src_file#"$KIT_DIR"/}"
    dest="$TARGET_DIR/$rel"
    if [[ "$FORCE" != "1" && -e "$dest" ]]; then
      continue
    fi
    if [[ "$DRY_RUN" == "1" ]]; then
      echo "[dry-run] copy \"$src_file\" -> \"$dest\""
      continue
    fi
    mkdir -p "$(dirname "$dest")"
    cp -p "$src_file" "$dest"
  done < <(find "$KIT_DIR" -type f -print0)
}

ensure_dirs

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[dry-run] install kit from \"$KIT_DIR\" to \"$TARGET_DIR\" (force=$FORCE)"
else
  : >"$LOG_FILE"
  log "install kit from \"$KIT_DIR\" to \"$TARGET_DIR\" (force=$FORCE)"
fi

backup_conflicts

if have_rsync; then
  copy_with_rsync
else
  copy_with_cp
fi

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[dry-run] done"
else
  log "done"
fi

