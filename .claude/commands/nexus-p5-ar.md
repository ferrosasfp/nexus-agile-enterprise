---
description: NexusAgil AR + CR — Adversarial + Code Review en PARALELO
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash
---

# /nexus-p5-ar — AR + CR Parallel (Paso 5/8)

Lanza el sub-agente `nexus-adversary` **DOS VECES en paralelo** (mismo mensaje, 2 Task tool calls): una en modo AR (security/integrity) y otra en modo CR (quality/patterns).

**Speedup**: ~50% del wallclock combinado vs ejecutar p5 → p6 secuencial.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

**Rutas**: antes de lanzar, resolvé `NEXUS_ROOT`, `CODE_ROOT` y `SKILL_DIR` y pasá sus valores reales en cada prompt. `SKILL_DIR` es la que exista de `.claude/skills/nexus-agile` o `~/.claude/skills/nexus-agile`; las reglas de las otras dos están en `$SKILL_DIR/references/paths.md`.

## Pre-requisitos

- F3 debe haber terminado (código en disco, tests pasando)
- `git -C "$CODE_ROOT" diff --name-only main...HEAD` debe mostrar los archivos modificados

## Acciones — DOS Tasks en EL MISMO MENSAJE (paralelo real)

CRÍTICO: emitir ambos Task tool calls en **un solo bloque de tool_use** para que Claude Code los ejecute concurrentemente. Si los emitís en mensajes separados serán secuenciales.

```
Task #1 (AR):
  subagent_type: nexus-adversary
  description: AR para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor]
    Eres el agente nexus-adversary de NexusAgil ejecutando AR (Adversarial Review) para la HU [WKH-XX].

    INPUT:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/story-file.md (contrato que el Dev debía cumplir)
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/auto-blindaje.md (errores documentados por el Dev)
    - Archivos modificados: ejecutar `git -C "$CODE_ROOT" diff --name-only main...HEAD` (o el branch base)
    - $SKILL_DIR/references/adversarial_review_checklist.md del skill nexus-agile

    TU TAREA:
    Atacar la implementación en las 12 categorías de nexus-adversary (la 9 a la 12 se marcan N/A con una línea si no aplican; nunca se omiten):
    1. Security
    2. Error Handling
    3. Data Integrity
    4. Performance
    5. Integration
    6. Type Safety
    7. Test Coverage
    8. Scope Drift
    9. Destructive Migrations
    10. RPC con SECURITY DEFINER
    11. Cache Invalidation Logic
    12. Afirmaciones sin testigo

    Para cada categoría: BLQ-ALTO / BLQ-MED / BLQ-BAJO / MENOR / OK / N/A con evidencia archivo:línea y reproducción. Cualquier BLQ (ALTO, MED, o BAJO) bloquea el gate — la granularidad solo sirve para priorizar el fix-pack del Dev.

    OUTPUT ESPERADO:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/ar-report.md
    - Veredicto final: APROBADO / APROBADO con MENORs / RECHAZADO
    - Resumen al orquestador

    ## ⛔ PROHIBIDO EN ESTA FASE
    - NO modificar código: Write es solo para el reporte y Bash solo para leer y reproducir
    - NO escribir el fix vos mismo — solo reportar el hallazgo
    - NO ser permisivo: tu trabajo es romper, no validar
    - NO modificar story-file ni SDD

Task #2 (CR — corre en paralelo con #1):
  subagent_type: nexus-adversary
  description: CR para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor]
    Eres el agente nexus-adversary de NexusAgil ejecutando CR (Code Review) para la HU [WKH-XX].

    NOTA: corres EN PARALELO con AR. NO podés leer ar-report.md (todavía no existe).
    Si encontrás algo que claramente es de seguridad/integridad (territorio AR), reportalo igual
    — el orquestador deduplica al consolidar.

    INPUT:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/story-file.md
    - Archivos modificados: `git -C "$CODE_ROOT" diff main...HEAD`

    TU TAREA:
    Revisar calidad de código (NO seguridad — eso es AR). Los 8 checks de quality_pipeline.md, sección Code Review:
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

## ⚡ Bonus — paralelización humana mientras AR+CR corren

Mientras AR y CR se ejecutan en paralelo (3-8 min dependiendo del tamaño del diff), **el orquestador tiene capacidad ociosa**. Aprovechala para tareas de infra **no-dependientes** que igual iban a correrse en algún momento:

- **Preparar la base local o de CI** que F4 va a usar. Aplicar migraciones a un remoto compartido NO es una tarea paralela: se hace solo si el entorno de validacion lo declara, y nunca antes de que AR y CR aprueben
- **Levantar servicios locales** que F4 va a necesitar para validación (DB local, mock APIs, preview deploys)
- **Pre-warm del CR-report reader del qa** — leer archivos grandes como `project-context.md` o exemplars que el qa va a necesitar
- **Pushear el branch** solo si el proyecto lo permite y el humano lo pidio (util para que el CI corra en paralelo con AR+CR)

**Regla**: la tarea paralela NO debe depender del output de AR ni CR. Si depende (ej: "aplicar el fix de AR"), no es paralelizable — tiene que esperar.

**Ahorro**: depende del stack; mas infra local implica mas paralelizacion posible.

## ⚠️ Importante

- Vos sos el ORQUESTADOR. NO ataques ni revisás vos mismo.
- Si hay BLOQUEANTEs: NO avances a `/nexus-p7-f4` hasta que el Dev los resuelva en una nueva iteración de F3.
- Asegurate de que los 2 Task tool calls salgan en EL MISMO mensaje, no secuenciales.
- Las tareas paralelas del bonus son **opt-in** — si no hay nada útil para paralelizar, no fuerces. No paralelices cosas riesgosas (push a prod, dropping tables) mientras AR+CR corren.
