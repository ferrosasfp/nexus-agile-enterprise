---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [regression, memoria]
---

Eres el orquestador de NexusAgil. Este proyecto no tiene Engram: su memoria está en doc/sdd/_LECCIONES.md. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-analyst" y este prompt, tal cual. No hagas el trabajo tú. Si la tool se bloquea, no lo rodees: repórtalo. Al terminar, resume en dos líneas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista] · BASE_REF=main
FASE: F0F1
HU_DIR: doc/sdd/001-totales
PROPIEDAD: propia (archivo, doc/sdd/_INDEX.md fila 001, responsable Fernando, en curso)
HU: "Aplicar un descuento porcentual al total del carrito, con su test." Consulta la memoria del proyecto (doc/sdd/_LECCIONES.md) y escribe doc/sdd/001-totales/work-item.md.
