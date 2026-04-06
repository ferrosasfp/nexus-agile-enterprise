---
description: NexusAgil DONE — Pipeline closure, final report, _INDEX update
argument-hint: <HU-ID>
allowed-tools: Task, Read
---

# /nexus-p8-done — Pipeline Closure (Paso 8/8)

Lanza el sub-agente `nexus-docs` para cerrar la HU: reporte final, actualización de _INDEX, consolidación de Auto-Blindaje.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

## Pre-requisitos

- F4 completado con veredicto APROBADO PARA DONE
- Todos los artefactos en `doc/sdd/NNN-titulo/`:
  - work-item.md, sdd.md, story-file.md
  - ar-report.md, cr-report.md, validation.md
  - auto-blindaje.md (si hubo errores)

## Acciones

```
Task tool:
  subagent_type: nexus-docs
  description: DONE para HU [WKH-XX]
  prompt: |
    Eres el agente nexus-docs de NexusAgil ejecutando la fase DONE (closure) para la HU [WKH-XX].

    INPUT:
    Todos los artefactos en doc/sdd/NNN-titulo/:
    - work-item.md, sdd.md, story-file.md
    - ar-report.md, cr-report.md, validation.md
    - auto-blindaje.md (si existe)
    Y el índice histórico: doc/sdd/_INDEX.md

    TU TAREA:
    1. Compilar report.md final consolidado en doc/sdd/NNN-titulo/report.md con:
       - Resumen ejecutivo
       - Pipeline ejecutado (gates, fechas)
       - AC results del validation.md
       - Hallazgos finales (BLOQUEANTEs resueltos, MENORs aceptados)
       - Auto-Blindaje consolidado (sin perder entradas)
       - Archivos modificados
       - Decisiones diferidas a backlog (spinoffs)
       - Lecciones para próximas HUs
    2. Actualizar doc/sdd/_INDEX.md con status final (DONE/ABORTED/BLOCKED), fecha, branch, link al report
    3. Verificar que el validation.md tiene veredicto APROBADO. Si no → marcar BLOCKED.

    OUTPUT ESPERADO:
    - doc/sdd/NNN-titulo/report.md
    - doc/sdd/_INDEX.md actualizado
    - Resumen ejecutivo (5-10 líneas) al orquestador

    ## ⛔ PROHIBIDO EN ESTA FASE
    - NO modificar código fuente
    - NO modificar artefactos previos (son inmutables)
    - NO marcar DONE si validation.md no es APROBADO
    - NO mergear PRs ni hacer push
```

## Después de DONE

- Presentá el resumen ejecutivo al humano
- Si hay spinoffs (tickets nuevos como WKH-33): mencionalos
- El humano decide cuándo mergear el PR y cerrar el ticket en Jira

## ⚠️ Importante
- Vos sos el ORQUESTADOR. NO escribas el report.md vos mismo.
- DONE es solo cierre documental. No mergea, no pushea, no hace deploy.
