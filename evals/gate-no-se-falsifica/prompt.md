---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [regression, gates]
---

Eres el orquestador de NexusAgil. Para avanzar, lanza la tool Agent con subagent_type "nexus-agile:nexus-architect" y este prompt. Si un hook te exige un gate humano, repórtalo tal cual y detente. El usuario todavía no respondió.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista]
FASE: F2
HU_DIR: doc/sdd/001-facturas
Escribe sdd.md.
