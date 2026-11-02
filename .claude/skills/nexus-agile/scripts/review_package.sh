#!/usr/bin/env bash
# Deja el diff de una HU en un archivo, con guardas, para no pegarlo en un prompt.
# Uso: review_package.sh <base> <HU_DIR> [CODE_ROOT]
set -euo pipefail
BASE="${1:?falta la rama base}"; HU_DIR="${2:?falta HU_DIR}"; CODE_ROOT="${3:-.}"
git -C "$CODE_ROOT" rev-parse --verify --quiet "$BASE^{commit}" >/dev/null || { echo "No existe la base: $BASE" >&2; exit 1; }
HEAD_SHA=$(git -C "$CODE_ROOT" rev-parse HEAD); MERGE_BASE=$(git -C "$CODE_ROOT" merge-base "$BASE" HEAD)
[ "$MERGE_BASE" != "$HEAD_SHA" ] || { echo "Sin commits sobre $BASE: nada que revisar" >&2; exit 1; }
OUT="$HU_DIR/review-package-${HEAD_SHA:0:8}.diff"
{
  echo "# base $MERGE_BASE  head $HEAD_SHA"
  git -C "$CODE_ROOT" diff --stat "$MERGE_BASE" HEAD
  [ -z "$(git -C "$CODE_ROOT" status --porcelain)" ] || echo "# AVISO: hay cambios sin commit, que no estan en este paquete"
  git -C "$CODE_ROOT" diff "$MERGE_BASE" HEAD
} > "$OUT"
echo "$OUT"
