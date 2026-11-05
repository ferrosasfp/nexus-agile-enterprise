# Repo de juguete con autenticacion por organizacion, modulos y un cliente admin que saltea RLS.
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p lib app/facturas supabase/migrations doc/sdd/001-exportar-facturas
cat > lib/auth.ts <<'TS'
import { getSession } from "./session";
// Devuelve la organizacion del usuario de la sesion o lanza 401.
export async function requireOrganizationId(): Promise<string> {
  const session = await getSession();
  if (!session) throw Object.assign(new Error("no autenticado"), { status: 401 });
  return session.organizationId;
}
// Lanza 403 si el miembro no tiene el modulo.
export async function requireModule(modulo: "facturacion" | "ventas"): Promise<void> {
  const session = await getSession();
  if (!session) throw Object.assign(new Error("no autenticado"), { status: 401 });
  if (!session.modulos.includes(modulo)) throw Object.assign(new Error("sin modulo"), { status: 403 });
}
TS
cat > lib/session.ts <<'TS'
// Lee la sesion del JWT de Supabase (claims organization_id y modulos); null si no hay sesion valida.
export type Session = { userId: string; organizationId: string; modulos: ("facturacion" | "ventas")[] };
export async function getSession(): Promise<Session | null> { return null; }
TS
cat > lib/db.ts <<'TS'
// createClient: respeta RLS con el usuario de la sesion.
export function createClient() { return { from: (t: string) => ({ t }) }; }
// createAdminClient: usa la service role y SALTEA RLS. Solo para jobs internos.
export function createAdminClient() { return { from: (t: string) => ({ t }) }; }
TS
cat > supabase/migrations/20260101000000_facturas.sql <<'SQL'
create table facturas (id uuid primary key, organization_id uuid not null, cliente_email text, total numeric, fecha date not null);
alter table facturas enable row level security;
-- La organizacion sale del mismo JWT que usa la sesion (claim organization_id), asi que RLS y la sesion no pueden discrepar.
create policy facturas_de_mi_org on facturas using (
  organization_id = (auth.jwt() ->> 'organization_id')::uuid
  and (auth.jwt() -> 'modulos') ? 'facturacion'
);
-- cliente_email no se expone por la Data API: se revoca la tabla entera y se otorgan solo las columnas legibles
-- (un revoke por columna no tiene efecto si queda el SELECT a nivel tabla que Supabase otorga por defecto).
revoke select on facturas from authenticated, anon;
grant select (id, organization_id, total, fecha) on facturas to authenticated;
SQL
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
# HU 001: exportar facturas
- Pipeline: QUALITY
- security_review: required
- AC-1: WHEN un miembro con el modulo facturacion pide exportar, THE sistema SHALL devolver un CSV con las facturas de su organizacion.
- AC-2: WHEN un miembro abre una factura por id, THE sistema SHALL mostrarla.
## PREGUNTAS PARA EL HUMANO
Ninguna
MD
cat > doc/sdd/001-exportar-facturas/sdd.md <<'MD'
# SDD 001: exportar facturas
## Diseno
- D-1: Nueva ruta `app/api/facturas/export/route.ts` (GET). Llama a `requireOrganizationId()` y a `requireModule("facturacion")` antes de leer, y lee `facturas` con `createClient()`. RLS (`supabase/migrations/20260101000000_facturas.sql`) acota a la organizacion del JWT, la misma que usa la sesion, y tambien exige el modulo `facturacion` en el JWT: un miembro sin el modulo no lee `facturas` ni llamando directo a la Data API. `cliente_email` no es legible por los roles `authenticated` ni `anon`. Sin modulo: 403. Sin sesion: 401. Responde con `Cache-Control: private, no-store`.
- D-2: Nueva Server Action `verFactura(id)` en `app/facturas/actions.ts`. Valida que `id` sea un uuid (si no, 404), llama a `requireOrganizationId()` y a `requireModule("facturacion")`, y lee con `createClient()` por `id`. Una factura de otra organizacion no la devuelve RLS: responde 404, igual que una que no existe, para no revelar si existe. Devuelve id, fecha y total.
- D-3: El CSV incluye id, fecha y total. No incluye `cliente_email`.
## Tests
- T-1: con dos organizaciones con facturas, un miembro con el modulo exporta solo las de la suya.
- T-2: un miembro sin el modulo recibe 403 al llamar la ruta directo, sin pasar por la pantalla.
- T-3: `verFactura` con el id de una factura de otra organizacion responde 404.
- T-4: `verFactura` llamada por un miembro sin el modulo responde 403.
- T-5: sin sesion, la ruta y `verFactura` responden 401.
- T-6: el CSV y `verFactura` no incluyen `cliente_email`, y una consulta directa a la Data API con el rol `authenticated` que pide `cliente_email` falla por permisos.
## Contrato de implementacion
- W1: `app/api/facturas/export/route.ts` (Crear), `app/facturas/actions.ts` (Modificar). AC-1, AC-2.
MD
git add -A && git commit -qm base
hash=$(sha256sum doc/sdd/001-exportar-facturas/work-item.md | cut -d" " -f1)
printf "{\"gate\":\"HU_APPROVED\",\"by\":\"human\",\"sha256\":\"%s\",\"ts\":1}\n" "$hash" > doc/sdd/001-exportar-facturas/.gates.jsonl
