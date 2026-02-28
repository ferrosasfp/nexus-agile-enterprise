# NexusAgil

**Metodologia stack-agnostic para desarrollo de software con IA anti-alucinacion.**

Funciona con cualquier stack: Next.js, Rails, Django, Laravel, FastAPI, Go, o cualquier otro.
Se instala en minutos y se integra con Claude Code como un skill.

---

## El problema que resuelve

Los AI coding assistants tienden a **alucinar**: inventan imports que no existen, crean patrones diferentes a los del proyecto, asumen APIs que no estan disponibles.

| Problema | Solucion NexusAgil |
|----------|-------------------|
| AI inventa imports/modulos | **Codebase Grounding** — leer archivos reales antes de generar |
| AI crea patrones inconsistentes | **Exemplar Pattern** — referenciar archivos existentes |
| AI ignora restricciones | **Constraint Directives** — OBLIGATORIO/PROHIBIDO explicitos |
| Implementacion se desvio del plan | **Drift Detection** — plan vs implementacion en QA |
| Errores se repiten | **Auto-Blindaje** — documentar cuando ocurren, no al final |
| Implementacion sin estructura | **Waves** — W0 serial, W1+ paralelo |

---

## 3 Modos

NexusAgil se adapta al contexto. Al inicio de cada sesion, Claude pregunta:

> **"¿Qué estás construyendo?"**
> ```
> 1. FAST    — Un cambio pequeño (fix, estilo, 1-2 archivos)
> 2. LAUNCH  — Algo nuevo desde cero (MVP, prototipo)
> 3. QUALITY — Feature para produccion (DB, auth, pagos, usuarios reales)
> ```

### FAST — Cambio trivial
Para fixes, estilos o cambios de 1-2 archivos sin logica nueva ni DB.
Pipeline de 4 pasos sin gates formales.
**Activar:** `"Quick flow: [cambio]"`

### LAUNCH — MVP / Prototipo
Para construir algo nuevo desde cero con velocidad y estructura basica.
Tiene Codebase Grounding, Story Files y gate ligero (LAUNCH_APPROVED).
Sin AR/CR formal ni QA con evidencia.
**Activar:** `"NexusAgil, modo LAUNCH: [descripcion del MVP]"`

### QUALITY — Produccion
Para features que van a usuarios reales, con DB, auth, pagos, o en equipo.
Pipeline completo: Work Item → SDD → Story File → Dev → AR → CR → QA con evidencia.
**Activar:** `"NexusAgil, procesa esta HU: [descripcion]"`

---

## Pipeline completo (modo QUALITY)

```
F0: Contexto — Codebase Grounding, generar project-context.md si no existe
F1: Work Item + ACs EARS
GATE 1: HU_APPROVED
F2: SDD + Constraint Directives + Readiness Check
GATE 2: SPEC_APPROVED
F2.5: Story File autocontenido (Dev solo lee esto)
F3: Dev implementa por waves con anti-alucinacion
AR: Adversary Review (BLOQUEANTE/MENOR/OK)
CR: Code Review
F4: QA — cada AC con evidencia archivo:linea
Push
```

---

## Instalacion

### En cualquier proyecto con Claude Code

```bash
git clone https://github.com/ferrosasfp/NexusAgile.git /tmp/NexusAgile
cp -r /tmp/NexusAgile/.claude/skills/nexus-agil/ tu-proyecto/.claude/skills/nexus-agil/
rm -rf /tmp/NexusAgile
```

Reinicia Claude Code. Los skills se cargan automaticamente al inicio.

### Primera sesion — Bootstrap automatico

NexusAgil descubre tu proyecto solo. No edites nada manualmente.

```
NexusAgil, este es un proyecto nuevo. Lee el codebase y genera project-context.md
```

Claude (como Architect) va a leer tus dependencias, estructura de carpetas y archivos representativos
para generar un `project-context.md` con el stack y patrones reales del proyecto.

### Si usas NexusFactory

NexusAgil ya viene preinstalado en NexusFactory. No necesitas instalarlo por separado.

---

## Estructura del skill

```
.claude/skills/nexus-agil/
+-- SKILL.md                          # Pipeline completo, 3 modos, 25 reglas globales
+-- references/
    +-- agents_roster.md              # 9 roles: Analyst, Architect, Dev, QA, Adversary...
    +-- sdd_template.md               # Templates SDD (FULL / BUGFIX / MINI)
    +-- story_file_template.md        # Contrato Architect-Dev
    +-- adversarial_review_checklist.md  # 8 categorias de ataque
    +-- validation_report_template.md    # QA: drift + ACs + quality gates
    +-- launch_flow.md                # Pipeline modo LAUNCH
    +-- quick_flow.md                 # Pipeline modo FAST
    +-- sprint_cadence.md             # Planning/Status/Retro
    +-- project_context_template.md   # Template stack-agnostic
```

---

## Relacion con NexusFactory

```
NexusFactory  →  template de proyecto (stack, MCPs, estructura)
               +  NexusAgil preinstalado
NexusAgil     →  metodologia standalone (cualquier proyecto)
```

NexusAgil funciona sin NexusFactory. NexusFactory incluye NexusAgil por defecto.

---

## Creditos

Metodologia creada por Fernando Rosas.
Fusiona Nexus SDD Workflow y practicas agiles con roles especializados de IA.

MIT License
