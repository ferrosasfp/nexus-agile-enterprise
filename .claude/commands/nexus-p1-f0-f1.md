---
description: NexusAgil F0+F1 — Bootstrap context and generate work-item.md for an HU
argument-hint: <HU-ID> [descripción libre]
allowed-tools: Task, Read, Glob, Grep, Write
---

# /nexus-p1-f0-f1 — Context Bootstrap + Work Item (Paso 1/8)

Lanza el sub-agente `nexus-analyst` para ejecutar F0 (Context Bootstrap) + F1 (Work Item generation) sobre la HU especificada.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX [descripción opcional]`)

## Acciones

1. Verificá que `project-context.md` exista en la raíz del proyecto. Si no existe, el sub-agente lo genera primero.
2. Leé `doc/sdd/_INDEX.md` para conocer el siguiente NNN. Si no existe el directorio `doc/sdd/`, creá la estructura.
3. Lanzá el sub-agente con el Task tool:

```
Task tool:
  subagent_type: nexus-analyst
  description: F0+F1 para HU [WKH-XX]
  prompt: |
    Eres el agente nexus-analyst de NexusAgil ejecutando F0 + F1 para la HU [WKH-XX].

    INPUT:
    - HU descrita por el humano: $ARGUMENTS
    - project-context.md: [verificar si existe en la raíz]
    - _INDEX.md: doc/sdd/_INDEX.md
    - Ticket en Jira/issue tracker (si aplica): consultar mcp__claude_ai_Atlassian__getJiraIssue

    TU TAREA:
    1. Si project-context.md no existe → generarlo siguiendo references/project_context_template.md
    2. Smart Sizing: clasificar como FAST/LAUNCH/QUALITY
    3. Skills Router: declarar máximo 2 skills relevantes
    4. Generar work-item.md en doc/sdd/NNN-titulo/work-item.md con:
       - ACs en EARS (mínimo 3)
       - Scope IN/OUT explícito
       - Decisiones técnicas iniciales (DT-N)
       - Constraint Directives iniciales (CD-N)
       - Análisis de paralelismo
       - Branch sugerido
    5. Actualizar _INDEX.md con la nueva HU en estado "in progress"

    OUTPUT ESPERADO:
    - doc/sdd/NNN-titulo/work-item.md
    - _INDEX.md actualizado
    - Resumen ejecutivo (5-10 líneas) al orquestador

    SCOPE:
    - Lee SOLO archivos necesarios para entender stack y dominio
    - Máximo 3 preguntas al humano vía AskUserQuestion para completar DoR
    - Si falta info crítica → marcar [NEEDS CLARIFICATION] y avanzar

    ## ⛔ PROHIBIDO EN ESTA FASE
    - NO escribir código de producción
    - NO generar SDD ni Story File (eso es Architect en F2)
    - NO modificar archivos fuera de doc/sdd/NNN-titulo/
    - NO inventar requirements
    - NO asumir scope: si dudás, marcar [NEEDS CLARIFICATION]
```

4. Cuando el sub-agente entregue el work-item, presentalo al humano con un resumen y esperá el gate `HU_APPROVED` (texto literal).
5. NO continúes a F2 hasta recibir el gate.

## ⚠️ Importante
- Vos sos el ORQUESTADOR. NO leas el codebase, NO escribas el work-item vos mismo.
- Esto es un comando de F0+F1 SOLAMENTE. NO incluyas F2 en el mismo lanzamiento (los gates se romperían en sub-agente one-shot).
