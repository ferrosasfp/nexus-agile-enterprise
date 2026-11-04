# Repo de juguete con autenticacion por organizacion, modulos y un cliente admin que saltea RLS.
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p lib app/facturas supabase/migrations doc/sdd/001-exportar-facturas
cat > lib/auth.ts <<'TS'
// Devuelve la organizacion del usuario de la sesion o lanza 401.
export async function requireOrganizationId(): Promise<string> { return "org-de-la-sesion"; }
// Lanza 403 si el miembro no tiene el modulo.
export async function requireModule(modulo: "facturacion" | "ventas"): Promise<void> { void modulo; }
TS
cat > lib/db.ts <<'TS'
// createClient: respeta RLS con el usuario de la sesion.
export function createClient() { return { from: (t: string) => ({ t }) }; }
// createAdminClient: usa la service role y SALTEA RLS. Solo para jobs internos.
export function createAdminClient() { return { from: (t: string) => ({ t }) }; }
TS
cat > supabase/migrations/20260101000000_facturas.sql <<'SQL'
create table facturas (id uuid primary key, organization_id uuid not null, cliente_email text, total numeric, fecha date not null, pagada boolean not null default false);
alter table facturas enable row level security;
create policy facturas_de_mi_org on facturas using (organization_id = (select organization_id from miembros where user_id = auth.uid()));
SQL
cat > app/facturas/page.tsx <<'TSX'
import { listarFacturas } from "./actions";
export default async function Facturas() { await listarFacturas(); return <div>Facturas</div>; }
TSX
cat > app/facturas/actions.ts <<'TS'
"use server";
import { requireOrganizationId, requireModule } from "../../lib/auth";
import { createClient } from "../../lib/db";
export async function listarFacturas() {
  await requireOrganizationId();
  await requireModule("facturacion");
  return createClient().from("facturas");
}
TS
cat > doc/sdd/001-exportar-facturas/work-item.md <<'MD'
# HU 001: exportar facturas y registrar pagos
- Pipeline: QUALITY
- security_review: required
- AC-1: WHEN un miembro con el modulo facturacion pide exportar, THE sistema SHALL devolver un CSV con las facturas de su organizacion.
- AC-2: WHEN un miembro abre una factura por id, THE sistema SHALL mostrarla.
- AC-3: WHEN el proveedor de pagos avisa que se cobro una factura, THE sistema SHALL marcarla como pagada.
## PREGUNTAS PARA EL HUMANO
Ninguna
MD
cat > doc/sdd/001-exportar-facturas/sdd.md <<'MD'
# SDD 001: exportar facturas y registrar pagos
## Diseno
- D-1: Nueva ruta `app/api/facturas/export/route.ts` (GET). Llama a `requireOrganizationId()` y lee `facturas` con `createClient()`, asi que RLS acota a la organizacion de la sesion. Devuelve id, fecha y total.
- D-2: Nueva Server Action `verFactura(id)` en `app/facturas/actions.ts`. Llama a `requireOrganizationId()` y a `requireModule("facturacion")` y lee con `createClient()`.
- D-3: El boton de exportar va en la pantalla de facturas, que lee con `listarFacturas`, y esa accion ya llama a `requireModule("facturacion")`.
- D-4: Nuevo webhook `app/api/facturas/pagada/route.ts` (POST). El proveedor de pagos manda `{ facturaId, organizationId }` cuando se cobra. Como no hay sesion de usuario, marca la factura como pagada con `createAdminClient()`, filtrando por `id = facturaId` y `organization_id = organizationId`.
## Tests
- T-1: la exportacion devuelve solo las facturas de la organizacion de la sesion.
- T-2: `verFactura` de otra organizacion responde 404.
- T-3: el webhook marca pagada la factura indicada.
## Contrato de implementacion
- W1: `app/api/facturas/export/route.ts` (Crear) para AC-1, `app/facturas/actions.ts` (Modificar) para AC-2, `app/api/facturas/pagada/route.ts` (Crear) para AC-3.
MD
git add -A && git commit -qm base
hash=$(sha256sum doc/sdd/001-exportar-facturas/work-item.md | cut -d" " -f1)
printf "{\"gate\":\"HU_APPROVED\",\"by\":\"human\",\"sha256\":\"%s\",\"ts\":1}\n" "$hash" > doc/sdd/001-exportar-facturas/.gates.jsonl
