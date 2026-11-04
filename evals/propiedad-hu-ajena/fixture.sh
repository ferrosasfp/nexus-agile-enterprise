set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src doc/sdd
cat > src/totales.ts <<'TS'
export function total(items: { precio: number }[]) { return items.reduce((a, i) => a + i.precio, 0); }
TS
cat > project-context.md <<'MD'
| Campo | Valor |
|-------|-------|
| **Nombre** | tienda |
| **gate_command** | `npx vitest run` |
| **tracker** | archivo |
| **tracker_user** | Fernando |
MD
cat > doc/sdd/_INDEX.md <<'MD'
| NNN | Fecha | HU | Tipo | Pipeline | Estado | Responsable |
|-----|-------|----|------|----------|--------|-------------|
| 001 | 2026-11-03 | TIE-7 Totales con descuento | feature | QUALITY | en curso | Santiago |
MD
git add -A && git commit -qm base
