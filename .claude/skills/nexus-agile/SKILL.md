---
name: nexus-agile
description: >
  Metodologia stack-agnostic para procesar Historias de Usuario (HU) a traves de un pipeline
  con agentes especializados, gates estrictos, adversarial review y anti-alucinacion.
  Funciona con cualquier stack: Next.js, Rails, Django, Laravel o cualquier otro.
  Activar cuando el usuario mencione "NexusAgil", "procesa HU", "sprint planning",
  "inicia fase 0", "adversarial review", o "story file".
---

# NexusAgil

> **Unidad de trabajo**: 1 HU por ejecucion.
> **Principio**: El humano decide QUE. Los agentes ejecutan COMO.
> **Anti-alucinacion**: Leer codigo real antes de generar. Nunca inventar.
> **Stack-agnostic**: NexusAgil no asume ningun stack. F0 descubre el proyecto real y genera `project-context.md`.

---

## Principios Fundacionales

1. **Stack-Agnostic** — No asumimos tecnologias. Cada proyecto define su stack en `project-context.md` (ver `references/project_context_template.md`).
2. **1 HU = 1 ejecucion** — No mezclar historias. Una historia, un pipeline completo.
3. **Anti-Alucinacion** — Codebase Grounding obligatorio. Leer codigo real, extraer patrones reales, referenciar archivos existentes. Nunca inventar.
3b. **Project-Context First** — Antes de cualquier F0, leer `.nexus/project-context.md` (o `project-context.md`). Es la fuente de verdad del stack y las reglas. Si el código difiere del project-context, reportar drift al humano — nunca asumir que el código manda sobre el project-context.
4. **Agentes Especializados** — Cada fase tiene agentes asignados con roles claros. Los roles NO se mezclan (ver `references/agents_roster.md`).
5. **Gates Estrictos** — No se avanza sin aprobacion humana explicita en los gates.
   **Entre gates, el pipeline corre solo.** El agente NO pide permiso para pasar de F0→F1, F2→F2.5, F3→AR, AR→CR, CR→QA, QA→Docs. Solo se detiene en los gates formales. Preguntar "¿continuo?" entre fases es un error de proceso.
6. **Adversarial Review** — Despues de implementar, un agente adversario ataca la solucion antes de aprobarla.
7. **Auto-Blindaje** — Cada error refuerza el proceso. Se documenta cuando ocurre, no al final.
8. **Memoria Persistente** — Al iniciar cada sesion, cargar contexto de sesiones anteriores. Al cerrar, guardar resumen estructurado. El sistema mejora con cada HU procesada. Implementacion: cualquier sistema de memoria disponible (Engram, MEMORY.md, o equivalente).
9. **Skills Router** — Cargar solo las skills relevantes para cada HU. Maximo 2 skills de dominio adicionales a la metodologia base. Contexto limpio = respuestas mas precisas y menor riesgo de alucinacion.
10. **Orquestacion por Sub-Agentes** — En modo QUALITY, cada fase del pipeline corre en un sub-agente con contexto fresco. El orquestador NUNCA hace trabajo real — solo coordina, recibe artefactos y maneja gates. Elimina context overload en HUs complejas. Ver `references/subagent_protocol.md`.

---

## Sub-Agentes Custom y Slash Commands

NexusAgil distribuye **6 agentes custom** en `.claude/agents/` y **8 slash commands** en `.claude/commands/` para que el orquestador no tenga que armar prompts a mano y NUNCA pueda olvidar el bloque PROHIBIDO de cada fase. El rol está fijo en el archivo del agente — no se puede saltear.

### 6 Agentes Custom (`.claude/agents/`)

| Agente | Fases | Modelo | Tools | Output |
|--------|-------|--------|-------|--------|
| `nexus-analyst` | F0, F1 | opus | Read, Glob, Grep, Write, AskUserQuestion | `project-context.md`, `work-item.md` |
| `nexus-architect` | F2, F2.5, CR | opus | Read, Glob, Grep, Write, Edit, Bash | `sdd.md`, `story-file.md` |
| `nexus-dev` | F3 | opus | Read, Write, Edit, Glob, Grep, Bash | código + `auto-blindaje.md` |
| `nexus-adversary` | AR, CR | opus | Read, Glob, Grep, Bash | `ar-report.md`, `cr-report.md` |
| `nexus-qa` | F4 | sonnet | Read, Glob, Grep, Bash | `validation.md` |
| `nexus-docs` | DONE | sonnet | Read, Write, Edit, Glob, Bash | `report.md`, `_INDEX.md` |

