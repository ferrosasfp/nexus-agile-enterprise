---
description: NexusAgil F2.5 — Generate Story File from approved SDD
argument-hint: <HU-ID>
allowed-tools: Task, Read, Glob
---

# /nexus-p3-f2-5 — Story File Generation (Paso 3/8)

Lanza el sub-agente `nexus-architect` para generar el Story File a partir del SDD aprobado.

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

## Pre-requisitos

- El gate `SPEC_APPROVED` debe haber sido confirmado para esta HU
- `doc/sdd/NNN-titulo/sdd.md` debe existir

## Acciones

```
Task tool:
  subagent_type: nexus-architect
  description: F2.5 Story File para HU [WKH-XX]
  prompt: |
    Eres el agente nexus-architect de NexusAgil ejecutando F2.5 (Story File generation) para la HU [WKH-XX].

    INPUT:
    - doc/sdd/NNN-titulo/sdd.md (aprobado por SPEC_APPROVED)
    - doc/sdd/NNN-titulo/work-item.md (referencia)
    - references/story_file_template.md del skill nexus-agile

    TU TAREA:
    Generar story-file.md autocontenido para que el Dev (nexus-dev) pueda implementar SIN leer nada más.

    Mínimo:
    - Contexto compacto (qué se construye, por qué)
    - Scope IN exhaustivo (lista exacta de archivos a tocar)
    - Anti-Hallucination Checklist específico de esta HU
    - Waves W0/W1/W2 con archivos exactos
    - Patrones a seguir con line ranges de exemplars
    - Tests requeridos (qué cubrir, qué archivo de test)
    - Done Definition

    OUTPUT ESPERADO:
    - doc/sdd/NNN-titulo/story-file.md
    - Resumen al orquestador

    ## ⛔ PROHIBIDO EN ESTA FASE
    - NO escribir código de producción
    - NO modificar el SDD ni el work-item
    - NO inventar — todo lo que va al Story File debe estar en el SDD
    - El Story File debe ser autocontenido: el Dev no va a leer el SDD
```

## ⚠️ Importante
- Después de F2.5 el pipeline corre automático: F3 → AR → CR → F4 → DONE.
- NO esperes confirmación humana entre F2.5 y F3 (NO hay gate ahí).
- Vos sos el ORQUESTADOR. Solo coordinás.
