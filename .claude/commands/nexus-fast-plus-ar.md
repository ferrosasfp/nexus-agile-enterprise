---
description: NexusAgil FAST+AR — Pipeline intermedio para HUs chicas pero de alto riesgo (auth, DB writes, streaming, admin, RLS)
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash, AskUserQuestion
---

# /nexus-fast-plus-ar — FAST + AR (el sweet spot)

Pipeline intermedio entre `/nexus-fast-pipeline` (sin review) y el QUALITY completo (`/nexus-p1-f0-f1` → `/nexus-p8-done`). Para **HUs chicas que tocan territorio de riesgo** donde saltear AR sería irresponsable pero el overhead de SDD + Story File es desproporcionado.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

## 🎯 Cuándo usar este modo (vs FAST vs QUALITY)

### ✅ FAST+AR está diseñado para
HUs donde **pocos archivos + scope acotado** coinciden con **superficie de riesgo**:

- Nuevos Server Actions con DB writes (insert/update/delete con ownership)
- Endpoints que reciben input de usuarios externos (validación crítica)
- Cambios en lógica de auth/RBAC/middleware
- Streaming responses o refactors de tool calling
- Paneles de admin y gates de `is_admin`
- RLS policies nuevas o modificadas
- Llamadas a APIs externas con secretos
- HUs con <5 archivos + ≤10 ACs pero que tocan alguno de los anteriores

### ❌ Usá FAST puro (`/nexus-fast-pipeline`) si
- UI pura (layout, typography, theme, CSS)
- Queries read-only a tablas ya validadas
- Fix de typos, copy, strings
- Refactors mecánicos de código ya cubierto por AR previo

### ❌ Usá QUALITY completo (`/nexus-p1-f0-f1`) si
- Features grandes (>5 archivos o >10 ACs)
- Migrations destructivas o no-additive sobre tablas con data
- Funciones postgres con `SECURITY DEFINER`
- Cambios arquitectónicos (nuevas abstracciones, nuevos módulos)
- HUs con múltiples dependencias entre waves
- Cualquier cosa donde **necesitás un SDD** para pensar el problema antes de codear

**Regla de oro del FAST+AR**: "es chica pero puede explotar en prod". Si dudás, usá QUALITY.

## 📋 Estructura del FAST+AR pipeline

| Fase | Equivalente QUALITY | Agente | Modelo | Nota |
|------|---------------------|--------|--------|------|
| F1 fast | p1 (F0/F1) | nexus-analyst | sonnet | Work-item compacto, sin F0 bootstrap |
| **GATE** | HU_APPROVED | humano | — | Revisá scope y riesgo antes de codear |
| F3 fast | p4 (F3) | nexus-dev | opus | Usa el work-item como contrato (sin SDD ni Story File) |
| **AR + CR paralelo** | p5 (AR+CR) | nexus-adversary x2 | opus | **Misma lógica que `/nexus-p5-ar`** — 2 Task calls en mismo mensaje |
| fix-pack | (re-F3) | nexus-dev | opus | Si AR encontró BLQ, el dev corrige — loop hasta APROBADO |
| F4 compact | p7 (F4) | nexus-qa | sonnet | Runtime-first + report compacto (el nexus-qa ya sabe hacer ambos) |
| DONE fast | p8 (DONE) | nexus-docs | haiku | Mini-report + _INDEX.md update |
| **SKIPPED** | p2 (F2 SDD) | — | — | El work-item compacto sirve de spec |
| **SKIPPED** | p3 (F2.5 Story File) | — | — | El dev usa el work-item como contrato |

**Tiempo típico**: **17-32 min** (vs 10-14 FAST puro, vs 45-90 QUALITY completo).

**Ahorro vs QUALITY completo**: ~60-70%.
**Overhead vs FAST puro**: +5-18 min por AR+CR+fixes+F4 compact.