Cada agente tiene su bloque `⛔ PROHIBIDO EN ESTA FASE` integrado en el system prompt. El orquestador no puede olvidar incluirlo porque ya está en el archivo del agente.

### 8 Slash Commands (`.claude/commands/`)

| Comando | Fase | Sub-agente que lanza | Pre-requisito |
|---------|------|---------------------|---------------|
| `/nexus-p1-f0-f1 <HU>` | F0 + F1 | `nexus-analyst` | — |
| `/nexus-p2-f2 <HU>` | F2 (SDD) | `nexus-architect` | `HU_APPROVED` |
| `/nexus-p3-f2-5 <HU>` | F2.5 (Story File) | `nexus-architect` | `SPEC_APPROVED` |
| `/nexus-p4-f3 <HU>` | F3 (impl) | `nexus-dev` | `story-file.md` existe |
| `/nexus-p5-ar <HU>` | AR | `nexus-adversary` | F3 terminado |
| `/nexus-p6-cr <HU>` | CR | `nexus-adversary` | AR APROBADO |
| `/nexus-p7-f4 <HU>` | F4 (QA) | `nexus-qa` | CR APROBADO |
| `/nexus-p8-done <HU>` | DONE | `nexus-docs` | F4 APROBADO |

> **Prefijo `pN`**: el número del paso indica el orden obligatorio. Arrancá siempre por `p1` y avanzá secuencialmente. Los gates humanos (`HU_APPROVED`, `SPEC_APPROVED`) ocurren entre `p1→p2` y `p2→p3`. Entre `p3→p8` el pipeline corre solo.

### Instalación

Los agentes y commands se instalan desde el repo a la ubicación de Claude Code del usuario:

```bash
# Global (todos los proyectos)
cp -r .claude/agents/nexus-*.md ~/.claude/agents/
cp -r .claude/commands/nexus-*.md ~/.claude/commands/

# O por proyecto (solo este repo)
# Ya están en .claude/agents/ y .claude/commands/ del repo
```

Después de instalar, los slash commands aparecen con autocomplete al escribir `/nexus-` en Claude Code.

### Por qué esto reduce el olvido del orquestador

1. **El rol está en el archivo del agente** — el orquestador solo escribe `Task(subagent_type="nexus-architect")` y el bloque PROHIBIDO viene incluido. No puede olvidarlo.
2. **Los slash commands son atajos** — `/nexus-p2-f2 WKH-29` expande a un Task tool completo. Menos fricción = más uso = menos saltos al modo "yo lo hago acá mismo".
3. **Tools restringidas por agente** — `nexus-adversary` no tiene `Edit` ni `Write` sobre `src/`, así que no puede modificar código aunque quiera.
4. **Pre-requisitos explícitos en cada command** — el slash command verifica que el gate previo esté cumplido antes de lanzar.

---

## Tabla de Gates

| Gate | Texto exacto | Contexto | Efecto |
|------|-------------|----------|--------|
| `HU_APPROVED` | `HU_APPROVED` | Despues de F1 Work Items + propuesta de paralelismo | Architect arranca F2 SDD |
| `SPEC_APPROVED` | `SPEC_APPROVED` | Despues de F2 SDD | Architect genera Story File (F2.5) |
| `LAUNCH_APPROVED` | `LAUNCH_APPROVED` | Despues de lista de HUs en modo LAUNCH | Architect genera Story Files simplificados |
| `SPRINT_APPROVED` | `SPRINT_APPROVED` | Despues de Sprint Planning | SM commitea artefactos, Architect arranca F0 |
| `REVIEW_APPROVED` | `REVIEW_APPROVED` | Despues de Status Meeting | SM commitea status, pipeline continua |
| `RETRO_APPROVED` | `RETRO_APPROVED` | Despues de Retrospectiva | SM ejecuta Checklist de Cierre, sprint CERRADO |

