---
description: NexusAgil F2.5 — Generate Story File from approved SDD
argument-hint: <HU-ID>
allowed-tools: Task, Read, Glob
---

# /nexus-p3-f2-5 — Story File Generation (Paso 3/8)

Lanza el sub-agente `nexus-architect` para generar el Story File a partir del SDD aprobado.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

**Rutas**: antes de lanzar, resolvé `NEXUS_ROOT`, `CODE_ROOT`, `SKILL_DIR` y `BASE_REF`, y pasá sus valores reales en cada prompt. `BASE_REF` es la base real de la HU, no siempre `main`: si la HU parte de otro PR, es esa rama o ese commit. `SKILL_DIR` es la primera que exista de `${CLAUDE_PLUGIN_ROOT}/.claude/skills/nexus-agile`, `.claude/skills/nexus-agile` y `~/.claude/skills/nexus-agile`; las demás reglas están en `$SKILL_DIR/references/paths.md`.

**Agentes**: si invocaste este comando como `/nexus-agile:...`, lanzá cada agente con el prefijo: `nexus-agile:nexus-analyst`. Sin prefijo correría otra versión instalada, y el hook lo bloquea. Si un agente termina sin entregarte su reporte, leé su artefacto y su transcript antes de seguir: nunca avances sin saber qué devolvió.

## Pre-requisitos

- El gate `SPEC_APPROVED` debe haber sido confirmado para esta HU
- `$NEXUS_ROOT/doc/sdd/NNN-titulo/sdd.md` debe existir

## Acciones

F2.5 solo corre si el work-item dice `contract_mode: classic`. Con `contract_mode: unified` (el default, también cuando el campo falta), NO lances nada: confirmá que `sdd.md` tiene la sección `Contrato de implementación` y seguí con `/nexus-p4-f3`. Si falta, relanzá `/nexus-p2-f2`.

```
Task tool:
  subagent_type: nexus-architect
  description: F2.5 Story File para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor] · BASE_REF=[valor]
    FASE: F2.5
    HU_DIR: [ruta absoluta de $NEXUS_ROOT/doc/sdd/NNN-titulo]
    Eres el agente nexus-architect de NexusAgil ejecutando F2.5 (Story File generation) para la HU [WKH-XX].

    INPUT:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/sdd.md (aprobado por SPEC_APPROVED)
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/work-item.md (referencia)
    - $SKILL_DIR/references/story_file_template.md del skill nexus-agile

    TU TAREA:
    Generar story-file.md autocontenido para que el Dev (nexus-dev) pueda implementar SIN leer nada más.

    Mínimo:
    - Contexto compacto (qué se construye, por qué)
    - Scope IN exhaustivo (lista exacta de archivos a tocar)
    - Anti-Hallucination Checklist específico de esta HU
    - Waves W0/W1/W2 con archivos exactos
    - Patrones a seguir con line ranges de exemplars
    - Tests requeridos (qué cubrir, qué archivo de test)
    - Done Definition

    OUTPUT ESPERADO:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/story-file.md
    - Resumen al orquestador

    ## Prohibido en esta fase
    - NO escribir código de producción
    - NO modificar el SDD ni el work-item
    - NO inventar — todo lo que va al Story File debe estar en el SDD
    - El Story File debe ser autocontenido: el Dev puede consultar el SDD para entender el porqué, pero el contrato es este documento
```

## Importante
- Después de F2.5 el pipeline corre automático: F3 → AR → CR → F4 → DONE.
- NO esperes confirmación humana entre F2.5 y F3 (NO hay gate ahí).
- Vos sos el ORQUESTADOR. Solo coordinás.
