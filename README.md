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
| Implementacion sin estructura | **Waves** — W0 serial, W1+ paralelo con re-mapeo entre waves |

---

## Los 9 Agentes

Los agentes son roles que Claude asume segun la fase. No son personas distintas — es Claude cambiando de sombrero. Quien especifica no implementa. Quien implementa no valida.

| Agente | Rol | Fases donde actua |
|--------|-----|-------------------|
| **Analyst** | Extrae requisitos, normaliza HU, define ACs EARS | F0, F1 |
| **Architect** | Codebase Grounding, SDD, Story File, Code Review | F0, F1, F2, F2.5, CR |
| **UX** | Microcopy, flujos de usuario, accesibilidad | F1 (si hay UI) |
| **Adversary** | Ataca la solucion buscando fallas de seguridad y logica | AR, CR |
| **Dev** | Implementa SOLO desde el Story File, waves, anti-alucinacion | F3 |
| **SM** | Sprint Planning, Status, Retrospectiva | Cadencia semanal |
| **QA** | Valida ACs con evidencia archivo:linea, Drift Detection | F4 |
| **Triage** | Evalua si un cambio califica como FAST o sube de modo | Quick Flow |
| **Docs** | Documenta artefactos finales, actualiza _INDEX.md | DONE |

**Regla de separacion de roles:**
- Quien **especifica** (Architect) NO implementa (Dev)
- Quien **implementa** (Dev) NO valida (QA)
- Quien **revisa adversarialmente** (Adversary) NO implemento el codigo

---

## 3 Modos

Al inicio de cada sesion, Claude pregunta:

> **"¿Qué estás construyendo?"**
> ```
> 1. FAST    — Un cambio pequeño (fix, estilo, 1-2 archivos)
> 2. LAUNCH  — Algo nuevo desde cero (MVP, prototipo)
> 3. QUALITY — Feature para produccion (DB, auth, pagos, usuarios reales)
> ```

---

## FAST — Cambio trivial

**Activar:** `"Quick flow: [cambio]"` / `"Implementa [algo pequeño]"`

**Califica como FAST si cumple TODO:**
- Maximo 2 archivos
- Menos de 30 lineas de cambio
- Sin cambios de DB ni migraciones
- Sin logica de negocio nueva
- Sin auth ni pagos involucrados

**Si no cumple alguno → sube automaticamente a LAUNCH o QUALITY.**

### Pipeline FAST

```
[Triage] evalua si califica como FAST
    |
    v
[Architect] Codebase Grounding minimo
    Lee el archivo a modificar
    Identifica el patron existente
    |
    v
[Dev] implementa el cambio
    Sigue el patron encontrado
    No inventa nada nuevo
    |
    v
[Dev] verificacion: typecheck/build pasa
    |
    v
Push
```

**Agentes:** Triage → Architect (minimo) → Dev

**Sin gates formales. Sin story file. Sin AR ni QA formal.**

---

## LAUNCH — MVP / Prototipo

**Activar:** `"NexusAgil, modo LAUNCH: [descripcion del MVP]"`

**Usar cuando:**
- Proyecto nuevo desde cero
- MVP para demo, pitch o primera version
- No va a produccion todavia (o es la v1)
- Quieres velocidad con estructura basica

### Pipeline LAUNCH

```
[Architect] F0: Bootstrap de Proyecto
    Lee codebase real (dependencias, estructura, archivos)
    Genera project-context.md con stack y patrones reales
    Confirma al humano lo que encontro
    |
    v
[Analyst] F1: Lista de HUs del MVP
    Normaliza lo que el humano quiere construir
    Genera lista de HUs con titulo + objetivo + estimacion
    Presenta al humano para confirmar scope
    |
    v
⛔ GATE: humano escribe LAUNCH_APPROVED
    |
    v
[Architect] F2: Story File por HU (simplificado)
    Lee archivos relacionados (Codebase Grounding)
    Genera story file con: objetivo, ACs, archivos, exemplars, waves
    Sin SDD completo ni Constraint Directives extensas
    |
    v
[Dev] F3: Implementacion por waves
    Lee el Story File completo
    Anti-Hallucination Protocol: lee exemplar antes de cada tarea
    Implementa W0 serial, W1+ paralelo
    Re-mapeo ligero entre waves
    Auto-Blindaje si hay errores
    |
    v
[Dev / QA] QA ligero
    Build/typecheck limpio
    ACs verificados: CUMPLE / NO CUMPLE
    Sin evidencia archivo:linea (eso es QUALITY)
    |
    v
Push — repetir F2→F3→QA por cada HU
```

**Agentes:** Architect → Analyst → (GATE) → Architect → Dev → QA ligero

**Tiene:** Codebase Grounding, Story Files, gate humano, anti-alucinacion, waves
**No tiene:** Work Item formal, SDD completo, Adversarial Review, Code Review formal, QA con evidencia

---

## QUALITY — Produccion

**Activar:** `"NexusAgil, procesa esta HU: [descripcion]"`

**Usar siempre cuando:**
- Va a usuarios reales
- Tiene DB, auth, pagos o datos sensibles
- Equipo de 2+ personas
- Un bug tiene costo real (datos, dinero, reputacion)

### Pipeline QUALITY