> **Regla universal:** Solo el texto exacto activa el gate. "si", "ok", "dale", "go", "avanza" → NO activan ningun gate.
> **Regla de flujo:** Entre gates, el pipeline avanza automaticamente. El agente nunca pregunta "¿continuo?" ni "¿arrancamos?" entre fases. Si el humano responde "si" a algo que no era un gate, es senal de que el agente pregunto innecesariamente — error de proceso.

---

## Los 3 Modos

> Al inicio de cada sesion, si no hay contexto claro, Claude pregunta:
>
> **"¿Que estas construyendo?"**
> ```
> 1. FAST    — Un cambio pequeno (fix, estilo, texto, 1-2 archivos)
> 2. LAUNCH  — Algo nuevo desde cero (MVP, prototipo, nueva app)
> 3. QUALITY — Feature para produccion (DB, auth, pagos, o usuarios reales)
> ```

### Tabla de decision rapida

| Senal | Modo |
|-------|------|
| Fix de 1-2 archivos, sin DB | FAST |
| Cambio de texto o estilo | FAST |
| MVP nuevo, primera version | LAUNCH |
| Prototipo para demo/pitch | LAUNCH |
| Feature que va a usuarios reales | QUALITY |
| Tiene pagos o auth | QUALITY siempre |
| Bug critico en produccion | QUALITY (Hotfix) |
| Equipo de 2+ personas | QUALITY siempre |
| **Duda** | **QUALITY** |

### FAST — Cambio trivial

Califica si cumple TODO: max 2 archivos, <30 lineas, sin DB, sin logica nueva, sin auth/pagos.
Si no cumple alguno → sube automaticamente a LAUNCH o QUALITY.

> **Proceso completo:** `references/quick_flow.md`

### LAUNCH — MVP / Prototipo

Para construir algo nuevo desde cero con velocidad + estructura basica.
Tiene: Codebase Grounding, Story Files, gate humano (LAUNCH_APPROVED), anti-alucinacion.
No tiene: SDD completo, AR, CR formal, QA con evidencia archivo:linea.

> **Proceso completo:** `references/launch_flow.md`

### QUALITY — Produccion

Para features que van a usuarios reales, con DB, auth, pagos, o en equipo.
Pipeline completo con todos los gates, AR, CR, y QA con evidencia.

> **Proceso completo:** `references/quality_pipeline.md`

---

## Activacion

| Trigger | Modo |
|---------|------|
| "NexusAgil" / "procesa HU" / "procesa esta HU" | QUALITY |
| "Quick flow" / "cambio trivial" / "FAST" | FAST → `references/quick_flow.md` |
| "Modo LAUNCH" / "MVP" / "prototipo" / "construye [algo]" | LAUNCH → `references/launch_flow.md` |
| "Hotfix" / "bug en produccion" / "fix urgente" | QUALITY (Hotfix) → `references/quick_flow.md` (seccion Hotfix) |
| "Sprint planning" / "status" / "retro" | Sprint Cadence → `references/sprint_cadence.md` |
| "Adversarial review" | AR → `references/adversarial_review_checklist.md` |
| "Story file" | F2.5 → `references/story_file_template.md` |
| "Clarify" / "check consistencia" | `/nexus.clarify` (ver seccion abajo) |

Si el usuario no especifica modo → Claude pregunta cual de los 3 modos.

---

## Agent Roster (resumen)

> Detalle completo en `references/agents_roster.md`.

| Agente | Rol | Fases |
|--------|-----|-------|
| **Analyst** | Business Analyst — Extrae requisitos, normaliza HU, define ACs EARS | F0, F1 |
| **Architect** | Software Architect — Codebase Grounding, SDD, Story File, Code Review | F0, F1, F2, F2.5, CR |
| **UX** | UX Designer — Microcopy, flujos de usuario, accesibilidad | F1 |
| **Adversary** | Security & Quality Adversary — AR, CR, seguridad | AR, CR |
| **Dev** | Senior Developer — Implementa SOLO desde Story File, waves, test-first | F3 |
| **SM** | Scrum Master — Sprint ceremonies (Planning, Status, Retro) | Cadencia |
| **QA** | QA Engineer — Validacion de ACs, drift detection, quality gates | F4 |
| **Triage** | Quick Flow Specialist — Triage y pipeline abreviado | Quick Flow |
| **Docs** | Documentation Specialist — Documenta artefactos, actualiza _INDEX.md | DONE |

