---
description: NexusAgil CR — Code Review (legacy / re-run después de fixes de AR)
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash
---

# /nexus-p6-cr — Code Review (Paso 6/8) — OPCIONAL desde Fase 1.5

> **Desde Fase 1.5**, este comando es **opcional**: `/nexus-p5-ar` ahora lanza AR y CR EN PARALELO en una sola pasada. Solo usá `/nexus-p6-cr` standalone si:
>
> 1. Querés ejecutar CR sin AR (caso raro)
> 2. Necesitás **re-correr CR** después de que el Dev aplicó fixes de BLOQUEANTEs de AR que cambiaron el código de forma estructural (ver tradeoff en `/nexus-p5-ar`)
> 3. El cr-report.md no se generó por algún motivo y querés regenerarlo

Lanza el sub-agente `nexus-adversary` (en modo CR) para revisar calidad de código, patrones y complejidad.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

**Rutas**: antes de lanzar, resolvé `NEXUS_ROOT`, `CODE_ROOT`, `SKILL_DIR` y `BASE_REF`, y pasá sus valores reales en cada prompt. `BASE_REF` es la base real de la HU, no siempre `main`: si la HU parte de otro PR, es esa rama o ese commit. `SKILL_DIR` es la primera que exista de `${CLAUDE_PLUGIN_ROOT}/.claude/skills/nexus-agile`, `.claude/skills/nexus-agile` y `~/.claude/skills/nexus-agile`; las demás reglas están en `$SKILL_DIR/references/paths.md`.

**Agentes**: si invocaste este comando como `/nexus-agile:...`, lanzá cada agente con el prefijo: `nexus-agile:nexus-analyst`. Sin prefijo correría otra versión instalada, y el hook lo bloquea. Si un agente termina sin entregarte su reporte, leé su artefacto y su transcript antes de seguir: nunca avances sin saber qué devolvió.

## Pre-requisitos

- F3 (o re-F3) completado, código en disco
- Si es re-run post-AR-fixes: el Dev ya aplicó los BLOQUEANTEs de AR
- `ar-report.md` puede existir o no — CR no depende de él en modo standalone

## Acciones

```
Task tool:
  subagent_type: nexus-adversary
  description: CR para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor] · BASE_REF=[valor]
    FASE: CR
    HU_DIR: [ruta absoluta de $NEXUS_ROOT/doc/sdd/NNN-titulo]
    Eres el agente nexus-adversary de NexusAgil ejecutando CR (Code Review) para la HU [WKH-XX].

    INPUT:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/story-file.md (o la sección "Contrato de implementación" de sdd.md si el work-item dice contract_mode: unified)
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/ar-report.md (referencia — no repitas hallazgos del AR)
    - Archivos modificados: `git -C "$CODE_ROOT" diff $BASE_REF...HEAD`
    - La corrida del gate del Dev al cerrar F3: [comando, exit code, HEAD y últimas líneas]. No repitas la suite completa

    TU TAREA:
    Revisar calidad de código (NO seguridad — eso fue AR). Los 8 checks de quality_pipeline.md, sección Code Review:
    1. Patrones: ¿se siguieron los exemplars?
    2. Naming: consistente con el proyecto
    3. Complejidad: funciones cortas y responsabilidad única. SOLID como lente, no como checklist: solo se reporta con impacto concreto, y YAGNI gana a una abstracción prematura. Comentarios solo donde la lógica no es obvia
    4. Duplicación evitable
    5. Imports: solo dependencias aprobadas
    6. Límites de archivo del proyecto
    7. Escala: `git -C "$CODE_ROOT" diff --stat` contra el presupuesto del SDD 4.1; un exceso sin justificar es hallazgo
    8. Claims: números, tablas de ejemplos y frases de cobertura deben tener testigo

    Clasificar hallazgos como BLQ-ALTO / BLQ-MED / BLQ-BAJO / MENOR / OK (cualquier BLQ bloquea el gate).

    OUTPUT ESPERADO:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/cr-report.md
    - Veredicto final
    - Resumen al orquestador

    ## Prohibido en esta fase
    - NO modificar código
    - NO repetir hallazgos del AR (referencialos si aplica)
    - NO ser exigente con cosas no documentadas en el project-context
```

## Después de CR

| Veredicto | Acción |
|-----------|--------|
| APROBADO / APROBADO con MENORs | Lanzar `/nexus-p7-f4` |
| RECHAZADO | Verificar los BLQ como indica `/nexus-p5-ar` y re-lanzar `/nexus-p4-f3` con los que sigan en pie |

## Importante
- Vos sos el ORQUESTADOR. NO revisás vos mismo.
- CR es menos crítico que AR — sé razonable con MENORs aceptados como deuda técnica.
