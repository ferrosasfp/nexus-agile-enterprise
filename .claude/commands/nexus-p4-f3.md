---
description: NexusAgil F3 — Implementation by waves from Story File
argument-hint: <HU-ID> [wave-number]
allowed-tools: Task, Read, Bash
---

# /nexus-p4-f3 — Implementation (Paso 4/8)

Lanza el sub-agente `nexus-dev` para implementar la HU desde el Story File.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX` o `WKH-XX W1`)

**Rutas**: antes de lanzar, resolvé `NEXUS_ROOT`, `CODE_ROOT` y `SKILL_DIR` y pasá sus valores reales en cada prompt. `SKILL_DIR` es la que exista de `.claude/skills/nexus-agile` o `~/.claude/skills/nexus-agile`; las reglas de las otras dos están en `$SKILL_DIR/references/paths.md`.

## Pre-requisitos (Pre-flight checks obligatorios)

Antes de lanzar el sub-agente Dev, verificá:

```
[ ] El contrato existe: story-file.md, o la sección "Contrato de implementación" de sdd.md con contract_mode: unified
[ ] El branch base (main/develop) está actualizado
[ ] El branch feature de la HU existe y está checked out
[ ] Las env vars necesarias están configuradas
[ ] No hay otro sub-agente Dev corriendo sobre el mismo directorio
    → Si paralelismo necesario: un worktree por HU, con CODE_ROOT apuntando a él (ver subagent_protocol.md)
```

Si algún check falla: avisá al humano antes de lanzar.

## Acciones

```
Task tool:
  subagent_type: nexus-dev
  description: F3 Implementación para HU [WKH-XX]
  prompt: |
    RUTAS: NEXUS_ROOT=[valor] · CODE_ROOT=[valor] · SKILL_DIR=[valor]
    Eres el agente nexus-dev de NexusAgil ejecutando F3 (implementation) para la HU [WKH-XX].

    CONTRATO:
    - $NEXUS_ROOT/doc/sdd/NNN-titulo/story-file.md (o la sección "Contrato de implementación" de sdd.md si el work-item dice contract_mode: unified)

    Podés leer sdd.md solo para entender el porqué. No agrega alcance; si difiere del contrato, manda el contrato y escalás. NO leas el work-item ni el historial de chat.
    El contrato es autocontenido. Si algo falta, ESCALÁ al orquestador (NO inventes).

    TU TAREA:
    Implementar las waves del contrato en orden:
    - W0 (serial): contratos, tipos, migraciones
    - W1+ (paralelo si la wave lo permite): lógica, servicios, rutas, UI

    Para cada archivo:
    1. Verificar que está en Scope IN del contrato
    2. Re-mapeo ligero antes de cada wave (re-leer archivos de la wave anterior)
    3. Anti-Hallucination Protocol: verificar exemplars, imports, signatures
    4. Implementar
    5. Verificación incremental: typecheck + tests específicos del archivo
    6. Si falla: documentar Auto-Blindaje en $NEXUS_ROOT/doc/sdd/NNN-titulo/auto-blindaje.md, corregir, re-verificar

    OUTPUT ESPERADO:
    - Código en disco según Scope IN
    - Tests pasando
    - auto-blindaje.md (si hubo errores)
    - Reporte al orquestador: archivos creados/modificados, comandos ejecutados, output de typecheck/tests

    ## Prohibido en esta fase
    - NO tocar archivos fuera del Scope IN del contrato
    - NO crear archivos no listados
    - NO expandir scope (no refactors, no "mejoras")
    - NO usar librerías que no estén en el contrato o project-context
    - NO inventar APIs ni signatures
    - NO hacer commits sin validar la wave
    - NO marcar la HU como DONE — eso es trabajo de Docs en F4/DONE
```

## Después de F3

El pipeline continúa automático: lanzá `/nexus-p5-ar` inmediatamente con la misma HU.

## Importante
- Vos sos el ORQUESTADOR. NO escribas código vos mismo.
- Si el Dev reporta scope drift o hallazgos no resueltos: re-lanzá con instrucciones específicas.
- Si el Dev pide info que no está en el contrato: escalá al Architect (relanzá F2.5, o F2 con `contract_mode: unified`, con la corrección).
