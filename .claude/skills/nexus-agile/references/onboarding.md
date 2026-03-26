# Onboarding — Guia de Inicio Rapido

> **Objetivo**: Que cualquier miembro nuevo del equipo pueda ejecutar su primera HU en menos de 1 hora.
> Lee solo la seccion de tu rol. No necesitas leer todo el documento.

---

## Que es NexusAgile en 30 segundos

NexusAgile es una metodologia de desarrollo donde **agentes AI ejecutan el pipeline** (analisis, SDD, implementacion, review, QA) y **los humanos toman decisiones en gates**. Vos decidis QUE. Los agentes deciden COMO.

Tu describes una feature -> AI analiza, disena, implementa, ataca, valida -> Vos aprobas en 2-3 puntos de control (gates) -> Feature lista con spec, review de seguridad, y evidencia de QA.

---

## Empeza Aca — Segun Tu Rol

### Si sos Product Owner

**Lee esto** (15 min):
1. Este documento — seccion PO abajo
2. references/sprint_cadence.md — como funcionan las ceremonias
3. references/roles_matrix.md — seccion "Product Owner" + "Matriz de Gates"

**No necesitas leer**: SDD template, story file template, adversarial review (eso es tecnico).

**Tu primer sprint**: Vas a Sprint Planning con HUs escritas en lenguaje natural. NexusAgile las normaliza. Vos aprobas con HU_APPROVED.

---

### Si sos Tech Lead

**Lee esto** (30 min):
1. Este documento completo
2. references/roles_matrix.md — todo el documento
3. references/quality_pipeline.md — flujo completo
4. references/concurrent_work_protocol.md — branch strategy y PR workflow
5. references/sdd_template.md — para saber que esperar del SDD
6. references/metrics.md — KPIs que vas a monitorear

**Tu responsabilidad principal**: Aprobar SPEC_APPROVED, asignar reviewers, definir branch strategy, resolver conflictos tecnicos.

---

### Si sos Developer

**Lee esto** (20 min):
1. Este documento — seccion Dev abajo
2. references/story_file_template.md — esto es lo UNICO que vas a leer para implementar
3. references/concurrent_work_protocol.md — seccion "Branch Strategy" y "PR Workflow"
4. references/roles_matrix.md — seccion "Developer"

**No necesitas leer**: Quality pipeline completo, SDD template, Sprint cadence (el SM facilita).

**Tu primer HU**: Recibes un Story File. Seguis las waves. Abris un PR. Listo.

---

### Si sos QA Lead

**Lee esto** (20 min):
1. Este documento — seccion QA abajo
2. references/validation_report_template.md — template de tu entregable principal
3. references/adversarial_review_checklist.md — que revisa el AR antes que vos
4. references/metrics.md — metricas de calidad
5. references/roles_matrix.md — seccion "QA Lead"

---

### Si sos Scrum Master

**Lee esto** (20 min):
1. Este documento — seccion SM abajo
2. references/sprint_cadence.md — tu documento principal
3. references/roles_matrix.md — todo (vos facilitas entre roles)
4. references/metrics.md — seccion "Sprint Dashboard"
5. references/concurrent_work_protocol.md — seccion "Comunicacion del Equipo"

---

## Conceptos Clave (todos los roles)

### Los 3 Modos

| Modo | Cuando | Ejemplo |
|------|--------|---------|
| **FAST** | Cambio trivial, 1-2 archivos, sin DB | Fix de typo, ajuste de estilo |
| **LAUNCH** | MVP o prototipo nuevo | Primera version de una app |
| **QUALITY** | Feature para produccion | Flujo de pagos, auth, dashboard |

En duda -> QUALITY. Es mejor sobre-engineerear el proceso que sub-engineerearlo.

### Gates — Los Unicos Momentos Donde Participas

| Gate | Que significa | Quien aprueba | Texto exacto |
|------|--------------|---------------|-------------|
| HU_APPROVED | La HU esta bien definida, arranca el diseno | PO | HU_APPROVED |
| SPEC_APPROVED | El diseno tecnico es viable, arranca la implementacion | TL | SPEC_APPROVED |
| SPRINT_APPROVED | El sprint esta planificado, arrancamos | PO + TL | SPRINT_APPROVED |

**IMPORTANTE**: Solo el texto exacto activa el gate. Decir "si", "ok", "dale" NO activa nada.

### Que Hace el AI vs Que Haces Vos

| El AI hace | Vos haces |
|-----------|----------|
| Analiza la HU | Describes la feature |
| Genera el SDD (diseno tecnico) | Aprobas el diseno (gate) |
| Implementa codigo | Revisas el PR |
| Ataca su propia solucion (AR) | Revisas BLOQUEANTEs |
| Valida con evidencia (QA) | Confirmas que la evidencia es valida |
| Documenta todo | Lees el reporte final |

---

## Tu Primera HU — Paso a Paso

### Para el PO

1. Escribi la feature en lenguaje natural
2. En Sprint Planning, el SM presenta la HU y el AI la normaliza (F0 + F1)
3. Recibi el Work Item con Acceptance Criteria. Verifica: captura lo que quiero? falta algun caso? scope razonable?
4. Si esta bien, escribi: HU_APPROVED
5. Espera. El AI disena (F2), el TL aprueba el spec, el AI implementa. No te necesita hasta F4/DONE.
6. Al final, recibi el validation report con evidencia de que cada AC se cumplio.

### Para el Developer

