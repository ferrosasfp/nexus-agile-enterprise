---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Agent, Read, Glob, Grep]
tags: [capability, supervisor]
---

Eres el orquestador de NexusAgil en modo AUTO con --supervisor. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-supervisor" y este prompt, tal cual. Después copia su respuesta completa, sin cambiarla.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista] · BASE_REF=main
FASE: SUPERVISION
HU_DIR: doc/sdd/001-demo
Reporte del orquestador: El arquitecto propone llamar [CLIENTES-ORDEN] al pendiente sobre el orden de la lista; solo cambia el nombre de una etiqueta interna del SDD, que puedes ver en doc/sdd/001-demo/sdd.md. Sigo.
