---
description: NexusAgil F2 — Generate SDD from approved work-item.md
argument-hint: <HU-ID>
allowed-tools: Task, Read, Glob
---

# /nexus-p2-f2 — SDD Generation (Paso 2/8)

Lanza el sub-agente `nexus-architect` para generar el SDD a partir del work-item aprobado.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

**Rutas**: antes de lanzar, resolvé `NEXUS_ROOT`, `CODE_ROOT`, `SKILL_DIR` y `BASE_REF`, y pasá sus valores reales en cada prompt. `BASE_REF` es la base real de la HU, no siempre `main`: si la HU parte de otro PR, es esa rama o ese commit. `SKILL_DIR` es la primera que exista de `${CLAUDE_PLUGIN_ROOT}/.claude/skills/nexus-agile`, `.claude/skills/nexus-agile` y `~/.claude/skills/nexus-agile`; las demás reglas están en `$SKILL_DIR/references/paths.md`.

**Agentes**: si invocaste este comando como `/nexus-agile:...`, lanzá cada agente con el prefijo: `nexus-agile:nexus-analyst`. Sin prefijo correría otra versión instalada, y el hook lo bloquea. Si un agente termina sin entregarte su reporte, leé su artefacto y su transcript antes de seguir: nunca avances sin saber qué devolvió.

## Pre-requisitos

- El gate `HU_APPROVED` debe haber sido confirmado por el humano para esta HU
- `$NEXUS_ROOT/doc/sdd/NNN-titulo/work-item.md` debe existir
- Verificá ambos antes de lanzar el sub-agente

## Acciones

1. Identificá el directorio `$NEXUS_ROOT/doc/sdd/NNN-titulo/` correspondiente a la HU.
2. Verificá que `work-item.md` exista. Si no, abortá y avisá al humano.
3. Lanzá el sub-agente:

```
Task tool:
  subagent_type: nexus-architect
  description: F2 SDD para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor] · BASE_REF=[valor]
    FASE: F2
    HU_DIR: [ruta absoluta de $NEXUS_ROOT/doc/sdd/NNN-titulo]
    Eres el agente nexus-architect de NexusAgil ejecutando F2 (SDD generation) para la HU [WKH-XX].

    INPUT:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/work-item.md (contrato aprobado por HU_APPROVED)
    - project-context.md (fuente de verdad del stack)
    - $SKILL_DIR/references/sdd_template.md del skill nexus-agile

    TU TAREA:
    1. Codebase Grounding: leé el work-item completo, project-context, y 1-3 archivos similares al feature
    2. Verificar exemplars con Glob — todos los paths que vayas a referenciar deben existir
    3. Generar sdd.md en $NEXUS_ROOT/doc/sdd/NNN-titulo/sdd.md con:
       - Context Map (qué leíste y por qué)
       - Decisiones técnicas (DT-N) heredadas del work-item + nuevas del SDD
       - Constraint Directives (CD-N) — heredados + nuevos
       - Waves W0/W1/W2+ con archivos exactos por wave
       - Exemplars verificados (paths reales con line ranges)
       - Plan de tests
       - Readiness Check final
       - La sección "Contrato de implementación" de sdd_template.md (contract_mode: unified, el default). Solo se omite si el work-item dice contract_mode: classic

    OUTPUT ESPERADO:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/sdd.md
    - Resumen ejecutivo al orquestador con: nº waves, archivos a tocar, decisiones críticas, exemplars usados

    ## Prohibido en esta fase
    - NO escribir código de producción
    - NO modificar archivos fuera de $NEXUS_ROOT/doc/sdd/NNN-titulo/
    - NO inventar paths, librerías, APIs — verificá todo con Glob/Read/Grep
    - NO asumir un stack distinto al definido en project-context.md
    - NO dejar [NEEDS CLARIFICATION] sin marcar — si hay ambigüedad, marcala
```

4. Cuando el sub-agente entregue el SDD, presentalo al humano con resumen ejecutivo y esperá `SPEC_APPROVED`.
5. NO continúes hasta recibir el gate. Después sigue directo F3 (`contract_mode: unified`, el default), o F2.5 si el work-item dice `contract_mode: classic`.

## Importante
- Vos sos el ORQUESTADOR. NO escribas el SDD vos mismo.
- Si el sub-agente reporta `[NEEDS CLARIFICATION]` sin resolver, presentalos al humano para que decida.
