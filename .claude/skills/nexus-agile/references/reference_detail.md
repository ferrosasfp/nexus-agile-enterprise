# Detalle de consulta — NexusAgil

Sale de `SKILL.md` para mantener corto lo que siempre se carga.

### Instalación

Los agentes y commands se instalan desde el repo a la ubicación de Claude Code del usuario:

```bash

### Por qué esto reduce el olvido del orquestador

1. **El rol está en el archivo del agente** — el orquestador solo escribe `Task(subagent_type="nexus-architect")` y el bloque PROHIBIDO viene incluido. No puede olvidarlo.
2. **Los slash commands son atajos** — `/nexus-p2-f2 WKH-29` expande a un Task tool completo. Menos fricción = más uso = menos saltos al modo "yo lo hago acá mismo".
3. **Tools acotadas por agente**: revisores y QA no tienen `Edit`. Tienen `Write` para su reporte y `Bash` para ejecutar, así que técnicamente podrían modificar código: lo impide la regla de rol, y la Drift Detection lo detecta.
4. **Pre-requisitos explícitos en cada command** — el slash command verifica que el gate previo esté cumplido antes de lanzar.

## Agent Roster (resumen)

> Detalle completo en `references/agents_roster.md`.

| Agente | Rol | Fases |
|--------|-----|-------|
| **Analyst** | Business Analyst — Extrae requisitos, normaliza HU, define ACs EARS | F0, F1 |
| **Architect** | Software Architect — Codebase Grounding, SDD, Story File | F2, F2.5 |
| **UX** | UX Designer — Microcopy, flujos de usuario, accesibilidad | F1 |
| **Adversary** | Security & Quality Adversary — AR, CR, seguridad | AR, CR |
| **Dev** | Senior Developer — Implementa solo el contrato, en waves, test-first | F3 |
| **SM** | Scrum Master — Sprint ceremonies (Planning, Status, Retro) | Cadencia |
| **QA** | QA Engineer — Validacion de ACs, drift detection, quality gates | F4 |
| **Triage** | Quick Flow Specialist — Triage y pipeline abreviado | Quick Flow |
| **Docs** | Documentation Specialist — Documenta artefactos, actualiza _INDEX.md | DONE |

### Regla de Separacion
- Quien **especifica** (Architect) NO implementa (Dev).
- Quien **implementa** (Dev) NO valida (QA).
- Quien **revisa adversarialmente** (Adversary) NO implemento.

## /nexus.clarify — Consistency Check

Invocable en cualquier momento: "clarify", "check consistencia", "valida artefactos".

| Check | Status |
|-------|--------|
| **AC Coverage** | Cada AC tiene al menos 1 tarea |
| **Scope Drift** | Ninguna tarea toca archivos fuera de Scope IN |
| **Traceability** | Cada archivo del plan aparece en SDD |
| **Contradictions** | No hay conflictos entre AC y reglas de negocio |
| **Markers** | No hay [NEEDS CLARIFICATION] pendientes |
| **Missing Inputs** | Missing Inputs bloqueantes resueltos |
| **Exemplars Valid** | Archivos referenciados como exemplar existen |

El clarify es informativo, no bloqueante. El humano decide.

## Modelo Recomendado por Fase

| Fase | Modelo | Razon |
|------|--------------------|-------|
| F0-F1 (analisis) | Sonnet | Lo revisa un humano en el gate. En AUTO QUALITY, Opus: ahi no hay humano |
| F2 (SDD) | Opus | Razonamiento profundo |
| F2.5 (Story File) | Opus | Contrato critico |
| F3 (implementacion) | Opus | Anti-alucinacion |
| AR | Opus | Seguridad requiere el modelo mas capaz |
| CR | Opus | Mismo agente que AR |
| F4 (QA) | Sonnet | Parcialmente mecanico |
| DONE | Haiku | Compilacion mecanica |
| Quick Flow | Sonnet | Cambios triviales |
| Hotfix | Opus | Investigacion de causa raiz |
| Sprint Cadence | Sonnet | Ceremonias estructuradas |

---

El esfuerzo se fija en el agente: `effort: high` en `nexus-architect` y `nexus-adversary`, porque un error ahi se paga en todas las fases siguientes. Los demas usan el de la sesion. La variable `CLAUDE_CODE_EFFORT_LEVEL` tiene prioridad sobre este campo.

### Formato _INDEX.md

```markdown

### Regla de Exemplar Vivo

Antes de usar cualquier archivo como exemplar:
1. Verificar que existe (`Glob` o `Read`)
2. Si **no existe**: buscar en la misma carpeta y elegir el mas similar
3. Si **la carpeta tampoco existe**: buscar por patron en el proyecto (`Grep`)
4. **Nunca referenciar un archivo que no se haya confirmado que existe**

### 11 Slash Commands (`.claude/commands/`)

| Comando | Fase | Sub-agente que lanza | Pre-requisito |
|---------|------|---------------------|---------------|
| `/nexus-p1-f0-f1 <HU>` | F0 + F1 | `nexus-analyst` | — |
| `/nexus-p2-f2 <HU>` | F2 (SDD) | `nexus-architect` | `HU_APPROVED` |
| `/nexus-p3-f2-5 <HU>` | F2.5 (Story File) | `nexus-architect` | `SPEC_APPROVED` |
| `/nexus-p4-f3 <HU>` | F3 (impl) | `nexus-dev` | `story-file.md` existe |
| `/nexus-p5-ar <HU>` | AR + CR | `nexus-adversary` x2 | F3 terminado |
| `/nexus-p6-cr <HU>` | Re-correr CR (opcional) | `nexus-adversary` | Fixes estructurales de AR |
| `/nexus-p7-f4 <HU>` | F4 (QA) | `nexus-qa` | AR y CR APROBADOS |
| `/nexus-p8-done <HU>` | DONE | `nexus-docs` | F4 APROBADO |
| `/nexus-fast-pipeline <HU>` | FAST completo | analyst → dev → qa → docs | — |
| `/nexus-fast-plus-ar <HU>` | FAST+AR completo | analyst → dev → adversary → qa → docs | — |
| `/nexus-auto <HU> [HU ...]` | AUTO (analyst decide) | orquestador (self) | — |

> **Prefijo `pN`**: el número del paso indica el orden obligatorio. Arrancá siempre por `p1` y avanzá secuencialmente. Los gates humanos (`HU_APPROVED`, `SPEC_APPROVED`) ocurren entre `p1→p2` y `p2→p3`. Entre `p3→p8` el pipeline corre solo.

# Global (todos los proyectos)
cp -r .claude/agents/nexus-*.md ~/.claude/agents/
cp -r .claude/commands/nexus-*.md ~/.claude/commands/

# O por proyecto (solo este repo)
# Ya están en .claude/agents/ y .claude/commands/ del repo
```

Después de instalar, los slash commands aparecen con autocomplete al escribir `/nexus-` en Claude Code.
