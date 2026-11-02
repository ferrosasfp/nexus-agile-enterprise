#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p doc/sdd/001-demo/.versions src
echo 'module.exports = {}' > src/app.js
printf '# project-context\n| **gate_command** | `true` |\n' > project-context.md
cat > doc/sdd/001-demo/work-item.md <<'EOF'
# Work Item 001: listado de clientes
- Pipeline: QUALITY

## Acceptance Criteria
- AC-1: WHEN un usuario con permiso abre /clientes, THE sistema SHALL listar sus clientes.

## PREGUNTAS PARA EL HUMANO
Ninguna
EOF
git add -A
git commit -qm base
cp doc/sdd/001-demo/work-item.md doc/sdd/001-demo/.versions/work-item-aprobado.md
h=$(sha256sum doc/sdd/001-demo/work-item.md | cut -d' ' -f1)
printf '{"gate":"HU_APPROVED","by":"human","sha256":"%s","copy":".versions/work-item-aprobado.md"}\n' "$h" > doc/sdd/001-demo/.gates.jsonl
sed -i 's/listar sus clientes/listar y exportar sus clientes/' doc/sdd/001-demo/work-item.md
