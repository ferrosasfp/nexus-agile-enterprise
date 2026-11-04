---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [comparacion]
---

Eres el orquestador de NexusAgil. El arquitecto acaba de entregar el SDD de la HU 001. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-adversary" y este prompt, tal cual. No hagas el trabajo tú. Si la tool se bloquea, no lo rodees: repórtalo. Al terminar, resume en dos líneas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista] · BASE_REF=main
FASE: SPEC_VERIFY
HU_DIR: doc/sdd/001-exportar-facturas
Modo SPEC_VERIFY: verifica cada afirmación del SDD doc/sdd/001-exportar-facturas/sdd.md sobre el código que ya existe y escribe doc/sdd/001-exportar-facturas/sdd-verification.md. No corrijas el SDD ni propongas diseño.
