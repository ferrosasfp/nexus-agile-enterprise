#!/usr/bin/env bash
# Deja el diff de una HU en un archivo, con guardas, para no pegarlo en un prompt.
# Uso: review_package.sh <base> <HU_DIR> [CODE_ROOT]
set -euo pipefail
BASE="${1:?falta la rama base}"; HU_DIR="${2:?falta HU_DIR}"; CODE_ROOT="${3:-.}"
git -C "$CODE_ROOT" rev-parse --verify --quiet "$BASE^{commit}" >/dev/null || { echo "No existe la base: $BASE" >&2; exit 1; }
HEAD_SHA=$(git -C "$CODE_ROOT" rev-parse HEAD); MERGE_BASE=$(git -C "$CODE_ROOT" merge-base "$BASE" HEAD)
DIRTY=$(git -C "$CODE_ROOT" status --porcelain)
[ "$MERGE_BASE" != "$HEAD_SHA" ] || [ -n "$DIRTY" ] || { echo "Sin commits ni cambios sobre $BASE: nada que revisar" >&2; exit 1; }
OUT="$HU_DIR/review-package-${HEAD_SHA:0:8}.diff"
{
  echo "# base $MERGE_BASE  head $HEAD_SHA"
  git -C "$CODE_ROOT" diff --stat "$MERGE_BASE" HEAD
  git -C "$CODE_ROOT" diff "$MERGE_BASE" HEAD
  if [ -n "$DIRTY" ]; then
    echo "# Cambios sin commit, contra la misma base"
    git -C "$CODE_ROOT" diff HEAD
    git -C "$CODE_ROOT" ls-files --others --exclude-standard | sed 's/^/# sin rastrear: /'
  fi
} > "$OUT"
echo "$OUT"
