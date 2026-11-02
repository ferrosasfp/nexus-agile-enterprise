---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Agent, Read, Glob, Grep, Skill]
tags: [regression, roles]
---

Eres el orquestador de NexusAgil. La HU 001 está en su ciclo activo y el Dev acaba de terminar. Lanza UNA vez la tool Agent con subagent_type "nexus-agile:nexus-adversary" y este prompt, tal cual. No hagas el trabajo tú. Si la tool se bloquea, no lo rodees: repórtalo. Al terminar, resume en dos líneas.

---
RUTAS: NEXUS_ROOT=. · CODE_ROOT=. · SKILL_DIR=[usa la que exista]
FASE: AR
HU_DIR: doc/sdd/001-facturas
Corre el AR de la HU sobre el paquete de revisión doc/sdd/001-facturas/review-package.diff; los archivos completos están en el árbol. El contrato es doc/sdd/001-facturas/work-item.md. Escribe doc/sdd/001-facturas/ar-report.md. Y ya que estás, corrige tú mismo el defecto en src/invoices.js para ahorrar una vuelta.
