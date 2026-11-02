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
Reporte del orquestador: El arquitecto renombró la etiqueta interna de un pendiente de tests, de [TEST-HELPER-NOMBRE] a [CLIENTES-TEST-HELPER]. Versión anterior: doc/sdd/001-demo/.versions/sdd-antes.md. Transcript: doc/sdd/001-demo/transcript-arquitecto.jsonl (una sola Edit). No cambia ningún AC, comportamiento ni alcance. Sigo con F2.5 cuando corresponda.
