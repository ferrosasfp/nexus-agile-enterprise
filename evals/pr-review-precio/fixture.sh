set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src test doc/sdd/002-review-pr7
cat > package.json <<'J'
{ "name": "lanzamientos", "version": "1.0.0", "private": true, "scripts": { "test": "node --test test/" } }
J
cat > src/lanzamientos.js <<'J'
const lanzamientos = new Map();
function guardar(orgId, datos) {
  if (!orgId) throw new Error("sin organizacion");
  lanzamientos.set(datos.id, { ...datos, orgId });
  return { ok: true };
}
module.exports = { guardar, lanzamientos };
J
git add -A && git commit -qm base
git config user.name "Ana Autora"
git config user.email ana@example.com
cat > src/formulario.js <<'J'
// Precio de la oferta: el usuario lo escribe en el formulario, con coma o punto decimal.
function numeroONulo(texto) {
  const limpio = texto.trim().replace(",", ".");
  if (limpio === "") return null;
  return Number(limpio);
}
function datosDelFormulario(campos) {
  return { id: campos.id, nombre: campos.nombre.trim(), precio: numeroONulo(campos.precio) };
}
module.exports = { numeroONulo, datosDelFormulario };
J
cat > test/formulario.test.js <<'J'
const test = require("node:test");
const assert = require("node:assert");
const { numeroONulo } = require("../src/formulario");
test("precio con coma decimal", () => assert.strictEqual(numeroONulo("997,50"), 997.5));
test("vacio es null", () => assert.strictEqual(numeroONulo(" "), null));
J
cat > CHANGES.md <<'J'
## Lanzamientos: precio de la oferta
El formulario acepta el precio con coma o punto decimal, como lo escribe el usuario. Tests: formulario.test.js.
J
git add -A && git commit -qm "feat(lanzamientos): precio de la oferta en el formulario (HU-29)"
SHA=$(git rev-parse HEAD)
git config user.name eval
git config user.email eval@example.com
cat > doc/sdd/002-review-pr7/pr-context.md <<J
# Revisión del PR #7 (Ana Autora)

## PR
PR #7, autora Ana Autora, base main, head fijado en $SHA.

## UNIDADES
| id | commits | autor | HU | archivos | sensible |
|----|---------|-------|----|----------|----------|
| precio | $SHA | Ana Autora | HU-29 | src/formulario.js, test/formulario.test.js, CHANGES.md | no |

## FUERA DE ALCANCE
Ninguno.

## CONTRATO POR UNIDAD
### precio (HU-29)
- AC-1: el usuario de Argentina escribe el precio de la oferta como lo escribe siempre (por ejemplo 1.500 o 997,50) y se guarda el valor correcto.
- AC-2: un precio inválido se rechaza con un mensaje claro en español.

## PREGUNTAS PARA EL HUMANO
Ninguna.
J
SUM=$(sha256sum doc/sdd/002-review-pr7/pr-context.md | cut -d' ' -f1)
printf '{"gate": "SCOPE_APPROVED", "by": "human", "sha256": "%s", "ts": %s}\n' "$SUM" "$(date +%s)" > doc/sdd/002-review-pr7/.gates.jsonl