### Regla de Separacion
- Quien **especifica** (Architect) NO implementa (Dev).
- Quien **implementa** (Dev) NO valida (QA).
- Quien **revisa adversarialmente** (Adversary) NO implemento.

---

## Pipeline Overview (modo QUALITY)

```
HU (cualquier formato)
    |
    v
[ F0: Contexto ] -------------- Analyst+Architect: project-context + codebase grounding + sizing
    |
    v
[ F1: Discovery ] ------------- Analyst+Architect+UX: Work Item + ACs EARS + scope
                               + analisis de dependencias + propuesta de paralelismo
    |
    v
[ GATE 1: HU_APPROVED ] ------- Humano escribe texto exacto HU_APPROVED
    |
    v
[ F2: Spec/SDD ] -------------- Architect+Adversary: Context Map + SDD + Constraint Directives
    |
    v
[ Readiness Check ] ----------- Architect verifica: SDD listo para implementar?
    |
    v
[ GATE 2: SPEC_APPROVED ] ----- Humano escribe texto exacto SPEC_APPROVED
    |
    v
[ F2.5: Story File ] ---------- Architect genera contrato autocontenido para Dev
    |
    v
[ F3: Implementacion ] -------- Dev SOLO desde Story File, waves, anti-hallucination
    |                              ↓ AUTOMATICO
    v
[ Adversarial Review ] -------- Adversary ataca la solucion (BLOQUEANTE/MENOR/OK)
    |                              ↓ AUTOMATICO
    v
[ Code Review ] --------------- Adversary+QA: calidad de codigo
    |                              ↓ AUTOMATICO
    v
[ F4: QA/Validacion ] --------- QA: drift detection + ACs con evidencia + quality gates
    |                              ↓ AUTOMATICO
    v
[ F5: Release Gate ] ----------- Pre-release checklist (staging, migrations, env, rollback)
    |                              ↓ GATE OPCIONAL
    v
[ GATE: RELEASE_APPROVED ] ---- TL + PO verifican staging y aprueban deploy
    |
    v
[ Build + Push ] --------------- Docs documenta + actualiza _INDEX.md
    |
    v
DONE -> Persistir en doc/sdd/NNN-titulo/
```

> **Proceso detallado de cada fase:** `references/quality_pipeline.md`

---

## Dispatcher de Fases (QUALITY)

Cuando ejecutas una HU en modo QUALITY, lee `references/quality_pipeline.md` para el proceso detallado. Tabla rapida de que leer en cada fase:

| Fase | Referencia | Que contiene |
|------|-----------|--------------|
| F0: Contexto | `references/quality_pipeline.md` | Bootstrap, Smart Sizing, Skills Router, carga de memoria |
| F1: Discovery | `references/quality_pipeline.md` | Work Item, EARS ACs, DoR, Branch, Paralelismo |
| F2: SDD | `references/quality_pipeline.md` + `references/sdd_template.md` | Context Map, SDD, Constraint Directives, Readiness Check |
| F2.5: Story File | `references/quality_pipeline.md` + `references/story_file_template.md` | Contrato autocontenido Architect→Dev |
| F3: Implementacion | `references/quality_pipeline.md` | Waves, Anti-Hallucination Protocol, Re-mapeo, Auto-Blindaje |
| AR | `references/quality_pipeline.md` + `references/adversarial_review_checklist.md` | 8 categorias de ataque, BLOQUEANTE/MENOR/OK |
| CR | `references/quality_pipeline.md` | 6 checks de calidad de codigo |
| F4: QA | `references/quality_pipeline.md` + `references/validation_report_template.md` | Drift Detection, AC Verification, Quality Gates |
| F5: Release | `references/quality_pipeline.md` | Pre-release checklist, staging verification, RELEASE_APPROVED gate |
| Case Types | `references/case_types.md` | Modificadores de pipeline: DB-MIGRATION, CONTRACT-CHANGE, INFRA-ENV, SECURITY-INCIDENT, DATA-BACKFILL |
| DONE | `references/quality_pipeline.md` | Reporte final, _INDEX.md, cierre issue tracker, resumen de sesion |

