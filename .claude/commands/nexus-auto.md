---
description: NexusAgil AUTO — Autonomous pipeline for 1-N HUs. Analyst decides FAST/FAST+AR/QUALITY per HU. Clinical review at gates.
argument-hint: <HU-ID> [HU-ID ...] [--user=Fernando]
allowed-tools: Task, Read, Bash, Glob, Grep, AskUserQuestion
---

# /nexus-auto — Autonomous Multi-HU Pipeline Orchestrator

## §1 Qué es AUTO y cuándo usarlo

AUTO es el modo donde Claude actúa como **orquestador Y aprobador de gates** para 1-N HUs.
En lugar de esperar al humano en cada gate (HU_APPROVED, SPEC_APPROVED), Claude ejecuta
**clinical reviews estructurados** — checklists con criterios objetivos — y self-aprueba
si todos los criterios pasan. Si alguno falla, escala al humano con detalle.

**Cuándo usar AUTO:**
- Batch de HUs donde el humano confía en el proceso y quiere resultados end-to-end
- Sesiones donde el humano no estará disponible para aprobar gates interactivamente
- Sprint execution de HUs ya priorizadas y bien definidas

**Cuándo NO usar AUTO:**
- HUs exploratorias donde el humano necesita validar dirección en cada gate
- Primera ejecución de NexusAgil en un proyecto (corré manual primero para calibrar)
- HUs con alta ambigüedad en requisitos — mejor `/nexus-p1-f0-f1` manual

---

## §2 Argumentos e invocación

```
/nexus-auto WKH-XX                          # 1 HU
/nexus-auto WKH-XX WKH-YY WKH-ZZ           # Batch de N HUs
/nexus-auto WKH-XX --user=Fernando          # Atribución explícita
```

**Argumentos:**
- `$ARGUMENTS` — 1 o más HU-IDs separados por espacio
- `--user=NOMBRE` (opcional) — nombre del humano que delega. Default: "the user"

Parsear `$ARGUMENTS` para extraer la lista de HU-IDs y el flag `--user` si existe.

---

## §3 Pipeline selection (delegado al Analyst)

El orquestador **NO decide** qué pipeline usar. Cada HU pasa por F1 (analyst) que incluye
**Smart Sizing**. El sizing determina el pipeline:

| Sizing del Analyst | Pipeline AUTO |
|--------------------|---------------|
| FAST | FAST AUTO (§7.1) |
| FAST + categoría de riesgo | FAST+AR AUTO (§7.2) |
| QUALITY / full | QUALITY AUTO (§7.3) |