```
[Analyst + Architect] F0: Contexto
    Verifica si existe project-context.md
    Si NO existe: Bootstrap (lee codebase, genera project-context.md)
    Codebase Grounding inicial
    Smart Sizing: clasifica la HU (full / bugfix / mini / patch)
    |
    v
[Analyst + Architect + UX] F1: Discovery
    Normaliza la HU en un Work Item estructurado
    Define ACs en formato EARS (Event/State/Unwanted-driven)
    Define Scope IN y OUT
    Presenta al humano
    |
    v
⛔ GATE 1: humano escribe HU_APPROVED
    (solo este texto exacto — "ok", "dale", "si" NO cuentan)
    |
    v
[Architect + Adversary] F2: SDD
    Codebase Grounding profundo (lee archivos relacionados)
    Genera Context Map con archivos leidos y patrones extraidos
    Genera SDD con: rutas, schema DB, componentes UI, DoD
    Genera Constraint Directives: OBLIGATORIO / PROHIBIDO
    Implementation Readiness Check
    |
    v
⛔ GATE 2: humano escribe SPEC_APPROVED
    (solo este texto exacto)
    |
    v
[Architect] F2.5: Story File
    Contrato autocontenido para Dev
    Incluye: objetivo, ACs, archivos, exemplars con codigo real,
    Constraint Directives, waves, out of scope, escalation rule
    Dev SOLO lee este archivo — nada mas
    |
    v
[Dev] F3: Implementacion
    Lee Story File completo
    Anti-Hallucination Protocol antes de cada tarea:
      - Lee el exemplar referenciado
      - Verifica que los imports existen
      - Sigue el patron del exemplar
    Implementa W0 serial, W1+ paralelo
    Re-mapeo ligero entre waves
    Verificacion incremental al completar cada wave
    Auto-Blindaje si hay errores (documenta inmediatamente)
    |
    v
[Adversary] Adversarial Review
    Ataca la solucion buscando fallas reales:
      - Auth bypass
      - SSRF
      - Race conditions
      - API keys expuestas
      - Hardcodes
      - Datos simulados en produccion
    Clasifica: BLOQUEANTE / MENOR / OK
    BLOQUEANTEs → Dev corrige → Adversary re-revisa
    |
    v
[Adversary + QA] Code Review
    Valida patrones seguidos vs exemplars del Story File
    Naming consistente con el proyecto
    Sin logica duplicada
    Sin archivos fuera de scope
    Clasifica: DEBE CORREGIR / SUGERENCIA
    |
    v
[QA] F4: Validacion
    Drift Detection: archivos creados/modificados vs esperados
    Verifica cada AC con evidencia obligatoria:
      ✅ CUMPLE — src/archivo.tsx:42
      ❌ NO CUMPLE — no encontrado en codebase
      ⚠️ PARCIAL — src/archivo.tsx:42 (razon)
    Quality Gates: build limpio, sin imports inexistentes
    |
    v
[Docs] DONE
    Genera reporte final
    Actualiza doc/sdd/_INDEX.md
    |
    v
Push
```

**Agentes:** Analyst + Architect + UX → (GATE 1) → Architect + Adversary → (GATE 2) → Architect → Dev → Adversary → Adversary + QA → QA → Docs

---

## Tabla comparativa de modos

| | FAST | LAUNCH | QUALITY |
|---|---|---|---|
| **Para que** | Fix trivial | MVP / prototipo | Produccion |
| **Archivos** | 1-2 | multiples | multiples |
| **Codebase Grounding** | minimo | completo | profundo |
| **Work Item formal** | ❌ | ❌ | ✅ |
| **ACs EARS** | ❌ | basicos | ✅ |
| **SDD completo** | ❌ | ❌ | ✅ |
| **Constraint Directives** | ❌ | ❌ | ✅ |
| **Story File** | ❌ | simplificado | autocontenido |
| **Gate HU_APPROVED** | ❌ | ❌ | ✅ |
| **Gate LAUNCH_APPROVED** | ❌ | ✅ | ❌ |
| **Gate SPEC_APPROVED** | ❌ | ❌ | ✅ |
| **Adversarial Review** | ❌ | ❌ | ✅ |
| **Code Review formal** | ❌ | ❌ | ✅ |
| **QA con evidencia** | ❌ | ❌ | ✅ |
| **Anti-alucinacion** | parcial | ✅ | ✅ |
| **Waves** | ❌ | ✅ | ✅ |
| **Auto-Blindaje** | ❌ | ✅ | ✅ |
| **Velocidad** | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| **Seguridad** | basica | media | alta |

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

```
NexusAgil, este es un proyecto nuevo. Lee el codebase y genera project-context.md
```

Claude descubre solo: lenguaje, framework, arquitectura, comandos, patrones.
No necesitas editar nada manualmente.

### Si usas NexusFactory

NexusAgil ya viene preinstalado. No necesitas instalarlo por separado.

---

## Estructura del skill

```
.claude/skills/nexus-agil/
+-- SKILL.md                             # Pipeline completo, 3 modos, reglas globales
+-- references/
    +-- agents_roster.md                 # 9 agentes con personalidad y responsabilidades
    +-- sdd_template.md                  # Templates SDD (FULL / BUGFIX / MINI)
    +-- story_file_template.md           # Contrato Architect-Dev
    +-- adversarial_review_checklist.md  # 8 categorias de ataque del Adversary
    +-- validation_report_template.md    # QA: drift + ACs + quality gates
    +-- launch_flow.md                   # Pipeline detallado modo LAUNCH
    +-- quick_flow.md                    # Pipeline detallado modo FAST
    +-- sprint_cadence.md                # Planning/Status/Retro del SM
    +-- project_context_template.md      # Template stack-agnostic para project-context.md
```

---

## Relacion con NexusFactory

```
NexusFactory  =  template de proyecto (stack, MCPs, estructura)
             +   NexusAgil preinstalado

NexusAgil     =  metodologia standalone (cualquier proyecto)
```

NexusAgil funciona sin NexusFactory.
NexusFactory incluye NexusAgil por defecto con los 3 modos disponibles.

---

## Creditos

Metodologia creada por Fernando Rosas.
Fusiona Nexus SDD Workflow y practicas agiles con roles especializados de IA.

MIT License
