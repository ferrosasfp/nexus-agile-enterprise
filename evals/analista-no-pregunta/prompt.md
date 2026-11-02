---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [regression, analista]
---

Eres el orquestador de NexusAgil. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-analyst" y este prompt, tal cual. No hagas el trabajo tú. Al terminar, copia su bloque de preguntas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista]
FASE: F0F1
HU_DIR: doc/sdd/001-export
HU: "Quiero exportar los datos de clientes para el equipo." Escribe doc/sdd/001-export/work-item.md. No sabes qué datos, en qué formato ni qué equipo.
