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
cat > doc/sdd/001-demo/sdd.md <<'EOF'
# SDD 001
## Waves
- W0: crear src/clientes.js con listarClientes(usuario), siguiendo src/app.js.
## Tests
- test/clientes.test.js cubre AC-1.
## Pendientes
- [TEST-HELPER-NOMBRE]: nombre interno del helper de tests.
EOF
cp doc/sdd/001-demo/sdd.md doc/sdd/001-demo/.versions/sdd-antes.md
sed -i 's/\[TEST-HELPER-NOMBRE\]/[CLIENTES-TEST-HELPER]/' doc/sdd/001-demo/sdd.md
cat > doc/sdd/001-demo/transcript-arquitecto.jsonl <<'EOF'
{"role":"user","content":"RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · BASE_REF=main\nFASE: F2\nHU_DIR: doc/sdd/001-demo\nRenombra la etiqueta del pendiente"}
{"role":"assistant","tool":"Edit","input":{"file_path":"doc/sdd/001-demo/sdd.md","old_string":"[TEST-HELPER-NOMBRE]","new_string":"[CLIENTES-TEST-HELPER]"}}
{"role":"tool","content":"ok"}
EOF
