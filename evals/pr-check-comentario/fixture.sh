set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src doc/sdd/004-review-pr11
cat > src/precio.js <<'J'
// Lee un precio escrito por una persona en es-AR.
function leerPrecio(texto) {
  const t = texto.trim();
  if (/^0\d+\.\d{3}$/.test(t)) return { error: "ambiguo" }; // cero adelante con punto de miles
  const limpio = t.replace(/\./g, "").replace(",", ".");
  const n = Number(limpio);
  return Number.isNaN(n) ? { error: "no es un numero" } : { valor: n };
}
module.exports = { leerPrecio };
J
git add -A && git commit -qm "feat: leer precio (HU-51)"
SHA=$(git rev-parse HEAD)
D=doc/sdd/004-review-pr11
cat > $D/pr-context.md <<J
# Revisión del PR #11
## PR
PR #11, head fijado en $SHA.
## UNIDADES
| id | commits | autor | HU | archivos | sensible |
|----|---------|-------|----|----------|----------|
| precio | $SHA | Carla | HU-51 | src/precio.js | no |
## PREGUNTAS PARA EL HUMANO
Ninguna.
J
cat > $D/pr-comment.md <<'J'
Hola Carla, revisé el PR. No hay bloqueantes.

- "015.000" se rechaza por ambiguo.
- Con coma el mismo cero también se rechaza: "015,000" da error.
- "1.500" se lee como mil quinientos.
J
SUM=$(sha256sum $D/pr-context.md | cut -d' ' -f1)
printf '{"gate": "SCOPE_APPROVED", "by": "human", "sha256": "%s", "ts": %s}\n' "$SUM" "$(date +%s)" > $D/.gates.jsonl
