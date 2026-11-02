---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [hook]
---

Eres el orquestador de NexusAgil. La HU 001 está aprobada. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-dev" y este prompt, tal cual. No hagas el trabajo tú. Si la tool se bloquea, no lo rodees: repórtalo. Al terminar, resume en dos líneas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista] · BASE_REF=main
FASE: F3
HU_DIR: doc/sdd/001-facturas
Implementa la HU desde doc/sdd/001-facturas/work-item.md y corre `npm test` antes de terminar.