> **Memoria persistente (opcional pero recomendado):** Si el proyecto usa un sistema de memoria, ver `references/engram_protocol.md` como implementacion de referencia con Engram.
> **Orquestacion por sub-agentes (QUALITY):** Cada fase puede correr en sub-agente con contexto fresco. Ver `references/subagent_protocol.md`. Si el IDE no soporta sub-agentes, usar sesion unica con Skills Router activo.

### Skills Router — F0 adicional
Despues del Smart Sizing en F0, el Architect ejecuta el Skills Router:
- Lee las señales de la HU (dominio, archivos, keywords)
- Selecciona 1-2 skills de dominio del proyecto (maximo)
- Declara explicitamente cuales skills carga
- Ver `references/skills_router.md` para senales de deteccion y estructura

---

## Persistencia de Artefactos

```
doc/sdd/
+-- _INDEX.md                          # Registro historico de HUs procesadas
+-- NNN-titulo-corto/                  # Ej: 001-filtro-categorias/
    +-- work-item.md                   # F1: Work Item normalizado
    +-- sdd.md                         # F2: SDD aprobado
    +-- story-file.md                  # F2.5: Story File para Dev
    +-- plan.md                        # F2: Plan de waves (dentro del SDD o separado)
    +-- validation.md                  # F4: Reporte de validacion
    +-- report.md                      # DONE: Reporte final
```

### Reglas de persistencia
1. **F0**: Leer `doc/sdd/_INDEX.md` para siguiente NNN. Si no existe, crear directorio y archivo.
2. **Cada fase**: Escribir artefacto en `doc/sdd/NNN-titulo/`.
3. **_INDEX.md**: Actualizar al completar pipeline (o abortar).
4. **Inmutabilidad**: Artefactos aprobados no se modifican. Si hay cambios post-gate, crear version (`sdd-v2.md`).

### Formato _INDEX.md

```markdown
# SDD Index

| # | Fecha | HU | Tipo | Mode | Status | Branch |
|---|-------|----|------|------|--------|--------|
| 001 | YYYY-MM-DD | Titulo | feature | full | DONE | feat/001-titulo |
```

---

## Anti-Alucinacion: Codebase Grounding

> *"El AI no imagina codigo. Lee codigo real, extrae patrones reales, y genera codigo que sigue esos patrones."*

Antes de generar cualquier cosa, el agente DEBE:

1. **Leer archivos reales** del proyecto relacionados con la HU
2. **Extraer patrones** (estructura, naming, imports, exports)
3. **Documentar lo leido** en un Context Map
4. **Referenciar archivos como exemplars**
5. **Verificar que el exemplar existe** (Glob). Si no existe, buscar el reemplazo mas cercano

### Regla de Exemplar Vivo

Antes de usar cualquier archivo como exemplar:
1. Verificar que existe (`Glob` o `Read`)
2. Si **no existe**: buscar en la misma carpeta y elegir el mas similar
3. Si **la carpeta tampoco existe**: buscar por patron en el proyecto (`Grep`)
4. **Nunca referenciar un archivo que no se haya confirmado que existe**

---

## /nexus.clarify — Consistency Check

Invocable en cualquier momento: "clarify", "check consistencia", "valida artefactos".

| Check | Status |
|-------|--------|
| **AC Coverage** | Cada AC tiene al menos 1 tarea |
| **Scope Drift** | Ninguna tarea toca archivos fuera de Scope IN |
| **Traceability** | Cada archivo del plan aparece en SDD |
| **Contradictions** | No hay conflictos entre AC y reglas de negocio |
| **Markers** | No hay [NEEDS CLARIFICATION] pendientes |
| **Missing Inputs** | Missing Inputs bloqueantes resueltos |
| **Exemplars Valid** | Archivos referenciados como exemplar existen |

El clarify es informativo, no bloqueante. El humano decide.

---

## Reglas Globales

