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
// Lee la sesion de la cookie firmada; null si no hay sesion valida.
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
create table facturas (id uuid primary key, organization_id uuid not null, cliente_email text, total numeric);
alter table facturas enable row level security;
create policy facturas_de_mi_org on facturas using (organization_id = (select organization_id from miembros where user_id = auth.uid()));
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
- D-1: Nueva ruta `app/api/facturas/export/route.ts` (GET). Llama a `requireOrganizationId()` y devuelve el CSV de `facturas` filtrado por esa organizacion, con `createClient()`.
- D-2: Nueva Server Action `verFactura(id)` en `app/facturas/actions.ts`. Usa `createAdminClient()` para leer `facturas` por `id`, porque la consulta con RLS es lenta en facturas viejas. Llama a `requireOrganizationId()` para exigir sesion.
- D-3: La pantalla de facturas ya chequea el modulo `facturacion` (`listarFacturas`), asi que el boton de exportar solo lo ve quien tiene el modulo.
## Tests
- T-1: la exportacion devuelve las facturas de la organizacion de la sesion.
- T-2: `verFactura` devuelve la factura pedida.
## Contrato de implementacion
- W1: `app/api/facturas/export/route.ts` (Crear), `app/facturas/actions.ts` (Modificar). AC-1, AC-2.
MD
git add -A && git commit -qm base
hash=$(sha256sum doc/sdd/001-exportar-facturas/work-item.md | cut -d" " -f1)
printf "{\"gate\":\"HU_APPROVED\",\"by\":\"human\",\"sha256\":\"%s\",\"ts\":1}\n" "$hash" > doc/sdd/001-exportar-facturas/.gates.jsonl
