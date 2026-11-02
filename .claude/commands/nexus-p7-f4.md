---
description: NexusAgil F4 — QA Validation with evidence
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash
---

# /nexus-p7-f4 — QA Validation (Paso 7/8)

Lanza el sub-agente `nexus-qa` para validar ACs con evidencia concreta y ejecutar quality gates.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

**Rutas**: antes de lanzar, resolvé `NEXUS_ROOT`, `CODE_ROOT` y `SKILL_DIR` y pasá sus valores reales en cada prompt. `SKILL_DIR` es la que exista de `.claude/skills/nexus-agile` o `~/.claude/skills/nexus-agile`; las reglas de las otras dos están en `$SKILL_DIR/references/paths.md`.

## Pre-requisitos

- AR y CR completados con veredicto APROBADO
- BLOQUEANTEs (si los hubo) resueltos por el Dev

## Acciones

```
Task tool:
  subagent_type: nexus-qa
  description: F4 QA Validation para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor]
    FASE: F4
    HU_DIR: [ruta absoluta de $NEXUS_ROOT/doc/sdd/NNN-titulo]
    Eres el agente nexus-qa de NexusAgil ejecutando F4 (Validation) para la HU [WKH-XX].

    INPUT:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/work-item.md (ACs originales en EARS)
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/story-file.md (o la sección "Contrato de implementación" de sdd.md si el work-item dice contract_mode: unified)
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/sdd.md (para drift detection)
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/ar-report.md y cr-report.md (¿hay findings sin resolver?)
    - Archivos modificados: `git -C "$CODE_ROOT" diff main...HEAD`
    - project-context.md (gate único y Entorno de validación)

    TU TAREA:
    0. Leer el Entorno de validación y validar ahí; si falta, marcar NO VERIFICABLE y escalar
    1. Drift Detection: scope drift, wave order, spec adherence, test drift
    2. AC Verification: cada AC con status PASS/FAIL/NO VERIFICABLE + evidencia concreta
    3. Gate del repo: correr UNA vez el comando único de project-context.md, con comando literal, exit code y salida. No correr sus partes por separado
    4. AR/CR follow-up: ¿los findings fueron resueltos o aceptados?

    OUTPUT ESPERADO:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/validation.md siguiendo $SKILL_DIR/references/validation_report_template.md
    - Veredicto final: APROBADO PARA DONE / APROBADO con observaciones / RECHAZADO
    - Resumen al orquestador

    ## Prohibido en esta fase
    - NO modificar código
    - NO modificar tests para que pasen (eso es trampa)
    - NO marcar AC como PASS sin evidencia concreta
    - NO ignorar drift "porque es menor"
    - "Se ve bien" NO es evidencia
```

## Después de F4

| Veredicto | Acción |
|-----------|--------|
| APROBADO PARA DONE | Con `release_gate: true`: correr F5 (`quality_pipeline.md`) y esperar `RELEASE_APPROVED`. Después, o sin ese campo, lanzar `/nexus-p8-done` |
| APROBADO con observaciones | Presentar al humano para decidir |
| RECHAZADO | Re-lanzar `/nexus-p4-f3` con AC fallidos |

## Importante
- Vos sos el ORQUESTADOR. NO ejecutás los tests vos mismo, ni validás ACs vos mismo.
- El QA es la última línea de defensa antes de DONE — no permitir saltar evidencia.