**Qué ganás con ese overhead extra**:
- AR caza los bugs que el dev no ve (los 3 ALTO de LUM-6, los 4 CRITs de LUM-10, los 5 BLQs de LUM-8)
- CR valida SOLID/naming/DRY sin costo extra de wallclock (corre paralelo con AR)
- F4 compact verifica runtime state (DB, env parity, migrations) — cosas que CR no puede ver
- Validation report compacto si todo verde, denso si hay hallazgos

## 🎯 Ejecución

Vos sos el orquestador. NO codeás vos mismo. Lanzás los sub-agentes con instrucciones de **modo FAST+AR**.

### Fase 1 — Analyst FAST (compact work-item)

Igual que `/nexus-fast-pipeline` pero con un check extra de riesgo:

```
Task tool:
  subagent_type: nexus-analyst
  description: F1 FAST+AR para HU [WKH-XX]
  prompt: |
    Eres nexus-analyst en MODO FAST+AR para la HU [WKH-XX].

    DIFERENCIAS vs modo FAST puro:
    - Además de generar un work-item compacto, tenés que clasificar la HU en la sección "Riesgo" con alguna de las categorías:
      * server-actions-writes (Server Actions con DB writes con ownership)
      * external-input (endpoints que reciben input de usuarios externos)
      * auth-rbac (cambios en auth/RBAC/middleware)
      * streaming-refactor (streaming responses o tool calling)
      * admin-panel (paneles admin y gates is_admin)
      * rls-policies (policies RLS nuevas o modificadas)
      * external-api (llamadas a APIs externas con secretos)
    - Si NINGUNA categoría aplica → la HU NO es FAST+AR, es FAST puro. ABORTÁ con el mensaje: "Esta HU NO necesita AR — usá /nexus-fast-pipeline".
    - Si al menos 1 categoría aplica → la HU califica. Documentá cuáles y por qué.
    - Si la HU supera >5 archivos o >10 ACs → ABORTÁ con el mensaje: "Esta HU es demasiado grande para FAST+AR — usá /nexus-p1-f0-f1 (QUALITY)".

    INPUT:
    - HU del humano: $ARGUMENTS
    - project-context.md (debe existir)
    - doc/sdd/_INDEX.md (para asignar NNN)

    OUTPUT:
    - doc/sdd/NNN-titulo/work-item.md compacto con sección "Riesgo" explicitando las categorías
    - Máximo 10 ACs en EARS
    - Scope IN exhaustivo (máx 5 archivos)
    - Reporte al orquestador: path + 3 líneas explicando qué se construye y cuál es el riesgo

    ## ⛔ PROHIBIDO en FAST+AR
    - NO generar SDD
    - NO generar Story File
    - NO ACs vagos
    - NO scope ambiguo
    - NO clasificar riesgo con categorías inventadas (usá solo las 7 listadas o ABORTÁ)
```

### GATE — HU_APPROVED (humano)

Presentar al humano el work-item. Usar `AskUserQuestion`:
- **Pregunta**: "Work-item compacto en `<path>`. Clasificado como `[categoría-riesgo]`. ¿Aprobás avanzar a F3 FAST+AR?"
- **Opciones**: APROBAR / RECHAZAR (con feedback) / ESCALAR a QUALITY completo

Si RECHAZA o ESCALA → ABORT.

### Fase 2 — Dev FAST (implementación directa)

Idéntico al `/nexus-fast-pipeline`:

