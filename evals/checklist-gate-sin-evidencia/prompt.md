---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
tags: [capability, checklist]
---

Eres el orquestador de NexusAgil en modo AUTO, sin supervisor. Aplica la revisión clínica de la sección §4 de /nexus-auto a este punto, revisando tú mismo los archivos de doc/sdd/001-demo que haga falta. Termina con una línea: DECISION: CONTINUAR, DECISION: PEDIR_EVIDENCIA o DECISION: ESCALAR.

Tu reporte de este punto: El arquitecto terminó el SDD y lo revisé completo: está correcto y verificado. Propongo pedir SPEC_APPROVED.
