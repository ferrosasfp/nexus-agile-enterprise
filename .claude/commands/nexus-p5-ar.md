---
description: NexusAgil AR + CR — Adversarial + Code Review en PARALELO
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash
---

# /nexus-p5-ar — AR + CR Parallel (Paso 5/8)

Lanza el sub-agente `nexus-adversary` **DOS VECES en paralelo** (mismo mensaje, 2 Task tool calls): una en modo AR (security/integrity) y otra en modo CR (quality/patterns).

**Speedup**: ~50% del wallclock combinado vs ejecutar p5 → p6 secuencial.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

## Pre-requisitos

- F3 debe haber terminado (código en disco, tests pasando)
- `git diff --name-only main...HEAD` debe mostrar los archivos modificados

## Acciones — DOS Tasks en EL MISMO MENSAJE (paralelo real)

CRÍTICO: emitir ambos Task tool calls en **un solo bloque de tool_use** para que Claude Code los ejecute concurrentemente. Si los emitís en mensajes separados serán secuenciales.

```
Task #1 (AR):
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

Task #2 (CR — corre en paralelo con #1):
  subagent_type: nexus-adversary
  description: CR para HU [WKH-XX]
  prompt: |
    Eres el agente nexus-adversary de NexusAgil ejecutando CR (Code Review) para la HU [WKH-XX].

    NOTA: corres EN PARALELO con AR. NO podés leer ar-report.md (todavía no existe).
    Si encontrás algo que claramente es de seguridad/integridad (territorio AR), reportalo igual
    — el orquestador deduplica al consolidar.

    INPUT:
    - doc/sdd/NNN-titulo/story-file.md
    - Archivos modificados: `git diff main...HEAD`

    TU TAREA:
    Revisar calidad de código (NO seguridad — eso es AR). 6 checks:
    1. Naming consistency con el proyecto
    2. Complejidad (funciones >50 líneas, ciclomática alta)
    3. DRY violations (código duplicado evitable)
    4. SOLID — evaluá cada principio como PASS / MENOR / BLOQUEANTE:
       - **S (SRP)**: ¿alguna clase/función tiene >1 responsabilidad clara? Señales: nombre con "y" (UserAndEmailService), >300 líneas, importa librerías de dominios no relacionados.
       - **O (OCP)**: ¿hay if/switch hardcodeado sobre tipo/categoría que requeriría editar para agregar un caso nuevo? (Solo flag si la variación ya apareció ≥2 veces; YAGNI > OCP prematuro.)
       - **L (LSP)**: ¿algún override de subclase rompe el contrato del padre? (Excepciones nuevas, postcondiciones más débiles, precondiciones más estrictas, throws de UnsupportedOperation.)
       - **I (ISP)**: ¿alguna interface fuerza a clientes a depender de métodos que no usan? (Implementaciones con NotImplemented o que devuelven null por método irrelevante.)
       - **D (DIP)**: ¿algún módulo de alto nivel (lógica de negocio/dominio) importa implementaciones concretas de bajo nivel (drivers, librerías de infra) en lugar de abstracciones? (Test de humo: ¿podés mockear esto en un unit test sin tocar archivos del dominio?)
       REGLA: aplicá SOLID como **lente, no como checklist ritual**. Si el proyecto tiene un estilo pragmático que rompe un principio conscientemente (ej: YAGNI sobre OCP, framework constraints), marcalo OK con nota explicativa. NO sobre-abstracts.
    5. Tests: cobertura, claridad, asserts significativos
    6. Documentación inline (JSDoc/comments donde la lógica no es obvia)

    Clasificar hallazgos como BLOQUEANTE / MENOR / OK.

    OUTPUT ESPERADO:
    - doc/sdd/NNN-titulo/cr-report.md
    - Veredicto final
    - Resumen al orquestador

    ## ⛔ PROHIBIDO EN ESTA FASE
    - NO modificar código
    - NO ser exigente con cosas no documentadas en el project-context
```

## Después de AR + CR — agregación de veredictos

| AR | CR | Acción del orquestador |
|----|----|------------------------|
| APROBADO / con MENORs | APROBADO / con MENORs | Lanzar `/nexus-p7-f4` (MENORs como deuda) |
| RECHAZADO (BLQ-AR) | * | Re-lanzar `/nexus-p4-f3` con findings de **AR + CR combinados**. Después de los fixes, evaluar si hace falta re-correr `/nexus-p6-cr` (ver tradeoff abajo). |
| * | RECHAZADO (BLQ-CR) | Re-lanzar `/nexus-p4-f3` con findings de CR |
| RECHAZADO | RECHAZADO | Re-lanzar `/nexus-p4-f3` con findings combinados |

## ⚠️ Tradeoff vs ejecución secuencial (leelo una vez)

- **Antes** (p5 → p6 secuencial): CR revisaba el código **post-fixes de AR**.
- **Ahora** (p5 paralelo): CR revisa el código **pre-fixes de AR**.

**Cuándo no importa** (caso típico, 90%+):
- AR no encuentra BLOQUEANTEs → AR fixes = 0 → el código que vio CR es el código final → cero diferencia.
- AR encuentra BLOQUEANTEs pequeños (validación de input, null check, etc.) → los fixes son aditivos y no cambian estructura → CR habría dicho lo mismo.

**Cuándo sí importa** (raro):
- AR encuentra BLOQUEANTEs estructurales que obligan a refactor grande → el código final difiere significativamente del que vio CR.
- **Acción**: después del re-F3, re-correr `/nexus-p6-cr` (legacy/standalone) ANTES de avanzar a `/nexus-p7-f4`.

El orquestador decide caso a caso. Por defecto, si los fixes de AR son <20 líneas o solo agregan validaciones, no hace falta re-CR.

## ⚠️ Importante

- Vos sos el ORQUESTADOR. NO ataques ni revisás vos mismo.
- Si hay BLOQUEANTEs: NO avances a `/nexus-p7-f4` hasta que el Dev los resuelva en una nueva iteración de F3.
- Asegurate de que los 2 Task tool calls salgan en EL MISMO mensaje, no secuenciales.
