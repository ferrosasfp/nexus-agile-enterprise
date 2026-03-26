# NexusAgile Enterprise — Casos de Uso

> Escenarios reales simulados para cada configuracion de equipo y modo.
> Cada caso muestra el flujo completo: que hace el humano, que hace el AI, donde estan los gates.

---

## Indice

| # | Escenario | Team | Modo | Pagina |
|---|-----------|------|------|--------|
| 1 | [Solo dev — Feature de pagos](#caso-1-solo-dev--feature-quality) | 1 persona | QUALITY | Este doc |
| 2 | [Solo dev — Fix trivial](#caso-2-solo-dev--fix-trivial-fast) | 1 persona | FAST | Este doc |
| 3 | Solo dev — MVP desde cero | 1 persona | LAUNCH | Pendiente |
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
