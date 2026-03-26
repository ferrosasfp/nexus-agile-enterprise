# NexusAgile Enterprise — Casos de Uso

> Escenarios reales simulados para cada configuracion de equipo y modo.
> Cada caso muestra el flujo completo: que hace el humano, que hace el AI, donde estan los gates.

---

## Indice

| # | Escenario | Team | Modo | Pagina |
|---|-----------|------|------|--------|
| 1 | [Solo dev — Feature de pagos](#caso-1-solo-dev--feature-quality) | 1 persona | QUALITY | Este doc |
| 2 | [Solo dev — Fix trivial](#caso-2-solo-dev--fix-trivial-fast) | 1 persona | FAST | Este doc |
| 3 | [Equipo de 2 — Feature + Fix](#caso-3-equipo-de-2--feature-quality-con-peer-review) | 2 personas | QUALITY + FAST | Este doc |
| 4 | Small team — Sprint con dependencias | 3 personas | QUALITY | Pendiente |
| 5 | Small team — Primer sprint (onboarding) | 3 personas | QUALITY | Pendiente |
| 6 | Small team — Hotfix mid-sprint | 4 personas | QUALITY + HOTFIX | Pendiente |
| 7 | Medium team — Feature cross-cutting | 6 personas | QUALITY | Pendiente |
| 8 | Medium team — Sprint mixto | 6 personas | FAST + QUALITY + LAUNCH | Pendiente |
| 9 | Large team — Dependencia cross-team | 12 personas (2 equipos) | QUALITY | Pendiente |
| 10 | Edge case — FAST escala a QUALITY | 1 persona | FAST -> QUALITY | Pendiente |
| 11 | Edge case — Disputa de BLOQUEANTE en AR | 4 personas | QUALITY | Pendiente |
| 12 | Edge case — Scope change post-gate | 4 personas | QUALITY | Pendiente |

---

## Caso 1: Solo Dev — Feature QUALITY

### Contexto

| Campo | Valor |
|-------|-------|
| **Quien** | Diego, freelancer. Hace todo: PO, TL, Dev, QA. |
| **Proyecto** | App de facturacion para PyMEs |
| **Stack** | Next.js 14 (App Router) + Supabase + Tailwind |
| **Codebase** | 4 meses, ~80 archivos, tiene auth + dashboard + facturas |
| **Feature** | Clientes pagan facturas via link de MercadoPago |
| **Modo** | QUALITY (tiene pagos + webhooks + DB + auth) |

### Timeline

```
09:00  Diego describe la feature en lenguaje natural
09:02  [AUTO] F0: Bootstrap + Smart Sizing (full) + Skills Router
09:07  [AUTO] F1: Work Item + ACs EARS + 2 preguntas
09:09  Diego responde preguntas
09:12  Diego lee Work Item → HU_APPROVED
       ─── pipeline corre solo ───
09:22  [AUTO] F2: Codebase Grounding + SDD + AR del SDD
09:27  Diego lee SDD → SPEC_APPROVED
       ─── pipeline corre solo hasta DONE ───
09:29  [AUTO] F2.5: Story File
09:45  [AUTO] F3: Implementacion (3 waves + anti-hallucination)
09:48  [AUTO] AR: 8 categorias (0 BLOQUEANTES, 1 MENOR resuelto)
09:50  [AUTO] CR: Code Review
09:53  [AUTO] F4: QA (drift 0%, 6/6 ACs con evidencia)
09:54  [AUTO] DONE: artefactos + _INDEX.md
```

**Tiempo activo de Diego: ~12 minutos**
**Tiempo total: ~54 minutos**

### Flujo Detallado

#### Diego abre Claude Code

```
> NexusAgile, procesa HU: Los clientes de mis usuarios necesitan poder
> pagar una factura a traves de un link de pago con MercadoPago.
> El usuario genera el link desde la factura, se lo envia al cliente
> por email, el cliente paga, y la factura se marca como pagada
> automaticamente.
```

#### F0: Contexto (automatico)

El AI lee project-context.md, detecta stack, hace Smart Sizing:

- Senales: pagos, webhook, DB, auth, email
- SDD_MODE: full -> pipeline QUALITY
- Skills cargadas: skill-payments + skill-backend (2/2 max)
- Siguiente NNN: 012
- Branch: feat/012-link-pago-mp

Diego no hace nada. Pasa a F1.

#### F1: Discovery (automatico + 2 preguntas)

El Analyst genera el Work Item. Hace 2 preguntas (max 3):

```
[F1] Preguntas para completar DoR:

1. Tenes cuenta de MercadoPago con credenciales de produccion,
   o solo sandbox por ahora?

2. El email al cliente se envia desde la app (Resend/SendGrid)
   o el usuario copia el link y lo manda manualmente?
```

Diego responde:

```
> 1. Solo sandbox por ahora, despues paso a produccion
> 2. Por ahora el usuario copia el link. Email automatico despues.
```

Work Item generado:

| Campo | Contenido |
|-------|-----------|
| **Objetivo** | Boton "Generar link de pago" en factura -> crea preferencia MP -> cliente paga -> webhook marca como pagada |
| **AC1** | WHEN clic "Generar link" en factura pendiente THEN crea preferencia MP AND muestra link copiable |
| **AC2** | WHEN clic "Copiar link" THEN copia al clipboard AND confirmacion visual |
| **AC3** | WHEN cliente paga THEN webhook actualiza factura a "pagada" AND guarda payment_id |
| **AC4** | IF factura ya tiene link THEN muestra "Ver link" en vez de "Generar" |
| **AC5** | IF factura ya pagada THEN boton no aparece |
| **AC6** | IF webhook sin match THEN loggear sin descartar |
| **Scope IN** | Boton, MP SDK sandbox, webhook, tabla payment_links, update status |
| **Scope OUT** | Email automatico, otros medios de pago, reembolsos, modo produccion |

#### Gate 1

```
> HU_APPROVED
```

Pipeline avanza automaticamente. Diego no necesita hacer nada hasta SPEC_APPROVED.

#### F2: SDD (automatico)

Architect lee 6 archivos reales del proyecto:

| Archivo leido | Patron extraido |
|---|---|
| src/app/facturas/[id]/page.tsx | Server Component, fetch con createServerClient |
| src/lib/supabase/server.ts | createServerClient() helper, typed |
| src/app/api/webhooks/route.ts | Route Handler, verifica headers, NextResponse |
| src/components/facturas/FacturaActions.tsx | Client component, usa server actions |
| src/app/facturas/actions.ts | "use server", zod validation, try/catch |
| supabase/migrations/20240115_add_invoice_status.sql | SQL directo, ALTER TABLE |

SDD generado con:

**7 archivos** (5 CREATE + 2 MODIFY), cada uno con exemplar real del proyecto.

**Schema payment_links**: id, invoice_id (FK UNIQUE), mp_preference_id, mp_payment_link, mp_payment_id, status, created_at, paid_at.

**Constraint Directives**:
- OBLIGATORIO: mercadopago SDK, verificar x-signature, server actions, RLS
- PROHIBIDO: access_token en DB, client-side fetch a MP, archivos fuera de scope

**Waves**: W0 (migration + tipos + helper) -> W1 (server actions + webhook) -> W2 (UI)

Adversary revisa el SDD: 0 BLOQUEANTES, 1 MENOR (idempotencia en webhook).

#### Gate 2

```
> SPEC_APPROVED
```

A partir de aca, TODO es automatico hasta DONE.

#### F2.5: Story File (automatico)

Contrato autocontenido generado. El agente Dev lee SOLO este documento.

Contiene: Goal, 6 ACs, tabla de 7 archivos con exemplars, fragmentos de patron extraidos de exemplars reales, Constraint Directives, Test Expectations (4 tests), 3 Waves con verificacion entre cada una.

#### F3: Implementacion (automatico)

Dev ejecuta Anti-Hallucination Protocol antes de cada tarea:

**W0 (serial — base)**:
1. Lee exemplar de migration -> crea migration con tabla payment_links
2. Lee database.ts -> agrega tipo PaymentLink
3. Lee exemplar de helper -> crea mercadopago.ts
4. Verificacion: typecheck PASS

**W1 (parallel — logica)**:
1. Re-mapeo: lee mercadopago.ts (W0) para verificar exports
2. Lee exemplar de actions.ts -> crea payment-actions.ts
3. Lee exemplar de webhooks/route.ts -> crea webhook MP route
4. Tests: 4/4 PASS
5. Verificacion: typecheck PASS

**W2 (serial — UI)**:
1. Re-mapeo: lee payment-actions.ts (W1) para verificar funciones
2. Crea PaymentLinkButton.tsx siguiendo patron de FacturaActions
3. Modifica FacturaActions.tsx (agrega import + render)
4. Verificacion: typecheck PASS, build PASS

#### AR: Adversarial Review (automatico)

| Categoria | Resultado |
|-----------|-----------|
| Auth/Authz | PASS — RLS + session check en server action |
| Input Validation | PASS — zod en invoiceId, schema en webhook body |
| Injection | PASS — sin SQL directo, sin interpolacion |
| Secrets | PASS — MP token solo en process.env |
| Race Conditions | MENOR — webhook duplicado. Fix: ON CONFLICT DO NOTHING |
| Data Exposure | PASS — link es publico by design |
| Mock/Hardcoded Data | PASS — sin datos hardcodeados |
| DB Security | PASS — RLS, FK, UNIQUE |

**Veredicto: 0 BLOQUEANTES, 1 MENOR (resuelto con 1 linea)**

#### CR: Code Review (automatico)

- Patrones seguidos (Server Components, Server Actions)
- Naming consistente
- Imports reales (verificados con Glob)
- Tests cubren ACs criticos
- 0 archivos fuera de scope
- 1 dependencia nueva (mercadopago) aprobada en SDD

**Veredicto: APROBADO**

#### F4: QA (automatico)

**Drift Detection:**
- Esperados: 7 archivos | Reales: 7 | Fuera de scope: 0

**AC Verification (con evidencia archivo:linea):**

| AC | Status | Evidencia |
|----|--------|-----------|
| AC1 | CUMPLE | payment-actions.ts:12 + PaymentLinkButton.tsx:34 |
| AC2 | CUMPLE | PaymentLinkButton.tsx:45 clipboard + toast |
| AC3 | CUMPLE | webhooks/mercadopago/route.ts:28 update + :31 payment_id |
| AC4 | CUMPLE | PaymentLinkButton.tsx:18 condicional |
| AC5 | CUMPLE | PaymentLinkButton.tsx:15 if paid return null |
| AC6 | CUMPLE | webhooks/mercadopago/route.ts:42 console.warn + 200 |

**Quality Gates:** typecheck PASS, lint PASS, tests 4/4 PASS, build PASS

**Veredicto: APROBADO**

#### DONE (automatico)

Artefactos generados:

```
doc/sdd/012-link-pago-mp/
  work-item.md      <- F1
  sdd.md            <- F2
  story-file.md     <- F2.5
  validation.md     <- F4
  report.md         <- DONE
```

_INDEX.md actualizado:

| # | Fecha | HU | Tipo | Mode | Status | Branch |
|---|-------|----|------|------|--------|--------|
| 012 | 2026-03-26 | Link de pago MercadoPago | feature | full | DONE | feat/012-link-pago-mp |

### Resumen: Que hizo Diego vs que hizo el AI

| Diego (humano) | AI (agentes) | Tiempo Diego |
|---|---|---|
| Describio la feature | F0: Bootstrap, sizing, skills | 2 min |
| Respondio 2 preguntas | F1: Work Item + ACs EARS | 2 min |
| Leyo Work Item, escribio HU_APPROVED | Transicion F1->F2 | 3 min |
| Leyo SDD, escribio SPEC_APPROVED | F2: Grounding + SDD + AR | 5 min |
| **Nada** | F2.5 + F3 + AR + CR + F4 + DONE | 0 min |
| **Total: ~12 min activos** | **Total: ~40 min automaticos** | |

### Que obtuvo Diego

1. **Codigo funcionando** — 7 archivos, type-safe, con tests, patrones de su propio proyecto
2. **Spec documentada** — SDD con Context Map y decisiones para referencia futura
3. **Seguridad validada** — AR reviso webhook verification, secrets, RLS, race conditions
4. **Evidencia de QA** — 6 ACs con archivo:linea
5. **Audit trail** — Todo en doc/sdd/012-link-pago-mp/, versionado en git

### Por que QUALITY y no FAST

Porque toca **pagos + webhooks + DB + auth**. La regla: "Tiene pagos o auth: QUALITY siempre." No importa que Diego sea 1 persona. El riesgo de un webhook mal verificado o un secret hardcodeado es el mismo para 1 persona que para 100.

---

## Caso 2: Solo Dev — Fix Trivial (FAST)

### Contexto

| Campo | Valor |
|-------|-------|
| **Quien** | Diego, mismo freelancer |
| **Proyecto** | Misma app de facturacion |
| **Cambio** | El cliente dice "el boton de descarga dice 'Donwload', arreglalo" |
| **Modo** | FAST (1 archivo, 1 palabra, 0 logica, 0 riesgo) |

### Timeline

```
09:00  Diego: "FAST: fix typo en boton de descarga, dice Donwload"
09:01  [AUTO] Triage: califica como Quick Flow
09:02  [AUTO] Codebase Grounding ligero: lee el archivo
09:03  [AUTO] Implementa + typecheck
09:04  [AUTO] DONE + _INDEX.md
```

**Tiempo total: 4 minutos**

### Flujo Detallado

#### Diego abre Claude Code

```
> FAST: fix typo en boton de descarga, dice "Donwload" en vez de "Download"
```

#### Triage: Qualification Check (automatico)

```
QUICK FLOW QUALIFICATION:
[x] Max 2 archivos: SI (1 archivo)
[x] Max 30 lineas: SI (1 palabra)
[x] No toca DB: SI
[x] No logica nueva: SI
[x] No auth: SI
[x] No tests nuevos: SI

Resultado: CALIFICA para Quick Flow
```

#### Intake rapido

```
Quick Flow — Fix typo boton descarga

| Campo     | Valor |
|-----------|-------|
| Tipo      | patch |
| Objetivo  | Corregir "Donwload" -> "Download" |
| Archivos  | src/components/facturas/FacturaActions.tsx |
| Cambio    | 1 string, 1 caracter |
```

Diego confirma (cualquier respuesta afirmativa — FAST no tiene gate formal).

#### Codebase Grounding ligero + Implementacion

```
[FAST] Leyendo src/components/facturas/FacturaActions.tsx...
  Linea 42: <Button>Donwload PDF</Button>
  Cambio: "Donwload" -> "Download"

[FAST] typecheck: PASS
```

#### DONE

```
Quick Flow Completado

- Cambio: "Donwload" -> "Download" en FacturaActions.tsx:42
- Archivos: 1 (1 linea)
- Verificacion: typecheck PASS
- Branch: patch/013-fix-typo-download
```

_INDEX.md:

| # | Fecha | HU | Tipo | Mode | Status | Branch |
|---|-------|----|------|------|--------|--------|
| 013 | 2026-03-26 | Fix typo download | patch | quick-flow | DONE | patch/013-fix-typo-download |

### Que NO se hizo (y por que)

| Fase | Se hizo? | Por que |
|------|----------|---------|
| F0 Bootstrap | No | No se necesita contexto completo para 1 typo |
| F1 Work Item | No | El cambio ES la especificacion |
| F2 SDD | No | Sin diseno, es 1 string |
| F2.5 Story File | No | Sin contrato, es 1 linea |
| F3 Waves | No | Sin waves, es 1 cambio atomico |
| AR | No | Sin auth, sin DB, sin logica = sin superficie de ataque |
| CR | No | Typecheck es suficiente verificacion |
| F4 QA formal | No | Typecheck pass = QA pass para un typo |

### Cuando FAST escala automaticamente

Si durante el Codebase Grounding ligero Triage descubre que:

```
[FAST] Leyendo archivo...
  Hmm, "Donwload" aparece en 5 archivos diferentes.
  Y uno de ellos es un API response message.
  Y el test de integracion verifica ese mensaje exacto.

  UPGRADE: Quick Flow -> Pipeline Completo
  Razon: Cambio afecta 5 archivos + 1 test
  Recomendacion: SDD_MODE mini
```

El AI escala solo. Diego no decide. Triage califica, Triage escala.

---

## Apendice: Decision de Modo

### Para 1 persona

| Situacion | Modo | Razon |
|-----------|------|-------|
| Typo, color, padding, texto | **FAST** | 0 riesgo, 0 logica |
| Agregar campo a form sin validacion | **FAST** | 1-2 archivos, <30 lineas |
| Agregar campo a form con validacion + DB | **QUALITY** | Toca DB + logica |
| Fix de bug con causa conocida, <2 archivos | **FAST** | Trivial si la causa es obvia |
| Fix de bug con causa desconocida | **QUALITY (Hotfix)** | Investigacion de causa raiz |
| Feature con auth o pagos | **QUALITY siempre** | Riesgo de seguridad |
| Feature con DB | **QUALITY** | Schema changes necesitan spec |
| MVP nuevo desde cero | **LAUNCH** | No hay codebase |
| Prototipo para demo | **LAUNCH** | Velocidad > ceremonia |
| **En duda** | **QUALITY** | Siempre err on the side of safety |

### Overhead por modo (1 persona)

| Modo | Tiempo humano | Tiempo AI | Artefactos |
|------|--------------|-----------|-----------|
| **FAST** | 1-2 min (confirmar) | 2-5 min | Solo _INDEX.md |
| **LAUNCH** | 5-10 min (aprobar HU list) | 15-30 min por HU | Story Files simplificados |
| **QUALITY** | 10-15 min (2 gates) | 30-60 min | work-item + sdd + story-file + validation + report |

---

## Caso 3: Equipo de 2 — Feature QUALITY con Peer Review

### Contexto

| Dato | Valor |
|------|-------|
| **Proyecto** | "RecetaFit" — App web de recetas saludables con filtros nutricionales |
| **Stack** | Next.js 14 + Prisma + PostgreSQL + Tailwind |
| **Equipo** | 2 personas |
| **HU** | "Como usuario, quiero guardar recetas como favoritas para acceder rapido desde mi perfil" |
| **Modo** | QUALITY (toca DB + auth + UI + API) |

### Distribucion de Roles (2 personas)

| Persona | Roles que asume | Responsabilidad clave |
|---------|----------------|----------------------|
| **Lucia** (Senior Dev) | TL + Dev + QA Lead | Arquitectura, implementacion, validacion final, aprueba SPEC_APPROVED |
| **Martin** (Product Manager) | PO + SM | Define features, prioriza, facilita ceremonias, aprueba HU_APPROVED |

> Segun `roles_matrix.md` seccion "Equipo chico (2-4 personas)":
> PO = 1 persona (puede ser part-time). TL + QA = 1 persona (Dev senior asume ambos).
> SM = rotativo o el TL facilita. En este caso Martin facilita como SM.

### Diferencias clave vs Solo Dev

| Aspecto | Solo Dev | Equipo de 2 |
|---------|----------|-------------|
| Gates | Auto-aprobados | **PO aprueba HU_APPROVED**, **TL aprueba SPEC_APPROVED** — personas distintas |
| Code Review | Solo AI (AR + CR) | AI (AR + CR) + **peer review humano** (imposible: Lucia se auto-reviewea, ver nota) |
| PR workflow | Opcional (puede commitear a main) | **Obligatorio** — PR contra main, review requerido |
| Comunicacion | Notas para uno mismo | Canal #sprint-001, async o sync |
| Sprint Planning | El dev prioriza solo | Martin trae prioridades, Lucia estima, acuerdan |

> **Nota sobre peer review en equipo de 2**: Con solo 1 dev, no hay peer review humano posible.
> Lucia es la unica dev y TL. El protocol indica: "Equipo chico: 1 approval (TL o peer)".
> Lucia aprueba como TL. La revision de peer la cubre el AR + CR del AI.
> Si esto es insuficiente para el CTO, se puede agregar: Martin revisa UX/funcionalidad del PR aunque no sea tecnico.

---

### Timeline Completo

#### Dia 1 — Sprint Planning (30 min, sync)

**Participantes**: Martin (PO+SM) + Lucia (TL+Dev+QA)

Martin dice:
> "Las prioridades de esta semana son: (1) Favoritos — los usuarios lo piden mucho, (2) Mejora de filtros — performance lenta, (3) Fix del bug de login en Safari."

Lucia responde:
> "Favoritos es QUALITY — toca DB, API y UI. Filtros tambien QUALITY. El bug de Safari suena FAST si ya sabemos la causa. Puedo hacer Favoritos esta semana y el fix de Safari como FAST rapido."

**Resultado del planning**:

| HU | Owner | Modo | Branch | Dependencia | Status |
|----|-------|------|--------|-------------|--------|
| 001 — Guardar favoritos | @lucia | QUALITY | feat/001-favoritos | ninguna | pending |
| 002 — Fix Safari login | @lucia | FAST | hotfix/002-safari-fix | ninguna | pending (post-001) |
| 003 — Mejora filtros | @lucia | QUALITY | — | ninguna | backlog (semana prox) |

Martin escribe:
> SPRINT_APPROVED

---

#### Dia 1 — F0: Bootstrap + Smart Sizing (AI, 2 min)

Lucia dice:
> "NexusAgile, procesa esta HU: Como usuario, quiero guardar recetas como favoritas para acceder rapido desde mi perfil"

**AI ejecuta Triage Agent**:
- Lee project-context.md — Next.js 14, Prisma, PostgreSQL, /src/app structure
- Evalua: toca DB (nueva tabla), API (nuevos endpoints), UI (componente favorito + pagina perfil), Auth (user context)
- **Resultado**: QUALITY (4 areas impactadas, DB migration, requiere spec)

```
TRIAGE RESULT:
Mode: QUALITY
Reasoning: Feature touches database schema (new table), API layer (2+ endpoints),
UI (multiple components), and requires auth context. Estimated 8-12 files affected.
Confidence: HIGH
```

---

#### Dia 1 — F1: Discovery + Work Item (AI, 8 min)

**AI ejecuta Analyst Agent**:
- Escanea: `prisma/schema.prisma` (modelos existentes: User, Recipe, Category)
- Escanea: `src/app/api/` (endpoints existentes: /recipes, /auth, /categories)
- Escanea: `src/components/` (RecipeCard.tsx, RecipeGrid.tsx, ProfilePage.tsx)
- Escanea: `src/lib/auth.ts` (getServerSession, getCurrentUser)

**Work Item generado**:

```markdown
# HU-001: Guardar Recetas como Favoritas

## Descripcion
El usuario autenticado puede marcar/desmarcar recetas como favoritas.
Las recetas favoritas se listan en una seccion dedicada en su perfil.

## Acceptance Criteria

AC1: El usuario ve un icono de corazon en cada RecipeCard
AC2: Al hacer click en el corazon, la receta se guarda como favorita (toggle)
AC3: El estado del corazon persiste entre sesiones (DB)
AC4: En /profile, hay una seccion "Mis Favoritos" con las recetas guardadas
AC5: Solo usuarios autenticados pueden guardar favoritos (redirigir a login si no)
AC6: Si el usuario no tiene favoritos, muestra mensaje "No tenes favoritos aun"

## Out of Scope
- Ordenar favoritos
- Compartir lista de favoritos
- Notificaciones de cambios en recetas favoritas
```

---

#### Dia 1 — Gate: HU_APPROVED (Martin, 5 min)

Martin recibe el Work Item. Revisa:

| Check | Resultado |
|-------|-----------|
| Captura lo que quiero? | Si — favoritos con toggle y vista en perfil |
| Faltan casos? | No. Out of scope bien definido |
| ACs verificables? | Si — cada AC es observable |
| Scope razonable para 1 semana? | Si |

Martin escribe:
> HU_APPROVED

**Gate activado**. Pipeline avanza a F2.

---

#### Dia 1 — F2: SDD + Codebase Grounding (AI, 15 min)

**AI ejecuta Architect Agent** con Codebase Grounding:

1. **Lee codigo real primero** (anti-alucinacion):
   - `prisma/schema.prisma` linea 12-45: modelos User, Recipe con sus relaciones
   - `src/app/api/recipes/route.ts`: patron existente de API route (GET handler con prisma.recipe.findMany)
   - `src/components/RecipeCard.tsx`: props actuales { recipe: Recipe, className?: string }
   - `src/app/profile/page.tsx`: layout actual del perfil
   - `src/lib/auth.ts`: getCurrentUser() devuelve User | null

2. **Genera SDD con Exemplar Pattern** — cada decision referencia codigo real:

```markdown
# SDD-001: Guardar Recetas como Favoritas

## Arquitectura
- Nueva tabla Favorite (userId, recipeId, createdAt) — relacion many-to-many
- 2 API routes: POST /api/favorites (toggle), GET /api/favorites (listar)
- Componente FavoriteButton embebido en RecipeCard
- Seccion FavoritesList en ProfilePage

## Archivos a Crear
| Archivo | Proposito |
|---------|-----------|
| prisma/migrations/xxx_add_favorites/migration.sql | Schema migration |
| src/app/api/favorites/route.ts | API endpoints |
| src/components/FavoriteButton.tsx | Toggle button |
| src/components/FavoritesList.tsx | Lista en perfil |

## Archivos a Modificar
| Archivo | Cambio | Linea ref |
|---------|--------|-----------|
| prisma/schema.prisma | Agregar modelo Favorite + relaciones | Despues de linea 45 |
| src/components/RecipeCard.tsx | Agregar FavoriteButton como child | Props existentes linea 8 |
| src/app/profile/page.tsx | Agregar seccion FavoritesList | Despues de seccion "Mis Recetas" linea 32 |

## Exemplars (codigo real referenciado)
| Patron | Archivo:Linea | Usar como |
|--------|--------------|-----------|
| API route handler | src/app/api/recipes/route.ts:5-25 | Template para favorites/route.ts |
| Prisma query | src/app/api/recipes/route.ts:12 | prisma.recipe.findMany pattern |
| Component props | src/components/RecipeCard.tsx:8 | Extender interface |
| Auth check | src/lib/auth.ts:15 | getCurrentUser() en API |
| Profile layout | src/app/profile/page.tsx:32 | Insertar FavoritesList |

## Constraints
REQUIRED: Usar getCurrentUser() de src/lib/auth.ts — no crear auth propio
REQUIRED: Seguir patron de API route de recipes/route.ts
REQUIRED: Prisma migrate dev para migration
FORBIDDEN: No usar localStorage para persistir favoritos
FORBIDDEN: No crear tabla intermedia manual — usar relacion Prisma
FORBIDDEN: No modificar el modelo User existente (agregar relacion en Favorite)
```

**AI ejecuta Adversarial Review del SDD**:

```
AR-SDD RESULT:
- INFORMATIVO: Considerar indice en (userId, recipeId) para performance
- INFORMATIVO: Definir comportamiento si la receta se borra — cascade delete?
- No BLOQUEANTEs encontrados
```

---

#### Dia 1 — Gate: SPEC_APPROVED (Lucia como TL, 10 min)

Lucia revisa el SDD con ojo tecnico:

| Check | Resultado |
|-------|-----------|
| Exemplars referencian archivos reales? | Si — verifique las lineas |
| Patron de API consistente con existente? | Si — misma estructura que recipes/ |
| Migration strategy correcta? | Si — Prisma migrate dev |
| Constraints hacen sentido? | Si — evita anti-patrones |
| Falta algo? | Agrego: cascade delete en Favorite cuando se borra Recipe |

Lucia escribe:
> SPEC_APPROVED
> Nota: agregar onDelete: Cascade en la relacion Favorite -> Recipe

**Gate activado**. Pipeline avanza a F2.5.

---

#### Dia 1 — F2.5: Story File (AI, 5 min)

**AI genera el Story File** — el unico documento que Lucia necesita para implementar:

```markdown
# Story File: HU-001 — Guardar Recetas como Favoritas

## Goal
Usuarios autenticados pueden toggle favoritos en recetas y verlos en su perfil.

## Acceptance Criteria
AC1: Icono corazon en RecipeCard
AC2: Toggle guarda/quita favorito
AC3: Estado persiste en DB
AC4: /profile muestra "Mis Favoritos"
AC5: Requiere auth — redirect a /login si no
AC6: Empty state "No tenes favoritos aun"

## Wave 1 — DB + API (backend first)
### Crear: prisma/schema.prisma (modificar)
Agregar despues de modelo Recipe:
- model Favorite { id visitorId recipeId createdAt }
- Relacion: User hasMany Favorite, Recipe hasMany Favorite
- onDelete: Cascade en Recipe relation
- @@unique([userId, recipeId])
EXEMPLAR: modelo Recipe lineas 20-35 como referencia de estructura

### Crear: src/app/api/favorites/route.ts
- POST: toggle favorito (crear si no existe, borrar si existe)
- GET: listar favoritos del usuario actual
- Auth check con getCurrentUser()
EXEMPLAR: src/app/api/recipes/route.ts completo como template
REQUIRED: Retornar 401 si no auth
REQUIRED: Retornar { isFavorite: boolean } en POST

### Ejecutar: npx prisma migrate dev --name add-favorites

## Wave 2 — Componentes UI
### Crear: src/components/FavoriteButton.tsx
- Props: { recipeId: string, initialIsFavorite: boolean }
- Heart icon (lleno si favorito, outline si no)
- onClick: fetch POST /api/favorites con recipeId
- Optimistic update (cambiar icono antes de respuesta)
- Mostrar solo si usuario autenticado
EXEMPLAR: src/components/RecipeCard.tsx para patron de componente
FORBIDDEN: No usar estado global — estado local + fetch

### Crear: src/components/FavoritesList.tsx
- Fetch GET /api/favorites
- Renderear RecipeGrid con las recetas favoritas
- Empty state: "No tenes favoritos aun" con icono
EXEMPLAR: src/app/profile/page.tsx seccion "Mis Recetas" para layout

## Wave 3 — Integracion
### Modificar: src/components/RecipeCard.tsx
- Agregar FavoriteButton al card
- Pasar recipeId y estado inicial de favorito
REQUIRED: No romper props existentes — agregar isFavorite?: boolean opcional

### Modificar: src/app/profile/page.tsx
- Importar FavoritesList
- Agregar seccion despues de "Mis Recetas"
- Titulo: "Mis Favoritos"
EXEMPLAR: seccion "Mis Recetas" existente como template de layout
```

---

#### Dia 1-2 — F3: Implementacion (Lucia + AI, 2-3 horas)

Lucia crea el branch:
```bash
git checkout main && git pull
git checkout -b feat/001-favoritos
```

Lucia implementa siguiendo las Waves del Story File:

**Wave 1 — Backend** (~45 min)
- Modifica `prisma/schema.prisma`: agrega modelo Favorite con relaciones
- Corre `npx prisma migrate dev --name add-favorites`
- Crea `src/app/api/favorites/route.ts` siguiendo el exemplar de recipes
- Testea con curl: POST y GET funcionan, 401 sin auth

**Wave 2 — UI** (~45 min)
- Crea `FavoriteButton.tsx` con heart toggle y optimistic update
- Crea `FavoritesList.tsx` con fetch + empty state

**Wave 3 — Integracion** (~30 min)
- Agrega FavoriteButton a RecipeCard (prop opcional para backward compat)
- Agrega seccion FavoritesList a ProfilePage

Lucia verifica localmente:
```bash
npx prisma migrate dev     # ✓ migration applied
npm run typecheck           # ✓ no errors
npm run lint                # ✓ clean
npm run test                # ✓ 12/12 passing
npm run build               # ✓ build successful
```

---

#### Dia 2 — AR: Adversarial Review (AI, 5 min)

**AI ejecuta Adversary Agent** — ataca la implementacion de Lucia:

```
ADVERSARIAL REVIEW — HU-001

HALLAZGO 1: INFORMATIVO
Categoria: Performance
FavoriteButton hace fetch en cada render si no se cachea.
Recomendacion: Verificar que el estado inicial viene del server side.

HALLAZGO 2: INFORMATIVO
Categoria: UX
No hay feedback visual (loading state) mientras se procesa el toggle.
Recomendacion: Agregar spinner o disabled state durante fetch.

HALLAZGO 3: INFORMATIVO
Categoria: Security
Rate limiting no implementado en POST /api/favorites.
Recomendacion: Considerar rate limit para prevenir spam de toggle.

RESULTADO: 0 BLOQUEANTEs, 3 INFORMATIVOS
Implementacion APROBADA para continuar.
```

> Los INFORMATIVOS se documentan. No bloquean el PR.
> Si hubiera BLOQUEANTEs, Lucia tendria que corregir antes de abrir PR.

---

#### Dia 2 — CR: Code Review (AI, 3 min)

**AI ejecuta Code Review automatizado**:

```
CODE REVIEW — HU-001

Files reviewed: 6
- prisma/schema.prisma ✓ (modelo correcto, relaciones bien definidas)
- src/app/api/favorites/route.ts ✓ (sigue patron de recipes, auth check presente)
- src/components/FavoriteButton.tsx ✓ (optimistic update implementado)
- src/components/FavoritesList.tsx ✓ (empty state presente)
- src/components/RecipeCard.tsx ✓ (prop opcional, backward compatible)
- src/app/profile/page.tsx ✓ (seccion agregada correctamente)

Patterns check:
✓ Imports validos — todos los modulos existen
✓ Patron de API route consistente con codebase
✓ Tipos TypeScript correctos
✓ No hay archivos fuera de scope del SDD

RESULTADO: APROBADO
```

---

#### Dia 2 — PR: Pull Request (Lucia, 5 min)

Lucia hace rebase y abre PR:
```bash
git fetch origin main
git rebase origin/main          # sin conflictos
git push -u origin feat/001-favoritos
```

**PR #1 — HU-001: Guardar recetas como favoritas**

```markdown
## HU: 001 — Guardar recetas como favoritas

## Resumen
Usuarios autenticados pueden marcar recetas como favoritas con un toggle
en RecipeCard. Favoritos se muestran en una nueva seccion del perfil.

## Tipo: Feature

## Archivos clave
- prisma/schema.prisma — modelo Favorite con cascade delete
- src/app/api/favorites/route.ts — POST (toggle) + GET (listar)
- src/components/FavoriteButton.tsx — heart icon con optimistic update
- src/components/FavoritesList.tsx — grid de favoritos en perfil
- src/components/RecipeCard.tsx — integra FavoriteButton
- src/app/profile/page.tsx — seccion "Mis Favoritos"

## Testing
- ✓ Prisma migration exitosa
- ✓ Typecheck clean
- ✓ Lint clean
- ✓ 12/12 tests passing
- ✓ Build successful

## Checklist
- [x] Patron de API route seguido (exemplar: recipes/route.ts)
- [x] Auth check con getCurrentUser()
- [x] No imports inventados
- [x] No archivos fuera de scope
- [x] AR completado — 0 BLOQUEANTEs
- [x] CR completado — APROBADO

## Evidencia
AR: 0 BLOQUEANTEs, 3 INFORMATIVOS (documentados en SDD)
CR: 6/6 archivos aprobados
```

---

#### Dia 2 — Review del PR (Martin + Lucia, 10 min)

**Aqui es donde el equipo de 2 difiere del solo dev:**

En equipo solo, Lucia mergearia directo. En equipo de 2:

**Martin (como PO)** revisa funcionalidad:
- Abre el preview/staging deploy
- Prueba: login -> ir a receta -> click corazon -> ir a perfil -> ver favoritos
- Prueba: click corazon de nuevo -> se quita -> perfil vacio -> mensaje empty state
- Prueba: sin login -> no se ve el corazon (o redirige a login)

Martin comenta en el PR:
> "Funciona perfecto. El empty state esta claro. Unica sugerencia: el corazon podria tener una animacion sutil al hacer click, pero no es bloqueante, puede ser otra HU."

**Lucia (como TL)** revisa tecnica:
- Ya hizo la implementacion, pero revisa el diff final como TL
- Verifica que el AR no tiene BLOQUEANTEs
- Verifica que CI paso (typecheck + lint + test + build)

> **Limitacion de equipo de 2**: Lucia es dev Y reviewer. No hay peer review de otra persona.
> El AI (AR + CR) cubre la revision tecnica automatizada.
> Martin cubre la revision funcional/UX.
> Para el CTO: si se necesita peer review tecnico humano, se necesita minimo 3 personas.

Lucia aprueba y mergea (squash merge):
```bash
# CI green ✓ — Martin approved ✓ — AR clean ✓
# Lucia mergea como TL
git checkout main && git pull   # branch eliminado automaticamente
```

---

#### Dia 2 — F4: QA Validation (Lucia como QA + AI, 10 min)

**AI genera el Validation Report**:

```markdown
# Validation Report — HU-001

## Drift Detection
| Planificado (SDD) | Implementado | Match? |
|-------------------|-------------|--------|
| prisma/schema.prisma (mod) | ✓ modificado | ✓ |
| src/app/api/favorites/route.ts (crear) | ✓ creado | ✓ |
| src/components/FavoriteButton.tsx (crear) | ✓ creado | ✓ |
| src/components/FavoritesList.tsx (crear) | ✓ creado | ✓ |
| src/components/RecipeCard.tsx (mod) | ✓ modificado | ✓ |
| src/app/profile/page.tsx (mod) | ✓ modificado | ✓ |
| Archivos fuera de scope | Ninguno | ✓ |

Drift rate: 0%

## Acceptance Criteria Verification
| AC | Evidencia | Status |
|----|-----------|--------|
| AC1: Icono corazon en RecipeCard | src/components/RecipeCard.tsx:24 — <FavoriteButton /> renderizado | ✓ PASS |
| AC2: Toggle guarda/quita favorito | src/app/api/favorites/route.ts:18 — logica toggle implementada | ✓ PASS |
| AC3: Estado persiste en DB | prisma/schema.prisma:48 — modelo Favorite con userId+recipeId | ✓ PASS |
| AC4: /profile muestra favoritos | src/app/profile/page.tsx:45 — <FavoritesList /> renderizado | ✓ PASS |
| AC5: Requiere auth | src/app/api/favorites/route.ts:8 — getCurrentUser() + 401 | ✓ PASS |
| AC6: Empty state | src/components/FavoritesList.tsx:32 — "No tenes favoritos aun" | ✓ PASS |

## Quality Gates
| Check | Resultado |
|-------|-----------|
| TypeScript | ✓ 0 errors |
| Lint | ✓ 0 warnings |
| Tests | ✓ 12/12 passing |
| Build | ✓ successful |

## Resultado: APROBADO — 6/6 ACs cumplidos, 0% drift
```

Lucia (como QA Lead) confirma:
> "Evidencia valida. Cada AC tiene archivo:linea. Drift 0%. Aprobado."

---

#### Dia 2 — DONE (AI, 2 min)

**AI ejecuta Docs Agent** — genera report final:

```
doc/sdd/001-favoritos/
├── work-item.md      (lo que Martin aprobo)
├── sdd.md            (lo que Lucia aprobo como TL)
├── story-file.md     (lo que Lucia uso para implementar)
├── validation.md     (evidencia de QA)
└── report.md         (resumen ejecutivo)
```

AI actualiza `_INDEX.md`:
```
| 001 | Guardar recetas favoritas | QUALITY | Lucia | DONE | 2026-03-25 | 2026-03-26 |
```

---

### Resumen del Caso 3 — Equipo de 2

#### Timeline

| Dia | Actividad | Quien | Duracion |
|-----|-----------|-------|----------|
| 1 AM | Sprint Planning | Martin + Lucia | 30 min |
| 1 AM | F0 + F1 (AI) | AI | 10 min |
| 1 AM | HU_APPROVED | Martin | 5 min |
| 1 AM | F2 + AR-SDD (AI) | AI | 15 min |
| 1 PM | SPEC_APPROVED | Lucia (TL) | 10 min |
| 1 PM | F2.5 Story File (AI) | AI | 5 min |
| 1 PM - 2 AM | F3 Implementacion | Lucia + AI | 2-3 horas |
| 2 AM | AR + CR (AI) | AI | 8 min |
| 2 AM | PR abierto | Lucia | 5 min |
| 2 AM | Review PR (funcional) | Martin | 5 min |
| 2 AM | Review PR (tecnico) + Merge | Lucia (TL) | 5 min |
| 2 PM | F4 + DONE (AI + Lucia QA) | AI + Lucia | 12 min |

**Total**: ~4-5 horas de trabajo efectivo en ~1.5 dias

#### Tiempo humano vs AI

| Persona | Tiempo invertido | Actividades |
|---------|-----------------|-------------|
| **Martin (PO+SM)** | ~40 min | Sprint planning (30) + HU_APPROVED (5) + PR review funcional (5) |
| **Lucia (TL+Dev+QA)** | ~3.5 horas | SPEC_APPROVED (10) + Implementacion (2.5h) + PR (5) + Merge (5) + QA (10) |
| **AI** | ~45 min | F0+F1 (10) + F2 (15) + F2.5 (5) + AR (5) + CR (3) + F4 (5) + DONE (2) |

#### Valor del equipo de 2 vs solo dev

| Beneficio | Detalle |
|-----------|---------|
| **Separation of concerns** | Martin se enfoca en QUE, Lucia en COMO. Ni uno interfiere con el otro. |
| **Gate real** | HU_APPROVED lo da alguien que NO va a implementar. Evita sesgo de "es facil, no necesita spec". |
| **Review funcional** | Martin prueba como usuario real. Lucia no puede hacer eso objetivamente sobre su propio codigo. |
| **Accountability** | Si algo falla en produccion, hay trazabilidad: Martin aprobo el scope, Lucia aprobo la arquitectura. |
| **El PO no necesita saber codigo** | Martin nunca lee el SDD ni el Story File. Solo revisa el Work Item y prueba el resultado. |

#### Que NO cambia vs solo dev

| Aspecto | Igual que solo dev |
|---------|-------------------|
| Pipeline | F0 → F1 → HU_APPROVED → F2 → SPEC_APPROVED → F2.5 → F3 → AR → CR → F4 → DONE |
| AI agents | Los mismos 9 agentes hacen el mismo trabajo |
| Artefactos | Mismos documentos en doc/sdd/NNN/ |
| Anti-alucinacion | Exemplar Pattern, Codebase Grounding, Constraints — todo igual |
| Modos | FAST / LAUNCH / QUALITY — mismos criterios |

---

### Bonus: El Fix FAST con 2 personas (HU-002 — Safari Bug)

Despues de mergear HU-001, Lucia ataca el fix FAST:

```
Timeline total: 15 minutos

1. Lucia dice: "NexusAgile, procesa HU: Fix del bug de login que no funciona en Safari"
2. AI Triage: FAST (bug conocido, 1-2 archivos, sin DB)
3. AI Analyst: investiga, encuentra que Safari no soporta crypto.randomUUID()
4. Martin: HU_APPROVED (texto "Es exactamente ese bug")
5. AI genera mini-spec + fix directo
6. Lucia implementa: polyfill de 3 lineas en src/lib/auth.ts
7. AI AR: 0 BLOQUEANTEs
8. Lucia abre PR, Martin aprueba funcional ("ya no crashea en Safari"), Lucia mergea
9. _INDEX.md actualizado: HU-002 DONE

Total Martin: 2 min (HU_APPROVED + PR approval)
Total Lucia: 10 min (fix + PR)
Total AI: 3 min (triage + analysis + AR)
```

> En modo FAST con 2 personas, el overhead del gate HU_APPROVED es minimo (1 mensaje de Martin).
> El valor: Martin confirma que el bug reportado es el que se esta fixeando — evita el clasico "fixee otra cosa".

---

### Cuando pasar de 2 a 3+ personas

| Senal | Por que indica que necesitas mas gente |
|-------|---------------------------------------|
| Lucia no llega a hacer QA porque esta implementando | QA Lead separado |
| PRs se acumulan sin review >24h | Peer reviewer (otro dev) |
| Martin no tiene tiempo para gates | PO dedicado o SM separado |
| Carry-over rate >30% | Mas devs para cubrir capacidad |
| >3 HUs QUALITY por sprint | 1 dev no puede con todo |

> Regla de oro: **con 2 personas haces 2-3 HUs QUALITY por sprint**.
> Si necesitas mas throughput, agrega un dev (3 personas).
> Si necesitas peer review humano obligatorio, necesitas minimo 3 personas.
