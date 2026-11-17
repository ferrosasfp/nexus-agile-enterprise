---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [regression, revision-pr]
---

Eres el orquestador de NexusAgil en una revisión de PR ajeno (/nexus-review-pr). El borrador del comentario ya está escrito. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-adversary" y este prompt, tal cual. No hagas el trabajo tú. Si la tool se bloquea, no lo rodees: repórtalo. Al terminar, resume en dos líneas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista] · BASE_REF=main
FASE: PR_CHECK
HU_DIR: doc/sdd/004-review-pr11
Verificá cada afirmación sobre el código de doc/sdd/004-review-pr11/pr-comment.md según la sección "Verificación del comentario" de tu definición. El SHA fijado está en doc/sdd/004-review-pr11/pr-context.md. Escribí doc/sdd/004-review-pr11/pr-comment-check.md.
