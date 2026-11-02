---
description: NexusAgil F0+F1 — Bootstrap context and generate work-item.md for an HU
argument-hint: <HU-ID> [descripción libre]
allowed-tools: Task, Read, Glob, Grep, Write, Bash, AskUserQuestion
---

# /nexus-p1-f0-f1 — Context Bootstrap + Work Item (Paso 1/8)

Lanza el sub-agente `nexus-analyst` para ejecutar F0 (Context Bootstrap) + F1 (Work Item generation) sobre la HU especificada.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX [descripción opcional]`)

**Rutas**: antes de lanzar, resolvé `NEXUS_ROOT`, `CODE_ROOT` y `SKILL_DIR` y pasá sus valores reales en cada prompt. `SKILL_DIR` es la que exista de `.claude/skills/nexus-agile` o `~/.claude/skills/nexus-agile`; las reglas de las otras dos están en `$SKILL_DIR/references/paths.md`.

## Acciones

1. Verificá que `project-context.md` exista en NEXUS_ROOT. Si no existe, el sub-agente lo genera primero.
2. Leé `$NEXUS_ROOT/doc/sdd/_INDEX.md` para conocer el siguiente NNN y creá `$NEXUS_ROOT/doc/sdd/NNN-titulo/`: los hooks exigen ese `HU_DIR` en el prompt.
3. Lanzá el sub-agente con el Task tool:

```
Task tool:
  subagent_type: nexus-analyst
  description: F0+F1 para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor]
    FASE: F0F1
    HU_DIR: [ruta absoluta de $NEXUS_ROOT/doc/sdd/NNN-titulo]
    Eres el agente nexus-analyst de NexusAgil ejecutando F0 + F1 para la HU [WKH-XX].

    INPUT:
    - HU descrita por el humano: $ARGUMENTS
    - project-context.md: [verificar si existe en la raíz]
    - product-context.md: [verificar si existe en la raíz — contexto de negocio]
    - _INDEX.md: $NEXUS_ROOT/doc/sdd/_INDEX.md
    - Ticket en Jira/issue tracker (si aplica): leerlo con la tool getJiraIssue disponible. Si no está disponible, marcarlo y avisar; el orquestador pasa el texto

    TU TAREA:
    1. Si project-context.md no existe → generarlo siguiendo $SKILL_DIR/references/project_context_template.md
    1b. Product Context:
        Si product-context.md EXISTE → leerlo. Usar personas, flujos, y restricciones de negocio para informar los ACs y el sizing.
        Si NO existe y el prompt no trae la respuesta → devolver en PREGUNTAS PARA EL HUMANO:
          "No encontré product-context.md. ¿Cómo querés darme el contexto de negocio?"
          (a) texto, (b) link, (c) archivo ya subido a $NEXUS_ROOT/doc/prd/, (d) seguir sin contexto ([SIN PRODUCT CONTEXT] en el work-item)
        Con la respuesta: guardar el material en $NEXUS_ROOT/doc/prd/prd-raw.md si aplica, y generar product-context.md (~200 líneas) en NEXUS_ROOT, con $NEXUS_ROOT/doc/prd/ en su sección Fuentes.
        Usar $SKILL_DIR/references/product_context_template.md como estructura del documento generado.
    2. Smart Sizing: clasificar como FAST/LAUNCH/QUALITY
    3. Skills Router: declarar máximo 2 skills relevantes
    4. Generar work-item.md en $NEXUS_ROOT/doc/sdd/NNN-titulo/work-item.md con:
       - ACs en EARS (mínimo 3)
       - Scope IN/OUT explícito
       - Decisiones técnicas iniciales (DT-N)
       - Constraint Directives iniciales (CD-N)
       - Análisis de paralelismo
       - Branch sugerido
    5. Actualizar _INDEX.md con la nueva HU en estado "in progress"

    OUTPUT ESPERADO:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/work-item.md
    - _INDEX.md actualizado
    - Resumen ejecutivo (5-10 líneas) al orquestador

    SCOPE:
    - Lee SOLO archivos necesarios para entender stack y dominio
    - No podés preguntar directamente: máximo 3 preguntas en el bloque PREGUNTAS PARA EL HUMANO
    - Si falta info crítica → marcar [NEEDS CLARIFICATION] y avanzar

    ## Prohibido en esta fase
    - NO escribir código de producción
    - NO generar SDD ni Story File (eso es Architect en F2)
    - NO modificar archivos fuera de $NEXUS_ROOT/doc/sdd/NNN-titulo/, $NEXUS_ROOT/doc/prd/, product-context.md
    - NO inventar requirements
    - NO asumir scope: si dudás, marcar [NEEDS CLARIFICATION]
```

4. Si el sub-agente devuelve PREGUNTAS PARA EL HUMANO, hacelas con `AskUserQuestion` y relanzalo con las respuestas.
5. Cuando el work-item esté completo, presentalo al humano con un resumen y esperá el gate `HU_APPROVED` (texto literal).
6. NO continúes a F2 hasta recibir el gate.

## Importante
- Vos sos el ORQUESTADOR. NO leas el codebase, NO escribas el work-item vos mismo.
- Esto es un comando de F0+F1 SOLAMENTE. NO incluyas F2 en el mismo lanzamiento (los gates se romperían en sub-agente one-shot).