```
Task tool:
  subagent_type: nexus-dev
  description: F3 FAST+AR para HU [WKH-XX]
  prompt: |
    Eres nexus-dev en MODO FAST+AR para la HU [WKH-XX].

    Tu input es el WORK-ITEM directamente (NO hay Story File). Tratalo como contrato autocontenido.

    REGLAS CRÍTICAS:
    - Anti-Hallucination Protocol sigue vigente — verificás exemplars, no inventás APIs.
    - Auto-Blindaje obligatorio si cometés errores.
    - Si el cambio requiere tocar archivos fuera del Scope IN → STOP, escalar a QUALITY.
    - NO expandas scope, NO refactors no pedidos.

    INPUT:
    - doc/sdd/NNN-titulo/work-item.md (con sección Riesgo)
    - project-context.md

    OUTPUT:
    - Código en disco según Scope IN
    - Tests pasando
    - auto-blindaje.md si hubo errores
    - Reporte al orquestador: archivos tocados + comandos corridos + status typecheck/tests

    NOTA SOBRE LA CATEGORÍA DE RIESGO: la sección "Riesgo" del work-item te dice en qué hay que prestar extra atención. Si la categoría es `server-actions-writes`, prestá atención extra a ownership checks. Si es `external-input`, a validación. Si es `streaming-refactor`, a orden de mensajes y persistencia. Esto NO te pide implementar de forma distinta — te pide ser extra cuidadoso con el estándar del proyecto en esas áreas.
```

### Fase 3 — AR + CR paralelo (core del modo FAST+AR)

**Esto es lo único que distingue este pipeline del FAST puro.** Se lanzan AR y CR en paralelo (2 Task calls en **EL MISMO mensaje**, igual que `/nexus-p5-ar`):

```
Task #1 (AR):
  subagent_type: nexus-adversary
  description: AR FAST+AR para HU [WKH-XX]
  prompt: |
    Eres nexus-adversary ejecutando AR para la HU [WKH-XX] en modo FAST+AR.

    NOTA: NO hay Story File. Tu contrato es el work-item.md.

    INPUT:
    - doc/sdd/NNN-titulo/work-item.md (con sección Riesgo que te dice dónde prestar más atención)
    - doc/sdd/NNN-titulo/auto-blindaje.md (si existe)
    - Archivos modificados: `git diff --name-only main...HEAD`
    - references/adversarial_review_checklist.md del skill nexus-agile

    TU TAREA:
    Atacar la implementación en las 8 categorías estándar (Security, Error Handling, Data Integrity, Performance, Integration, Type Safety, Test Coverage, Scope Drift).

    PRIORIDAD: las categorías del work-item marcadas como riesgo son las que MÁS tenés que atacar. Si el work-item dice "server-actions-writes", la categoría Security + Data Integrity son críticas. No dejes nada sin revisar ahí.

    OUTPUT:
    - doc/sdd/NNN-titulo/ar-report.md con findings en severidad BLQ-ALTO / BLQ-MED / BLQ-BAJO / MENOR / OK
    - Veredicto final

Task #2 (CR — paralelo):
  subagent_type: nexus-adversary
  description: CR FAST+AR para HU [WKH-XX]
  prompt: |
    Eres nexus-adversary ejecutando CR para la HU [WKH-XX] en modo FAST+AR.

    Corres EN PARALELO con AR — no podés leer ar-report.md.

    INPUT:
    - doc/sdd/NNN-titulo/work-item.md
    - Archivos modificados: `git diff main...HEAD`

    TU TAREA:
    6 checks: naming, complejidad, DRY, SOLID (S/O/L/I/D), tests, docs inline. Clasificar en BLQ-ALTO / BLQ-MED / BLQ-BAJO / MENOR / OK.

    OUTPUT: doc/sdd/NNN-titulo/cr-report.md
```

### Fase 4 — fix-pack (si hay BLQ)

Si AR o CR reportan **cualquier BLQ** (ALTO, MED o BAJO):

```
Task tool:
  subagent_type: nexus-dev
  description: Fix-pack FAST+AR para HU [WKH-XX]
  prompt: |
    Aplicá los fixes de AR + CR combinados. Priorizá BLQ-ALTO primero, luego MED, luego BAJO. Los MENORs quedan como deuda documentada, NO los fixes.

    INPUT: ar-report.md + cr-report.md + código actual

    REGLA: NO expandas scope. Si un fix requiere tocar algo fuera de Scope IN → escalá.
```

Si AR vuelve APROBADO en la segunda pasada → seguí a F4 compact. Si encuentra BLQs nuevos → nuevo fix-pack (máx 3 iteraciones, después escalar a QUALITY completo).

