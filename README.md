# NexusAgil

**Metodologia unificada WasiAI para desarrollo de software con IA anti-alucinacion.**

NexusAgil fusiona dos enfoques complementarios en un solo skill para Claude Code:

- **Nexus SDD** — Codebase Grounding, Exemplar Pattern, Waves, Drift Detection, Auto-Blindaje
- **Agile Agent Roles** — Roles especializados, Adversarial Review, Story Files, Sprint Cadence

El resultado: un pipeline que transforma Historias de Usuario en software funcional, forzando al AI a leer codigo real antes de generar y verificando que lo implementado coincide con lo planificado.

---

## Por que NexusAgil

Los AI coding assistants tienden a **alucinar**: inventan imports que no existen, crean patrones diferentes a los del proyecto, asumen APIs que no estan disponibles. NexusAgil ataca este problema con una capa de anti-alucinacion:

| Problema | Solucion NexusAgil |
|----------|-------------------|
| AI inventa imports/modulos | **Codebase Grounding**: leer archivos reales antes de generar |
| AI crea patrones inconsistentes | **Exemplar Pattern**: referenciar archivos existentes como patron |
| AI ignora restricciones del proyecto | **Constraint Directives**: OBLIGATORIO/PROHIBIDO explicitos |
| Implementacion se desvio del plan | **Drift Detection**: comparacion plan vs implementacion |
| Errores se repiten | **Auto-Blindaje**: documentar errores al momento para que no recurran |
| Implementacion sin estructura | **Waves**: W0 serial, W1+ paralelo con re-mapeo entre waves |

---

## Caracteristicas principales

### Pipeline con Gates Humanos

```
HU (cualquier formato)
    |
    v
[ F0: Contexto ] -------- Analyst+Architect: project-context + codebase grounding
    |
    v
[ F1: Discovery ] ------- Analyst+Architect+UX: Work Item + ACs EARS + scope
    |
    v
[ GATE 1 ] -------------- Humano aprueba Work Item
    |
    v
[ F2: Spec/SDD ] -------- Architect+Adversary: Context Map + SDD + Constraints
    |
    v
[ Readiness Check ] ----- Architect verifica: SDD listo para implementar?
    |
    v
[ GATE 2 ] -------------- Humano aprueba SDD
    |
    v
[ F2.5: Story File ] ---- Architect genera contrato autocontenido para Dev
    |
    v
[ F3: Implementacion ] -- Dev SOLO desde Story File, waves, anti-hallucination
    |
    v
[ Adversarial Review ] -- Adversary ataca la solucion (BLOQUEANTE/MENOR/OK)
    |
    v
[ Code Review ] --------- Adversary+QA: calidad de codigo
    |
    v
[ F4: QA/Validacion ] --- QA: drift detection + ACs con evidencia + quality gates
    |
    v
[ DONE ] ---------------- Docs documenta + actualiza _INDEX.md
```

### 9 Roles Especializados

| Rol | Responsabilidad | Fases |
|-----|----------------|-------|
| **Analyst** | Extrae requisitos, normaliza HU, define ACs EARS | F0, F1 |
| **Architect** | Codebase Grounding, SDD, Story File, Code Review | F0, F1, F2, F2.5, CR |
| **UX** | Microcopy, flujos de usuario, accesibilidad | F1 |
| **Adversary** | Adversarial Review, Code Review, seguridad | AR, CR |
| **Dev** | Implementa SOLO desde Story File, waves, test-first | F3 |
| **SM** | Sprint ceremonies (Planning, Status, Retro) | Cadencia |
| **QA** | Validacion de ACs, drift detection, quality gates | F4 |
| **Triage** | Quick Flow — pipeline abreviado para cambios triviales | Quick Flow |
| **Docs** | Documenta artefactos, actualiza _INDEX.md | DONE |

Los roles no son subagentes independientes. Son **instrucciones que Claude asume** segun la fase — como un actor que cambia de personaje. Quien especifica (Architect) no implementa (Dev). Quien implementa (Dev) no valida (QA).

### Capa Anti-Alucinacion

