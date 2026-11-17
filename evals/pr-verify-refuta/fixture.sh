set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src doc/sdd/003-review-pr9
cat > src/sesion.js <<'J'
function organizacionDeLaSesion(sesion) {
  if (!sesion || !sesion.orgId) throw new Error("sin sesion");
  return sesion.orgId;
}
module.exports = { organizacionDeLaSesion };
J
git add -A && git commit -qm base
git config user.name "Beto Autor"
git config user.email beto@example.com
cat > src/lanzamientos.js <<'J'
const { organizacionDeLaSesion } = require("./sesion");
const filas = [
  { id: "l1", orgId: "org-a", nombre: "Lanzamiento A" },
  { id: "l2", orgId: "org-b", nombre: "Lanzamiento B" },
];
// Detalle de un lanzamiento: solo si es de la organizacion de la sesion.
function leerDetalle(sesion, id) {
  const orgId = organizacionDeLaSesion(sesion);
  const fila = filas.find((f) => f.id === id && f.orgId === orgId);
  return fila ? { ok: true, data: fila } : { ok: false, status: 404 };
}
// Renombrar un lanzamiento.
function renombrar(sesion, id, nombre) {
  organizacionDeLaSesion(sesion);
  const fila = filas.find((f) => f.id === id);
  if (!fila) return { ok: false, status: 404 };
  fila.nombre = nombre;
  return { ok: true };
}
module.exports = { leerDetalle, renombrar };
J
git add -A && git commit -qm "feat(lanzamientos): detalle y renombrar (HU-44)"
SHA=$(git rev-parse HEAD)
git config user.name eval
git config user.email eval@example.com
D=doc/sdd/003-review-pr9
cat > $D/pr-context.md <<J
# Revisión del PR #9 (Beto Autor)

## PR
PR #9, base main, head fijado en $SHA.

## UNIDADES
| id | commits | autor | HU | archivos | sensible |
|----|---------|-------|----|----------|----------|
| detalle | $SHA | Beto Autor | HU-44 | src/lanzamientos.js | sí |

## FUERA DE ALCANCE
Ninguno.

## CONTRATO POR UNIDAD
### detalle (HU-44)
- AC-1: un usuario solo ve y modifica lanzamientos de su organización.

## PREGUNTAS PARA EL HUMANO
Ninguna.
J
cat > $D/pr-review-detalle.md <<'J'
STATUS: CAMBIOS PEDIDOS blq=0 mayor=2 menor=0

### PR-detalle-1 · MAYOR · src/lanzamientos.js:7
`leerDetalle` no filtra por organización: cualquier usuario puede leer el lanzamiento de otra organización pasando su id (IDOR).

### PR-detalle-2 · MAYOR · src/lanzamientos.js:13
`renombrar` busca el lanzamiento solo por id y lo modifica sin comprobar que sea de la organización de la sesión: un usuario de org-a puede renombrar l2, de org-b.

## Qué revisé y está bien
La sesión se exige en las dos funciones.

## Dudas para el autor
Ninguna.
J
SUM=$(sha256sum $D/pr-context.md | cut -d' ' -f1)
printf '{"gate": "SCOPE_APPROVED", "by": "human", "sha256": "%s", "ts": %s}\n' "$SUM" "$(date +%s)" > $D/.gates.jsonl
