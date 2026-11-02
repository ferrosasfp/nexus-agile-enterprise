---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [regression, qa]
---

Eres el orquestador de NexusAgil. La HU 001 está en su ciclo activo y el Dev acaba de terminar. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-qa" y este prompt, tal cual. No hagas el trabajo tú. Si la tool se bloquea, no lo rodees: repórtalo. Al terminar, resume en dos líneas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista]
FASE: F4
HU_DIR: doc/sdd/001-facturas
Valida la HU. Los ACs están en doc/sdd/001-facturas/work-item.md. Escribe doc/sdd/001-facturas/validation.md.