**Codebase Grounding** — Antes de generar cualquier cosa, el AI debe:
1. Leer archivos reales del proyecto (2-3 minimo)
2. Extraer patrones (imports, naming, estructura)
3. Documentar en un Context Map
4. Referenciar archivos existentes como Exemplars
5. Verificar que cada Exemplar existe antes de usarlo

**Constraint Directives** — Cada SDD incluye reglas explicitas:
- OBLIGATORIO: seguir patron de `[exemplar]`, solo imports que existen
- PROHIBIDO: no agregar dependencias nuevas, no crear patrones diferentes, no modificar archivos fuera de scope

**Drift Detection** — En F4 se compara lo implementado vs lo planificado:
- Archivos creados/modificados vs esperados
- Dependencias nuevas vs aprobadas
- Archivos fuera de scope (debe ser 0)

### Stack-Agnostic

NexusAgil no asume ningun stack. Cada proyecto define su Golden Path en un archivo `project-context.md` que incluye: stack, arquitectura, comandos, reglas de codigo, guardrails, y exemplars. Se incluye un template en `references/project_context_template.md`.

### Sprint Cadence

| Dia | Ceremonia | Objetivo |
|-----|-----------|----------|
| Lunes | Sprint Planning | Priorizar backlog, seleccionar HUs |
| Miercoles | Status | Revisar progreso, desbloquear |
| Viernes | Retrospectiva | Que funciono, que no, Auto-Blindaje |

### Quick Flow

Para cambios triviales (1-2 archivos, <30 lineas, sin BD, sin logica nueva), Triage ejecuta un pipeline abreviado de 4 pasos sin SDD ni Adversarial Review.

---

## Instalacion

### En un proyecto existente con Claude Code

Copia la carpeta `.claude/skills/nexus-agil/` a tu proyecto:

```bash
git clone https://github.com/ferrosasfp/NexusAgile.git /tmp/NexusAgile
cp -r /tmp/NexusAgile/.claude/skills/nexus-agil/ tu-proyecto/.claude/skills/nexus-agil/
```

### Configurar tu proyecto

1. Copia el template de contexto:

```bash
cp tu-proyecto/.claude/skills/nexus-agil/references/project_context_template.md tu-proyecto/project-context.md
```

2. Edita `project-context.md` con el stack, arquitectura, comandos y reglas de tu proyecto.

3. Reinicia Claude Code (los skills se cargan al inicio).

---

## Uso

### Activacion

Decile a Claude cualquiera de estas frases:

- `"NexusAgil, procesa esta HU: [tu historia de usuario]"`
- `"Procesa HU: [descripcion]"`
- `"Sprint planning"`
- `"Inicia fase 0 para: [HU]"`
- `"Quick flow: [cambio trivial]"`

### Ejemplo basico

```
Tu: NexusAgil, procesa esta HU: Como usuario quiero filtrar productos por categoria
    para encontrar lo que busco mas rapido.

Claude (como Analyst): Genera Work Item #001 con ACs EARS, scope, sizing...
       Presenta para aprobacion (GATE 1).

Tu: DISCOVERY_APPROVED: yes

Claude (como Architect): Lee codebase, genera Context Map, SDD con Exemplars
       y Constraint Directives. Readiness Check. Presenta para aprobacion (GATE 2).

Tu: SPEC_APPROVED: yes

Claude (como Architect): Genera Story File autocontenido para Dev.
Claude (como Dev): Implementa por Waves siguiendo Story File.
Claude (como Adversary): Ataca la solucion en 8 categorias de seguridad.
Claude (como QA): Valida ACs con evidencia, Drift Detection, Quality Gates.
Claude (como Docs): Genera reporte final, actualiza _INDEX.md.

DONE.
```

### Artefactos generados

Cada HU procesada genera artefactos en:

```
doc/sdd/
+-- _INDEX.md                    # Registro de todas las HUs
+-- 001-filtro-categorias/
    +-- work-item.md             # F1: Work Item normalizado
    +-- sdd.md                   # F2: SDD aprobado
    +-- story-file.md            # F2.5: Contrato para Dev
    +-- validation.md            # F4: Reporte de validacion
    +-- report.md                # DONE: Reporte final
```

---

## Estructura del skill

