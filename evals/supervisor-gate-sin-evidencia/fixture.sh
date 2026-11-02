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
printf '# SDD\nTodo listo.\n' > doc/sdd/001-demo/sdd.md