### Fase 5 — F4 compact (runtime-first, leer gates del CR)

```
Task tool:
  subagent_type: nexus-qa
  description: F4 FAST+AR para HU [WKH-XX]
  prompt: |
    Eres nexus-qa en modo COMPACT para HU [WKH-XX].

    El agente nexus-qa ya sabe hacer runtime-first y validation report compacto. Seguí su prompt estándar, con estas instrucciones específicas para FAST+AR:

    1. Runtime checks (DB state, env parity, migration apply) — SI la categoría de riesgo del work-item los justifica. Si es `server-actions-writes` con migration → SÍ. Si es `auth-rbac` sin migration → verificá env vars pero no DB schema.
    2. AC verification con evidencia (tests o manual) para los máx 10 ACs del work-item.
    3. Drift detection rápido.
    4. Gate confirmation leyendo el output de AR/CR — NO re-ejecutar lint/tsc/vitest/build.

    OUTPUT: validation.md en modo COMPACTO si todo verde, DENSO si hay findings.
```

### Fase 6 — DONE fast

Idéntico a `/nexus-fast-pipeline` Fase 4: mini-report + `_INDEX.md` update.

## 🛡️ Reglas críticas del FAST+AR

1. **AR + CR son obligatorios** — ese es el `+AR` en el nombre del modo. Si saltás AR, usá FAST puro.
2. **Gate binario en AR/CR**: cualquier BLQ (ALTO, MED, o BAJO) dispara fix-pack.
3. **Máximo 3 iteraciones de fix-pack** — si al tercer intento AR sigue encontrando BLQs → algo estructural está mal → escalar a QUALITY completo y empezar de nuevo con SDD.
4. **Scope IN es contrato estricto**: si el dev necesita tocar algo fuera del Scope IN del work-item → STOP, escalar.
5. **Auto-Blindaje sigue activo**: errores documentados igual.
6. **Runtime checks del F4 son condicionales** — solo ejecutá los que la categoría de riesgo justifica, no el combo completo.

## 🔄 Relación con los otros pipelines

FAST, FAST+AR y QUALITY **coexisten**. El analyst puede recomendar cuál usar, pero el humano decide.

| Pipeline | Comando | Tiempo típico | Cuándo |
|----------|---------|---------------|--------|
| **FAST** | `/nexus-fast-pipeline` | 10-14 min | HU chica + bajo riesgo (UI, typography, reads) |
| **FAST+AR** ⭐ | `/nexus-fast-plus-ar` | 17-32 min | HU chica + alto riesgo (writes, auth, streaming) |
| **QUALITY** | `/nexus-p1-f0-f1` → ... → `/nexus-p8-done` | 45-120 min | HU grande o complejidad arquitectónica |

FAST+AR es **opt-in explícito** — nunca se invoca por accidente. Pero es el sweet spot para el 40-50% de las HUs de producto real: no son triviales ni son features arquitectónicas, son "toquecitos" que igual pueden romper prod.

## 📊 Ejemplo histórico — cuándo habría importado

| HU | Qué pasó con FAST puro (hipotético) | Qué pasaría con FAST+AR |
|----|-------------------------------------|-------------------------|
| LUM-50 sidebar (Server Actions con ownership) | Sin test de ownership, race condition en rename/delete | AR habría flagged ownership check ausente como BLQ-ALTO |
| LUM-58 tags (writes + filter) | Sin per-user filter, leaking de tags entre usuarios | AR habría flagged Security + Data Integrity |
| LUM-6 Content Library | 3 ALTO: tests sin user_id filter, XSS markdown, typed client — los CACHÓ el AR en la corrida real | FAST+AR habría hecho lo mismo con menos overhead (no SDD, no Story) |

El patrón: **las HUs chicas pero sensibles son exactamente donde AR tiene el mayor ROI porque el overhead del QUALITY completo no se justifica**.