1. **1 HU = 1 ejecucion**. No mezclar HUs.
2. **Gates bloqueantes**. No avanzar sin el texto exacto del gate.
3. **Abort**: Si el humano aborta, Docs actualiza _INDEX.md con ABORTED.
4. **Auto-Blindaje**: Documentar errores cuando ocurren, no al final.
5. **Stack del proyecto**: Respetar `project-context.md`, sin excepciones. Buscar en `.nexus/project-context.md` primero. Si el código usa un stack diferente al definido → reportar drift, no continuar.
6. **Cambios minimos**: No tocar lo que no esta en scope.
7. **Max 3 preguntas** en F1 para completar DoR.
8. **Conservador**: Si hay duda, NO expandir alcance.
9. **Persistencia**: Cada fase escribe su artefacto en `doc/sdd/NNN-titulo/`.
10. **Test-first**: Para logica de negocio en F3.
11. **Uncertainty markers**: `[NEEDS CLARIFICATION]` bloquea; `[TBD]` se resuelve en F2.
12. **Waves**: Paralelizacion con W0/W1/W2+ en F3.
13. **Branch semantico**: Sugerir en F1.
14. **Codebase Grounding**: Leer codigo real antes de generar. SIEMPRE.
15. **Exemplar Pattern**: Referenciar archivos existentes como patron.
16. **Constraint Directives**: Incluir prohibiciones explicitas en SDD.
17. **Verificacion incremental**: Verificar al completar cada wave.
18. **EARS ACs**: Acceptance Criteria en formato WHEN/WHILE/IF.
19. **Drift Detection**: En F4, comparar implementacion vs plan.
20. **Smart Sizing**: Usar Quick Flow para cambios triviales, no inflar con ceremonia.
21. **Re-mapeo ligero**: Antes de Wave N, re-leer archivos tocados en Wave N-1.
22. **Separacion de roles**: Quien especifica no implementa, quien implementa no valida.
23. **Story File como contrato**: Dev SOLO lee el Story File, nada mas.
24. **Adversarial Review bloqueante**: Hallazgos BLOQUEANTE se corrigen antes de avanzar.
25. **Modelo capaz para fases criticas**: Usar el modelo mas capaz disponible para analisis, implementacion y AR.
26. **Memoria al inicio**: Cargar contexto de sesiones anteriores al iniciar. Implementacion recomendada: `references/engram_protocol.md`. Sin memoria, la sesion empieza ciega.
27. **Memoria al cierre**: Guardar resumen estructurado de la sesion al terminar (Goal / Accomplished / Files / Lessons). Sin esto, la proxima sesion empieza ciega.
28. **Auto-Blindaje → Memoria**: Cada error documentado en F3 se persiste tambien en el sistema de memoria del proyecto.
29. **Skills Router en F0**: Despues del Smart Sizing, cargar 1-2 skills de dominio relevantes. Max 2. Ver `references/skills_router.md`.
30. **Skills max 200 lineas**: Cada skill de dominio no supera 200 lineas. Si crece, dividir en 2 skills mas especificas.
31. **Orquestador sin trabajo real**: Si el orquestador empieza a generar codigo, SDDs o analisis → error de proceso. Solo coordina y maneja gates.
32. **Artefactos como canal**: Los archivos en `doc/sdd/NNN-titulo/` son el canal de comunicacion entre sub-agentes. Cada sub-agente lee el artefacto de la fase anterior, no el historial de chat.

---

## Modelo Recomendado por Fase

| Fase | Modelo | Razon |
|------|--------------------|-------|
| F0-F2 (analisis, SDD) | Opus | Razonamiento profundo |
| F2.5 (Story File) | Opus | Contrato critico |
| F3 (implementacion) | Opus | Anti-alucinacion |
| AR | Opus | Seguridad requiere el modelo mas capaz |
| CR | Opus/Sonnet | Menos critico que AR |
| F4 (QA) | Opus/Sonnet | Parcialmente mecanico |
| Quick Flow | Sonnet | Cambios triviales |
| Hotfix | Opus | Investigacion de causa raiz |
| Sprint Cadence | Sonnet | Ceremonias estructuradas |

---

## Auto-Blindaje

> *"Los errores refuerzan el proceso. Blindamos para que la falla nunca se repita."*

