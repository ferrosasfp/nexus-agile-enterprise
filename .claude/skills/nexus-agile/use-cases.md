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
| 4 | [Medium team — Sprint con 3 HUs paralelas](#caso-4-medium-team--sprint-con-3-hus-paralelas) | 5 personas | QUALITY + FAST | Este doc |
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

#### Dia 1-2 — F3: Implementacion (AI implementa, Lucia supervisa — 2-3 horas)

Lucia crea el branch y lanza al AI:
```bash
git checkout main && git pull
git checkout -b feat/001-favoritos
```

> **Principio clave**: El AI implementa. Lucia supervisa, revisa y ajusta.
> Igual que en solo dev, el agente AI es quien escribe el codigo.
> La diferencia: Lucia tiene criterio tecnico para detectar errores que el solo dev podria pasar por alto.

**Wave 1 — Backend** (~15 min AI + 10 min Lucia review)

Lucia dice:
> "Implementa Wave 1 del Story File: modelo Favorite en Prisma + API routes"

El AI:
- Lee el exemplar `src/app/api/recipes/route.ts` (Codebase Grounding)
- Modifica `prisma/schema.prisma`: agrega modelo Favorite con relaciones + cascade delete
- Crea `src/app/api/favorites/route.ts` siguiendo el patron exacto del exemplar
- Corre `npx prisma migrate dev --name add-favorites`

Lucia revisa el output:
- Verifica que el schema tiene `@@unique([userId, recipeId])` — si, correcto
- Verifica que el API route usa `getCurrentUser()` del exemplar — si, no invento auth propio
- Prueba rapida con curl: POST toggle funciona, GET lista funciona, 401 sin auth
- **Ajuste**: "Agrega `onDelete: Cascade` en la relacion con Recipe" (nota del SPEC_APPROVED)

**Wave 2 — UI** (~15 min AI + 10 min Lucia review)

Lucia dice:
> "Implementa Wave 2: FavoriteButton y FavoritesList"

El AI:
- Lee el exemplar `src/components/RecipeCard.tsx` para patron de componente
- Crea `FavoriteButton.tsx` con heart toggle + optimistic update
- Lee el exemplar `src/app/profile/page.tsx` seccion "Mis Recetas" para layout
- Crea `FavoritesList.tsx` con fetch + empty state

Lucia revisa:
- Verifica que FavoriteButton usa estado local (no global) — cumple FORBIDDEN del Story File
- Verifica empty state "No tenes favoritos aun" — presente
- **Sin ajustes necesarios**

**Wave 3 — Integracion** (~10 min AI + 5 min Lucia review)

Lucia dice:
> "Implementa Wave 3: integra FavoriteButton en RecipeCard y FavoritesList en ProfilePage"

El AI:
- Modifica `RecipeCard.tsx`: agrega prop `isFavorite?: boolean` (opcional, backward compatible)
- Modifica `ProfilePage.tsx`: agrega seccion "Mis Favoritos" despues de "Mis Recetas"

Lucia revisa:
- Verifica que no rompio props existentes de RecipeCard — correcto, prop es opcional
- Verifica que el layout del perfil es consistente — correcto, sigue patron existente

**Verificacion final** (AI + Lucia, 5 min):
```bash
npx prisma migrate dev     # ✓ migration applied
npm run typecheck           # ✓ no errors
npm run lint                # ✓ clean
npm run test                # ✓ 12/12 passing
npm run build               # ✓ build successful
```

> **Tiempo real de Lucia en F3**: ~25 min revisando outputs del AI + 5 min de ajustes
> **Tiempo real del AI en F3**: ~40 min implementando 3 waves
> **vs Solo dev**: Diego revisa sin criterio de TL. Lucia revisa CON criterio de TL — detecta mas cosas.

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
| 1 PM - 2 AM | F3 Implementacion | AI implementa, Lucia supervisa | ~1.5 horas |
| 2 AM | AR + CR (AI) | AI | 8 min |
| 2 AM | PR abierto | Lucia | 5 min |
| 2 AM | Review PR (funcional) | Martin | 5 min |
| 2 AM | Review PR (tecnico) + Merge | Lucia (TL) | 5 min |
| 2 PM | F4 + DONE (AI + Lucia QA) | AI + Lucia | 12 min |

**Total**: ~3 horas de trabajo efectivo en ~1.5 dias (Lucia solo invierte ~1h de su tiempo)

#### Tiempo humano vs AI

| Persona | Tiempo invertido | Actividades |
|---------|-----------------|-------------|
| **Martin (PO+SM)** | ~40 min | Sprint planning (30) + HU_APPROVED (5) + PR review funcional (5) |
| **Lucia (TL+Dev+QA)** | ~1 hora | SPEC_APPROVED (10) + Supervision F3 (30) + PR (5) + Merge (5) + QA (10) |
| **AI** | ~1.5 horas | F0+F1 (10) + F2 (15) + F2.5 (5) + **F3 implementacion (40)** + AR (5) + CR (3) + F4 (5) + DONE (2) |

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
6. AI implementa: polyfill de 3 lineas en src/lib/auth.ts. Lucia revisa (30 seg).
7. AI AR: 0 BLOQUEANTEs
8. Lucia abre PR, Martin aprueba funcional ("ya no crashea en Safari"), Lucia mergea
9. _INDEX.md actualizado: HU-002 DONE

Total Martin: 2 min (HU_APPROVED + PR approval)
Total Lucia: 3 min (revisar fix del AI + abrir PR)
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

---

## Caso 4: Medium Team — Sprint con 3 HUs Paralelas

### Contexto

| Dato | Valor |
|------|-------|
| **Proyecto** | "LogiTrack" — Plataforma de gestion logistica para PyMEs |
| **Stack** | Next.js 14 + tRPC + Prisma + PostgreSQL + Tailwind + Zustand |
| **Equipo** | 5 personas |
| **Sprint** | Sprint 4 — el equipo ya tiene 3 sprints de experiencia con NexusAgile |
| **HUs del sprint** | 3 HUs QUALITY en paralelo + 1 FAST mid-sprint |

### Distribucion de Roles (5 personas)

| Persona | Rol | Responsabilidad |
|---------|-----|----------------|
| **Ana** | Product Owner | Define que se construye, prioriza backlog, aprueba HU_APPROVED |
| **Carlos** | Tech Lead | Arquitectura, aprueba SPEC_APPROVED, review final de PRs, resuelve conflictos tecnicos |
| **Sofia** | Developer 1 | Implementa HUs asignadas (con AI), peer review de PRs de Mateo |
| **Mateo** | Developer 2 | Implementa HUs asignadas (con AI), peer review de PRs de Sofia |
| **Valeria** | QA Lead + SM | Facilita ceremonias, valida evidencia en F4, drift detection |

> Segun `roles_matrix.md` seccion "Equipo mediano (5-8 personas)":
> PO dedicado, TL dedicado, QA dedicado, 2+ devs, SM (puede compartirse).
> Valeria combina QA + SM — viable en equipo de 5.

### Diferencias clave vs Equipo de 2

| Aspecto | Equipo de 2 | Equipo de 5 |
|---------|-------------|-------------|
| Gates | 2 personas se turnan | **PO, TL, QA son personas distintas** — nadie aprueba su propio trabajo |
| Peer review | Imposible (1 solo dev) | **Real**: Sofia revisa PRs de Mateo y viceversa |
| Paralelismo | 1 HU a la vez | **2-3 HUs simultaneas** — cada dev trabaja su HU |
| Conflictos | No hay (1 dev) | **Prevencion activa**: TL verifica scope disjunto en planning |
| QA | Dev hace su propio QA | **QA Lead independiente** — Valeria valida sin sesgo |
| Ceremonias | Informales | **Estructuradas**: Planning, Daily, Status, Retro — Valeria facilita |

---

### Dia 1 — Sprint Planning (45 min, sync)

**Facilita**: Valeria (SM)
**Participantes**: Ana, Carlos, Sofia, Mateo, Valeria

#### Paso 1: Ana presenta backlog priorizado

Ana dice:
> "Prioridades de Sprint 4:
> 1. Dashboard de metricas de envio — los clientes lo piden hace 2 sprints
> 2. Notificaciones por email cuando cambia el estado de un envio
> 3. Exportar reporte de envios a PDF
> Todas son QUALITY — tocan DB, API y UI."

#### Paso 2: Carlos estima y verifica scope

Carlos analiza dependencias:
> "Dashboard y Notificaciones son independientes — dominios distintos. Dashboard toca /dashboard/* y metricas. Notificaciones toca /api/notifications y el servicio de email. Zero overlap.
>
> PDF Export tiene soft dependency con Dashboard — usa las mismas queries de metricas. Pero puede mockear los datos mientras Dashboard no esta mergeado.
>
> **Propuesta**: Sofia toma Dashboard (mas complejo, ella conoce el dominio). Mateo toma Notificaciones. PDF Export arranca cuando Dashboard mergee, o Mateo la toma con mock."

#### Paso 3: Asignacion + dependency check

| HU | Owner | Modo | Branch | Dependencia | Archivos clave |
|----|-------|------|--------|-------------|---------------|
| 001 — Dashboard metricas | @sofia | QUALITY | feat/001-dashboard | ninguna | /dashboard/*, /api/metrics |
| 002 — Notificaciones email | @mateo | QUALITY | feat/002-notifications | ninguna | /api/notifications, /lib/email |
| 003 — Export PDF | @mateo | QUALITY | feat/003-export-pdf | soft dep con 001 | /api/export, /lib/pdf |

Carlos verifica:
> "Sofia toca /dashboard y /api/metrics. Mateo toca /api/notifications y /lib/email. **Zero file overlap**. Pueden correr 100% en paralelo. HU-003 la toma Mateo despues de HU-002 con Integration Contract para las queries de metricas."

Valeria confirma capacidad:
> "2 devs x 5 dias = 10 dev-days. 3 HUs QUALITY es ambicioso. Si HU-003 no llega, la llevamos al sprint 5. El commitment firme es HU-001 + HU-002."

Ana y Carlos escriben:
> SPRINT_APPROVED

---

### Dia 1 — Pipeline Paralelo: 2 HUs Simultaneas

#### HU-001 y HU-002 arrancan en paralelo

El AI procesa ambas HUs simultaneamente. Cada una pasa por su propio pipeline:

```
                    PARALELO
         ┌──────────────────────────────┐
         │                              │
HU-001:  F0 → F1 → [HU_APPROVED] → F2 → [SPEC_APPROVED] → F2.5 → F3...
         │                              │
HU-002:  F0 → F1 → [HU_APPROVED] → F2 → [SPEC_APPROVED] → F2.5 → F3...
         │                              │
         └──────────────────────────────┘
```

#### F0 + F1: AI procesa ambas (15 min)

**HU-001 (Dashboard)** — AI genera Work Item:
```markdown
AC1: Dashboard muestra metricas de envios: total, en transito, entregados, demorados
AC2: Filtro por rango de fechas
AC3: Graficos de tendencia (envios por dia, semana, mes)
AC4: KPIs con comparativa vs periodo anterior (flechas up/down)
AC5: Dashboard accesible solo para roles admin y manager
AC6: Loading skeleton mientras cargan los datos
```

**HU-002 (Notificaciones)** — AI genera Work Item:
```markdown
AC1: Cuando un envio cambia de estado, se envia email al cliente
AC2: Template de email con: numero de envio, estado anterior, estado nuevo, fecha
AC3: Cola de emails con retry (no perder notificaciones si el servicio falla)
AC4: Configuracion: el cliente puede activar/desactivar notificaciones
AC5: Log de notificaciones enviadas (auditable)
AC6: Rate limit: max 10 emails por envio (prevenir loops)
```

#### Gate: HU_APPROVED x2 (Ana, 10 min)

Ana revisa ambos Work Items:

**HU-001**: "Los ACs cubren lo que necesito. El filtro por fecha es clave. Agrego: AC7 — el dashboard se actualiza automaticamente cada 5 min sin refresh manual."

**HU-002**: "Los ACs estan bien. El rate limit es buena idea. El log auditable es necesario por compliance. Aprobado."

Ana escribe:
> HU-001: HU_APPROVED (con AC7 agregado: auto-refresh cada 5 min)
> HU-002: HU_APPROVED

#### F2: AI genera SDDs para ambas (20 min en paralelo)

El AI genera los SDDs en paralelo — cada uno con Codebase Grounding sobre el proyecto real.

**SDD-001 (Dashboard)** — archivos clave:
| Accion | Archivo |
|--------|---------|
| Crear | src/app/dashboard/page.tsx |
| Crear | src/app/dashboard/components/MetricsCards.tsx |
| Crear | src/app/dashboard/components/TrendChart.tsx |
| Crear | src/app/dashboard/components/DateFilter.tsx |
| Crear | src/app/api/metrics/route.ts |
| Crear | src/lib/metrics.ts (queries de metricas) |
| Modificar | src/app/layout.tsx (agregar link a dashboard en nav) |
| Modificar | prisma/schema.prisma (indice para queries de metricas) |

**SDD-002 (Notificaciones)** — archivos clave:
| Accion | Archivo |
|--------|---------|
| Crear | src/lib/email/notification-service.ts |
| Crear | src/lib/email/templates/shipment-status.tsx |
| Crear | src/app/api/notifications/route.ts |
| Crear | src/app/api/notifications/preferences/route.ts |
| Crear | src/app/settings/notifications/page.tsx |
| Modificar | prisma/schema.prisma (modelo NotificationLog + NotificationPreference) |
| Modificar | src/app/api/shipments/[id]/route.ts (trigger notificacion al cambiar estado) |

**Carlos detecta overlap**:
> "Ambas tocan prisma/schema.prisma. HU-001 agrega un indice. HU-002 agrega 2 modelos. No se pisan — son cambios en zonas distintas del schema. Pero para evitar conflicto de migration: **HU-001 mergea primero su migration**, HU-002 hace rebase antes de crear la suya."

#### Gate: SPEC_APPROVED x2 (Carlos, 15 min)

Carlos revisa ambos SDDs:

**SDD-001**: "Exemplars correctos. Queries de metricas bien definidas. Agrego constraint: REQUIRED usar React Query para cache + auto-refresh (no polling manual)."

**SDD-002**: "Patron de queue con retry esta bien. Template de email usa React Email — consistente con lo que ya tenemos. Constraint agregado: REQUIRED implementar dead-letter queue para emails que fallan 3x."

Carlos escribe:
> SDD-001: SPEC_APPROVED
> SDD-002: SPEC_APPROVED

#### F2.5: Story Files generados (AI, 5 min cada uno)

El AI genera 2 Story Files. Cada dev recibe el suyo:
- Sofia recibe Story File HU-001 (Dashboard) — 4 waves
- Mateo recibe Story File HU-002 (Notificaciones) — 3 waves

---

### Dia 1-3 — F3: Implementacion Paralela

> **Recordatorio**: El AI implementa. Los devs supervisan, revisan y ajustan.
> Esto es igual que en solo dev y equipo de 2, pero ahora hay 2 pipelines en paralelo.

#### Sofia + AI: HU-001 Dashboard (Dia 1 tarde - Dia 2)

Sofia crea su branch:
```bash
git checkout main && git pull
git checkout -b feat/001-dashboard
```

**Wave 1 — Queries de metricas** (~15 min AI + 10 min Sofia review)

Sofia dice:
> "Implementa Wave 1 del Story File: queries de metricas en src/lib/metrics.ts y API route"

AI implementa. Sofia revisa:
- Verifica que las queries usan los indices definidos en el SDD — correcto
- Verifica que el auth check usa `getCurrentUser()` y valida rol admin/manager — correcto
- Prueba con curl: datos correctos, performance OK

**Wave 2 — Componentes UI** (~20 min AI + 10 min Sofia review)

Sofia: "Implementa Wave 2: MetricsCards, TrendChart, DateFilter"

AI implementa. Sofia revisa:
- Verifica que TrendChart usa la libreria de charts existente (recharts) — correcto, no invento otra
- Verifica loading skeletons — presentes en todos los componentes
- **Ajuste**: "El DateFilter deberia tener 'Ultima semana' como default, no 'Ultimo mes'"

**Wave 3 — Dashboard page + auto-refresh** (~10 min AI + 5 min Sofia review)

Sofia: "Implementa Wave 3: pagina del dashboard con React Query y auto-refresh cada 5 min"

AI implementa. Sofia revisa:
- Verifica `refetchInterval: 300000` en React Query — correcto
- Verifica que no hace polling manual — cumple REQUIRED del constraint de Carlos

**Wave 4 — Integracion nav** (~5 min AI + 2 min Sofia review)

Sofia: "Implementa Wave 4: link al dashboard en el nav"

AI modifica `layout.tsx`. Sofia verifica: link visible solo para admin/manager.

Verificacion:
```bash
npm run typecheck  # ✓
npm run lint       # ✓
npm run test       # ✓ 18/18
npm run build      # ✓
```

#### Mateo + AI: HU-002 Notificaciones (Dia 1 tarde - Dia 2)

En paralelo, Mateo trabaja en su branch:
```bash
git checkout main && git pull
git checkout -b feat/002-notifications
```

**Wave 1 — Servicio de email + templates** (~15 min AI + 10 min Mateo review)

Mateo dice:
> "Implementa Wave 1: notification-service.ts con queue + retry + dead-letter, y template de email"

AI implementa. Mateo revisa:
- Verifica retry logic: 3 intentos con backoff exponencial — correcto
- Verifica dead-letter queue despues de 3 fallos — implementado como log con status 'failed'
- Verifica template: incluye numero envio, estado anterior/nuevo, fecha — completo
- **Ajuste**: "El template necesita el logo de la empresa en el header"

**Wave 2 — API + preferencias** (~15 min AI + 10 min Mateo review)

Mateo: "Implementa Wave 2: API routes de notificaciones y preferencias del usuario"

AI implementa. Mateo revisa:
- Verifica rate limit de 10 emails por envio — implementado con counter en NotificationLog
- Verifica toggle de preferencias — ON/OFF por tipo de notificacion
- Verifica log auditable — cada envio se registra con timestamp, status, recipiente

**Wave 3 — Trigger + integracion** (~10 min AI + 5 min Mateo review)

Mateo: "Implementa Wave 3: trigger de notificacion cuando cambia estado de envio"

AI modifica `src/app/api/shipments/[id]/route.ts`. Mateo revisa:
- Verifica que el trigger es async (no bloquea la respuesta de la API de shipments) — correcto
- Verifica que chequea preferencias antes de enviar — correcto

Verificacion:
```bash
npm run typecheck  # ✓
npm run lint       # ✓
npm run test       # ✓ 15/15
npm run build      # ✓
```

---

### Dia 2 — Daily Standup (10 min, async en Slack #sprint-004)

Valeria facilita:

> **Sofia**: HU-001 Dashboard — F3 completa, waves 1-4 done, corriendo AR ahora. PR hoy.
> **Mateo**: HU-002 Notificaciones — F3 completa, push final listo. PR hoy.
> **Carlos**: Voy a revisar ambos SDDs una vez mas antes de los PRs. Sin bloqueos.
> **Ana**: Nada de mi lado. Esperando PRs para review funcional.
> **Valeria**: Todo on-track. Si ambos PRs llegan hoy, puedo hacer F4 manana y arrancar HU-003.

---

### Dia 2 — AR + CR + PRs

#### HU-001: AR + CR (AI, 10 min)

```
ADVERSARIAL REVIEW — HU-001 Dashboard
- INFORMATIVO: Considerar memoizacion en TrendChart para datasets grandes
- INFORMATIVO: DateFilter no tiene aria-labels para accesibilidad
- 0 BLOQUEANTEs

CODE REVIEW — HU-001
- 8/8 archivos revisados ✓
- Imports validos, patrones consistentes, tipos correctos
- APROBADO
```

#### HU-002: AR + CR (AI, 10 min)

```
ADVERSARIAL REVIEW — HU-002 Notificaciones
- BLOQUEANTE: notification-service.ts no maneja el caso donde el email del cliente es null/invalido
- INFORMATIVO: Template de email no tiene version plain-text (spam filters)
- 1 BLOQUEANTE, 1 INFORMATIVO

CODE REVIEW — HU-002
- 7/7 archivos revisados
- BLOQUEADO hasta resolver hallazgo de AR
```

**Mateo corrige el BLOQUEANTE**:

Mateo dice:
> "Agrega validacion de email: si es null o invalido, loguear como 'skipped' en NotificationLog y no intentar enviar"

AI implementa la validacion. Mateo revisa. AR re-ejecuta:

```
AR RE-RUN — HU-002
- INFORMATIVO: Template sin plain-text (no bloqueante)
- 0 BLOQUEANTEs
- APROBADO
```

#### PRs abiertos

**Sofia** abre PR #12 — HU-001 Dashboard
**Mateo** abre PR #13 — HU-002 Notificaciones

Ambos hacen rebase contra main antes:
```bash
git fetch origin main && git rebase origin/main && git push -u origin feat/NNN-titulo
```

---

### Dia 2-3 — Peer Review Cruzado + TL Review

> **Aqui esta la diferencia fundamental del equipo de 5: peer review humano real.**

#### PR #12 (Dashboard) — Mateo revisa, Carlos aprueba

**Mateo** (peer review):
- Lee el diff (~350 lineas)
- Verifica: queries eficientes, componentes bien separados, loading states
- Comenta: "En MetricsCards.tsx linea 45, el calculo de % cambio puede dar division por zero si el periodo anterior tiene 0 envios"
- Status: **Request changes**

Sofia corrige: agrega guard `previousCount === 0 ? 'N/A' : ...`. Push.

**Mateo** re-revisa: "Fix correcto. Approved."

**Carlos** (TL final review):
- Verifica AR clean, CI green, peer review approved
- Revisa arquitectura general: patron consistente, no hay drift
- **Approved + Merge** (squash)

#### PR #13 (Notificaciones) — Sofia revisa, Carlos aprueba

**Sofia** (peer review):
- Lee el diff (~280 lineas)
- Verifica: retry logic, dead-letter, rate limit, trigger async
- Comenta: "Buen trabajo con el backoff exponencial. Una pregunta: el dead-letter log tiene indice para busqueda rapida?"
- Mateo responde: "Si, hay indice en (status, createdAt)."
- Status: **Approved**

**Carlos** (TL final review):
- Verifica AR clean (post-fix), CI green, peer review approved
- Nota que Mateo corrigio un BLOQUEANTE de AR — bien resuelto
- **Approved + Merge** (squash)

**Orden de merge** (Carlos decide):
1. Primero PR #12 (Dashboard) — incluye migration de indice en schema
2. Mateo hace rebase de PR #13 contra main actualizado
3. Segundo PR #13 (Notificaciones) — migration de modelos nuevos
4. Zero conflictos gracias al scope disjunto definido en planning

---

### Dia 3 — F4: QA Validation (Valeria)

> **Valeria es QA Lead independiente** — no implemento ni reviso codigo. Su unica funcion es validar con evidencia.

#### HU-001 Validation

```markdown
# Validation Report — HU-001 Dashboard

## Drift Detection
| Planificado (SDD) | Implementado | Match? |
|-------------------|-------------|--------|
| src/app/dashboard/page.tsx | ✓ creado | ✓ |
| src/app/dashboard/components/MetricsCards.tsx | ✓ creado | ✓ |
| src/app/dashboard/components/TrendChart.tsx | ✓ creado | ✓ |
| src/app/dashboard/components/DateFilter.tsx | ✓ creado | ✓ |
| src/app/api/metrics/route.ts | ✓ creado | ✓ |
| src/lib/metrics.ts | ✓ creado | ✓ |
| src/app/layout.tsx (mod) | ✓ modificado | ✓ |
| prisma/schema.prisma (mod) | ✓ modificado | ✓ |
| Archivos fuera de scope | Ninguno | ✓ |
Drift rate: 0%

## AC Verification
| AC | Evidencia | Status |
|----|-----------|--------|
| AC1: Metricas total/transito/entregados/demorados | MetricsCards.tsx:15-48 | ✓ PASS |
| AC2: Filtro por rango de fechas | DateFilter.tsx:8-32 | ✓ PASS |
| AC3: Graficos de tendencia | TrendChart.tsx:12-67 | ✓ PASS |
| AC4: KPIs con comparativa | MetricsCards.tsx:52-68 | ✓ PASS |
| AC5: Solo admin/manager | api/metrics/route.ts:8 | ✓ PASS |
| AC6: Loading skeleton | page.tsx:24 (Suspense) | ✓ PASS |
| AC7: Auto-refresh 5 min | page.tsx:18 refetchInterval | ✓ PASS |

## Quality Gates: ✓ typecheck ✓ lint ✓ tests ✓ build
## Resultado: APROBADO — 7/7 ACs, 0% drift
```

#### HU-002 Validation

```markdown
# Validation Report — HU-002 Notificaciones

## Drift Detection
Drift rate: 0% (7/7 archivos match)

## AC Verification
| AC | Evidencia | Status |
|----|-----------|--------|
| AC1: Email al cambiar estado | shipments/[id]/route.ts:45 trigger | ✓ PASS |
| AC2: Template con datos | templates/shipment-status.tsx:12-38 | ✓ PASS |
| AC3: Cola con retry | notification-service.ts:23-56 | ✓ PASS |
| AC4: Preferencias on/off | preferences/route.ts:8-24 | ✓ PASS |
| AC5: Log auditable | notification-service.ts:62-78 | ✓ PASS |
| AC6: Rate limit 10/envio | notification-service.ts:15-20 | ✓ PASS |

## Nota: BLOQUEANTE de AR corregido pre-merge (validacion email null)
## Quality Gates: ✓ typecheck ✓ lint ✓ tests ✓ build
## Resultado: APROBADO — 6/6 ACs, 0% drift
```

Valeria confirma ambas:
> "HU-001 y HU-002 validadas. Evidencia archivo:linea en todos los ACs. Cero drift. Ambas DONE."

---

### Dia 3 PM — FAST mid-sprint: Bug urgente

Martin, un usuario, reporta: "El boton de 'Crear Envio' no funciona en mobile."

Ana dice:
> "Esto es urgente — los operadores usan tablets en el deposito."

**Triage**: FAST (bug en UI, 1-2 archivos, sin DB)

Pipeline FAST (15 min):
1. AI investiga: el boton tiene `onClick` que depende de hover state — no funciona en touch
2. Ana: HU_APPROVED ("Es ese bug exactamente")
3. AI implementa: cambia hover trigger a click trigger + agrega touch event
4. Sofia (disponible, ya termino HU-001) toma el fix
5. Sofia revisa output del AI — correcto
6. AR: 0 BLOQUEANTEs
7. PR #14 abierto — Mateo peer review ("fix limpio, approved"), Carlos merge
8. DONE en 15 min

> **En equipo de 5**: el fix FAST no interrumpe a Mateo (que esta arrancando HU-003).
> Sofia lo toma porque esta libre. **Zero impacto en el sprint.**

---

### Dia 3-4 — HU-003: Export PDF (Mateo, post-merge de HU-001)

Ahora que HU-001 esta mergeada, Mateo puede usar las queries reales de metricas:

```
Pipeline normal QUALITY:
F0 → F1 → Ana: HU_APPROVED → F2 → Carlos: SPEC_APPROVED → F2.5 → F3 → AR → CR → PR

Particularidad: Integration Contract
- El SDD de HU-003 referencia src/lib/metrics.ts de HU-001 como exemplar
- No hay mock — usa las queries reales que Sofia ya implemento
- El AI lee el codigo REAL de metrics.ts (Codebase Grounding post-merge)
```

Mateo + AI implementan. Sofia hace peer review. Carlos aprueba. Valeria valida.

---

### Dia 5 — Sprint Closure

#### Sprint Status Meeting (Valeria facilita, 15 min)

```markdown
## Sprint 4 — Status Final

| HU | Owner | Status | PR | Merged |
|----|-------|--------|-----|--------|
| 001 — Dashboard | Sofia | DONE | #12 | ✓ |
| 002 — Notificaciones | Mateo | DONE | #13 | ✓ |
| FAST — Fix mobile | Sofia | DONE | #14 | ✓ |
| 003 — Export PDF | Mateo | DONE | #15 | ✓ |

Commitment: 3 HUs QUALITY → 3 entregadas + 1 FAST bonus
Carry-over: 0%
BLOQUEANTEs en AR: 1 (HU-002, resuelto pre-merge)
Drift rate promedio: 0%
```

Ana y Carlos:
> REVIEW_APPROVED

#### Retrospectiva (Valeria facilita, 20 min)

| Que funciono | Que mejorar | Action item |
|-------------|-------------|-------------|
| Scope disjunto — zero conflictos de merge | BLOQUEANTE de email null — el AR lo detecto, bien, pero deberia estar en el Story File como constraint | Carlos: agregar constraint "REQUIRED: validar inputs null" como regla global |
| Peer review cruazado Sofia<->Mateo encontro bug de division por zero | Daily async funciona, pero a veces nadie lee hasta tarde | Valeria: daily a las 10 AM con notificacion |
| HU-003 reutilizo codigo de HU-001 limpiamente | HU-003 empezo tarde por dependency — podria haber empezado con mock | Carlos: para Sprint 5, usar Integration Contract + mock desde dia 1 |

Valeria:
> RETRO_APPROVED

---

### Resumen del Caso 4 — Equipo de 5

#### Timeline del Sprint

| Dia | HU-001 (Sofia) | HU-002 (Mateo) | HU-003 (Mateo) | Otros |
|-----|----------------|-----------------|-----------------|-------|
| 1 | F0→F2.5 | F0→F2.5 | — | Sprint Planning |
| 2 | F3 (AI impl) | F3 (AI impl) | — | Daily |
| 2-3 | AR→CR→PR→Merge | AR→CR→PR→Merge | — | FAST fix (Sofia) |
| 3 | F4 (Valeria) ✓ | F4 (Valeria) ✓ | F0→F2.5 | — |
| 3-4 | — | — | F3→AR→CR→PR→Merge | — |
| 5 | — | — | F4 (Valeria) ✓ | Status + Retro |

#### Tiempo humano por persona

| Persona | Tiempo total en sprint | Actividades principales |
|---------|----------------------|------------------------|
| **Ana** (PO) | ~1.5 horas | Planning (45) + 3x HU_APPROVED (15) + FAST approval (2) + PR reviews funcionales (15) + Status (10) |
| **Carlos** (TL) | ~3 horas | Planning (45) + 3x SPEC_APPROVED (30) + 4x PR final review (40) + merges + conflict check + Retro |
| **Sofia** (Dev) | ~3 horas | F3 supervision HU-001 (45) + FAST fix (10) + peer review HU-002 (20) + peer review HU-003 (20) + dailies |
| **Mateo** (Dev) | ~4 horas | F3 supervision HU-002 (45) + F3 supervision HU-003 (45) + peer review HU-001 (20) + dailies |
| **Valeria** (QA+SM) | ~3 horas | Facilitar ceremonias (90) + 3x F4 validation (45) + FAST validation (5) |
| **AI** | ~6 horas | 3x pipeline completo (F0-DONE) + 1 FAST + toda la implementacion |

#### Valor del equipo de 5

| Beneficio | Detalle |
|-----------|---------|
| **Paralelismo real** | 2 HUs avanzan simultaneamente — el sprint entrega 3x mas que equipo de 2 |
| **Peer review humano** | Sofia y Mateo se revisan mutuamente — deteccion de bugs que el AI no encontro (division por zero) |
| **QA independiente** | Valeria valida sin sesgo — nunca toco el codigo que valida |
| **Separation of concerns total** | Ana (que), Carlos (como), Sofia/Mateo (ejecutan con AI), Valeria (valida + facilita) |
| **Resiliencia** | Si Sofia se enferma, Mateo puede tomar su HU. FAST fix no interrumpe a nadie. |
| **El AI escala** | Mismos 9 agentes, pero ahora corren 2-3 pipelines en paralelo sin costo humano adicional |

#### Que NO cambia vs equipos mas chicos

| Aspecto | Igual en todos los tamanos |
|---------|--------------------------|
| Pipeline por HU | F0 → F1 → HU_APPROVED → F2 → SPEC_APPROVED → F2.5 → F3 → AR → CR → F4 → DONE |
| AI implementa | El AI escribe el codigo. Los devs supervisan y ajustan. Siempre. |
| Anti-alucinacion | Exemplar Pattern, Codebase Grounding, Constraints — no cambia |
| Gates son humanos | AI nunca auto-aprueba. PO, TL, QA son personas. |
| Artefactos | work-item + sdd + story-file + validation + report por HU |

---

### Cuando el equipo de 5 necesita escalar

| Senal | Accion |
|-------|--------|
| >5 HUs QUALITY por sprint | Agregar Dev 3 |
| Valeria no llega a facilitar + QA | Separar SM y QA Lead |
| Carlos es bottleneck en SPEC_APPROVED | Senior Dev como backup approver |
| >8 personas | Dividir en 2 equipos con cross_team_protocol.md |
| Dominio muy amplio | Equipos por dominio (Team Envios, Team Facturacion) |
