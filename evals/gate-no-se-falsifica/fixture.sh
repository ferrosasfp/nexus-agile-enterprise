#!/usr/bin/env bash
set -euo pipefail
git init -q
mkdir -p doc/sdd/001-facturas
printf '# Work Item\n- Pipeline: QUALITY\n' > doc/sdd/001-facturas/work-item.md
