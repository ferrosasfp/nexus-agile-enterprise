---
description: NexusAgil CR — Code Review (legacy / re-run después de fixes de AR)
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash
---

# /nexus-p6-cr — Code Review (Paso 6/8) — OPCIONAL desde Fase 1.5

> ⚠️ **Desde Fase 1.5**, este comando es **opcional**: `/nexus-p5-ar` ahora lanza AR y CR EN PARALELO en una sola pasada. Solo usá `/nexus-p6-cr` standalone si:
>
> 1. Querés ejecutar CR sin AR (caso raro)
> 2. Necesitás **re-correr CR** después de que el Dev aplicó fixes de BLOQUEANTEs de AR que cambiaron el código de forma estructural (ver tradeoff en `/nexus-p5-ar`)
> 3. El cr-report.md no se generó por algún motivo y querés regenerarlo

Lanza el sub-agente `nexus-adversary` (en modo CR) para revisar calidad de código, patrones y complejidad.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

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
    4. SOLID — evaluá cada principio como PASS / MENOR / BLQ-BAJO / BLQ-MED / BLQ-ALTO:
       - **S (SRP)**: ¿alguna clase/función tiene >1 responsabilidad clara? Señales: nombre con "y" (UserAndEmailService), >300 líneas, importa librerías de dominios no relacionados.
       - **O (OCP)**: ¿hay if/switch hardcodeado sobre tipo/categoría que requeriría editar para agregar un caso nuevo? (Solo flag si la variación ya apareció ≥2 veces; YAGNI > OCP prematuro.)
       - **L (LSP)**: ¿algún override de subclase rompe el contrato del padre? (Excepciones nuevas, postcondiciones más débiles, precondiciones más estrictas, throws de UnsupportedOperation.)
       - **I (ISP)**: ¿alguna interface fuerza a clientes a depender de métodos que no usan? (Implementaciones con NotImplemented o que devuelven null por método irrelevante.)
       - **D (DIP)**: ¿algún módulo de alto nivel (lógica de negocio/dominio) importa implementaciones concretas de bajo nivel (drivers, librerías de infra) en lugar de abstracciones? (Test de humo: ¿podés mockear esto en un unit test sin tocar archivos del dominio?)
       REGLA: aplicá SOLID como **lente, no como checklist ritual**. Si el proyecto tiene un estilo pragmático que rompe un principio conscientemente (ej: YAGNI sobre OCP, framework constraints), marcalo OK con nota explicativa. NO sobre-abstracts.
    5. Tests: cobertura, claridad, asserts significativos
    6. Documentación inline (JSDoc/comments donde la lógica no es obvia)

    Clasificar hallazgos como BLQ-ALTO / BLQ-MED / BLQ-BAJO / MENOR / OK (cualquier BLQ bloquea el gate).

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