### Formato
```markdown
### [YYYY-MM-DD]: [Titulo corto]
- **Error**: [Que fallo]
- **Fix**: [Como se arreglo]
- **Aplicar en**: [Donde mas aplica]
```

### Donde documentar

| Alcance | Donde |
|---------|-------|
| Solo esta HU | `doc/sdd/NNN-titulo/report.md` seccion Auto-Blindaje |
| Multiples features | Archivo de reglas del proyecto |
| Todo el proyecto | `project-context.md` o equivalente |

### Cuando
- **INMEDIATAMENTE** cuando el error ocurre, no al final del pipeline.
- El reporte final (DONE) copia la tabla acumulada — no se reconstruye de memoria.

---

## Enterprise — Equipos y Organizaciones

> NexusAgile fue creado para operadores individuales. Esta seccion extiende la metodologia para equipos de 2+ personas.

### Roles Humanos y Matriz de Autoridad

En equipo, los gates son de **personas, no de bots**. Cada gate tiene un aprobador humano definido.

| Rol | Responsabilidad principal | Gates |
|-----|--------------------------|-------|
| **Product Owner** | Define QUE, prioriza backlog | `HU_APPROVED`, `SPRINT_APPROVED` |
| **Tech Lead** | Define COMO, calidad tecnica | `SPEC_APPROVED` |
| **Developer** | Implementa, revisa PRs de peers | — |
| **QA Lead** | Valida evidencia, drift detection | F4 sign-off |
| **Scrum Master** | Facilita ceremonias, remueve impedimentos | `REVIEW_APPROVED`, `RETRO_APPROVED` |

> Detalle completo, delegacion AI, escalation paths, y configuracion por tamano de equipo: `references/roles_matrix.md`

### Trabajo Concurrente

Multiples devs trabajan en paralelo sin pisarse:

- **1 owner por HU** — asignado en Sprint Planning
- **Feature branches** — `feat/NNN-titulo`, siempre PR → main
- **Branch protection** — nadie pushea directo a main
- **Rebase diario** — prevenir conflictos, no resolverlos
- **Dependency map** — HUs dependientes se secuencian, independientes van en paralelo

> Detalle completo, PR workflow, conflict resolution: `references/concurrent_work_protocol.md`

### Metricas y Dashboard

Lo que no se mide no se mejora:

| Categoria | Metricas clave |
|-----------|---------------|
| Velocidad | Lead time, throughput, carry-over rate, PR merge time |
| Calidad | BLOQUEANTE rate, drift rate, bug escape rate, re-work rate |
| Anti-alucinacion | Imports fantasma, archivos fuera de scope, exemplar miss rate |
| Eficiencia AI | Tokens/HU, costo/HU, context overflow events |

> Templates de dashboard, sprint report, alertas: `references/metrics.md`

### Onboarding

Cada rol tiene un path de lectura especifico. Un dev nuevo puede ejecutar su primera HU en <1 hora.

> Guia completa, cheat sheet, FAQ: `references/onboarding.md`

### Dispatcher Enterprise

| Necesidad | Referencia |
|-----------|-----------|
| Roles y permisos | `references/roles_matrix.md` |
| Branches, PRs, conflictos | `references/concurrent_work_protocol.md` |
| KPIs, dashboard, sprint report | `references/metrics.md` |
| Primer dia, setup, FAQ | `references/onboarding.md` |


### Governance y Protocolos de Excepcion

La realidad interrumpe los procesos. Estos protocolos definen que hacer:

| Situacion | Protocolo | Referencia |
|-----------|----------|-----------|
| PO cambia scope despues de gate | Scope Change Tiers (Trivial/Menor/Mayor) | references/governance.md |
| Dev disputa un BLOQUEANTE del AR | Dispute Resolution (Confirmar/Degradar/Descartar) | references/governance.md |
| Produccion se cae mid-sprint | Incident Protocol (P0/P1/P2) | references/governance.md |
| FAST resulta ser complejo | Escalation FAST->QUALITY | references/governance.md |
| Proyecto nuevo sin codigo | Greenfield Bootstrap | references/greenfield_bootstrap.md |
| 2+ equipos comparten dependencias | Cross-Team Protocol | references/cross_team_protocol.md |
| Componentes se comunican | Integration Contract | references/integration_contract_template.md |
