# Sub-Agent Protocol — NexusAgil

> Protocolo de orquestación por sub-agentes para eliminar context overload.
> Principio: el orquestador coordina, los sub-agentes ejecutan.
> Agnóstico de herramienta: Claude Code (Task tool), OpenCode, Cursor, o cualquier agente con sub-agentes.

---

## El Problema que Resuelve

Sin sub-agentes, el pipeline QUALITY acumula contexto en una sola sesión:

```
F0 → F1 → F2 → F2.5 → F3 → AR → CR → F4 → DONE
                                              ↑
                             ventana de contexto saturada
                             → compactación → alucinaciones
```

Con sub-agentes, cada fase empieza limpia:

```
Orchestrator (contexto mínimo — solo coordina)
     │
     ├─► [sub-agente F0] → entrega: project-context.md + sizing
     ├─► [sub-agente F1] → entrega: work-item.md
     │         ⛔ GATE: HU_APPROVED
     ├─► [sub-agente F2] → entrega: sdd.md
     │         ⛔ GATE: SPEC_APPROVED
     ├─► [sub-agente F2.5] → entrega: story-file.md
     ├─► [sub-agente F3]  → entrega: código + auto-blindaje
     ├─► [sub-agente AR]  → entrega: reporte adversarial
     ├─► [sub-agente CR]  → entrega: reporte code review
     ├─► [sub-agente F4]  → entrega: validation.md
     └─► [sub-agente DONE] → entrega: report.md + _INDEX actualizado
```

---

## Rol del Orquestador

El orquestador NUNCA:
- Lee archivos del codebase
- Escribe código
- Genera SDDs ni Story Files
- Ejecuta tests

El orquestador SOLO:
- Lanza sub-agentes con el prompt correcto
- Recibe el artefacto de salida
- Presenta resúmenes al humano en los gates
- Pasa el artefacto como input al siguiente sub-agente
- Detecta si un sub-agente falló y re-lanza

---

## Prompt de cada sub-agente

Cada sub-agente recibe un prompt autocontenido con:

```
Eres el agente [ROL] de NexusAgil ejecutando [FASE].
Stack-agnostic skill: .claude/skills/nexus-agile/SKILL.md
Skills de dominio: [skill-frontend | skill-database | ...] (según Skills Router)

INPUT:
[artefacto de la fase anterior — work-item.md, sdd.md, etc.]

TU TAREA:
[descripción exacta de la fase]

OUTPUT ESPERADO:
[artefacto a generar — nombre de archivo, formato]

SCOPE:
- Lee SOLO los archivos referenciados en tu INPUT
- No explores el codebase más allá de lo necesario para tu tarea
- Si necesitas algo que no está en tu INPUT: escala al orquestador
```

---

## Tabla de delegación por fase

| Fase | Sub-agente | Input | Output |
|------|-----------|-------|--------|
| F0 | Analyst + Architect | HU raw + repo path | project-context.md (si no existe) + SDD_MODE |
| F1 | Analyst + Architect + UX | HU + project-context.md | work-item.md |
| F2 | Architect + Adversary | work-item.md + project-context.md | sdd.md |
| F2.5 | Architect | sdd.md | story-file.md |
| F3 | Dev | story-file.md | código en disco + auto-blindaje |
| AR | Adversary | story-file.md + archivos modificados | reporte adversarial |
| CR | Adversary + QA | story-file.md + archivos modificados | reporte code review |
| F4 | QA | story-file.md + archivos modificados | validation.md |
| DONE | Docs | todos los artefactos anteriores | report.md + _INDEX.md |

---

## Paralelismo real en F2

Spec Writer + Designer pueden correr en paralelo como sub-agentes independientes:

```
Orchestrator
     │
     ├─► [sub-agente Spec Writer] ──┐
     │                              ├─► merge → sdd.md completo
     └─► [sub-agente Designer]  ──┘
```

El orquestador espera ambos outputs antes de presentar el SDD al humano.
Solo si el IDE soporta sub-agentes paralelos (Claude Code Task tool, OpenCode).
Si no hay soporte de paralelismo: correr en secuencia, mismo resultado.

---

## Comunicación entre fases

Los artefactos en disco (`doc/sdd/NNN-titulo/`) son el canal de comunicación entre sub-agentes:

```
sub-agente F1 → escribe work-item.md
sub-agente F2 → lee work-item.md (sin necesidad de cargar la conversación anterior)
```

Esto es posible porque los artefactos son autocontenidos. El orquestador no necesita pasar el historial de chat — solo la ruta del archivo.

---

## Cuándo usar sub-agentes vs sesión única

| Señal | Recomendación |
|-------|--------------|
| HU con SDD_MODE = full | Sub-agentes (F2 en adelante) |
| HU con SDD_MODE = bugfix o mini | Sesión única (overhead no justificado) |
| F3 con 3+ waves o 10+ archivos | Sub-agente Dev obligatorio |
| IDE soporta Task tool / sub-agentes | Siempre sub-agentes en QUALITY |
| IDE sin soporte de sub-agentes | Sesión única con Skills Router |

---

## Implementación por herramienta

**Claude Code:**
```
Task tool — el orquestador usa `task` para lanzar cada fase como sub-agente
El sub-agente recibe el prompt completo y los archivos de input
```

**OpenCode:**
```
Spawned agents — el orquestador usa el sistema de agentes de OpenCode
Compatible con el plugin de Engram para persistencia entre fases
```

**Sin soporte nativo:**
```
Sesión única con Skills Router activo
El contexto crece pero el Skills Router lo mantiene limpio
La memoria persistente (Principio 8) compensa la falta de sub-agentes
```

---

## Reglas del orquestador

1. **Nunca hace trabajo real** — si el orquestador empieza a generar código o SDDs, es un error de proceso
2. **Contexto mínimo** — el orquestador solo mantiene: fase actual + artefacto de salida + estado del gate
3. **Falla explícita** — si un sub-agente no entrega el artefacto esperado, el orquestador informa al humano y re-lanza
4. **Gates en el orquestador** — los gates (HU_APPROVED, SPEC_APPROVED) los maneja el orquestador, no los sub-agentes
5. **Agnóstico** — el protocolo funciona con cualquier implementación de sub-agentes disponible en el IDE
