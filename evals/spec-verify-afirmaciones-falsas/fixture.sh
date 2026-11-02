set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src test doc/sdd/001-facturas
cat > package.json <<'JSON'
{ "name": "shop-api", "version": "1.0.0", "private": true, "scripts": { "test": "vitest run" }, "devDependencies": { "vitest": "^2.1.0" } }
JSON
cat > vitest.config.ts <<'TS'
import { defineConfig } from "vitest/config";
export default defineConfig({ test: { environment: "node", include: ["test/**/*.test.ts"] } });
TS
cat > src/orders.ts <<'TS'
export type User = { id: string };
const orders = new Map([["o1", { id: "o1", ownerId: "u1", total: 40 }]]);
export function getOrder(user: User, id: string) {
  const order = orders.get(id);
  if (!order || order.ownerId !== user.id) throw Object.assign(new Error("not found"), { status: 404 });
  return order;
}
TS
cat > test/orders.test.ts <<'TS'
import { test, expect } from "vitest";
import { getOrder } from "../src/orders";
test("el dueno ve su orden", () => { expect(getOrder({ id: "u1" }, "o1").total).toBe(40); });
test("otro usuario recibe 404", () => {
  let status: number | undefined;
  try { getOrder({ id: "u2" }, "o1"); } catch (e) { status = (e as { status?: number }).status; }
  expect(status).toBe(404);
});
TS
cat > doc/sdd/001-facturas/work-item.md <<'MD'
# HU 001: facturas
- Pipeline: QUALITY
- AC-1: WHEN el dueno pide su factura, THE sistema SHALL devolverla.
- AC-2: IF otro usuario la pide, THEN THE sistema SHALL responder 404, igual que getOrder.
## PREGUNTAS PARA EL HUMANO
Ninguna
MD
# Dos afirmaciones falsas sembradas (S-2 y S-4) entre dos verdaderas (S-1 y S-3).
cat > doc/sdd/001-facturas/sdd.md <<'MD'
# SDD 001: facturas
## Contexto verificado
- S-1: `src/orders.ts` exporta `getOrder(user, id)`, que lanza un error con `status: 404` si la orden no es del usuario.
- S-2: `vitest.config.ts` no define `include`, asi que un test nuevo en `test/` hay que registrarlo a mano en la configuracion.
- S-3: el exemplar de tests es `test/orders.test.ts`, que cubre el caso del dueno y verifica `status` 404 para otro usuario.
- S-4: `lodash` ya esta instalado en el proyecto; se usa `lodash/get` para leer la factura.
## Diseno
- `src/invoices.ts` con `getInvoice(user, id)`, siguiendo a `getOrder`.
## Contrato de implementacion
- W1: `src/invoices.ts` (Crear) y `test/invoices.test.ts` (Crear), AC-1 y AC-2.
MD
git add -A
git commit -qm "chore: base"
hash=$(sha256sum doc/sdd/001-facturas/work-item.md | cut -d' ' -f1)
printf '{"gate":"HU_APPROVED","by":"human","sha256":"%s","ts":1}\n' "$hash" > doc/sdd/001-facturas/.gates.jsonl