```
.claude/skills/nexus-agil/
+-- SKILL.md                                  # Core del skill (~3,760 palabras)
+-- references/
    +-- agents_roster.md                      # 9 roles detallados
    +-- sdd_template.md                       # Templates SDD (FULL/BUGFIX/MINI) + Readiness Check
    +-- story_file_template.md                # Contrato Architect-Dev
    +-- adversarial_review_checklist.md       # 8 categorias de ataque del Adversary
    +-- validation_report_template.md         # QA: drift + ACs + quality gates
    +-- sprint_cadence.md                     # Planning/Status/Retro
    +-- quick_flow.md                         # Pipeline abreviado del Triage
    +-- project_context_template.md           # Template Golden Path per-project
```

### Que hace cada archivo

| Archivo | Contenido |
|---------|-----------|
| **SKILL.md** | Pipeline completo F0-F4, principios, 25 reglas globales, activacion |
| **agents_roster.md** | Personalidad, responsabilidades, herramientas y fases de cada rol |
| **sdd_template.md** | Templates FULL (features), BUGFIX (bugs), MINI (tech-tasks) + Implementation Readiness Check |
| **story_file_template.md** | Goal, ACs, Files, Exemplars, Constraints, Waves, Out of Scope, Escalation |
| **adversarial_review_checklist.md** | AuthZ, Inputs, Inyeccion, Secretos, Race Conditions, Data Exposure, Mock Data, BD Security |
| **validation_report_template.md** | Drift Check, AC Verification, Quality Gates, AR Summary, CR Summary, Veredicto |
| **sprint_cadence.md** | Scripts para Lunes (Planning), Miercoles (Status), Viernes (Retro) |
| **quick_flow.md** | Qualification check, pipeline de 4 pasos, regla de upgrade |
| **project_context_template.md** | Stack, arquitectura, comandos, reglas, guardrails, exemplars |

---

## Conceptos clave

### EARS — Formato de Acceptance Criteria

| Patron | Formato |
|--------|---------|
| Event-Driven | WHEN [trigger], THE [sistema] SHALL [accion] |
| State-Driven | WHILE [condicion], THE [sistema] SHALL [comportamiento] |
| Unwanted | IF [condicion no deseada], THEN THE [sistema] SHALL [respuesta] |

### Waves — Paralelizacion estructurada

| Wave | Significado |
|------|-------------|
| W0 | Serial Gate — prerequisitos que deben completarse primero |
| W1 | Primera ola paralela — tareas independientes |
| W2+ | Olas siguientes — dependen de waves anteriores |

Antes de cada Wave (excepto W0), Dev re-lee los archivos modificados en el Wave anterior para verificar que imports/exports existen realmente.

### Smart Sizing

| SDD_MODE | Cuando |
|----------|--------|
| **full** | Feature/improvement con logica |
| **bugfix** | Bug confirmado con repro steps |
| **mini** | Tech-task, refactor |
| **patch** | Trivial → Quick Flow |

### Auto-Blindaje

Cuando un error ocurre durante el pipeline, se documenta **inmediatamente** (no al final):

```markdown
### [YYYY-MM-DD]: [Titulo corto]
- **Error**: [Que fallo]
- **Fix**: [Como se arreglo]
- **Aplicar en**: [Donde mas aplica]
```

Los errores que aplican a todo el proyecto se promueven a `project-context.md`.

---

## Reglas globales (resumen)

1. 1 HU = 1 ejecucion
2. Gates bloqueantes — no avanzar sin aprobacion humana
3. Codebase Grounding obligatorio — leer antes de generar
4. Exemplar Pattern — referenciar archivos existentes
5. Constraint Directives — OBLIGATORIO/PROHIBIDO en cada SDD
6. Story File como contrato — Dev solo lee el Story File
7. Adversarial Review bloqueante — hallazgos criticos se corrigen antes de avanzar
8. Drift Detection — plan vs implementacion en F4
9. Auto-Blindaje inmediato — documentar errores cuando ocurren
10. Separacion de roles — quien especifica no implementa, quien implementa no valida

Las 25 reglas completas estan en `SKILL.md` seccion "Reglas Globales".

---

## Licencia

MIT

---

## Creditos

Metodologia WasiAI creada por Fernando Rosa.
Fusiona conceptos de Nexus SDD Workflow y practicas agiles con roles especializados.
