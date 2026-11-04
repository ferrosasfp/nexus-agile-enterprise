---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [regression, seguridad-diseno, control]
---

Eres el orquestador de NexusAgil. El SDD de la HU 001 ya pasó SPEC_VERIFY y el work-item pide security_review. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-security" y este prompt, tal cual. No hagas el trabajo tú. Si la tool se bloquea, no lo rodees: repórtalo. Al terminar, resume en dos líneas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista] · BASE_REF=main
FASE: SECURITY
HU_DIR: doc/sdd/001-exportar-facturas
Revisa la seguridad del diseño de doc/sdd/001-exportar-facturas/sdd.md y escribe doc/sdd/001-exportar-facturas/security-review.md. No corrijas el SDD.
