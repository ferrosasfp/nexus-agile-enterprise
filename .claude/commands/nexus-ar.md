---
description: NexusAgil AR — Adversarial Review of implementation
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash
---

# /nexus-ar — Adversarial Review

Lanza el sub-agente `nexus-adversary` para atacar la implementación recién terminada.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

## Pre-requisitos

- F3 debe haber terminado (código en disco, tests pasando)
- `git diff --name-only main...HEAD` debe mostrar los archivos modificados

## Acciones

```
Task tool:
  subagent_type: nexus-adversary
  description: AR para HU [WKH-XX]
  prompt: |
    Eres el agente nexus-adversary de NexusAgil ejecutando AR (Adversarial Review) para la HU [WKH-XX].

    INPUT:
    - doc/sdd/NNN-titulo/story-file.md (contrato que el Dev debía cumplir)
    - doc/sdd/NNN-titulo/auto-blindaje.md (errores documentados por el Dev)
    - Archivos modificados: ejecutar `git diff --name-only main...HEAD` (o el branch base)
    - references/adversarial_review_checklist.md del skill nexus-agile

    TU TAREA:
    Atacar la implementación en las 8 categorías:
    1. Security
    2. Error Handling
    3. Data Integrity
    4. Performance
    5. Integration
    6. Type Safety
    7. Test Coverage
    8. Scope Drift

    Para cada categoría: BLOQUEANTE / MENOR / OK con evidencia archivo:línea.

    OUTPUT ESPERADO:
    - doc/sdd/NNN-titulo/ar-report.md
    - Veredicto final: APROBADO / APROBADO con MENORs / RECHAZADO
    - Resumen al orquestador

    ## ⛔ PROHIBIDO EN ESTA FASE
    - NO modificar código (solo Read, Glob, Grep, Bash)
    - NO escribir el fix vos mismo — solo reportar el hallazgo
    - NO ser permisivo: tu trabajo es romper, no validar
    - NO modificar story-file ni SDD
```

## Después de AR

| Veredicto | Acción del orquestador |
|-----------|------------------------|
| APROBADO / APROBADO con MENORs | Lanzar `/nexus-cr` |
| RECHAZADO (BLOQUEANTEs activos) | Re-lanzar `/nexus-f3` con la lista de findings |

## ⚠️ Importante
- Vos sos el ORQUESTADOR. NO ataques vos mismo.
- Si hay BLOQUEANTEs: NO avances a CR hasta que el Dev los resuelva en una nueva iteración de F3.
