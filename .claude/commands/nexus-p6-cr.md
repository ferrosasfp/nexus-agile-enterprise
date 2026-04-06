---
description: NexusAgil CR — Code Review (quality, patterns, complexity)
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash
---

# /nexus-p6-cr — Code Review (Paso 6/8)

Lanza el sub-agente `nexus-adversary` (en modo CR) para revisar calidad de código, patrones y complejidad.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

## Pre-requisitos

- AR completado con veredicto APROBADO o APROBADO con MENORs
- `ar-report.md` existe en `doc/sdd/NNN-titulo/`

## Acciones

```
Task tool:
  subagent_type: nexus-adversary
  description: CR para HU [WKH-XX]
  prompt: |
    Eres el agente nexus-adversary de NexusAgil ejecutando CR (Code Review) para la HU [WKH-XX].

    INPUT:
    - doc/sdd/NNN-titulo/story-file.md
    - doc/sdd/NNN-titulo/ar-report.md (referencia — no repitas hallazgos del AR)
    - Archivos modificados: `git diff main...HEAD`

    TU TAREA:
    Revisar calidad de código (NO seguridad — eso fue AR). 6 checks:
    1. Naming consistency con el proyecto
    2. Complejidad (funciones >50 líneas, ciclomática alta)
    3. DRY violations (código duplicado evitable)
    4. SOLID / patrones del proyecto
    5. Tests: cobertura, claridad, asserts significativos
    6. Documentación inline (JSDoc/comments donde la lógica no es obvia)

    Clasificar hallazgos como BLOQUEANTE / MENOR / OK.

    OUTPUT ESPERADO:
    - doc/sdd/NNN-titulo/cr-report.md
    - Veredicto final
    - Resumen al orquestador

    ## ⛔ PROHIBIDO EN ESTA FASE
    - NO modificar código
    - NO repetir hallazgos del AR (referencialos si aplica)
    - NO ser exigente con cosas no documentadas en el project-context
```

## Después de CR

| Veredicto | Acción |
|-----------|--------|
| APROBADO / APROBADO con MENORs | Lanzar `/nexus-p7-f4` |
| RECHAZADO | Re-lanzar `/nexus-p4-f3` con la lista de findings |

## ⚠️ Importante
- Vos sos el ORQUESTADOR. NO revisás vos mismo.
- CR es menos crítico que AR — sé razonable con MENORs aceptados como deuda técnica.
