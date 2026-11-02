---
description: NexusAgil DONE — Pipeline closure, final report, _INDEX update
argument-hint: <HU-ID>
allowed-tools: Task, Read
---

# /nexus-p8-done — Pipeline Closure (Paso 8/8)

Lanza el sub-agente `nexus-docs` para cerrar la HU: reporte final, actualización de _INDEX, consolidación de Auto-Blindaje.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

**Rutas**: antes de lanzar, resolvé `NEXUS_ROOT`, `CODE_ROOT`, `SKILL_DIR` y `BASE_REF`, y pasá sus valores reales en cada prompt. `BASE_REF` es la base real de la HU, no siempre `main`: si la HU parte de otro PR, es esa rama o ese commit. `SKILL_DIR` es la primera que exista de `${CLAUDE_PLUGIN_ROOT}/.claude/skills/nexus-agile`, `.claude/skills/nexus-agile` y `~/.claude/skills/nexus-agile`; las demás reglas están en `$SKILL_DIR/references/paths.md`.

**Agentes**: si invocaste este comando como `/nexus-agile:...`, lanzá cada agente con el prefijo: `nexus-agile:nexus-analyst`. Sin prefijo correría otra versión instalada, y el hook lo bloquea. Si un agente termina sin entregarte su reporte, leé su artefacto y su transcript antes de seguir: nunca avances sin saber qué devolvió.

## Pre-requisitos

- F4 completado con veredicto APROBADO PARA DONE, o APROBADO con observaciones si la persona decidió cerrar igual (cada observación va como deuda en `report.md`, con su fuente), y `RELEASE_APPROVED` si `project-context.md` declara `release_gate: true`
- Todos los artefactos en `$NEXUS_ROOT/doc/sdd/NNN-titulo/`:
  - work-item.md, sdd.md, story-file.md (no existe con contract_mode: unified)
  - ar-report.md, cr-report.md, validation.md
  - auto-blindaje.md (si hubo errores)

## Acciones

Antes de lanzar Docs, corré las métricas de la HU y pasáselas en el prompt (las lee de los transcripts y de `.gates.jsonl`, sin modelo):

```bash
python3 "$SKILL_DIR/scripts/nexus_metrics.py" --hu-dir "[HU_DIR]"
```

```
Task tool:
  subagent_type: nexus-docs
  description: DONE para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor] · BASE_REF=[valor]
    FASE: DONE
    HU_DIR: [ruta absoluta de $NEXUS_ROOT/doc/sdd/NNN-titulo]
    Eres el agente nexus-docs de NexusAgil ejecutando la fase DONE (closure) para la HU [WKH-XX].

    INPUT:
    Todos los artefactos en $NEXUS_ROOT/doc/sdd/NNN-titulo/:
    - work-item.md, sdd.md, story-file.md (no existe con contract_mode: unified)
    - blq-verification.md (si existe)
    - ar-report.md, cr-report.md, validation.md
    - auto-blindaje.md (si existe)
    Y el índice histórico: $NEXUS_ROOT/doc/sdd/_INDEX.md

    TU TAREA:
    1. Compilar report.md final consolidado en $NEXUS_ROOT/doc/sdd/NNN-titulo/report.md con:
       - Resumen ejecutivo
       - Pipeline ejecutado (gates, fechas)
       - AC results del validation.md
       - Hallazgos finales (BLOQUEANTEs resueltos, MENORs aceptados)
       - Auto-Blindaje consolidado (sin perder entradas)
       - Archivos modificados
       - Decisiones diferidas a backlog (spinoffs)
       - Lecciones para próximas HUs
       - Métricas: la tabla de nexus_metrics.py que te paso, tal cual, sin recalcular
    2. Actualizar $NEXUS_ROOT/doc/sdd/_INDEX.md con status final (DONE/ABORTED/BLOCKED), fecha, branch, link al report
    3. Verificar que el validation.md tiene veredicto APROBADO. Si no → marcar BLOCKED.

    OUTPUT ESPERADO:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/report.md
    - $NEXUS_ROOT/doc/sdd/_INDEX.md actualizado
    - Resumen ejecutivo (5-10 líneas) al orquestador

    ## Prohibido en esta fase
    - NO modificar código fuente
    - NO modificar artefactos previos (son inmutables)
    - NO marcar DONE si validation.md no es APROBADO
    - NO mergear PRs ni hacer push
```

## Después de DONE

- Presentá el resumen ejecutivo al humano
- Si hay spinoffs (tickets nuevos como WKH-33): mencionalos
- El humano decide cuándo mergear el PR y cerrar el ticket en Jira
- **Antes de un push o de abrir el PR**, mostrale a la persona qué va a disparar, leyendo los workflows completos (no buscando palabras): cada job de CI que corre con ese push o PR y qué hace (por ejemplo, migraciones sobre una base desechable), y si hay deploy de preview. Pedí la autorización con esa lista. En una corrida real, el push disparó un job de migraciones y un preview que nadie había anticipado
- Si la base de la HU no existe en el remoto (HU apilada), la descripción del PR lo dice y trae el enlace de comparación contra `BASE_REF`

## Si Claude Code rechaza la escritura del artefacto

Claude Code puede rechazar que un subagente escriba un archivo de reporte, con un mensaje como `Subagents should return findings as text, not write report files`. Lo rechaza Claude Code, no el hook de NexusAgil, y el propio mensaje pide devolver el contenido como texto. Visto en una corrida real con `report.md`.

En ese caso, y solo en ese:
1. El agente devuelve el contenido completo entre las líneas `<<<ARTEFACTO report.md` y `ARTEFACTO>>>`, sin resumirlo.
2. El orquestador lo escribe tal cual con Write en `HU_DIR`, sin cambiar nada, y anota en la bitácora el mensaje literal y el sha256 del archivo.
3. Si hace falta corregir algo del contenido, lo decide una persona y la corrección se muestra como diff aparte.

No cuenta como rodeo: el rechazo pide exactamente eso. Escribir el artefacto con otro contenido, o por Bash, sí lo es.

## Importante
- Vos sos el ORQUESTADOR. NO escribas el report.md vos mismo, salvo en el caso de arriba, copiándolo tal cual.
- DONE es solo cierre documental. No mergea, no pushea, no hace deploy.