Si el analyst aborta (scope too large, ambigüedad) → escalar al humano (§6 regla #3).

---

## §4 Clinical Review Checklists

### §4.1 HU_APPROVED — Clinical Review (todos los pipelines)

Después de que el analyst entrega `work-item.md`, el orquestador lo **lee** y evalúa:

```
HU_APPROVED — [YYYY-MM-DD] by Claude (delegated by [user])
Clinical review:
- Scope: [PASS/FAIL] — N files in Scope IN, N ACs, sizing [FAST/FAST+AR/QUALITY], waves defined
- EARS format: [PASS/FAIL] — N/N ACs valid EARS (sin "debería"/"quizás"/"podría")
- Codebase grounding: [PASS/FAIL] — analyst leyó project-context.md, refs mapeadas a archivos reales
- Edge cases: [PASS/FAIL] — sin [NEEDS CLARIFICATION] bloqueantes sin resolver
- Security: [PASS/FAIL] — categorías de riesgo documentadas (obligatorio si FAST+AR/QUALITY)
- Zero regression: [PASS/FAIL] — Scope OUT explícito, sin conflictos con otras HUs del batch
- Constraint Directives: [PASS/FAIL] — ≥2 CDs presentes en el work-item
Notes: [observaciones si las hay]
```

**Decisión:**
- **Todos PASS** → self-approve, escribir el bloque de atribución en el log, continuar al siguiente paso
- **Cualquier FAIL** → `AskUserQuestion` al humano con el checklist completo y el criterio fallido resaltado

### §4.2 SPEC_APPROVED — Clinical Review (solo QUALITY)

Después de que el architect entrega `sdd.md`, el orquestador lo **lee** y evalúa:

```
SPEC_APPROVED — [YYYY-MM-DD] by Claude (delegated by [user])
Clinical review:
- Codebase grounding: [PASS/FAIL] — ≥2 archivos del codebase leídos, exemplars verificados vía Glob
- Waves: [PASS/FAIL] — W0 existe, orden lógico entre waves
- DT/CD coverage: [PASS/FAIL] — DTs documentados, CDs inherited del work-item + nuevos
- Exemplar verification: [PASS/FAIL] — paths de exemplars existen en disco (verificar con Glob)
- Readiness Check: [PASS/FAIL] — el SDD incluye su propio Readiness Check
- No blockers: [PASS/FAIL] — cero [NEEDS CLARIFICATION] sin resolver en el SDD
- Test plan: [PASS/FAIL] — ≥1 test por AC documentado en el SDD
Notes: [observaciones si las hay]
```

**Decisión:** misma lógica que §4.1 — todos PASS → self-approve, cualquier FAIL → escalar.

### §4.3 Post-AR/CR y Post-F4

Estos gates ya son automáticos en el pipeline normal (tabla de decisión en `/nexus-p5-ar`
y `/nexus-p7-f4`). No requieren clinical review adicional en AUTO mode.

### §4.4 Formato de atribución (obligatorio)

Todo self-approval se documenta en el output del orquestador con este formato exacto:

```
═══════════════════════════════════════
[GATE_NAME] — [YYYY-MM-DD] by Claude (delegated by [user])
Clinical review:
[criterios con PASS/FAIL]
Notes: [observaciones]
═══════════════════════════════════════
```

---

## §5 Batch Orchestration

### §5.1 Dependency Detection

Después de que TODOS los analysts completan F1 para cada HU del batch:

1. Leer el **Scope IN** de cada `work-item.md`
2. Para cada par de HUs: `overlap = scope_a ∩ scope_b`
3. Si overlap no vacío:
   - La HU con NNN menor va primero (criterio default)
   - O la que **crea** archivos que la otra **modifica** (criterio de precedencia)
4. Si no hay overlap → pueden correr en paralelo (sujeto a §5.3)

### §5.2 Execution Priority

```
Fase 1: Todos los F1 (analyst) en paralelo — N Task calls en 1 mensaje
Fase 2: Clinical review HU_APPROVED por cada HU + clasificar pipelines + detectar dependencias
Fase 3: Ejecutar por pipeline type en este orden:
         1. FAST HUs primero (más rápidas, desbloquean recursos antes)
         2. FAST+AR HUs
         3. QUALITY HUs (F2 → SPEC_REVIEW → F2.5 → F3 → ...)
Fase 4: HUs dependientes esperan que su blocker haga merge antes de arrancar F3
```

### §5.3 Serial vs Parallel (F3)

- **Default: serial** — un F3 a la vez sobre el mismo repo
  (Auto-Blindaje WKH-6/WKH-7: sub-agentes F3 paralelos sobre el mismo directorio
  causan commits mezclados entre branches)
- **Opt-in: worktrees** — si el repo soporta git worktrees y el humano lo pidió:
  ```bash
  git worktree add ../[repo]-[hu-id] -b feat/[hu-id]-titulo
  ```
  Cada sub-agente F3 recibe su propio `cwd`. Al terminar, limpiar worktrees.

---

## §6 Escalation Rules

El orquestador **PARA** y usa `AskUserQuestion` cuando:

| # | Condición | Acción |
|---|-----------|--------|
| 1 | Clinical review FAIL en cualquier criterio | Mostrar checklist completo con el FAIL resaltado |
| 2 | Fix-pack ≥3 iteraciones sin resolver BLQs | Reportar hallazgos persistentes, sugerir escalar a QUALITY |
| 3 | Analyst aborta (scope too large, no FAST, ambigüedad) | Reportar razón del abort, pedir reclasificación |
| 4 | `[NEEDS CLARIFICATION]` que requiere conocimiento de dominio | Presentar la pregunta del agente al humano |
| 5 | Dev necesita archivos fuera de Scope IN | Listar archivos requeridos vs Scope IN, pedir autorización |
| 6 | Dependencia circular entre HUs del batch | Mostrar el grafo circular, pedir al humano que rompa el ciclo |
| 7 | Sub-agente crashea o retorna output vacío | Reportar error, ofrecer re-lanzar o abortar |
| 8 | SDD con items irresolubles sin conocimiento de dominio humano | Listar items pendientes, pedir decisión |
| 9 | Conflicto de Scope IN entre HUs sin orden claro | Presentar overlap y opciones de ordenamiento |
| 10 | Batch completo (todas las HUs en DONE) | Presentar dashboard final (§8) para cierre |

**Regla general:** ante incertidumbre del orquestador sobre si self-aprobar o escalar → **escalar siempre**.
Es más barato preguntar al humano que aprobar algo incorrecto.

---

## §7 Flows por pipeline type

> **NOTA IMPORTANTE:** Los prompts de cada sub-agente NO se duplican aquí.
> Se referencian los prompts existentes en los slash commands correspondientes.
> Esto evita drift entre AUTO y manual.

### §7.1 FAST AUTO (4 fases)

```
Fase 1 — F1 Analyst
  Prompt: usar el de /nexus-fast-pipeline "Fase 1 — Analyst FAST"
  Sub-agente: nexus-analyst
  Modelo: sonnet

  GATE — HU_APPROVED (clinical review §4.1)
  El orquestador lee work-item.md y ejecuta clinical review.
  PASS → continuar. FAIL → escalar al humano.

Fase 2 — F3 Dev
  Prompt: usar el de /nexus-fast-pipeline "Fase 2 — Dev FAST"
  Sub-agente: nexus-dev
  Modelo: opus

Fase 3 — F4 QA
  Prompt: usar el de /nexus-fast-pipeline "Fase 3 — QA FAST"
  Sub-agente: nexus-qa
  Modelo: sonnet

Fase 4 — DONE
  Prompt: usar el de /nexus-fast-pipeline "Fase 4 — Docs FAST"
  Sub-agente: nexus-docs
  Modelo: haiku
```

**Diferencia vs manual:** el gate HU_APPROVED es clinical review en vez de pregunta al humano.

### §7.2 FAST+AR AUTO (6 fases)

```
Fase 1 — F1 Analyst
  Prompt: usar el de /nexus-fast-plus-ar "Fase 1 — Analyst FAST"
  Sub-agente: nexus-analyst
  Modelo: sonnet

  GATE — HU_APPROVED (clinical review §4.1)
  El orquestador lee work-item.md y ejecuta clinical review.
  PASS → continuar. FAIL → escalar al humano.

Fase 2 — F3 Dev
  Prompt: usar el de /nexus-fast-plus-ar "Fase 2 — Dev FAST"
  Sub-agente: nexus-dev
  Modelo: opus

Fase 3 — AR + CR paralelo
  Prompt: usar el de /nexus-fast-plus-ar "Fase 3 — AR + CR paralelo"
  Sub-agentes: nexus-adversary x2 (2 Task calls en 1 mensaje)
  Modelo: opus

  Si BLQ encontrados:
    Fase 3b — Fix-pack
    Prompt: usar el de /nexus-fast-plus-ar "Fase 4 — fix-pack"
    Sub-agente: nexus-dev
    Modelo: opus
    Loop: re-AR hasta APROBADO o 3 iteraciones (→ escalar §6 regla #2)

Fase 4 — F4 QA compact
  Prompt: usar el de /nexus-fast-plus-ar "Fase 5 — F4 compact"
  Sub-agente: nexus-qa
  Modelo: sonnet

Fase 5 — DONE
  Prompt: usar el de /nexus-fast-plus-ar "Fase 6 — DONE fast"
  Sub-agente: nexus-docs
  Modelo: haiku
```

**Diferencia vs manual:** el gate HU_APPROVED es clinical review en vez de pregunta al humano.

### §7.3 QUALITY AUTO (8 fases)

```
Fase 1 — F0+F1 Analyst
  Prompt: usar el de /nexus-p1-f0-f1
  Sub-agente: nexus-analyst
  Modelo: opus

  GATE — HU_APPROVED (clinical review §4.1)
  El orquestador lee work-item.md y ejecuta clinical review.
  PASS → continuar. FAIL → escalar al humano.

Fase 2 — F2 SDD
  Prompt: usar el de /nexus-p2-f2
  Sub-agente: nexus-architect
  Modelo: opus

  GATE — SPEC_APPROVED (clinical review §4.2)
  El orquestador lee sdd.md y ejecuta clinical review.
  PASS → continuar. FAIL → escalar al humano.

Fase 3 — F2.5 Story File
  Prompt: usar el de /nexus-p3-f2-5
  Sub-agente: nexus-architect
  Modelo: opus

Fase 4 — F3 Implementation
  Prompt: usar el de /nexus-p4-f3
  Sub-agente: nexus-dev
  Modelo: opus
  Pre-check: ejecutar el checklist de subagent_protocol.md §F3 antes de lanzar

Fase 5 — AR + CR paralelo
  Prompt: usar el de /nexus-p5-ar
  Sub-agentes: nexus-adversary x2 (2 Task calls en 1 mensaje)
  Modelo: opus

  Si BLQ encontrados:
    Fase 5b — Fix-pack (dev corrige, re-AR)
    Loop: máx 3 iteraciones (→ escalar §6 regla #2)

Fase 6 — CR (si no corrió paralelo con AR)
  Prompt: usar el de /nexus-p6-cr
  Sub-agente: nexus-adversary
  Modelo: opus

Fase 7 — F4 QA
  Prompt: usar el de /nexus-p7-f4
  Sub-agente: nexus-qa
  Modelo: sonnet

Fase 8 — DONE
  Prompt: usar el de /nexus-p8-done
  Sub-agente: nexus-docs
  Modelo: sonnet
```

**Diferencias vs manual:**
- HU_APPROVED es clinical review (§4.1) en vez de pregunta al humano
- SPEC_APPROVED es clinical review (§4.2) en vez de pregunta al humano
- El resto del pipeline (F3→DONE) ya es automático en manual — sin cambios

---

## §8 Completion Dashboard

Al terminar TODAS las HUs del batch (o al escalar en la regla #10), presentar:

```
╔══════════════════════════════════════════════════╗
║           NEXUS-AUTO — BATCH COMPLETE            ║
╠══════════════════════════════════════════════════╣
║ HU       │ Pipeline  │ Status │ Time   │ Branch ║
║──────────┼───────────┼────────┼────────┼────────║
║ WKH-XX   │ FAST      │ ✅ DONE │ 12 min │ feat/… ║
║ WKH-YY   │ FAST+AR   │ ✅ DONE │ 25 min │ feat/… ║
║ WKH-ZZ   │ QUALITY   │ ⚠️ ESC  │ 40 min │ feat/… ║
╠══════════════════════════════════════════════════╣
║ Gates self-approved: N                           ║
║ Gates escalated: N                               ║
║ Fix-pack iterations: N                           ║
║ Total wallclock: NN min                          ║
╚══════════════════════════════════════════════════╝
```

Si alguna HU fue escalada, incluir el motivo en una sección debajo del dashboard.

---

## §9 Reglas críticas

1. **El orquestador NUNCA hace trabajo real** — no lee codebase, no escribe código, no genera SDDs.
   Solo coordina sub-agentes, ejecuta clinical reviews, y maneja el batch.

2. **Los sub-agentes reciben UNA fase a la vez** — compatible con Auto-Blindaje "Gates saltados".
   AUTO mode no viola esta regla: los sub-agentes siguen recibiendo una fase. La diferencia es
   que el orquestador self-aprueba en vez de esperar al humano.

3. **Clinical review es binario** — todos PASS → self-approve. Cualquier FAIL → escalar.
   No hay "FAIL pero sigo porque parece menor". Si falla, el humano decide.

4. **Prompts no se duplican** — se referencian los de los slash commands existentes.
   Si un prompt cambia en `/nexus-fast-pipeline`, AUTO hereda el cambio automáticamente.

5. **Atribución siempre** — todo self-approval documenta quién aprobó, por delegación de quién,
   con qué criterios, y la fecha. Trazabilidad completa.

6. **Scope IN es sagrado** — si un dev necesita tocar algo fuera del Scope IN, escalar.
   AUTO no relaja las reglas de scope.

7. **Anti-Blindaje activo** — errores se documentan cuando ocurren, igual que en manual.

8. **Serial F3 por default** — no lanzar 2 devs sobre el mismo repo sin worktrees.

9. **Máximo 3 fix-pack iterations** — si AR no aprueba después de 3 rondas, escalar.

10. **Dashboard final obligatorio** — el batch no está completo sin el dashboard de §8.

---

## §10 Relación con pipelines manuales

AUTO **reutiliza** los pipelines manuales. No los reemplaza.

| Modo | Cómo se invoca | Quién aprueba gates |
|------|----------------|---------------------|
| Manual | `/nexus-fast-pipeline`, `/nexus-p1-f0-f1`, etc. | Humano (texto exacto) |
| AUTO | `/nexus-auto WKH-XX [...]` | Claude (clinical review) |

El humano siempre puede:
- Correr una HU en manual si quiere aprobar gates personalmente
- Interrumpir un AUTO en curso y tomar control manual del gate
- Rechazar un self-approval cuando el orquestador escala por FAIL

**Los 6 agents y los 10 commands existentes no cambian.** AUTO los orquesta, no los modifica.
