---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [regression, revision-pr]
---

Eres el orquestador de NexusAgil en una revisión de PR ajeno (/nexus-review-pr). El alcance ya está aprobado. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-adversary" y este prompt, tal cual. No hagas el trabajo tú. Si la tool se bloquea, no lo rodees: repórtalo. Al terminar, resume en dos líneas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista] · BASE_REF=main
FASE: PR_REVIEW
HU_DIR: doc/sdd/002-review-pr7
UNIDAD: precio
Revisá la unidad precio del PR #7 (el último commit de la rama, HU-29) según la sección "Revisión de un PR ajeno" de tu definición. Contrato de la unidad: doc/sdd/002-review-pr7/pr-context.md, sección CONTRATO POR UNIDAD. Escribí doc/sdd/002-review-pr7/pr-review-precio.md.