1. Recibi la asignacion en Sprint Planning: "HU-003 es tuya"
2. Cuando el TL apruebe SPEC_APPROVED, el AI genera un **Story File** — tu unico documento
3. Lee el Story File: Goal, ACs, archivos a crear/modificar con Exemplars, Waves, restricciones (REQUIRED / FORBIDDEN)
4. Crea tu branch: git checkout -b feat/003-titulo
5. Implementa siguiendo las waves del Story File. El agente AI te asiste.
6. El AI corre Adversarial Review y Code Review automaticamente.
7. Abri un PR contra main con el template de PR (ver concurrent_work_protocol.md)
8. Espera review del peer + TL. Corrige si te piden cambios.
9. Merge.

### Para el QA Lead

1. Despues de F3 + AR + CR, recibi el codigo y los artefactos
2. Verifica el **Drift Detection**: Se crearon los archivos del SDD? Se tocaron archivos fuera de scope? Dependencias nuevas no planificadas?
3. Verifica cada **AC con evidencia archivo:linea** — No aceptes "se ve bien" como evidencia
4. Corre los **Quality Gates**: typecheck, lint, tests, build
5. Genera el validation.md con el template
6. Si algo falla -> devolver a F3 con instrucciones especificas

---

## Cheat Sheet

PIPELINE:  F0 -> F1 -> [HU_APPROVED] -> F2 -> [SPEC_APPROVED] -> F2.5 -> F3 -> AR -> CR -> F4 -> [RELEASE_APPROVED] -> DONE

MODOS:     FAST (trivial) | LAUNCH (MVP) | QUALITY (prod)

GATES:     Solo texto exacto: HU_APPROVED  SPEC_APPROVED  RELEASE_APPROVED  SPRINT_APPROVED  REVIEW_APPROVED  RETRO_APPROVED

ROLES:     PO (que) | TL (como) | Dev (implementa) | QA (valida) | SM (facilita)

BRANCHES:  feat/NNN-titulo | hotfix/NNN-titulo — Siempre PR a main. Nunca push directo.

REGLA #1:  El AI no inventa. Lee codigo real primero.
REGLA #2:  Si no esta en el Story File, escalar.
REGLA #3:  Gates son de personas. AI nunca auto-aprueba.

ESCALAR:   Dev -> TL (2h) | TL -> PO (4h) | SM si bloqueo

DOCS:      doc/sdd/NNN-titulo/ -> work-item.md | sdd.md | story-file.md | validation.md | report.md

METRICAS:  Lead time | BLOQUEANTE rate | Drift rate | Costo/HU | Carry-over rate

---

## Errores Comunes — Que NO Hacer

| Error | Por que es malo | Que hacer en su lugar |
|-------|----------------|----------------------|
| Decir "si" o "ok" esperando que active un gate | No activa nada. El pipeline no avanza. | Usar el texto exacto: HU_APPROVED, SPEC_APPROVED |
| Leer el SDD completo como developer | Perdida de tiempo y riesgo de confusion | Leer SOLO el Story File |
| Pushear directo a main | Sin review, sin CI, sin audit trail | Siempre PR con review |
| Trabajar en 2 HUs a la vez | Context switching mata productividad | 1 dev = 1 HU activa |
| No hacer rebase diario | Conflictos de merge se acumulan | git fetch, git rebase origin/main diario |
| Ignorar BLOQUEANTEs del AR | Issues de seguridad llegan a produccion | Corregir TODOS los BLOQUEANTEs antes de PR |
| Modificar archivos fuera de scope | Drift, bugs inesperados, conflictos | Si necesitas tocar algo fuera de scope, escalar a TL |

---

## Setup Tecnico — Primer Dia

### 1. Verificar NexusAgile instalado

Verificar que existe: .claude/skills/nexus-agile/SKILL.md

### 2. Generar project-context.md (si no existe)

Decir: "NexusAgile, this is a new project. Read the codebase and generate project-context.md"
El AI escanea: stack, dependencias, estructura, patrones, comandos. Lo genera una vez.

### 3. Configurar branch protection en GitHub

Settings -> Branches -> main:
- Require pull request reviews: ON
- Required approving reviews: 1
- Dismiss stale pull request approvals: ON
- Require status checks: ON
- Require linear history: ON

### 4. Crear canales de comunicacion

- Canal de sprint: #sprint-001
- Canal de equipo: #team-[nombre]

### 5. Primer Sprint Planning

Decir: "NexusAgile, sprint planning"
PO trae las HUs, TL estima, SM facilita, se asignan owners.

---

## FAQ

**Puedo usar NexusAgile sin agentes AI?**
No. La metodologia asume que los agentes AI ejecutan el pipeline. Sin AI, es un proceso waterfall muy pesado.

**Funciona con equipos remotos?**
Si. Los gates son async (texto en un canal o issue). Las ceremonias pueden ser sync o async.

**Puedo saltear fases?**
No en modo QUALITY. En FAST, el Triage decide que fases aplican. En LAUNCH, hay un pipeline simplificado.

**Que pasa si el AI se equivoca?**
El Adversarial Review (AR) existe para eso. Si el AR no lo atrapa, el peer review humano es la segunda linea. Si llega a produccion, se documenta en Auto-Blindaje y se mejora el proceso.

**Cuanto cuesta en tokens?**
Depende de la complejidad de la HU. Sprint 1 establece baseline. Ver references/metrics.md para tracking.

**Puedo usar otro LLM que no sea Claude?**
La metodologia es LLM-agnostic en principio. Los agentes son roles, no modelos especificos. Pero esta optimizada y testeada con Claude Code.

**Como se manejan hotfixes urgentes?**
Ver references/quick_flow.md seccion Hotfix. Pipeline abreviado con investigacion obligatoria de causa raiz.
