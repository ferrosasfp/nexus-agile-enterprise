set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src tests doc/sdd/001-totales
cat > vitest.config.ts <<'TS'
import { defineConfig } from "vitest/config";
export default defineConfig({ test: { environment: "node", include: ["tests/**/*.test.ts"] } });
TS
cat > src/totales.ts <<'TS'
export function total(items: { precio: number }[]) { return items.reduce((a, i) => a + i.precio, 0); }
TS
cat > project-context.md <<'MD'
| Campo | Valor |
|-------|-------|
| **Nombre** | tienda |
| **gate_command** | `npx vitest run` |
| **tracker** | archivo |
MD
# Memoria en el respaldo de archivo: una leccion vigente y un hecho viejo (el hash es de una version anterior del archivo).
cat > doc/sdd/_LECCIONES.md <<'MD'
# Lecciones y hechos del proyecto

## hecho/vitest.config.ts
- Claim: vitest.config.ts no define include; un test nuevo hay que registrarlo a mano en la configuracion.
- File: vitest.config.ts @ 0000000000000000000000000000000000000000
- Evidence: vitest.config.ts:2
- Source: HU-000, 2026-09-01

## trampa/rtk-cat
- What: el proxy rtk reescribe cat y puede esconder lineas de un archivo.
- Learned: para afirmar algo de un archivo, leerlo con Read o con rtk proxy cat.
- Source: HU-000, 2026-09-01
MD
cat > doc/sdd/_INDEX.md <<'MD'
| NNN | Fecha | HU | Tipo | Pipeline | Estado | Responsable |
|-----|-------|----|------|----------|--------|-------------|
| 001 | 2026-11-04 | Totales con descuento | feature | QUALITY | en curso | Fernando |
MD
git add -A && git commit -qm base
